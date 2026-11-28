"""Version 0.2 launch contracts; legacy readers do not authorize new writes."""

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal
from pydantic import Field, UUID4, create_model, model_validator
from .legacy_v1 import (
    StrictModel,
    RecordedState,
    PathologyCategory as PathologyCategory,
    Region,
    AgeBand,
    Permissions as Permissions,
    ParticipationPolicy as ParticipationPolicy,
    RecordReceipt as RecordReceipt,
    SubmissionReceipt as SubmissionReceipt,
    AnalyticalPopulation,
    DisclosurePolicy as DisclosurePolicy,
    Digest,
    Version,
    Evidence as LegacyEvidence,
    DeidentificationProfile as LegacyProfile,
)
from .launch import (
    PROFILE,
    VERSION,
    ENTITY_MODELS,
    NATIONAL_MODELS,
    CaseDetails,
    Target,
    EBUSSession,
    StationSurvey,
    NavigationRun,
    LocalizationEvent,
    SamplingAcquisition,
    Specimen,
    SamplingSpecimenLink,
    PathologyResult,
    Complication,
    FollowUp,
    FieldProvenance,
    validate_links,
)

CONTRACT_VERSION = VERSION


class Evidence(LegacyEvidence):
    model_config = {**StrictModel.model_config, "str_strip_whitespace": False}


class ProcedureCategory(StrEnum):
    robotic_bronchoscopy = "robotic_bronchoscopy"
    linear_ebus = "linear_ebus"


class Performance(StrEnum):
    performed = "performed"
    attempted = "attempted"
    not_performed = "not_performed"
    unknown = "unknown"
    not_documented = "not_documented"


class ProcedureEvent(StrictModel):
    category: ProcedureCategory
    performance: Performance
    planned: bool | None = None
    completion: (
        Literal["completed", "partially_completed", "aborted_after_start", "not_started", "unknown"]
        | None
    ) = None
    abort_reason: Annotated[str, Field(max_length=1000)] | None = None

    @model_validator(mode="after")
    def completion_consistency(self):
        if self.completion in {
            "completed",
            "partially_completed",
            "aborted_after_start",
        } and self.performance not in {Performance.performed, Performance.attempted}:
            raise ValueError("completion_requires_started_component")
        if self.completion == "not_started" and self.performance in {
            Performance.performed,
            Performance.attempted,
        }:
            raise ValueError("started_component_cannot_be_not_started")
        return self


class ClinicalRevision(StrictModel):
    schema_version: Literal["0.2.0"] = "0.2.0"
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE
    event_date: date
    procedures: list[ProcedureEvent] = Field(min_length=1, max_length=2)
    case_details: CaseDetails = Field(default_factory=CaseDetails)
    targets: list[Target] = Field(default_factory=list, max_length=100)
    ebus_sessions: list[EBUSSession] = Field(default_factory=list, max_length=10)
    station_surveys: list[StationSurvey] = Field(default_factory=list, max_length=100)
    navigation_runs: list[NavigationRun] = Field(default_factory=list, max_length=100)
    localization_events: list[LocalizationEvent] = Field(default_factory=list, max_length=300)
    sampling_acquisitions: list[SamplingAcquisition] = Field(default_factory=list, max_length=500)
    specimens: list[Specimen] = Field(default_factory=list, max_length=200)
    sampling_specimen_links: list[SamplingSpecimenLink] = Field(
        default_factory=list, max_length=500
    )
    pathology_results: list[PathologyResult] = Field(default_factory=list, max_length=500)
    complications: list[Complication] = Field(default_factory=list, max_length=100)
    follow_up: list[FollowUp] = Field(default_factory=list, max_length=2)
    complication_assessment: RecordedState = RecordedState.not_documented
    evidence: list[Evidence] = Field(default_factory=list, max_length=1000)
    field_provenance: list[FieldProvenance] = Field(default_factory=list, max_length=5000)
    suggested_codes: list[Annotated[str, Field(pattern=r"^[0-9]{5}$")]] = Field(
        default_factory=list, max_length=40
    )
    manual_fields: list[Annotated[str, Field(pattern=r"^[a-z_]+$", max_length=64)]] = Field(
        default_factory=list, max_length=50
    )

    @model_validator(mode="after")
    def relationships(self):
        if len({p.category for p in self.procedures}) != len(self.procedures):
            raise ValueError("duplicate_procedure_component")
        validate_links(self)
        scalar_values = {}
        for collection in [*ENTITY_MODELS, "procedures"]:
            entity = getattr(self, collection)
            rows = (
                [("/" + collection, entity)]
                if collection == "case_details"
                else [(f"/{collection}/{i}", row) for i, row in enumerate(entity)]
            )
            for prefix, row in rows:
                for field, value in row.model_dump().items():
                    path = prefix + "/" + field
                    scalar_values[path] = value
        scalar_values["/event_date"] = self.event_date
        scalar_values["/complication_assessment"] = self.complication_assessment
        paths = set()
        for provenance in self.field_provenance:
            if provenance.field_path not in scalar_values:
                raise ValueError("provenance_field_path_not_in_revision")
            if provenance.field_path in paths:
                raise ValueError("duplicate_field_provenance")
            paths.add(provenance.field_path)
            current = scalar_values[provenance.field_path]
            if provenance.value_origin == "missing" and current is not None:
                raise ValueError("filled_field_requires_updated_provenance")
            if current is None and provenance.missingness_reason is None:
                raise ValueError("null_field_requires_missingness_reason")
        for path, value in scalar_values.items():
            if value is None and path not in paths:
                self.field_provenance.append(
                    FieldProvenance(
                        field_path=path, value_origin="missing", missingness_reason="not_documented"
                    )
                )
        if len(self.field_provenance) > 5000:
            raise ValueError("field_provenance_capacity_exceeded")
        return self


def eligibility(value):
    return (
        "eligible"
        if any(
            p.performance in {Performance.performed, Performance.attempted}
            for p in value.procedures
        )
        else "needs_review"
    )


def approval_errors(value):
    errors = []
    if eligibility(value) != "eligible":
        errors.append("eligible_started_component_required")
    if any(p.conflict_status == "unresolved" for p in value.field_provenance):
        errors.append("unresolved_field_conflict")
    present_events = [c for c in value.complications if c.state == RecordedState.present]
    if value.complication_assessment == RecordedState.absent and any(
        c.event_time_window == "immediate" for c in present_events
    ):
        errors.append("immediate_safety_summary_conflicts_with_event")
    for window in value.follow_up:
        if (
            window.procedure_related_event == RecordedState.absent
            or window.safety_ascertainment_status == "completed_no_events"
        ) and any(
            c.relatedness_to_procedure == "related"
            and (
                c.event_time_window == window.window
                or (window.window == "days_0_7" and c.event_time_window == "immediate")
            )
            for c in present_events
        ):
            errors.append("followup_safety_summary_conflicts_with_event")
            break
    attributed_targets = {
        s.target_id for s in value.specimens if s.target_attribution_status == "attributed"
    }
    if any(
        t.specimen_obtained is False and t.target_id in attributed_targets for t in value.targets
    ):
        errors.append("specimen_summary_conflicts_with_attributed_specimen")
    return errors


NationalProcedureEvent = create_model(
    "NationalProcedureEvent",
    __base__=StrictModel,
    category=(ProcedureCategory, ...),
    performance=(Performance, ...),
    planned=(bool | None, None),
    completion=(
        Literal["completed", "partially_completed", "aborted_after_start", "not_started", "unknown"]
        | None,
        None,
    ),
)


class _NationalBase(StrictModel):
    schema_version: Literal["0.2.0"] = "0.2.0"
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE
    patient_export_id: UUID4
    procedure_export_id: UUID4
    revision: int = Field(ge=1)
    procedure_year: int = Field(ge=2000, le=2100)
    age_band: AgeBand
    facility_id: UUID4
    procedures: list[NationalProcedureEvent] = Field(min_length=1, max_length=2)
    complication_assessment: RecordedState
    quality: Literal["complete", "incomplete", "requires_reconciliation"]
    measure_version: Literal["0.2.0"] = "0.2.0"
    deidentification_profile_id: UUID4
    deidentification_profile_version: Version

    @model_validator(mode="after")
    def clinical_integrity(self):
        if eligibility(self) != "eligible":
            raise ValueError("eligible_started_component_required")
        clinical = {name: getattr(self, name) for name in ENTITY_MODELS}
        revision = ClinicalRevision(
            event_date=date(self.procedure_year, 1, 1),
            procedures=[p.model_dump() for p in self.procedures],
            complication_assessment=self.complication_assessment,
            **{
                name: (
                    [row.model_dump() for row in value]
                    if isinstance(value, list)
                    else value.model_dump()
                )
                for name, value in clinical.items()
            },
        )
        errors = approval_errors(revision)
        if errors:
            raise ValueError(",".join(errors))
        return self


NationalRegistryRecord = create_model(
    "NationalRegistryRecord",
    __base__=_NationalBase,
    **{
        name: (model, Field(default_factory=model))
        if name == "case_details"
        else (list[model], Field(default_factory=list, max_length=500))
        for name, model in NATIONAL_MODELS.items()
    },
)


class SubmissionManifest(StrictModel):
    batch_id: UUID4
    schema_version: Literal["0.2.0"] = "0.2.0"
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE
    software_version: Version
    policy_revision: int = Field(ge=1)
    deidentification_profile_id: UUID4
    deidentification_profile_version: Version
    payload_digest: Digest
    record_count: int = Field(ge=1, le=1000)


class SubmissionBatch(StrictModel):
    manifest: SubmissionManifest
    records: list[NationalRegistryRecord] = Field(min_length=1, max_length=1000)

    @model_validator(mode="before")
    @classmethod
    def explicit_launch_contract(cls, data):
        if isinstance(data, dict):
            for item in [data.get("manifest"), *(data.get("records") or [])]:
                if isinstance(item, dict) and (
                    item.get("schema_version") != VERSION or item.get("registry_profile") != PROFILE
                ):
                    raise ValueError("explicit_launch_contract_required")
        return data


class DeidentificationProfile(LegacyProfile):
    schema_version: Literal["0.2.0"] = "0.2.0"
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE
    approved_categories: list[ProcedureCategory] = Field(min_length=1, max_length=2)


class BenchmarkDefinition(StrictModel):
    measure_id: Literal["complication_rate", "robotic_ebus_launch"] = "complication_rate"
    version: Literal["0.2.0"] = "0.2.0"
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE
    population: AnalyticalPopulation
    year: int = Field(ge=2000, le=2100)
    region: Region | None = None
    adjustment: Literal["unadjusted"] = "unadjusted"

    @model_validator(mode="after")
    def region_usage(self):
        if (self.population == AnalyticalPopulation.regional) != (self.region is not None):
            raise ValueError("region_required_only_for_regional_comparison")
        return self


class ExtractionRequest(StrictModel):
    model_config = {**StrictModel.model_config, "str_strip_whitespace": False}
    job_id: UUID4
    source_document_id: UUID4
    source_digest: Digest
    text: str = Field(min_length=1, max_length=1_000_000)
    kind: Literal["procedure", "imaging", "pathology", "clinical_update"]
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE


class ExtractionResponse(StrictModel):
    job_id: UUID4
    source_digest: Digest
    engine_version: Literal["0.2.0"] = "0.2.0"
    status: Literal["proposed", "degraded", "unsupported"]
    registry_profile: Literal["robotic_ebus_v1"] = PROFILE
    observations: dict
    warnings: list[
        Literal[
            "requires_clinical_review",
            "full_procedure_engine_unqualified",
            "model_unavailable",
            "model_incompatible",
            "model_inference_failed",
            "outside_launch_scope",
            "eligibility_requires_review",
            "unresolved_target_attribution",
        ]
    ]


def read_clinical_revision(payload):
    """History only. Call ClinicalRevision directly at every write boundary."""
    if payload.get("schema_version", "0.1.0") == "0.1.0":
        from .legacy_v1 import ClinicalRevision as LegacyRevision

        return LegacyRevision.model_validate(payload)
    return ClinicalRevision.model_validate(payload)


def read_national_record(payload):
    if payload.get("schema_version") == "0.1.0":
        from .legacy_v1 import NationalRegistryRecord as LegacyRecord

        return LegacyRecord.model_validate(payload)
    return NationalRegistryRecord.model_validate(payload)
