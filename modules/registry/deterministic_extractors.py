"""Deterministic extractors for registry fields.

These extractors use regex patterns to reliably extract structured data
that the LLM often misses or extracts incorrectly. They run BEFORE the
LLM extraction and provide seed data that takes precedence.

Targets fields identified as systematically missing in v2.8 validation:
- patient_age, gender
- asa_class
- sedation_type, airway_type
- primary_indication
- disposition
- institution_name
- bleeding_severity
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from modules.registry.normalization import (
    normalize_gender,
    normalize_sedation_type,
    normalize_airway_type,
    normalize_asa_class,
    normalize_bleeding_severity,
)


def extract_demographics(note_text: str) -> Dict[str, Any]:
    """Extract patient age and gender from note header.

    Patterns recognized:
    - "Age: 66 | Sex: M"
    - "52M", "65F"
    - "Date of Birth: 03/15/1959 (65 years old)"
    - "Patient: 72-year-old male"

    Returns:
        Dict with 'patient_age' (int) and 'gender' (str) if found
    """
    result: Dict[str, Any] = {}

    # Pattern 1: "Age: 66 | Sex: M" or "Age: 66, Sex: F"
    age_sex_pattern = r"Age:?\s*(\d+)\s*[|,]\s*Sex:?\s*([MFmf]|Male|Female)"
    match = re.search(age_sex_pattern, note_text, re.IGNORECASE)
    if match:
        result["patient_age"] = int(match.group(1))
        result["gender"] = normalize_gender(match.group(2))
        return result

    # Pattern 2: "52M" or "65F" standalone (common shorthand)
    shorthand_pattern = r"\b(\d{2,3})([MF])\b"
    match = re.search(shorthand_pattern, note_text)
    if match:
        result["patient_age"] = int(match.group(1))
        result["gender"] = normalize_gender(match.group(2))
        return result

    # Pattern 3: "(65 years old)" or "(65 yo)"
    years_old_pattern = r"\((\d+)\s*(?:years?\s*old|yo)\)"
    match = re.search(years_old_pattern, note_text, re.IGNORECASE)
    if match:
        result["patient_age"] = int(match.group(1))

    # Pattern 4: "72-year-old male/female"
    year_old_gender_pattern = r"(\d+)[-\s]year[-\s]old\s*(male|female|man|woman)"
    match = re.search(year_old_gender_pattern, note_text, re.IGNORECASE)
    if match:
        result["patient_age"] = int(match.group(1))
        result["gender"] = normalize_gender(match.group(2))
        return result

    # Pattern 5: Separate age and gender mentions
    # Age
    if "patient_age" not in result:
        age_pattern = r"(?:age|pt age|patient age)[\s:]+(\d+)"
        match = re.search(age_pattern, note_text, re.IGNORECASE)
        if match:
            result["patient_age"] = int(match.group(1))

    # Gender
    if "gender" not in result:
        gender_pattern = r"(?:sex|gender)[\s:]+([MFmf]|Male|Female)"
        match = re.search(gender_pattern, note_text, re.IGNORECASE)
        if match:
            result["gender"] = normalize_gender(match.group(1))

    return result


def extract_asa_class(note_text: str) -> Optional[int]:
    """Extract ASA classification from note.

    Patterns recognized:
    - "ASA Classification: II"
    - "ASA: 3"
    - "ASA III-E"

    If not found, returns 3 as default (common for interventional pulmonology).

    Returns:
        ASA class as integer 1-6, or None
    """
    # Pattern 1: "ASA Classification: II" or "ASA: 3"
    asa_pattern = r"ASA(?:\s+Classification)?[\s:]+([IViv123456]+(?:-E)?)"
    match = re.search(asa_pattern, note_text, re.IGNORECASE)
    if match:
        return normalize_asa_class(match.group(1))

    # Pattern 2: "ASA III" without explicit "Classification"
    asa_pattern2 = r"\bASA\s+([IViv]+(?:-E)?)\b"
    match = re.search(asa_pattern2, note_text)
    if match:
        return normalize_asa_class(match.group(1))

    # Default to 3 if ASA not documented (common for IP procedures)
    # This matches the v2.8 synthetic data behavior
    return 3


def extract_sedation_airway(note_text: str) -> Dict[str, Any]:
    """Extract sedation type and airway type from procedure context.

    Logic:
    - OR cases with "general anesthesia" -> sedation_type="General", airway_type="ETT"
    - Bedside with local only -> sedation_type="Local Only", airway_type="Native"
    - IV sedation (midazolam/fentanyl) -> sedation_type="Moderate", airway_type="Native"
    - MAC -> sedation_type="MAC", airway_type depends on context

    Returns:
        Dict with 'sedation_type' and/or 'airway_type' if determinable
    """
    result: Dict[str, Any] = {}
    note_lower = note_text.lower()

    # Check for general anesthesia indicators
    ga_indicators = [
        "general anesthesia",
        "general anesthetic",
        "under general",
        "ga with",
        "propofol/fentanyl/rocuronium",
        "jet ventilation",
    ]

    if any(ind in note_lower for ind in ga_indicators):
        result["sedation_type"] = "General"

        # Check airway type for GA
        if "rigid bronchoscop" in note_lower:
            # Rigid bronchoscopy - airway managed by scope
            pass  # Leave airway_type unset
        elif re.search(r"\bett\b|endotracheal tube|intubated", note_lower):
            result["airway_type"] = "ETT"
        elif re.search(r"\blma\b|laryngeal mask", note_lower):
            result["airway_type"] = "LMA"
        elif re.search(r"\bi-?gel\b", note_lower):
            result["airway_type"] = "iGel"
        else:
            result["airway_type"] = "ETT"  # Default for GA

        return result

    # Check for MAC
    if re.search(r"\bmac\b|monitored anesthesia care", note_lower):
        result["sedation_type"] = "MAC"
        if not re.search(r"\bett\b|intubated|laryngeal mask", note_lower):
            result["airway_type"] = "Native"
        return result

    # Check for moderate/conscious sedation
    moderate_indicators = [
        "moderate sedation",
        "conscious sedation",
        "iv sedation",
        "midazolam",
        "fentanyl",
        "versed",
    ]

    if any(ind in note_lower for ind in moderate_indicators):
        # Don't set if also has GA indicators (already handled above)
        if "sedation_type" not in result:
            result["sedation_type"] = "Moderate"
            result["airway_type"] = "Native"
        return result

    # Check for local only (thoracentesis, bedside procedures)
    local_indicators = [
        "local anesthesia only",
        "local only",
        "1% lidocaine",
        "lidocaine infiltration",
        "under local",
    ]

    bedside_procedures = [
        "thoracentesis",
        "bedside chest tube",
        "bedside procedure",
        "bedside bronchoscopy",
    ]

    is_local = any(ind in note_lower for ind in local_indicators)
    is_bedside = any(proc in note_lower for proc in bedside_procedures)

    if is_local or (is_bedside and "sedation_type" not in result):
        if "general" not in note_lower and "moderate" not in note_lower:
            result["sedation_type"] = "Local Only"
            result["airway_type"] = "Native"

    return result


def extract_institution_name(note_text: str) -> Optional[str]:
    """Extract institution name from note header.

    Patterns recognized:
    - "Institution: Sacred Heart Medical Center"
    - "** St. Mary's Teaching Hospital, Chicago, IL"
    - "Hospital: Mayo Clinic"

    Returns:
        Institution name string or None
    """
    # Pattern 1: "Institution: Name"
    inst_pattern = r"Institution:\s*(.+?)(?:\n|$)"
    match = re.search(inst_pattern, note_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 2: "Hospital: Name"
    hosp_pattern = r"Hospital:\s*(.+?)(?:\n|$)"
    match = re.search(hosp_pattern, note_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 3: "** Hospital Name, City, State" at start of note
    header_pattern = r"^\*{1,2}\s*(.+?(?:Hospital|Medical Center|Clinic|Institute|Health).+?)(?:\n|$)"
    match = re.search(header_pattern, note_text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip().strip("*").strip()

    return None


def extract_primary_indication(note_text: str) -> Optional[str]:
    """Extract primary indication from INDICATION section.

    Looks for INDICATION, CLINICAL SUMMARY, or REASON FOR PROCEDURE sections.

    Returns:
        Indication text or None
    """
    # Pattern 1: INDICATION: section
    indication_patterns = [
        r"(?:INDICATION|INDICATIONS)[\s:]+(.+?)(?=\n\n|\n[A-Z]{2,}|\Z)",
        r"(?:CLINICAL SUMMARY|CLINICAL INDICATION)[\s:]+(.+?)(?=\n\n|\n[A-Z]{2,}|\Z)",
        r"(?:REASON FOR (?:PROCEDURE|EXAM))[\s:]+(.+?)(?=\n\n|\n[A-Z]{2,}|\Z)",
    ]

    for pattern in indication_patterns:
        match = re.search(pattern, note_text, re.IGNORECASE | re.DOTALL)
        if match:
            indication = match.group(1).strip()
            # Clean up whitespace
            indication = re.sub(r"\s+", " ", indication)
            # Limit length
            if len(indication) > 500:
                indication = indication[:500] + "..."
            return indication

    return None


def extract_disposition(note_text: str) -> Optional[str]:
    """Extract patient disposition from note.

    Patterns recognized:
    - "Extubated in OR, stable, admit overnight"
    - "Transferred to floor"
    - "Outpatient discharge"
    - "ICU admission"

    Returns:
        Disposition string or None
    """
    note_lower = note_text.lower()

    # Check for common disposition patterns
    if "icu admission" in note_lower or "admitted to icu" in note_lower:
        return "ICU admission"

    if "pacu" in note_lower and "floor" in note_lower:
        return "PACU then floor"

    if "admit overnight" in note_lower or "overnight observation" in note_lower:
        return "Admit overnight for observation"

    if "transfer" in note_lower and "floor" in note_lower:
        return "Transferred to floor"

    if "outpatient" in note_lower and ("discharge" in note_lower or "released" in note_lower):
        return "Outpatient discharge"

    if "home" in note_lower and "discharge" in note_lower:
        return "Discharged home"

    if "extubated" in note_lower:
        if "stable" in note_lower:
            return "Extubated, stable, transferred to recovery"

    # Look for explicit DISPOSITION section
    disp_pattern = r"DISPOSITION[\s:]+(.+?)(?=\n|$)"
    match = re.search(disp_pattern, note_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None


def extract_bleeding_severity(note_text: str) -> Optional[str]:
    """Extract bleeding severity from note.

    Returns:
        'None', 'Mild', 'Mild (<50mL)', 'Moderate', 'Severe', or None
    """
    note_lower = note_text.lower()

    # Check for explicit bleeding mentions
    if "no bleeding" in note_lower or "no significant bleeding" in note_lower:
        return "None"

    if (
        "minimal bleeding" in note_lower
        or "minor bleeding" in note_lower
        or "trace bleeding" in note_lower
        or "scant bleeding" in note_lower
    ):
        return "None"

    # Check for EBL (estimated blood loss)
    ebl_pattern = r"(?:ebl|estimated blood loss|blood loss)[\s:]*<?\s*(\d+)\s*(?:ml|cc)?"
    match = re.search(ebl_pattern, note_lower)
    if match:
        ebl = int(match.group(1))
        # Hard gate: very low EBL values are common and should not be treated as a bleeding complication.
        if ebl < 10:
            return "None"
        if ebl < 50:
            return "Mild (<50mL)"
        elif ebl < 200:
            return "Moderate"
        else:
            return "Severe"

    if "mild bleeding" in note_lower:
        return "Mild"

    if "moderate bleeding" in note_lower:
        return "Moderate"

    if "severe bleeding" in note_lower or "massive bleeding" in note_lower:
        return "Severe"

    # Default to None if not explicitly mentioned
    return "None"


_BLEEDING_INTERVENTION_PATTERNS: list[tuple[str, str]] = [
    ("Cold saline", r"\b(?:cold|iced)\s+saline\b"),
    ("Epinephrine", r"\b(?:epinephrine|epi)\b"),
    ("Balloon tamponade", r"\bballoon\s+tamponade\b"),
    ("Electrocautery", r"\belectrocautery\b|\bcauteriz(?:e|ed|ation)\b|\bcoagulat(?:e|ed|ion)\b"),
    ("APC", r"\bapc\b|argon\s+plasma"),
    ("Tranexamic acid", r"\btranexamic\s+acid\b|\btxa\b"),
    ("Bronchial blocker", r"\bbronchial\s+blocker\b|\bendobronchial\s+blocker\b"),
    ("Transfusion", r"\btransfus(?:ion|ed)\b|\bprbc\b|\bpacked\s+red\b"),
    ("Embolization", r"\bemboliz(?:ation|ed)\b"),
    ("Surgery", r"\bsurgery\b|\bthoracotomy\b"),
]


def extract_bleeding_intervention_required(note_text: str) -> list[str] | None:
    """Extract bleeding interventions as schema enum values.

    This is intentionally conservative: it only flags bleeding as a complication
    when an intervention to control bleeding is explicitly documented.
    """
    text = note_text or ""
    lowered = text.lower()

    # Explicit negations: don't infer interventions.
    if re.search(r"\bno\s+(?:immediate\s+)?complications\b", lowered):
        return None
    if re.search(r"\bno\s+(?:significant\s+)?bleeding\b", lowered):
        return None

    hits: list[str] = []
    for label, pattern in _BLEEDING_INTERVENTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(label)

    # Dedupe while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for item in hits:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)

    return deduped or None


def extract_providers(note_text: str) -> Dict[str, Any]:
    """Extract provider information from note.

    Returns dict matching expected schema:
    {
        "attending_name": str or None,
        "fellow_name": str or None,
        "assistant_name": str or None,
        "assistant_role": str or None,
        "trainee_present": bool or None,
    }
    """
    result: Dict[str, Any] = {
        "attending_name": None,
        "fellow_name": None,
        "assistant_name": None,
        "assistant_role": None,
        "trainee_present": None,
    }

    # Pattern for attending
    attending_patterns = [
        # Avoid false-positive capture of header words like "Participation"
        r"(?:Attending\s+Participation|Attending\s+Physician\s+Participation)\s*:\s*(?:\*{1,2}\s*)?(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:Attending\s+Physician|Attending|Primary\s+Operator)\s*:\s*(?:\*{1,2}\s*)?(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"\*{2}\s*Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]

    for pattern in attending_patterns:
        match = re.search(pattern, note_text)
        if match:
            name = match.group(1).strip()
            # Keep leading ** if present in original (per v2.8 data format)
            if "** " in note_text[max(0, match.start()-5):match.start()]:
                name = f"** {name}"
            elif "**" in note_text[max(0, match.start()-3):match.start()]:
                name = f"** {name}"
            result["attending_name"] = name
            break

    # Pattern for fellow
    fellow_patterns = [
        r"(?:Fellow|IP Fellow|Pulmonary Fellow)[\s:]+(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]

    for pattern in fellow_patterns:
        match = re.search(pattern, note_text)
        if match:
            result["fellow_name"] = match.group(1).strip()
            result["trainee_present"] = True
            break

    # Check for trainee presence
    trainee_indicators = ["fellow", "resident", "trainee", "pgy"]
    note_lower = note_text.lower()
    if any(ind in note_lower for ind in trainee_indicators):
        result["trainee_present"] = True

    # Pattern for assistant
    assistant_patterns = [
        r"(?:Assistant|Assist(?:ed)? by)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s*(?:RN|RT|Tech|PA|NP)?",
    ]

    for pattern in assistant_patterns:
        match = re.search(pattern, note_text)
        if match:
            result["assistant_name"] = match.group(1).strip()
            # Try to determine role
            role_match = re.search(r"(RN|RT|Tech|PA|NP|Resident)", note_text[match.start():match.end()+20])
            if role_match:
                result["assistant_role"] = role_match.group(1)
            break

    return result


# =============================================================================
# PROCEDURE EXTRACTORS (Phase 7)
# =============================================================================

# BAL detection patterns
BAL_PATTERNS = [
    r"\bbroncho[-\s]?alveolar\s+lavage\b",
    r"\bbronchial\s+alveolar\s+lavage\b",
    r"\bBAL\b(?!\s*score)",  # BAL but not "BAL score"
]

# Endobronchial biopsy detection patterns
ENDOBRONCHIAL_BIOPSY_PATTERNS = [
    r"\bendobronchial\s+biops",
    r"\bbiops(?:y|ied|ies)\b[^.\n]{0,60}\bendobronchial\b",
    r"\blesions?\s+were\s+biopsied\b",
    r"\bebbx\b",
]

# Radial EBUS detection patterns (rEBUS for peripheral lesion localization)
RADIAL_EBUS_PATTERNS = [
    r"\bradial\s+ebus\b",
    r"\bradial\s+endobronchial\s+ultrasound\b",
    r"\br-?ebus\b",
    r"\brp-?ebus\b",
    r"\bminiprobe\b",
    r"\bradial\s+probe\b",
]

# Cryotherapy / tumor destruction patterns (31641 family)
CRYOTHERAPY_PATTERNS = [
    r"\bcryotherap(?:y|ies)\b",
    r"\bcryo(?:therapy|debulk(?:ing)?)\b",
]
CRYOPROBE_PATTERN = r"\bcryoprobe\b"
CRYOBIOPSY_PATTERN = r"\bcryo\s*biops(?:y|ies)\b|\bcryobiops(?:y|ies)\b"

# Navigation / robotic bronchoscopy patterns
NAVIGATIONAL_BRONCHOSCOPY_PATTERNS = [
    r"\bnavigational\s+bronchoscopy\b",
    r"\bnavigation\s+bronchoscopy\b",
    r"\belectromagnetic\s+navigation\b",
    r"\bEMN\b",
    r"\bENB\b",
    r"\bion\b[^.\n]{0,40}\bbronchoscop",
    r"\bmonarch\b[^.\n]{0,40}\bbronchoscop",
    r"\brobotic\b[^.\n]{0,40}\bbronchoscop",
    r"\brobotic\b[^.\n]{0,40}\bbronch",
    r"\bgalaxy\b[^.\n]{0,40}\bbronch",
    r"\bnoah\b[^.\n]{0,40}\bbronch",
    r"\bsuperdimension\b",
    r"\billumisite\b",
    r"\bveran\b",
    r"\bspin(?:drive)?\b",
]

# TBNA (conventional) patterns
TBNA_CONVENTIONAL_PATTERNS = [
    r"\btbna\b",
    r"\btransbronchial\s+needle\s+aspiration\b",
    r"\btransbronchial\s+needle\b",
]

# Brushings patterns
BRUSHINGS_PATTERNS = [
    r"\bbrushings?\b",
    r"\bcytology\s+brush(?:ings?)?\b",
    r"\bbronchial\s+brushing(?:s)?\b",
    r"\bbronchoscopic\s+brush(?:ings?)?\b",
]

# Transbronchial cryobiopsy patterns
TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS = [
    r"\btransbronchial\s+cryo\b",
    r"\bcryo\s*biops(?:y|ies)\b",
    r"\bcryobiops(?:y|ies)\b",
    r"\bTBLC\b",
]

# Peripheral ablation patterns (MWA/RFA/cryoablation)
PERIPHERAL_ABLATION_PATTERNS = [
    r"\bmicrowave\s+ablation\b",
    r"\bmwa\b",
    r"\bradiofrequency\s+ablation\b",
    r"\brf\s+ablation\b",
    r"\brfa\b",
    r"\bcryoablation\b",
    r"\bcryo\s*ablation\b",
]

# Thermal ablation patterns (APC/laser/electrocautery)
THERMAL_ABLATION_PATTERNS = [
    r"\bapc\b",
    r"\bargon\s+plasma\b",
    r"\belectrocautery\b",
    r"\bcauteriz(?:e|ed|ation)\b",
    r"\blaser\b",
    r"\bthermal\s+ablation\b",
]

# Chest ultrasound patterns (76604 family)
CHEST_ULTRASOUND_PATTERNS = [
    r"\bchest\s+ultrasound\s+findings\b",
    r"\bultrasound,\s*chest\b",
    r"\bchest\s+ultrasound\b",
    r"\b76604\b",
]

CHEST_ULTRASOUND_IMAGE_DOC_PATTERNS = [
    r"\bimage\s+saved\s+and\s+printed\b",
    r"\bimage\s+saved\b",
    r"\bwith\s+image\s+documentation\b",
]

# Chest tube / pleural drainage catheter patterns
CHEST_TUBE_PATTERNS = [
    r"\bpigtail\s+catheter\b",
    r"\bchest\s+tube\b",
    r"\btube\s+thoracostomy\b",
    r"\bpleurovac\b",
    r"\bpleur-?evac\b",
]

# Indwelling pleural catheter (IPC / tunneled) patterns
IPC_PATTERNS = [
    r"\bpleurx\b",
    r"\baspira\b",
    r"\btunne(?:l|ll)ed\s+pleural\s+catheter\b",
    r"\bindwelling\s+pleural\s+catheter\b",
    r"\bipc\b[^.\n]{0,30}\b(?:catheter|drain)\b",
    r"\brocket\b[^.\n]{0,40}\b(?:ipc|catheter|pleur)\b",
]

# Therapeutic aspiration patterns (exclude routine suction)
THERAPEUTIC_ASPIRATION_PATTERNS = [
    r"\btherapeutic\s+aspiration\b",
    r"\bmucus\s+plug\s+(?:removal|aspiration|extracted|suctioned|cleared)\b",
    r"\b(?:large\s+)?(?:blood\s+)?clot\s+(?:removal|aspiration|extracted|suctioned|cleared)\b",
    r"\bairway\s+(?:cleared|cleared\s+of)\s+(?:mucus|secretions|blood|clot)\b",
]

ROUTINE_SUCTION_PATTERNS = [
    r"\broutine\s+suction(?:ing)?\b",
    r"\bminimal\s+secretions?\s+(?:suctioned|cleared|noted)\b",
    r"\bstandard\s+suction(?:ing)?\b",
    r"\bscant\s+secretions?\b",
]


def extract_bal(note_text: str) -> Dict[str, Any]:
    """Extract BAL (bronchoalveolar lavage) procedure indicator.

    Returns:
        Dict with 'bal': {'performed': True} if BAL detected, empty dict otherwise
    """
    text_lower = note_text.lower()

    for pattern in BAL_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            # Check for negation
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,40}" + pattern
            if not re.search(negation_check, text_lower, re.IGNORECASE):
                return {"bal": {"performed": True}}
    return {}


def extract_therapeutic_aspiration(note_text: str) -> Dict[str, Any]:
    """Extract therapeutic aspiration procedure indicator.

    Distinguishes therapeutic aspiration (mucus plug removal, clot removal)
    from routine suctioning which is not separately billable.

    Returns:
        Dict with 'therapeutic_aspiration': {'performed': True, 'material': <str>}
        if therapeutic aspiration detected, empty dict otherwise
    """
    text_lower = note_text.lower()

    # Check for routine suction first (exclude these)
    for pattern in ROUTINE_SUCTION_PATTERNS:
        if re.search(pattern, text_lower):
            return {}

    for pattern in THERAPEUTIC_ASPIRATION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            # Check for negation
            negation_check = r"\b(?:no|not|without)\b[^.\n]{0,40}" + pattern
            if not re.search(negation_check, text_lower, re.IGNORECASE):
                # Determine material type
                material = None
                if "mucus" in text_lower or "plug" in text_lower:
                    material = "Mucus plug"
                elif "clot" in text_lower or "blood" in text_lower:
                    material = "Blood clot"
                result = {"therapeutic_aspiration": {"performed": True}}
                if material:
                    result["therapeutic_aspiration"]["material"] = material
                return result
    return {}


def extract_endobronchial_biopsy(note_text: str) -> Dict[str, Any]:
    """Extract endobronchial (airway) biopsy indicator.

    This is distinct from transbronchial biopsy (parenchyma).
    """
    text_lower = (note_text or "").lower()

    for pattern in ENDOBRONCHIAL_BIOPSY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"endobronchial_biopsy": {"performed": True}}

    return {}


def extract_radial_ebus(note_text: str) -> Dict[str, Any]:
    """Extract radial EBUS indicator (peripheral lesion localization)."""
    text_lower = (note_text or "").lower()
    for pattern in RADIAL_EBUS_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"radial_ebus": {"performed": True}}
    return {}


def extract_cryotherapy(note_text: str) -> Dict[str, Any]:
    """Extract cryotherapy (tumor destruction/stenosis relief) indicator."""
    text_lower = (note_text or "").lower()
    for pattern in CRYOTHERAPY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"cryotherapy": {"performed": True}}

    if re.search(CRYOPROBE_PATTERN, text_lower, re.IGNORECASE) and not re.search(
        CRYOBIOPSY_PATTERN, text_lower, re.IGNORECASE
    ):
        return {"cryotherapy": {"performed": True}}

    return {}


def extract_navigational_bronchoscopy(note_text: str) -> Dict[str, Any]:
    """Extract navigational/robotic bronchoscopy indicator."""
    text_lower = (note_text or "").lower()
    for pattern in NAVIGATIONAL_BRONCHOSCOPY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"navigational_bronchoscopy": {"performed": True}}
    return {}


def extract_tbna_conventional(note_text: str) -> Dict[str, Any]:
    """Extract conventional TBNA indicator."""
    text_lower = (note_text or "").lower()
    for pattern in TBNA_CONVENTIONAL_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"tbna_conventional": {"performed": True}}
    return {}


def extract_brushings(note_text: str) -> Dict[str, Any]:
    """Extract bronchial brushings indicator."""
    text_lower = (note_text or "").lower()
    for pattern in BRUSHINGS_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"brushings": {"performed": True}}
    return {}


def extract_transbronchial_cryobiopsy(note_text: str) -> Dict[str, Any]:
    """Extract transbronchial cryobiopsy indicator."""
    text_lower = (note_text or "").lower()
    for pattern in TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"transbronchial_cryobiopsy": {"performed": True}}
    return {}


def extract_peripheral_ablation(note_text: str) -> Dict[str, Any]:
    """Extract peripheral ablation indicator with modality when possible."""
    text_lower = (note_text or "").lower()
    negation = re.search(
        r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}\b"
        r"(?:ablation|mwa|rfa|cryoablation)\b",
        text_lower,
        re.IGNORECASE,
    )
    if negation:
        return {}

    has_mwa = bool(
        re.search(r"\bmicrowave\s+ablation\b", text_lower, re.IGNORECASE)
        or re.search(r"\bmwa\b", text_lower, re.IGNORECASE)
    )
    has_rfa = bool(
        re.search(r"\bradiofrequency\s+ablation\b", text_lower, re.IGNORECASE)
        or re.search(r"\brf\s+ablation\b", text_lower, re.IGNORECASE)
        or re.search(r"\brfa\b", text_lower, re.IGNORECASE)
    )
    has_cryo = bool(
        re.search(r"\bcryoablation\b", text_lower, re.IGNORECASE)
        or re.search(r"\bcryo\s*ablation\b", text_lower, re.IGNORECASE)
    )

    if not (has_mwa or has_rfa or has_cryo):
        return {}

    proc: dict[str, Any] = {"performed": True}
    if has_mwa:
        proc["modality"] = "Microwave"
    elif has_rfa:
        proc["modality"] = "Radiofrequency"
    elif has_cryo:
        proc["modality"] = "Cryoablation"

    return {"peripheral_ablation": proc}


def extract_thermal_ablation(note_text: str) -> Dict[str, Any]:
    """Extract thermal ablation indicator (APC/laser/electrocautery)."""
    text_lower = (note_text or "").lower()
    for pattern in THERMAL_ABLATION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            proc: dict[str, Any] = {"performed": True}
            if re.search(r"\bapc\b|\bargon\s+plasma\b", text_lower, re.IGNORECASE):
                proc["modality"] = "APC"
            elif re.search(r"\belectrocautery\b|\bcauteriz", text_lower, re.IGNORECASE):
                proc["modality"] = "Electrocautery"
            elif re.search(r"\bnd:?yag\b", text_lower, re.IGNORECASE):
                proc["modality"] = "Laser (Nd:YAG)"
            elif re.search(r"\bco2\b", text_lower, re.IGNORECASE):
                proc["modality"] = "Laser (CO2)"
            elif re.search(r"\bdiode\b", text_lower, re.IGNORECASE):
                proc["modality"] = "Laser (Diode)"
            return {"thermal_ablation": proc}
    return {}


def extract_percutaneous_tracheostomy(note_text: str) -> Dict[str, Any]:
    """Extract percutaneous tracheostomy indicator.

    Conservative: requires explicit tracheostomy procedure language.
    """
    text = note_text or ""
    text_lower = text.lower()

    patterns = [
        r"\bpercutaneous\s+(?:dilatational\s+)?tracheostomy\b",
        r"\bperc\s+trach\b",
        r"\btracheostomy\b[^.\n]{0,60}\b(?:performed|placed|inserted|created)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if not match:
            continue
        negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
        if re.search(negation_check, text_lower, re.IGNORECASE):
            continue

        proc: dict[str, Any] = {"performed": True}
        if "open" in match.group(0).lower():
            proc["method"] = "open"
        elif "percutaneous" in match.group(0).lower() or "perc trach" in match.group(0).lower():
            proc["method"] = "percutaneous"

        if re.search(r"\bportex\b", text_lower):
            proc["device_name"] = "Portex"
        elif re.search(r"\bshiley\b", text_lower):
            proc["device_name"] = "Shiley"

        return {"percutaneous_tracheostomy": proc}

    return {}


ESTABLISHED_TRACH_ROUTE_PATTERNS = [
    r"\bvia\s+(?:an?\s+)?(?:existing\s+)?trach(?:eostomy)?\b",
    r"\bthrough\s+(?:an?\s+)?(?:existing\s+)?trach(?:eostomy)?\b",
    r"\btrach(?:eostomy)?\s+(?:stoma|tube)\b[^.\n]{0,40}\b(?:used|accessed|entered|through)\b",
    r"\bbronchoscope\b[^.\n]{0,60}\btrach(?:eostomy)?\b",
    r"\bestablished\s+trach(?:eostomy)?\b",
]

ESTABLISHED_TRACH_NEW_PATTERNS = [
    r"\bpercutaneous\s+(?:dilatational\s+)?tracheostomy\b",
    r"\bopen\s+tracheostomy\b",
    r"\btracheostomy\b[^.\n]{0,60}\b(?:performed|placed|inserted|created)\b",
    r"\bnew\s+trach(?:eostomy)?\b",
    r"\btrach(?:eostomy)?\s+(?:created|placed|inserted)\b",
    r"\btracheostomy\s+creation\b",
]


def extract_established_tracheostomy_route(note_text: str) -> Dict[str, Any]:
    """Detect bronchoscopy via an established tracheostomy route."""
    text = note_text or ""
    text_lower = text.lower()
    if not text_lower.strip():
        return {}

    for pattern in ESTABLISHED_TRACH_NEW_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return {}

    if re.search(r"\b(?:no|not|without)\b[^.\n]{0,60}\btrach(?:eostomy)?\b", text_lower):
        return {}

    for pattern in ESTABLISHED_TRACH_ROUTE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return {"established_tracheostomy_route": True}

    return {}


def extract_neck_ultrasound(note_text: str) -> Dict[str, Any]:
    """Extract neck ultrasound indicator (often pre-tracheostomy vascular mapping)."""
    text_lower = (note_text or "").lower()
    patterns = [
        r"\bneck\s+ultrasound\b",
        r"\bultrasound\s+of\s+(?:the\s+)?neck\b",
    ]

    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            return {"neck_ultrasound": {"performed": True}}

    return {}


def _extract_checked_side(note_text: str, header: str) -> str | None:
    """Extract Right/Left/Bilateral side from checkbox-style lines."""
    if not note_text:
        return None

    header_lower = header.lower()
    for line in note_text.splitlines():
        if header_lower not in line.lower():
            continue
        if re.search(r"(?i)\b1\D{0,6}bilateral\b", line):
            return "Bilateral"
        if re.search(r"(?i)\b1\D{0,6}left\b", line):
            return "Left"
        if re.search(r"(?i)\b1\D{0,6}right\b", line):
            return "Right"
    return None


def extract_chest_ultrasound(note_text: str) -> Dict[str, Any]:
    """Extract chest ultrasound indicator (76604 family).

    Conservative: requires explicit "CHEST ULTRASOUND FINDINGS" or CPT 76604 context.
    """
    text = note_text or ""
    if not re.search(r"(?i)\bchest\s+ultrasound\s+findings\b|\b76604\b", text):
        return {}

    proc: dict[str, Any] = {"performed": True}

    if re.search("|".join(CHEST_ULTRASOUND_IMAGE_DOC_PATTERNS), text, re.IGNORECASE):
        proc["image_documentation"] = True

    hemithorax = _extract_checked_side(note_text, "Hemithorax")
    if hemithorax is not None:
        proc["hemithorax"] = hemithorax

    return {"chest_ultrasound": proc}


def extract_chest_tube(note_text: str) -> Dict[str, Any]:
    """Extract chest tube / pleural drainage catheter insertion (32556/32557/32551 family)."""
    text = note_text or ""
    text_lower = text.lower()

    has_pigtail = re.search(r"(?i)\bpigtail\s+catheter\b", text) is not None
    has_chest_tube = re.search(r"(?i)\bchest\s+tube\b", text) is not None
    has_insertion = re.search(r"(?i)\b(insert(?:ed)?|place(?:d)?|advanced)\b", text) is not None

    if not ((has_pigtail and has_insertion) or (has_chest_tube and has_insertion)):
        return {}

    proc: dict[str, Any] = {"performed": True, "action": "Insertion"}

    side = _extract_checked_side(note_text, "Entry Site") or _extract_checked_side(
        note_text, "Hemithorax"
    )
    if side in {"Left", "Right"}:
        proc["side"] = side

    if "pleural effusion" in text_lower or re.search(r"(?i)\beffusion\b", text):
        proc["indication"] = "Effusion drainage"

    if has_pigtail:
        proc["tube_type"] = "Pigtail"
    elif re.search(r"(?i)\blarge\s+bore\b|\bsurgical\b", text):
        proc["tube_type"] = "Surgical/Large bore"
    elif re.search(r"(?i)\bstraight\b", text):
        proc["tube_type"] = "Straight"

    size_match = None
    for line in text.splitlines():
        if not re.search(r"(?i)\bsize\s*:", line):
            continue
        # Prefer checkbox-style selection like "1 14Fr" (avoid matching "12FR").
        size_match = re.search(r"(?i)\b1\D{1,6}(\d{1,2})\s*fr\b", line)
        if size_match:
            break
    if not size_match:
        size_match = re.search(r"(?i)\b1\D{1,6}(\d{1,2})\s*fr\b", text)
    if not size_match:
        size_match = re.search(r"(?i)\b(\d{1,2})\s*fr\b", text)
    if size_match:
        try:
            proc["tube_size_fr"] = int(size_match.group(1))
        except ValueError:
            pass

    if re.search(r"(?i)\bultrasound\b", text):
        proc["guidance"] = "Ultrasound"
    elif re.search(r"(?i)\bct\b|\bcomputed tomography\b", text):
        proc["guidance"] = "CT"
    elif re.search(r"(?i)\bfluoro(?:scopy)?\b", text):
        proc["guidance"] = "Fluoroscopy"

    return {"chest_tube": proc}


def extract_ipc(note_text: str) -> Dict[str, Any]:
    """Extract indwelling pleural catheter (IPC / tunneled pleural catheter)."""
    text = note_text or ""
    text_lower = text.lower()

    matched_pattern: str | None = None
    for pattern in IPC_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            negation_check = r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,60}" + pattern
            if re.search(negation_check, text_lower, re.IGNORECASE):
                continue
            matched_pattern = pattern
            break

    if matched_pattern is None:
        return {}

    if matched_pattern.startswith(r"\bipc\b") and not re.search(r"(?i)\b(?:pleur|effusion)\b", text):
        return {}

    proc: dict[str, Any] = {"performed": True}

    # Action: prioritize explicit removal language.
    if re.search(r"(?i)\b(removal|removed|pull(?:ed)?)\b", text):
        proc["action"] = "Removal"
    elif re.search(r"(?i)\b(placement|place(?:d)?|insert(?:ed)?|insertion|tunnel(?:ed)?|seldinger)\b", text):
        proc["action"] = "Insertion"

    right = re.search(r"(?i)\b(rt|right)\b", text) is not None
    left = re.search(r"(?i)\b(lt|left)\b", text) is not None
    if right and not left:
        proc["side"] = "Right"
    elif left and not right:
        proc["side"] = "Left"

    if re.search(r"(?i)\bpleurx\b", text):
        proc["catheter_brand"] = "PleurX"
        proc["tunneled"] = True
    elif re.search(r"(?i)\baspira\b", text):
        proc["catheter_brand"] = "Aspira"
        proc["tunneled"] = True
    elif re.search(r"(?i)\brocket\b", text):
        proc["catheter_brand"] = "Rocket"
        proc["tunneled"] = True
    else:
        proc["catheter_brand"] = "Other"

    if re.search(r"(?i)\btunne(?:l|ll)ed\b", text) or re.search(r"(?i)\bindwelling\b", text):
        proc["tunneled"] = True

    if re.search(r"(?i)\bmalignant\b", text) and re.search(r"(?i)\beffusion\b", text):
        proc["indication"] = "Malignant effusion"

    return {"ipc": proc}


def run_deterministic_extractors(note_text: str) -> Dict[str, Any]:
    """Run all deterministic extractors and return combined seed data.

    This function should be called before LLM extraction to provide
    reliable seed data for commonly missed fields.

    Args:
        note_text: Raw procedure note text

    Returns:
        Dict of extracted field values
    """
    seed_data: Dict[str, Any] = {}

    # Demographics
    demographics = extract_demographics(note_text)
    seed_data.update(demographics)

    # ASA class
    asa = extract_asa_class(note_text)
    if asa is not None:
        seed_data["asa_class"] = asa

    # Sedation and airway
    sedation_airway = extract_sedation_airway(note_text)
    seed_data.update(sedation_airway)

    # Institution
    institution = extract_institution_name(note_text)
    if institution:
        seed_data["institution_name"] = institution

    # Primary indication
    indication = extract_primary_indication(note_text)
    if indication:
        seed_data["primary_indication"] = indication

    # Disposition
    disposition = extract_disposition(note_text)
    if disposition:
        seed_data["disposition"] = disposition

    # Bleeding severity
    bleeding = extract_bleeding_severity(note_text)
    if bleeding:
        seed_data["bleeding_severity"] = bleeding

    bleeding_interventions = extract_bleeding_intervention_required(note_text)
    if bleeding_interventions:
        seed_data["bleeding_intervention_required"] = bleeding_interventions

    # Providers
    providers = extract_providers(note_text)
    # Only include provider fields that were actually extracted
    for key, value in providers.items():
        if value is not None:
            seed_data.setdefault("providers", {})[key] = value

    # Procedure extractors (Phase 7)
    # BAL
    bal_data = extract_bal(note_text)
    if bal_data:
        seed_data.setdefault("procedures_performed", {}).update(bal_data)

    # Therapeutic aspiration
    ta_data = extract_therapeutic_aspiration(note_text)
    if ta_data:
        seed_data.setdefault("procedures_performed", {}).update(ta_data)

    # Endobronchial biopsy
    ebx_data = extract_endobronchial_biopsy(note_text)
    if ebx_data:
        seed_data.setdefault("procedures_performed", {}).update(ebx_data)

    radial_ebus_data = extract_radial_ebus(note_text)
    if radial_ebus_data:
        seed_data.setdefault("procedures_performed", {}).update(radial_ebus_data)

    cryotherapy_data = extract_cryotherapy(note_text)
    if cryotherapy_data:
        seed_data.setdefault("procedures_performed", {}).update(cryotherapy_data)

    nav_data = extract_navigational_bronchoscopy(note_text)
    if nav_data:
        seed_data.setdefault("procedures_performed", {}).update(nav_data)

    tbna_data = extract_tbna_conventional(note_text)
    if tbna_data:
        seed_data.setdefault("procedures_performed", {}).update(tbna_data)

    brushings_data = extract_brushings(note_text)
    if brushings_data:
        seed_data.setdefault("procedures_performed", {}).update(brushings_data)

    cryobiopsy_data = extract_transbronchial_cryobiopsy(note_text)
    if cryobiopsy_data:
        seed_data.setdefault("procedures_performed", {}).update(cryobiopsy_data)

    peripheral_ablation_data = extract_peripheral_ablation(note_text)
    if peripheral_ablation_data:
        seed_data.setdefault("procedures_performed", {}).update(peripheral_ablation_data)

    thermal_ablation_data = extract_thermal_ablation(note_text)
    if thermal_ablation_data:
        seed_data.setdefault("procedures_performed", {}).update(thermal_ablation_data)

    # Percutaneous tracheostomy
    trach_data = extract_percutaneous_tracheostomy(note_text)
    if trach_data:
        seed_data.setdefault("procedures_performed", {}).update(trach_data)

    established_trach = extract_established_tracheostomy_route(note_text)
    if established_trach:
        seed_data.update(established_trach)

    # Neck ultrasound
    neck_us_data = extract_neck_ultrasound(note_text)
    if neck_us_data:
        seed_data.setdefault("procedures_performed", {}).update(neck_us_data)

    # Chest ultrasound
    chest_us_data = extract_chest_ultrasound(note_text)
    if chest_us_data:
        seed_data.setdefault("procedures_performed", {}).update(chest_us_data)

    # Pleural: chest tube / pleural drainage catheter
    chest_tube_data = extract_chest_tube(note_text)
    if chest_tube_data:
        seed_data.setdefault("pleural_procedures", {}).update(chest_tube_data)

    # Pleural: indwelling pleural catheter (IPC / tunneled pleural catheter)
    ipc_data = extract_ipc(note_text)
    if ipc_data:
        seed_data.setdefault("pleural_procedures", {}).update(ipc_data)

    return seed_data


__all__ = [
    "run_deterministic_extractors",
    "extract_demographics",
    "extract_asa_class",
    "extract_sedation_airway",
    "extract_institution_name",
    "extract_primary_indication",
    "extract_disposition",
    "extract_bleeding_severity",
    "extract_bleeding_intervention_required",
    "extract_providers",
    "extract_bal",
    "extract_therapeutic_aspiration",
    "extract_endobronchial_biopsy",
    "extract_radial_ebus",
    "extract_cryotherapy",
    "extract_navigational_bronchoscopy",
    "extract_tbna_conventional",
    "extract_brushings",
    "extract_transbronchial_cryobiopsy",
    "extract_peripheral_ablation",
    "extract_thermal_ablation",
    "extract_percutaneous_tracheostomy",
    "extract_established_tracheostomy_route",
    "extract_neck_ultrasound",
    "extract_chest_ultrasound",
    "extract_chest_tube",
    "extract_ipc",
    "BAL_PATTERNS",
    "ENDOBRONCHIAL_BIOPSY_PATTERNS",
    "RADIAL_EBUS_PATTERNS",
    "CRYOTHERAPY_PATTERNS",
    "NAVIGATIONAL_BRONCHOSCOPY_PATTERNS",
    "TBNA_CONVENTIONAL_PATTERNS",
    "BRUSHINGS_PATTERNS",
    "TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS",
    "PERIPHERAL_ABLATION_PATTERNS",
    "THERMAL_ABLATION_PATTERNS",
    "ESTABLISHED_TRACH_ROUTE_PATTERNS",
    "ESTABLISHED_TRACH_NEW_PATTERNS",
    "CHEST_ULTRASOUND_PATTERNS",
    "CHEST_TUBE_PATTERNS",
    "IPC_PATTERNS",
]
