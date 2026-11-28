"""Explicit clinical and national contracts; national payloads have no narrative fields."""
from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, UUID4, model_validator

CONTRACT_VERSION = "0.1.0"
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Version = Annotated[str, Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", max_length=24)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)


class RecordedState(StrEnum):
    present = "present"
    absent = "absent"
    unknown = "unknown"
    not_documented = "not_documented"


class ProcedureCategory(StrEnum):
    diagnostic_bronchoscopy = "diagnostic_bronchoscopy"
    linear_ebus = "linear_ebus"
    peripheral_bronchoscopy = "peripheral_bronchoscopy"
    therapeutic_bronchoscopy = "therapeutic_bronchoscopy"
    blvr = "blvr"
    pleural = "pleural"
    airway_access = "airway_access"
    other_approved = "other_approved"


class Performance(StrEnum):
    performed = "performed"
    not_performed = "not_performed"
    unknown = "unknown"
    not_documented = "not_documented"


class PathologyCategory(StrEnum):
    malignant = "malignant"
    benign = "benign"
    atypical = "atypical"
    suspicious = "suspicious"
    nondiagnostic = "nondiagnostic"
    pending = "pending"
    unknown = "unknown"
    not_documented = "not_documented"


class ComplicationCategory(StrEnum):
    bleeding = "bleeding"
    pneumothorax = "pneumothorax"
    respiratory_failure = "respiratory_failure"
    infection = "infection"
    unplanned_admission = "unplanned_admission"
    other_approved = "other_approved"


class Region(StrEnum):
    northeast = "northeast"
    midwest = "midwest"
    south = "south"
    west = "west"


class TargetSite(StrEnum):
    lymph_node = "lymph_node"
    lung = "lung"
    airway = "airway"
    pleura = "pleura"
    other_approved = "other_approved"


class Target(StrictModel):
    target_id: UUID4
    site: TargetSite


class Specimen(StrictModel):
    specimen_id: UUID4
    target_id: UUID4
    pathology: PathologyCategory = PathologyCategory.pending


class ProcedureEvent(StrictModel):
    category: ProcedureCategory
    performance: Performance


class Complication(StrictModel):
    category: ComplicationCategory
    state: RecordedState


class FollowUpWindow(StrEnum):
    days_0_7 = "days_0_7"
    days_8_30 = "days_8_30"
    days_31_90 = "days_31_90"
    days_91_365 = "days_91_365"


class FollowUp(StrictModel):
    window: FollowUpWindow
    complete: bool
    alive: RecordedState = RecordedState.unknown
    unplanned_admission: RecordedState = RecordedState.not_documented


class Evidence(StrictModel):
    source_document_id: UUID4
    source_digest: Digest
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str = Field(min_length=1, max_length=4096)
    confidence: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def valid_span(self):
        if self.end <= self.start:
            raise ValueError("invalid evidence span")
        return self


class ClinicalRevision(StrictModel):
    event_date: date
    procedures: list[ProcedureEvent] = Field(min_length=1, max_length=30)
    targets: list[Target] = Field(default_factory=list, max_length=100)
    specimens: list[Specimen] = Field(default_factory=list, max_length=100)
    complications: list[Complication] = Field(default_factory=list, max_length=30)
    follow_up: list[FollowUp] = Field(default_factory=list, max_length=4)
    complication_assessment: RecordedState = RecordedState.not_documented
    evidence: list[Evidence] = Field(default_factory=list, max_length=300)
    suggested_codes: list[Annotated[str, Field(pattern=r"^[0-9]{5}$")]] = Field(default_factory=list, max_length=40)
    manual_fields: list[Annotated[str, Field(pattern=r"^[a-z_]+$", max_length=64)]] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def relationships(self):
        targets = {t.target_id for t in self.targets}
        if len(targets) != len(self.targets):
            raise ValueError("duplicate targets")
        if any(s.target_id not in targets for s in self.specimens):
            raise ValueError("specimen target requires reconciliation")
        if len({s.specimen_id for s in self.specimens}) != len(self.specimens):
            raise ValueError("duplicate specimens")
        if len({f.window for f in self.follow_up}) != len(self.follow_up):
            raise ValueError("duplicate follow-up windows")
        return self


class AgeBand(StrEnum):
    under_18 = "under_18"
    age_18_39 = "18_39"
    age_40_49 = "40_49"
    age_50_59 = "50_59"
    age_60_69 = "60_69"
    age_70_79 = "70_79"
    age_80_89 = "80_89"
    age_90_plus = "90_plus"
    unknown = "unknown"


class NationalRegistryRecord(StrictModel):
    schema_version: Literal["0.1.0"] = "0.1.0"
    patient_export_id: UUID4
    procedure_export_id: UUID4
    revision: int = Field(ge=1)
    procedure_year: int = Field(ge=2000, le=2100)
    age_band: AgeBand
    # Administrative facility ID is assigned by the national directory, never an EHR ID.
    facility_id: UUID4
    procedures: list[ProcedureEvent] = Field(min_length=1, max_length=30)
    targets: list[Target] = Field(default_factory=list, max_length=100)
    specimens: list[Specimen] = Field(default_factory=list, max_length=100)
    complications: list[Complication] = Field(default_factory=list, max_length=30)
    complication_assessment: RecordedState
    follow_up: list[FollowUp] = Field(default_factory=list, max_length=4)
    quality: Literal["complete", "incomplete", "requires_reconciliation"]
    measure_version: Version
    deidentification_profile_id: UUID4
    deidentification_profile_version: Version

    @model_validator(mode="after")
    def relationships(self):
        ClinicalRevision(event_date=date(self.procedure_year, 1, 1), procedures=self.procedures,
                         targets=self.targets, specimens=self.specimens, complications=self.complications,
                         follow_up=self.follow_up, complication_assessment=self.complication_assessment)
        return self


class Permissions(StrictModel):
    national_contribution: bool = False
    institutional_benchmarking: bool = False
    regional_comparisons: bool = False
    named_participant_reporting: Literal[False] = False
    public_reporting: Literal[False] = False
    secondary_research_releases: Literal[False] = False
    development_model_training_reuse: Literal[False] = False

    def intersect(self, national: "Permissions") -> "Permissions":
        return Permissions(**{k: bool(v and national.model_dump()[k]) for k, v in self.model_dump().items()})


class ParticipationPolicy(StrictModel):
    institution_id: UUID4
    revision: int = Field(ge=1)
    effective_at: datetime
    authorized_by: UUID4
    authorization_reference: UUID4
    permissions: Permissions


class SubmissionManifest(StrictModel):
    batch_id: UUID4
    schema_version: Literal["0.1.0"] = "0.1.0"
    software_version: Version
    policy_revision: int = Field(ge=1)
    deidentification_profile_id: UUID4
    deidentification_profile_version: Version
    payload_digest: Digest
    record_count: int = Field(ge=1, le=1000)


class SubmissionBatch(StrictModel):
    manifest: SubmissionManifest
    records: list[NationalRegistryRecord] = Field(min_length=1, max_length=1000)


class RecordReceipt(StrictModel):
    procedure_export_id: UUID4
    revision: int
    outcome: Literal["accepted", "duplicate", "superseded"]


class SubmissionReceipt(StrictModel):
    batch_id: UUID4
    payload_digest: Digest
    records: list[RecordReceipt]


class AnalyticalPopulation(StrEnum):
    national = "national_descriptive"
    institutional = "institutional_benchmark"
    regional = "regional_comparison"


class BenchmarkDefinition(StrictModel):
    measure_id: Literal["complication_rate"] = "complication_rate"
    version: Version = "0.1.0"
    population: AnalyticalPopulation
    year: int = Field(ge=2000, le=2100)
    region: Region | None = None
    adjustment: Literal["unadjusted"] = "unadjusted"

    @model_validator(mode="after")
    def region_usage(self):
        if (self.population == AnalyticalPopulation.regional) != (self.region is not None):
            raise ValueError("region required only for regional comparison")
        return self


class DisclosurePolicy(StrictModel):
    version: Version = "0.1.0"
    small_cell_max: int = Field(default=10, ge=10)
    minimum_rate_denominator: int = Field(default=30, ge=30)
    minimum_other_institutions: int = Field(default=5, ge=5)
    minimum_regional_institutions: int = Field(default=6, ge=6)
    maximum_institution_fraction: float = Field(default=0.4, gt=0, le=0.4)


class DeidentificationProfile(StrictModel):
    profile_id: UUID4
    version: Version
    schema_version: Literal["0.1.0"] = "0.1.0"
    environment: Literal["synthetic", "clinical"]
    recipient: Literal["aabip_national"] = "aabip_national"
    valid_from: datetime
    expires_at: datetime
    approval_reference: UUID4
    approved_categories: list[ProcedureCategory] = Field(min_length=1)
    # Until a qualified expert approves a detailed combination review, records are held.
    requires_case_release: Literal[True] = True


class ExtractionRequest(StrictModel):
    job_id: UUID4
    source_document_id: UUID4
    source_digest: Digest
    text: str = Field(min_length=1, max_length=1_000_000)
    kind: Literal["pathology", "clinical_update"]


class ExtractionResponse(StrictModel):
    job_id: UUID4
    source_digest: Digest
    engine_version: Version
    status: Literal["proposed", "unsupported"]
    # Hospital-local engine observations may contain text. This is NEVER a national contract.
    observations: dict
    warnings: list[Literal["requires_clinical_review", "full_procedure_engine_unqualified"]]
