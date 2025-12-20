"""Presidio-based scrubber adapter (Unified Clinical Context).

Implements PHIScrubberPort using Presidio AnalyzerEngine with enhanced
dynamic safeguards for clinical terms, providers, and HIPAA age rules.
Unified version combining scispacy integration and targeted false positive fixes.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable
from functools import lru_cache

from modules.phi.ports import PHIScrubberPort, ScrubResult

logger = logging.getLogger(__name__)

ZERO_WIDTH_CHARACTERS: frozenset[str] = frozenset(
    {
        "\u200b",  # ZERO WIDTH SPACE
        "\u200c",  # ZERO WIDTH NON-JOINER
        "\u200d",  # ZERO WIDTH JOINER
        "\u200e",  # LEFT-TO-RIGHT MARK
        "\u200f",  # RIGHT-TO-LEFT MARK
        "\u2060",  # WORD JOINER
        "\ufeff",  # ZERO WIDTH NO-BREAK SPACE (BOM)
    }
)
ZERO_WIDTH_TRANSLATION_TABLE: dict[int, int] = {ord(ch): ord(" ") for ch in ZERO_WIDTH_CHARACTERS}

# --- Dynamic Regex Configurations ---

# HIPAA Age Rule: Match ages >= 90 for aggregation.
AGE_OVER_90_RE = re.compile(
    r"(?i)(?:\b(?:age|aged)\s*[:]?\s*(?:9\d|[1-9]\d{2,})\b)|"
    r"(?:\b(?:9\d|[1-9]\d{2,})\s*-?\s*(?:y/o|y\.?o\.?|yo|yrs?|years?|year-old|year\s+old)\b)"
)

# ICD-10 Codes (e.g., J98.09) - often misidentified as PERSON
_ICD_CODE_RE = re.compile(r"\b[A-Z]\d{2}(?:\.\d{1,4})?\b")

# Eponym Suffixes: If a PERSON entity is followed by these, it's likely a medical term
MEDICAL_EPONYM_SUFFIXES = {
    "syndrome", "maneuver", "sign", "catheter", "tube", "stent", "clamp",
    "retractor", "forceps", "needle", "classification", "criteria", "score",
    "scale", "stage", "grade", "grading", "system", "procedure", "operation",
    "technique", "approach", "incision", "fascia", "ligament", "artery",
    "vein", "nerve", "muscle", "reflex", "law", "principle", "solution",
    "medium", "agar", "stain", "position", "view", "line", "drain", "bag",
    "mask", "airway", "blade", "scope", "loop", "snare", "basket", "anesthesia"
}

# Dynamic Headers: Matches "History of Present Illness:" or "Findings:"
# Robustness Fix: Changed ^\s* to ^[ \t]* to prevent greedily consuming newlines
_DYNAMIC_HEADER_RE = re.compile(
    r"^[ \t]*([A-Z][A-Z0-9\s\/\-\(\)]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s*:\s*",
    re.MULTILINE
)

# Context-aware check for ROSE (Rapid On-Site Evaluation) to avoid flagging as Person "Rose"
# Looks for "ROSE" followed by clinical findings or status
_ROSE_CONTEXT_RE = re.compile(
    r"\bROSE(?:\s+|:)\s*(?:suspicious|consistent|positive|negative|pos|neg|performed|"
    r"collected|sample|specimen|analysis|evaluation|procedure|review|findings?)\b",
    re.IGNORECASE,
)

# Terms that the Biomedical Shield should NOT protect (prevent un-redacting actual people)
BIOMEDICAL_SHIELD_BLOCKLIST = {
    "patient", "pt", "dr", "doctor", "mr", "ms", "mrs", "male", "female", 
    "man", "woman", "boy", "girl", "mother", "father", "son", "daughter",
    "husband", "wife", "spouse", "partner", "subject", "participant"
}
BIOMEDICAL_ENTITY_LABELS: frozenset[str] = frozenset(
    {"ENTITY", "DISEASE", "CHEMICAL", "PROCEDURE", "BODY_PART"}
)
BIOMEDICAL_SHIELD_TARGET_TYPES: frozenset[str] = frozenset(
    {"PERSON", "LOCATION", "ORGANIZATION"}
)
US_STATE_ABBREVS: frozenset[str] = frozenset(
    {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
        "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
        "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
        "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
        "WI", "WY", "DC",
    }
)

ANATOMICAL_ALLOW_LIST = {
    "larynx", "pharynx", "oropharynx", "nasopharynx", "glottis", "subglottis",
    "epiglottis", "vocal cords", "true vocal cords", "false vocal cords", "cords",
    "naris", "nares", "oral cavity", "tongue", "palate", "upper lobe", "lower lobe",
    "middle lobe", "right upper lobe", "rul", "right middle lobe", "rml",
    "right lower lobe", "rll", "left upper lobe", "lul", "left lower lobe", "lll",
    "lingula", "lingular", "carina", "main carina", "trachea", "distal trachea",
    "proximal trachea", "bronchus", "bronchi", "mainstem", "right mainstem",
    "left mainstem", "bronchus intermedius", "segmental", "subsegmental",
    "proximal airways", "distal airways", "station 4r", "station 4l", "station 7",
    "station 2r", "station 2l", "station 10", "station 11", "station 12",
    "4r", "4l", "7", "10r", "10l", "11r", "11l", "11rs", "11ri", "mediastinum",
    "mediastinal", "hilum", "hilar", "paratracheal", "subcarinal", "lymph node",
    "lymph nodes", "node", "nodes", "ebus", "eus", "tbna", "bal", "bronchoscopy",
    "left", "right", "bilateral", "unilateral",
    "apicoposterior", "left main", "single lobe", "upper lobes",
    "nose", "nasal", "pulmonary", "lung", "lungs", "pleura", "pleural",
    "tracheobronchial", "endobronchial", "chest", "thorax", "thoracic",
    # Lymph Node Stations (1-14 with variants)
    "station", "stations",
    "1r", "1l", "2r", "2l", "3a", "3p", "4r", "4l", "5", "6", "7", "8", "9",
    "10r", "10l", "11r", "11l", "11rs", "11ri", "12r", "12l", "13r", "13l", "14r", "14l"
}

CLINICAL_ALLOW_LIST = {
    # Retaining extensive list for fallback safety
    *ANATOMICAL_ALLOW_LIST,
    "ion", "monarch", "galaxy", "superdimension", "illumisite", "spin", 
    "lungvision", "archimedes", "inreach", "veran", "intuitive", "auris",
    "shape-sensing", "robotic-assisted", "nav-guided", "enb", "zephyr",
    "spiration", "pulmonx", "olympus", "coviden", "medtronic", "boston scientific",
    "cook", "merit", "conmed", "erbe", "chartis", "collateral ventilation",
    "pleurx", "aspira", "rocket", "yueh", "cooke", "pigtail", "tru-cut", 
    "abrams", "heimlich", "pleurovac", "chest tube", "ipc", "tunneled catheter",
    "picc", "picc line", "midline", "central line", "art line", "a-line",
    "dumon", "hood", "novatech", "aero", "ultraflex", "sems", "silicone",
    "hybrid stent", "y-stent", "airway stent", "bonastent", "cios", "cios spin",
    "cone beam", "cbct", "fluoroscopy", "rebus", "radial ebus", "radial probe",
    "miniprobe", "ultrasound", "sonographic", "elastography", "apc", "argon plasma",
    "electrocautery", "cryo", "cryoprobe", "cryospray", "cryoablation", "cryotherapy",
    "cryobiopsy", "mwa", "microwave", "radiofrequency", "rfa", "laser", "nd:yag",
    "co2 laser", "diode", "microdebrider", "snare", "basket", "fogarty", "arndt",
    "cohen", "blocker", "balloon", "bougie", "brush", "knife", "forceps",
    "alligator forceps", "needle", "catheter", "dilator", "guidewire", "trochar",
    "introduction needle", "introducer", "lyofoam", "rigid", "rigid scope",
    "rigid bronchoscope", "ventilating scope", "lma", "laryngeal mask",
    "laryngeal mask airway", "ett", "endotracheal tube", "lidocaine", "fentanyl",
    "midazolam", "versed", "propofol", "etomidate", "succinylcholine", "rocuronium",
    "cisatracurium", "sugammadex", "neostigmine", "glycopyrrolate", "atropine",
    "epinephrine", "phenylephrine", "norepinephrine", "flumazenil", "naloxone",
    "narcan", "romazicon", "kenalog", "tranexamic acid", "txa", "doxycycline",
    "bleomycin", "talc", "saline", "ns", "instillation", "fibrinolysis", "tpa",
    "dnase", "absen", "absent", "present", "normal", "abnormal", "stable",
    "unstable", "adequate", "inadequate", "diagnostic", "nondiagnostic",
    "malignant", "benign", "suspicious", "atypical", "granuloma", "necrosis",
    "inflammation", "anthracotic", "cobblestoning", "erythematous", "friable",
    "nodular", "polypoid", "patent", "occluded", "obstructed", "stenosis",
    "stricture", "malacia", "fistula", "dehiscence", "granulation", "secretions",
    "mucus", "blood", "clot", "purulent", "serous", "serosanguinous", "chylous",
    "bloody", "fluid", "size", "volume", "echogenicity", "anechoic", "hypoechoic",
    "isoechoic", "hyperechoic", "loculations", "thin", "thick", "diminished",
    "eccentric", "continuous", "margin", "lung", "lungs", "lobe", "lobes", "pleura",
    "pleural", "airway", "trachea", "esophagus", "thyroid", "spine", "rib",
    "chest wall", "diaphragm", "nodule", "mass", "lesion", "tumor", "infiltrate",
    "consolidation", "ground glass", "cavity", "calcification", "effusion",
    "pneumothorax", "hemothorax", "empyema", "chylothorax", "trapped lung",
    "lymphadenopathy", "neoplasm", "malignancy", "mycetoma", "pleural effusion",
    "initial day", "subsequent day", "initial episode", "repeat", "modifier",
    "separate structure", "distinct service", "unlisted procedure", "cpt",
    "icd-10", "diagnosis", "indication", "history", "plan", "assessment", "tbbx",
    "tbna", "tbcbx", "mm", "cm", "fr", "french", "gauge", "liter", "liters", "cc",
    "ml", "joules", "watts", "lpm", "l/min", "mins", "seconds", "secs", "minutes",
    "attending", "fellow", "resident", "anesthesiologist", "crna", "nurse", "rn",
    "tech", "technician", "observer", "proceduralist", "assistant", "self, referred",
    "referred", "provider", "hodgkin", "hodgkin's", "non-hodgkin", "lymphoma",
    "carcinoma", "adenocarcinoma", "squamous", "sarcoidosis", "tuberculosis", "afb",
    "fungal", "bacterial", "viral", "nonobstructive", "anesthesia",
    "general anesthesia", "us", "mc", "pacs", "on", "md", "do", "phd", "target",
    "freeze", "brush", "media", "samples", "sample", "specimen", "specimens",
    "disposition", "mediastinal", "lymph", "lymph node", "lymph nodes",
    "lung nodule", "solitary lung nodule", "mass", "lesion", "mark", "place",
    "note", "report", "review",
    # Clinical abbreviations/phrases seen in procedure notes
    "abx", "epi", "peds", "onco", "ptx", "blvr", "apc", "mac", "rfa",
    "bronchoscopic", "bronchoscopic lung volume reduction", "lung volume reduction",
    "jet vent", "jet ventilation", "moderate sedation", "mod sed", "sedation",
    "thoracoscopy", "dx thoracoscopy", "rigid", "rigid bevel", "rigid tracheal",
    "debulking", "mech debulking", "mechanical debulking", "brachy", "brachy cath",
    "cath", "chartis", "seldinger", "cooled rfa", "sprayed talc",
    "emphysema", "adenopathy", "adeno", "carcinoid", "sarcoid", "laryngospasm",
    "mesothelioma", "oligometastatic", "telemetry", "path", "wash", "nasal",
    "dye", "marking", "mark", "tattoo", "clip", "fiducial", "drainage", "drng",
    "papilloma", "papa lima", "novatech", "novatech silicone", "silicone", "aerostent", "lavage",
    "brushing", "trap", "lukens", "pathology", "cytology", "histology", "biopsy",
    "frozen", "permanent", "section", "mod", "sed", "general", "local", "topical",
    "antibiotics",
    # Devices, equipment, and procedures
    "airway stenting", "cuff", "deployed aero", "aero sems", "diode laser",
    "doppler", "fibrin glue", "fibrin", "glidescope", "hurricane", "ion nav",
    "ion robot", "karl storz", "storz", "laryngoscope", "monarch platform",
    "photofrin", "pleurx", "pneumostat", "polypectomy snare", "protected brush",
    "surgicel", "thermoplasty", "thoracostomy tube", "tube thoracostomy",
    "ultrathin", "veran", "volumetric", "volumetric ct", "em nav",
    "em navigation", "electromagnetic navigation",
    # Clinical findings/pathology/Lab
    "atypia", "boggy", "debris", "desat", "dyspnea", "gastric ca", "glucose",
    "hemorrhagic hilar", "lymphocytes", "melanoma", "metastatic breast cancer",
    "mucosa", "neoplasia", "nsclc", "ovarian ca", "papillomas", "pus",
    "schwannoma", "squamous cell carcinoma", "stridor", "thymoma",
    "tracheomalacia", "tracheobronchomalacia", "egfr", "hemoglobin", "hgb",
    "infiltrating", "vc mode", "pmean", "thoracoscope", "dumon tracheal", 
    "dumon",
    # Medications
    "alteplase", "azithromycin", "bicarb", "dornase", "levofloxacin",
    "levofloxacin prophylaxis", "lido", "midaz", "oxygen", "prednisone",
    "temoporfin", "augmentin", "decadron",
    # Administrative, Roles, and Common False Positives
    "electronically signed", "findings rounded", "findings short", "findings tumor",
    "breast", "vessel", "myer-cotton", "endotek",
    "alert", "metrics", "dob", "mrn", "birth date", "birthdate",
    "patient status", "registration", "minimal", "significant", "successful",
    "prepared", "reduce", "remain", "max", "physician", "attending physician",
    # Institution / IT Terms to prevent False Positive Location redaction
    "ucsd", "nmcsd", "balboa", "navy", "va", "veterans affairs", "scripps", 
    "sharp", "kaiser", "sutter", "mercy", "providence", "palomar", "radys",
    "rady children's", "rady childrens", "memorial", "tri-city", "tricity",
    "media", "indication"
}

FACILITY_ALLOW_LIST: frozenset[str] = frozenset(
    {
        "ucsd", "nmcsd", "balboa", "navy", "va", "veterans affairs", "scripps",
        "sharp", "kaiser", "sutter", "mercy", "providence", "palomar", "radys",
        "rady children's", "rady childrens", "memorial", "tri-city", "tricity",
    }
)

AMBIGUOUS_ALLOW_LIST: frozenset[str] = frozenset(
    {"cook", "merit", "rocket", "cohen", "hood"}
)

CONTEXTUAL_ALLOWLIST_KEYWORDS: frozenset[str] = frozenset(
    {
        "device", "catheter", "stent", "scope", "bronchoscope", "bronch",
        "needle", "probe", "implant", "balloon", "laser", "ablation",
        "robotic", "navigation", "system", "tube", "line", "biopsy", "ipc",
    }
)
_CONTEXTUAL_ALLOWLIST_RE = re.compile(
    r"\b(?:"
    + "|".join(sorted((re.escape(t) for t in CONTEXTUAL_ALLOWLIST_KEYWORDS), key=len, reverse=True))
    + r")\b",
    re.IGNORECASE,
)

DEFAULT_ALLOWLIST_OVERLAP_THRESHOLD = 0.5

DEFAULT_ENTITY_SCORE_THRESHOLDS: dict[str, float] = {
    "PERSON": 0.50,
    "DATE_TIME": 0.60,
    "LOCATION": 0.70,
    "MRN": 0.50,
    "__DEFAULT__": 0.50,
}

DEFAULT_RELATIVE_DATE_TIME_PHRASES: tuple[str, ...] = (
    "about a week", "in a week", "next week", "today", "tomorrow", "yesterday", "same day",
)

STRUCTURED_ENTITY_TYPES: frozenset[str] = frozenset(
    {
        "MRN", "US_SSN", "PHONE_NUMBER", "EMAIL_ADDRESS", "ADDRESS",
        "AGE_OVER_90", "US_DRIVER_LICENSE", "MEDICAL_LICENSE",
    }
)

# UPDATED: Robust regex handling "Name: Last, First", Mixed Case, and Keyword Exclusion
PATIENT_NAME_LINE_RE = re.compile(
    r"""(?im)^[ \t]*
        (?:INDICATION\s+FOR\s+OPERATION|IMPRESSION\s*/\s*PLAN|PATIENT|NAME|PATIENT\s+NAME)\s*[:]\s*
        (?P<name>
            (?!MRN\b|ID\b|DOD\b|Date\b|DOB\b|Sex\b|Gender\b)[A-Z][a-z'’-]+
            (?:
                ,\s+(?!MRN\b|ID\b|DOD\b|Date\b|DOB\b|Sex\b|Gender\b)[A-Z][a-z'’-]+(?:\s+(?!MRN\b|ID\b|DOD\b)[A-Z][a-z'’-]+)*
                |
                (?:\s+(?!MRN\b|ID\b|DOD\b)[A-Z]\.?)?
                (?:\s+(?!MRN\b|ID\b|DOD\b)[A-Z][a-z'’-]+){1,3}
            )
        )
        \s+(?:is\s+(?:a|an)\b|MRN|ID|DOD|Date|DOB|Sex|Gender|\d)
    """,
    re.VERBOSE,
)

_DATE_NUMERIC_RE = re.compile(
    r"""(?ix)
    \b(
        (?:0?[1-9]|1[0-2]) [/-] (?:0?[1-9]|[12]\d|3[01]) [/-] (?:\d{4}|\d{2})
        |
        (?:0?[1-9]|1[0-2]) [/-] (?:0?[1-9]|[12]\d|3[01]) (?:\d{4})
    )\b
    """
)

_DATE_ISO_RE = re.compile(r"\b(?:19|20)\d{2}[/-](?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])\b")

_MONTH_NAME_FRAGMENT = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
    r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)
_DATE_TEXT_MONTH_FIRST_RE = re.compile(
    rf"(?ix)\b(?:{_MONTH_NAME_FRAGMENT})\s+(?:0?[1-9]|[12]\d|3[01])(?:st|nd|rd|th)?(?:,)?\s+(?:\d{{4}}|\d{{2}})\b"
)
_DATE_TEXT_DAY_FIRST_RE = re.compile(
    rf"(?ix)\b(?:0?[1-9]|[12]\d|3[01])(?:st|nd|rd|th)?\s+(?:{_MONTH_NAME_FRAGMENT})(?:,)?\s+(?:\d{{4}}|\d{{2}})\b"
)
# NEW: Added support for compact dates like "21Nov2019"
_DATE_COMPACT_TEXT_RE = re.compile(r"(?i)\b\d{1,2}[a-z]{3}\d{4}\b")

_DATETIME_ISO_RE = re.compile(
    r"(?ix)\b(?:19|20)\d{2}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b"
)
_DATETIME_SLASH_TIME_COLON_RE = re.compile(
    r"""(?ix)\b
        (?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+
        (?:[01]?\d|2[0-3]):[0-5]\d
        (?:\s*(?:am|pm))?
    \b"""
)
_DATETIME_SLASH_TIME_COMPACT_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\s+\d{3,4}\b")

_MEASUREMENT_UNIT_TAIL_RE = re.compile(r"(?i)^\s*(?:ml|cc|mg|mcg|g|kg|fr|cmh2o|mmhg|%|c|°c)\b")

_CREDENTIAL_NORMALIZED: frozenset[str] = frozenset(
    {
        "MD", "DO", "PHD", "RN", "RT", "PA", "PAC", "NPC", "NP", "DNP", "FNP", 
        "CRNA", "RRT", "LPN", "CNA", "MA",
    }
)

# UPDATED: Use ^[ \t]* to correctly anchor line start. Added "PROCEDURALIST" and plural handling.
_PROVIDER_LINE_LABEL_RE = re.compile(
    r"""(?im)^[ \t]*(?:CC\s+REFERRED\s+PHYSICIAN|REFERRED\s+PHYSICIAN|REFERRING\s+PHYSICIAN|
        PRIMARY\s+CARE\s+PHYSICIAN|ATTENDING(?:\s+PHYSICIAN)?|SURGEON|ASSISTANT|
        ANESTHESIOLOGIST|FELLOW|RESIDENT|COSIGNED\s+BY|SIGNED\s+BY|DICTATED\s+BY|
        PERFORMED\s+BY|AUTHORED\s+BY|APPROVED\s+BY|ELECTRONICALLY\s+SIGNED\s+BY|
        PROVIDER|PROCEDURALIST(?:s|\(s\))?|OPERATOR)\s*:\s*""",
    re.VERBOSE,
)
_STAFF_ROLE_LINE_RE = re.compile(r"(?im)^[ \t]*(?:RN|RT|PA|NP|MA|CNA)\s*:\s*")

_SECTION_HEADER_WORDS: frozenset[str] = frozenset(
    {
        "DISPOSITION", "SPECIMEN", "SPECIMEN(S)", "SAMPLE", "SAMPLES", "IMPRESSION",
        "PLAN", "PROCEDURE", "PROCEDURES", "ATTENDING", "ASSISTANT", "ANESTHESIA",
        "MONITORING", "TRACHEA", "BRUSH", "CRYOBIOPSY", "MEDIASTINAL", "MEDIA",
        "SIZE", "FLUID", "LARYNX", "PHARYNX", "FINDINGS", "COMPLICATIONS", "INDICATION",
        "DESCRIPTION", "DISCHARGE", "RECOMMENDATION", "DISCUSSION", "METRICS", 
        "BIRTH DATE", "PATIENT STATUS", "PHYSICIAN", "ATTENDING PHYSICIAN"
    }
)

_LOCATION_WORKFLOW_WORDS: frozenset[str] = frozenset(
    {
        "await", "awaiting", "pending", "scheduled", "sequential", "symptomatic",
        "asymptomatic", "discharge", "recurrent", "telemetry", "observe",
    }
)
_PERSON_NAME_PUNCT_RE = re.compile(r"[^\w\s\-'. ,]")
_CLINICAL_CONTEXT_RE = re.compile(
    r"\b(?:pacu|ventilat(?:ion)?|onc|ct\s+surgery|rad\s+onc|fluoro|navigation|"
    r"granulom(?:a|as)?|cultures?|emphysema|ptx|talc|spray(?:ed)?|"
    r"sed(?:ation)?|mod\s+sed|abx|decadron|augmentin|ebus|bal|blvr|"
    r"thoracoscopy|debulking|rigid|carcinoid|adenopath(?:y|ic)|adeno|sarcoid|"
    r"laryngospasm|mesothelioma|seldinger|apc|rfa|jet\s+vent(?:ilation)?|"
    r"telemetry|discharge|recurrent|monitoring|description|wash|path|re-?expanded)\b",
    re.IGNORECASE,
)

_SHORT_CLINICAL_TOKENS: frozenset[str] = frozenset(
    {"mm", "cm", "mg", "mcg", "g", "ml", "cc", "fr", "iv", "cv", "ir", "te", "m", "reg"}
)
_CLINICAL_ABBREV_TOKENS: frozenset[str] = frozenset(
    {
        "bal", "ebus", "blvr", "ptx", "rfa", "apc", "mac", "abx", "epi", "peds",
        "onco", "lul", "lll", "rml", "rll", "rul", "lingula", "lml", "mod", "sed",
        "ipc", "loc", "drng", "dx", "hx", "tx", "fx", "sx", "iv", "po", "prn",
        "nav", "em", "er", "ncci",
    }
)
_NON_NAME_TOKENS: frozenset[str] = frozenset(
    {
        "moderate", "standard", "complete", "continue", "determine", "discharge",
        "recurrent", "observe", "observed", "monitoring", "continuous",
        "description", "unknown", "insert", "found", "looked", "frozen",
        "resultant", "subsequent", "sprayed", "wedged", "sampled", "employed",
        "combined", "superior", "large", "small", "path", "telemetry", "wash",
        "suite", "stuck", "decay", "cancer", "reg", "neg", "pos", "pro", "pre",
        "post", "intra", "antibiotics",
        "addl", "debulk", "drop", "due", "freezing", "guidance", "inserted",
        "juxta", "kinda", "loaded", "marker", "max", "messy", "mgmt", "mini",
        "obs", "primary", "refer", "resume", "scan", "screening", "sequential",
        "sputum", "transfer", "wean", "withdrew", "signed", "rounded", "short",
        "minimal", "significant", "successful", "prepared", "reduce", "remain"
    }
)
_NON_NAME_LEADERS: frozenset[str] = frozenset(
    {
        "continue", "determine", "complete", "start", "insert", "found", "employed",
        "combined", "subsequent", "resultant", "monitoring", "description",
        "unknown", "discharge", "recurrent", "observe", "observed", "looked",
        "sprayed", "wedged", "frozen", "moderate", "standard", "nodes", "large",
        "small", "superior", "findings", "electronically", "inserted", "loaded",
        "withdrew", "resume", "refer", "minimal", "significant", "successful"
    }
)
_LOBE_ABBREV_RE = re.compile(r"\b(?:rul|rml|rll|lul|lll|lml|lingula)\b", re.IGNORECASE)
_BAL_LOBE_RE = re.compile(r"\b(?:bal|lavage)\s+(?:rul|rml|rll|lul|lll|lml|lingula)\b", re.IGNORECASE)
_LOBE_BAL_RE = re.compile(r"\b(?:rul|rml|rll|lul|lll|lml|lingula)\s+bal\b", re.IGNORECASE)
_PROVIDER_TOKEN_RE = re.compile(r"\b(md|do|rn|pa|np|phd)\b", re.IGNORECASE)

_ALLOWLIST_BOUNDARY_RE = re.compile(
    r"(?i)\b(?:"
    + "|".join(sorted((re.escape(t) for t in CLINICAL_ALLOW_LIST), key=len, reverse=True))
    + r")\b"
)

_DEVICE_MODEL_CONTEXT_RE = re.compile(
    r"\b(?:(?:Ref|Lot|Model|SN|ID)\s*[:#]?\s*)?"
    r"(?:[A-Z]{1,3}\d{2,4}|[A-Z]{1,3}-[A-Z0-9]{2,10})\b"
    r"(?=[^\n]{0,20}\b(?:video bronchoscope|bronchoscope|scope|cryoprobe|needle|catheter)\b)",
    re.IGNORECASE,
)

_MRN_LABEL_PATTERN = (
    r"(?:MRN|MED(?:ICAL)?\s*REC(?:ORD)?(?:\s*(?:NO|NUMBER))?"
    r"|PATIENT\s*ID|DOD\s*ID|EDIPI)"
)
_MRN_ID_LINE_RE = re.compile(rf"(?i)\b{_MRN_LABEL_PATTERN}\b\s*[:#]")

_ADDRESS_STATE_ZIP_RE = re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b")
_ADDRESS_UNIT_TOKENS = r"(?:#|Apt\.?|Apartment|Unit|Ste\.?|Suite|Fl\.?|Floor|Rm\.?|Room)"
_ADDRESS_DR_SUFFIX = rf"Dr(?=\.?\s*(?:$|,|{_ADDRESS_UNIT_TOKENS}\b))"
_ADDRESS_SUFFIX_PATTERN = (
    r"St\.?|Street|Ave\.?|Avenue|Blvd\.?|Boulevard|Rd\.?|Road|"
    + _ADDRESS_DR_SUFFIX +
    r"|Drive|Ln\.?|Lane|Way|Ct\.?|Court|Pl\.?|Place|Ter\.?|Terrace|"
    r"Pkwy\.?|Parkway|Hwy\.?|Highway|Cir\.?|Circle"
)
_ADDRESS_STREET_LINE_RE = re.compile(
    rf"(?im)^[ \t]*\d{{1,6}}\s+.+\b(?:{_ADDRESS_SUFFIX_PATTERN})\b.*$"
)
_ADDRESS_MAILCODE_RE = re.compile(r"\bMC\s*\d{3,6}\b", re.IGNORECASE)

_CPT_HINT_RE = re.compile(r"\b(?:CPT|HCPCS|ICD-?10|ICD)\b", re.IGNORECASE)
_CPT_CODE_RE = re.compile(r"\b(?<!/)\d{5}[A-Z0-9]{0,4}\b", re.IGNORECASE)
_PROCEDURE_CONTEXT_RE = re.compile(
    r"\b(?:bronch(?:o(?:scope|scopy))?|bronchoscopic|biopsy|lavage|ablation|"
    r"catheter|stent|anesth(?:esia)?|sedat(?:ion)?|mod\s+sed|procedure|"
    r"surg(?:ery)?|resection|scope|radiology|pathology|specimen|culture|"
    r"bal|ebus|blvr|ptx|rfa|apc|talc|spray(?:ed)?|thoracoscopy|debulking|"
    r"rigid|carcinoid|adenopath(?:y|ic)|sarcoid|laryngospasm|mesothelioma|"
    r"seldinger|augmentin|decadron|emphysema|jet\s+vent(?:ilation)?|"
    r"telemetry|discharge|recurrent|wash|hemostasis|forceps|cryo|nodes?|"
    r"sampled|sample|mod|thermoplasty|thoracostomy|stenting|fibrin|"
    r"glidescope|doppler|laryngoscope|ultrathin|volumetric|ion|monarch|"
    r"storz|photofrin|temoporfin|pleurx|pneumostat|surgicel|"
    r"tracheomalacia|tracheobronchomalacia|melanoma|thymoma|schwannoma)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float
    source: str | None = None


@dataclass(frozen=True)
class RedactionPolicy:
    name: str
    redact_entity_types: frozenset[str]
    redact_provider_names: bool
    redact_facilities: bool
    pseudonymize_names: bool
    allowlist_contextual: bool = False
    allowlist_overlap_threshold: float = DEFAULT_ALLOWLIST_OVERLAP_THRESHOLD


def _detection_key(d: Detection) -> tuple[str, int, int, float, str | None]:
    return (d.entity_type, d.start, d.end, d.score, d.source)


def _diff_removed(before: list[Detection], after: list[Detection]) -> list[Detection]:
    remaining: dict[tuple[str, int, int, float], int] = {}
    for d in after:
        key = _detection_key(d)
        remaining[key] = remaining.get(key, 0) + 1

    removed: list[Detection] = []
    for d in before:
        key = _detection_key(d)
        count = remaining.get(key, 0)
        if count > 0:
            remaining[key] = count - 1
            continue
        removed.append(d)
    return removed


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


DEFAULT_REDACTION_ENTITIES: frozenset[str] = frozenset(
    {
        "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "LOCATION",
        "MEDICAL_LICENSE", "MRN", "US_DRIVER_LICENSE", "DATE_TIME", "ADDRESS",
        "AGE_OVER_90",
    }
)

_POLICY_PRESETS: dict[str, RedactionPolicy] = {
    "clinical": RedactionPolicy(
        name="clinical",
        redact_entity_types=DEFAULT_REDACTION_ENTITIES,
        redact_provider_names=False,
        redact_facilities=False,
        pseudonymize_names=False,
    ),
    "limited": RedactionPolicy(
        name="limited",
        redact_entity_types=DEFAULT_REDACTION_ENTITIES,
        redact_provider_names=True,
        redact_facilities=False,
        pseudonymize_names=False,
    ),
    "safe_harbor": RedactionPolicy(
        name="safe_harbor",
        redact_entity_types=DEFAULT_REDACTION_ENTITIES,
        redact_provider_names=True,
        redact_facilities=True,
        pseudonymize_names=False,
    ),
}


def _parse_entity_list(value: str | None) -> frozenset[str] | None:
    if not value:
        return None
    entities = {part.strip().upper() for part in value.split(",") if part.strip()}
    return frozenset(entities) if entities else None


def _parse_float(value: str | None, default: float) -> float:
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _load_redaction_policy() -> RedactionPolicy:
    mode = os.getenv("PHI_REDACTION_MODE", "clinical").strip().lower()
    mode_key = mode.replace("-", "_")
    base = _POLICY_PRESETS.get(mode_key, _POLICY_PRESETS["clinical"])

    redact_entities = _parse_entity_list(os.getenv("PHI_REDACTION_ENTITIES")) or base.redact_entity_types
    redact_providers = _env_flag("PHI_REDACT_PROVIDERS", base.redact_provider_names)
    redact_facilities = _env_flag("PHI_REDACT_FACILITIES", base.redact_facilities)
    pseudonymize_names = _env_flag("PHI_PSEUDONYMIZE_NAMES", base.pseudonymize_names)
    allowlist_contextual = _env_flag("PHI_ALLOWLIST_CONTEXTUAL", base.allowlist_contextual)
    overlap_threshold = _parse_float(
        os.getenv("PHI_ALLOWLIST_OVERLAP_THRESHOLD"), base.allowlist_overlap_threshold
    )
    overlap_threshold = max(0.0, min(1.0, overlap_threshold))

    return RedactionPolicy(
        name=base.name,
        redact_entity_types=redact_entities,
        redact_provider_names=redact_providers,
        redact_facilities=redact_facilities,
        pseudonymize_names=pseudonymize_names,
        allowlist_contextual=allowlist_contextual,
        allowlist_overlap_threshold=overlap_threshold,
    )


def _parse_score_thresholds(value: str | None) -> dict[str, float]:
    if not value:
        return dict(DEFAULT_ENTITY_SCORE_THRESHOLDS)
    thresholds: dict[str, float] = dict(DEFAULT_ENTITY_SCORE_THRESHOLDS)
    for part in value.split(","):
        if not part.strip():
            continue
        if ":" not in part:
            continue
        entity, raw_score = part.split(":", 1)
        entity = entity.strip().upper()
        try:
            thresholds[entity] = float(raw_score.strip())
        except ValueError:
            continue
    return thresholds


def _is_allowlisted(detected_text: str) -> bool:
    stripped = detected_text.strip().lower()
    if stripped in CLINICAL_ALLOW_LIST:
        return True
    return _ALLOWLIST_BOUNDARY_RE.search(detected_text) is not None


def _is_structured_entity(entity_type: str) -> bool:
    return entity_type.upper() in STRUCTURED_ENTITY_TYPES


def _normalize_terms(terms: Iterable[str]) -> tuple[str, ...]:
    cleaned = {t.strip() for t in terms if t and t.strip()}
    return tuple(sorted(cleaned, key=len, reverse=True))


@lru_cache()
def _compile_allowlist_re(terms: tuple[str, ...]) -> re.Pattern:
    pattern = r"(?i)\b(?:"
    pattern += "|".join(re.escape(t) for t in terms)
    pattern += r")\b"
    return re.compile(pattern)


def _allowlist_terms_for_policy(policy: RedactionPolicy | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    active = policy or _load_redaction_policy()
    terms = set(CLINICAL_ALLOW_LIST)
    if active.redact_facilities:
        terms -= set(FACILITY_ALLOW_LIST)
    if active.allowlist_contextual:
        safe_terms = terms - set(AMBIGUOUS_ALLOW_LIST)
        contextual_terms = terms & set(AMBIGUOUS_ALLOW_LIST)
    else:
        safe_terms = terms
        contextual_terms = set()
    return _normalize_terms(safe_terms), _normalize_terms(contextual_terms)


def build_allowlist_spans(text: str, policy: RedactionPolicy | None = None) -> list[tuple[int, int]]:
    safe_terms, contextual_terms = _allowlist_terms_for_policy(policy)
    spans: list[tuple[int, int]] = []
    if safe_terms:
        pattern = _compile_allowlist_re(safe_terms)
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    if contextual_terms:
        pattern = _compile_allowlist_re(contextual_terms)
        for m in pattern.finditer(text):
            context = _context_window(text, m.start(), m.end(), window=40).lower()
            if _CONTEXTUAL_ALLOWLIST_RE.search(context):
                spans.append((m.start(), m.end()))
    if not spans:
        return []
    return sorted(set(spans), key=lambda s: (s[0], s[1]))


def _overlaps_allowlist(start: int, end: int, spans: list[tuple[int, int]], threshold: float) -> bool:
    det_len = end - start
    if det_len <= 0:
        return False
    for span_start, span_end in spans:
        overlap_start = max(start, span_start)
        overlap_end = min(end, span_end)
        if overlap_end <= overlap_start:
            continue
        overlap_len = overlap_end - overlap_start
        if (overlap_len / det_len) >= threshold:
            return True
    return False


def sanitize_length_preserving(text: str) -> str:
    """Replace invisible/formatting marks without shifting offsets."""
    if not text:
        return text
    return text.translate(ZERO_WIDTH_TRANSLATION_TABLE)


def extract_patient_names(text: str) -> list[str]:
    names: set[str] = set()
    for m in PATIENT_NAME_LINE_RE.finditer(text):
        names.add(m.group("name").strip())
    return sorted(names, key=len, reverse=True)


def forced_patient_name_detections(text: str, names: Iterable[str]) -> list[Detection]:
    detections: list[Detection] = []
    for name in names:
        if not name:
            continue
        pattern = re.compile(rf"(?i)\b{re.escape(name)}\b")
        for m in pattern.finditer(text):
            detections.append(
                Detection(
                    entity_type="PERSON",
                    start=m.start(),
                    end=m.end(),
                    score=1.0,
                    source="forced_patient_name",
                )
            )
    return detections


def _valid_hhmm(token: str) -> bool:
    if not token.isdigit() or len(token) not in {3, 4}:
        return False
    if len(token) == 3:
        hour = int(token[0])
        minute = int(token[1:])
    else:
        hour = int(token[:2])
        minute = int(token[2:])
    return 0 <= hour <= 23 and 0 <= minute <= 59


def detect_hipaa_ages(text: str) -> list[Detection]:
    """Detect ages over 89 for HIPAA compliance (must be redacted)."""
    detections: list[Detection] = []
    for m in AGE_OVER_90_RE.finditer(text):
        detections.append(
            Detection(
                entity_type="AGE_OVER_90",
                start=m.start(),
                end=m.end(),
                score=1.0,
                source="regex_hipaa_age"
            )
        )
    return detections


def detect_datetime_detections(text: str) -> list[Detection]:
    detections: list[Detection] = []
    seen: set[tuple[int, int, str]] = set()

    def _add(start: int, end: int, source: str) -> None:
        key = (start, end, "DATE_TIME")
        if key in seen:
            return
        seen.add(key)
        detections.append(Detection(entity_type="DATE_TIME", start=start, end=end, score=1.0, source=source))

    for m in _DATETIME_ISO_RE.finditer(text): _add(m.start(), m.end(), "regex_datetime_iso")
    for m in _DATETIME_SLASH_TIME_COLON_RE.finditer(text): _add(m.start(), m.end(), "regex_datetime_time_colon")
    for m in _DATETIME_SLASH_TIME_COMPACT_RE.finditer(text):
        if _valid_hhmm(m.group(0).split()[-1]): _add(m.start(), m.end(), "regex_datetime_time_compact")

    for m in _DATE_NUMERIC_RE.finditer(text): _add(m.start(), m.end(), "regex_date_numeric")
    for m in _DATE_ISO_RE.finditer(text): _add(m.start(), m.end(), "regex_date_iso")
    for m in _DATE_TEXT_MONTH_FIRST_RE.finditer(text): _add(m.start(), m.end(), "regex_date_text")
    for m in _DATE_TEXT_DAY_FIRST_RE.finditer(text): _add(m.start(), m.end(), "regex_date_text")
    for m in _DATE_COMPACT_TEXT_RE.finditer(text): _add(m.start(), m.end(), "regex_date_compact")

    return detections


def detect_address_detections(text: str) -> list[Detection]:
    detections: list[Detection] = []
    for m in _ADDRESS_STREET_LINE_RE.finditer(text):
        line_start, line_end = m.span()
        detections.append(
            Detection(entity_type="ADDRESS", start=line_start, end=line_end, score=1.0, source="regex_address_line")
        )

        if line_end < len(text):
            next_start = line_end + 1
            next_end = text.find("\n", next_start)
            if next_end == -1: next_end = len(text)
            next_line = text[next_start:next_end]
            if _ADDRESS_STATE_ZIP_RE.search(next_line):
                detections.append(
                    Detection(
                        entity_type="ADDRESS",
                        start=next_start,
                        end=next_end,
                        score=1.0,
                        source="regex_address_line_continuation",
                    )
                )

    for m in _ADDRESS_STATE_ZIP_RE.finditer(text):
        detections.append(
            Detection(entity_type="ADDRESS", start=m.start(), end=m.end(), score=1.0, source="regex_state_zip")
        )

    for m in _ADDRESS_MAILCODE_RE.finditer(text):
        detections.append(
            Detection(entity_type="ADDRESS", start=m.start(), end=m.end(), score=0.95, source="regex_mail_code")
        )

    return detections


# --- FILTERS ---

def filter_allowlisted_terms(
    text: str,
    results: list,
    *,
    allowlist_spans: list[tuple[int, int]] | None = None,
    policy: RedactionPolicy | None = None,
    overlap_threshold: float | None = None,
) -> list:
    """Drop detections whose spans overlap allow-listed terms."""
    if not results:
        return results
    active_policy = policy or _load_redaction_policy()
    if overlap_threshold is None:
        overlap_threshold = active_policy.allowlist_overlap_threshold
    if allowlist_spans is None:
        allowlist_spans = build_allowlist_spans(text, active_policy)
    if not allowlist_spans:
        return results

    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if getattr(res, "source", None) == "forced_patient_name" or _is_structured_entity(entity_type):
            filtered.append(res)
            continue
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        if _overlaps_allowlist(start, end, allowlist_spans, overlap_threshold):
            continue
        filtered.append(res)
    return filtered


def filter_technical_context(text: str, results: list) -> list:
    """Filter out False Positives for locations/organizations in technical contexts."""
    tech_keywords = {"firewall", "server", "drive", "folder", "pacs", "cloud", "portal", "system", "database", "emr", "ehr", "network", "wifi"}
    filtered = []
    for res in results:
        if res.entity_type not in ("LOCATION", "ORGANIZATION"):
            filtered.append(res)
            continue
        context = _context_window(text, res.start, res.end, window=30).lower()
        if any(kw in context for kw in tech_keywords):
            continue
        filtered.append(res)
    return filtered


def filter_icd_codes(text: str, results: list) -> list:
    """Filter out ICD-10 codes that get detected as People/Locations."""
    filtered = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if entity_type not in {"PERSON", "LOCATION"} or getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        detected_text = text[int(res.start) : int(res.end)]
        if _ICD_CODE_RE.match(detected_text):
            continue
        filtered.append(res)
    return filtered


def filter_eponyms(text: str, results: list) -> list:
    filtered: list = []
    suffix_pattern = re.compile(
        r"^\s+(" + "|".join(re.escape(s) for s in MEDICAL_EPONYM_SUFFIXES) + r")\b",
        re.IGNORECASE
    )
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "PERSON":
            filtered.append(res)
            continue
        end = int(getattr(res, "end"))
        suffix_window = text[end : min(len(text), end + 20)]
        if suffix_pattern.match(suffix_window):
            continue
        filtered.append(res)
    return filtered


def filter_structural_headers(text: str, results: list) -> list:
    header_spans = []
    for m in _DYNAMIC_HEADER_RE.finditer(text):
        header_spans.append((m.start(1), m.end(1)))
        
    if not header_spans:
        return results
        
    filtered: list = []
    for res in results:
        if getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        if any(start >= h_start and end <= h_end for h_start, h_end in header_spans):
            continue
        filtered.append(res)
    return filtered


def filter_dynamic_biomedical_shield(
    text: str,
    results: list,
    biomedical_nlp: Any | None = None,
    nlp_engine: Any | None = None,
    *,
    allowlist_spans: list[tuple[int, int]] | None = None,
    overlap_threshold: float = DEFAULT_ALLOWLIST_OVERLAP_THRESHOLD,
) -> list:
    if biomedical_nlp is None and nlp_engine is not None:
        try:
            biomedical_nlp = nlp_engine.nlp.get("en")
        except Exception:  # noqa: BLE001
            biomedical_nlp = None

    bio_spans: list[tuple[int, int]] = []
    if biomedical_nlp is not None:
        try:
            doc = biomedical_nlp(text)
            for ent in doc.ents:
                if ent.label_ in BIOMEDICAL_ENTITY_LABELS and ent.text.lower() not in BIOMEDICAL_SHIELD_BLOCKLIST:
                    bio_spans.append((ent.start_char, ent.end_char))
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Biomedical shield scan failed: {e}")
            bio_spans = []

    if not bio_spans and allowlist_spans:
        bio_spans = allowlist_spans

    if not bio_spans:
        return results

    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if entity_type not in BIOMEDICAL_SHIELD_TARGET_TYPES:
            filtered.append(res)
            continue
        if getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        r_start, r_end = int(res.start), int(res.end)
        if _overlaps_allowlist(r_start, r_end, bio_spans, overlap_threshold):
            continue
        filtered.append(res)
    return filtered


def filter_device_model_context(text: str, results: list) -> list:
    safe_spans: list[tuple[int, int]] = []
    for m in _DEVICE_MODEL_CONTEXT_RE.finditer(text):
        line_start, line_end = _line_bounds(text, m.start())
        line = text[line_start:line_end]
        if _MRN_ID_LINE_RE.search(line):
            continue
        safe_spans.append((m.start(), m.end()))

    if not safe_spans: return results

    filtered: list = []
    for res in results:
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        if any(start >= s and end <= e for s, e in safe_spans): continue
        filtered.append(res)
    return filtered


def filter_cpt_codes(text: str, results: list) -> list:
    safe_spans: list[tuple[int, int]] = []
    cursor = 0
    while cursor <= len(text):
        line_end = text.find("\n", cursor)
        if line_end == -1: line_end = len(text)
        line = text[cursor:line_end]
        if line.strip():
            if _CPT_HINT_RE.search(line):
                for m in _CPT_CODE_RE.finditer(line): safe_spans.append((cursor + m.start(), cursor + m.end()))
            elif re.match(r"^[ \t]*\d{5}[A-Z0-9]{0,4}\b", line) and not _ADDRESS_STREET_LINE_RE.match(line):
                for m in _CPT_CODE_RE.finditer(line): safe_spans.append((cursor + m.start(), cursor + m.end()))
        if line_end == len(text): break
        cursor = line_end + 1

    header_re = re.compile(r"(?im)^[ \t]*(?:PROCEDURE|CPT\s*CODES?|CODES?)\s*[:]")
    next_header_re = re.compile(r"(?im)^[ \t]*[A-Z][A-Za-z\s/]+[:]")
    lines = text.splitlines(keepends=True)
    current_pos = 0
    in_cpt_block = False
    for line in lines:
        if header_re.match(line): in_cpt_block = True
        elif in_cpt_block and next_header_re.match(line): in_cpt_block = False
        if in_cpt_block or "CPT" in line:
            for m in _CPT_CODE_RE.finditer(line): safe_spans.append((current_pos + m.start(), current_pos + m.end()))
        current_pos += len(line)

    if not safe_spans: return results
    filtered = []
    for res in results:
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        if any(start >= s and end <= e for s, e in safe_spans): continue
        filtered.append(res)
    return filtered


def filter_address_false_positives(text: str, results: list) -> list:
    """Drop address detections that look like procedure/code lines."""
    filtered = []
    
    # Enhanced narrative check to avoid flagging "68 y.o. male with..." as ADDRESS
    narrative_keywords = {"history", "presents", "male", "female", "y.o.", "year-old", "year old", "mass", "lesion", "nodule", "ct", "pet", "smoking", "pack-year"}
    
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "ADDRESS":
            filtered.append(res)
            continue
        start = int(getattr(res, "start"))
        line_start, line_end = _line_bounds(text, start)
        line = text[line_start:line_end]
        line_lower = line.lower()

        # Check for CPT/Procedure context
        if _CPT_HINT_RE.search(line):
            continue
        if _PROCEDURE_CONTEXT_RE.search(line_lower) and not _ADDRESS_STATE_ZIP_RE.search(line):
            if re.match(r"^[ \t]*\d{4,6}\b", line) or _CPT_CODE_RE.search(line):
                continue
                
        # Check for Narrative/History context (e.g. "68 y.o. male...")
        token_words = set(re.findall(r"\w+", line_lower))
        if len(token_words & narrative_keywords) >= 2:
             continue

        filtered.append(res)
    return filtered


def filter_credentials(text: str, results: list) -> list:
    filtered = []
    for res in results:
        norm = re.sub(r"[^A-Za-z0-9]", "", text[int(getattr(res, "start")) : int(getattr(res, "end"))]).upper()
        if norm not in _CREDENTIAL_NORMALIZED: filtered.append(res)
    return filtered


def filter_datetime_measurements(text: str, results: list) -> list:
    filtered = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "DATE_TIME":
            filtered.append(res)
            continue
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        if text[start:end].isdigit():
            tail = text[end : min(len(text), end + 12)]
            if _MEASUREMENT_UNIT_TAIL_RE.match(tail): continue
        filtered.append(res)
    return filtered


def filter_strict_datetime_patterns(text: str, results: list) -> list:
    filtered = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "DATE_TIME":
            filtered.append(res)
            continue
        candidate = text[int(getattr(res, "start")) : int(getattr(res, "end"))].strip()
        if (_DATE_NUMERIC_RE.fullmatch(candidate) or _DATE_ISO_RE.fullmatch(candidate) or
            _DATE_TEXT_MONTH_FIRST_RE.fullmatch(candidate) or _DATE_TEXT_DAY_FIRST_RE.fullmatch(candidate) or
            _DATETIME_ISO_RE.fullmatch(candidate) or _DATETIME_SLASH_TIME_COLON_RE.fullmatch(candidate) or
            (_DATETIME_SLASH_TIME_COMPACT_RE.fullmatch(candidate) and _valid_hhmm(candidate.split()[-1])) or
            _DATE_COMPACT_TEXT_RE.fullmatch(candidate)):
            filtered.append(res)
    return filtered


def _is_header_label_context(text: str, start: int, end: int) -> bool:
    token = text[start:end].strip()
    if not token or any(ch.islower() for ch in token) or not any(ch.isalpha() for ch in token): return False
    line_start, line_end = _line_bounds(text, start)
    line = text[line_start:line_end]
    if line[: start - line_start].strip(): return False
    suffix = line[end - line_start :]
    colon_idx = suffix.find(":")
    return colon_idx != -1 and colon_idx <= 40


def filter_person_location_false_positives(text: str, results: list) -> list:
    filtered = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() not in {"PERSON", "LOCATION"}:
            filtered.append(res)
            continue
        token = text[int(getattr(res, "start")) : int(getattr(res, "end"))].strip()
        if not token or any(ch.isdigit() for ch in token) or "/" in token or ":" in token: continue
        if token.upper() in _SECTION_HEADER_WORDS or _is_header_label_context(text, int(getattr(res, "start")), int(getattr(res, "end"))): continue
        filtered.append(res)
    return filtered


def filter_person_location_sanity(text: str, results: list) -> list:
    filtered = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if entity_type not in {"PERSON", "LOCATION"} or getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        token = text[int(getattr(res, "start")) : int(getattr(res, "end"))].strip()
        if not token:
            continue
        token_lower = token.lower()
        token_words = re.findall(r"[A-Za-z]+", token_lower)
        context = _context_window(text, int(getattr(res, "start")), int(getattr(res, "end")), window=40).lower()

        if token_lower in BIOMEDICAL_SHIELD_BLOCKLIST:
            continue
        if token_lower in _NON_NAME_TOKENS:
            continue
        # SPECIAL HANDLING: ROSE (Rapid On-Site Evaluation)
        if token.upper().startswith("ROSE"):
            rose_context = text[int(res.start) : int(res.end) + 50].lower()
            if _ROSE_CONTEXT_RE.search(rose_context):
                continue
        if any(token_lower.startswith(f"{leader} ") for leader in _NON_NAME_LEADERS):
            continue
        if any(word in _SHORT_CLINICAL_TOKENS or word in _CLINICAL_ABBREV_TOKENS for word in token_words):
            continue
        if len(token_words) > 1 and any(word in {"lung", "pleura", "pleural"} for word in token_words):
            continue
        if _BAL_LOBE_RE.search(token_lower) or _LOBE_BAL_RE.search(token_lower):
            continue
        if _PROCEDURE_CONTEXT_RE.search(token_lower) or _CLINICAL_CONTEXT_RE.search(token_lower):
            continue

        if entity_type == "PERSON":
            if _PERSON_NAME_PUNCT_RE.search(token):
                continue
            if token_lower.startswith("dr ") or token_lower.startswith("doctor "):
                continue
            if _PROVIDER_TOKEN_RE.search(token):
                continue
            # NEW: Filter known clinical terms appearing capitalized at sentence start or in lists
            if token_lower in {"hemoglobin", "hgb", "egfr", "pulmonary", "nose", "vc mode", "pmean", "dumon tracheal", "dumon"}:
                continue
                
            if token.isupper() and len(token) <= 4:
                if _PROCEDURE_CONTEXT_RE.search(context) or _CLINICAL_CONTEXT_RE.search(context):
                    continue
        else:
            if token_lower in _LOCATION_WORKFLOW_WORDS:
                continue
            if token.isupper() and len(token) == 2 and token in US_STATE_ABBREVS:
                continue
            if token.islower() and (
                _PROCEDURE_CONTEXT_RE.search(context) or _CLINICAL_CONTEXT_RE.search(context)
            ):
                continue
            if _PROCEDURE_CONTEXT_RE.search(context) or _CLINICAL_CONTEXT_RE.search(context):
                continue
                
            # NEW: Specific Location False Positives
            if token_lower in {"thoracoscope", "infiltrating", "attending physician"}:
                continue

        filtered.append(res)
    return filtered


def filter_person_provider_lines(text: str, results: list) -> list:
    provider_spans = []
    # Use m.end() to anchor the check to the content line, avoiding issues where
    # regex matches preceding newlines in multiline mode.
    for m in _PROVIDER_LINE_LABEL_RE.finditer(text): provider_spans.append(_line_bounds(text, m.end()))
    for m in _STAFF_ROLE_LINE_RE.finditer(text): provider_spans.append(_line_bounds(text, m.end()))
    
    if not provider_spans: return results
    
    patient_label_re = re.compile(r"^[ \t]*patient\s*:", re.IGNORECASE)
    filtered = []
    for res in results:
        # Only protect PERSON entities in provider lines. 
        # We definitely want to redact Dates found in these lines (signatures).
        if str(getattr(res, "entity_type", "")).upper() != "PERSON" or getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
            
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        line_start, line_end = _line_bounds(text, start)
        
        # Safety check: If the line actually says "Patient:", don't un-redact it.
        if patient_label_re.search(text[line_start:line_end].lstrip()):
            filtered.append(res)
            continue
            
        if any(start >= s and end <= e for s, e in provider_spans): continue
        filtered.append(res)
    return filtered


def filter_datetime_exclusions(text: str, results: list, relative_phrases: Iterable[str]) -> list:
    # Extended to include treatment days "Day 1"
    duration_re = re.compile(
        r"^\s*(?:\d+(?:\.\d+)?\s*(?:second|seconds|minute|minutes|hour|hours|day|days|week|weeks)|"
        r"(?:post-?op\s+)?day\s+\d+)\b",
        re.IGNORECASE,
    )
    short_numeric_date_re = re.compile(r"^\s*\d{1,2}[-/]\d{1,2}[-/]\d{1,2}\s*$")
    relative_res = [re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in relative_phrases]
    filtered = []
    for res in results:
        if getattr(res, "entity_type", None) != "DATE_TIME":
            filtered.append(res)
            continue
        token = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if short_numeric_date_re.match(token):
            continue
        if duration_re.search(token): continue
        if any(r.search(token) for r in relative_res): continue
        filtered.append(res)
    return filtered


def filter_low_score_results(results: list, thresholds: dict[str, float]) -> list:
    filtered = []
    for res in results:
        score = float(getattr(res, "score", 0.0) or 0.0)
        min_score = thresholds.get(str(getattr(res, "entity_type", "")).upper(), thresholds.get("__DEFAULT__", 0.0))
        if score >= min_score: filtered.append(res)
    return filtered


def select_non_overlapping_results(results: list) -> list:
    entity_priority = {
        "AGE_OVER_90": 95,  # High priority to resolve conflicts with Generic Dates/Numbers
        "MRN": 100, "US_SSN": 95, "EMAIL_ADDRESS": 90, "PHONE_NUMBER": 90, 
        "ADDRESS": 85, "DATE_TIME": 80, "PERSON": 70, "LOCATION": 60, 
        "MEDICAL_LICENSE": 50, "US_DRIVER_LICENSE": 50
    }
    def _key(r):
        return (entity_priority.get(str(getattr(r, "entity_type", "")).upper(), 0), 
                float(getattr(r, "score", 0.0) or 0.0), 
                int(getattr(r, "end")) - int(getattr(r, "start")), 
                -int(getattr(r, "start")))
    selected = []
    for res in sorted(results, key=_key, reverse=True):
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        if any(start < int(getattr(s, "end")) and end > int(getattr(s, "start")) for s in selected): continue
        selected.append(res)
    return sorted(selected, key=lambda r: int(getattr(r, "start")))


def filter_provider_signature_block(text: str, results: list) -> list:
    header = re.search(r"(?im)^recommendations:\s*$", text)
    zone_start = header.start() if header else int(len(text) * 0.75)
    cred_re = re.compile(r"(?:,\s*)?(md|do)\b", re.IGNORECASE)
    service_re = re.compile(r"\binterventional\s+pulmonology\b", re.IGNORECASE)
    filtered = []
    for res in results:
        if getattr(res, "entity_type", None) != "PERSON" or int(getattr(res, "start")) < zone_start:
            filtered.append(res)
            continue
        line_start, line_end = _line_bounds(text, int(getattr(res, "start")))
        line = text[line_start:line_end]
        if cred_re.search(line) and service_re.search(line): continue
        filtered.append(res)
    return filtered


def _line_bounds(text: str, index: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    return start, end if end != -1 else len(text)


def _context_window(text: str, start: int, end: int, window: int = 40) -> str:
    return text[max(0, start - window) : min(len(text), end + window)]


def filter_person_provider_context(text: str, results: list) -> list:
    """Context-aware provider protection (e.g. 'Dr. Smith', 'Jane Doe, MD')."""
    patient_label_re = re.compile(r"^[ \t]*patient\s*:", re.IGNORECASE)
    dr_prefix_re = re.compile(r"\b(dr\.?|doctor)\s*$", re.IGNORECASE)
    provider_inline_label_re = re.compile(
        r"\b(surgeon|assistant|anesthesiologist|attending|fellow|resident|proceduralist|cosigned\s+by|dictated\s+by|signed\s+by)\b\s*:\s*$",
        re.IGNORECASE
    )
    # Increased lookahead window to catch trailing credentials like "Name, MD, PhD"
    credential_suffix_re = re.compile(r"^\s*,?.{0,50}\s*(md|do|rn|pa|np)\b", re.IGNORECASE)
    # If a PERSON span is immediately followed by an MRN label, treat it as a patient-header name
    # even if "MD" appears later on the same line (e.g. "Last, First MRN: ... SURGEON: X MD").
    mrn_label_after_name_re = re.compile(rf"^\s*(?:{_MRN_LABEL_PATTERN})\b\s*[:#]", re.IGNORECASE)
    
    filtered = []
    for res in results:
        if getattr(res, "entity_type", None) != "PERSON" or getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        res_start, res_end = int(getattr(res, "start")), int(getattr(res, "end"))
        line_start, line_end = _line_bounds(text, res_start)
        # Always redact if on a 'Patient:' line
        if patient_label_re.search(text[line_start:line_end].lstrip()):
            filtered.append(res)
            continue

        # Keep patient header names like "Aronson, Gary MRN: 11207396 ..."
        # regardless of later provider credentials on the same line.
        suffix_in_line = text[res_end:line_end]
        if mrn_label_after_name_re.match(suffix_in_line):
            filtered.append(res)
            continue
        
        prefix = text[max(0, res_start - 20) : res_start]
        suffix = text[res_end : min(line_end, res_end + 60)]
        
        if provider_inline_label_re.search(prefix) or dr_prefix_re.search(prefix) or credential_suffix_re.match(suffix):
            continue
            
        filtered.append(res)
    return filtered


def redact_with_audit(
    *,
    text: str,
    detections: list[Detection],
    enable_driver_license_recognizer: bool,
    score_thresholds: dict[str, float],
    relative_datetime_phrases: Iterable[str],
    nlp_backend: str | None = None,
    nlp_model: str | None = None,
    requested_nlp_model: str | None = None,
    nlp_engine: Any | None = None,  # New: Access to analyzer.nlp_engine
    biomedical_nlp: Any | None = None,
    redaction_policy: RedactionPolicy | None = None,
) -> tuple[ScrubResult, dict[str, Any]]:
    
    if not text:
        return ScrubResult("", []), {"detections": [], "removed_detections": [], "redacted_text": ""}
    
    policy = redaction_policy or _load_redaction_policy()
    raw = [
        d for d in detections
        if str(getattr(d, "entity_type", "")).upper() in policy.redact_entity_types
    ]
    allowlist_spans = build_allowlist_spans(text, policy)
    removed: list[dict[str, Any]] = []

    def _record_removed(before: list[Detection], after: list[Detection], reason: str) -> None:
        for d in _diff_removed(before, after):
            removed.append({
                "reason": reason, "entity_type": d.entity_type, "start": d.start, "end": d.end,
                "score": d.score, "source": d.source, "detected_text": text[d.start : d.end],
                "surrounding_context": _context_window(text, d.start, d.end)
            })

    # 1. Contextual Provider Protection
    if policy.redact_provider_names:
        step0 = raw
    else:
        step0 = filter_person_provider_lines(text, raw)
        step0 = filter_person_provider_context(text, step0)
        step0 = filter_provider_signature_block(text, step0)
        _record_removed(raw, step0, "provider_context")

    # 2. Dynamic Guards (Headers, Eponyms, Biomedical)
    step1 = filter_structural_headers(text, step0)
    _record_removed(step0, step1, "dynamic_header")
    
    step2 = filter_eponyms(text, step1)
    _record_removed(step1, step2, "medical_eponym")
    
    # This is the primary robustness upgrade: leveraging scispacy or allowlist fallback
    step3 = filter_dynamic_biomedical_shield(
        text,
        step2,
        biomedical_nlp,
        nlp_engine,
        allowlist_spans=allowlist_spans,
        overlap_threshold=policy.allowlist_overlap_threshold,
    )
    # If we don't have a biomedical model, `filter_dynamic_biomedical_shield` falls back to using
    # allowlist spans for protection. In that case, removed detections should be attributed to
    # the allowlist for audit/contract purposes.
    bio_reason = "biomedical_shield"
    if biomedical_nlp is None and allowlist_spans:
        bio_reason = "allowlist"
    _record_removed(step2, step3, bio_reason)

    # 3. Technical Filters
    step4a = filter_device_model_context(text, step3)
    _record_removed(step3, step4a, "device_model")
    step4b = filter_credentials(text, step4a)
    _record_removed(step4a, step4b, "credentials")
    step4c = filter_cpt_codes(text, step4b)
    _record_removed(step4b, step4c, "procedure_codes")
    step4d = filter_technical_context(text, step4c) # New: Technical Context (Folders, Servers)
    _record_removed(step4c, step4d, "technical_filters")
    step4e = filter_icd_codes(text, step4d)         # New: ICD-10 Code filter
    _record_removed(step4d, step4e, "icd_codes")

    # 4. Address Filters
    step4f = filter_address_false_positives(text, step4e)
    _record_removed(step4e, step4f, "address_filters")

    # 5. Date/Time Logic
    step5a = filter_datetime_exclusions(text, step4f, relative_datetime_phrases)
    _record_removed(step4f, step5a, "duration_datetime")
    step5b = filter_datetime_measurements(text, step5a)
    _record_removed(step5a, step5b, "datetime_measurement")
    step5c = filter_strict_datetime_patterns(text, step5b)
    _record_removed(step5b, step5c, "datetime_logic")

    # 6. Allowlist (Span-based)
    step6 = filter_allowlisted_terms(text, step5c, allowlist_spans=allowlist_spans, policy=policy)
    _record_removed(step5c, step6, "allowlist")

    # 7. Header False Positives & Scoring
    step7a = filter_person_location_false_positives(text, step6)
    _record_removed(step6, step7a, "header_false_positive")
    step7b = filter_person_location_sanity(text, step7a)
    _record_removed(step7a, step7b, "header_false_positive")
    step7c = filter_low_score_results(step7b, score_thresholds)
    _record_removed(step7b, step7c, "low_score")

    # 8. Final Selection
    final = select_non_overlapping_results(step7c)
    _record_removed(step7c, final, "overlap_resolution")

    # Custom placeholders for specific entity types to support registry value extraction
    CUSTOM_PLACEHOLDERS = {
        "AGE_OVER_90": ">90"  # HIPAA Safe Harbor aggregation
    }

    name_map: dict[str, str] = {}

    def _person_key(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def _placeholder_for(detection: Detection) -> str:
        entity_type = str(detection.entity_type).upper()
        if entity_type == "PERSON" and policy.pseudonymize_names:
            key = _person_key(text[detection.start : detection.end])
            if not key:
                return "<PERSON>"
            if key not in name_map:
                name_map[key] = f"<PERSON_{len(name_map) + 1}>"
            return name_map[key]
        return CUSTOM_PLACEHOLDERS.get(entity_type, f"<{entity_type}>")

    scrubbed_text = text
    entities = []
    # Apply redactions in reverse order to preserve indices
    for d in sorted(final, key=lambda r: r.start, reverse=True):
        # Use custom placeholder if defined, otherwise default to <ENTITY_TYPE>
        placeholder = _placeholder_for(d)
        
        scrubbed_text = scrubbed_text[: d.start] + placeholder + scrubbed_text[d.end :]
        entities.append({
            "placeholder": placeholder, "entity_type": d.entity_type, 
            "original_start": d.start, "original_end": d.end
        })
    
    entities = list(reversed(entities))
    
    detections_report = [
        {"entity_type": d.entity_type, "text": text[d.start:d.end], "score": d.score} 
        for d in raw
    ]

    config = {
        "nlp_model": nlp_model,
        "redaction_mode": policy.name,
        "redact_provider_names": policy.redact_provider_names,
        "redact_facilities": policy.redact_facilities,
        "allowlist_contextual": policy.allowlist_contextual,
        "allowlist_overlap_threshold": policy.allowlist_overlap_threshold,
    }
    if biomedical_nlp is not None:
        config["biomedical_model"] = getattr(biomedical_nlp, "meta", {}).get("name")

    return ScrubResult(scrubbed_text, entities), {
        "config": config,
        "detections": detections_report,
        "removed_detections": removed,
        "redacted_text": scrubbed_text
    }


def _build_analyzer(model_name: str):
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult

    provider = NlpEngineProvider(
        nlp_configuration={"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": model_name}]}
    )
    nlp_engine = provider.create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    class _PatientLabelRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(supported_entity="PERSON", patterns=[
                Pattern("patient_label_line", r"(?im)^Patient:\s*.+$", 0.95),
                Pattern(
                    "name_then_mrn",
                    rf"(?im)^[ \t]*(?:(?:NAME|PATIENT)(?:\s+NAME)?\s*:\s*)?[A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+.*\b(?:{_MRN_LABEL_PATTERN})\b\s*[:#]",
                    0.95,
                )
            ], name="PATIENT_LABEL_NAME")
            self._patient_line = re.compile(
                rf"(?im)^Patient:\s*(.+?)(?:\s+(?:{_MRN_LABEL_PATTERN})\b\s*[:#].*)?$"
            )
            self._name_then_mrn = re.compile(
                rf"(?im)^[ \t]*(?:(?:NAME|PATIENT)(?:\s+NAME)?\s*:\s*)?"
                rf"([A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)?)"
                rf"(?=\s+(?:{_MRN_LABEL_PATTERN})\b\s*[:#])"
            )
        def analyze(self, text, entities, nlp_artifacts=None):
            results = []
            if "PERSON" not in entities: return results
            for m in self._patient_line.finditer(text):
                start, end = m.span(1)
                if end - start >= 2: results.append(RecognizerResult("PERSON", start, end, 0.95))
            for m in self._name_then_mrn.finditer(text):
                start, end = m.span(1)
                if end - start >= 2: results.append(RecognizerResult("PERSON", start, end, 0.95))
            return results
    analyzer.registry.add_recognizer(_PatientLabelRecognizer())

    class _InstitutionRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="LOCATION",
                patterns=[
                    Pattern("ucsd", r"(?i)\bUCSD\b", 0.95),
                    Pattern("nmcsd", r"(?i)\bNMCSD\b", 0.95),
                    Pattern("balboa", r"(?i)\bBalboa\b", 0.95),
                    Pattern("navy", r"(?i)\bNavy\b", 0.95),
                ],
                name="INSTITUTION_PATTERN",
            )
    analyzer.registry.add_recognizer(_InstitutionRecognizer())

    class _MrnRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="MRN",
                patterns=[
                    Pattern(
                        "mrn",
                        rf"(?i)\b{_MRN_LABEL_PATTERN}\b\s*[:#]\s*(?=[A-Z0-9-]*\d)[A-Z0-9][A-Z0-9-]{{3,}}\b",
                        0.95,
                    )
                ],
                name="MRN",
            )
            self._mrn = re.compile(
                rf"(?i)\b{_MRN_LABEL_PATTERN}\b\s*[:#]\s*((?=[A-Z0-9-]*\d)[A-Z0-9][A-Z0-9-]{{3,}})\b"
            )

        def analyze(self, text, entities, nlp_artifacts=None):
            results = []
            if "MRN" not in entities:
                return results
            for m in self._mrn.finditer(text):
                start, end = m.span(1)
                results.append(RecognizerResult(entity_type="MRN", start=start, end=end, score=0.95))
            return results
    analyzer.registry.add_recognizer(_MrnRecognizer())
    
    return analyzer


@lru_cache()
def _get_analyzer(model_name: str):
    try:
        analyzer = _build_analyzer(model_name)
        logger.info("PresidioScrubber initialized", extra={"model": model_name})
        return analyzer
    except Exception as exc:
        raise RuntimeError("PresidioScrubber initialization failed") from exc


@lru_cache()
def _get_spacy_model(model_name: str):
    import spacy

    return spacy.load(model_name)


class PresidioScrubber(PHIScrubberPort):
    """Presidio-powered scrubber with dynamic IP allowlist filtering."""

    def __init__(self, model_name: str | None = None):
        self.nlp_backend = os.getenv("NLP_BACKEND", "spacy").lower()
        default_model = "en_core_sci_sm" if self.nlp_backend == "scispacy" else "en_core_web_sm"
        self.requested_model_name = model_name or os.getenv("PRESIDIO_NLP_MODEL", default_model)
        
        fallbacks = ["en_core_web_sm", "en_core_web_md"]
        candidates = [self.requested_model_name] + [m for m in fallbacks if m != self.requested_model_name]

        for candidate in candidates:
            try:
                self._analyzer = _get_analyzer(candidate)
                self.model_name = candidate
                break
            except RuntimeError:
                continue
        
        if not hasattr(self, "_analyzer"):
            raise RuntimeError(f"Could not load any spaCy model from {candidates}")

        self.redaction_policy = _load_redaction_policy()
        self.enable_driver_license_recognizer = _env_flag("ENABLE_DRIVER_LICENSE_RECOGNIZER", False)
        self.score_thresholds = _parse_score_thresholds(os.getenv("PHI_ENTITY_SCORE_THRESHOLDS"))
        self.relative_datetime_phrases = tuple(p.strip() for p in os.getenv("PHI_DATE_TIME_RELATIVE_PHRASES", ",".join(DEFAULT_RELATIVE_DATE_TIME_PHRASES)).split(",") if p.strip())

        self.entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "LOCATION", "MEDICAL_LICENSE", "MRN"]
        if self.enable_driver_license_recognizer:
            self.entities.append("US_DRIVER_LICENSE")
        self.entities = [e for e in self.entities if e in self.redaction_policy.redact_entity_types]

        self.biomedical_model_name = None
        self._biomedical_nlp = None
        requested_bio_model = os.getenv("PHI_BIOMEDICAL_MODEL")
        if requested_bio_model:
            if requested_bio_model.strip().lower() not in {"none", "off", "false", "0"}:
                try:
                    self._biomedical_nlp = _get_spacy_model(requested_bio_model)
                    self.biomedical_model_name = requested_bio_model
                except Exception as exc:  # noqa: BLE001
                    logger.debug(f"Failed to load biomedical model '{requested_bio_model}': {exc}")

        if self._biomedical_nlp is None and self.nlp_backend == "scispacy":
            try:
                self._biomedical_nlp = self._analyzer.nlp_engine.nlp.get("en")
                self.biomedical_model_name = self.model_name
            except Exception as exc:  # noqa: BLE001
                logger.debug(f"Failed to reuse analyzer model for biomedical shield: {exc}")

        if self._biomedical_nlp is None:
            for candidate in ("en_core_sci_sm", "en_core_sci_md", "en_core_sci_lg"):
                try:
                    self._biomedical_nlp = _get_spacy_model(candidate)
                    self.biomedical_model_name = candidate
                    break
                except Exception:  # noqa: BLE001
                    continue

    def _analyze_detections(self, text: str) -> list[Detection]:
        results = self._analyzer.analyze(text=text, language="en", entities=self.entities)
        detections = []
        for r in results:
            start, end = int(r.start), int(r.end)
            span = text[start:end]
            if "\n" in span: end = start + span.find("\n")
            detections.append(Detection(str(r.entity_type), start, end, float(r.score)))
        return detections

    def scrub_with_audit(self, text: str, document_type: str | None = None, specialty: str | None = None) -> tuple[ScrubResult, dict[str, Any]]:
        sanitized = sanitize_length_preserving(text)
        policy = self.redaction_policy
        raw = self._analyze_detections(sanitized)

        forced_detections: list[Detection] = []
        if "PERSON" in policy.redact_entity_types:
            forced_names = extract_patient_names(sanitized)
            forced_detections = forced_patient_name_detections(sanitized, forced_names)

        datetime_detections: list[Detection] = []
        if "DATE_TIME" in policy.redact_entity_types:
            datetime_detections = detect_datetime_detections(sanitized)

        address_detections: list[Detection] = []
        if "ADDRESS" in policy.redact_entity_types:
            address_detections = detect_address_detections(sanitized)

        age_detections: list[Detection] = []
        if "AGE_OVER_90" in policy.redact_entity_types:
            age_detections = detect_hipaa_ages(sanitized)
        
        raw = raw + forced_detections + datetime_detections + address_detections + age_detections
        
        return redact_with_audit(
            text=sanitized,
            detections=raw,
            enable_driver_license_recognizer=self.enable_driver_license_recognizer,
            score_thresholds=self.score_thresholds,
            relative_datetime_phrases=self.relative_datetime_phrases,
            nlp_backend=self.nlp_backend,
            nlp_model=self.model_name,
            requested_nlp_model=self.requested_model_name,
            nlp_engine=self._analyzer.nlp_engine, # Pass NLP engine for dynamic biomedical check
            biomedical_nlp=self._biomedical_nlp,
            redaction_policy=policy,
        )

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        scrub_result, _ = self.scrub_with_audit(text, document_type=document_type, specialty=specialty)
        return scrub_result

__all__ = ["PresidioScrubber"]