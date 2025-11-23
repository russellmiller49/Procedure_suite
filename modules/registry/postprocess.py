"""Field-specific normalization for registry extraction outputs."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, List
import re
from datetime import datetime

__all__ = [
    "normalize_sedation_type",
    "normalize_airway_type",
    "map_pleural_guidance",
    "normalize_pleural_procedure",
    "postprocess_patient_mrn",
    "normalize_procedure_date",
    "normalize_disposition",
    "postprocess_asa_class",
    "normalize_final_diagnosis_prelim",
    "normalize_stent_type",
    "normalize_stent_location",
    "normalize_stent_deployment_method",
    "normalize_ebus_rose_result",
    "normalize_ebus_needle_gauge",
    "normalize_ebus_needle_type",
    "normalize_list_field",
    "normalize_anesthesia_agents",
    "normalize_ebus_stations",
    "normalize_nav_sampling_tools",
    "normalize_follow_up_plan",
    "normalize_cao_location",
    "normalize_cao_tumor_location",
    "normalize_cpt_codes",
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
        # Default per instruction: moderate if undocumented
        return "Moderate"
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
        "monitored anesthesia care": "Monitored Anesthesia Care",
        "mac": "Monitored Anesthesia Care",
        "mac anesthesia": "Monitored Anesthesia Care",
    }

    if text in mapping:
        val = mapping[text]
    else:
        if "general" in text and "anesth" in text:
            val = "General"
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
                "monitored anesthesia care": "Monitored Anesthesia Care",
            }
            val = lowered_allowed.get(text, None)

    allowed = {"Moderate", "Deep", "General", "Local", "Monitored Anesthesia Care"}
    return val if val in allowed else "Moderate"


def normalize_airway_type(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    text = text_raw.strip().lower()
    if text in {"", "none", "n/a", "na", "null"}:
        return None

    mapping = {
        "native": "Native",
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
    if "native" in text or "natural airway" in text:
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
        "tunneled catheter": "Tunneled Catheter",
        "tunnelled catheter": "Tunneled Catheter",
        "medical thoracoscopy": "Medical Thoracoscopy",
        "chemical pleurodesis": "Chemical Pleurodesis",
    }
    if text in canonical:
        return canonical[text]

    if "pleurodesis" in text:
        return "Chemical Pleurodesis"

    if "tunneled" in text or "tunnelled" in text:
        if "catheter" in text or "pleural catheter" in text:
            return "Tunneled Catheter"

    if "thoracoscopy" in text or "pleuroscopy" in text:
        return "Medical Thoracoscopy"

    if any(k in text for k in ["chest tube", "pleural drain", "pleural tube", "pigtail", "intercostal drain", "icd"]):
        return "Chest Tube"

    if "thoracentesis" in text or "pleural tap" in text:
        return "Thoracentesis"

    for k, v in canonical.items():
        if k in text:
            return v

    return None


def postprocess_patient_mrn(raw: Any) -> str | None:
    text_raw = _coerce_to_text(raw)
    if text_raw is None:
        return None
    s = text_raw
    date_patterns = [
        r"^\d{1,2}/\d{1,2}/\d{2,4}$",
        r"^\d{1,2}-\d{1,2}-\d{2,4}$",
        r"^\d{4}-\d{1,2}-\d{1,2}$",
    ]
    for pat in date_patterns:
        if re.match(pat, s):
            return None

    m = re.match(r"^(?:MRN|Mrn|mrn|ID|Id|id)[:#\s-]*([A-Za-z0-9-]+)$", s)
    if m:
        s = m.group(1)
    return s or None


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
        "to home",
        "go home",
        "going home",
        "ok for discharge",
        "ok to discharge",
        "same-day discharge",
        "same day discharge",
    ]
    if any(k in text for k in home_keywords):
        return "Discharge Home"

    return None


def postprocess_asa_class(raw_text: Any) -> str | None:
    text_raw = _coerce_to_text(raw_text)
    if text_raw is None or not str(text_raw).strip():
        # Default ASA when not documented
        return 3
    cleaned = str(text_raw).strip().upper()
    # Extract first digit if present
    m = re.search(r"([1-5])", cleaned)
    if m:
        return int(m.group(1))
    return 3


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
    if "malig" in t or "carcinoma" in t or "adenocarcinoma" in t:
        return "Malignancy"
    if "non" in t and "diagnostic" in t:
        return "Non-diagnostic"
    return "Other"


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


def normalize_ebus_rose_result(raw: Any) -> str | None:
    # Per latest instructions, leave empty/None for now
    return None


def normalize_ebus_needle_gauge(raw: Any) -> str | None:
    return None


def normalize_ebus_needle_type(raw: Any) -> str | None:
    return None


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
    """Normalize EBUS stations list, handling comma-separated strings."""
    result = normalize_list_field(raw)
    if result is None:
        return None
    # Clean and validate station format (e.g., "4R", "7", "11L")
    normalized = []
    for station in result:
        cleaned = station.strip().upper()
        # Remove common prefixes/suffixes
        cleaned = re.sub(r"^(STATION|STN|NODE)[\s:]*", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized if normalized else None


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


def normalize_cpt_codes(raw: Any) -> List[int | str] | None:
    """Normalize CPT codes, handling comma-separated strings and converting to list of int/str."""
    if raw is None:
        return None
    
    # If already a list, normalize items
    if isinstance(raw, list):
        normalized = []
        for item in raw:
            if item is None:
                continue
            # Try to convert to int if it's a numeric string
            if isinstance(item, str):
                item_clean = item.strip()
                if not item_clean:
                    continue
                try:
                    normalized.append(int(item_clean))
                except ValueError:
                    # Keep as string if it contains non-numeric characters (e.g., modifiers)
                    normalized.append(item_clean)
            elif isinstance(item, int):
                normalized.append(item)
            else:
                # Try to convert other types
                try:
                    normalized.append(int(item))
                except (ValueError, TypeError):
                    normalized.append(str(item).strip())
        return normalized if normalized else None
    
    # If it's a string, split by comma and process
    if isinstance(raw, str):
        if not raw.strip():
            return None
        items = [item.strip() for item in raw.split(",") if item.strip()]
        normalized = []
        for item in items:
            try:
                normalized.append(int(item))
            except ValueError:
                # Keep as string if it contains non-numeric characters
                normalized.append(item)
        return normalized if normalized else None
    
    # Try to convert other types to string and split
    try:
        s = str(raw).strip()
        if not s:
            return None
        items = [item.strip() for item in s.split(",") if item.strip()]
        normalized = []
        for item in items:
            try:
                normalized.append(int(item))
            except ValueError:
                normalized.append(item)
        return normalized if normalized else None
    except Exception:
        return None


POSTPROCESSORS: Dict[str, Callable[[Any], Any]] = {
    "sedation_type": normalize_sedation_type,
    "airway_type": normalize_airway_type,
    "pleural_guidance": map_pleural_guidance,
    "pleural_procedure_type": normalize_pleural_procedure,
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
    # List field normalizers - convert comma-separated strings to lists
    "anesthesia_agents": normalize_anesthesia_agents,
    "ebus_stations_sampled": normalize_ebus_stations,
    "nav_sampling_tools": normalize_nav_sampling_tools,
    "follow_up_plan": normalize_follow_up_plan,
    "cao_location": normalize_cao_location,
    "cao_tumor_location": normalize_cao_tumor_location,
    "cpt_codes": normalize_cpt_codes,
}
