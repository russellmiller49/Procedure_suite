"""Event-log Registry V3 extraction schema (LLM-facing).

Used by the V3 extraction engine (`modules/registry/extractors/v3_extractor.py`) and
evidence verification (`modules/registry/evidence/verifier.py`).

Do not confuse this with the richer registry entry schema at `proc_schemas.registry.ip_v3`.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    quote: str
    start: int | None = None
    end: int | None = None


class ProcedureTarget(BaseModel):
    model_config = ConfigDict(extra="ignore")

    anatomy_type: str | None = None
    lobe: str | None = None
    segment: str | None = None
    station: str | None = None


class LesionDetails(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lesion_type: str | None = None
    size_mm: float | None = None


class Outcomes(BaseModel):
    model_config = ConfigDict(extra="ignore")

    airway_lumen_pre: str | None = None
    airway_lumen_post: str | None = None
    symptoms: str | None = None
    pleural: str | None = None
    complications: str | None = None


class ProcedureEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str
    type: str
    method: str | None = None
    target: ProcedureTarget = ProcedureTarget()
    lesion: LesionDetails = LesionDetails()
    devices: list[str] = []
    specimens: list[str] = []
    outcomes: Outcomes = Outcomes()
    evidence: EvidenceSpan | None = None

    measurements: Any | None = None
    findings: Any | None = None
    stent_size: str | None = None
    stent_material_or_brand: str | None = None
    catheter_size_fr: float | None = None


class IPRegistryV3(BaseModel):
    model_config = ConfigDict(extra="ignore")

    note_id: str
    source_filename: str
    schema_version: Literal["v3"] = "v3"
    established_tracheostomy_route: bool = False
    procedures: list[ProcedureEvent] = []
