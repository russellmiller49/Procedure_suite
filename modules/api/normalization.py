"""Normalization layer for registry payloads.

This module provides functions to normalize noisy incoming registry payloads
so they conform to the strict Pydantic schemas in proc_registry / proc_schemas.
This normalization does NOT loosen schema rules; it only reshapes inputs.
"""

from __future__ import annotations

import re
from typing import Any, Mapping


def _strip_unit_suffix(value: Any, suffix: str) -> Any:
    """Strip a unit suffix from a string value and convert to float.

    Args:
        value: The value to process (may be string, number, or other)
        suffix: The unit suffix to strip (e.g., "mm", "cm")

    Returns:
        A float if conversion succeeds, otherwise the original value
    """
    if isinstance(value, str):
        # Case-insensitive suffix matching
        pattern = re.compile(re.escape(suffix) + r"\s*$", re.IGNORECASE)
        if pattern.search(value):
            try:
                cleaned = pattern.sub("", value).strip()
                return float(cleaned)
            except ValueError:
                return value
    return value


def _normalize_numeric_with_unit(value: Any, unit_patterns: list[str]) -> Any:
    """Normalize a value that might have various unit suffixes.

    Args:
        value: The value to normalize
        unit_patterns: List of unit patterns to try stripping

    Returns:
        Normalized numeric value or original value
    """
    if value is None:
        return None
    for pattern in unit_patterns:
        result = _strip_unit_suffix(value, pattern)
        if result != value:
            return result
    return value


# Role mapping: common variations -> canonical enum values
# From IP_Registry.json: ["RN", "RT", "Tech", "Resident", "PA", "NP", "Medical Student", null]
ASSISTANT_ROLE_MAP: dict[str, str] = {
    # Fellow variations -> Resident (fellows are considered residents in training)
    "fellow": "Resident",
    "pulm fellow": "Resident",
    "pulmonary fellow": "Resident",
    "ip fellow": "Resident",
    "interventional pulmonology fellow": "Resident",
    "pgy4": "Resident",
    "pgy5": "Resident",
    "pgy6": "Resident",
    "pgy7": "Resident",
    "pgy8": "Resident",
    # Resident variations
    "resident": "Resident",
    "intern": "Resident",
    "pgy1": "Resident",
    "pgy2": "Resident",
    "pgy3": "Resident",
    # RN variations
    "rn": "RN",
    "nurse": "RN",
    "registered nurse": "RN",
    # RT variations
    "rt": "RT",
    "respiratory therapist": "RT",
    "resp therapist": "RT",
    # Tech variations
    "tech": "Tech",
    "technician": "Tech",
    "technologist": "Tech",
    "bronch tech": "Tech",
    # PA variations
    "pa": "PA",
    "pa-c": "PA",
    "physician assistant": "PA",
    # NP variations
    "np": "NP",
    "nurse practitioner": "NP",
    "aprn": "NP",
    # Medical student variations
    "medical student": "Medical Student",
    "med student": "Medical Student",
    "ms3": "Medical Student",
    "ms4": "Medical Student",
    "student": "Medical Student",
}

# Forceps type mapping: LLM outputs -> canonical enum values
# From IP_Registry.json: ["Standard", "Cryoprobe", null]
FORCEPS_TYPE_MAP: dict[str, str] = {
    # Standard variations
    "standard": "Standard",
    "standard forceps": "Standard",
    "forceps": "Standard",
    "biopsy forceps": "Standard",
    "conventional": "Standard",
    "regular": "Standard",
    # Cryoprobe variations
    "cryoprobe": "Cryoprobe",
    "cryo": "Cryoprobe",
    "cryobiopsy": "Cryoprobe",
    "cryo probe": "Cryoprobe",
    # Mixed values - if cryoprobe is mentioned, use Cryoprobe
    "needle, cryoprobe": "Cryoprobe",
    "cryoprobe, needle": "Cryoprobe",
    "forceps, cryoprobe": "Cryoprobe",
    "standard, cryoprobe": "Cryoprobe",
    # Needle alone -> Standard (TBNA uses needles, not forceps for TBBx)
    "needle": "Standard",
}

# Probe position mapping: descriptive text -> canonical enum values
# From IP_Registry.json: ["Concentric", "Eccentric", "Adjacent", "Not visualized", null]
PROBE_POSITION_MAP: dict[str, str] = {
    # Not visualized variations
    "not visualized": "Not visualized",
    "aerated lung on radial ebus": "Not visualized",
    "aerated lung": "Not visualized",
    "no lesion seen": "Not visualized",
    "not seen": "Not visualized",
    "no target identified": "Not visualized",
    "negative": "Not visualized",
    # Concentric variations
    "concentric": "Concentric",
    "central": "Concentric",
    "within lesion": "Concentric",
    "lesion visualized concentrically": "Concentric",
    # Eccentric variations
    "eccentric": "Eccentric",
    "off-center": "Eccentric",
    "peripheral": "Eccentric",
    "lesion visualized eccentrically": "Eccentric",
    # Adjacent variations
    "adjacent": "Adjacent",
    "beside lesion": "Adjacent",
    "near lesion": "Adjacent",
}

# Stent type mapping: LLM outputs -> canonical enum values
# From IP_Registry.json: ["Silicone - Dumon", "Silicone - Hood", "Silicone - Novatech",
#                         "SEMS - Uncovered", "SEMS - Covered", "SEMS - Partially covered",
#                         "Hybrid", "Y-Stent", "Other", null]
STENT_TYPE_MAP: dict[str, str] = {
    # Y-Stent variations (LLM often combines silicone + y-stent)
    "y-stent": "Y-Stent",
    "y stent": "Y-Stent",
    "ystent": "Y-Stent",
    "silicone-y-stent": "Y-Stent",
    "silicone y-stent": "Y-Stent",
    "silicone y stent": "Y-Stent",
    "dumon y-stent": "Y-Stent",
    "dumon y stent": "Y-Stent",
    # Silicone - Dumon variations
    "silicone - dumon": "Silicone - Dumon",
    "silicone-dumon": "Silicone - Dumon",
    "silicone dumon": "Silicone - Dumon",
    "dumon": "Silicone - Dumon",
    "dumon stent": "Silicone - Dumon",
    # Silicone - Hood variations
    "silicone - hood": "Silicone - Hood",
    "silicone-hood": "Silicone - Hood",
    "silicone hood": "Silicone - Hood",
    "hood": "Silicone - Hood",
    "hood stent": "Silicone - Hood",
    # Silicone - Novatech variations
    "silicone - novatech": "Silicone - Novatech",
    "silicone-novatech": "Silicone - Novatech",
    "silicone novatech": "Silicone - Novatech",
    "novatech": "Silicone - Novatech",
    "novatech stent": "Silicone - Novatech",
    # Generic silicone -> Dumon (most common)
    "silicone": "Silicone - Dumon",
    "silicone stent": "Silicone - Dumon",
    # SEMS variations
    "sems - uncovered": "SEMS - Uncovered",
    "sems-uncovered": "SEMS - Uncovered",
    "sems uncovered": "SEMS - Uncovered",
    "uncovered sems": "SEMS - Uncovered",
    "uncovered metal stent": "SEMS - Uncovered",
    "sems - covered": "SEMS - Covered",
    "sems-covered": "SEMS - Covered",
    "sems covered": "SEMS - Covered",
    "covered sems": "SEMS - Covered",
    "covered metal stent": "SEMS - Covered",
    "sems - partially covered": "SEMS - Partially covered",
    "sems-partially covered": "SEMS - Partially covered",
    "sems partially covered": "SEMS - Partially covered",
    "partially covered sems": "SEMS - Partially covered",
    "partially covered metal stent": "SEMS - Partially covered",
    # Generic SEMS -> Uncovered (most common)
    "sems": "SEMS - Uncovered",
    "metal stent": "SEMS - Uncovered",
    # Hybrid
    "hybrid": "Hybrid",
    "hybrid stent": "Hybrid",
    # Other
    "other": "Other",
}


def normalize_registry_payload(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize noisy incoming registry payloads.

    This function normalizes data to conform to the strict Pydantic schemas
    in proc_registry / proc_schemas. It does NOT loosen schema rules; it only
    reshapes inputs to match expected formats.

    Args:
        raw: The raw incoming payload (dict-like)

    Returns:
        A normalized dict that should validate against registry schemas
    """
    # Make a shallow copy to avoid mutating the original
    payload: dict[str, Any] = {k: v for k, v in raw.items()}

    # Normalize providers.assistant_role
    providers = payload.get("providers")
    if isinstance(providers, dict):
        role = providers.get("assistant_role")
        if isinstance(role, str):
            normalized_role = role.strip().lower()
            providers["assistant_role"] = ASSISTANT_ROLE_MAP.get(normalized_role, role)

    # Normalize equipment.bronchoscope_outer_diameter_mm: "12 mm" -> 12.0
    equipment = payload.get("equipment")
    if isinstance(equipment, dict):
        diameter = equipment.get("bronchoscope_outer_diameter_mm")
        if diameter is not None:
            equipment["bronchoscope_outer_diameter_mm"] = _normalize_numeric_with_unit(
                diameter, ["mm", "millimeters", "millimeter"]
            )

        # Also normalize fluoroscopy_time_seconds and fluoroscopy_dose_mgy
        fluoro_time = equipment.get("fluoroscopy_time_seconds")
        if fluoro_time is not None:
            equipment["fluoroscopy_time_seconds"] = _normalize_numeric_with_unit(
                fluoro_time, ["s", "sec", "seconds", "second"]
            )

        fluoro_dose = equipment.get("fluoroscopy_dose_mgy")
        if fluoro_dose is not None:
            equipment["fluoroscopy_dose_mgy"] = _normalize_numeric_with_unit(
                fluoro_dose, ["mgy", "mGy"]
            )

    # Normalize procedures_performed fields
    procedures = payload.get("procedures_performed")
    if isinstance(procedures, dict):
        # Normalize radial_ebus.probe_position
        radial_ebus = procedures.get("radial_ebus")
        if isinstance(radial_ebus, dict):
            probe_position = radial_ebus.get("probe_position")
            if isinstance(probe_position, str):
                text = probe_position.strip().lower()
                radial_ebus["probe_position"] = PROBE_POSITION_MAP.get(text, probe_position)

        # Normalize navigational_bronchoscopy fields
        nav_bronch = procedures.get("navigational_bronchoscopy")
        if isinstance(nav_bronch, dict):
            divergence = nav_bronch.get("divergence_mm")
            if divergence is not None:
                nav_bronch["divergence_mm"] = _normalize_numeric_with_unit(
                    divergence, ["mm", "millimeters", "millimeter"]
                )

            # Normalize sampling_tools_used list
            # Enum: ["Needle", "Forceps", "Brush", "Cryoprobe", "NeedleInNeedle"]
            tools = nav_bronch.get("sampling_tools_used")
            if isinstance(tools, list):
                tool_map = {
                    "needle": "Needle",
                    "tbna needle": "Needle",
                    "21g needle": "Needle",
                    "22g needle": "Needle",
                    "ion needle": "Needle",
                    "forceps": "Forceps",
                    "biopsy forceps": "Forceps",
                    "standard forceps": "Forceps",
                    "brush": "Brush",
                    "bronchial brush": "Brush",
                    "cryoprobe": "Cryoprobe",
                    "cryo": "Cryoprobe",
                    "cryobiopsy": "Cryoprobe",
                    "needleinneedle": "NeedleInNeedle",
                    "needle in needle": "NeedleInNeedle",
                }
                valid_tools = ("Needle", "Forceps", "Brush", "Cryoprobe", "NeedleInNeedle")
                normalized_tools = []
                for tool in tools:
                    if isinstance(tool, str):
                        normalized = tool_map.get(tool.strip().lower(), tool)
                        # Only add if it's a valid enum value
                        if normalized in valid_tools and normalized not in normalized_tools:
                            normalized_tools.append(normalized)
                nav_bronch["sampling_tools_used"] = normalized_tools

        # Normalize transbronchial_biopsy.forceps_type
        tbbx = procedures.get("transbronchial_biopsy")
        if isinstance(tbbx, dict):
            forceps_type = tbbx.get("forceps_type")
            if isinstance(forceps_type, str):
                text = forceps_type.strip().lower()
                tbbx["forceps_type"] = FORCEPS_TYPE_MAP.get(text, forceps_type)
                # If still not valid after mapping, check if cryoprobe is mentioned
                if tbbx["forceps_type"] not in ("Standard", "Cryoprobe", None):
                    if "cryo" in text:
                        tbbx["forceps_type"] = "Cryoprobe"
                    else:
                        # Default to Standard for unrecognized values
                        tbbx["forceps_type"] = "Standard"

        # Normalize transbronchial_cryobiopsy.forceps_type (same enum)
        cryo_bx = procedures.get("transbronchial_cryobiopsy")
        if isinstance(cryo_bx, dict):
            forceps_type = cryo_bx.get("forceps_type")
            if isinstance(forceps_type, str):
                text = forceps_type.strip().lower()
                cryo_bx["forceps_type"] = FORCEPS_TYPE_MAP.get(text, forceps_type)
                if cryo_bx["forceps_type"] not in ("Standard", "Cryoprobe", None):
                    if "cryo" in text:
                        cryo_bx["forceps_type"] = "Cryoprobe"
                    else:
                        cryo_bx["forceps_type"] = "Cryoprobe"  # Default for cryobiopsy

        # Normalize airway_stent.stent_type
        airway_stent = procedures.get("airway_stent")
        if isinstance(airway_stent, dict):
            stent_type = airway_stent.get("stent_type")
            if isinstance(stent_type, str):
                text = stent_type.strip().lower()
                airway_stent["stent_type"] = STENT_TYPE_MAP.get(text, stent_type)
                # If still not valid, try to infer from keywords
                valid_stent_types = (
                    "Silicone - Dumon", "Silicone - Hood", "Silicone - Novatech",
                    "SEMS - Uncovered", "SEMS - Covered", "SEMS - Partially covered",
                    "Hybrid", "Y-Stent", "Other"
                )
                if airway_stent["stent_type"] not in valid_stent_types:
                    # Check for Y-stent pattern (most specific first)
                    if "y-stent" in text or "y stent" in text or "ystent" in text:
                        airway_stent["stent_type"] = "Y-Stent"
                    elif "sems" in text or "metal" in text:
                        if "covered" in text and "uncovered" not in text:
                            if "partial" in text:
                                airway_stent["stent_type"] = "SEMS - Partially covered"
                            else:
                                airway_stent["stent_type"] = "SEMS - Covered"
                        else:
                            airway_stent["stent_type"] = "SEMS - Uncovered"
                    elif "silicone" in text:
                        if "dumon" in text:
                            airway_stent["stent_type"] = "Silicone - Dumon"
                        elif "hood" in text:
                            airway_stent["stent_type"] = "Silicone - Hood"
                        elif "novatech" in text:
                            airway_stent["stent_type"] = "Silicone - Novatech"
                        else:
                            airway_stent["stent_type"] = "Silicone - Dumon"  # Default silicone
                    elif "hybrid" in text:
                        airway_stent["stent_type"] = "Hybrid"
                    else:
                        airway_stent["stent_type"] = "Other"

    # Normalize clinical_context.lesion_size_mm
    clinical_context = payload.get("clinical_context")
    if isinstance(clinical_context, dict):
        lesion_size = clinical_context.get("lesion_size_mm")
        if lesion_size is not None:
            clinical_context["lesion_size_mm"] = _normalize_numeric_with_unit(
                lesion_size, ["mm", "millimeters", "millimeter", "cm"]
            )
            # Handle cm -> mm conversion
            if isinstance(lesion_size, str) and "cm" in lesion_size.lower():
                try:
                    cm_val = float(re.sub(r"[^\d.]", "", lesion_size))
                    clinical_context["lesion_size_mm"] = cm_val * 10
                except ValueError:
                    pass

    # Normalize patient_demographics numeric fields
    demographics = payload.get("patient_demographics")
    if isinstance(demographics, dict):
        height = demographics.get("height_cm")
        if height is not None:
            demographics["height_cm"] = _normalize_numeric_with_unit(
                height, ["cm", "centimeters", "centimeter"]
            )

        weight = demographics.get("weight_kg")
        if weight is not None:
            demographics["weight_kg"] = _normalize_numeric_with_unit(
                weight, ["kg", "kilograms", "kilogram", "kgs"]
            )

    # Normalize pleural_procedures.thoracentesis.volume_removed_ml
    pleural = payload.get("pleural_procedures")
    if isinstance(pleural, dict):
        thoracentesis = pleural.get("thoracentesis")
        if isinstance(thoracentesis, dict):
            volume = thoracentesis.get("volume_removed_ml")
            if volume is not None:
                thoracentesis["volume_removed_ml"] = _normalize_numeric_with_unit(
                    volume, ["ml", "mL", "cc", "milliliters"]
                )

    # Normalize pathology_results: if it's a string, convert to proper dict structure
    pathology = payload.get("pathology_results")
    if isinstance(pathology, str):
        # LLM returned a string like "ROSE malignant" - convert to proper structure
        pathology_text = pathology.strip()
        payload["pathology_results"] = {
            "final_diagnosis": pathology_text if pathology_text else None,
            "final_staging": None,
            "histology": None,
            "molecular_markers": None,
            "adequacy": None,
            "rose_result": pathology_text if "rose" in pathology_text.lower() else None,
        }

    return payload


__all__ = ["normalize_registry_payload", "FORCEPS_TYPE_MAP"]
