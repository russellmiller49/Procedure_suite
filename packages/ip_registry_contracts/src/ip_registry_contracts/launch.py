"""Robotic/linear-EBUS launch entities. Nulls are observations, never defaults to no.

The national allowlist below is intentionally independent of model serialization.
Dates, narrative and source evidence belong exclusively to the clinical revision.
"""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, UUID4, create_model, model_validator

from .legacy_v1 import StrictModel, RecordedState

PROFILE = "robotic_ebus_v1"
VERSION = "0.2.0"
Number = Annotated[float, Field(ge=0, allow_inf_nan=False, strict=True)]
Count = Annotated[int, Field(ge=0, strict=True)]
ShortText = Annotated[str, Field(max_length=500)]
Narrative = Annotated[str, Field(max_length=4096)]
Station = Literal[
    "2R",
    "2L",
    "3A",
    "3P",
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
    "11Rs",
    "11Ri",
    "12R",
    "12L",
]
IndexResult = Literal[
    "specific_malignant",
    "specific_benign",
    "atypical_or_suspicious",
    "nonspecific_benign",
    "nondiagnostic",
    "pending",
    "unknown",
]
Modality = Literal[
    "radial_EBUS",
    "2D_fluoroscopy",
    "fixed_CBCT",
    "mobile_CBCT",
    "CBCT_unspecified",
    "digital_tomosynthesis",
    "augmented_fluoroscopy",
    "conventional_CT",
    "cone_beam_overlay",
    "other",
]
ToolRelation = Literal["TIL", "touching", "adjacent", "outside", "indeterminate", "not_applicable"]
MissingReason = Literal[
    "not_documented",
    "unknown",
    "not_done",
    "not_applicable",
    "pending",
    "technical_failure",
    "patient_declined",
    "not_available_at_site",
    "lost_to_followup",
]


class CaseDetails(StrictModel):
    operator_id: UUID4 | None = None
    age_at_procedure_years: Annotated[float, Field(ge=0, le=125, allow_inf_nan=False)] | None = None
    sex_at_birth: Literal["female", "male", "intersex", "unknown", "declined"] | None = None
    smoking_status: Literal["never", "former", "current", "unknown"] | None = None
    pack_years: Number | None = None
    indication: Narrative | None = None
    intent: (
        Literal[
            "diagnosis",
            "staging",
            "diagnosis_and_staging",
            "restaging",
            "molecular_rebiopsy",
            "other",
        ]
        | None
    ) = None
    asa_physical_status: Annotated[int, Field(ge=1, le=6)] | None = None
    anesthesia_type: Literal["general", "moderate", "deep", "local", "none", "other"] | None = None
    airway_device: (
        Literal["ETT", "LMA", "natural_airway", "tracheostomy", "rigid_bronchoscope", "other"]
        | None
    ) = None
    airway_size_value: Number | None = None
    airway_size_unit: Literal["mm", "LMA_size", "Fr", "other"] | None = None
    procedure_duration_minutes: Number | None = None
    immediate_disposition: (
        Literal["home", "recovery", "observation", "inpatient", "ICU", "other"] | None
    ) = None


class Target(StrictModel):
    target_id: UUID4
    site: Literal["lung", "lymph_node", "central_mass"]
    target_identity_id: UUID4 | None = None
    anatomic_label: ShortText | None = None
    lobe: Literal["RUL", "RML", "RLL", "LUL", "LLL", "Lingula"] | None = None
    segment: ShortText | None = None
    max_diameter_mm: Number | None = None
    lesion_attenuation_type: (
        Literal["solid", "part_solid", "ground_glass", "cavitary", "calcified", "other"] | None
    ) = None
    bronchus_sign_present: bool | None = None
    distance_to_pleura_mm: Number | None = None
    pet_avid: bool | None = None
    pet_suv_max: Number | None = None
    pet_description: ShortText | None = None
    prespecified_biopsy_target: bool | None = None
    diagnostic_attempted: bool | None = None
    sampling_attempted: bool | None = None
    specimen_obtained: bool | None = None
    reason_sampling_not_attempted: ShortText | None = None
    iaslc_station: Station | None = None
    station_survey_id: UUID4 | None = None
    ebus_session_id: UUID4 | None = None
    short_axis_mm: Number | None = None
    size_axis_explicit: bool | None = None
    measurement_modality: Literal["EBUS", "EUS_B"] | None = None
    puncture_route: Literal["EBUS", "EUS_B"] | None = None
    needle_pass_count: Count | None = None
    needle_gauge: Annotated[int, Field(ge=10, le=30)] | None = None
    rose_used: bool | None = None
    rose_result: Narrative | None = None
    rose_adequate: bool | None = None
    target_specimen_adequate: bool | None = None
    target_molecular_adequacy: bool | None = None
    benign_lymphoid_tissue_present: bool | None = None
    nodal_adequacy_basis: (
        Literal["lymphoid_material", "specific_diagnosis", "pathologist_assessment", "unknown"]
        | None
    ) = None
    node_interpretation: (
        Literal["malignant", "adequate_negative", "inadequate", "indeterminate", "pending"] | None
    ) = None

    @model_validator(mode="after")
    def measurement_axis(self):
        if self.short_axis_mm is not None and (
            self.size_axis_explicit is not True or self.measurement_modality is None
        ):
            raise ValueError("short_axis_requires_explicit_ultrasound_axis")
        if self.node_interpretation == "adequate_negative" and self.nodal_adequacy_basis not in {
            "lymphoid_material",
            "specific_diagnosis",
            "pathologist_assessment",
        }:
            raise ValueError("negative_node_requires_adequacy_basis")
        if (
            self.node_interpretation == "adequate_negative"
            and self.target_specimen_adequate is False
        ):
            raise ValueError("negative_node_conflicts_with_inadequate_specimen")
        return self


class EBUSSession(StrictModel):
    ebus_session_id: UUID4
    primary_purpose: (
        Literal[
            "initial_staging",
            "targeted_diagnosis",
            "restaging",
            "recurrence",
            "molecular_rebiopsy",
            "lymphoma",
            "sarcoidosis",
            "infection",
            "other",
        ]
        | None
    ) = None
    planned_sampling_strategy: Literal["systematic", "targeted", "other"] | None = None
    performed_sampling_strategy: Literal["systematic", "targeted", "other"] | None = None
    systematic_exam_complete: bool | None = None
    incomplete_exam_reason: ShortText | None = None
    eus_b_performed: bool | None = None
    rose_used: bool | None = None


class StationSurvey(StrictModel):
    station_survey_id: UUID4
    ebus_session_id: UUID4
    iaslc_station: Station
    survey_modality: Literal["EBUS", "EUS_B"] | None = None
    station_surveyed: bool | None = None
    station_visualized: bool | None = None
    station_sampled: bool | None = None
    reason_not_sampled: ShortText | None = None
    largest_short_axis_mm: Number | None = None
    size_axis_explicit: bool | None = None

    @model_validator(mode="after")
    def measurement_axis(self):
        if self.largest_short_axis_mm is not None and (
            self.size_axis_explicit is not True or self.survey_modality is None
        ):
            raise ValueError("short_axis_requires_explicit_ultrasound_axis")
        return self


class NavigationRun(StrictModel):
    navigation_run_id: UUID4
    target_id: UUID4
    run_sequence_number: Annotated[int, Field(ge=1)]
    platform_family: Literal["Ion", "Monarch", "Galaxy", "other", "unknown"] | None = None
    platform_manufacturer: ShortText | None = None
    platform_model: ShortText | None = None
    navigation_success_system_reported: bool | None = None
    target_reached_operational: bool | None = None
    navigation_failure_reason: ShortText | None = None
    navigation_run_outcome: (
        Literal[
            "reached_and_sampled",
            "reached_not_sampled",
            "not_reached_sampled_by_rescue",
            "not_reached_not_sampled",
            "aborted",
        ]
        | None
    ) = None


class LocalizationEvent(StrictModel):
    localization_event_id: UUID4
    target_id: UUID4
    navigation_run_id: UUID4 | None = None
    event_sequence_number: Annotated[int, Field(ge=1)]
    localization_modality: Modality
    event_phase: (
        Literal["initial", "correction", "prebiopsy", "post_sampling", "unknown"] | None
    ) = None
    radial_ebus_view: (
        Literal["concentric", "eccentric", "adjacent", "not_visualized", "indeterminate"] | None
    ) = None
    sampling_tool_present: bool | None = None
    lesion_visible: bool | None = None
    tool_lesion_relationship: ToolRelation | None = None
    actual_lesion_vs_virtual_target: (
        Literal["actual_lesion", "virtual_target", "unknown"] | None
    ) = None
    confirmation_basis: (
        Literal["volumetric_imaging", "tomosynthesis", "ultrasound", "fluoroscopy", "other"] | None
    ) = None
    verified_tool_component: (
        Literal[
            "sampling_tool",
            "needle_tip",
            "forceps",
            "cryoprobe",
            "catheter",
            "radial_probe",
            "unknown",
        ]
        | None
    ) = None
    position_correction_performed: bool | None = None
    catheter_or_tool_changed_after_confirmation: bool | None = None
    final_prebiopsy_confirmation: bool | None = None

    @model_validator(mode="after")
    def actual_tool_confirmation(self):
        if self.tool_lesion_relationship == "TIL" and (
            self.localization_modality
            not in {
                "fixed_CBCT",
                "mobile_CBCT",
                "CBCT_unspecified",
                "digital_tomosynthesis",
                "conventional_CT",
            }
            or self.actual_lesion_vs_virtual_target != "actual_lesion"
            or self.sampling_tool_present is not True
            or self.verified_tool_component
            not in {"sampling_tool", "needle_tip", "forceps", "cryoprobe"}
            or self.confirmation_basis not in {"volumetric_imaging", "tomosynthesis"}
        ):
            raise ValueError("til_requires_actual_sampling_tool_and_lesion_confirmation")
        return self


class SamplingAcquisition(StrictModel):
    sampling_pass_id: UUID4
    target_id: UUID4 | None = None
    acquisition_record_granularity: Literal["single_pass", "aggregate_reported"]
    pass_sequence_number: Annotated[int, Field(ge=1)] | None = None
    reported_pass_count: Count | None = None
    sampling_tool: (
        Literal[
            "aspiration_needle",
            "core_needle",
            "forceps",
            "mini_forceps",
            "brush",
            "curette",
            "cryoprobe",
            "BAL",
            "wash",
            "lavage_catheter",
            "other",
        ]
        | None
    ) = None
    needle_gauge: Annotated[int, Field(ge=10, le=30)] | None = None
    tool_size_mm: Number | None = None
    localization_event_id_before_pass: UUID4 | None = None
    rose_performed: bool | None = None
    rose_result: Narrative | None = None
    rose_adequate: bool | None = None
    attribution_status: Literal["attributed", "ambiguous", "unallocated"] = "unallocated"

    @model_validator(mode="after")
    def aggregate_integrity(self):
        if (
            self.acquisition_record_granularity == "aggregate_reported"
            and self.pass_sequence_number is not None
        ):
            raise ValueError("aggregate_cannot_claim_individual_pass")
        if (
            self.acquisition_record_granularity == "single_pass"
            and self.reported_pass_count not in {None, 1}
        ):
            raise ValueError("single_pass_count_must_be_one")
        if self.attribution_status == "attributed" and self.target_id is None:
            raise ValueError("attribution_requires_target")
        return self


class Specimen(StrictModel):
    specimen_id: UUID4
    target_id: UUID4 | None = None
    pathology: (
        Literal[
            "malignant",
            "benign",
            "atypical",
            "suspicious",
            "nondiagnostic",
            "pending",
            "unknown",
            "not_documented",
        ]
        | None
    ) = None
    specimen_label: ShortText | None = None
    specimen_type: (
        Literal["cytology", "histology", "microbiology", "flow_cytometry", "other"] | None
    ) = None
    container_medium: ShortText | None = None
    intended_purpose: ShortText | None = None
    target_attribution_status: Literal["attributed", "mixed_target", "ambiguous", "unallocated"] = (
        "unallocated"
    )

    @model_validator(mode="after")
    def attribution(self):
        if self.target_attribution_status == "attributed" and self.target_id is None:
            raise ValueError("attribution_requires_target")
        return self


class SamplingSpecimenLink(StrictModel):
    sampling_specimen_link_id: UUID4
    sampling_pass_id: UUID4
    specimen_id: UUID4
    link_certainty: Literal["confirmed", "uncertain"]
    allocation_purpose: ShortText | None = None


class PathologyResult(StrictModel):
    pathology_result_id: UUID4
    specimen_id: UUID4
    target_id: UUID4 | None = None
    result_scope: Literal["index", "followup"]
    result_status: Literal["preliminary", "final", "amended", "pending"]
    index_result_class: IndexResult | None = None
    diagnosis_text: Narrative | None = None
    adequate_for_primary_diagnosis: bool | None = None
    adequate_for_molecular_testing: bool | None = None
    lymphoid_material_adequacy: bool | None = None
    final_result_datetime: datetime | None = None
    supersedes_pathology_result_id: UUID4 | None = None
    source_document_id: UUID4 | None = None

    @model_validator(mode="after")
    def status_consistency(self):
        if self.result_status == "pending" and (
            self.index_result_class not in {None, "pending", "unknown"}
            or self.diagnosis_text is not None
        ):
            raise ValueError("pending_result_cannot_establish_diagnosis")
        if self.result_status == "amended" and self.supersedes_pathology_result_id is None:
            raise ValueError("amendment_requires_prior_result")
        return self


class Complication(StrictModel):
    category: Literal[
        "bleeding",
        "pneumothorax",
        "respiratory_failure",
        "infection",
        "unplanned_admission",
        "hypoxemia",
        "bronchospasm",
        "hypotension",
        "arrhythmia",
        "airway_displacement",
        "death",
        "other_approved",
    ]
    state: RecordedState
    adverse_event_id: UUID4 | None = None
    event_time_window: Literal["immediate", "days_0_7", "days_8_30", "unknown"] | None = None
    relative_day_offset: int | None = None
    severity_scale: ShortText | None = None
    severity_grade: ShortText | None = None
    event_treatment_summary: Narrative | None = None
    procedure_component_attribution: (
        Literal["robotic_bronchoscopy", "linear_ebus", "anesthesia", "combined", "unknown"] | None
    ) = None
    relatedness_to_procedure: (
        Literal["related", "possibly_related", "unrelated", "unknown"] | None
    ) = None
    pneumothorax_laterality: Literal["left", "right", "bilateral", "unknown"] | None = None
    pleural_intervention: bool | None = None
    new_hospital_admission: bool | None = None
    new_icu_admission: bool | None = None
    unplanned_ventilation: bool | None = None

    @model_validator(mode="after")
    def timing_consistency(self):
        if self.relative_day_offset is not None:
            limits = {"immediate": (0, 0), "days_0_7": (0, 7), "days_8_30": (8, 30)}
            if not 0 <= self.relative_day_offset <= 30:
                raise ValueError("event_outside_launch_followup")
            if (
                self.event_time_window in limits
                and not limits[self.event_time_window][0]
                <= self.relative_day_offset
                <= limits[self.event_time_window][1]
            ):
                raise ValueError("event_window_day_mismatch")
        return self


class FollowUp(StrictModel):
    window: Literal["days_0_7", "days_8_30"]
    complete: bool
    alive: RecordedState = RecordedState.unknown
    unplanned_admission: RecordedState = RecordedState.not_documented
    ed_visit: RecordedState = RecordedState.not_documented
    icu_admission: RecordedState = RecordedState.not_documented
    unplanned_ventilation: RecordedState = RecordedState.not_documented
    procedure_related_event: RecordedState = RecordedState.not_documented
    safety_ascertainment_status: (
        Literal["completed_no_events", "completed_events", "partial", "not_completed"] | None
    ) = None
    contact_datetime: datetime | None = None

    @model_validator(mode="after")
    def assessed_window(self):
        if (
            self.safety_ascertainment_status in {"completed_no_events", "completed_events"}
            and not self.complete
        ):
            raise ValueError("completed_assessment_requires_complete_window")
        if (
            self.safety_ascertainment_status == "completed_no_events"
            and self.procedure_related_event == RecordedState.present
        ):
            raise ValueError("conflicting_safety_assessment")
        if not self.complete and any(
            getattr(self, f) == RecordedState.absent
            for f in (
                "ed_visit",
                "unplanned_admission",
                "procedure_related_event",
                "icu_admission",
                "unplanned_ventilation",
            )
        ):
            raise ValueError("incomplete_window_cannot_establish_negative_outcomes")
        return self


class FieldProvenance(StrictModel):
    model_config = {**StrictModel.model_config, "str_strip_whitespace": False}
    field_path: Annotated[str, Field(max_length=500, pattern=r"^/")]
    source_document_id: UUID4 | None = None
    source_digest: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")] | None = None
    source_start: Count | None = None
    source_end: Count | None = None
    source_excerpt: Narrative | None = None
    raw_value: Narrative | None = None
    value_origin: Literal["extracted", "manual", "derived", "missing"]
    missingness_reason: MissingReason | None = None
    assertion_context: Literal["active", "negated", "planned", "historical", "uncertain"] | None = (
        None
    )
    conflict_status: Literal["none", "unresolved", "resolved"] = "none"
    review_status: Literal["proposed", "reviewed", "amended"] = "proposed"
    extractor_model_version: ShortText | None = None
    derivation_rule_version: ShortText | None = None

    @model_validator(mode="after")
    def evidence_completeness(self):
        evidence = (
            self.source_document_id,
            self.source_digest,
            self.source_start,
            self.source_end,
            self.source_excerpt,
        )
        if any(value is not None for value in evidence) and not all(
            value is not None for value in evidence
        ):
            raise ValueError("field_evidence_requires_complete_source_span")
        if self.source_end is not None and self.source_end <= self.source_start:
            raise ValueError("invalid_field_evidence_span")
        if self.value_origin == "extracted" and self.source_document_id is None:
            raise ValueError("extracted_field_requires_evidence")
        if self.value_origin == "missing" and self.missingness_reason is None:
            raise ValueError("missing_field_requires_reason")
        return self


ENTITY_MODELS = {
    "case_details": CaseDetails,
    "targets": Target,
    "ebus_sessions": EBUSSession,
    "station_surveys": StationSurvey,
    "navigation_runs": NavigationRun,
    "localization_events": LocalizationEvent,
    "sampling_acquisitions": SamplingAcquisition,
    "specimens": Specimen,
    "sampling_specimen_links": SamplingSpecimenLink,
    "pathology_results": PathologyResult,
    "complications": Complication,
    "follow_up": FollowUp,
}

# Explicit national destination list. Never infer this from a clinical model dump.
NATIONAL_ENTITY_FIELDS = {
    "case_details": (
        "sex_at_birth",
        "smoking_status",
        "pack_years",
        "intent",
        "asa_physical_status",
        "anesthesia_type",
        "airway_device",
        "airway_size_value",
        "airway_size_unit",
        "procedure_duration_minutes",
        "immediate_disposition",
    ),
    "targets": (
        "target_id",
        "site",
        "target_identity_id",
        "lobe",
        "max_diameter_mm",
        "lesion_attenuation_type",
        "bronchus_sign_present",
        "distance_to_pleura_mm",
        "pet_avid",
        "pet_suv_max",
        "prespecified_biopsy_target",
        "diagnostic_attempted",
        "sampling_attempted",
        "specimen_obtained",
        "iaslc_station",
        "station_survey_id",
        "ebus_session_id",
        "short_axis_mm",
        "size_axis_explicit",
        "measurement_modality",
        "puncture_route",
        "needle_pass_count",
        "needle_gauge",
        "rose_used",
        "rose_adequate",
        "target_specimen_adequate",
        "target_molecular_adequacy",
        "benign_lymphoid_tissue_present",
        "nodal_adequacy_basis",
        "node_interpretation",
    ),
    "ebus_sessions": (
        "ebus_session_id",
        "primary_purpose",
        "planned_sampling_strategy",
        "performed_sampling_strategy",
        "systematic_exam_complete",
        "eus_b_performed",
        "rose_used",
    ),
    "station_surveys": (
        "station_survey_id",
        "ebus_session_id",
        "iaslc_station",
        "survey_modality",
        "station_surveyed",
        "station_visualized",
        "station_sampled",
        "largest_short_axis_mm",
        "size_axis_explicit",
    ),
    "navigation_runs": (
        "navigation_run_id",
        "target_id",
        "run_sequence_number",
        "platform_family",
        "navigation_success_system_reported",
        "target_reached_operational",
        "navigation_run_outcome",
    ),
    "localization_events": (
        "localization_event_id",
        "target_id",
        "navigation_run_id",
        "event_sequence_number",
        "localization_modality",
        "event_phase",
        "radial_ebus_view",
        "sampling_tool_present",
        "lesion_visible",
        "tool_lesion_relationship",
        "actual_lesion_vs_virtual_target",
        "confirmation_basis",
        "verified_tool_component",
        "position_correction_performed",
        "catheter_or_tool_changed_after_confirmation",
        "final_prebiopsy_confirmation",
    ),
    "sampling_acquisitions": (
        "sampling_pass_id",
        "target_id",
        "acquisition_record_granularity",
        "pass_sequence_number",
        "reported_pass_count",
        "sampling_tool",
        "needle_gauge",
        "tool_size_mm",
        "localization_event_id_before_pass",
        "rose_performed",
        "rose_adequate",
        "attribution_status",
    ),
    "specimens": (
        "specimen_id",
        "target_id",
        "pathology",
        "specimen_type",
        "target_attribution_status",
    ),
    "sampling_specimen_links": (
        "sampling_specimen_link_id",
        "sampling_pass_id",
        "specimen_id",
        "link_certainty",
    ),
    "pathology_results": (
        "pathology_result_id",
        "specimen_id",
        "target_id",
        "result_scope",
        "result_status",
        "index_result_class",
        "adequate_for_primary_diagnosis",
        "adequate_for_molecular_testing",
        "lymphoid_material_adequacy",
        "supersedes_pathology_result_id",
    ),
    "complications": (
        "category",
        "state",
        "adverse_event_id",
        "event_time_window",
        "procedure_component_attribution",
        "relatedness_to_procedure",
        "pneumothorax_laterality",
        "pleural_intervention",
        "new_hospital_admission",
        "new_icu_admission",
        "unplanned_ventilation",
    ),
    "follow_up": (
        "window",
        "complete",
        "alive",
        "unplanned_admission",
        "ed_visit",
        "icu_admission",
        "unplanned_ventilation",
        "procedure_related_event",
        "safety_ascertainment_status",
    ),
}


def national_entity_model(name):
    """Build strict types from the declared allowlist, retaining field constraints."""
    source = ENTITY_MODELS[name]
    return create_model(
        "National" + source.__name__,
        __base__=StrictModel,
        **{
            key: (source.model_fields[key].annotation, source.model_fields[key])
            for key in NATIONAL_ENTITY_FIELDS[name]
        },
    )


NATIONAL_MODELS = {name: national_entity_model(name) for name in ENTITY_MODELS}


def validate_links(record):
    """Enforce encounter-local IDs; a station is not an individual-node identity."""
    indices = {}
    primary_keys = {
        "targets": "target_id",
        "ebus_sessions": "ebus_session_id",
        "station_surveys": "station_survey_id",
        "navigation_runs": "navigation_run_id",
        "localization_events": "localization_event_id",
        "sampling_acquisitions": "sampling_pass_id",
        "specimens": "specimen_id",
        "sampling_specimen_links": "sampling_specimen_link_id",
        "pathology_results": "pathology_result_id",
    }
    for collection, key in primary_keys.items():
        items = getattr(record, collection, [])
        index = {getattr(row, key): row for row in items}
        if len(index) != len(items):
            raise ValueError("duplicate_" + collection)
        indices[collection] = index
    references = {
        "target_id": "targets",
        "ebus_session_id": "ebus_sessions",
        "station_survey_id": "station_surveys",
        "navigation_run_id": "navigation_runs",
        "localization_event_id_before_pass": "localization_events",
        "specimen_id": "specimens",
        "sampling_pass_id": "sampling_acquisitions",
        "supersedes_pathology_result_id": "pathology_results",
    }
    for collection, index in indices.items():
        for row in index.values():
            for field, parent in references.items():
                if primary_keys[collection] == field:
                    continue
                value = getattr(row, field, None)
                if value is not None and value not in indices[parent]:
                    raise ValueError("unresolved_" + collection + "_" + field)
            if collection == "pathology_results":
                specimen = indices["specimens"][row.specimen_id]
                if row.target_id is not None and (
                    row.target_id != specimen.target_id
                    or specimen.target_attribution_status != "attributed"
                ):
                    raise ValueError("pathology_target_requires_attributed_specimen")
                visited = {row.pathology_result_id}
                ancestor = row.supersedes_pathology_result_id
                while ancestor is not None:
                    if ancestor in visited:
                        raise ValueError("pathology_supersession_cycle")
                    visited.add(ancestor)
                    prior = indices["pathology_results"][ancestor]
                    if prior.specimen_id != row.specimen_id:
                        raise ValueError("amendment_cannot_change_specimen")
                    ancestor = prior.supersedes_pathology_result_id
            if collection == "sampling_acquisitions" and row.localization_event_id_before_pass:
                event = indices["localization_events"][row.localization_event_id_before_pass]
                if row.target_id != event.target_id:
                    raise ValueError("sampling_localization_target_mismatch")
                if event.catheter_or_tool_changed_after_confirmation is True:
                    raise ValueError("sampling_requires_reconfirmation_after_tool_change")
            if collection == "sampling_specimen_links":
                acquisition = indices["sampling_acquisitions"][row.sampling_pass_id]
                specimen = indices["specimens"][row.specimen_id]
                if (
                    row.link_certainty == "confirmed"
                    and specimen.target_attribution_status == "attributed"
                    and acquisition.target_id != specimen.target_id
                ):
                    raise ValueError("sampling_specimen_target_mismatch")
            if (
                collection == "localization_events"
                and row.navigation_run_id
                and indices["navigation_runs"][row.navigation_run_id].target_id != row.target_id
            ):
                raise ValueError("navigation_localization_target_mismatch")
            if collection == "targets" and row.station_survey_id:
                station = indices["station_surveys"][row.station_survey_id]
                if station.iaslc_station != row.iaslc_station or (
                    row.ebus_session_id and station.ebus_session_id != row.ebus_session_id
                ):
                    raise ValueError("target_station_context_mismatch")
                if station.station_sampled is False and (
                    row.sampling_attempted is True
                    or row.needle_pass_count
                    or getattr(row, "rose_result", None)
                ):
                    raise ValueError("inspected_station_cannot_have_sampling_results")
    if len({f.window for f in record.follow_up}) != len(record.follow_up):
        raise ValueError("duplicate_follow_up_window")
    for collection, parent_key, sequence in (
        ("navigation_runs", "target_id", "run_sequence_number"),
        ("localization_events", "target_id", "event_sequence_number"),
    ):
        items = getattr(record, collection)
        if len({(getattr(row, parent_key), getattr(row, sequence)) for row in items}) != len(items):
            raise ValueError("duplicate_" + collection + "_sequence")
    superseded = [
        row.supersedes_pathology_result_id
        for row in record.pathology_results
        if row.supersedes_pathology_result_id
    ]
    if len(set(superseded)) != len(superseded):
        raise ValueError("branching_pathology_amendments_require_reconciliation")
    categories = {str(p.category) for p in record.procedures}
    if record.navigation_runs and "robotic_bronchoscopy" not in categories:
        raise ValueError("robotic_navigation_requires_robotic_component")
    if record.ebus_sessions and "linear_ebus" not in categories:
        raise ValueError("ebus_session_requires_linear_component")
    started = {
        str(p.category)
        for p in record.procedures
        if str(p.performance) in {"performed", "attempted"}
    }
    if record.navigation_runs and "robotic_bronchoscopy" not in started:
        raise ValueError("navigation_requires_started_robotic_component")
    if (
        any(s.station_surveyed is True or s.station_sampled is True for s in record.station_surveys)
        and "linear_ebus" not in started
    ):
        raise ValueError("station_survey_requires_started_linear_component")
    return record
