"""Synthetic launch integrity tests; no clinical qualification is implied."""
# ruff: noqa: E402 -- Exercise the isolated packages without changing the installed application.

import hashlib
import sys
from pathlib import Path
from uuid import uuid4
import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]
from ip_registry_contracts.models import (
    ClinicalRevision,
    ExtractionRequest,
    approval_errors,
    read_clinical_revision,
)
from ip_registry_contracts.launch import Target, LocalizationEvent, SamplingAcquisition, FollowUp
from ip_registry_contracts.measures import launch_measures
from ip_registry_contracts.projection import project_national
from ip_registry_engine.engine import LocalDeterministicProvider


def revision(**values):
    return ClinicalRevision(
        event_date="2026-09-14",
        procedures=[
            {
                "category": "robotic_bronchoscopy",
                "performance": "attempted",
                "completion": "aborted_after_start",
            }
        ],
        **values,
    )


@pytest.mark.parametrize(
    "category",
    [
        "peripheral_bronchoscopy",
        "diagnostic_bronchoscopy",
        "radial_ebus",
        "eus_b",
        "robotic_ablation",
        "pleural",
        "blvr",
    ],
)
def test_unsupported_components_rejected(category):
    with pytest.raises(ValidationError):
        ClinicalRevision(
            event_date="2026-09-14", procedures=[{"category": category, "performance": "performed"}]
        )


def test_failed_attempt_eligible_unknown_requires_review_legacy_read_only():
    assert not approval_errors(revision())
    unknown = ClinicalRevision(
        event_date="2026-09-14", procedures=[{"category": "linear_ebus", "performance": "unknown"}]
    )
    assert approval_errors(unknown) == ["eligible_started_component_required"]
    legacy = read_clinical_revision(
        {
            "event_date": "2025-01-01",
            "procedures": [{"category": "blvr", "performance": "performed"}],
        }
    )
    assert legacy.procedures[0].category == "blvr"


@pytest.mark.parametrize("axis,modality", [(None, None), (False, "EBUS"), (True, None)])
def test_short_axis_must_be_explicit(axis, modality):
    with pytest.raises(ValidationError):
        Target(
            target_id=uuid4(),
            site="lymph_node",
            short_axis_mm=12,
            size_axis_explicit=axis,
            measurement_modality=modality,
        )


def test_aggregate_counts_cannot_create_individual_passes():
    with pytest.raises(ValidationError):
        SamplingAcquisition(
            sampling_pass_id=uuid4(),
            acquisition_record_granularity="aggregate_reported",
            reported_pass_count=6,
            pass_sequence_number=1,
        )


@pytest.mark.parametrize(
    "modality,component,actual",
    [
        ("radial_EBUS", "radial_probe", "actual_lesion"),
        ("mobile_CBCT", "catheter", "actual_lesion"),
        ("fixed_CBCT", "sampling_tool", "virtual_target"),
    ],
)
def test_til_requires_actual_sampling_tool(modality, component, actual):
    with pytest.raises(ValidationError):
        LocalizationEvent(
            localization_event_id=uuid4(),
            target_id=uuid4(),
            event_sequence_number=1,
            localization_modality=modality,
            tool_lesion_relationship="TIL",
            sampling_tool_present=True,
            verified_tool_component=component,
            actual_lesion_vs_virtual_target=actual,
            confirmation_basis="volumetric_imaging",
        )


def test_repositioning_invalidates_link_to_old_confirmation():
    target, event = uuid4(), uuid4()
    with pytest.raises(ValidationError, match="reconfirmation"):
        revision(
            targets=[{"target_id": target, "site": "lung"}],
            localization_events=[
                {
                    "localization_event_id": event,
                    "target_id": target,
                    "event_sequence_number": 1,
                    "localization_modality": "mobile_CBCT",
                    "catheter_or_tool_changed_after_confirmation": True,
                }
            ],
            sampling_acquisitions=[
                {
                    "sampling_pass_id": uuid4(),
                    "target_id": target,
                    "acquisition_record_granularity": "aggregate_reported",
                    "localization_event_id_before_pass": event,
                }
            ],
        )


def test_followup_never_fabricates_negative_and_longterm_excluded():
    assert FollowUp(window="days_8_30", complete=False).ed_visit == "not_documented"
    with pytest.raises(ValidationError):
        FollowUp(window="days_8_30", complete=False, ed_visit="absent")
    with pytest.raises(ValidationError):
        FollowUp(window="days_31_90", complete=True)


def test_target_outcomes_index_only_and_amended_history():
    a, b, sa, sb, p1, p2 = [uuid4() for _ in range(6)]
    values = revision(
        targets=[
            {
                "target_id": t,
                "site": "lung",
                "prespecified_biopsy_target": True,
                "diagnostic_attempted": True,
            }
            for t in (a, b)
        ],
        specimens=[
            {"specimen_id": s, "target_id": t, "target_attribution_status": "attributed"}
            for s, t in ((sa, a), (sb, b))
        ],
        pathology_results=[
            {
                "pathology_result_id": p1,
                "specimen_id": sa,
                "target_id": a,
                "result_scope": "index",
                "result_status": "final",
                "index_result_class": "nondiagnostic",
            },
            {
                "pathology_result_id": p2,
                "specimen_id": sa,
                "target_id": a,
                "result_scope": "index",
                "result_status": "amended",
                "index_result_class": "specific_malignant",
                "supersedes_pathology_result_id": p1,
            },
            {
                "pathology_result_id": uuid4(),
                "specimen_id": sb,
                "target_id": b,
                "result_scope": "followup",
                "result_status": "final",
                "index_result_class": "specific_malignant",
            },
        ],
    )
    metrics = launch_measures([values])
    assert metrics["strict_index_yield"] == {"numerator": 1, "denominator": 2, "rate": 0.5}
    assert metrics["counts"]["index_pending_or_unassessed"] == 1
    assert metrics["counts"]["cases_aborted"] == 1


def test_ambiguous_specimen_requires_attribution_before_target_result():
    t, s = uuid4(), uuid4()
    with pytest.raises(ValidationError, match="attributed_specimen"):
        revision(
            targets=[{"target_id": t, "site": "lung"}],
            specimens=[
                {"specimen_id": s, "target_id": t, "target_attribution_status": "mixed_target"}
            ],
            pathology_results=[
                {
                    "pathology_result_id": uuid4(),
                    "specimen_id": s,
                    "target_id": t,
                    "result_scope": "index",
                    "result_status": "final",
                }
            ],
        )


def test_projection_remaps_all_ids_and_rejects_narrative_in_national():
    t, s, p = uuid4(), uuid4(), uuid4()
    values = revision(
        case_details={
            "operator_id": uuid4(),
            "age_at_procedure_years": 96,
            "indication": "NARRATIVE_CANARY",
        },
        targets=[{"target_id": t, "site": "lung", "anatomic_label": "LOCAL_CANARY"}],
        specimens=[
            {
                "specimen_id": s,
                "target_id": t,
                "target_attribution_status": "attributed",
                "specimen_label": "SPECIMEN_CANARY",
            }
        ],
        pathology_results=[
            {
                "pathology_result_id": p,
                "specimen_id": s,
                "target_id": t,
                "result_scope": "index",
                "result_status": "final",
                "diagnosis_text": "DIAGNOSIS_CANARY",
            }
        ],
    )
    ids = {}

    def remap(namespace, value):
        return ids.setdefault((namespace, value), uuid4())

    national = project_national(
        values,
        remap=remap,
        patient_id=uuid4(),
        procedure_id=uuid4(),
        revision_number=1,
        facility_id=uuid4(),
        age_band="90_plus",
        profile_id=uuid4(),
        profile_version="0.2.0",
    )
    text = national.model_dump_json()
    assert "CANARY" not in text and "2026-09-14" not in text
    assert all(str(i) not in text for i in (t, s, p))
    assert national.pathology_results[0].target_id == national.targets[0].target_id
    with pytest.raises(ValidationError):
        type(national).model_validate({**national.model_dump(), "diagnosis_text": "NO"})
    with pytest.raises(ValidationError, match="safety_summary_conflicts"):
        type(national).model_validate(
            {
                **national.model_dump(),
                "complication_assessment": "absent",
                "complications": [
                    {
                        "category": "pneumothorax",
                        "state": "present",
                        "event_time_window": "immediate",
                    }
                ],
            }
        )


def extract(text, kind="procedure"):
    request = ExtractionRequest(
        job_id=uuid4(),
        source_document_id=uuid4(),
        text=text,
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        kind=kind,
    )
    return LocalDeterministicProvider().extract(request)


@pytest.mark.parametrize(
    "text",
    [
        "Nonrobotic electromagnetic navigation was performed for a RUL lesion.",
        "Radial EBUS was performed for a peripheral nodule.",
        "EUS-B-only examination was performed exclusively transesophageal.",
        "Robotic ablation was performed.",
        "History: Ion robotic bronchoscopy was performed last year. Today thoracentesis was performed.",
    ],
)
def test_outside_scope_no_eligible_proposal(text):
    assert extract(text).status == "unsupported"


def test_node_measurements_survey_sampling_and_evidence():
    text = "Linear EBUS was performed. Station 4R (12 mm) was sampled with 3 passes. Station 7 was visualized but not sampled."
    result = extract(text)
    assert result.status == "degraded" and "model_unavailable" in result.warnings
    value = ClinicalRevision(event_date="2026-09-14", **result.observations["proposal"])
    assert len(value.targets) == 1 and len(value.station_surveys) == 2
    assert value.targets[0].needle_pass_count == 3 and value.targets[0].short_axis_mm is None
    for evidence in value.field_provenance:
        if evidence.source_excerpt:
            assert text[evidence.source_start : evidence.source_end] == evidence.source_excerpt


def test_proposal_replay_ids_and_explicit_model_failure(tmp_path):
    text = "Ion robotic bronchoscopy was performed. The planned RUL lesion was reached."
    left, right = extract(text), extract(text)
    assert left.observations["proposal"]["targets"] == right.observations["proposal"]["targets"]
    bad = LocalDeterministicProvider(tmp_path)
    assert bad.model_error == "model_incompatible"


def test_local_inference_failure_is_explicit():
    class FailedModel:
        manifest = {}

        def predict(self, text):
            raise RuntimeError("synthetic inference failure")

    provider = LocalDeterministicProvider()
    provider.ner = FailedModel()
    text = "Linear EBUS was performed."
    request = ExtractionRequest(
        job_id=uuid4(),
        source_document_id=uuid4(),
        text=text,
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        kind="procedure",
    )
    result = provider.extract(request)
    assert result.status == "degraded"
    assert "model_inference_failed" in result.warnings
    assert result.observations["inference"]["ner_available"] is False


def test_known_safety_event_survives_incomplete_followup():
    from ip_registry_contracts.measures import launch_measures

    record = revision(
        follow_up=[{"window": "days_0_7", "complete": False, "procedure_related_event": "present"}]
    )
    counts = launch_measures([record])["counts"]
    assert counts["safety_30_day_incomplete"] == 1
    assert counts["safety_30_day_events"] == 1
    assert counts["safety_30_day_no_events"] == 0
    assert launch_measures([revision()])["counts"]["safety_30_day_outcome_unassessed"] == 1


def test_documented_complication_survives_missing_summaries_and_blocks_conflicting_approval():
    events = [
        {
            "category": "pneumothorax",
            "state": "present",
            "event_time_window": "immediate",
            "relatedness_to_procedure": "related",
        }
    ]
    record = revision(complications=events)
    counts = launch_measures([record])["counts"]
    assert counts["safety_immediate_present"] == 1
    assert counts["safety_immediate_unassessed"] == 0
    assert counts["safety_30_day_events"] == 1
    assert counts["safety_30_day_incomplete"] == 1
    assert not approval_errors(record)
    conflicting = revision(
        complications=events,
        complication_assessment="absent",
        follow_up=[{"window": "days_0_7", "complete": True, "procedure_related_event": "absent"}],
    )
    assert "immediate_safety_summary_conflicts_with_event" in approval_errors(conflicting)
    assert "followup_safety_summary_conflicts_with_event" in approval_errors(conflicting)


def test_uncertain_event_timing_or_relatedness_does_not_establish_30_day_outcome():
    events = [{"category": "infection", "state": "present", "event_time_window": "unknown"}]
    counts = launch_measures([revision(complications=events)])["counts"]
    assert counts["safety_30_day_events"] == 0
    assert counts["safety_30_day_outcome_unassessed"] == 1


def test_attributed_specimen_cannot_be_approved_with_negative_specimen_summary():
    target = uuid4()
    record = revision(
        targets=[{"target_id": target, "site": "lung", "specimen_obtained": False}],
        specimens=[
            {"specimen_id": uuid4(), "target_id": target, "target_attribution_status": "attributed"}
        ],
    )
    assert approval_errors(record) == ["specimen_summary_conflicts_with_attributed_specimen"]


def test_decimal_centimetres_and_lingula_preserve_original_evidence():
    text = (
        "Ion robotic bronchoscopy. The robotic catheter was introduced. "
        "The target was a 1.9 cm ground-glass lesion in the Lingula. "
        "Navigation proceeded to the target. Bronchus sign was positive."
    )
    result = extract(text).observations["proposal"]
    target = next(t for t in result["targets"] if t["site"] == "lung")
    assert target["max_diameter_mm"] == 19
    assert target["lobe"] == "Lingula"
    size = next(
        p for p in result["field_provenance"] if p["field_path"].endswith("/max_diameter_mm")
    )
    assert size["source_excerpt"] == "1.9 cm"
    assert text[size["source_start"] : size["source_end"]] == size["source_excerpt"]


def test_survey_then_sampling_enriches_station_without_duplicate_nodes_or_invented_axes():
    result = extract(
        "Linear EBUS was performed. Stations 4R (12.6 mm) and 11R (7.8 mm) were visualized. "
        "Station 4R: 4 passes. Station 11R: 3 passes. Station 4R: 4 passes."
    ).observations["proposal"]
    assert {s["iaslc_station"] for s in result["station_surveys"]} == {"4R", "11R"}
    assert {(t["iaslc_station"], t["needle_pass_count"]) for t in result["targets"]} == {
        ("4R", 4),
        ("11R", 3),
    }
    assert len(result["targets"]) == 2
    assert all(t.get("short_axis_mm") is None for t in result["targets"])
    assert all(s["station_sampled"] is True for s in result["station_surveys"])


def test_explicit_decimal_short_axis_and_grouped_counts_remain_distinct():
    result = extract(
        "Linear EBUS was performed. Station 4R short axis 12.6 mm: 3 passes. "
        "Stations 7 and 11R were sampled with 5 passes total."
    ).observations["proposal"]
    target = next(t for t in result["targets"] if t["iaslc_station"] == "4R")
    assert target["short_axis_mm"] == 12.6
    assert target["needle_pass_count"] == 3
    assert all(
        t.get("needle_pass_count") is None for t in result["targets"] if t["iaslc_station"] != "4R"
    )


def test_known_platform_requires_an_active_procedure_not_a_header():
    performed = extract(
        "The NOAH Galaxy navigation platform was used to register the airway map and guide "
        "the catheter to the target lesion. The target was a 2.1 cm RUL lesion."
    )
    assert performed.observations["proposal"]["procedures"][0]["category"] == "robotic_bronchoscopy"
    assert extract("Planned platform: Galaxy navigational bronchoscopy.").status == "unsupported"


def test_soft_pdf_wraps_and_station_x_counts_retain_source_offsets():
    text = (
        "Linear EBUS was performed. Surveyed stations included 11L (5.8 mm), 4L\n"
        "(6.4 mm), 7 (10.1 mm). Sampled stations: 11L x4 (ROSE); 4L x3 (ROSE); 7 x4 (ROSE)."
    )
    result = extract(text).observations["proposal"]
    assert {(t["iaslc_station"], t.get("needle_pass_count")) for t in result["targets"]} == {
        ("11L", 4),
        ("4L", 3),
        ("7", 4),
    }
    assert all(
        text[p["source_start"] : p["source_end"]] == p["source_excerpt"]
        for p in result["field_provenance"]
    )


def test_active_complication_overrides_negative_template_but_requires_conflict_review():
    text = (
        "Linear EBUS was performed.\nCOMPLICATIONS:\nBrief bronchospasm treated with bronchodilator.\n"
        "IMPRESSION:\nNo immediate complications."
    )
    proposal = extract(text).observations["proposal"]
    assert proposal["complication_assessment"] == "present"
    assert proposal["complications"][0]["category"] == "bronchospasm"
    assert "unresolved_field_conflict" in approval_errors(
        ClinicalRevision.model_validate({"event_date": "2026-09-14", **proposal})
    )
    negative = extract(
        "Linear EBUS was performed.\nCOMPLICATIONS:\nNo bronchospasm or bleeding requiring treatment.\n"
        "IMPRESSION:\nNo immediate complications."
    ).observations["proposal"]
    assert negative["complications"] == []
    assert negative["complication_assessment"] == "absent"


def test_contradictory_station_details_produce_reviewable_draft():
    proposal = extract(
        "Linear EBUS was performed. Station 4R was visualized only. Station 4R: 3 passes. Station 4R: 3 passes."
    ).observations["proposal"]
    value = ClinicalRevision.model_validate({"event_date": "2026-09-14", **proposal})
    assert "unresolved_field_conflict" in approval_errors(value)


def test_explicit_ebus_station_sampling_section_and_transesophageal_negative():
    text = "PROCEDURES\nConvex-probe EBUS-TBNA\nEBUS STAGING\nStation 4R: 3 needle passes."
    assert extract(text).observations["proposal"]["procedures"][0]["performance"] == "performed"
    assert (
        extract(
            text.replace("EBUS STAGING", "EBUS").replace("Station 4R", "stn level 4R")
        ).observations["proposal"]["procedures"][0]["performance"]
        == "performed"
    )
    assert extract(text.replace("3 needle passes", "not sampled")).status == "degraded"
    assert not any(
        p["performance"] == "performed"
        for p in extract(text + " EUS-B only.").observations["proposal"]["procedures"]
    )


def test_localization_excludes_header_summary_and_segment_name_is_not_second_target():
    text = (
        "**Procedures performed:** Galaxy robotic bronchoscopy with fixed CBCT.\n"
        "The robotic catheter was introduced. The target was a 24-mm LUL inferior lingular lesion. "
        "Mobile CBCT showed the lesion. rEBUS: concentirc signal.\n"
        "Impression: Confirmation incorporated fixed CBCT."
    )
    proposal = extract(text).observations["proposal"]
    assert [t["lobe"] for t in proposal["targets"]] == ["LUL"]
    assert {e["localization_modality"] for e in proposal["localization_events"]} == {
        "mobile_CBCT",
        "radial_EBUS",
    }
