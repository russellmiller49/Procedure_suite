"""Reporter-only schema overrides for interactive, partially-populated bundles.

The registry/extraction pipeline can often identify *that* a procedure was
performed without all documentation details (counts, segments, tests, etc.).

For the interactive Reporter Builder, we need those procedures to still be
represented in a ProcedureBundle so validation can prompt the user for missing
details, and rendering can produce a draft without crashing.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TransbronchialNeedleAspirationPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lung_segment: str | None = None
    needle_tools: str | None = None
    samples_collected: int | None = None
    tests: List[str] = Field(default_factory=list)


class BALPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lung_segment: str | None = None
    instilled_volume_cc: int | None = None
    returned_volume_cc: int | None = None
    tests: List[str] = Field(default_factory=list)


class BronchialBrushingPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lung_segment: str | None = None
    samples_collected: int | None = None
    brush_tool: str | None = None
    tests: List[str] = Field(default_factory=list)


class BronchialWashingPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    airway_segment: str | None = None
    instilled_volume_ml: int | None = None
    returned_volume_ml: int | None = None
    tests: List[str] = Field(default_factory=list)


class TransbronchialCryobiopsyPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lung_segment: str | None = None
    num_samples: int | None = None
    cryoprobe_size_mm: float | None = None
    freeze_seconds: int | None = None
    thaw_seconds: int | None = None
    blocker_type: str | None = None
    blocker_volume_ml: float | None = None
    blocker_location: str | None = None
    tests: List[str] = Field(default_factory=list)
    radial_vessel_check: bool | None = None
    notes: str | None = None


class PeripheralAblationPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    modality: str | None = None
    target: str | None = None
    power_w: int | None = None
    duration_min: float | None = None
    max_temp_c: int | None = None
    notes: str | None = None


class EndobronchialCatheterPlacementPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    target_airway: str | None = None
    catheter_size_french: int | None = None
    obstruction_pct: int | None = None
    fluoroscopy_used: bool | None = None
    dummy_wire_check: bool | None = None


class AirwayStentPlacementPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    location: str | None = None
    stent_brand: str | None = None
    stent_type: str | None = None
    covered: bool | None = None
    device_size: str | None = None
    diameter_mm: float | None = None
    length_mm: float | None = None
    pre_obstruction_pct: int | None = None
    post_obstruction_pct: int | None = None
    notes: str | None = None


class ChartisAssessmentPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    target_lobe: str | None = None
    cv_status: str | None = None
    flow: str | None = None
    notes: str | None = None


class MedicalThoracoscopyPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")

    side: str | None = None
    findings: str | None = None
    fluid_evacuated: bool | None = None
    chest_tube_left: bool | None = None
