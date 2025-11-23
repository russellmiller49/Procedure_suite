"""Registry data structures built from the JSON schema in data/knowledge/IP_Registry.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, create_model

from modules.common.spans import Span

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"

# Domain-specific enums that extend/override the JSON schema for validation.
SedationType = Literal["Moderate", "Deep", "General", "Local", "Monitored Anesthesia Care"]
NavImagingVerification = Literal["Fluoroscopy", "Cone Beam CT", "O-Arm", "Ultrasound", "None"]
CaoTumorLocation = Literal[
    "Trachea",
    "RMS",
    "LMS",
    "Bronchus Intermedius",
    "Lobar",
    "RUL",
    "RML",
    "RLL",
    "LUL",
    "LLL",
    "Mainstem",
]
PleuralProcedureType = Literal[
    "Thoracentesis",
    "Chest Tube",
    "Tunneled Catheter",
    "Medical Thoracoscopy",
    "Chemical Pleurodesis",
]
PleuralFluidAppearance = Literal[
    "Serous",
    "Sanguinous",
    "Purulent",
    "Chylous",
    "Serosanguinous",
    "Turbid",
    "Other",
]
StentType = Literal[
    "Silicone-Dumon",
    "Silicone-Y-Stent",
    "Silicone Y-Stent",
    "Hybrid",
    "Metallic-Covered",
    "Metallic-Uncovered",
    "Other",
]
FinalDiagnosisPrelim = Literal[
    "Malignancy",
    "Granulomatous",
    "Infectious",
    "Non-diagnostic",
    "Benign",
    "Other",
]
EbusRoseResult = Literal[
    "Malignant",
    "Benign",
    "Granuloma",
    "Nondiagnostic",
    "Atypical cells present",
    "Atypical lymphoid proliferation",
]

# Field-level overrides to keep validation flexible even when the JSON schema is more
# restrictive. This avoids hard failures on newly observed real-world values.
CUSTOM_FIELD_TYPES: dict[str, Any] = {
    "sedation_type": SedationType,
    "nav_imaging_verification": NavImagingVerification,
    "cao_tumor_location": CaoTumorLocation,
    "pleural_procedure_type": PleuralProcedureType,
    "pleural_fluid_appearance": PleuralFluidAppearance,
    "stent_type": StentType,
    "final_diagnosis_prelim": FinalDiagnosisPrelim,
    "ebus_rose_result": EbusRoseResult,
    # Allow modifiers/verification text alongside integers for CPT entries.
    "cpt_codes": list[int | str],
}


def _json_type_to_py(prop: dict[str, Any]) -> Any:
    """Map JSON schema type/enum to Python type."""
    typ = prop.get("type")
    enum = prop.get("enum")
    if enum:
        return Literal[tuple(enum)]  # type: ignore[arg-type]

    # Handle union types like ["string", "null"]
    if isinstance(typ, list):
        base_types = [t for t in typ if t != "null"]
        if not base_types:
            return Any
        typ = base_types[0]

    if typ == "string":
        return str
    if typ == "number":
        return float
    if typ == "integer":
        return int
    if typ == "boolean":
        return bool
    if typ == "array":
        items = prop.get("items", {}) or {}
        item_type = _json_type_to_py(items)
        return list[item_type]  # type: ignore[index]
    if typ == "object":
        return dict[str, Any]
    return Any


def _build_registry_model() -> type[BaseModel]:
    if not _SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Registry schema not found at {_SCHEMA_PATH}")

    schema = json.loads(_SCHEMA_PATH.read_text())
    properties: dict[str, dict[str, Any]] = schema.get("properties", {})

    field_defs: dict[str, tuple[Any, Any]] = {}
    for name, prop in properties.items():
        py_type = CUSTOM_FIELD_TYPES.get(name) or _json_type_to_py(prop)
        # Allow nulls by default
        py_type = py_type | None  # type: ignore[operator]
        default = None
        field_defs[name] = (py_type, default)

    # Append metadata
    field_defs["evidence"] = (dict[str, list[Span]], Field(default_factory=dict))
    field_defs["version"] = (str, "0.5.0")

    model_config = ConfigDict(extra="ignore")

    return create_model(
        "RegistryRecord",
        __config__=model_config,
        **field_defs,  # type: ignore[arg-type]
    )


RegistryRecord = _build_registry_model()

class BLVRData(BaseModel):
    lobes: list[str]
    valve_count: int | None
    valve_details: list[dict[str, Any]]
    manufacturer: str | None
    chartis: dict[str, str]

class DestructionEvent(BaseModel):
    modality: str
    site: str

class EnhancedDilationEvent(BaseModel):
    site: str
    balloon_size: str | None
    inflation_pressure: str | None

class AspirationEvent(BaseModel):
    site: str
    volume: str | None
    character: str | None

__all__ = ["RegistryRecord", "BLVRData", "DestructionEvent", "EnhancedDilationEvent", "AspirationEvent"]
