"""Presidio-based scrubber adapter (Dynamic Clinical Context).

Implements PHIScrubberPort using Presidio AnalyzerEngine with enhanced
dynamic safeguards for clinical terms, providers, and HIPAA age rules.
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
# Captures: "92 yo", "92 year old", "Age: 92", "Aged 102"
# Avoids: "BP 120/92" (requires either "Age:" prefix OR "yo" suffix to be confident)
AGE_OVER_90_RE = re.compile(
    r"(?i)(?:\b(?:age|aged)\s*[:]?\s*(?:9\d|[1-9]\d{2,})\b)|(?:\b(?:9\d|[1-9]\d{2,})\s*-?\s*(?:yo|yrs?|years?|year-old|year\s+old)\b)"
)

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
_DYNAMIC_HEADER_RE = re.compile(
    r"^\s*([A-Z][A-Z0-9\s\/\-\(\)]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s*:\s*$",
    re.MULTILINE
)

# Terms that the Biomedical Shield should NOT protect (prevent un-redacting actual people)
BIOMEDICAL_SHIELD_BLOCKLIST = {
    "patient", "pt", "dr", "doctor", "mr", "ms", "mrs", "male", "female", 
    "man", "woman", "boy", "girl", "mother", "father", "son", "daughter",
    "husband", "wife", "spouse", "partner", "subject", "participant"
}

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
    "note", "report", "review"
}

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

PATIENT_NAME_LINE_RE = re.compile(
    r"""(?im)^\s*
        (?:INDICATION\s+FOR\s+OPERATION|IMPRESSION\s*/\s*PLAN|PATIENT|NAME)\s*[:]\s*
        (?P<name>
            [A-Z][a-z'’-]+
            (?:\s+[A-Z]\.?)?
            (?:\s+[A-Z][a-z'’-]+){1,3}
        )
        \s+(?:is\s+(?:a|an)\b|MRN|ID)
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

_PROVIDER_LINE_LABEL_RE = re.compile(
    r"""(?im)^\s*(?:CC\s+REFERRED\s+PHYSICIAN|REFERRED\s+PHYSICIAN|REFERRING\s+PHYSICIAN|
        PRIMARY\s+CARE\s+PHYSICIAN|ATTENDING(?:\s+PHYSICIAN)?|SURGEON|ASSISTANT|
        ANESTHESIOLOGIST|FELLOW|RESIDENT|COSIGNED\s+BY|SIGNED\s+BY|DICTATED\s+BY|
        PERFORMED\s+BY|AUTHORED\s+BY|PROVIDER|PROCEDURALIST|OPERATOR)\s*:\s*""",
    re.VERBOSE,
)
_STAFF_ROLE_LINE_RE = re.compile(r"(?im)^\s*(?:RN|RT|PA|NP|MA|CNA)\s*:\s*")

_SECTION_HEADER_WORDS: frozenset[str] = frozenset(
    {
        "DISPOSITION", "SPECIMEN", "SPECIMEN(S)", "SAMPLE", "SAMPLES", "IMPRESSION",
        "PLAN", "PROCEDURE", "PROCEDURES", "ATTENDING", "ASSISTANT", "ANESTHESIA",
        "MONITORING", "TRACHEA", "BRUSH", "CRYOBIOPSY", "MEDIASTINAL", "MEDIA",
        "SIZE", "FLUID", "LARYNX", "PHARYNX", "FINDINGS", "COMPLICATIONS", "INDICATION",
    }
)

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

_MRN_ID_LINE_RE = re.compile(r"\b(mrn|id)\s*[:#]", re.IGNORECASE)

_ADDRESS_STATE_ZIP_RE = re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b")
_ADDRESS_STREET_LINE_RE = re.compile(
    r"(?im)^\s*\d{1,6}\s+.+\b(?:St\.?|Street|Ave\.?|Avenue|Blvd\.?|Boulevard|Rd\.?|Road|Dr\.?|Drive|Ln\.?|Lane|Way|Ct\.?|Court|Pl\.?|Place|Ter\.?|Terrace|Pkwy\.?|Parkway|Hwy\.?|Highway|Cir\.?|Circle)\b.*$"
)
_ADDRESS_MAILCODE_RE = re.compile(r"\bMC\s*\d{3,6}\b", re.IGNORECASE)


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float
    source: str | None = None


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


# --- New: HIPAA Age Detection ---
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

def filter_allowlisted_terms(text: str, results: list) -> list:
    """Drop detections whose detected text is allow-listed."""
    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if entity_type == "ADDRESS" or getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        detected_text = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if _is_allowlisted(detected_text):
            continue
        filtered.append(res)
    return filtered


def filter_eponyms(text: str, results: list) -> list:
    """Drop PERSON detections that are likely part of a medical eponym.
    
    Checks if the word immediately following the detection is a common medical noun.
    """
    filtered: list = []
    
    # Use a simple lookahead window
    suffix_pattern = re.compile(
        r"^\s+(" + "|".join(re.escape(s) for s in MEDICAL_EPONYM_SUFFIXES) + r")\b",
        re.IGNORECASE
    )

    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "PERSON":
            filtered.append(res)
            continue

        end = int(getattr(res, "end"))
        # Check text immediately following the entity
        suffix_window = text[end : min(len(text), end + 20)]
        if suffix_pattern.match(suffix_window):
            # E.g. "Foley" in "Foley catheter" -> Drop "Foley"
            continue
            
        filtered.append(res)
    return filtered


def filter_structural_headers(text: str, results: list) -> list:
    """Drop PERSON/LOCATION detections that are actually dynamic section headers."""
    header_spans = []
    for m in _DYNAMIC_HEADER_RE.finditer(text):
        # Protect the label part
        header_spans.append((m.start(1), m.end(1)))
        
    if not header_spans:
        return results
        
    filtered: list = []
    for res in results:
        # Keep forced names
        if getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
            
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        
        is_header = False
        for h_start, h_end in header_spans:
            if start >= h_start and end <= h_end:
                is_header = True
                break
        
        if is_header:
            continue
            
        filtered.append(res)
    return filtered


def filter_dynamic_biomedical_shield(text: str, results: list, nlp_engine: Any) -> list:
    """Dynamic Veto: Use the underlying spaCy model (scispacy) to detect medical entities.
    
    If the NLP model identifies a span as a biomedical ENTITY/CHEMICAL/DISEASE, and Presidio 
    flagged it as PII (PERSON/LOCATION), we prioritize the biomedical classification and
    veto the redaction.
    """
    if not nlp_engine:
        return results
    
    try:
        # Access the 'en' model from Presidio's NLP engine wrapper
        nlp = nlp_engine.nlp.get("en")
        if not nlp:
            return results
            
        doc = nlp(text)
        # scispacy uses 'ENTITY' for broad coverage; ensure we don't un-redact 'Patient'
        valid_labels = {"ENTITY", "DISEASE", "CHEMICAL", "PROCEDURE", "BODY_PART"}
        
        bio_spans = []
        for ent in doc.ents:
            if ent.label_ in valid_labels and ent.text.lower() not in BIOMEDICAL_SHIELD_BLOCKLIST:
                bio_spans.append((ent.start_char, ent.end_char))
    except Exception as e:
        # Fail safe if model access fails
        logger.debug(f"Biomedical shield scan failed: {e}")
        return results
        
    if not bio_spans:
        return results

    filtered: list = []
    for res in results:
        # Do not un-redact forced names, MRNs, or strong PII types
        if (getattr(res, "source", None) == "forced_patient_name" or 
            res.entity_type in {"MRN", "US_SSN", "PHONE_NUMBER", "EMAIL_ADDRESS", "AGE_OVER_90"}):
            filtered.append(res)
            continue
            
        r_start, r_end = int(res.start), int(res.end)
        
        is_biomedical = False
        for b_start, b_end in bio_spans:
            # If the detection is significantly overlapping a biomedical term
            overlap_start = max(r_start, b_start)
            overlap_end = min(r_end, b_end)
            
            if overlap_end > overlap_start:
                # Calculate overlap ratio
                overlap_len = overlap_end - overlap_start
                det_len = r_end - r_start
                # If overlap covers > 50% of the detection, trust the bio model
                if det_len > 0 and (overlap_len / det_len) > 0.5:
                    is_biomedical = True
                    break
        
        if is_biomedical:
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
    cpt_hint_re = re.compile(r"\b(?:CPT|HCPCS|ICD-?10|ICD)\b", re.IGNORECASE)
    code_re = re.compile(r"\b(?<!/)\d{5}[A-Z0-9]{0,4}\b", re.IGNORECASE)
    cursor = 0
    while cursor <= len(text):
        line_end = text.find("\n", cursor)
        if line_end == -1: line_end = len(text)
        line = text[cursor:line_end]
        if line.strip():
            if cpt_hint_re.search(line):
                for m in code_re.finditer(line): safe_spans.append((cursor + m.start(), cursor + m.end()))
            elif re.match(r"^\s*\d{5}[A-Z0-9]{0,4}\b", line) and not _ADDRESS_STREET_LINE_RE.match(line):
                for m in code_re.finditer(line): safe_spans.append((cursor + m.start(), cursor + m.end()))
        if line_end == len(text): break
        cursor = line_end + 1

    # Block-based scanning
    header_re = re.compile(r"(?im)^\s*(?:PROCEDURE|CPT\s*CODES?|CODES?)\s*[:]")
    next_header_re = re.compile(r"(?im)^\s*[A-Z][A-Za-z\s/]+[:]")
    lines = text.splitlines(keepends=True)
    current_pos = 0
    in_cpt_block = False
    for line in lines:
        if header_re.match(line): in_cpt_block = True
        elif in_cpt_block and next_header_re.match(line): in_cpt_block = False
        if in_cpt_block or "CPT" in line:
            for m in code_re.finditer(line): safe_spans.append((current_pos + m.start(), current_pos + m.end()))
        current_pos += len(line)

    if not safe_spans: return results
    filtered = []
    for res in results:
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        if any(start >= s and end <= e for s, e in safe_spans): continue
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
            (_DATETIME_SLASH_TIME_COMPACT_RE.fullmatch(candidate) and _valid_hhmm(candidate.split()[-1]))):
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


def filter_person_provider_lines(text: str, results: list) -> list:
    provider_spans = []
    for m in _PROVIDER_LINE_LABEL_RE.finditer(text): provider_spans.append(_line_bounds(text, m.start()))
    for m in _STAFF_ROLE_LINE_RE.finditer(text): provider_spans.append(_line_bounds(text, m.start()))
    if not provider_spans: return results
    patient_label_re = re.compile(r"^patient\s*:", re.IGNORECASE)
    filtered = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "PERSON" or getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        start, end = int(getattr(res, "start")), int(getattr(res, "end"))
        line_start, line_end = _line_bounds(text, start)
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
    relative_res = [re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in relative_phrases]
    filtered = []
    for res in results:
        if getattr(res, "entity_type", None) != "DATE_TIME":
            filtered.append(res)
            continue
        token = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
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
    patient_label_re = re.compile(r"^patient\s*:", re.IGNORECASE)
    dr_prefix_re = re.compile(r"\b(dr\.?|doctor)\s*$", re.IGNORECASE)
    provider_inline_label_re = re.compile(r"\b(surgeon|assistant|anesthesiologist|attending|fellow|resident|proceduralist)\b\s*:\s*$", re.IGNORECASE)
    credential_suffix_re = re.compile(r"^\s*,?\s*(md|do|rn|pa|np)\b", re.IGNORECASE)
    
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
        
        # Check local context
        prefix = text[max(0, res_start - 20) : res_start]
        suffix = text[res_end : min(len(text), res_end + 12)]
        
        if provider_inline_label_re.search(prefix) or dr_prefix_re.search(prefix) or credential_suffix_re.search(suffix):
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
) -> tuple[ScrubResult, dict[str, Any]]:
    
    if not text:
        return ScrubResult("", []), {"detections": [], "removed_detections": [], "redacted_text": ""}
    
    raw = detections
    removed: list[dict[str, Any]] = []

    def _record_removed(before: list[Detection], after: list[Detection], reason: str) -> None:
        for d in _diff_removed(before, after):
            removed.append({
                "reason": reason, "entity_type": d.entity_type, "start": d.start, "end": d.end,
                "score": d.score, "source": d.source, "detected_text": text[d.start : d.end],
                "surrounding_context": _context_window(text, d.start, d.end)
            })

    # 1. Contextual Provider Protection
    step0 = filter_person_provider_lines(text, raw)
    step0 = filter_person_provider_context(text, step0)
    step0 = filter_provider_signature_block(text, step0)
    _record_removed(raw, step0, "provider_context")

    # 2. Dynamic Guards (Headers, Eponyms, Biomedical)
    step1 = filter_structural_headers(text, step0)
    _record_removed(step0, step1, "dynamic_header")
    
    step2 = filter_eponyms(text, step1)
    _record_removed(step1, step2, "medical_eponym")
    
    # This is the primary robustness upgrade: leveraging scispacy
    step3 = filter_dynamic_biomedical_shield(text, step2, nlp_engine)
    _record_removed(step2, step3, "biomedical_shield")

    # 3. Technical Filters
    step4 = filter_device_model_context(text, step3)
    step4 = filter_credentials(text, step4)
    step4 = filter_cpt_codes(text, step4)
    _record_removed(step3, step4, "technical_filters")

    # 4. Date/Time Logic
    step5 = filter_datetime_exclusions(text, step4, relative_datetime_phrases)
    step5 = filter_datetime_measurements(text, step5)
    step5 = filter_strict_datetime_patterns(text, step5)
    _record_removed(step4, step5, "datetime_logic")

    # 5. Static Allowlist (Fallback)
    step6 = filter_allowlisted_terms(text, step5)
    _record_removed(step5, step6, "static_allowlist")

    # 6. Header False Positives & Scoring
    step7 = filter_person_location_false_positives(text, step6)
    step7 = filter_low_score_results(step7, score_thresholds)
    _record_removed(step6, step7, "header_low_score")

    # 7. Final Selection
    final = select_non_overlapping_results(step7)
    _record_removed(step7, final, "overlap_resolution")

    # Custom placeholders for specific entity types to support registry value extraction
    CUSTOM_PLACEHOLDERS = {
        "AGE_OVER_90": ">90"  # HIPAA Safe Harbor aggregation
    }

    scrubbed_text = text
    entities = []
    # Apply redactions in reverse order to preserve indices
    for d in sorted(final, key=lambda r: r.start, reverse=True):
        # Use custom placeholder if defined, otherwise default to <ENTITY_TYPE>
        placeholder = CUSTOM_PLACEHOLDERS.get(d.entity_type, f"<{d.entity_type.upper()}>")
        
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

    return ScrubResult(scrubbed_text, entities), {
        "config": {"nlp_model": nlp_model},
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
                Pattern("name_then_mrn", r"(?im)^[A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+.*\b(?:MRN|ID)\s*[:#]", 0.95)
            ], name="PATIENT_LABEL_NAME")
            self._patient_line = re.compile(r"(?im)^Patient:\s*(.+?)(?:\s+(?:MRN|ID)\s*[:#].*)?$")
            self._name_then_mrn = re.compile(r"(?im)^([A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)?)\s+(?=(?:MRN|ID)\s*[:#])")
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
                        r"(?i)\b(?:MRN|ID)\b\s*[:#]?\s*[A-Z0-9][A-Z0-9-]{3,}\b",
                        0.95,
                    )
                ],
                name="MRN",
            )
            self._mrn = re.compile(r"(?i)\b(?:MRN|ID)\b\s*[:#]?\s*([A-Z0-9][A-Z0-9-]{3,})\b")

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

        self.enable_driver_license_recognizer = _env_flag("ENABLE_DRIVER_LICENSE_RECOGNIZER", False)
        self.score_thresholds = _parse_score_thresholds(os.getenv("PHI_ENTITY_SCORE_THRESHOLDS"))
        self.relative_datetime_phrases = tuple(p.strip() for p in os.getenv("PHI_DATE_TIME_RELATIVE_PHRASES", ",".join(DEFAULT_RELATIVE_DATE_TIME_PHRASES)).split(",") if p.strip())
        self.entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "LOCATION", "MEDICAL_LICENSE", "MRN"]
        if self.enable_driver_license_recognizer: self.entities.append("US_DRIVER_LICENSE")

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
        raw = self._analyze_detections(sanitized)
        forced_names = extract_patient_names(sanitized)
        forced_detections = forced_patient_name_detections(sanitized, forced_names)
        datetime_detections = detect_datetime_detections(sanitized)
        address_detections = detect_address_detections(sanitized)
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
            nlp_engine=self._analyzer.nlp_engine # Pass NLP engine for dynamic biomedical check
        )

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        scrub_result, _ = self.scrub_with_audit(text, document_type=document_type, specialty=specialty)
        return scrub_result

__all__ = ["PresidioScrubber"]
