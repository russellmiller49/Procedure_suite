"""Field-specific normalization for registry extraction outputs."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, List
import re
from datetime import datetime


# Valid EBUS lymph node stations - canonical format
VALID_EBUS_STATIONS = frozenset({
    "2R", "2L", "4R", "4L", "7", "10R", "10L", "11R", "11L",
    # Also accept numeric-only for station 7
})

# Pattern to match valid station format
STATION_PATTERN = re.compile(r"^(2R|2L|4R|4L|7|10R|10L|11R|11L)$", re.IGNORECASE)

# Canonical ROSE result values
ROSE_RESULT_CANONICAL = {
    "malignant": "Malignant",
    "benign": "Benign",
    "nondiagnostic": "Nondiagnostic",
    "non-diagnostic": "Nondiagnostic",
    "non diagnostic": "Nondiagnostic",
    "granuloma": "Granuloma",
    "granulomatous": "Granuloma",
    "atypical": "Atypical cells present",
    "atypical cells": "Atypical cells present",
    "atypical cells present": "Atypical cells present",
    "atypical lymphoid": "Atypical lymphoid proliferation",
    "atypical lymphoid proliferation": "Atypical lymphoid proliferation",
    "insufficient": "Nondiagnostic",
    "inadequate": "Nondiagnostic",
}

# ROSE result priority for deriving global result (higher = more significant)
ROSE_RESULT_PRIORITY = {
    "Malignant": 6,
    "Atypical lymphoid proliferation": 5,
    "Atypical cells present": 4,
    "Granuloma": 3,
    "Benign": 2,
    "Nondiagnostic": 1,
}

__all__ = [
    "normalize_sedation_type",
    "normalize_airway_type",
    "map_pleural_guidance",
    "normalize_pleural_procedure",
    "normalize_pleural_side",
    "normalize_pleural_intercostal_space",
    "postprocess_patient_mrn",
    "normalize_procedure_date",
    "normalize_disposition",
    "postprocess_asa_class",
    "normalize_final_diagnosis_prelim",
    "normalize_stent_type",
    "normalize_stent_location",
    "normalize_stent_deployment_method",
    "normalize_ebus_rose_result",
    "normalize_ebus_station_rose_result",
    "derive_global_ebus_rose_result",
    "normalize_ebus_needle_gauge",
    "normalize_ebus_needle_type",
    "normalize_ebus_stations_detail",
    "normalize_elastography_pattern",
    "normalize_list_field",
    "normalize_anesthesia_agents",
    "normalize_ebus_stations",
    "normalize_linear_ebus_stations",
    "normalize_nav_sampling_tools",
    "normalize_follow_up_plan",
    "normalize_cao_location",
    "normalize_cao_tumor_location",
    "normalize_cpt_codes",
    "normalize_assistant_names",
    "normalize_ablation_modality",
    "normalize_airway_device_size",
    "normalize_nav_registration_method",
    "normalize_assistant_name_single",
    "normalize_ventilation_mode",
    "normalize_procedure_setting",
    "normalize_bronch_location_lobe",
    "normalize_attending_name",
    "normalize_provider_role",
    "normalize_immediate_complications",
    "normalize_radiographic_findings",
    "validate_station_format",
    "VALID_EBUS_STATIONS",
    "ROSE_RESULT_CANONICAL",
    "ROSE_RESULT_PRIORITY",
    "POSTPROCESSORS",
]


def _coerce_to_text(raw: Any) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, list) and raw:
        raw = raw[0]
    text = str(raw).strip()
    return text or None


def normalize_sedation_type(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.lower()

    mapping = {
        "moderate": "Moderate",
        "moderate sedation": "Moderate",
        "conscious sedation": "Moderate",
        "deep": "Deep",
        "deep sedation": "Deep",
        "general": "General",
        "general anesthesia": "General",
        "ga": "General",
        "local": "Local",
        "local anesthesia": "Local",
        "local only": "Local",
        # Project convention: treat MAC as deep sedation when no explicit GA/ETT
        "monitored anesthesia care": "Deep",
        "mac": "Deep",
        "mac anesthesia": "Deep",
    }

    if text in mapping:
        val = mapping[text]
    else:
        if "general" in text and "anesth" in text:
            val = "General"
        elif "monitored anesthesia care" in text or " mac " in text or re.search(r"\bmac\b", text):
            val = "Deep"
        elif "deep" in text and "sedat" in text:
            val = "Deep"
        elif "conscious" in text and "sedat" in text:
            val = "Moderate"
        elif "moderate" in text and "sedat" in text:
            val = "Moderate"
        elif "local" in text and "anesth" in text:
            val = "Local"
        elif "mac" in text or "monitored anesthesia care" in text:
            # Convention: MAC → Deep when not otherwise specified
            val = "Deep"
        else:
            lowered_allowed = {
                "moderate": "Moderate",
                "deep": "Deep",
                "general": "General",
                "local": "Local",
                "monitored anesthesia care": "Deep",
            }
            val = lowered_allowed.get(text, None)

    allowed = {"Moderate", "Deep", "General", "Local", "Monitored Anesthesia Care"}
    return val if val in allowed else None


def normalize_airway_type(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if text in {"", "none", "n/a", "na", "null"}:
        return None

    mapping = {
        "native": "Native",
        "native airway": "Native",
        "native airway with bite block": "Native",
        "natural": "Native",
        "natural airway": "Native",
        "spontaneous": "Native",
        "lma": "LMA",
        "laryngeal mask": "LMA",
        "laryngeal mask airway": "LMA",
        "ett": "ETT",
        "endotracheal": "ETT",
        "endotracheal tube": "ETT",
        "et tube": "ETT",
        "trach": "Tracheostomy",
        "tracheostomy": "Tracheostomy",
        "tracheostomy tube": "Tracheostomy",
        "rigid": "Rigid Bronchoscope",
        "rigid bronchoscope": "Rigid Bronchoscope",
        "rigid bronch": "Rigid Bronchoscope",
        "rigid bronchoscopy": "Rigid Bronchoscope",
    }

    if text in mapping:
        return mapping[text]

    if "rigid" in text and "bronch" in text:
        return "Rigid Bronchoscope"
    if "trach" in text:
        return "Tracheostomy"
    if "lma" in text or "laryngeal mask" in text:
        return "LMA"
    if "ett" in text or "endotracheal" in text or "et tube" in text:
        return "ETT"
    if "native" in text or "natural airway" in text or "bite block" in text:
        return "Native"

    return None


def map_pleural_guidance(raw_value: Any) -> str | None:
    text_raw = _coerce_to_text(raw_value)
    if text_raw is None:
        return None
    text = text_raw.lower()

    if text in {"ultrasound", "us", "u/s", "ultrasound-guided", "ultrasound guidance"}:
        return "Ultrasound"
    if text in {"ct", "ct-guided", "ct guidance", "computed tomography"}:
        return "CT"
    if text in {"blind", "no imaging", "unguided"}:
        return "Blind"

    if "ultrasound" in text or "sonograph" in text:
        return "Ultrasound"
    if "ct-guid" in text or " ct " in text or "computed tomography" in text:
        return "CT"
    if "no imaging" in text or "without imaging" in text or "blind" in text or "no image guidance" in text:
        return "Blind"

    return None


def normalize_pleural_procedure(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.lower()

    canonical = {
        "thoracentesis": "Thoracentesis",
        "chest tube": "Chest Tube",
        "chest tube removal": "Chest Tube Removal",
        "tunneled catheter": "Tunneled Catheter",
        "tunnelled catheter": "Tunneled Catheter",
        "tunneled catheter exchange": "Tunneled Catheter Exchange",
        "tunnelled catheter exchange": "Tunneled Catheter Exchange",
        "ipc drainage": "IPC Drainage",
        "medical thoracoscopy": "Medical Thoracoscopy",
        "chemical pleurodesis": "Chemical Pleurodesis",
    }
    if text in canonical:
        return canonical[text]

    # Map common brand names/abbreviations for tunneled catheters
    if any(k in text for k in ["pleurx", "aspira", "denver catheter", "ipc", "indwelling pleural catheter"]):
        if "exchange" in text or "replac" in text:
            return "Tunneled Catheter Exchange"
        if "drain" in text and "place" not in text and "insert" not in text:
            return "IPC Drainage"
        return "Tunneled Catheter"

    if "pleurodesis" in text:
        return "Chemical Pleurodesis"

    if "tunneled" in text or "tunnelled" in text:
        if "catheter" in text or "pleural catheter" in text:
            if "exchange" in text or "replac" in text:
                return "Tunneled Catheter Exchange"
            return "Tunneled Catheter"

    if "thoracoscopy" in text or "pleuroscopy" in text:
        return "Medical Thoracoscopy"

    if any(k in text for k in ["chest tube", "pleural drain", "pleural tube", "pigtail", "intercostal drain", "icd"]):
        if "remov" in text:
            return "Chest Tube Removal"
        return "Chest Tube"

    if "thoracentesis" in text or "pleural tap" in text:
        return "Thoracentesis"

    for k, v in canonical.items():
        if k in text:
            return v

    return None


def normalize_pleural_side(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if text in {"r", "rt", "right", "right-sided", "right side"}:
        return "Right"
    if text in {"l", "lt", "left", "left-sided", "left side"}:
        return "Left"
    if text.startswith("r"):
        return "Right"
    if text.startswith("l"):
        return "Left"
    return None


def normalize_pleural_intercostal_space(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.lower()
    match = re.search(r"(\\d{1,2})(?:st|nd|rd|th)?", text)
    if not match:
        return text_raw.strip() or None
    num = int(match.group(1))
    if 10 <= num % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(num % 10, "th")
    return f"{num}{suffix}"


def normalize_elastography_pattern(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    cleaned = text_raw.strip().rstrip(".;,")
    return cleaned or None


def postprocess_patient_mrn(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    raw_text = str(text_raw).strip()
    if not raw_text:
        return None

    # Remove surrounding quotes/punctuation that sometimes wrap IDs
    raw_text = raw_text.strip().strip("\"'").strip(",:;")

    # Reject obvious dates
    date_patterns = [
        r"^\d{1,2}/\d{1,2}/\d{2,4}$",
        r"^\d{1,2}-\d{1,2}-\d{2,4}$",
        r"^\d{4}-\d{1,2}-\d{1,2}$",
    ]
    for pat in date_patterns:
        if re.match(pat, raw_text):
            return None

    # Strip common labels if present
    labeled = re.search(r"(?:MRN|Medical Record Number|Patient ID|Pt ID|ID)\s*[:#-]?\s*(.+)$", raw_text, re.IGNORECASE)
    candidate = labeled.group(1).strip() if labeled else raw_text
    candidate = candidate.strip().strip(",:;")

    # Reject obvious phone-like strings only when separators are present
    if re.search(r"[-()\s]", candidate) and re.fullmatch(r"[\d\s().+-]{6,}", candidate) and not re.search(r"[A-Za-z]", candidate):
        return None

    return candidate or None


def normalize_procedure_date(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    raw = text_raw.strip()
    if raw.lower() == "null" or raw == "":
        return None

    iso_match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if iso_match:
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            return None

    candidates = [
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%m/%d/%y",
        "%m-%d-%y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    for fmt in candidates:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    date_like = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", raw)
    if date_like:
        text = date_like.group(1)
        for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"]:
            try:
                dt = datetime.strptime(text, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    # Handle compact formats like 03Nov17 or 3Nov2017
    compact = re.search(r"(\d{1,2}[A-Za-z]{3}\d{2,4})", raw)
    if compact:
        text = compact.group(1)
        for fmt in ["%d%b%Y", "%d%b%y"]:
            try:
                dt = datetime.strptime(text, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return None


def normalize_disposition(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text:
        return None

    mapping_exact = {
        "discharge home": "Discharge Home",
        "home": "Discharge Home",
        "pacu recovery": "PACU Recovery",
        "pacu": "PACU Recovery",
        "recovery": "PACU Recovery",
        "floor admission": "Floor Admission",
        "admit to floor": "Floor Admission",
        "icu admission": "ICU Admission",
        "admit to icu": "ICU Admission",
    }
    if text in mapping_exact:
        return mapping_exact[text]

    icu_keywords = [
        "icu",
        "micu",
        "sicu",
        "cticu",
        "ccu",
        "neuro icu",
        "burn icu",
        "intensive care",
        "critical care",
    ]
    if any(k in text for k in icu_keywords):
        return "ICU Admission"

    floor_keywords = [
        "admit to floor",
        "to the floor",
        "medicine floor",
        "surgery floor",
        "inpatient ward",
        "telemetry",
        "step-down",
        "step down",
        "intermediate care",
        "imcu",
        "admit to medicine",
        "admit to oncology",
        "admit to hospitalist",
        "admit for observation",
        "admitted for observation",
    ]
    if any(k in text for k in floor_keywords):
        return "Floor Admission"

    pacu_keywords = [
        "to pacu",
        "pacu",
        "post-anesthesia care",
        "post anesthesia care",
        "recovery room",
        "phase i recovery",
        "postop recovery",
        "short stay recovery",
        "day surgery recovery",
        "sds recovery",
    ]
    if any(k in text for k in pacu_keywords):
        return "PACU Recovery"

    home_keywords = [
        "discharge home",
        "discharged home",
        "dc home",
        "sent home",
        "to home",
        "home after",
        "go home",
        "going home",
        "return home",
        "ok for discharge",
        "ok to discharge",
        "same-day discharge",
        "same day discharge",
    ]
    if any(k in text for k in home_keywords):
        return "Discharge Home"

    return None


def postprocess_asa_class(raw_text: Any) -> int | None:
    text_raw = _coerce_to_text(raw_text)
    if text_raw is None or not str(text_raw).strip():
        return None
    cleaned = str(text_raw).strip().upper()
    # Extract first digit if present
    m = re.search(r"([1-5])", cleaned)
    if m:
        return int(m.group(1))
    roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
    for roman, val in roman_map.items():
        if re.search(rf"\b{roman}\b", cleaned):
            return val
    return None


def normalize_final_diagnosis_prelim(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    t = text_raw.strip().lower()
    if not t:
        return None
    mapping = {
        "malignancy": "Malignancy",
        "malignant": "Malignancy",
        "cancer": "Malignancy",
        "infectious": "Infectious",
        "infection": "Infectious",
        "granulomatous": "Granulomatous",
        "granuloma": "Granulomatous",
        "non-diagnostic": "Non-diagnostic",
        "nondiagnostic": "Non-diagnostic",
        "non diagnostic": "Non-diagnostic",
        "other": "Other",
    }
    if t in mapping:
        return mapping[t]
    if "granulom" in t:
        return "Granulomatous"
    if "infect" in t:
        return "Infectious"
    if "benign" in t:
        return "Benign"
    if "malig" in t or "carcinoma" in t or "adenocarcinoma" in t:
        return "Malignancy"
    if "non" in t and "diagnostic" in t:
        return "Non-diagnostic"
    return None


def normalize_stent_type(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    t = text_raw.strip().lower()
    if not t:
        return None
    mapping = {
        "silicone-dumon": "Silicone-Dumon",
        "dumon": "Silicone-Dumon",
        "silicone y-stent": "Silicone Y-Stent",
        "silicone-y-stent": "Silicone-Y-Stent",
        "y stent": "Silicone Y-Stent",
        "hybrid": "Hybrid",
        "metallic-covered": "Metallic-Covered",
        "covered metallic": "Metallic-Covered",
        "metallic-uncovered": "Metallic-Uncovered",
        "uncovered metallic": "Metallic-Uncovered",
    }
    if t in mapping:
        return mapping[t]
    if "dumon" in t:
        return "Silicone-Dumon"
    if "y" in t and "stent" in t:
        return "Silicone Y-Stent"
    if "covered" in t and "metal" in t:
        return "Metallic-Covered"
    if "uncovered" in t and "metal" in t:
        return "Metallic-Uncovered"
    if "hybrid" in t:
        return "Hybrid"
    if "metal" in t:
        return "Metallic-Uncovered"
    return "Other" if t else None


def normalize_stent_location(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    t = text_raw.strip().lower()
    if not t:
        return None
    if "trache" in t:
        return "Trachea"
    if "mainstem" in t or "main stem" in t or "left main" in t or "right main" in t:
        return "Mainstem"
    if "lob" in t or "rul" in t or "rml" in t or "rll" in t or "lul" in t or "lll" in t:
        return "Lobar"
    return None


def normalize_stent_deployment_method(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    t = text_raw.strip().lower()
    if not t:
        return None
    if "rigid" in t:
        return "Rigid"
    if "flex" in t or "wire" in t:
        return "Flexible over Wire"
    return None


def validate_station_format(station: str) -> str | None:
    """Validate and normalize a station name to canonical format.

    Returns the canonical station name (uppercase) if valid, None otherwise.
    Valid stations: 2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L
    """
    if not station:
        return None
    cleaned = station.strip().upper()
    # Remove common prefixes
    cleaned = re.sub(r"^(STATION|STN|NODE)[\s:]*", "", cleaned, flags=re.IGNORECASE).strip()
    if STATION_PATTERN.match(cleaned):
        return cleaned
    return None


def normalize_ebus_station_rose_result(raw: Any) -> str | None:
    """Normalize a per-station ROSE result to canonical form.

    This normalizes individual station ROSE results (not the global result).
    Returns canonical ROSE result string or None.
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text or text in {"null", "none", "n/a", "na", ""}:
        return None

    # Check direct mapping
    if text in ROSE_RESULT_CANONICAL:
        return ROSE_RESULT_CANONICAL[text]

    # Fuzzy matching
    if "malignan" in text or "carcinoma" in text or "adenocarcinoma" in text:
        return "Malignant"
    if "granulom" in text:
        return "Granuloma"
    if "non" in text and "diagnostic" in text:
        return "Nondiagnostic"
    if "insufficient" in text or "inadequate" in text:
        return "Nondiagnostic"
    if "atypical" in text and "lymphoid" in text:
        return "Atypical lymphoid proliferation"
    if "atypical" in text:
        return "Atypical cells present"
    if "benign" in text or "reactive" in text or "lymphocyte" in text:
        return "Benign"

    return None


def derive_global_ebus_rose_result(station_details: list[dict[str, Any]] | None) -> str | None:
    """Derive a global EBUS ROSE result from per-station detail.

    Rules (per specification):
    - If all stations have the same result: return that result
    - If any station is Malignant: return "Malignant"
    - If mixture (e.g., benign + nondiagnostic): return "Mixed (station results)"
    - If no station-level ROSE data: return None

    Args:
        station_details: List of station detail dicts with optional 'rose_result' key

    Returns:
        Derived global ROSE result or None
    """
    if not station_details:
        return None

    # Collect all non-null rose results
    rose_by_station: list[tuple[str, str]] = []
    for detail in station_details:
        station = detail.get("station")
        rose = detail.get("rose_result")
        if station and rose:
            rose_by_station.append((station, rose))

    if not rose_by_station:
        return None

    # Get unique results
    unique_results = set(r for _, r in rose_by_station)

    if len(unique_results) == 1:
        # All stations have the same result
        return rose_by_station[0][1]

    # Multiple different results - check for malignant (highest priority)
    for _, result in rose_by_station:
        if result and "malignant" in result.lower():
            return "Malignant"

    # Build mixed summary: "Mixed (11L Nondiagnostic; 4R Benign)"
    parts = [f"{station} {result}" for station, result in rose_by_station]
    return f"Mixed ({'; '.join(parts)})"


def normalize_ebus_rose_result(raw: Any) -> str | None:
    """Normalize global EBUS ROSE result.

    NOTE: This normalizer should generally NOT be used for global ebus_rose_result
    when per-station ROSE data is available. Use derive_global_ebus_rose_result instead.
    This function normalizes the raw string value if one is provided directly.
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text or text in {"null", "none", "n/a", "na", ""}:
        return None

    # If it looks like a derived "Mixed" result, preserve it
    if text.startswith("mixed"):
        return raw.strip() if isinstance(raw, str) else str(raw).strip()

    # Otherwise normalize like a single result
    return normalize_ebus_station_rose_result(raw)


def normalize_ebus_needle_gauge(raw: Any) -> str | None:
    return None


def normalize_ebus_needle_type(raw: Any) -> str | None:
    return None


def _parse_size_mm(value: Any) -> float | None:
    """Convert size strings/numbers to millimeters."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _coerce_to_text(value)
    if text is None:
        return None
    lowered = text.lower()
    # Handle two-dimension strings like 1.2 x 0.8 cm (use the smaller dimension)
    dim_match = re.findall(r"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)(?:\s*(mm|cm))?", lowered)
    if dim_match:
        dim1, dim2, unit = dim_match[0]
        unit = unit or "mm"
        vals = []
        for dim in (dim1, dim2):
            try:
                num = float(dim)
                vals.append(num * 10 if unit.startswith("c") else num)
            except Exception:
                continue
        return min(vals) if vals else None

    match = re.search(r"(\d+(?:\.\d+)?)(?:\s*(mm|cm))?", lowered)
    if match:
        try:
            val = float(match.group(1))
            unit = match.group(2) or "mm"
            return val * 10 if unit.startswith("c") else val
        except Exception:
            return None
    return None


def _normalize_morphology_value(text: str | None, mapping: dict[str, str]) -> str | None:
    if text is None:
        return None
    val = text.strip().lower()
    if val in mapping:
        return mapping[val]
    for key, normalized in mapping.items():
        if key in val:
            return normalized
    return None


def normalize_ebus_stations_detail(raw: Any) -> list[dict[str, Any]] | None:
    """Normalize station-level detail entries and pad morphology fields with nulls.

    Rules:
    - Only include entries with valid station names (2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L)
    - Normalize station names to uppercase canonical form
    - Do not invent morphology data - leave as null if not explicitly in source
    - Normalize ROSE results using normalize_ebus_station_rose_result
    """
    if raw is None:
        return None
    entries: list[Any]
    if isinstance(raw, list):
        entries = raw
    else:
        entries = [raw]

    normalized: list[dict[str, Any]] = []
    shape_map = {
        "oval": "oval",
        "elliptical": "oval",
        "elongated": "oval",
        "round": "round",
        "spherical": "round",
        "irregular": "irregular",
        "lobulated": "irregular",
        "asymmetric": "irregular",
    }
    margin_map = {
        "distinct": "distinct",
        "well-defined": "distinct",
        "well-circumscribed": "distinct",
        "clear margin": "distinct",
        "sharp": "distinct",
        "indistinct": "indistinct",
        "ill-defined": "indistinct",
        "blurred": "indistinct",
        "poorly defined": "indistinct",
        "irregular": "irregular",
        "spiculated": "irregular",
    }
    echo_map = {
        "homogeneous": "homogeneous",
        "uniform": "homogeneous",
        "heterogeneous": "heterogeneous",
        "mixed": "heterogeneous",
        "non-uniform": "heterogeneous",
    }
    appearance_allowed = {"benign", "malignant", "indeterminate"}

    for entry in entries:
        if isinstance(entry, dict):
            # Validate station name - skip entries with invalid stations
            raw_station = entry.get("station")
            station = validate_station_format(str(raw_station)) if raw_station else None
            if not station:
                # Skip entries without valid station
                continue

            size_mm = _parse_size_mm(entry.get("size_mm"))
            passes = entry.get("passes")

            # Use the per-station ROSE normalizer
            rose_result = normalize_ebus_station_rose_result(entry.get("rose_result"))

            # Only normalize morphology if explicit text is provided - don't invent
            shape = _normalize_morphology_value(_coerce_to_text(entry.get("shape")), shape_map)
            margin = _normalize_morphology_value(_coerce_to_text(entry.get("margin")), margin_map)
            echogenicity = _normalize_morphology_value(_coerce_to_text(entry.get("echogenicity")), echo_map)

            chs_raw = entry.get("chs_present")
            if isinstance(chs_raw, str):
                chs_lower = chs_raw.strip().lower()
                if chs_lower in {"true", "yes", "present"}:
                    chs_present = True
                elif chs_lower in {"false", "no", "absent"}:
                    chs_present = False
                else:
                    chs_present = None
            else:
                chs_present = bool(chs_raw) if isinstance(chs_raw, bool) else None

            appearance = _coerce_to_text(entry.get("appearance_category"))
            appearance = appearance.lower() if appearance else None
            if appearance not in appearance_allowed:
                appearance = None

            normalized.append(
                {
                    "station": station,  # Already validated and uppercase
                    "size_mm": size_mm,
                    "passes": passes if passes is None or isinstance(passes, int) else None,
                    "shape": shape,
                    "margin": margin,
                    "echogenicity": echogenicity,
                    "chs_present": chs_present,
                    "appearance_category": appearance,
                    "rose_result": rose_result,
                }
            )
        elif isinstance(entry, str):
            # Attempt minimal parsing from a string like "11L 5.4mm benign"
            station_match = re.search(r"(2r|2l|4r|4l|7|10r|10l|11r|11l)", entry, re.IGNORECASE)
            if not station_match:
                # Skip entries without valid station pattern
                continue
            station = station_match.group(1).upper()
            size_mm = _parse_size_mm(entry)
            normalized.append(
                {
                    "station": station,
                    "size_mm": size_mm,
                    "passes": None,
                    "shape": None,
                    "margin": None,
                    "echogenicity": None,
                    "chs_present": None,
                    "appearance_category": None,
                    "rose_result": normalize_ebus_station_rose_result(entry),
                }
            )
        else:
            continue

    return normalized or None


def normalize_list_field(raw: Any) -> List[str] | None:
    """Convert comma-separated strings or mixed input to a list of strings."""
    if raw is None:
        return None
    if isinstance(raw, list):
        # Already a list, clean and return
        return [str(item).strip() for item in raw if item and str(item).strip()]
    if isinstance(raw, str):
        # Comma-separated string - split and clean
        if not raw.strip():
            return None
        items = [item.strip() for item in raw.split(",") if item.strip()]
        return items if items else None
    # Try to convert to string and split
    try:
        s = str(raw).strip()
        if not s:
            return None
        items = [item.strip() for item in s.split(",") if item.strip()]
        return items if items else None
    except Exception:
        return None


def normalize_anesthesia_agents(raw: Any) -> List[str] | None:
    """Normalize anesthesia agents list, handling comma-separated strings."""
    result = normalize_list_field(raw)
    if result is None:
        return None
    # Normalize common variations
    normalized = []
    agent_mapping = {
        "propofol": "Propofol",
        "fentanyl": "Fentanyl",
        "midazolam": "Midazolam",
        "rocuronium": "Rocuronium",
        "succinylcholine": "Succinylcholine",
        "remifentanil": "Remifentanil",
        "sevoflurane": "Sevoflurane",
        "isoflurane": "Isoflurane",
        "desflurane": "Desflurane",
    }
    for agent in result:
        agent_lower = agent.lower().strip()
        normalized_agent = agent_mapping.get(agent_lower, agent.strip())
        if normalized_agent and normalized_agent not in normalized:
            normalized.append(normalized_agent)
    return normalized if normalized else None


def normalize_ebus_stations(raw: Any) -> List[str] | None:
    """Normalize EBUS stations list, handling comma-separated strings.

    Only includes stations that match valid EBUS lymph node station patterns:
    2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L

    Invalid or unrecognized station names are filtered out.
    """
    result = normalize_list_field(raw)
    if result is None:
        return None
    # Clean and validate station format - only include valid stations
    normalized = []
    for station in result:
        validated = validate_station_format(station)
        if validated and validated not in normalized:
            normalized.append(validated)
    return normalized if normalized else None


def normalize_linear_ebus_stations(raw: Any) -> List[str] | None:
    """Alias for linear stations; keeps normalization consistent with ebus_stations_sampled."""
    return normalize_ebus_stations(raw)


def normalize_nav_sampling_tools(raw: Any) -> List[str] | None:
    """Normalize navigation sampling tools list, handling comma-separated strings."""
    result = normalize_list_field(raw)
    if result is None:
        return None
    # Normalize tool names
    normalized = []
    tool_mapping = {
        "forceps": "Forceps",
        "needle": "Needle",
        "brush": "Brush",
        "cryoprobe": "Cryoprobe",
        "cryo": "Cryoprobe",
        "cryobiopsy": "Cryoprobe",
    }
    for tool in result:
        tool_lower = tool.lower().strip()
        normalized_tool = tool_mapping.get(tool_lower, tool.strip().title())
        if normalized_tool and normalized_tool not in normalized:
            normalized.append(normalized_tool)
    return normalized if normalized else None


def normalize_follow_up_plan(raw: Any) -> List[str] | None:
    """Normalize follow-up plan list, handling comma-separated strings."""
    result = normalize_list_field(raw)
    if result is None:
        return None
    # Clean and return as-is (follow-up plans are free text)
    normalized = [item.strip() for item in result if item.strip()]
    return normalized if normalized else None


def normalize_cao_location(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip()
    if not text:
        return None
    
    # Allowed values: ["None", "Trachea", "Mainstem", "Lobar"]
    # Hierarchy of severity/centrality: Trachea > Mainstem > Lobar > None
    
    # Check for presence of keywords in the text
    lower_text = text.lower()
    if "trachea" in lower_text:
        return "Trachea"
    if "mainstem" in lower_text:
        return "Mainstem"
    if "lobar" in lower_text:
        return "Lobar"
    if "none" in lower_text:
        return "None"
        
    # If exact match with Enum
    if text in {"Trachea", "Mainstem", "Lobar", "None"}:
        return text
        
    return None

def normalize_cao_tumor_location(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip()
    if not text:
        return None
        
    # Allowed: ["Trachea", "RMS", "LMS", "Bronchus Intermedius", "Lobar", "RUL", "RML", "RLL", "LUL", "LLL", "Mainstem"]
    
    lower_text = text.lower()
    
    # Priority 1: Trachea
    if "trachea" in lower_text:
        return "Trachea"
        
    # Priority 2: Mainstems
    if "rms" in text or "right mainstem" in lower_text:
        return "RMS"
    if "lms" in text or "left mainstem" in lower_text:
        return "LMS"
    if "mainstem" in lower_text: # Generic mainstem if side not specified or both
        return "Mainstem"
        
    # Priority 3: Bronchus Intermedius
    if "bronchus intermedius" in lower_text or "bi" in lower_text.split(): # 'bi' might be risky as substring
        return "Bronchus Intermedius"
        
    # Priority 4: Lobes
    lobes = {
        "rul": "RUL", "right upper": "RUL",
        "rml": "RML", "right middle": "RML",
        "rll": "RLL", "right lower": "RLL",
        "lul": "LUL", "left upper": "LUL",
        "lll": "LLL", "left lower": "LLL",
        "lobar": "Lobar"
    }
    
    for key, val in lobes.items():
        if key in lower_text:
            return val
            
    return None


def normalize_assistant_names(raw: Any) -> List[str] | None:
    """Normalize assistant names, handling both single strings and lists.

    Supports:
    - Single string: "Dr. Smith" -> ["Dr. Smith"]
    - Comma-separated: "Dr. Smith, Dr. Jones" -> ["Dr. Smith", "Dr. Jones"]
    - List: ["Dr. Smith", "Dr. Jones"] -> ["Dr. Smith", "Dr. Jones"]
    - Legacy assistant_name field migration
    """
    if raw is None:
        return None

    # If already a list, clean each item
    if isinstance(raw, list):
        normalized = []
        for item in raw:
            if item is None:
                continue
            name = str(item).strip()
            if name and name.lower() not in {"none", "n/a", "na", "null", ""}:
                normalized.append(name)
        return normalized if normalized else None

    # If it's a string, check for comma separation
    if isinstance(raw, str):
        text = raw.strip()
        if not text or text.lower() in {"none", "n/a", "na", "null"}:
            return None

        # Check for common separators
        if "," in text or ";" in text:
            items = re.split(r"[,;]", text)
            normalized = [item.strip() for item in items if item.strip()]
            return normalized if normalized else None

        # Single name
        return [text]

    # Try to convert other types
    try:
        text = str(raw).strip()
        if text and text.lower() not in {"none", "n/a", "na", "null"}:
            return [text]
    except Exception:
        pass

    return None


def normalize_assistant_name_single(raw: Any) -> str | None:
    """Normalize assistant_name (singular) to a string.

    Handles list input by taking the first non-empty entry.
    """
    names = normalize_assistant_names(raw)
    if not names:
        return None
    return names[0]


def normalize_nav_registration_method(raw: Any) -> str | None:
    text = _coerce_to_text(raw)
    if text is None:
        return None
    lowered = text.strip().lower()
    if lowered in {"auto", "automatic"}:
        return "Automatic"
    if lowered in {"manual"}:
        return "Manual"
    # Title-case fallback for unexpected casing
    if text.strip():
        candidate = text.strip().title()
        if candidate in {"Manual", "Automatic"}:
            return candidate
    return None


def normalize_airway_device_size(raw: Any) -> str | None:
    """Normalize airway device size to string format.

    Handles:
    - Integer input: 12 -> "12"
    - Float input: 7.5 -> "7.5"
    - String input: "7.5 ETT" -> "7.5 ETT"
    """
    if raw is None:
        return None

    # Convert numbers to strings
    if isinstance(raw, (int, float)):
        # Format float nicely (remove trailing .0)
        if isinstance(raw, float) and raw == int(raw):
            return str(int(raw))
        return str(raw)

    # Handle string input
    text = str(raw).strip()
    if not text or text.lower() in {"none", "n/a", "na", "null"}:
        return None

    return text


def normalize_ablation_modality(raw: Any) -> str | None:
    """Normalize ablation modality to match schema enum values.

    Handles:
    - List input: Takes first valid item (e.g., ['Radiofrequency', 'Cryoablation'] -> "Radiofrequency (RFA)")
    - String input: Maps to canonical enum value
    - Common abbreviations: RFA, MWA, cryo, etc.

    Schema enum: ["Microwave (MWA)", "Radiofrequency (RFA)", "Cryoablation", "Laser", "Brachytherapy"]
    """
    text_raw = _coerce_to_text(raw)  # _coerce_to_text already takes first item from list
    if text_raw is None:
        return None

    text = text_raw.strip().lower()
    if not text or text in {"none", "n/a", "na", "null"}:
        return None

    # Mapping from various inputs to canonical enum values
    mapping = {
        # Microwave
        "microwave": "Microwave (MWA)",
        "microwave (mwa)": "Microwave (MWA)",
        "mwa": "Microwave (MWA)",
        "microwave ablation": "Microwave (MWA)",
        # Radiofrequency
        "radiofrequency": "Radiofrequency (RFA)",
        "radiofrequency (rfa)": "Radiofrequency (RFA)",
        "rfa": "Radiofrequency (RFA)",
        "rf ablation": "Radiofrequency (RFA)",
        "radiofrequency ablation": "Radiofrequency (RFA)",
        # Cryoablation
        "cryoablation": "Cryoablation",
        "cryo": "Cryoablation",
        "cryotherapy": "Cryoablation",
        "cryo ablation": "Cryoablation",
        # Laser
        "laser": "Laser",
        "laser ablation": "Laser",
        # Brachytherapy
        "brachytherapy": "Brachytherapy",
        "brachy": "Brachytherapy",
    }

    if text in mapping:
        return mapping[text]

    # Fuzzy matching for partial matches
    if "microwave" in text or "mwa" in text:
        return "Microwave (MWA)"
    if "radiofrequency" in text or "rfa" in text:
        return "Radiofrequency (RFA)"
    if "cryo" in text:
        return "Cryoablation"
    if "laser" in text:
        return "Laser"
    if "brachy" in text:
        return "Brachytherapy"

    return None


def normalize_ventilation_mode(raw: Any) -> str | None:
    """Normalize ventilation mode to schema enum values.

    Schema enum: ["Spontaneous", "Controlled Mechanical Ventilation", "Jet Ventilation"]
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text or text in {"none", "n/a", "na", "null"}:
        return None

    mapping = {
        # Controlled variants
        "volume control": "Controlled Mechanical Ventilation",
        "pressure control": "Controlled Mechanical Ventilation",
        "controlled mechanical ventilation": "Controlled Mechanical Ventilation",
        "controlled": "Controlled Mechanical Ventilation",
        "mechanical ventilation": "Controlled Mechanical Ventilation",
        "ippv": "Controlled Mechanical Ventilation",
        "cmv": "Controlled Mechanical Ventilation",
        # Spontaneous variants
        "spontaneous": "Spontaneous",
        "spontaneous ventilation": "Spontaneous",
        "spontaneous ventilation with supplemental oxygen": "Spontaneous",
        "spontaneous ventilation on supplemental oxygen": "Spontaneous",
        "spontaneous ventilation with pressure support": "Spontaneous",
        "pressure support": "Spontaneous",
        "cpap": "Spontaneous",
        # Jet variants
        "jet ventilation": "Jet Ventilation",
        "jet": "Jet Ventilation",
        "hfjv": "Jet Ventilation",
        "high frequency jet ventilation": "Jet Ventilation",
    }

    if text in mapping:
        return mapping[text]

    # Fuzzy matching
    if "jet" in text:
        return "Jet Ventilation"
    if "spontaneous" in text or "pressure support" in text:
        return "Spontaneous"
    if "controlled" in text or "volume control" in text or "pressure control" in text or "mechanical" in text:
        return "Controlled Mechanical Ventilation"

    return None


def normalize_procedure_setting(raw: Any) -> str | None:
    """Normalize procedure setting to schema enum values.

    Schema enum: ["Bronchoscopy Suite", "Operating Room", "ICU", "Bedside", "Office/Clinic"]
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text or text in {"none", "n/a", "na", "null"}:
        return None

    mapping = {
        "bronchoscopy suite": "Bronchoscopy Suite",
        "bronchoscopy room": "Bronchoscopy Suite",
        "bronch suite": "Bronchoscopy Suite",
        "hybrid bronchoscopy suite": "Bronchoscopy Suite",
        "procedure room": "Bronchoscopy Suite",
        "endoscopy suite": "Bronchoscopy Suite",
        "operating room": "Operating Room",
        "or": "Operating Room",
        "main or": "Operating Room",
        "surgery": "Operating Room",
        "icu": "ICU",
        "intensive care unit": "ICU",
        "micu": "ICU",
        "sicu": "ICU",
        "ccu": "ICU",
        "bedside": "Bedside",
        "at bedside": "Bedside",
        "patient room": "Bedside",
        "office/clinic": "Office/Clinic",
        "office": "Office/Clinic",
        "clinic": "Office/Clinic",
        "outpatient clinic": "Office/Clinic",
    }

    if text in mapping:
        return mapping[text]

    # Fuzzy matching
    if "bronchoscopy" in text or "bronch" in text or "endoscopy" in text:
        return "Bronchoscopy Suite"
    if "operating room" in text or text == "or":
        return "Operating Room"
    if "icu" in text or "intensive care" in text:
        return "ICU"
    if "bedside" in text or "patient room" in text:
        return "Bedside"
    if "office" in text or "clinic" in text:
        return "Office/Clinic"

    return None


def normalize_bronch_location_lobe(raw: Any) -> str | None:
    """Normalize bronchoscopy location lobe to schema enum values.

    Schema enum: ["RUL", "RML", "RLL", "LUL", "LLL", "Central"]
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text or text in {"none", "n/a", "na", "null"}:
        return None

    mapping = {
        # Right upper lobe
        "rul": "RUL",
        "right upper lobe": "RUL",
        "right upper": "RUL",
        # Right middle lobe
        "rml": "RML",
        "right middle lobe": "RML",
        "right middle": "RML",
        # Right lower lobe
        "rll": "RLL",
        "right lower lobe": "RLL",
        "right lower": "RLL",
        # Left upper lobe
        "lul": "LUL",
        "left upper lobe": "LUL",
        "left upper": "LUL",
        # Left lower lobe
        "lll": "LLL",
        "left lower lobe": "LLL",
        "left lower": "LLL",
        # Central airways
        "central": "Central",
        "central airways": "Central",
        "trachea": "Central",
        "carina": "Central",
        "mainstem": "Central",
    }

    if text in mapping:
        return mapping[text]

    # Fuzzy matching
    if "right upper" in text or text == "rul":
        return "RUL"
    if "right middle" in text or text == "rml":
        return "RML"
    if "right lower" in text or text == "rll":
        return "RLL"
    if "left upper" in text or text == "lul":
        return "LUL"
    if "left lower" in text or text == "lll":
        return "LLL"
    if "central" in text or "trachea" in text or "carina" in text or "mainstem" in text:
        return "Central"

    return None


def normalize_cpt_codes(raw: Any) -> List[str] | None:
    """Normalize CPT codes to a list of string CPT code values only.

    Per specification:
    - Always returns array of strings containing only the CPT code itself
    - Example: ["31652"] not ["31652 convex probe endobronchial..."]
    - Extracts just the numeric code from longer descriptive strings
    - Modifiers if present are kept as separate entries
    """
    if raw is None:
        return None

    # CPT code pattern: 5-digit number (may have optional modifier like -26)
    cpt_pattern = re.compile(r"\b(\d{5})(?:-(\d{2}))?\b")

    def extract_cpt_codes(text: str) -> List[str]:
        """Extract CPT code(s) from a string, handling descriptive text."""
        codes = []
        # First try to extract CPT codes with pattern
        for match in cpt_pattern.finditer(text):
            code = match.group(1)
            modifier = match.group(2)
            if modifier:
                codes.append(f"{code}-{modifier}")
            else:
                codes.append(code)
        # If no pattern match but text is purely numeric (5 digits), use it
        if not codes:
            clean = text.strip()
            if re.fullmatch(r"\d{5}", clean):
                codes.append(clean)
        return codes

    normalized: List[str] = []

    if isinstance(raw, list):
        for item in raw:
            if item is None:
                continue
            item_str = str(item).strip()
            if not item_str:
                continue
            codes = extract_cpt_codes(item_str)
            for code in codes:
                if code not in normalized:
                    normalized.append(code)
    elif isinstance(raw, str):
        if not raw.strip():
            return None
        # Handle comma-separated strings
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            codes = extract_cpt_codes(part)
            for code in codes:
                if code not in normalized:
                    normalized.append(code)
    else:
        # Try to convert other types
        try:
            s = str(raw).strip()
            if s:
                codes = extract_cpt_codes(s)
                for code in codes:
                    if code not in normalized:
                        normalized.append(code)
        except Exception:
            pass

    return normalized if normalized else None


def normalize_attending_name(raw: Any) -> str | None:
    """Normalize attending physician name, removing role/specialty from the name.

    Per specification:
    - attending_name should contain only the clinician's name and credentials
    - Example: "Russell Miller MD" not "Russell Miller MD, Pulmonologist"
    - Role/specialty should go in provider_role field instead
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip()
    if not text or text.lower() in {"none", "n/a", "na", "null", ""}:
        return None

    # Common roles/specialties to strip from the name
    role_patterns = [
        r",?\s*(?:Interventional\s+)?Pulmonologist\s*$",
        r",?\s*(?:Interventional\s+)?Pulmonology\s*$",
        r",?\s*Thoracic\s+Surgeon\s*$",
        r",?\s*Thoracic\s+Surgery\s*$",
        r",?\s*Pulmonary(?:/Critical\s+Care)?\s*$",
        r",?\s*Critical\s+Care\s*$",
        r",?\s*Fellow\s*$",
        r",?\s*Attending\s*$",
        r",?\s*Physician\s*$",
        r",?\s*Surgeon\s*$",
    ]

    result = text
    for pattern in role_patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE).strip()

    # Clean up any trailing commas or whitespace
    result = result.rstrip(",").strip()

    return result if result else None


def normalize_provider_role(raw: Any) -> str | None:
    """Normalize provider role/specialty to canonical form.

    Common values: Pulmonologist, Interventional Pulmonologist, Thoracic Surgeon, Fellow
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if not text or text in {"none", "n/a", "na", "null", ""}:
        return None

    mapping = {
        "pulmonologist": "Pulmonologist",
        "pulmonology": "Pulmonologist",
        "interventional pulmonologist": "Interventional Pulmonologist",
        "interventional pulmonology": "Interventional Pulmonologist",
        "ip": "Interventional Pulmonologist",
        "thoracic surgeon": "Thoracic Surgeon",
        "thoracic surgery": "Thoracic Surgeon",
        "fellow": "Fellow",
        "pulmonary fellow": "Fellow",
        "ip fellow": "Fellow",
        "attending": "Attending",
        "attending physician": "Attending",
    }

    if text in mapping:
        return mapping[text]

    # Fuzzy matching
    if "interventional" in text and "pulmon" in text:
        return "Interventional Pulmonologist"
    if "pulmon" in text:
        return "Pulmonologist"
    if "thoracic" in text:
        return "Thoracic Surgeon"
    if "fellow" in text:
        return "Fellow"

    return text_raw.strip()  # Return original if no match


def normalize_immediate_complications(raw: Any) -> str | None:
    """Normalize immediate complications field to standardized vocabulary.

    Per specification:
    - Normalize variations like "No immediate complications" to "None"
    - For complications that did occur, use concise standard terms
    - Standardize vocabulary for consistency
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip()
    if not text:
        return None

    lowered = text.lower()

    # Normalize "no complications" variations to "None"
    no_complication_patterns = [
        r"^no\s+(?:immediate\s+)?complications?\.?$",
        r"^none\s+(?:noted|observed|reported)?\.?$",
        r"^no\s+(?:immediate\s+)?adverse\s+events?\.?$",
        r"^nil\.?$",
        r"^n/a\.?$",
        r"^na\.?$",
        r"^none\.?$",
    ]
    for pattern in no_complication_patterns:
        if re.match(pattern, lowered):
            return "None"

    # Standard complication mappings
    complication_mapping = {
        "bleeding": "Bleeding",
        "hemorrhage": "Bleeding",
        "pneumothorax": "Pneumothorax",
        "ptx": "Pneumothorax",
        "hypoxia": "Hypoxia",
        "hypoxemia": "Hypoxia",
        "desaturation": "Hypoxia",
        "respiratory failure": "Respiratory Failure",
        "bronchospasm": "Bronchospasm",
        "wheezing": "Bronchospasm",
        "arrhythmia": "Arrhythmia",
        "fever": "Fever",
        "infection": "Infection",
    }

    # Check for specific complications
    for key, value in complication_mapping.items():
        if key in lowered:
            return value

    # If none of the above, return cleaned original
    return text


def normalize_radiographic_findings(raw: Any) -> str | None:
    """Normalize radiographic findings, excluding non-imaging content.

    Per specification:
    - Only include actual radiographic/imaging descriptions (CT, PET, CXR findings)
    - Exclude sampling criteria (e.g., "nodes >= 5mm were sampled")
    - Exclude procedural details (needle passes, ROSE results, etc.)
    - Return null if no imaging description is present
    """
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip()
    if not text or text.lower() in {"none", "n/a", "na", "null", ""}:
        return None

    lowered = text.lower()

    # Patterns that indicate this is NOT a radiographic finding (should be excluded)
    exclusion_patterns = [
        r"sampling\s+criteria",
        r"nodes?\s*(?:>=?|≥|greater\s+than)\s*\d+\s*mm\s+(?:were\s+)?sampled",
        r"short\s+axis\s+(?:diameter\s+)?(?:criteria|threshold)",
        r"(?:were\s+)?met\s+(?:for\s+)?sampling",
        r"needle\s+pass",
        r"rose\s+(?:result|showed|demonstrates)",
        r"specimen\s+(?:sent|obtained)",
        r"cytolog",
        r"patholog",
        r"biopsy\s+(?:result|showed)",
    ]

    for pattern in exclusion_patterns:
        if re.search(pattern, lowered):
            return None

    # Patterns that indicate valid radiographic findings
    valid_imaging_patterns = [
        r"(?:ct|pet|cxr|x-ray|chest\s+x-ray|imaging|scan)",
        r"(?:nodule|mass|lesion|opacity|consolidation)",
        r"(?:hilar|mediastinal)\s+(?:adenopathy|lymphadenopathy)",
        r"(?:suv|standardized\s+uptake)",
        r"(?:avid|hypermetabolic)",
        r"(?:effusion|collapse|atelectasis)",
        r"(?:lobe|segment|upper|lower|middle)",
    ]

    has_imaging_content = any(re.search(pat, lowered) for pat in valid_imaging_patterns)

    if has_imaging_content:
        return text

    # If no clear imaging content, return None rather than procedural text
    return None


def apply_cross_field_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply cross-field consistency checks and corrections.

    Per specification, ensures fields are consistent with each other:
    - pneumothorax_intervention is null when pneumothorax=false
    - bronch_tbbx_tool is null when bronch_num_tbbx is null/0
    - ebus_stations_detail stations match ebus_stations_sampled
    - etc.
    """
    result = dict(data)

    # Pneumothorax consistency
    if result.get("pneumothorax") is False:
        result["pneumothorax_intervention"] = None

    # Transbronchial biopsy consistency
    num_tbbx = result.get("bronch_num_tbbx")
    if num_tbbx is None or num_tbbx == 0:
        result["bronch_tbbx_tool"] = None

    # EBUS station consistency
    # Ensure ebus_stations_sampled and ebus_stations_detail are consistent
    station_detail = result.get("ebus_stations_detail") or []
    stations_sampled = result.get("ebus_stations_sampled") or []

    if station_detail:
        # Get stations from detail
        detail_stations = {d.get("station") for d in station_detail if d.get("station")}
        # Merge with sampled
        all_stations = set(stations_sampled) | detail_stations
        if all_stations:
            result["ebus_stations_sampled"] = sorted(all_stations)
            # Also update linear_ebus_stations to match
            result["linear_ebus_stations"] = sorted(all_stations)

    # Derive global ROSE result from per-station data if available
    if station_detail and not result.get("ebus_rose_result"):
        derived_rose = derive_global_ebus_rose_result(station_detail)
        if derived_rose:
            result["ebus_rose_result"] = derived_rose

    # Pleural consistency - if no pleural procedure, clear pleural fields
    if not result.get("pleural_procedure_type"):
        pleural_fields = [
            "pleural_side", "pleural_volume_drained_ml", "pleural_fluid_appearance",
            "pleural_guidance", "pleural_intercostal_space", "pleural_catheter_type",
            "pleural_opening_pressure_measured", "pleural_opening_pressure_cmh2o",
        ]
        for field in pleural_fields:
            if field in result:
                result[field] = None

    return result


POSTPROCESSORS: Dict[str, Callable[[Any], Any]] = {
    "sedation_type": normalize_sedation_type,
    "airway_type": normalize_airway_type,
    "pleural_guidance": map_pleural_guidance,
    "pleural_procedure_type": normalize_pleural_procedure,
    "pleural_side": normalize_pleural_side,
    "pleural_intercostal_space": normalize_pleural_intercostal_space,
    "patient_mrn": postprocess_patient_mrn,
    "procedure_date": normalize_procedure_date,
    "disposition": normalize_disposition,
    "asa_class": postprocess_asa_class,
    "final_diagnosis_prelim": normalize_final_diagnosis_prelim,
    "stent_type": normalize_stent_type,
    "stent_location": normalize_stent_location,
    "stent_deployment_method": normalize_stent_deployment_method,
    "ebus_rose_result": normalize_ebus_rose_result,
    "ebus_needle_gauge": normalize_ebus_needle_gauge,
    "ebus_needle_type": normalize_ebus_needle_type,
    "ebus_stations_detail": normalize_ebus_stations_detail,
    "ebus_elastography_pattern": normalize_elastography_pattern,
    # List field normalizers - convert comma-separated strings to lists
    "anesthesia_agents": normalize_anesthesia_agents,
    "ebus_stations_sampled": normalize_ebus_stations,
    "linear_ebus_stations": normalize_linear_ebus_stations,
    "nav_sampling_tools": normalize_nav_sampling_tools,
    "nav_registration_method": normalize_nav_registration_method,
    "follow_up_plan": normalize_follow_up_plan,
    "pleural_thoracoscopy_findings": normalize_list_field,
    "fb_tool_used": normalize_list_field,
    "bronch_specimen_tests": normalize_list_field,
    "cao_location": normalize_cao_location,
    "cao_tumor_location": normalize_cao_tumor_location,
    "cpt_codes": normalize_cpt_codes,
    # Ablation modality - converts list to single value and normalizes to enum
    "ablation_modality": normalize_ablation_modality,
    # Airway device size - converts int/float to string
    "airway_device_size": normalize_airway_device_size,
    # Multi-assistant support - converts single name or comma-separated to list
    "assistant_names": normalize_assistant_names,
    # Also handle legacy field name migration
    "assistant_name": normalize_assistant_name_single,
    # New normalizers for validation consistency
    "ventilation_mode": normalize_ventilation_mode,
    "procedure_setting": normalize_procedure_setting,
    "bronch_location_lobe": normalize_bronch_location_lobe,
    # Provider and role normalization
    "attending_name": normalize_attending_name,
    "provider_role": normalize_provider_role,
    # Complication and safety field normalization
    "bronch_immediate_complications": normalize_immediate_complications,
    # Radiographic findings - exclude non-imaging content
    "radiographic_findings": normalize_radiographic_findings,
}
