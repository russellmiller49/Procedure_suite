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
  "sedation_type": "moderate" | "deep" | "general" | "local" | "monitored anesthesia care" | "",
  "airway_type": "native" | "ett" | "lma" | "tracheostomy" | "rigid bronchoscope" | "",
  "pleural_procedure_type": "chest tube" | "tunneled catheter" | "thoracentesis" | "medical thoracoscopy" | "chemical pleurodesis" | "",
  "pleural_guidance": "ultrasound" | "ct" | "blind" | "",
  "final_diagnosis_prelim": "malignancy" | "infectious" | "granulomatous" | "non-diagnostic" | "other" | "",
  "disposition": "discharge home" | "pacu recovery" | "icu admission" | "floor admission" | "",
  "ebus_needle_gauge": "",
  "ebus_rose_result": ""
}

General rules:
- Use only information about the current procedure for the primary patient; ignore appended reports for other patients.
- Prefer clearly labeled headers for MRN/ID and procedure date.
- If no pleural procedure is present, pleural_procedure_type and pleural_guidance should be null/empty. If a pleural procedure is documented but no guidance is mentioned, pleural_guidance may default to "blind". Leave asa_class/sedation_type/airway_type empty when not documented rather than inferring from context alone; ebus_* stay "".
""".strip()

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"
_PROMPT_CACHE: str | None = None
_FIELD_INSTRUCTIONS_CACHE: dict[str, str] | None = None
_FIELD_INSTRUCTION_OVERRIDES: dict[str, str] = {
    "sedation_type": """
Extract sedation/anesthesia level for the procedure. Allowed: moderate, deep, general, local, monitored anesthesia care; return ""/null if not documented. Use explicit labels when present. Treat MAC/monitored anesthesia care without ETT/GA as Deep (project convention). General only when GA/intubation/ETT/rigid context is documented (not merely implied). Moderate when procedural team gives midazolam/fentanyl/conscious sedation without anesthesia team or airway device. Local only when the note clearly states topical/local only and no systemic sedatives. If ambiguous, leave blank/null.""".strip(),
    "pleural_guidance": """
Imaging guidance for pleural procedures only (thoracentesis, chest tube/pigtail, tunneled pleural catheter, medical thoracoscopy/pleuroscopy, pleural drain/biopsy). Allowed: ultrasound, ct, blind; ""/null if no pleural procedure or guidance not documented. Ultrasound only when the pleural procedure is ultrasound-guided (ignore EBUS/radial/bronchial ultrasound). CT only when the pleural procedure is performed under CT/CT-fluoro (not just prior imaging). Blind when pleural procedure done without imaging or visualization only. If no pleural procedure exists in the note, leave this field blank.""".strip(),
    "pleural_procedure_type": """
Type of pleural procedure performed (not bronchoscopic). Allowed: thoracentesis, chest tube, tunneled catheter, medical thoracoscopy, chemical pleurodesis (lower-case); null if no pleural procedure. Priority when multiple: chemical pleurodesis > medical thoracoscopy > (chest tube vs tunneled catheter) > thoracentesis. Chemical pleurodesis when a sclerosing agent is instilled. Medical thoracoscopy/pleuroscopy when explicitly described. Chest tube for any non-tunneled pleural drain/pigtail/intercostal drain. Tunneled catheter for long-term tunneled/IPC/PleurX/Aspira indwelling catheters. If the note only lists bronchoscopic procedures (EBUS/bronchoscopy) or pleural procedure cannot be determined, leave null.""".strip(),
    "disposition": """
Immediate post-procedure disposition/destination. Allowed: discharge home, pacu recovery, floor admission, icu admission (lower-case); "" if not documented. Capture only the first destination after the procedure. Discharge home only when clearly stated (dc home/going home today). PACU recovery for PACU/recovery/Phase I. ICU admission for ICU/MICU/SICU/critical care destinations. Floor admission for non-ICU inpatient/telemetry/step-down/ward. If no clear plan is stated, leave blank.""".strip(),
    "procedure_date": """
Procedure date (YYYY-MM-DD). Convert common formats (e.g., 8/23/2023, 05-07-25, March 5, 2025) into YYYY-MM-DD. Prefer labels: "DATE OF PROCEDURE", "PROCEDURE DATE", "Service Date", or header Date within the procedure note. Ignore follow-up/past dates or non-procedure dates. If multiple and unclear, leave "". "" if truly undocumented.""".strip(),
    "patient_mrn": """
Patient medical record number or clearly labeled patient ID. Prefer explicit MRN/ID labels near the demographics/header (e.g., "MRN: 3847592", "ID: MR4729384"). If multiple IDs exist, pick the clearly labeled patient MRN/ID. Ignore dates, phone-like numbers, accession/specimen/order numbers, device IDs, or other non-patient identifiers. Preserve the ID format; strip labels if included. If no MRN/ID is documented, return "".""".strip(),
    "asa_class": """
ASA physical status only when explicitly documented ("ASA 2", "ASA III", etc.). Do not infer from comorbidities, sedation, or severity scores. If not documented anywhere, leave this field blank/null.""".strip(),
    "airway_type": """
Airway used for the bronchoscopy. Allowed: native, lma, ett, tracheostomy, rigid bronchoscope (lower-case); "" if not documented. Pick the explicit device/route when named. Rigid bronchoscopy anywhere -> rigid bronchoscope. ETT only when intubation/ETT for the case is documented (do not infer from GA alone). LMA placed for the case -> lma. Bronchoscopy via tracheostomy/trach tube -> tracheostomy. If awake/moderate/deep without any airway device documented, favor native; if unclear, leave blank.""".strip(),
    "final_diagnosis_prelim": """
Preliminary final diagnosis category. Allowed: malignancy, granulomatous, infectious, non-diagnostic, benign, other; use null if unclear. Choose Malignancy only when a malignant diagnosis/ROSE is explicitly documented or known cancer staging is described (do not infer from "suspicious" alone). Granulomatous for granulomas/sarcoidosis; Infectious for infections; Non-diagnostic when specimen inadequate/insufficient; Benign for clearly benign/reactive findings; Other for therapeutic/structural procedures without a specific pathology label. If truly cannot determine, leave null.""".strip(),
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
Intercostal space used for pleural access (e.g., '5th'). Accept ICS shorthand (\"5th ICS\" -> \"5th\"). Null if not documented.""".strip(),
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
Field: ebus_stations_detail (per-station EBUS node details)

ebus_stations_detail is an array of objects.
Include one object per lymph node station that is sampled or clearly described during EBUS (e.g. 2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L, etc.).

Each object must have the following structure:

station (string)
The numeric EBUS station name as written in the note: "11L", "4R", "7", etc.
Use the exact station label from the report. Do not invent station labels.

size_mm (number or null)
Short-axis size in millimeters for that station, if reported (e.g. "5.4 mm", "10 mm", "1.1 cm").
Convert centimeters to millimeters if needed (1.1 cm -> 11 mm).
If multiple sizes are given for the same station, use the short-axis size.
If size is not reported for that station, set size_mm to null.

shape (string or null)
Normalized values: "oval", "round", "irregular".
Map free text as follows:
"oval", "elliptical", "elongated" -> "oval"
"round", "spherical" -> "round"
"irregular", "lobulated", "asymmetric" -> "irregular"
If the shape is not described, set shape to null.

margin (string or null)
Normalized values: "distinct", "indistinct", "irregular".
Map free text as follows:
"sharp", "well-defined", "well-circumscribed", "clear margin" -> "distinct"
"ill-defined", "blurred", "poorly defined" -> "indistinct"
"spiculated", "irregular margin" -> "irregular"
If the margin is not described, set margin to null.

echogenicity (string or null)
Normalized values: "homogeneous", "heterogeneous".
Map free text as follows:
"homogeneous", "uniform echo pattern" -> "homogeneous"
"heterogeneous", "mixed echotexture", "non-uniform" -> "heterogeneous"
If echogenicity is not described, set echogenicity to null.

chs_present (boolean or null)
Central Hilar Structure (CHS) status for that node:
If the note explicitly states a central hilar structure is present / preserved -> true.
If the note explicitly states no central hilar structure / CHS absent -> false.
If CHS is not mentioned for that station -> null.

appearance_category (string or null)
Overall qualitative impression of node appearance, based only on EBUS morphological features, not on ROSE or final pathology.
Use the following mapping of features to categories:
Benign-appearing -> "benign"
Short-axis size < 10 mm and most described features match: shape: oval; margin: indistinct; echogenicity: homogeneous; CHS: present
Malignant-appearing -> "malignant"
Short-axis size ≥ 10 mm and most described features match: shape: round; margin: distinct; echogenicity: heterogeneous; CHS: absent
Indeterminate / mixed features -> "indeterminate"
Mixed benign and malignant features, or morphology is described but doesn't clearly fit benign or malignant patterns.
Node is described but only one weak feature is given (e.g. just "oval" and nothing else).
If morphology is not described at all for that station, set appearance_category to null.
If the report uses phrases like:
"benign-appearing node" -> "appearance_category": "benign"
"malignant-appearing node", "highly suspicious" -> "appearance_category": "malignant"
"indeterminate appearance", "non-specific appearance" -> "appearance_category": "indeterminate"
Do not infer appearance_category from ROSE or pathology alone.

rose_result (string or null)
Keep current behavior (e.g. "Benign", "Nondiagnostic", "Suspicious", "Malignant", "Not done").
If ROSE is not performed or not described, set to null or "Not done" depending on your existing conventions.

Parsing rules and edge cases
Multiple stations
Include one object per station (e.g. one for "11L", one for "4R").
If a station is mentioned but not sampled and has no morphological description, you may omit it from ebus_stations_detail.
Multiple nodes described at the same station
If several nodes at the same station are described, choose the largest or the one that is actually sampled.
If the note clearly distinguishes them (e.g. "two 4R nodes: one 8 mm oval and one 14 mm round heterogeneous"), prefer the sampled node; if that's unclear, prefer the larger node for registry purposes.

Size parsing
Accept variations like:
"5 mm", "5.0 mm", "0.5 cm", "short axis 5.4 mm", "measuring 1.2 x 0.8 cm".
When two dimensions are provided (e.g. "1.2 x 0.8 cm"), use the shorter dimension as the short-axis in mm (0.8 cm -> 8 mm).
Do not guess features
Only populate shape, margin, echogenicity, chs_present, and appearance_category when the text supports them.
If a feature is not mentioned, set that field to null.
Do not conflate ROSE and morphology
appearance_category is EBUS morphology-based only (size, shape, margin, echogenicity, CHS).
rose_result reflects cytology from ROSE.
It is valid for a node to be appearance_category: "benign" with rose_result: "Malignant" or vice versa.

Example minimal output when only size and ROSE are described:
{"station": "11L", "size_mm": 5.4, "shape": null, "margin": null, "echogenicity": null, "chs_present": null, "appearance_category": null, "rose_result": "Nondiagnostic"}
{"station": "4R", "size_mm": 5.5, "shape": null, "margin": null, "echogenicity": null, "chs_present": null, "appearance_category": null, "rose_result": "Benign"}""".strip(),
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
