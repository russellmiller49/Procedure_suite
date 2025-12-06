"""Registry data structures with granular per-site models.

This module extends the base schema with detailed per-site/per-node data structures
for EBUS, Navigation, CAO, BLVR, Cryobiopsy, and Thoracoscopy procedures.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# Pleural Procedure Overrides
# =============================================================================

class IPCProcedure(BaseModel):
    """Structured model for indwelling pleural catheter actions."""

    model_config = ConfigDict(extra="ignore")

    performed: bool | None = None
    action: Literal["Insertion", "Removal", "Fibrinolytic instillation"] | None = None
    side: Literal["Right", "Left"] | None = None
    catheter_brand: Literal["PleurX", "Aspira", "Rocket", "Other"] | None = None
    indication: Literal[
        "Malignant effusion",
        "Recurrent benign effusion",
        "Hepatic hydrothorax",
        "Heart failure",
        "Other",
    ] | None = None
    tunneled: bool | None = None

    @field_validator("action", mode="before")
    @classmethod
    def normalize_ipc_action(cls, v):
        """Map common IPC action synonyms into the constrained enum."""
        if v is None:
            return v
        s = str(v).strip().lower()
        if "tunneled" in s or "ipc" in s or "indwelling catheter" in s:
            return "Insertion"
        if "removal" in s or "removed" in s or "pull" in s:
            return "Removal"
        if "tpa" in s or "fibrinolytic" in s or "alteplase" in s:
            return "Fibrinolytic instillation"
        return v


class ClinicalContext(BaseModel):
    """Structured clinical context data with normalized bronchus sign."""

    model_config = ConfigDict(extra="ignore")

    asa_class: int | None = Field(
        None,
        ge=1,
        le=6,
        description="ASA physical status classification (1-6)",
    )
    primary_indication: str | None = Field(
        None,
        description="Primary indication for the procedure (free text)",
    )
    indication_category: Literal[
        "Lung Cancer Diagnosis",
        "Lung Cancer Staging",
        "Lung Nodule Evaluation",
        "Mediastinal Lymphadenopathy",
        "Infection Workup",
        "ILD Evaluation",
        "Hemoptysis",
        "Airway Obstruction",
        "Pleural Effusion - Diagnostic",
        "Pleural Effusion - Therapeutic",
        "Pneumothorax Management",
        "Empyema/Parapneumonic",
        "BLVR Evaluation",
        "BLVR Treatment",
        "Foreign Body",
        "Tracheobronchomalacia",
        "Stricture/Stenosis",
        "Fistula",
        "Stent Management",
        "Ablation",
        "Other",
    ] | None = None
    radiographic_findings: str | None = Field(
        None,
        description="Relevant radiographic findings",
    )
    lesion_size_mm: float | None = Field(
        None,
        ge=0,
        description="Target lesion size in mm",
    )
    lesion_location: str | None = Field(
        None,
        description="Anatomic location of target lesion",
    )
    pet_avidity: bool | None = Field(
        None,
        description="Whether lesion is PET avid",
    )
    suv_max: float | None = Field(
        None,
        ge=0,
        description="Maximum SUV on PET if applicable",
    )
    bronchus_sign: Literal["Positive", "Negative", "Not assessed"] | None = None

    @field_validator("bronchus_sign", mode="before")
    @classmethod
    def normalize_bronchus_sign(cls, v):
        if v is None:
            return "Not assessed"
        if isinstance(v, bool):
            return "Positive" if v else "Negative"

        s = str(v).strip().lower()
        if s in {"yes", "y", "present", "positive", "pos", "true", "1"}:
            return "Positive"
        if s in {"no", "n", "absent", "negative", "neg", "false", "0"}:
            return "Negative"
        if s in {"na", "n/a", "not assessed", "unknown", "indeterminate"}:
            return "Not assessed"
        return v


class PatientDemographics(BaseModel):
    """Demographics with normalized gender field."""

    model_config = ConfigDict(extra="ignore")

    age_years: int | None = Field(
        None,
        ge=0,
        le=120,
        description="Patient age in years",
    )
    gender: Literal["Male", "Female", "Other", "Unknown"] | None = None
    height_cm: float | None = Field(
        None,
        ge=50,
        le=250,
        description="Patient height in cm",
    )
    weight_kg: float | None = Field(
        None,
        ge=20,
        le=400,
        description="Patient weight in kg",
    )
    bmi: float | None = Field(
        None,
        ge=10,
        le=80,
        description="Body mass index",
    )
    smoking_status: Literal["Never", "Former", "Current", "Unknown"] | None = None
    pack_years: float | None = Field(
        None,
        ge=0,
        description="Pack-years of smoking history",
    )

    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, v):
        if v is None:
            return None
        s = str(v).strip().lower()
        if s in {"m", "male"}:
            return "Male"
        if s in {"f", "female"}:
            return "Female"
        if s in {"other", "nonbinary", "non-binary", "nb"}:
            return "Other"
        if s in {"u", "unknown"}:
            return "Unknown"
        return v


class AirwayStentProcedure(BaseModel):
    """Structured airway stent data with location normalization."""

    model_config = ConfigDict(extra="ignore")

    performed: bool | None = None
    action: Literal[
        "Placement",
        "Removal",
        "Revision/Repositioning",
        "Assessment only",
    ] | None = None
    stent_type: Literal[
        "Silicone - Dumon",
        "Silicone - Hood",
        "Silicone - Novatech",
        "SEMS - Uncovered",
        "SEMS - Covered",
        "SEMS - Partially covered",
        "Hybrid",
        "Y-Stent",
        "Other",
    ] | None = None
    stent_brand: str | None = None
    diameter_mm: float | None = Field(None, ge=6, le=25)
    length_mm: float | None = Field(None, ge=10, le=100)
    location: Literal[
        "Trachea",
        "Right mainstem",
        "Left mainstem",
        "Bronchus intermedius",
        "Carina (Y)",
        "Other",
    ] | None = None
    indication: Literal[
        "Malignant obstruction",
        "Benign stenosis",
        "Tracheomalacia",
        "Fistula",
        "Post-dilation",
        "Other",
    ] | None = None
    deployment_successful: bool | None = None

    @field_validator("location", mode="before")
    @classmethod
    def normalize_stent_location(cls, v):
        if v is None:
            return v
        s = str(v).strip().lower()
        if s == "mainstem":
            return "Other"
        return v


# =============================================================================
# EBUS Per-Station Detail
# =============================================================================

class EBUSStationDetail(BaseModel):
    """Per-station EBUS-TBNA data capturing morphology, sampling, and ROSE."""
    
    model_config = ConfigDict(extra="ignore")
    
    # Station identification
    station: str = Field(..., description="IASLC station (2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L, 12R, 12L)")
    
    # Morphology
    short_axis_mm: float | None = Field(None, ge=0, description="Short-axis diameter in mm")
    long_axis_mm: float | None = Field(None, ge=0, description="Long-axis diameter in mm")
    shape: Literal["oval", "round", "irregular"] | None = None
    margin: Literal["distinct", "indistinct", "irregular"] | None = None
    echogenicity: Literal["homogeneous", "heterogeneous"] | None = None
    chs_present: bool | None = Field(None, description="Central hilar structure present")
    necrosis_present: bool | None = None
    calcification_present: bool | None = None
    
    # Elastography
    elastography_performed: bool | None = None
    elastography_score: int | None = Field(None, ge=1, le=5)
    elastography_strain_ratio: float | None = None
    elastography_pattern: Literal[
        "predominantly_blue", "blue_green", "green", "predominantly_green"
    ] | None = None
    
    # Doppler
    doppler_performed: bool | None = None
    doppler_pattern: Literal["avascular", "hilar_vessel", "peripheral", "mixed"] | None = None
    
    # Morphologic interpretation (separate from pathology)
    morphologic_impression: Literal["benign", "suspicious", "malignant", "indeterminate"] | None = None
    
    # Sampling details
    sampled: bool = Field(True, description="Whether this station was actually sampled")
    needle_gauge: Literal[19, 21, 22, 25] | None = None
    needle_type: Literal["Standard FNA", "FNB/ProCore", "Acquire", "ViziShot Flex"] | None = None
    number_of_passes: int | None = Field(None, ge=0, le=10)
    intranodal_forceps_used: bool | None = None
    
    # ROSE
    rose_performed: bool | None = None
    rose_result: Literal[
        "Adequate lymphocytes", "Malignant", "Suspicious for malignancy",
        "Atypical cells", "Granuloma", "Necrosis only", "Nondiagnostic", "Deferred"
    ] | None = None
    rose_adequacy: bool | None = None
    
    # Specimen handling
    specimen_sent_for: list[str] | None = Field(default=None)
    
    # Final results
    final_pathology: str | None = None
    n_stage_contribution: Literal["N0", "N1", "N2", "N3"] | None = None
    
    notes: str | None = None


# =============================================================================
# Navigation Per-Target Detail
# =============================================================================

class NavigationTarget(BaseModel):
    """Per-target data for navigation/robotic bronchoscopy procedures."""
    
    model_config = ConfigDict(extra="ignore")
    
    # Target identification
    target_number: int = Field(..., ge=1, description="Sequential target number")
    target_location_text: str = Field(..., description="Full anatomic description")
    target_lobe: Literal["RUL", "RML", "RLL", "LUL", "LLL", "Lingula"] | None = None
    target_segment: str | None = None
    
    # Target characteristics
    lesion_size_mm: float | None = Field(None, ge=0)
    distance_from_pleura_mm: float | None = Field(None, ge=0)
    bronchus_sign: Literal["Positive", "Negative", "Not assessed"] | None = None
    ct_characteristics: Literal[
        "Solid", "Part-solid", "Ground-glass", "Cavitary", "Calcified"
    ] | None = None
    pet_suv_max: float | None = Field(None, ge=0)
    
    # Navigation performance
    registration_error_mm: float | None = Field(None, ge=0)
    navigation_successful: bool | None = None
    
    # Radial EBUS
    rebus_used: bool | None = None
    rebus_view: Literal["Concentric", "Eccentric", "Adjacent", "Not visualized"] | None = None
    rebus_lesion_appearance: str | None = None
    
    # Tool-in-lesion confirmation
    tool_in_lesion_confirmed: bool | None = None
    confirmation_method: Literal[
        "CBCT", "Augmented fluoroscopy", "Fluoroscopy", "Radial EBUS", "None"
    ] | None = None
    cbct_til_confirmed: bool | None = None
    
    # Sampling
    sampling_tools_used: list[str] | None = Field(default=None)
    number_of_forceps_biopsies: int | None = Field(None, ge=0)
    number_of_needle_passes: int | None = Field(None, ge=0)
    number_of_cryo_biopsies: int | None = Field(None, ge=0)
    
    # ROSE
    rose_performed: bool | None = None
    rose_result: str | None = None
    
    # Complications
    immediate_complication: Literal[
        "None", "Bleeding - mild", "Bleeding - moderate", "Bleeding - severe", "Pneumothorax"
    ] | None = None
    bleeding_management: str | None = None
    
    # Results
    specimen_sent_for: list[str] | None = Field(default=None)
    final_pathology: str | None = None
    
    notes: str | None = None

    @field_validator('bronchus_sign', mode='before')
    @classmethod
    def normalize_bronchus_sign(cls, v):
        """Normalize bronchus sign values from LLM output."""
        if v is True:
            return "Positive"
        if v is False:
            return "Negative"
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in ("pos", "positive", "+"):
                return "Positive"
            if v_lower in ("neg", "negative", "-"):
                return "Negative"
            if v_lower in ("not assessed", "n/a", "na", "unknown"):
                return "Not assessed"
        return v


# =============================================================================
# CAO Intervention Per-Site Detail
# =============================================================================

class CAOModalityApplication(BaseModel):
    """Details for a specific modality applied during CAO intervention."""
    
    model_config = ConfigDict(extra="ignore")
    
    modality: Literal[
        "APC", "Electrocautery - snare", "Electrocautery - knife", "Electrocautery - probe",
        "Cryotherapy - spray", "Cryotherapy - contact", "Cryoextraction",
        "Laser - Nd:YAG", "Laser - CO2", "Laser - diode", "Laser",
        "Mechanical debulking", "Rigid coring", "Microdebrider", "Balloon dilation",
        "Balloon tamponade", "PDT", "Iced saline lavage", "Epinephrine instillation",
        "Tranexamic acid instillation", "Suctioning"
    ]
    power_setting_watts: float | None = None
    apc_flow_rate_lpm: float | None = None
    balloon_diameter_mm: float | None = None
    balloon_pressure_atm: float | None = None
    freeze_time_seconds: int | None = None
    number_of_applications: int | None = Field(None, ge=0)
    duration_seconds: int | None = None


class CAOInterventionDetail(BaseModel):
    """Per-site CAO intervention data with modality details."""
    
    model_config = ConfigDict(extra="ignore")
    
    # Location
    location: str = Field(..., description="Airway location (Trachea, RMS, LMS, BI, etc.)")
    
    # Obstruction characterization
    obstruction_type: Literal["Intraluminal", "Extrinsic", "Mixed"] | None = None
    etiology: Literal[
        "Malignant - primary lung", "Malignant - metastatic", "Malignant - other",
        "Benign - post-intubation", "Benign - post-tracheostomy", "Benign - anastomotic",
        "Benign - inflammatory", "Benign - infectious", "Benign - granulation",
        "Benign - web/stenosis", "Benign - other", "Infectious", "Other"
    ] | None = None
    length_mm: float | None = Field(None, ge=0)
    
    # Pre/Post measurements
    pre_obstruction_pct: int | None = Field(None, ge=0, le=100)
    post_obstruction_pct: int | None = Field(None, ge=0, le=100)
    pre_diameter_mm: float | None = Field(None, ge=0)
    post_diameter_mm: float | None = Field(None, ge=0)
    
    # Treatment modalities
    modalities_applied: list[CAOModalityApplication] | None = Field(default=None)
    
    # Hemostasis
    hemostasis_required: bool | None = None
    hemostasis_methods: list[str] | None = Field(default=None)
    
    # Associated findings
    secretions_present: bool | None = None
    secretions_drained: bool | None = None
    stent_placed_at_site: bool | None = None
    
    notes: str | None = None


# =============================================================================
# BLVR Per-Valve Detail
# =============================================================================

class BLVRValvePlacement(BaseModel):
    """Individual valve placement data for BLVR."""
    
    model_config = ConfigDict(extra="ignore")
    
    valve_number: int = Field(..., ge=1)
    target_lobe: Literal["RUL", "RML", "RLL", "LUL", "LLL", "Lingula"]
    segment: str = Field(..., description="Specific segment (e.g., 'LB1+2', 'LB6')")
    airway_diameter_mm: float | None = Field(None, ge=0)
    valve_size: str = Field(..., description="Valve size (e.g., '4.0', '5.5', '6.0')")
    valve_type: Literal["Zephyr (Pulmonx)", "Spiration (Olympus)"]
    deployment_method: Literal["Standard", "Retroflexed"] | None = None
    deployment_successful: bool
    seal_confirmed: bool | None = None
    repositioned: bool | None = None
    notes: str | None = None


class BLVRChartisMeasurement(BaseModel):
    """Chartis collateral ventilation measurement data."""
    
    model_config = ConfigDict(extra="ignore")
    
    lobe_assessed: Literal["RUL", "RML", "RLL", "LUL", "LLL", "Lingula"]
    segment_assessed: str | None = None
    measurement_duration_seconds: int | None = Field(None, ge=0)
    adequate_seal: bool | None = None
    cv_result: Literal[
        "CV Negative", "CV Positive", "Indeterminate", "Low flow", "No seal", "Aborted"
    ]
    flow_pattern_description: str | None = None
    notes: str | None = None


# =============================================================================
# Cryobiopsy Per-Site Detail
# =============================================================================

class CryobiopsySite(BaseModel):
    """Per-site transbronchial cryobiopsy data."""
    
    model_config = ConfigDict(extra="ignore")
    
    site_number: int = Field(..., ge=1)
    lobe: Literal["RUL", "RML", "RLL", "LUL", "LLL", "Lingula"]
    segment: str | None = None
    distance_from_pleura: Literal[">2cm", "1-2cm", "<1cm", "Not documented"] | None = None
    fluoroscopy_position: str | None = None
    
    # Radial EBUS guidance
    radial_ebus_used: bool | None = None
    rebus_view: str | None = None
    
    # Biopsy details
    probe_size_mm: Literal[1.1, 1.7, 1.9, 2.4] | None = None
    freeze_time_seconds: int | None = Field(None, ge=0, le=10)
    number_of_biopsies: int | None = Field(None, ge=0)
    specimen_size_mm: float | None = Field(None, ge=0)
    
    # Blocker use
    blocker_used: bool | None = None
    blocker_type: Literal["Fogarty", "Arndt", "Cohen", "Cryoprobe sheath"] | None = None
    
    # Complications at site
    bleeding_severity: Literal["None/Scant", "Mild", "Moderate", "Severe"] | None = None
    bleeding_controlled_with: str | None = None
    pneumothorax_after_site: bool | None = None
    
    notes: str | None = None


# =============================================================================
# Thoracoscopy Findings Per-Site
# =============================================================================

class ThoracoscopyFinding(BaseModel):
    """Per-location thoracoscopy/pleuroscopy finding."""
    
    model_config = ConfigDict(extra="ignore")
    
    location: Literal[
        "Parietal pleura - chest wall", "Parietal pleura - diaphragm",
        "Parietal pleura - mediastinum", "Visceral pleura",
        "Lung parenchyma", "Costophrenic angle", "Apex"
    ]
    finding_type: Literal[
        "Normal", "Nodules", "Plaques", "Studding", "Mass",
        "Adhesions - filmy", "Adhesions - dense", "Inflammation",
        "Thickening", "Trapped lung", "Loculations", "Empyema", "Other"
    ]
    extent: Literal["Focal", "Multifocal", "Diffuse"] | None = None
    size_description: str | None = None
    biopsied: bool | None = None
    number_of_biopsies: int | None = Field(None, ge=0)
    biopsy_tool: Literal["Rigid forceps", "Flexible forceps", "Cryoprobe"] | None = None
    impression: Literal[
        "Benign appearing", "Malignant appearing", "Infectious appearing", "Indeterminate"
    ] | None = None
    notes: str | None = None

    @field_validator("biopsy_tool", mode="before")
    @classmethod
    def normalize_thoracoscopy_biopsy_tool(cls, v):
        if v is None:
            return v
        s = str(v).lower()
        if "cryo" in s:
            return "Cryoprobe"
        if "flexible" in s:
            return "Flexible forceps"
        if "rigid" in s:
            return "Rigid forceps"
        if "biopsy forceps" in s:
            return "Rigid forceps"
        return v

    @field_validator("location", mode="before")
    @classmethod
    def normalize_thoracoscopy_location(cls, v):
        if v is None:
            return v
        s = str(v).lower()
        if "pleural space" in s:
            return "Parietal pleura - chest wall"
        if "costophrenic" in s:
            return "Costophrenic angle"
        if "apex" in s:
            return "Apex"
        if "diaphragm" in s:
            return "Parietal pleura - diaphragm"
        if "mediastinum" in s:
            return "Parietal pleura - mediastinum"
        if "visceral" in s or "lung surface" in s:
            return "Visceral pleura"
        return v


# =============================================================================
# Unified Specimen Tracking
# =============================================================================

class SpecimenCollected(BaseModel):
    """Specimen tracking with source linkage."""
    
    model_config = ConfigDict(extra="ignore")
    
    specimen_number: int = Field(..., ge=1)
    source_procedure: Literal[
        "EBUS-TBNA", "Navigation biopsy", "Endobronchial biopsy",
        "Transbronchial biopsy", "Transbronchial cryobiopsy",
        "BAL", "Bronchial wash", "Brushing", "Pleural biopsy", "Pleural fluid", "Other"
    ]
    source_location: str = Field(..., description="Anatomic location")
    collection_tool: str | None = None
    specimen_count: int | None = Field(None, ge=0)
    specimen_adequacy: Literal["Adequate", "Limited", "Inadequate", "Pending"] | None = None
    destinations: list[str] | None = Field(default=None)
    rose_performed: bool | None = None
    rose_result: str | None = None
    final_pathology_diagnosis: str | None = None
    molecular_markers: dict[str, Any] | None = Field(default=None)
    notes: str | None = None


# =============================================================================
# Enhanced Registry Record with Granular Arrays
# =============================================================================

class EnhancedRegistryGranularData(BaseModel):
    """Container for all granular per-site data arrays.
    
    This can be embedded in the main RegistryRecord or used as a separate payload.
    """
    
    model_config = ConfigDict(extra="ignore")
    
    # EBUS per-station
    linear_ebus_stations_detail: list[EBUSStationDetail] | None = Field(default=None)
    
    # Navigation per-target
    navigation_targets: list[NavigationTarget] | None = Field(default=None)
    
    # CAO per-site
    cao_interventions_detail: list[CAOInterventionDetail] | None = Field(default=None)
    
    # BLVR per-valve
    blvr_valve_placements: list[BLVRValvePlacement] | None = Field(default=None)
    blvr_chartis_measurements: list[BLVRChartisMeasurement] | None = Field(default=None)
    
    # Cryobiopsy per-site
    cryobiopsy_sites: list[CryobiopsySite] | None = Field(default=None)
    
    # Thoracoscopy per-location
    thoracoscopy_findings_detail: list[ThoracoscopyFinding] | None = Field(default=None)
    
    # Unified specimen tracking
    specimens_collected: list[SpecimenCollected] | None = Field(default=None)


# =============================================================================
# Validation Helpers
# =============================================================================

def validate_ebus_consistency(
    stations_detail: list[EBUSStationDetail] | None,
    stations_sampled: list[str] | None
) -> list[str]:
    """Validate that EBUS station detail matches sampled stations list.
    
    Returns list of validation error messages (empty if valid).
    """
    errors = []
    
    if not stations_detail and not stations_sampled:
        return errors
    
    if stations_detail and stations_sampled:
        detail_stations = {
            s.station for s in stations_detail 
            if s.sampled is True or s.sampled is None
        }
        sampled_set = set(stations_sampled)
        
        missing = sampled_set - detail_stations
        extra = detail_stations - sampled_set
        
        if missing:
            errors.append(f"Stations in sampled list but missing detail: {sorted(missing)}")
        if extra:
            errors.append(f"Stations with detail but not in sampled list: {sorted(extra)}")
    
    elif stations_sampled and not stations_detail:
        errors.append("stations_sampled populated but no stations_detail provided")
    
    return errors


def derive_aggregate_fields(granular: EnhancedRegistryGranularData) -> dict[str, Any]:
    """Derive aggregate fields from granular data for backward compatibility.

    Returns a dict of aggregate fields that can be merged into the main registry record.
    """
    derived = {}

    # Derive linear_ebus_stations from detail
    if granular.linear_ebus_stations_detail:
        derived["linear_ebus_stations"] = [
            s.station for s in granular.linear_ebus_stations_detail
            if s.sampled is True or s.sampled is None
        ]

        # Count total passes
        total_passes = sum(
            s.number_of_passes or 0
            for s in granular.linear_ebus_stations_detail
        )
        if total_passes:
            derived["ebus_total_passes"] = total_passes

        # Get first ROSE result (for legacy compatibility)
        rose_results = [
            s.rose_result for s in granular.linear_ebus_stations_detail
            if s.rose_result
        ]
        if rose_results:
            derived["ebus_rose_result"] = rose_results[0]

    # Derive nav fields
    if granular.navigation_targets:
        derived["nav_targets_count"] = len(granular.navigation_targets)
        confirmed = sum(1 for t in granular.navigation_targets if t.tool_in_lesion_confirmed)
        derived["nav_til_confirmed_count"] = confirmed

    # Derive BLVR fields
    if granular.blvr_valve_placements:
        derived["blvr_number_of_valves"] = len(granular.blvr_valve_placements)
        lobes = set(v.target_lobe for v in granular.blvr_valve_placements)
        if len(lobes) == 1:
            derived["blvr_target_lobe"] = list(lobes)[0]

    # Derive cryobiopsy specimen count
    if granular.cryobiopsy_sites:
        total = sum(s.number_of_biopsies or 0 for s in granular.cryobiopsy_sites)
        if total:
            derived["cryo_specimens_count"] = total

    return derived


def derive_procedures_from_granular(
    granular_data: dict[str, Any] | None,
    existing_procedures: dict[str, Any] | None
) -> tuple[dict[str, Any], list[str]]:
    """Derive top-level procedures_performed fields from granular data.

    This function ensures that granular data is reflected in the top-level
    procedures_performed structure. It also generates validation warnings
    for inconsistencies.

    Args:
        granular_data: The granular_data dict from the registry record
        existing_procedures: The existing procedures_performed dict

    Returns:
        Tuple of (updated procedures_performed dict, list of validation warnings)
    """
    if not granular_data:
        return existing_procedures or {}, []

    procedures = dict(existing_procedures) if existing_procedures else {}
    warnings: list[str] = []

    # ==========================================================================
    # 1. Derive transbronchial_cryobiopsy from cryobiopsy_sites
    # ==========================================================================
    cryobiopsy_sites = granular_data.get("cryobiopsy_sites", [])
    if cryobiopsy_sites:
        cryo = procedures.get("transbronchial_cryobiopsy") or {}
        if not cryo.get("performed"):
            cryo["performed"] = True

            # Sum biopsies across all sites
            total_biopsies = sum(
                site.get("number_of_biopsies", 0) or 0
                for site in cryobiopsy_sites
            )
            if total_biopsies:
                cryo["number_of_samples"] = total_biopsies

            # Get probe size (use first site's if uniform)
            probe_sizes = [
                site.get("probe_size_mm")
                for site in cryobiopsy_sites
                if site.get("probe_size_mm")
            ]
            if probe_sizes:
                cryo["cryoprobe_size_mm"] = probe_sizes[0]

            # Get freeze time (use first site's)
            freeze_times = [
                site.get("freeze_time_seconds")
                for site in cryobiopsy_sites
                if site.get("freeze_time_seconds")
            ]
            if freeze_times:
                cryo["freeze_time_seconds"] = freeze_times[0]

            # Get locations
            locations = [
                f"{site.get('lobe', '')} {site.get('segment', '')}".strip()
                for site in cryobiopsy_sites
                if site.get("lobe")
            ]
            if locations:
                cryo["locations"] = locations

            procedures["transbronchial_cryobiopsy"] = cryo

        # Clear incorrect transbronchial_biopsy.forceps_type = "Cryoprobe"
        tbbx = procedures.get("transbronchial_biopsy")
        if tbbx and tbbx.get("forceps_type") == "Cryoprobe":
            tbbx["forceps_type"] = None

    # ==========================================================================
    # 2. Derive radial_ebus.performed from navigation_targets
    # ==========================================================================
    navigation_targets = granular_data.get("navigation_targets", [])
    if navigation_targets:
        # Check if any target used radial EBUS
        any_rebus = any(
            target.get("rebus_used") or target.get("rebus_view")
            for target in navigation_targets
        )

        radial_ebus = procedures.get("radial_ebus") or {}
        if any_rebus and not radial_ebus.get("performed"):
            radial_ebus["performed"] = True
            # Get probe position from first target with a view
            for target in navigation_targets:
                if target.get("rebus_view"):
                    radial_ebus["probe_position"] = target["rebus_view"]
                    break
            procedures["radial_ebus"] = radial_ebus
        elif radial_ebus.get("probe_position") and not radial_ebus.get("performed"):
            # probe_position is set but performed is not - fix it
            radial_ebus["performed"] = True
            procedures["radial_ebus"] = radial_ebus
            warnings.append(
                "radial_ebus.probe_position was set but performed was null - auto-set performed=true"
            )

    # ==========================================================================
    # 3. Derive linear_ebus.stations_sampled from linear_ebus_stations_detail
    # ==========================================================================
    linear_ebus_detail = granular_data.get("linear_ebus_stations_detail", [])
    if linear_ebus_detail:
        linear_ebus = procedures.get("linear_ebus") or {}

        # Get sampled stations
        sampled_stations = [
            station.get("station")
            for station in linear_ebus_detail
            if station.get("sampled") is True or station.get("sampled") is None
        ]

        if sampled_stations and not linear_ebus.get("stations_sampled"):
            linear_ebus["stations_sampled"] = sampled_stations
            if not linear_ebus.get("performed"):
                linear_ebus["performed"] = True
            procedures["linear_ebus"] = linear_ebus

    # ==========================================================================
    # 4. Derive BAL, brushings from specimens_collected
    # ==========================================================================
    specimens = granular_data.get("specimens_collected", [])
    if specimens:
        # BAL
        bal_specimens = [
            s for s in specimens
            if s.get("source_procedure") in ("BAL", "Bronchoalveolar lavage", "mini-BAL")
        ]
        if bal_specimens:
            bal = procedures.get("bal") or {}
            if not bal.get("performed"):
                bal["performed"] = True
                # Get location from first BAL specimen
                for spec in bal_specimens:
                    loc = spec.get("source_location")
                    if loc and loc != "BAL":
                        bal["location"] = loc
                        break
                procedures["bal"] = bal

        # Brushings
        brushing_specimens = [
            s for s in specimens
            if s.get("source_procedure") == "Brushing"
        ]
        if brushing_specimens:
            brushings = procedures.get("brushings") or {}
            if not brushings.get("performed"):
                brushings["performed"] = True
                # Get locations
                locations = [
                    s.get("source_location")
                    for s in brushing_specimens
                    if s.get("source_location")
                ]
                if locations:
                    brushings["locations"] = locations
                # Count samples
                total_samples = sum(
                    s.get("specimen_count", 1) or 1
                    for s in brushing_specimens
                )
                brushings["number_of_samples"] = total_samples
                procedures["brushings"] = brushings

    # ==========================================================================
    # 5. Derive navigational_bronchoscopy.sampling_tools_used from navigation_targets
    # ==========================================================================
    if navigation_targets:
        nav_bronch = procedures.get("navigational_bronchoscopy") or {}
        existing_tools = nav_bronch.get("sampling_tools_used") or []

        if not existing_tools:
            # Collect all tools from all targets
            all_tools: set[str] = set()
            for target in navigation_targets:
                tools = target.get("sampling_tools_used", [])
                if tools:
                    for tool in tools:
                        # Normalize tool names
                        if "needle" in tool.lower():
                            all_tools.add("Needle")
                        elif "forceps" in tool.lower():
                            all_tools.add("Forceps")
                        elif "brush" in tool.lower():
                            all_tools.add("Brush")
                        elif "cryo" in tool.lower():
                            all_tools.add("Cryoprobe")
                        else:
                            all_tools.add(tool)

            if all_tools:
                nav_bronch["sampling_tools_used"] = list(all_tools)
                procedures["navigational_bronchoscopy"] = nav_bronch

    # ==========================================================================
    # 6. Derive outcomes.procedure_completed and complications
    # ==========================================================================
    # This is done at a higher level since outcomes is a separate top-level field

    # ==========================================================================
    # Validation warnings for inconsistencies
    # ==========================================================================

    # Check: cryobiopsy_sites present but transbronchial_cryobiopsy not set
    if cryobiopsy_sites:
        cryo_proc = procedures.get("transbronchial_cryobiopsy")
        if not cryo_proc or not cryo_proc.get("performed"):
            warnings.append(
                "granular_data.cryobiopsy_sites is populated but "
                "procedures_performed.transbronchial_cryobiopsy.performed was not set"
            )

    # Check: navigation_target.rebus_used but radial_ebus.performed not set
    if navigation_targets:
        any_rebus = any(
            target.get("rebus_used") or target.get("rebus_view")
            for target in navigation_targets
        )
        radial_ebus = procedures.get("radial_ebus")
        if any_rebus and (not radial_ebus or not radial_ebus.get("performed")):
            warnings.append(
                "navigation_targets has rebus_used=true but "
                "radial_ebus.performed was not set"
            )

    return procedures, warnings


__all__ = [
    "IPCProcedure",
    "ClinicalContext",
    "PatientDemographics",
    "AirwayStentProcedure",
    # Per-site models
    "EBUSStationDetail",
    "NavigationTarget",
    "CAOModalityApplication",
    "CAOInterventionDetail",
    "BLVRValvePlacement",
    "BLVRChartisMeasurement",
    "CryobiopsySite",
    "ThoracoscopyFinding",
    "SpecimenCollected",
    # Container
    "EnhancedRegistryGranularData",
    # Helpers
    "validate_ebus_consistency",
    "derive_aggregate_fields",
    "derive_procedures_from_granular",
]
