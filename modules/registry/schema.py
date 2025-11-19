"""Registry data structures and validation utilities."""

from __future__ import annotations

import uuid
from datetime import date, time
from typing import Any, ClassVar, List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.common.spans import Span

IASLC_STATIONS = {
    "2R",
    "2L",
    "3",
    "4R",
    "4L",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10R",
    "10L",
    "11R",
    "11L",
    "12R",
    "12L",
    "13R",
    "13L",
    "14R",
    "14L",
}

LOBE_NAMES = {"RUL", "RML", "RLL", "LUL", "LLL"}

COMPLICATIONS = {
    "Bleeding",
    "Pneumothorax",
    "Hypoxemia",
    "Valve Migration",
    "None",
}

SETTINGS = {"OR", "Procedure Room", "ICU", "Clinic"}
ANESTHESIA_TYPES = {"Moderate Sedation", "MAC", "GA", "None"}


class Lesion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lesion_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str  # e.g., "complex_tracheal_stenosis", "tumor"
    location: str  # Normalized airway segment
    side: Literal["left", "right", "midline", "bilateral"] | None = None
    obstruction_baseline: int | None = None  # %
    obstruction_post: int | None = None  # %
    length_cm: float | None = None
    distance_from_cords_cm: float | None = None
    interventions: list[str] = Field(default_factory=list) # e.g. ["stent", "dilation"]
    comments: str | None = None


class Device(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: Literal["stent", "balloon", "catheter", "valve", "other"]
    name: str | None = None # e.g. "Ultraflex", "Elation"
    size_text: str | None = None # Raw text e.g. "16x40mm", "14/16.5/18mm"
    location: str | None = None
    details: dict[str, Any] = Field(default_factory=dict) # Extra metadata


# Keep BLVRData for now as it's used by the existing extractor
class BLVRData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lobes: list[str]
    valve_count: int | None = None
    valve_details: list[dict[str, object]] = Field(default_factory=list)
    manufacturer: str | None = None
    chartis: dict[str, str] = Field(default_factory=dict)

    @field_validator("lobes")
    @classmethod
    def validate_lobes(cls, value: list[str]) -> list[str]:
        for lobe in value:
            if lobe not in LOBE_NAMES:
                raise ValueError(f"Invalid lobe: {lobe}")
        return value


class RegistryRecord(BaseModel):
    """Structured registry payload with strict enum enforcement."""

    model_config = ConfigDict(extra="ignore") # Relax to allow flexible merging of old/new data

    patient_id: str | None = None
    encounter_date: date | None = None
    indication: str | None = None
    diagnosis_codes: list[str] = Field(default_factory=list)
    setting: str | None = None
    anesthesia: str | None = None
    sedation_start: time | None = None
    sedation_stop: time | None = None
    navigation_used: bool = False
    radial_ebus_used: bool = False
    linear_ebus_stations: list[str] = Field(default_factory=list)
    tblb_lobes: list[str] = Field(default_factory=list)
    blvr: BLVRData | None = None
    
    # NEW: Nested structures
    lesions: list[Lesion] = Field(default_factory=list)
    devices: list[Device] = Field(default_factory=list)
    
    # Legacy/Compatibility fields (kept for regex extractors temporarily)
    stents: list[dict[str, Any]] = Field(default_factory=list) # Relaxed type
    dilation_events: list[dict[str, Any]] = Field(default_factory=list) # Relaxed type
    destruction_events: list[dict[str, Any]] = Field(default_factory=list) # Relaxed type
    aspiration_events: list[dict[str, Any]] = Field(default_factory=list) # Relaxed type
    dilation_sites: list[str] = Field(default_factory=list)

    pleural_procedures: list[str] = Field(default_factory=list)
    
    # Outcome fields
    technical_success: Literal["complete", "partial", "failed", "unknown"] = "unknown"
    complications: list[str] = Field(default_factory=list)
    followup_plan: str | None = None
    
    imaging_archived: bool | None = None
    disposition: str | None = None
    evidence: dict[str, list[Span]] = Field(default_factory=dict)
    version: str = "0.3.0"

    @field_validator("setting")
    @classmethod
    def validate_setting(cls, value: str | None) -> str | None:
        if value and value not in SETTINGS:
            raise ValueError("Invalid setting")
        return value

    @field_validator("anesthesia")
    @classmethod
    def validate_anesthesia(cls, value: str | None) -> str | None:
        if value and value not in ANESTHESIA_TYPES:
            raise ValueError("Invalid anesthesia type")
        return value

    @field_validator("linear_ebus_stations", mode="after")
    @classmethod
    def validate_stations(cls, value: list[str]) -> list[str]:
        for station in value:
            if station not in IASLC_STATIONS:
                raise ValueError(f"Invalid station: {station}")
        return value

    @field_validator("tblb_lobes", mode="after")
    @classmethod
    def validate_tblb_lobes(cls, value: list[str]) -> list[str]:
        for lobe in value:
            if lobe not in LOBE_NAMES:
                raise ValueError(f"Invalid lobe: {lobe}")
        return value
