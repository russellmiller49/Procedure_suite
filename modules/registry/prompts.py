"""Prompts for LLM-based registry extraction, dynamically built from IP_Registry.json."""

from __future__ import annotations

import json
from pathlib import Path

PROMPT_HEADER = """
You are an expert Interventional Pulmonology Registry Abstractor.
Extract clinical data into a strict JSON object. Never guess; use null if not documented.
Output exactly one valid JSON object (no markdown).
Navigation imaging verification is only for bronchial navigation imaging (e.g., EMN/robotic/fluoroscopy); if no navigation imaging was performed, use \"None\".
Pleural imaging guidance (Ultrasound/CT/Blind) must be placed in pleural_guidance, not nav_imaging_verification.
""".strip()

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"
_PROMPT_CACHE: str | None = None
_FIELD_INSTRUCTIONS_CACHE: dict[str, str] | None = None
_FIELD_INSTRUCTION_OVERRIDES: dict[str, str] = {
    "sedation_type": """
Extract sedation/anesthesia level for the procedure. Allowed: Moderate, Deep, General, Local, Monitored Anesthesia Care; null if not documented. Prefer explicit labels (e.g., "moderate sedation", "general anesthesia", "local anesthesia", "MAC/monitored anesthesia care"). If intubated/ventilated or "general anesthesia/GA" → General. If anesthesia-managed MAC without ETT and no explicit general → Deep (project convention). If explicit deep sedation → Deep. Moderate/conscious sedation when typical midazolam/fentanyl given by procedural team without anesthesia provider. Local only when local anesthetic is used and note states no systemic sedatives. If unclear, null.""".strip(),
    "pleural_guidance": """
Imaging guidance for pleural procedures only (thoracentesis, chest tube/pigtail, tunneled pleural catheter, medical thoracoscopy, pleural drain/biopsy). Allowed: Ultrasound, CT, Blind; null if no pleural procedure or guidance not documented. Ultrasound only when pleural procedure is ultrasound-guided; ignore EBUS/rebus/bronchial ultrasound. CT only when pleural procedure performed under CT/CT-fluoro. Blind when no imaging or for medical thoracoscopy/pleuroscopy without imaging guidance. Do not set from non-pleural procedures or prior diagnostic imaging alone.""".strip(),
    "pleural_procedure_type": """
Type of pleural procedure performed (not bronchoscopic). Allowed: Thoracentesis, Chest Tube, Tunneled Catheter, Medical Thoracoscopy, Chemical Pleurodesis; null if no pleural procedure. Priority: Chemical Pleurodesis > Medical Thoracoscopy > (Chest Tube vs Tunneled Catheter) > Thoracentesis. Chest Tube for any pleural drain/pigtail/intercostal drain unless clearly tunneled/indwelling (then Tunneled Catheter). Thoracentesis only when fluid is drained and no tube left. Medical Thoracoscopy/pleuroscopy when explicitly described. Chemical Pleurodesis when agent instilled, regardless of tube/thoacoscopy.""".strip(),
    "disposition": """
Immediate post-procedure disposition. Allowed: Discharge Home, PACU Recovery, Floor Admission, ICU Admission; null if not documented. Choose the immediate destination after the procedure (not later transfers). PACU Recovery for recovery/PACU/phase I. ICU Admission for ICU/MICU/SICU/critical care. Floor Admission for non-ICU inpatient/telemetry/step-down. Discharge Home only when explicitly stated going home same day. If unclear or only intra-procedure locations, null.""".strip(),
    "procedure_date": """
Procedure date (YYYY-MM-DD). Convert common formats (e.g., 8/23/2023, 05-07-25, March 5, 2025) into YYYY-MM-DD. Prefer labels: "DATE OF PROCEDURE", "PROCEDURE DATE", "Service Date", or header Date within the procedure note. Ignore follow-up/past dates or non-procedure dates. If multiple and unclear, null.""".strip(),
    "patient_mrn": """
Patient medical record number or clearly labeled patient ID. Prefer explicit MRN/ID labels (e.g., "MRN: 3847592", "ID: MR4729384"). Do not return dates, accession numbers, or phone-like numbers. Preserve the ID format; strip labels if included. If no MRN/ID documented, return null.""".strip(),
    "asa_class": """
ASA physical status if explicitly documented. Valid answers are the text as written (e.g., "ASA 3", "ASA III", "ASA 2E"). Do not infer from comorbidities or vitals. If multiple ASA values, choose the one clearly tied to this procedure or the last mentioned if ambiguous. If not documented, return null.""".strip(),
    "airway_type": """
Airway used for the bronchoscopy. Allowed: Native, LMA, ETT, Tracheostomy, Rigid Bronchoscope; null if not documented. Rigid bronchoscopy → Rigid Bronchoscope. Intubated/ETT for the procedure → ETT. LMA placed for the case → LMA. Bronchoscopy via tracheostomy/trach tube → Tracheostomy. Awake/moderate sedation with topical anesthesia and no device → Native. If unsure, null.""".strip(),
    "stent_type": """
Airway stent type placed. Allowed: Silicone-Dumon, Silicone-Y-Stent, Silicone Y-Stent, Hybrid, Metallic-Covered, Metallic-Uncovered, Other; null if none. Map Dumon/Y-stent/metallic/covered/uncovered wording to the closest allowed value; use Other only if unclear.""".strip(),
    "stent_location": """
Location of airway stent. Allowed: Trachea, Mainstem, Lobar; null if no stent. Map mentions of trachea to Trachea; mainstem/right/left main bronchus to Mainstem; lobar or named lobes (RUL/RML/RLL/LUL/LLL) to Lobar.""".strip(),
    "stent_deployment_method": """
Stent deployment method. Allowed: Rigid, Flexible over Wire; null if not documented. Use Rigid when placed via rigid bronchoscope; Flexible over Wire when placed through flexible scope over a wire.""".strip(),
    "ebus_rose_result": """
ROSE result if performed. Allowed: Malignant, Benign, Granuloma, Nondiagnostic, Atypical cells present, Atypical lymphoid proliferation; null if not documented. Use the closest category matching the ROSE description; do not invent values.""".strip(),
    "ebus_needle_gauge": """
EBUS needle gauge if documented. Allowed: 21G, 22G, 25G; null if not documented. Normalize numeric mentions (21/22/25) to the matching gauge with 'G'.""".strip(),
    "ebus_needle_type": """
EBUS needle type if documented. Allowed: Standard, FNB; null if not documented. Map phrases containing 'FNB' to FNB; otherwise Standard if explicitly stated.""".strip(),
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
