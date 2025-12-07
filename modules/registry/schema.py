"""Registry data structures built from the JSON schema in data/knowledge/IP_Registry.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, create_model, field_serializer, model_validator

from modules.common.spans import Span
from modules.registry.schema_granular import (
    EnhancedRegistryGranularData,
    validate_ebus_consistency,
    derive_aggregate_fields,
    IPCProcedure,
    ClinicalContext,
    PatientDemographics,
    AirwayStentProcedure,
)

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"

# Optional overrides for individual fields (identified via dotted paths).
CUSTOM_FIELD_TYPES: dict[tuple[str, ...], Any] = {}
CUSTOM_FIELD_TYPES[("RegistryRecord", "pleural_procedures", "ipc")] = IPCProcedure
CUSTOM_FIELD_TYPES[("RegistryRecord", "clinical_context")] = ClinicalContext
CUSTOM_FIELD_TYPES[("RegistryRecord", "patient_demographics")] = PatientDemographics
CUSTOM_FIELD_TYPES[("RegistryRecord", "procedures_performed", "airway_stent")] = AirwayStentProcedure
_MODEL_CACHE: dict[tuple[str, ...], type[BaseModel]] = {}


def _load_schema() -> dict[str, Any]:
    if not _SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Registry schema not found at {_SCHEMA_PATH}")
    return json.loads(_SCHEMA_PATH.read_text())


def _pascal_case(parts: list[str]) -> str:
    tokens = []
    for part in parts:
        tokens.extend(re.split(r"[^0-9A-Za-z]", part))
    return "".join(token.capitalize() for token in tokens if token)


def _schema_type(prop: dict[str, Any], path: tuple[str, ...]) -> Any:
    override = CUSTOM_FIELD_TYPES.get(path)
    if override:
        return override

    enum = prop.get("enum")
    if enum:
        values = tuple(v for v in enum if v is not None)
        if values:
            return Literal[values]  # type: ignore[arg-type]

    typ = prop.get("type")
    if isinstance(typ, list):
        typ = next((t for t in typ if t != "null"), None)

    if typ == "string":
        return str
    if typ == "number":
        return float
    if typ == "integer":
        return int
    if typ == "boolean":
        return bool
    if typ == "array":
        items = prop.get("items") or {}
        item_type = _schema_type(items, path + ("item",))
        return list[item_type]  # type: ignore[index]
    if typ == "object" or prop.get("properties"):
        return _build_submodel(path, prop)
    return Any


def _build_submodel(path: tuple[str, ...], schema: dict[str, Any]) -> type[BaseModel]:
    if path in _MODEL_CACHE:
        return _MODEL_CACHE[path]

    properties = schema.get("properties", {})
    field_defs: dict[str, tuple[Any, Any]] = {}
    for name, prop in properties.items():
        field_type = _schema_type(prop, path + (name,))
        field_defs[name] = (field_type | None, Field(default=None))  # type: ignore[operator]

    model_name = _pascal_case(list(path)) or "RegistrySubModel"
    model = create_model(
        model_name,
        __config__=ConfigDict(extra="ignore"),
        **field_defs,  # type: ignore[arg-type]
    )
    _MODEL_CACHE[path] = model
    return model


def _build_registry_model() -> type[BaseModel]:
    schema = _load_schema()
    base_model = _build_submodel(("RegistryRecord",), schema)

    class RegistryRecord(base_model):  # type: ignore[misc,valid-type]
        """Concrete registry record model with evidence fields.

        Includes optional granular per-site data for research/QI.
        When granular_data is present, aggregate fields can be derived automatically
        using derive_aggregate_fields() for backward compatibility.
        """

        model_config = ConfigDict(extra="ignore")

        evidence: dict[str, list[Span]] = Field(default_factory=dict)
        version: str | None = None
        procedure_families: list[str] = Field(default_factory=list)

        # Granular per-site data (EBUS stations, navigation targets, CAO sites, etc.)
        granular_data: EnhancedRegistryGranularData | None = Field(
            default=None,
            description="Optional granular per-site registry data for research/QI. "
                        "Complements existing aggregate fields for backward compatibility."
        )

        # Validation warnings from granular data consistency checks
        granular_validation_warnings: list[str] = Field(default_factory=list)

        @field_serializer("procedure_setting")
        @classmethod
        def serialize_procedure_setting(cls, value):
            """Temporarily suppress procedure_setting from serialized payloads."""
            return None

        @model_validator(mode="before")
        @classmethod
        def hoist_granular_arrays(cls, values: Any):
            """Ensure legacy flat granular arrays get nested under granular_data."""
            if not isinstance(values, dict):
                return values

            granular = values.get("granular_data")
            if granular is None:
                granular_dict: dict[str, Any] = {}
            elif isinstance(granular, BaseModel):
                granular_dict = granular.model_dump()
            elif isinstance(granular, dict):
                granular_dict = dict(granular)
            else:
                # Unsupported type (e.g., list) - leave values untouched
                return values

            moved = False
            for field in GRANULAR_ARRAY_FIELDS:
                if field in values and values[field] is not None:
                    granular_dict.setdefault(field, values.pop(field))
                    moved = True

            if moved or granular_dict:
                values["granular_data"] = granular_dict
            else:
                values.pop("granular_data", None)
            return values

    RegistryRecord.__name__ = "RegistryRecord"
    return RegistryRecord


GRANULAR_ARRAY_FIELDS = (
    "linear_ebus_stations_detail",
    "navigation_targets",
    "cao_interventions_detail",
    "blvr_valve_placements",
    "blvr_chartis_measurements",
    "cryobiopsy_sites",
    "thoracoscopy_findings_detail",
    "specimens_collected",
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


class CaoIntervention(BaseModel):
    """Structured data for a single CAO intervention site.

    Supports multi-site CAO procedures where each airway segment may have
    different pre/post obstruction levels and treatment modalities.
    """

    location: str  # e.g., "RML", "RLL", "BI", "LMS", "distal_trachea"
    pre_obstruction_pct: int | None = None  # 0-100, approximate pre-procedure obstruction
    post_obstruction_pct: int | None = None  # 0-100, approximate post-procedure obstruction
    modalities: list[str] = Field(default_factory=list)  # e.g., ["APC", "cryo", "mechanical"]
    notes: str | None = None  # Additional context (e.g., "Post-obstructive pus drained")


class BiopsySite(BaseModel):
    """Structured data for a biopsy location.

    Supports multiple biopsy sites beyond just lobar locations.
    """

    location: str  # e.g., "distal_trachea", "RLL", "carina", "LMS"
    lobe: str | None = None  # If applicable: "RUL", "RML", "RLL", "LUL", "LLL"
    segment: str | None = None  # If applicable: segment name
    specimens_count: int | None = None  # Number of specimens from this site


__all__ = [
    "RegistryRecord",
    "BLVRData",
    "DestructionEvent",
    "EnhancedDilationEvent",
    "AspirationEvent",
    "CaoIntervention",
    "BiopsySite",
    # Granular data exports
    "EnhancedRegistryGranularData",
    "validate_ebus_consistency",
    "derive_aggregate_fields",
]
