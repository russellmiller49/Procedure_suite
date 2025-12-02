"""Registry data structures built from the JSON schema in data/knowledge/IP_Registry.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, create_model

from modules.common.spans import Span

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"

# Optional overrides for individual fields (identified via dotted paths).
CUSTOM_FIELD_TYPES: dict[tuple[str, ...], Any] = {}
_MODEL_CACHE: dict[tuple[str, ...], type[BaseModel]] = {}
_COMPAT_ATTRIBUTE_PATHS: dict[str, tuple[str, ...]] = {
    "sedation_type": ("sedation", "type"),
    "sedation_start": ("sedation", "start_time"),
    "sedation_stop": ("sedation", "end_time"),
    "nav_platform": ("equipment", "navigation_platform"),
    "nav_rebus_used": ("procedures_performed", "radial_ebus", "performed"),
    "nav_rebus_view": ("procedures_performed", "radial_ebus", "probe_position"),
    "nav_sampling_tools": ("procedures_performed", "navigational_bronchoscopy", "sampling_tools_used"),
    "nav_tool_in_lesion": ("procedures_performed", "navigational_bronchoscopy", "tool_in_lesion_confirmed"),
    "ebus_stations_sampled": ("procedures_performed", "linear_ebus", "stations_sampled"),
    "linear_ebus_stations": ("procedures_performed", "linear_ebus", "stations_planned"),
    "ebus_needle_gauge": ("procedures_performed", "linear_ebus", "needle_gauge"),
    "ebus_needle_type": ("procedures_performed", "linear_ebus", "needle_type"),
    "ebus_elastography_pattern": ("procedures_performed", "linear_ebus", "elastography_pattern"),
    "ebus_photodocumentation_complete": ("procedures_performed", "linear_ebus", "photodocumentation_complete"),
    "blvr_target_lobe": ("procedures_performed", "blvr", "target_lobe"),
    "blvr_valve_type": ("procedures_performed", "blvr", "valve_type"),
    "blvr_valve_count": ("procedures_performed", "blvr", "number_of_valves"),
    "ebus_rose_result": ("specimens", "rose_result"),
    "ebus_stations_detail": ("procedures_performed", "linear_ebus", "stations_detail"),
    "ebus_elastography_used": ("procedures_performed", "linear_ebus", "elastography_used"),
    # Stent-related compatibility paths
    "stent_type": ("procedures_performed", "airway_stent", "stent_type"),
    "stent_location": ("procedures_performed", "airway_stent", "location"),
    "stent_action": ("procedures_performed", "airway_stent", "action"),
    # Procedure setting
    "airway_type": ("procedure_setting", "airway_type"),
    # CAO-related legacy fields - mapped to thermal_ablation/mechanical_debulking where applicable
    # Note: These are "best effort" mappings; CAO data in schema is spread across multiple procedure types
    "cao_location": ("procedures_performed", "thermal_ablation", "location"),
    "cao_primary_modality": ("procedures_performed", "thermal_ablation", "modality"),
    "cao_tumor_location": ("procedures_performed", "mechanical_debulking", "location"),
    "cao_obstruction_pre_pct": ("procedures_performed", "thermal_ablation", "pre_obstruction_pct"),
    "cao_obstruction_post_pct": ("procedures_performed", "thermal_ablation", "post_obstruction_pct"),
    # cao_interventions is a complex array; return None until proper transform is built
    "cao_interventions": ("procedures_performed", "thermal_ablation", "interventions"),
}


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
        """Concrete registry record model with evidence fields."""

        model_config = ConfigDict(extra="ignore")

        evidence: dict[str, list[Span]] = Field(default_factory=dict)
        version: str | None = None
        procedure_families: list[str] = Field(default_factory=list)

        def __getattr__(self, item: str) -> Any:
            if item in _COMPAT_ATTRIBUTE_PATHS:
                target = self
                for attr in _COMPAT_ATTRIBUTE_PATHS[item]:
                    if target is None:
                        break
                    target = getattr(target, attr, None)
                return target
            raise AttributeError(f"{type(self).__name__!s} has no attribute {item!s}")

    RegistryRecord.__name__ = "RegistryRecord"
    return RegistryRecord


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
]
