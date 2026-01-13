"""IP Registry Schema v3.

This is the next-generation schema with enhanced features:
- Structured event timeline
- Enhanced complication modeling
- Better laterality tracking
- Procedure outcome flags
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


# =============================================================================
# EBUS Node Interaction (Granular)
# =============================================================================

NodeActionType = Literal[
    "inspected_only",       # Visual/Ultrasound only (NO needle)
    "needle_aspiration",    # TBNA / FNA
    "core_biopsy",          # FNB / Core needle
    "forceps_biopsy"        # Mini-forceps
]

NodeOutcomeType = Literal[
    "benign",
    "malignant",
    "suspicious",
    "nondiagnostic",
    "deferred_to_final_path",
    "unknown"
]


class NodeInteraction(BaseModel):
    """Represents a specific interaction with a lymph node station.

    DISTINCTION: 'inspected_only' vs 'needle_aspiration' is critical.
    """

    station: str = Field(
        ...,
        description="The standardized lymph node station (e.g., '4R', '7', '11L').",
    )
    action: NodeActionType = Field(
        ...,
        description=(
            "The specific action taken. Use 'inspected_only' if described as "
            "'sized', 'viewed', or 'not biopsied'."
        ),
    )
    outcome: Optional[NodeOutcomeType] = Field(
        None,
        description="The immediate interpretation (ROSE) or final pathology if mentioned.",
    )
    evidence_quote: str = Field(
        ...,
        description=(
            "CRITICAL: The verbatim quote from the text proving the specific action occurred. "
            "E.g., 'FNA of station 7 performed'."
        ),
    )


class LinearEBUS(BaseModel):
    """Linear EBUS with granular per-node events."""

    performed: bool = Field(False, description="Was Linear EBUS performed?")
    node_events: List[NodeInteraction] = Field(
        default_factory=list,
        description="List of all lymph node interactions, both sampled and inspected.",
    )
    needle_gauge: Optional[str] = Field(None, description="Size of needle used (e.g., '22G', '19G').")

    @property
    def stations_sampled(self) -> List[str]:
        """Derived property for CPT logic (e.g. 31653 requires count >= 3)."""
        return [
            event.station
            for event in self.node_events
            if event.action in ("needle_aspiration", "core_biopsy", "forceps_biopsy")
        ]

    @property
    def stations_inspected_only(self) -> List[str]:
        """Derived property for reporting."""
        return [event.station for event in self.node_events if event.action == "inspected_only"]


class PatientInfo(BaseModel):
    """Patient demographic information."""

    patient_id: str = ""
    mrn: str = ""
    age: Optional[int] = None
    sex: Optional[Literal["M", "F", "O"]] = None
    bmi: Optional[float] = None
    smoking_status: Optional[str] = None


class ProcedureInfo(BaseModel):
    """Procedure metadata."""

    procedure_id: str = ""
    procedure_date: Optional[date] = None
    procedure_type: str = ""
    indication: str = ""
    urgency: Literal["routine", "urgent", "emergent"] = "routine"
    operator: str = ""
    facility: str = ""


class Sedation(BaseModel):
    """Sedation details with timing."""

    type: Literal["none", "moderate", "deep", "general"] = "moderate"
    agents: List[str] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    provider: str = ""
    independent_observer: bool = False


class AnatomicLocation(BaseModel):
    """Detailed anatomic location with laterality."""

    name: str  # "4R", "RUL", "trachea"
    laterality: Optional[Literal["left", "right", "bilateral", "midline"]] = None
    segment: Optional[str] = None
    subsegment: Optional[str] = None
    lymph_node_station: Optional[str] = None


class BiopsySite(BaseModel):
    """Enhanced biopsy site with more detail."""

    location: AnatomicLocation
    technique: str = ""  # "EBUS-TBNA", "TBLB", "forceps", "cryobiopsy"
    passes: Optional[int] = None
    specimens_obtained: Optional[int] = None
    rose_result: Optional[str] = None
    pathology_result: Optional[str] = None
    adequacy: Optional[Literal["adequate", "inadequate", "pending"]] = None


class StentPlacement(BaseModel):
    """Enhanced stent placement details."""

    location: AnatomicLocation
    type: str = ""  # "silicone", "metal", "hybrid"
    subtype: str = ""  # "Y-stent", "straight", "tracheobronchial"
    size: str = ""  # "14x40mm"
    manufacturer: str = ""
    deployment_successful: bool = True
    complications: List[str] = Field(default_factory=list)


class ProcedureEvent(BaseModel):
    """A timestamped event during the procedure."""

    timestamp: Optional[datetime] = None
    event_type: str  # "start", "biopsy", "stent", "complication", "end"
    description: str
    location: Optional[AnatomicLocation] = None
    outcome: Optional[str] = None


class Finding(BaseModel):
    """A finding from the procedure."""

    category: str  # "anatomic", "pathologic", "incidental"
    description: str
    severity: Optional[str] = None
    location: Optional[AnatomicLocation] = None
    action_taken: Optional[str] = None


class Complication(BaseModel):
    """Enhanced complication with timing and causality."""

    type: str  # "bleeding", "pneumothorax", "hypoxia"
    severity: Literal["mild", "moderate", "severe"] = "mild"
    onset: Literal["immediate", "delayed", "post-procedure"] = "immediate"
    onset_time: Optional[datetime] = None
    related_to: Optional[str] = None  # Which procedure step caused it
    intervention: Optional[str] = None
    resolved: bool = True
    resolution_time: Optional[datetime] = None


class ProcedureOutcome(BaseModel):
    """Summary of procedure outcome."""

    completed: bool = True
    aborted: bool = False
    abort_reason: Optional[str] = None
    diagnostic_yield: Optional[str] = None
    therapeutic_success: Optional[bool] = None
    follow_up_planned: bool = False
    follow_up_notes: Optional[str] = None


class IPRegistryV3(BaseModel):
    """IP Registry Schema v3 - next-generation schema.

    New in v3:
    - Structured event timeline
    - Enhanced complication modeling with timing and causality
    - Better laterality tracking via AnatomicLocation
    - Procedure outcome flags
    - BMI and smoking status
    - Operator and facility info
    """

    # Metadata
    schema_version: Literal["v3"] = "v3"
    registry_id: str = "ip_registry"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Patient and procedure
    patient: PatientInfo = Field(default_factory=PatientInfo)
    procedure: ProcedureInfo = Field(default_factory=ProcedureInfo)

    # Sedation
    sedation: Sedation = Field(default_factory=Sedation)

    # Event timeline
    events: List[ProcedureEvent] = Field(default_factory=list)

    # EBUS-TBNA
    ebus_performed: bool = False
    ebus_stations: List[BiopsySite] = Field(default_factory=list)
    ebus_station_count: int = 0

    # Transbronchial biopsy
    tblb_performed: bool = False
    tblb_sites: List[BiopsySite] = Field(default_factory=list)
    tblb_technique: Optional[Literal["forceps", "cryobiopsy", "both"]] = None

    # Navigation
    navigation_performed: bool = False
    navigation_system: str = ""
    navigation_target_reached: Optional[bool] = None

    # Radial EBUS
    radial_ebus_performed: bool = False
    radial_ebus_findings: List[str] = Field(default_factory=list)

    # BAL
    bal_performed: bool = False
    bal_sites: List[AnatomicLocation] = Field(default_factory=list)
    bal_volume_ml: Optional[int] = None
    bal_return_ml: Optional[int] = None

    # Therapeutic procedures
    dilation_performed: bool = False
    dilation_sites: List[AnatomicLocation] = Field(default_factory=list)
    dilation_technique: str = ""

    stent_placed: bool = False
    stents: List[StentPlacement] = Field(default_factory=list)

    ablation_performed: bool = False
    ablation_technique: str = ""
    ablation_sites: List[AnatomicLocation] = Field(default_factory=list)

    blvr_performed: bool = False
    blvr_valves: int = 0
    blvr_target_lobe: str = ""
    blvr_chartis_performed: bool = False
    blvr_cv_result: Optional[str] = None

    # Findings
    findings: List[Finding] = Field(default_factory=list)

    # Complications
    complications: List[Complication] = Field(default_factory=list)
    any_complications: bool = False

    # Outcome
    outcome: ProcedureOutcome = Field(default_factory=ProcedureOutcome)

    # Disposition
    disposition: str = ""  # "home", "observation", "admit"
    length_of_stay_hours: Optional[int] = None

    # Free text
    impression: str = ""
    recommendations: str = ""

    model_config = {"frozen": False}
