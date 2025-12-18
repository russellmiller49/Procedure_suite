"""Presidio-based scrubber adapter (synthetic PHI demo ready).

Implements PHIScrubberPort using Presidio AnalyzerEngine. Avoids logging raw
PHI and preserves IP anatomical terms via allowlist filtering.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any
from functools import lru_cache
from typing import Iterable

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


ANATOMICAL_ALLOW_LIST = {
    # Head & Neck / Upper Airway
    "larynx",
    "pharynx",
    "oropharynx",
    "nasopharynx",
    "glottis",
    "subglottis",
    "epiglottis",
    "vocal cords",
    "true vocal cords",
    "false vocal cords",
    "cords",
    "naris",
    "nares",
    "oral cavity",
    "tongue",
    "palate",
    # Lung lobes and shorthand
    "upper lobe",
    "lower lobe",
    "middle lobe",
    "right upper lobe",
    "rul",
    "right middle lobe",
    "rml",
    "right lower lobe",
    "rll",
    "left upper lobe",
    "lul",
    "left lower lobe",
    "lll",
    "lingula",
    "lingular",
    # Airway structures
    "carina",
    "main carina",
    "trachea",
    "distal trachea",
    "proximal trachea",
    "bronchus",
    "bronchi",
    "mainstem",
    "right mainstem",
    "left mainstem",
    "bronchus intermedius",
    "segmental",
    "subsegmental",
    "proximal airways",
    "distal airways",
    # Stations
    "station 4r",
    "station 4l",
    "station 7",
    "station 2r",
    "station 2l",
    "station 10",
    "station 11",
    "station 12",
    # Station shorthand (common in bronchoscopy/EBUS notes)
    "4r",
    "4l",
    "7",
    "10r",
    "10l",
    "11r",
    "11l",
    "11rs",
    "11ri",
    # Mediastinal/lymphatic terms
    "mediastinum",
    "mediastinal",
    "hilum",
    "hilar",
    "paratracheal",
    "subcarinal",
    "lymph node",
    "lymph nodes",
    "node",
    "nodes",
    # Procedures/techniques
    "ebus",
    "eus",
    "tbna",
    "bal",
    "bronchoscopy",
    # Laterality descriptors
    "left",
    "right",
    "bilateral",
    "unilateral",
}

CLINICAL_ALLOW_LIST = {
    # --- From IP_Registry.json & Dictionaries ---
    
    # Navigation & Robotics (often flagged as Locations/Persons)
    "ion", "monarch", "galaxy", "superdimension", "illumisite", "spin", 
    "lungvision", "archimedes", "inreach", "veran", "intuitive", "auris",
    "shape-sensing", "robotic-assisted", "nav-guided", "enb",
    
    # Valves & Devices
    "zephyr", "spiration", "pulmonx", "olympus", "coviden", "medtronic",
    "boston scientific", "cook", "merit", "conmed", "erbe",
    "chartis", "collateral ventilation",
    
    # Catheters & Tubes
    "pleurx", "aspira", "rocket", "yueh", "cooke", "pigtail", "tru-cut", 
    "abrams", "heimlich", "pleurovac", "chest tube", "ipc", "tunneled catheter",
    "picc", "picc line", "midline", "central line", "art line", "a-line",
    
    # Stents
    "dumon", "hood", "novatech", "aero", "ultraflex", "sems", "silicone",
    "hybrid stent", "y-stent", "airway stent", "bonastent",
    
    # Imaging & Guidance
    "cios", "cios spin", "cone beam", "cbct", "fluoroscopy", "rebus", 
    "radial ebus", "radial probe", "miniprobe", "ultrasound", "sonographic",
    "elastography", "ultrasound elastography",
    
    # Ablation & Tools
    "apc", "argon plasma", "electrocautery", "cryo", "cryoprobe", "cryospray",
    "cryoablation", "cryotherapy", "cryobiopsy", "mwa", "microwave", "radiofrequency", "rfa",
    "laser", "nd:yag", "co2 laser", "diode", "microdebrider", "snare", "basket",
    "fogarty", "arndt", "cohen", "blocker", "balloon", "bougie", "brush", "knife",
    "forceps", "alligator forceps", "needle", "catheter", "dilator", "guidewire",
    "trochar", "introduction needle", "introducer", "lyofoam",
    "rigid", "rigid scope", "rigid bronchoscope", "ventilating scope",
    "lma", "laryngeal mask", "laryngeal mask airway", "ett", "endotracheal tube",
    
    # Medications (Sedation/Reversal/Local) - commonly flagged
    "lidocaine", "fentanyl", "midazolam", "versed", "propofol", "etomidate",
    "succinylcholine", "rocuronium", "cisatracurium", "sugammadex", "neostigmine",
    "glycopyrrolate", "atropine", "epinephrine", "phenylephrine", "norepinephrine",
    "flumazenil", "naloxone", "narcan", "romazicon", "kenalog", "tranexamic acid", 
    "txa", "doxycycline", "bleomycin", "talc", "saline", "ns",
    "instillation", "fibrinolysis", "tpa", "dnase",
    
    # Common Clinical Descriptors & Status
    "absen", "absent", "present", "normal", "abnormal", "stable", "unstable",
    "adequate", "inadequate", "diagnostic", "nondiagnostic", "malignant", "benign",
    "suspicious", "atypical", "granuloma", "necrosis", "inflammation", 
    "anthracotic", "cobblestoning", "erythematous", "friable", "nodular", "polypoid",
    "patent", "occluded", "obstructed", "stenosis", "stricture", "malacia",
    "fistula", "dehiscence", "granulation", "secretions", "mucus", "blood", "clot",
    "purulent", "serous", "serosanguinous", "chylous", "bloody", "fluid",
    "size", "volume", "echogenicity", "anechoic", "hypoechoic", "isoechoic",
    "hyperechoic", "loculations", "thin", "thick", "diminished", "eccentric",
    "continuous", "margin",
    
    # Anatomy & Pathology
    "lung", "lungs", "lobe", "lobes", "pleura", "pleural", "airway", "trachea",
    "esophagus", "thyroid", "spine", "rib", "chest wall", "diaphragm",
    "nodule", "mass", "lesion", "tumor", "infiltrate", "consolidation", 
    "ground glass", "cavity", "calcification", "effusion", "pneumothorax", 
    "hemothorax", "empyema", "chylothorax", "trapped lung", "lymphadenopathy",
    "neoplasm", "malignancy", "mycetoma", "pleural effusion",
    
    # Administrative/Coding Terms (often flagged as DATE/TIME or IDs)
    "initial day", "subsequent day", "initial episode", "repeat", "modifier",
    "separate structure", "distinct service", "unlisted procedure",
    "cpt", "icd-10", "diagnosis", "indication", "history", "plan", "assessment",
    "tbbx", "tbna", "tbcbx",
    
    # Units & Measurements
    "mm", "cm", "fr", "french", "gauge", "liter", "liters", "cc", "ml", 
    "joules", "watts", "lpm", "l/min", "mins", "seconds", "secs", "minutes",
    
    # Personnel roles (lower case to catch common misclassifications)
    "attending", "fellow", "resident", "anesthesiologist", "crna", "nurse", "rn", 
    "tech", "technician", "observer", "proceduralist", "assistant",
    "self, referred", "referred", "provider",
    
    # Disease specific
    "hodgkin", "hodgkin's", "non-hodgkin", "lymphoma", "carcinoma", 
    "adenocarcinoma", "squamous", "sarcoidosis", "tuberculosis", "afb",
    "fungal", "bacterial", "viral",
    
    # Meds + common descriptors that frequently false-positive as PHI.
    "nonobstructive",
    # Common clinical/admin tokens that spaCy can misclassify as entities (often LOCATION).
    "anesthesia",
    "general anesthesia",
    # Common abbreviations which can false-positive as entities.
    "us",  # Ultrasound (often misread as United States)
    "mc",  # Mail code / internal routing shorthand
    "pacs",
    "on",  # "on" (preposition) sometimes flagged
    # Common clinician credentials.
    "md",
    "do",
    "phd",
    # Clinical terms often capitalized in headers/lists.
    "target",
    "freeze",
    "brush",
    "media",
    "samples",
    "sample",
    "specimen",
    "specimens",
    "disposition",
    "mediastinal",
    "lymph",
    "lymph node",
    "lymph nodes",
    "lung nodule",
    "solitary lung nodule",
    "mass",
    "lesion",
    # Existing anatomical allow-list (critical for procedure coding).
    *ANATOMICAL_ALLOW_LIST,
}

DEFAULT_ENTITY_SCORE_THRESHOLDS: dict[str, float] = {
    "PERSON": 0.50,
    "DATE_TIME": 0.60,
    "LOCATION": 0.70,
    "MRN": 0.50,
    "__DEFAULT__": 0.50,
}

DEFAULT_RELATIVE_DATE_TIME_PHRASES: tuple[str, ...] = (
    "about a week",
    "in a week",
    "next week",
    "today",
    "tomorrow",
    "yesterday",
    "same day",
)

PATIENT_NAME_LINE_RE = re.compile(
    r"""(?im)^\s*
        (?:INDICATION\s+FOR\s+OPERATION|IMPRESSION\s*/\s*PLAN)\s*:\s*
        (?P<name>
            [A-Z][a-z'’-]+
            (?:\s+[A-Z]\.?)?
            (?:\s+[A-Z][a-z'’-]+){1,3}
        )
        \s+is\s+(?:a|an)\b
    """,
    re.VERBOSE,
)

_DATE_NUMERIC_RE = re.compile(
    r"""(?ix)
    \b(
        # MM/DD/YYYY or M/D/YY (supports / or -)
        (?:0?[1-9]|1[0-2]) [/-] (?:0?[1-9]|[12]\d|3[01]) [/-] (?:\d{4}|\d{2})
        |
        # MM/DDYYYY (missing slash before year): 12/162025
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
        "MD",
        "DO",
        "PHD",
        "RN",
        "RT",
        "PA",
        "PAC",
        "NPC",
        "NP",
        "DNP",
        "FNP",
        "CRNA",
        "RRT",
        "LPN",
        "CNA",
        "MA",
    }
)

_PROVIDER_LINE_LABEL_RE = re.compile(
    r"""(?im)^\s*(?:CC\s+REFERRED\s+PHYSICIAN|REFERRED\s+PHYSICIAN|REFERRING\s+PHYSICIAN|
        PRIMARY\s+CARE\s+PHYSICIAN|ATTENDING(?:\s+PHYSICIAN)?|SURGEON|ASSISTANT|
        ANESTHESIOLOGIST|FELLOW|RESIDENT|COSIGNED\s+BY|SIGNED\s+BY|DICTATED\s+BY|
        PERFORMED\s+BY|AUTHORED\s+BY|PROVIDER)\s*:\s*""",
    re.VERBOSE,
)
_STAFF_ROLE_LINE_RE = re.compile(r"(?im)^\s*(?:RN|RT|PA|NP|MA|CNA)\s*:\s*")

_SECTION_HEADER_WORDS: frozenset[str] = frozenset(
    {
        "DISPOSITION",
        "SPECIMEN",
        "SPECIMEN(S)",
        "SAMPLE",
        "SAMPLES",
        "IMPRESSION",
        "PLAN",
        "PROCEDURE",
        "PROCEDURES",
        "ATTENDING",
        "ASSISTANT",
        "ANESTHESIA",
        "MONITORING",
        "TRACHEA",
        "BRUSH",
        "CRYOBIOPSY",
        "MEDIASTINAL",
        "MEDIA",
        "SIZE",
        "FLUID",
        "LARYNX",
        "PHARYNX",
    }
)

_ALLOWLIST_BOUNDARY_RE = re.compile(
    r"(?i)\b(?:"
    + "|".join(sorted((re.escape(t) for t in CLINICAL_ALLOW_LIST), key=len, reverse=True))
    + r")\b"
)

_DEVICE_MODEL_CONTEXT_RE = re.compile(
    r"\b(?:[A-Z]{1,3}\d{2,4}|[A-Z]{1,3}-[A-Z0-9]{2,10})\b"
    r"(?=[^\n]{0,20}\b(?:video bronchoscope|bronchoscope|scope|cryoprobe|needle)\b)",
    re.IGNORECASE,
)

_MRN_ID_LINE_RE = re.compile(r"\b(mrn|id)\s*[:#]", re.IGNORECASE)


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


def filter_allowlisted_terms(text: str, results: list) -> list:
    """Drop detections whose detected text is allow-listed."""

    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if entity_type == "ADDRESS":
            filtered.append(res)
            continue
        if getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue
        detected_text = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if _is_allowlisted(detected_text):
            continue
        filtered.append(res)
    return filtered


def filter_device_model_context(text: str, results: list) -> list:
    """Drop detections which match known device/model identifiers in device context."""

    safe_spans: list[tuple[int, int]] = []
    for m in _DEVICE_MODEL_CONTEXT_RE.finditer(text):
        line_start, line_end = _line_bounds(text, m.start())
        line = text[line_start:line_end]
        if _MRN_ID_LINE_RE.search(line):
            continue
        safe_spans.append((m.start(), m.end()))

    if not safe_spans:
        return results

    filtered: list = []
    for res in results:
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        if any(start >= s and end <= e for s, e in safe_spans):
            continue
        filtered.append(res)
    return filtered


def filter_cpt_codes(text: str, results: list) -> list:
    """Drop detections which point at CPT/medical procedure codes.

    Detects CPT codes (5 digits, optionally alphanumeric) when they appear:
    1. On a line containing "CPT" or "PROCEDURE".
    2. In a block of text following a "PROCEDURE:"-style header.
    """
    safe_spans: list[tuple[int, int]] = []

    cpt_hint_re = re.compile(r"\b(?:CPT|HCPCS|ICD-?10|ICD)\b", re.IGNORECASE)
    # Negative lookbehind avoids matching the year portion of dates like 12/17/2025.
    code_re = re.compile(r"\b(?<!/)\d{5}[A-Z0-9]{0,4}\b", re.IGNORECASE)

    # Pass 1: line-based scanning (protect codes on CPT/ICD/HCPCS lines or standalone code lines).
    cursor = 0
    while cursor <= len(text):
        line_end = text.find("\n", cursor)
        if line_end == -1:
            line_end = len(text)
        line = text[cursor:line_end]
        if line.strip():
            if cpt_hint_re.search(line):
                for m in code_re.finditer(line):
                    safe_spans.append((cursor + m.start(), cursor + m.end()))
            elif re.match(r"^\s*\d{5}[A-Z0-9]{0,4}\b", line) and not _ADDRESS_STREET_LINE_RE.match(line):
                for m in code_re.finditer(line):
                    safe_spans.append((cursor + m.start(), cursor + m.end()))
        if line_end == len(text):
            break
        cursor = line_end + 1

    # Pass 2: block-based scanning after "PROCEDURE:" / "CPT CODES:" headers.
    header_re = re.compile(r"(?im)^\s*(?:PROCEDURE|CPT\s*CODES?|CODES?)\s*[:]")
    next_header_re = re.compile(r"(?im)^\s*[A-Z][A-Za-z\s/]+[:]")
    lines = text.splitlines(keepends=True)
    current_pos = 0
    in_cpt_block = False
    for line in lines:
        line_len = len(line)
        if header_re.match(line):
            in_cpt_block = True
        elif in_cpt_block and next_header_re.match(line):
            in_cpt_block = False
        if in_cpt_block or "CPT" in line:
            for m in code_re.finditer(line):
                safe_spans.append((current_pos + m.start(), current_pos + m.end()))
        current_pos += line_len

    if not safe_spans:
        return results

    filtered: list = []
    for res in results:
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        if any(start >= s and end <= e for s, e in safe_spans):
            continue
        filtered.append(res)
    return filtered


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


def detect_datetime_detections(text: str) -> list[Detection]:
    detections: list[Detection] = []
    seen: set[tuple[int, int, str]] = set()

    def _add(start: int, end: int, source: str) -> None:
        key = (start, end, "DATE_TIME")
        if key in seen:
            return
        seen.add(key)
        detections.append(Detection(entity_type="DATE_TIME", start=start, end=end, score=1.0, source=source))

    for m in _DATETIME_ISO_RE.finditer(text):
        _add(m.start(), m.end(), "regex_datetime_iso")
    for m in _DATETIME_SLASH_TIME_COLON_RE.finditer(text):
        _add(m.start(), m.end(), "regex_datetime_time_colon")
    for m in _DATETIME_SLASH_TIME_COMPACT_RE.finditer(text):
        token = m.group(0)
        time_token = token.split()[-1]
        if _valid_hhmm(time_token):
            _add(m.start(), m.end(), "regex_datetime_time_compact")

    for m in _DATE_NUMERIC_RE.finditer(text):
        _add(m.start(), m.end(), "regex_date_numeric")
    for m in _DATE_ISO_RE.finditer(text):
        _add(m.start(), m.end(), "regex_date_iso")
    for m in _DATE_TEXT_MONTH_FIRST_RE.finditer(text):
        _add(m.start(), m.end(), "regex_date_text")
    for m in _DATE_TEXT_DAY_FIRST_RE.finditer(text):
        _add(m.start(), m.end(), "regex_date_text")

    return detections


_ADDRESS_STATE_ZIP_RE = re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b")
_ADDRESS_STREET_LINE_RE = re.compile(
    r"(?im)^\s*\d{1,6}\s+.+\b(?:St\.?|Street|Ave\.?|Avenue|Blvd\.?|Boulevard|Rd\.?|Road|Dr\.?|Drive|Ln\.?|Lane|Way|Ct\.?|Court|Pl\.?|Place|Ter\.?|Terrace|Pkwy\.?|Parkway|Hwy\.?|Highway|Cir\.?|Circle)\b.*$"
)
_ADDRESS_MAILCODE_RE = re.compile(r"\bMC\s*\d{3,6}\b", re.IGNORECASE)


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
            if next_end == -1:
                next_end = len(text)
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


def _normalize_credential(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def is_credential(detected_text: str) -> bool:
    normalized = _normalize_credential(detected_text.strip())
    return normalized in _CREDENTIAL_NORMALIZED


def filter_credentials(text: str, results: list) -> list:
    """Drop detections which are provider credentials/titles (MD, RN, etc)."""

    filtered: list = []
    for res in results:
        detected_text = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if is_credential(detected_text):
            continue
        filtered.append(res)
    return filtered


def filter_datetime_measurements(text: str, results: list) -> list:
    """Drop DATE_TIME false positives which are numeric measurements with units (e.g., '1250 ml')."""

    filtered: list = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "DATE_TIME":
            filtered.append(res)
            continue
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        token = text[start:end]
        if token.isdigit():
            tail = text[end : min(len(text), end + 12)]
            if _MEASUREMENT_UNIT_TAIL_RE.match(tail):
                continue
        filtered.append(res)
    return filtered


def filter_strict_datetime_patterns(text: str, results: list) -> list:
    """Drop DATE_TIME detections which don't match strict date/time patterns."""

    filtered: list = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "DATE_TIME":
            filtered.append(res)
            continue

        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        detected_text = text[start:end]
        candidate = detected_text.strip()
        if (
            _DATE_NUMERIC_RE.fullmatch(candidate)
            or _DATE_ISO_RE.fullmatch(candidate)
            or _DATE_TEXT_MONTH_FIRST_RE.fullmatch(candidate)
            or _DATE_TEXT_DAY_FIRST_RE.fullmatch(candidate)
            or _DATETIME_ISO_RE.fullmatch(candidate)
            or _DATETIME_SLASH_TIME_COLON_RE.fullmatch(candidate)
            or (_DATETIME_SLASH_TIME_COMPACT_RE.fullmatch(candidate) and _valid_hhmm(candidate.split()[-1]))
        ):
            filtered.append(res)
            continue

    return filtered


def _is_header_label_context(text: str, start: int, end: int) -> bool:
    token = text[start:end].strip()
    if not token:
        return False
    if any(ch.islower() for ch in token):
        return False
    if not any(ch.isalpha() for ch in token):
        return False

    line_start, line_end = _line_bounds(text, start)
    line = text[line_start:line_end]
    prefix = line[: start - line_start]
    if prefix.strip():
        return False
    suffix = line[end - line_start :]
    colon_idx = suffix.find(":")
    if colon_idx == -1 or colon_idx > 40:
        return False
    return True


def filter_person_location_false_positives(text: str, results: list) -> list:
    """Drop common clinical/header false positives for PERSON/LOCATION."""

    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        if entity_type not in {"PERSON", "LOCATION"}:
            filtered.append(res)
            continue

        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        detected_text = text[start:end].strip()
        if not detected_text:
            continue
        if any(ch.isdigit() for ch in detected_text):
            continue
        if "/" in detected_text or ":" in detected_text:
            continue
        if detected_text.upper() in _SECTION_HEADER_WORDS:
            continue
        if _is_header_label_context(text, start, end):
            continue

        filtered.append(res)

    return filtered


def filter_person_provider_lines(text: str, results: list) -> list:
    """Suppress PERSON detections on structured provider/staff lines (keep clinician names)."""

    provider_line_spans: list[tuple[int, int]] = []
    for m in _PROVIDER_LINE_LABEL_RE.finditer(text):
        line_start, line_end = _line_bounds(text, m.start())
        provider_line_spans.append((line_start, line_end))
    for m in _STAFF_ROLE_LINE_RE.finditer(text):
        line_start, line_end = _line_bounds(text, m.start())
        provider_line_spans.append((line_start, line_end))

    if not provider_line_spans:
        return results

    patient_label_re = re.compile(r"^patient\s*:", re.IGNORECASE)

    filtered: list = []
    for res in results:
        if str(getattr(res, "entity_type", "")).upper() != "PERSON":
            filtered.append(res)
            continue
        if getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue

        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        line_start, line_end = _line_bounds(text, start)
        line = text[line_start:line_end]
        if patient_label_re.search(line.lstrip()):
            filtered.append(res)
            continue

        if any(start >= s and end <= e for s, e in provider_line_spans):
            continue

        filtered.append(res)

    return filtered


def filter_datetime_exclusions(text: str, results: list, relative_phrases: Iterable[str]) -> list:
    """Drop DATE_TIME detections that are durations or vague/relative time."""

    duration_re = re.compile(
        r"^\s*\d+(?:\.\d+)?\s*(?:second|seconds|minute|minutes|hour|hours|day|days|week|weeks)\b",
        re.IGNORECASE,
    )
    relative_res = [re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in relative_phrases]

    filtered: list = []
    for res in results:
        if getattr(res, "entity_type", None) != "DATE_TIME":
            filtered.append(res)
            continue
        detected_text = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if duration_re.search(detected_text):
            continue
        if any(r.search(detected_text) for r in relative_res):
            continue
        filtered.append(res)
    return filtered


def filter_low_score_results(results: list, thresholds: dict[str, float]) -> list:
    """Drop detections below per-entity minimum score thresholds."""

    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        score = float(getattr(res, "score", 0.0) or 0.0)
        minimum = float(thresholds.get(entity_type, thresholds.get("__DEFAULT__", 0.0)))
        if score < minimum:
            continue
        filtered.append(res)
    return filtered


def select_non_overlapping_results(results: list) -> list:
    """Resolve overlaps by keeping the highest-confidence, longest detections."""

    entity_priority: dict[str, int] = {
        "MRN": 100,
        "US_SSN": 95,
        "EMAIL_ADDRESS": 90,
        "PHONE_NUMBER": 90,
        "ADDRESS": 85,
        "DATE_TIME": 80,
        "PERSON": 70,
        "LOCATION": 60,
        "MEDICAL_LICENSE": 50,
        "US_DRIVER_LICENSE": 50,
    }

    def _key(r) -> tuple[int, float, int, int, str]:
        start = int(getattr(r, "start"))
        end = int(getattr(r, "end"))
        score = float(getattr(r, "score", 0.0) or 0.0)
        length = end - start
        entity_type = str(getattr(r, "entity_type", ""))
        priority = entity_priority.get(entity_type.upper(), 0)
        return (priority, score, length, -start, entity_type)

    selected: list = []
    for res in sorted(results, key=_key, reverse=True):
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        if any(start < int(getattr(s, "end")) and end > int(getattr(s, "start")) for s in selected):
            continue
        selected.append(res)

    return sorted(selected, key=lambda r: int(getattr(r, "start")))


def filter_provider_signature_block(text: str, results: list) -> list:
    """Drop PERSON detections in likely provider signature blocks near the end."""

    header = re.search(r"(?im)^recommendations:\s*$", text)
    zone_start = header.start() if header else int(len(text) * 0.75)

    cred_re = re.compile(r"(?:,\s*)?(md|do)\b", re.IGNORECASE)
    service_re = re.compile(r"\binterventional\s+pulmonology\b", re.IGNORECASE)

    filtered: list = []
    for res in results:
        if getattr(res, "entity_type", None) != "PERSON":
            filtered.append(res)
            continue
        if int(getattr(res, "start")) < zone_start:
            filtered.append(res)
            continue

        line_start, line_end = _line_bounds(text, int(getattr(res, "start")))
        line = text[line_start:line_end]
        next_line = ""
        if line_end < len(text):
            nl_start = line_end + 1
            nl_end = text.find("\n", nl_start)
            if nl_end == -1:
                nl_end = len(text)
            next_line = text[nl_start:nl_end]

        has_cred = cred_re.search(line) is not None
        has_service = service_re.search(line) is not None or service_re.search(next_line) is not None
        if has_cred and has_service:
            continue

        filtered.append(res)

    return filtered


def _line_bounds(text: str, index: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    if end == -1:
        end = len(text)
    return start, end


def _context_window(text: str, start: int, end: int, window: int = 40) -> str:
    left = max(0, start - window)
    right = min(len(text), end + window)
    return text[left:right]


def filter_person_provider_context(text: str, results: list) -> list:
    """Prevent redaction of clinician/provider names based on local context."""

    patient_label_re = re.compile(r"^patient\s*:", re.IGNORECASE)
    dr_prefix_re = re.compile(r"\b(dr\.?|doctor)\s*$", re.IGNORECASE)
    provider_inline_label_re = re.compile(
        r"\b(surgeon|assistant|anesthesiologist|attending|fellow|resident)\b\s*:\s*$",
        re.IGNORECASE,
    )
    credential_suffix_re = re.compile(r"^\s*,?\s*(md|do)\b", re.IGNORECASE)

    filtered: list = []
    for res in results:
        if getattr(res, "entity_type", None) != "PERSON":
            filtered.append(res)
            continue
        if getattr(res, "source", None) == "forced_patient_name":
            filtered.append(res)
            continue

        res_start = int(getattr(res, "start"))
        res_end = int(getattr(res, "end"))
        start, _ = _line_bounds(text, res_start)
        _, end = _line_bounds(text, res_end)
        line = text[start:end]

        # Patient header line always redacts (even if patient is a clinician with credentials).
        if patient_label_re.search(line.lstrip()):
            filtered.append(res)
            continue

        prefix_window = text[max(0, res_start - 60) : res_start]
        if provider_inline_label_re.search(prefix_window):
            continue
        if dr_prefix_re.search(prefix_window):
            continue

        suffix_window = text[res_end : min(len(text), res_end + 12)]
        if credential_suffix_re.search(suffix_window):
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
) -> tuple[ScrubResult, dict[str, Any]]:
    if not text:
        empty = ScrubResult(scrubbed_text="", entities=[])
        return empty, {"detections": [], "removed_detections": [], "redacted_text": ""}

    raw = detections
    removed: list[dict[str, Any]] = []

    def _record_removed(before: list[Detection], after: list[Detection], reason: str) -> None:
        for d in _diff_removed(before, after):
            removed.append(
                {
                    "reason": reason,
                    "entity_type": d.entity_type,
                    "start": d.start,
                    "end": d.end,
                    "score": d.score,
                    "source": d.source,
                    "detected_text": text[d.start : d.end],
                    "surrounding_context": _context_window(text, d.start, d.end, window=40),
                }
            )

    step0 = filter_person_provider_lines(text, raw)
    _record_removed(raw, step0, "provider_context")

    step = filter_person_provider_context(text, step0)
    _record_removed(step0, step, "provider_context")

    step2 = filter_provider_signature_block(text, step)
    _record_removed(step, step2, "provider_context")

    step3 = filter_device_model_context(text, step2)
    _record_removed(step2, step3, "device_model")

    step_cred = filter_credentials(text, step3)
    _record_removed(step3, step_cred, "credentials")

    step_cpt = filter_cpt_codes(text, step_cred)
    _record_removed(step_cred, step_cpt, "cpt_code")

    step4 = filter_datetime_exclusions(text, step_cpt, relative_phrases=relative_datetime_phrases)
    _record_removed(step_cpt, step4, "duration_datetime")

    step_dt_meas = filter_datetime_measurements(text, step4)
    _record_removed(step4, step_dt_meas, "measurement_datetime")

    step_dt_strict = filter_strict_datetime_patterns(text, step_dt_meas)
    _record_removed(step_dt_meas, step_dt_strict, "datetime_pattern")

    step5 = filter_allowlisted_terms(text, step_dt_strict)
    _record_removed(step_dt_strict, step5, "allowlist")

    step_fp = filter_person_location_false_positives(text, step5)
    _record_removed(step5, step_fp, "header_false_positive")

    step6 = filter_low_score_results(step_fp, thresholds=score_thresholds)
    _record_removed(step_fp, step6, "low_score")

    final = select_non_overlapping_results(step6)
    _record_removed(step6, final, "overlap")

    scrubbed_text = text
    entities = []
    for _, d in enumerate(sorted(final, key=lambda r: r.start, reverse=True)):
        placeholder = f"<{d.entity_type.upper()}>"
        scrubbed_text = scrubbed_text[: d.start] + placeholder + scrubbed_text[d.end :]
        entities.append(
            {
                "placeholder": placeholder,
                "entity_type": d.entity_type,
                "original_start": d.start,
                "original_end": d.end,
            }
        )

    entities = list(reversed(entities))
    scrub_result = ScrubResult(scrubbed_text=scrubbed_text, entities=entities)

    detections_report = []
    for d in raw:
        detections_report.append(
            {
                "entity_type": d.entity_type,
                "start": d.start,
                "end": d.end,
                "score": d.score,
                "source": d.source,
                "detected_text": text[d.start : d.end],
                "surrounding_context": _context_window(text, d.start, d.end, window=40),
            }
        )

    report: dict[str, Any] = {
        "config": {
            "nlp_backend": nlp_backend,
            "nlp_model": nlp_model,
            "requested_nlp_model": requested_nlp_model,
            "enable_driver_license_recognizer": enable_driver_license_recognizer,
            "entity_score_thresholds": dict(score_thresholds),
            "relative_datetime_phrases": list(relative_datetime_phrases),
        },
        "detections": detections_report,
        "removed_detections": removed,
        "redacted_text": scrub_result.scrubbed_text,
    }

    return scrub_result, report


def _build_analyzer(model_name: str):
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": model_name}],
        }
    )
    nlp_engine = provider.create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    # High-confidence override: treat patient header patterns as PERSON.
    # This helps when Presidio misses the patient identity in demographic headers.
    from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult

    class _PatientLabelRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="PERSON",
                patterns=[
                    # Pattern 1: Standard "Patient: First Last"
                    Pattern(name="patient_label_line", regex=r"(?im)^Patient:\s*.+$", score=0.95),
                    # Pattern 2: "Last, First" followed by MRN/ID
                    Pattern(
                        name="name_then_mrn",
                        regex=r"(?im)^[A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+.*\b(?:MRN|ID)\s*[:#]",
                        score=0.95,
                    ),
                    # Pattern 3: Explicit "Patient: Last, First" where MRN might be on next line
                    Pattern(
                         name="patient_label_comma",
                         regex=r"(?im)^Patient:\s*[A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+",
                         score=0.95
                    )
                ],
                name="PATIENT_LABEL_NAME",
            )
            # Regex to extract the name part only from the full matched line
            self._patient_line = re.compile(
                r"(?im)^Patient:\s*(.+?)(?:\s+(?:MRN|ID)\s*[:#].*)?$"
            )
            self._name_then_mrn = re.compile(
                r"(?im)^([A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)?)\s+(?=(?:MRN|ID)\s*[:#])"
            )

        def analyze(self, text: str, entities: list[str], nlp_artifacts=None):  # type: ignore[override]
            results: list[RecognizerResult] = []
            if "PERSON" not in entities:
                return results
            
            # Handle "Patient: Name" lines
            for m in self._patient_line.finditer(text):
                start, end = m.span(1)
                if end - start >= 2:
                    results.append(RecognizerResult(entity_type="PERSON", start=start, end=end, score=0.95))
            
            # Handle "Name, Name MRN: ..." lines
            for m in self._name_then_mrn.finditer(text):
                start, end = m.span(1)
                if end - start >= 2:
                    results.append(RecognizerResult(entity_type="PERSON", start=start, end=end, score=0.95))
            return results

    analyzer.registry.add_recognizer(_PatientLabelRecognizer())

    class _InstitutionRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="LOCATION",
                patterns=[
                    Pattern(name="ucsd", regex=r"(?i)\bUCSD\b", score=0.95),
                    Pattern(name="nmcsd", regex=r"(?i)\bNMCSD\b", score=0.95),
                    Pattern(name="balboa", regex=r"(?i)\bBalboa\b", score=0.95),
                    Pattern(name="navy", regex=r"(?i)\bNavy\b", score=0.95),
                ],
                name="INSTITUTION_PATTERN",
            )
    
    analyzer.registry.add_recognizer(_InstitutionRecognizer())

    class _MrnRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="MRN",
                # Added \b before and after to strictly match word ID, avoiding matches inside "identified".
                patterns=[
                    Pattern(name="mrn", regex=r"(?i)\b(?:MRN|ID)\b\s*[:#]?\s*[A-Z0-9][A-Z0-9-]{3,}\b", score=0.95)
                ],
                name="MRN",
            )
            self._mrn = re.compile(r"(?i)\b(?:MRN|ID)\b\s*[:#]?\s*([A-Z0-9][A-Z0-9-]{3,})\b")

        def analyze(self, text: str, entities: list[str], nlp_artifacts=None):  # type: ignore[override]
            results: list[RecognizerResult] = []
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
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "PresidioScrubber initialization failed; ensure presidio-analyzer and spaCy model are installed."
        ) from exc


class PresidioScrubber(PHIScrubberPort):
    """Presidio-powered scrubber with IP allowlist filtering."""

    def __init__(self, model_name: str | None = None):
        self.nlp_backend = os.getenv("NLP_BACKEND", "spacy").lower()
        default_model = "en_core_sci_sm" if self.nlp_backend == "scispacy" else "en_core_web_sm"
        self.requested_model_name = model_name or os.getenv("PRESIDIO_NLP_MODEL", default_model)

        fallbacks_env = os.getenv("PRESIDIO_NLP_MODEL_FALLBACKS")
        if fallbacks_env is not None:
            fallback_models = [m.strip() for m in fallbacks_env.split(",") if m.strip()]
        else:
            fallback_models = ["en_core_web_sm", "en_core_web_md", "en_core_web_lg"]

        model_candidates = [self.requested_model_name] + [
            m for m in fallback_models if m != self.requested_model_name
        ]

        last_exc: RuntimeError | None = None
        for candidate in model_candidates:
            try:
                self._analyzer = _get_analyzer(candidate)
                self.model_name = candidate
                break
            except RuntimeError as exc:
                last_exc = exc

        if last_exc is not None and not hasattr(self, "_analyzer"):
            raise last_exc

        if self.model_name != self.requested_model_name:
            logger.warning(
                "Requested spaCy model unavailable; falling back",
                extra={"requested_model": self.requested_model_name, "fallback_model": self.model_name},
            )
        # Clinical procedure notes rarely contain driver license IDs, but the recognizer
        # often false-positives on device model tokens like "T190" bronchoscope models.
        self.enable_driver_license_recognizer = _env_flag("ENABLE_DRIVER_LICENSE_RECOGNIZER", False)

        self.score_thresholds = _parse_score_thresholds(os.getenv("PHI_ENTITY_SCORE_THRESHOLDS"))
        self.relative_datetime_phrases = tuple(
            p.strip()
            for p in os.getenv("PHI_DATE_TIME_RELATIVE_PHRASES", ",".join(DEFAULT_RELATIVE_DATE_TIME_PHRASES)).split(
                ","
            )
            if p.strip()
        )

        # Entity types to request from Presidio (used by the scrubber and audit CLI).
        entities: list[str] = [
            "PERSON",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "US_SSN",
            "LOCATION",
            "MEDICAL_LICENSE",
            "MRN",
        ]
        if self.enable_driver_license_recognizer:
            entities.append("US_DRIVER_LICENSE")
        self.entities = entities

    def _analyze_detections(self, text: str) -> list[Detection]:
        results = self._analyzer.analyze(
            text=text,
            language="en",
            entities=self.entities,
        )
        detections: list[Detection] = []
        for r in results:
            start = int(getattr(r, "start"))
            end = int(getattr(r, "end"))
            # Truncate detections that mistakenly span across newlines (e.g. "Name\nLabel")
            text_span = text[start:end]
            if "\n" in text_span:
                newline_idx = text_span.find("\n")
                # Keep only the first line of the detection
                end = start + newline_idx
            
            detections.append(
                Detection(
                    entity_type=str(getattr(r, "entity_type")),
                    start=start,
                    end=end,
                    score=float(getattr(r, "score", 0.0) or 0.0),
                )
            )
        return detections

    def scrub_with_audit(
        self, text: str, document_type: str | None = None, specialty: str | None = None
    ) -> tuple[ScrubResult, dict[str, Any]]:
        sanitized = sanitize_length_preserving(text)
        raw = self._analyze_detections(sanitized)
        forced_names = extract_patient_names(sanitized)
        forced_detections = forced_patient_name_detections(sanitized, forced_names)
        datetime_detections = detect_datetime_detections(sanitized)
        address_detections = detect_address_detections(sanitized)
        raw = raw + forced_detections + datetime_detections + address_detections
        return redact_with_audit(
            text=sanitized,
            detections=raw,
            enable_driver_license_recognizer=self.enable_driver_license_recognizer,
            score_thresholds=self.score_thresholds,
            relative_datetime_phrases=self.relative_datetime_phrases,
            nlp_backend=self.nlp_backend,
            nlp_model=self.model_name,
            requested_nlp_model=self.requested_model_name,
        )

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        scrub_result, _ = self.scrub_with_audit(text, document_type=document_type, specialty=specialty)
        return scrub_result


__all__ = ["PresidioScrubber"]