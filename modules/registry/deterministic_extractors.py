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

    if "minimal bleeding" in note_lower or "minor bleeding" in note_lower:
        return "None"

    # Check for EBL (estimated blood loss)
    ebl_pattern = r"(?:ebl|estimated blood loss|blood loss)[\s:]+(\d+)\s*(?:ml|cc)?"
    match = re.search(ebl_pattern, note_lower)
    if match:
        ebl = int(match.group(1))
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
        r"(?:Attending|Attending Physician|Primary Operator)[\s:]+(?:\*{1,2}\s*)?(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
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

    # Providers
    providers = extract_providers(note_text)
    # Only include provider fields that were actually extracted
    for key, value in providers.items():
        if value is not None:
            seed_data.setdefault("providers", {})[key] = value

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
    "extract_providers",
]
