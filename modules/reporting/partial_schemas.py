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
