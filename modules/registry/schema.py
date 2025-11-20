"""Registry data structures and validation utilities."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from modules.common.spans import Span


ProviderRole = Literal["Attending", "Fellow", "Resident"]
Gender = Literal["M", "F", "Other"]
AnticoagStatus = Literal["None", "Aspirin", "Plavix", "DOAC", "Warfarin", "Heparin"]
PrimaryIndication = Literal[
    "Lung Nodule",
    "Lung Mass",
    "Mediastinal Lymphadenopathy",
    "Hemoptysis",
    "Airway Obstruction",
    "Pleural Effusion",
    "ILD",
    "COPD-Emphysema",
    "Asthma",
    "Foreign Body",
    "Other",
]
CaoLocation = Literal["None", "Trachea", "Mainstem", "Lobar"]
PriorTherapy = Literal["None", "Chemo", "Radiation", "Immunotherapy", "Prior Resection"]
SedationType = Literal["Moderate", "Deep", "General"]
AirwayType = Literal["Native", "LMA", "ETT", "Tracheostomy", "Rigid Bronchoscope"]
VentilationMode = Literal[
    "Spontaneous",
    "Jet Ventilation",
    "Controlled Mechanical Ventilation",
]
EbusScopeBrand = Literal["Olympus", "Pentax", "Fuji", "Other"]
EbusNeedleGauge = Literal["21G", "22G", "25G"]
EbusNeedleType = Literal["Standard", "FNB"]
EbusSystematicStaging = Literal["Yes", "No"]
EbusRoseResult = Literal["Malignant", "Benign", "Granuloma", "Nondiagnostic"]
NavPlatform = Literal[
    "Electromagnetic-SuperDimension",
    "Electromagnetic-Veran",
    "Robotic-Ion",
    "Robotic-Monarch",
    "Fluoroscopy Only",
]
NavRegistrationMethod = Literal["Automatic", "Manual"]
NavRebusView = Literal["Concentric", "Eccentric", "None"]
NavImagingVerification = Literal["Fluoroscopy", "Cone Beam CT", "O-Arm", "None"]
NavSamplingTool = Literal["Forceps", "Needle", "Brush", "Cryoprobe"]
CaoPrimaryModality = Literal[
    "Mechanical Core",
    "APC",
    "Electrocautery",
    "Cryotherapy",
    "Laser",
    "Microdebrider",
    "Photodynamic Therapy",
]
CaoTumorLocation = Literal["Trachea", "RMS", "LMS", "Bronchus Intermedius", "Lobar"]
StentType = Literal[
    "Silicone-Dumon",
    "Silicone-Y-Stent",
    "Hybrid",
    "Metallic-Covered",
    "Metallic-Uncovered",
]
StentDeploymentMethod = Literal["Rigid", "Flexible over Wire"]
StentLocation = Literal["Trachea", "Mainstem", "Lobar"]
BlvrTargetLobe = Literal["RUL", "RML", "RLL", "LUL", "LLL"]
BlvrCvAssessment = Literal["Chartis", "Visual", "CT-based"]
BlvrChartisResult = Literal["CV Negative", "CV Positive", "Indeterminate"]
BlvrValveType = Literal["Zephyr", "Spiration"]
ForeignBodyType = Literal["Organic", "Inorganic"]
PleuralProcedureType = Literal[
    "Thoracentesis",
    "Chest Tube",
    "Tunneled Catheter",
    "Medical Thoracoscopy",
]
PleuralGuidance = Literal["Ultrasound", "CT", "Blind"]
PleuralFluidAppearance = Literal["Serous", "Sanguinous", "Purulent", "Chylous"]
PleuralFinding = Literal["Adhesions", "Nodules", "Plaque", "Normal"]
PleurodesisAgent = Literal["Talc Slurry", "Talc Poudrage", "Doxycycline"]
BleedingSeverity = Literal["None/Scant", "Mild", "Moderate", "Severe"]
PneumothoraxIntervention = Literal[
    "Observation",
    "O2",
    "Aspiration",
    "Chest Tube",
    "Surgery",
]
HypoxiaRespiratoryFailure = Literal[
    "None",
    "Transient",
    "Escalation of Care",
    "Post-op Intubation",
]
FinalDiagnosisPrelim = Literal[
    "Malignancy",
    "Granulomatous",
    "Infectious",
    "Non-diagnostic",
    "Other",
]
Disposition = Literal[
    "Discharge Home",
    "PACU Recovery",
    "Floor Admission",
    "ICU Admission",
]
FollowUpPlan = Literal[
    "Clinic",
    "Oncology Referral",
    "Repeat Bronchoscopy",
    "Surveillance Imaging",
]


class RegistryRecord(BaseModel):
    """Structured registry payload matching the flat Supabase schema."""

    model_config = ConfigDict(extra="ignore")

    # Encounter & Demographics
    patient_mrn: str | None = None
    procedure_date: str | None = None
    provider_role: ProviderRole | None = None
    attending_name: str | None = None
    fellow_name: str | None = None
    patient_age: float | None = None
    gender: Gender | None = None
    asa_class: int | None = None
    anticoag_status: AnticoagStatus | None = None
    anticoag_held_preprocedure: bool | None = None

    # Indications & Pre-Op
    primary_indication: PrimaryIndication | None = None
    radiographic_findings: str | None = None
    lesion_size_mm: float | None = None
    lesion_location: str | None = None
    pet_suv_max: float | None = None
    pet_avid: bool | None = None
    bronchus_sign_present: bool | None = None
    cao_location: CaoLocation | None = None
    prior_therapy: PriorTherapy | None = None

    # Anesthesia
    sedation_type: SedationType | None = None
    airway_type: AirwayType | None = None
    airway_device_size: float | None = None
    ventilation_mode: VentilationMode | None = None
    anesthesia_agents: list[Literal[
        "Propofol",
        "Fentanyl",
        "Midazolam",
        "Rocuronium",
        "Succinylcholine",
        "Remifentanil",
        "Sevoflurane",
    ]] | None = None

    # Diagnostic (EBUS & Nav)
    ebus_scope_brand: EbusScopeBrand | None = None
    ebus_stations_sampled: list[str] | None = None
    ebus_needle_gauge: EbusNeedleGauge | None = None
    ebus_needle_type: EbusNeedleType | None = None
    ebus_systematic_staging: EbusSystematicStaging | None = None
    ebus_rose_available: bool | None = None
    ebus_rose_result: EbusRoseResult | None = None
    ebus_intranodal_forceps_used: bool | None = None

    nav_platform: NavPlatform | None = None
    nav_registration_method: NavRegistrationMethod | None = None
    nav_registration_error_mm: float | None = None
    nav_rebus_used: bool | None = None
    nav_rebus_view: NavRebusView | None = None
    nav_imaging_verification: NavImagingVerification | None = None
    nav_tool_in_lesion: bool | None = None
    nav_sampling_tools: list[NavSamplingTool] | None = None
    nav_cryobiopsy_for_nodule: bool | None = None

    # Therapeutics
    cao_primary_modality: CaoPrimaryModality | None = None
    cao_tumor_location: CaoTumorLocation | None = None
    cao_obstruction_pre_pct: int | None = None
    cao_obstruction_post_pct: int | None = None

    stent_type: StentType | None = None
    stent_deployment_method: StentDeploymentMethod | None = None
    stent_diameter_mm: float | None = None
    stent_length_mm: float | None = None
    stent_location: StentLocation | None = None

    blvr_target_lobe: BlvrTargetLobe | None = None
    blvr_cv_assessment_method: BlvrCvAssessment | None = None
    blvr_chartis_result: BlvrChartisResult | None = None
    blvr_valve_type: BlvrValveType | None = None
    blvr_number_of_valves: int | None = None

    fb_object_type: ForeignBodyType | None = None
    wll_volume_instilled_l: float | None = None

    # Pleural Procedures
    pleural_procedure_type: PleuralProcedureType | None = None
    pleural_guidance: PleuralGuidance | None = None
    pleural_opening_pressure_measured: bool | None = None
    pleural_fluid_appearance: PleuralFluidAppearance | None = None
    pleural_volume_drained_ml: float | None = None
    pleural_thoracoscopy_findings: list[PleuralFinding] | None = None
    pleurodesis_performed: bool | None = None
    pleurodesis_agent: PleurodesisAgent | None = None

    # Complications & Safety
    ebl_ml: float | None = None
    bleeding_severity: BleedingSeverity | None = None
    pneumothorax: bool | None = None
    pneumothorax_intervention: PneumothoraxIntervention | None = None
    hypoxia_respiratory_failure: HypoxiaRespiratoryFailure | None = None
    fluoro_time_min: float | None = None
    radiation_dap_gycm2: float | None = None

    # Diagnosis & Disposition
    final_diagnosis_prelim: FinalDiagnosisPrelim | None = None
    molecular_testing_requested: bool | None = None
    disposition: Disposition | None = None
    follow_up_plan: list[FollowUpPlan] | None = None

    # Metadata
    evidence: dict[str, list[Span]] = Field(default_factory=dict)
    version: str = "0.4.0"


__all__ = ["RegistryRecord"]
