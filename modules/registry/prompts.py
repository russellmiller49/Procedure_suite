"""Prompts for LLM-based registry extraction, dynamically built from IP_Registry.json."""

from __future__ import annotations

import json
from pathlib import Path

PROMPT_HEADER = """
You are extracting a registry JSON from an interventional pulmonology procedure note.

Return exactly one JSON object (no markdown) with keys:
{
  "patient_mrn": string or "",
  "procedure_date": "YYYY-MM-DD" or "",
  "asa_class": "1" | "2" | "3" | "4" | "5" | "",
  "sedation_type": "moderate" | "deep" | "general" | "",
  "airway_type": "native" | "ett" | "lma" | "tracheostomy" | "rigid bronchoscope" | "",
  "pleural_procedure_type": "chest tube" | "tunneled catheter" | "thoracentesis" | "medical thoracoscopy" | "",
  "pleural_guidance": "ultrasound" | "ct" | "blind" | "",
  "final_diagnosis_prelim": "malignancy" | "infectious" | "granulomatous" | "non-diagnostic" | "other" | "",
  "disposition": "discharge home" | "pacu recovery" | "icu admission" | "floor admission" | "",
  "ebus_needle_gauge": "",
  "ebus_rose_result": ""
}

General rules:
- Use only information about the current procedure for the primary patient; ignore appended reports for other patients.
- Prefer clearly labeled headers for MRN/ID and procedure date.
- Defaults if undocumented: asa_class → "3"; sedation_type → "moderate"; airway_type → if sedation is general and no device is documented use "ett", if sedation is moderate/deep use "native"; if pleural procedure is present but no guidance documented use "blind"; ebus_* stay "".
""".strip()

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"
_PROMPT_CACHE: str | None = None
_FIELD_INSTRUCTIONS_CACHE: dict[str, str] | None = None
_FIELD_INSTRUCTION_OVERRIDES: dict[str, str] = {
    "sedation_type": """
Extract sedation/anesthesia level for the procedure. Allowed: moderate, deep, general (use lower-case in output); default to moderate if undocumented. General if GA/intubation/neuromuscular blockade; deep for MAC/deep sedation/propofol without paralytic; moderate for midazolam+fentanyl/topical/local-only cases. If both moderate and later GA are described, final state wins (general).""".strip(),
    "pleural_guidance": """
Imaging guidance for pleural procedures only (thoracentesis, chest tube/pigtail, tunneled pleural catheter, medical thoracoscopy, pleural drain/biopsy). Allowed: ultrasound, ct, blind; default to blind if a pleural procedure is present but no modality documented. Ultrasound only when the pleural procedure is ultrasound-guided; ignore EBUS/radial EBUS/bronchial ultrasound. CT only when pleural procedure performed under CT/CT-fluoro. Do not set from non-pleural procedures or prior diagnostic imaging alone.""".strip(),
    "pleural_procedure_type": """
Type of pleural procedure performed (not bronchoscopic). Allowed: chest tube, tunneled catheter, thoracentesis, medical thoracoscopy (lower-case). Priority: chemical pleurodesis > medical thoracoscopy > (chest tube vs tunneled catheter) > thoracentesis. Chest tube for any pleural drain/pigtail/intercostal drain unless clearly tunneled/indwelling (then tunneled catheter). Thoracentesis only when fluid is drained and no tube left. Medical thoracoscopy/pleuroscopy when explicitly described. Chemical pleurodesis when agent instilled (override to chemical pleurodesis).""".strip(),
    "disposition": """
Immediate post-procedure disposition. Allowed: discharge home, pacu recovery, floor admission, icu admission (lower-case); "" if not documented. Choose the immediate destination after the procedure (not later transfers). PACU recovery for recovery/PACU/phase I. ICU admission for ICU/MICU/SICU/critical care. Floor admission for non-ICU inpatient/telemetry/step-down. Discharge home when explicitly stated going home same day; otherwise leave blank.""".strip(),
    "procedure_date": """
Procedure date (YYYY-MM-DD). Convert common formats (e.g., 8/23/2023, 05-07-25, March 5, 2025) into YYYY-MM-DD. Prefer labels: "DATE OF PROCEDURE", "PROCEDURE DATE", "Service Date", or header Date within the procedure note. Ignore follow-up/past dates or non-procedure dates. If multiple and unclear, leave "". "" if truly undocumented.""".strip(),
    "patient_mrn": """
Patient medical record number or clearly labeled patient ID. Prefer explicit MRN/ID labels (e.g., "MRN: 3847592", "ID: MR4729384"). Do not return dates, accession numbers, or phone-like numbers. Preserve the ID format; strip labels if included. If no MRN/ID documented, return "".""".strip(),
    "asa_class": """
ASA physical status. If explicitly documented ("ASA 2", "ASA III", etc.), extract the numeric value as a string 1-5. If not documented anywhere, default to "3" (do not leave blank).""".strip(),
    "airway_type": """
Airway used for the bronchoscopy. Allowed: native, lma, ett, tracheostomy, rigid bronchoscope (lower-case); "" if not documented. Rigid bronchoscopy → rigid bronchoscope. Intubated/ETT for the procedure → ett. LMA placed for the case → lma. Bronchoscopy via tracheostomy/trach tube → tracheostomy. If sedation_type is general and no device is documented, assume ett; if sedation_type is moderate/deep and no device is documented, assume native.""".strip(),
    "stent_type": """
Airway stent type placed. Allowed: Silicone-Dumon, Silicone-Y-Stent, Silicone Y-Stent, Hybrid, Metallic-Covered, Metallic-Uncovered, Other; "" if none. Map Dumon/Y-stent/metallic/covered/uncovered wording to the closest allowed value; use Other only if unclear.""".strip(),
    "stent_location": """
Location of airway stent. Allowed: Trachea, Mainstem, Lobar; "" if no stent. Map mentions of trachea to Trachea; mainstem/right/left main bronchus to Mainstem; lobar or named lobes (RUL/RML/RLL/LUL/LLL) to Lobar.""".strip(),
    "stent_deployment_method": """
Stent deployment method. Allowed: Rigid, Flexible over Wire; "" if not documented. Use Rigid when placed via rigid bronchoscope; Flexible over Wire when placed through flexible scope over a wire.""".strip(),
    "ebus_rose_result": """
Leave ebus_rose_result as "" for now, even if ROSE is described.""".strip(),
    "ebus_needle_gauge": """
Leave ebus_needle_gauge as "" for now, even if the needle size is described.""".strip(),
    "ebus_needle_type": """
Leave ebus_needle_type as "" for now.""".strip(),
    "ebus_elastography_used": """
True if the note explicitly states elastography was performed during EBUS; false if explicitly stated not done; null if not mentioned.""".strip(),
    "ebus_elastography_pattern": """
Elastography pattern or color map when documented (e.g., blue-green, predominantly blue). Strip trailing punctuation; null if not mentioned.""".strip(),
    "pleural_side": """
Pleural laterality for thoracentesis/chest tube/tunneled catheter. Allowed: Right, Left (capitalize first letter); accept R/L/right/left synonyms. Null if not documented.""".strip(),
    "pleural_intercostal_space": """
Intercostal space used for pleural access (e.g., '5th'). Accept ICS shorthand (\"5th ICS\" → \"5th\"). Null if not documented.""".strip(),
    "linear_ebus_stations": """
List of stations sampled with linear EBUS-TBNA (e.g., [\"4R\", \"7\", \"11L\"]). Use IASLC station names; null/[] if no stations documented.""".strip(),
    "nav_platform": """
Navigation platform (Ion/Monarch/EMN) only when robotic or navigation is explicitly documented by name. Do not set for standard mediastinal EBUS staging without navigation. Leave null unless the note clearly names Ion/robotic/Monarch/navigation system.""".strip(),
    "nav_registration_method": """
Only populate if robotic/navigation registration is clearly described. Leave null for non-navigation EBUS cases.""".strip(),
    "nav_registration_error_mm": """
Registration error in mm; only set when robotic/navigation registration is described. Null for non-navigation EBUS cases.""".strip(),
    "nav_imaging_verification": """
Imaging used to confirm tool-in-lesion (e.g., Cone Beam CT) only when navigation/robotic context exists. Null for routine EBUS without navigation.""".strip(),
    "nav_tool_in_lesion": """
True only when navigation/robotic tool-in-lesion confirmation is explicitly documented. Null otherwise; do not infer for standard EBUS.""".strip(),
    "nav_sampling_tools": """
Sampling tools used in navigation/robotic cases (forceps, needle, brush, cryoprobe). Leave null/[] for linear EBUS staging without navigation even if a generic needle is mentioned.""".strip(),
    "ebus_stations_detail": """
List of station-level details when available. Example: [{\"station\":\"4R\",\"size_mm\":13,\"passes\":3,\"rose_result\":\"Malignant\"},{\"station\":\"7\",\"size_mm\":15,\"passes\":3,\"rose_result\":\"Malignant\"},{\"station\":\"11L\",\"size_mm\":9,\"passes\":2,\"rose_result\":\"Benign\"}]. Use null if not documented.""".strip(),
    "bronch_indication": """
Brief indication for bronchoscopy (e.g., ILD workup). Use null if not documented.""".strip(),
    "bronch_location_lobe": """
Lobe targeted for transbronchial biopsies (e.g., RLL).""".strip(),
    "bronch_location_segment": """
Segment targeted for transbronchial biopsies (e.g., lateral basal).""".strip(),
    "bronch_guidance": """
Guidance modality for transbronchial biopsies (e.g., Fluoroscopy).""".strip(),
    "bronch_num_tbbx": """
Number of transbronchial biopsies obtained. Leave null if not documented.""".strip(),
    "bronch_tbbx_tool": """
Tool used for TBBx (e.g., Forceps).""".strip(),
    "bronch_specimen_tests": """
Specimen destinations/tests for TBBx (e.g., Histology, Microbiology).""".strip(),
    "bronch_immediate_complications": """
Immediate complications for TBBx (e.g., none, bleeding, pneumothorax).""".strip(),
}


def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def _load_field_instructions() -> dict[str, str]:
    """Build per-field instruction text from the schema description and enums."""

    global _FIELD_INSTRUCTIONS_CACHE
    if _FIELD_INSTRUCTIONS_CACHE is not None:
        return _FIELD_INSTRUCTIONS_CACHE

    schema = _load_schema()
    instructions: dict[str, str] = {}
    for name, prop in schema.get("properties", {}).items():
        desc = prop.get("description", "").strip()
        enum = prop.get("enum")
        enum_text = f" Allowed values: {', '.join(enum)}." if enum else ""
        text = f"{desc}{enum_text} Use null if not documented."
        instructions[name] = text.strip()

    # Apply curated overrides for fields with frequent errors
    instructions.update(_FIELD_INSTRUCTION_OVERRIDES)

    _FIELD_INSTRUCTIONS_CACHE = instructions
    return instructions


FIELD_INSTRUCTIONS: dict[str, str] = _load_field_instructions()


def _load_registry_prompt() -> str:
    """Load schema from IP_Registry.json and build a concise field guide for the LLM."""

    global _PROMPT_CACHE
    if _PROMPT_CACHE is not None:
        return _PROMPT_CACHE

    instructions = _load_field_instructions()
    lines = ["Return JSON with the following fields (use null if missing):"]
    for name, text in instructions.items():
        lines.append(f'- "{name}": {text}')

    _PROMPT_CACHE = f"{PROMPT_HEADER}\n\n" + "\n".join(lines)
    return _PROMPT_CACHE


def build_registry_prompt(note_text: str) -> str:
    prompt_text = _load_registry_prompt()
    return f"{prompt_text}\n\nProcedure Note:\n{note_text}\nJSON:"


__all__ = ["build_registry_prompt", "FIELD_INSTRUCTIONS"]
