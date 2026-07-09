from __future__ import annotations

from types import SimpleNamespace

from app.registry.aggregation.clinical.extract_clinical_update import extract_clinical_update_event
from app.registry.aggregation.imaging.extract_cxr import extract_cxr_event
from app.registry.aggregation.imaging.normalize import normalize_modality
from app.registry.aggregation.outcomes_rollup import (
    classify_diagnostic_yield,
    derive_longitudinal_outcomes,
    station_concordance_flags,
)
from app.registry.schema import RegistryRecord


# --- CXR / US extraction ------------------------------------------------------


def test_cxr_post_biopsy_pneumothorax_extracted() -> None:
    text = (
        "Portable chest radiograph obtained post-procedure following transbronchial biopsy. "
        "Small right apical pneumothorax, new compared to prior. Chest tube in satisfactory "
        "position. No pleural effusion."
    )
    payload = extract_cxr_event(text, relative_day_offset=0, event_subtype=None)
    snap = payload["imaging_snapshot"]
    assert snap["modality"] == "cxr"
    assert snap["subtype"] == "post_procedure"
    assert snap["pneumothorax"] is True
    assert snap["pneumothorax_side"] == "Right"
    assert snap["pneumothorax_trend"] == "New"
    assert snap["pleural_effusion"] is False
    assert snap["device_position_text"] is not None
    assert snap["response"] is None


def test_cxr_resolved_pneumothorax_and_effusion_trend() -> None:
    text = (
        "Follow-up chest x-ray. The previously seen pneumothorax has resolved. "
        "Small left pleural effusion, decreased from prior."
    )
    payload = extract_cxr_event(text, relative_day_offset=3, event_subtype="followup")
    snap = payload["imaging_snapshot"]
    assert snap["pneumothorax"] is False
    assert snap["pneumothorax_trend"] == "Resolved"
    assert snap["pleural_effusion"] is True
    assert snap["effusion_side"] == "Left"
    assert snap["effusion_trend"] == "Decreased"


def test_cxr_no_findings_flags_quality() -> None:
    payload = extract_cxr_event("Lungs clear.", relative_day_offset=1, event_subtype=None)
    assert "cxr_no_structured_findings" in payload["qa_flags"]


def test_modality_normalization() -> None:
    assert normalize_modality("Portable chest X-ray") == "cxr"
    assert normalize_modality("CXR") == "cxr"
    assert normalize_modality("PET/CT") == "pet_ct"
    assert normalize_modality("pleural ultrasound") == "us"
    assert normalize_modality("CT chest with contrast") == "ct"
    assert normalize_modality("") is None


def test_case_aggregator_routes_cxr_rows() -> None:
    from app.registry.application.case_aggregator import CaseAggregator

    row = SimpleNamespace(
        event_type="imaging",
        source_modality="portable chest x-ray",
        event_subtype=None,
        event_title="Post-procedure CXR",
        relative_day_offset=0,
        note_text="Post-procedure film. No pneumothorax. Lung re-expanded.",
        metadata_json={},
    )
    payload = CaseAggregator()._extract_event(row)  # noqa: SLF001
    assert payload["source_modality"] == "cxr"
    assert payload["imaging_snapshot"]["modality"] == "cxr"
    assert payload["imaging_snapshot"]["pneumothorax"] is False


# --- clinical follow-up hardening ----------------------------------------------


def test_clinical_update_ed_visit_readmission_and_types() -> None:
    text = (
        "Patient presented to the ED on post-procedure day 4 with hemoptysis and was "
        "readmitted for observation. CT showed a small pneumothorax."
    )
    payload = extract_clinical_update_event(text, update_type="clinical_update", relative_day_offset=4)
    update = payload["clinical_update"]
    assert update["ed_visit"] is True
    assert update["readmission"] is True
    assert update["hospital_admission"] is True
    assert "bleeding" in update["complication_types"]
    assert "pneumothorax" in update["complication_types"]


def test_clinical_update_negated_findings_not_extracted() -> None:
    text = (
        "Seen in clinic. No ED visits, no readmission. Denies hemoptysis. "
        "Prior pneumothorax resolved."
    )
    payload = extract_clinical_update_event(text, update_type="clinical_update", relative_day_offset=14)
    update = payload["clinical_update"]
    assert update["ed_visit"] is not True
    assert update["readmission"] is not True
    assert update["complication_types"] == []


# --- pathology diagnostic yield + concordance -----------------------------------


def test_classify_diagnostic_yield_categories() -> None:
    assert classify_diagnostic_yield("Adenocarcinoma of the lung, station 7") == "Malignant"
    assert classify_diagnostic_yield("Non-necrotizing granulomatous inflammation") == "Benign-specific"
    assert classify_diagnostic_yield("Scant cellularity, non-diagnostic specimen") == "Nondiagnostic"
    assert classify_diagnostic_yield("Negative for malignancy; benign bronchial cells") == "Benign-specific"
    assert classify_diagnostic_yield(None) is None


def test_station_concordance_flags_mismatch_both_directions() -> None:
    registry_json = {
        "procedures_performed": {"linear_ebus": {"stations_sampled": ["4R", "7"]}}
    }
    flags = station_concordance_flags(
        registry_json,
        [{"station": "7"}, {"station": "11L"}],
    )
    assert any(f.startswith("path_station_not_in_stations_sampled:11L") for f in flags)
    assert any(f.startswith("sampled_station_missing_from_path:4R") for f in flags)

    assert station_concordance_flags(registry_json, [{"station": "7"}, {"station": "4R"}]) == []
    assert station_concordance_flags({}, [{"station": "7"}]) == []


# --- longitudinal outcomes rollup ------------------------------------------------


def _snapshot_with_history() -> dict:
    return {
        "clinical_course": {
            "updates": [
                {
                    "relative_day_offset": 4,
                    "update_type": "complication",
                    "ed_visit": True,
                    "readmission": True,
                    "complication_types": ["bleeding"],
                },
                {
                    "relative_day_offset": 20,
                    "update_type": "clinical_update",
                    "deceased": True,
                },
            ]
        },
        "imaging_summary": {
            "followups": [
                {"relative_day_offset": 0, "modality": "cxr", "pneumothorax": True},
            ]
        },
        "pathology_results": {"final_diagnosis": "Adenocarcinoma, station 7"},
    }


def test_derive_longitudinal_outcomes_full_scenario() -> None:
    registry_json = _snapshot_with_history()
    rows = [SimpleNamespace(event_type="procedure_addendum", relative_day_offset=10)]
    changed, _flags = derive_longitudinal_outcomes(registry_json, event_rows=rows)
    assert changed is True
    block = registry_json["longitudinal_outcomes"]
    assert block["day30_complication"] is True
    assert block["day30_readmission"] is True
    assert block["day30_ed_visit"] is True
    assert block["day30_mortality"] is True
    assert block["survival_status"] == "Deceased"
    assert block["last_known_status_day_offset"] == 20
    assert block["diagnostic_yield"] == "Malignant"
    assert block["reintervention_within_30d"] is True
    assert set(block["complication_types"]) == {"bleeding", "pneumothorax"}


def test_derive_longitudinal_outcomes_respects_lock_and_noop() -> None:
    registry_json = _snapshot_with_history()
    changed, flags = derive_longitudinal_outcomes(
        registry_json,
        manual_overrides={"/longitudinal_outcomes": {"locked": True}},
    )
    assert changed is False
    assert "longitudinal_outcomes" not in registry_json
    assert "longitudinal_outcomes_locked" in flags

    empty: dict = {}
    changed, _ = derive_longitudinal_outcomes(empty)
    assert changed is False
    assert "longitudinal_outcomes" not in empty


def test_derive_longitudinal_outcomes_idempotent() -> None:
    registry_json = _snapshot_with_history()
    derive_longitudinal_outcomes(registry_json)
    changed_again, _ = derive_longitudinal_outcomes(registry_json)
    assert changed_again is False


# --- schema round-trips -----------------------------------------------------------


def test_registry_record_round_trips_longitudinal_sections() -> None:
    payload = {
        "imaging_summary": {
            "followups": [
                {
                    "relative_day_offset": 1,
                    "modality": "cxr",
                    "subtype": "post_procedure",
                    "pneumothorax": True,
                    "pneumothorax_side": "Right",
                    "pneumothorax_trend": "New",
                    "pleural_effusion": False,
                }
            ]
        },
        "clinical_course": {
            "updates": [
                {
                    "relative_day_offset": 4,
                    "update_type": "clinical_update",
                    "ed_visit": True,
                    "readmission": True,
                    "complication_types": ["bleeding"],
                }
            ]
        },
        "longitudinal_outcomes": {
            "day30_complication": True,
            "survival_status": "Alive",
            "diagnostic_yield": "Malignant",
            "complication_types": ["bleeding"],
        },
    }
    record = RegistryRecord.model_validate(payload)
    dumped = record.model_dump(exclude_none=True, mode="json")

    snap = dumped["imaging_summary"]["followups"][0]
    assert snap["modality"] == "cxr"
    assert snap["pneumothorax"] is True
    assert snap["pneumothorax_side"] == "Right"

    update = dumped["clinical_course"]["updates"][0]
    assert update["ed_visit"] is True
    assert update["readmission"] is True
    assert update["complication_types"] == ["bleeding"]

    outcomes = dumped["longitudinal_outcomes"]
    assert outcomes["day30_complication"] is True
    assert outcomes["diagnostic_yield"] == "Malignant"


def test_ip_v3_schema_round_trips_longitudinal_outcomes() -> None:
    from proc_schemas.registry.ip_v3 import IPRegistryV3

    entry = IPRegistryV3.model_validate(
        {
            "longitudinal_outcomes": {
                "day30_mortality": False,
                "survival_status": "Alive",
                "diagnostic_yield": "Benign-specific",
            }
        }
    )
    assert entry.longitudinal_outcomes.survival_status == "Alive"
    assert entry.longitudinal_outcomes.diagnostic_yield == "Benign-specific"


# --- per-specimen pathology yield ---------------------------------------------


def test_specimen_yields_from_station_specific_report() -> None:
    from app.registry.aggregation.pathology.specimen_yield import (
        best_yield_from_specimens,
        extract_specimen_yields,
    )

    text = open("tests/fixtures/case_events/path_ebus_station_specific_final_diagnosis.txt").read()
    out = extract_specimen_yields(text)
    by_station = {s["station"]: s for s in out["specimen_results"]}
    assert by_station["7"]["result_category"] == "Malignant"
    assert by_station["11RS"]["result_category"] == "Nondiagnostic"
    assert best_yield_from_specimens(out["specimen_results"]) == "Malignant"


def test_specimen_yields_modality_classification() -> None:
    from app.registry.aggregation.pathology.specimen_yield import extract_specimen_yields

    text = (
        "FINAL DIAGNOSIS\n"
        "A. Right lower lobe, transbronchial biopsy: Adenocarcinoma.\n"
        "B. Bronchial brushings: Negative for malignancy.\n"
        "C. Bronchial washing: Non-diagnostic, scant cellularity.\n"
        "D. Station 4R, EBUS-TBNA: Granulomatous inflammation.\n"
    )
    out = extract_specimen_yields(text)
    types = {s["specimen_label"]: s["specimen_type"] for s in out["specimen_results"]}
    cats = {s["specimen_label"]: s["result_category"] for s in out["specimen_results"]}
    assert types == {"A": "transbronchial_biopsy", "B": "brushing", "C": "washing", "D": "tbna"}
    assert cats["A"] == "Malignant"
    assert cats["C"] == "Nondiagnostic"
    assert cats["D"] == "Benign-specific"


def test_patch_pathology_results_merges_specimen_results_deduped() -> None:
    from app.registry.aggregation.pathology.patch_pathology_results import patch_pathology_results

    registry_json: dict = {}
    extracted = {
        "pathology_results_update": {"final_diagnosis": "Adenocarcinoma"},
        "specimen_results": [
            {"specimen_label": "A", "specimen_type": "tbna", "station": "7", "result_category": "Malignant"},
        ],
        "qa_flags": [],
    }
    changed, _ = patch_pathology_results(registry_json, extracted=extracted, manual_overrides=None)
    assert changed is True
    assert len(registry_json["pathology_results"]["specimen_results"]) == 1

    # Re-applying the same specimen does not duplicate.
    changed2, _ = patch_pathology_results(registry_json, extracted=extracted, manual_overrides=None)
    assert len(registry_json["pathology_results"]["specimen_results"]) == 1


def test_rollup_diagnostic_yield_falls_back_to_specimens() -> None:
    registry_json = {
        "pathology_results": {
            "specimen_results": [
                {"specimen_label": "A", "specimen_type": "washing", "result_category": "Nondiagnostic"},
                {"specimen_label": "B", "specimen_type": "tbna", "result_category": "Malignant"},
            ]
        },
        "clinical_course": {"updates": [{"relative_day_offset": 7, "update_type": "clinical_update"}]},
    }
    changed, _ = derive_longitudinal_outcomes(registry_json)
    assert changed is True
    assert registry_json["longitudinal_outcomes"]["diagnostic_yield"] == "Malignant"


def test_registry_record_round_trips_specimen_results() -> None:
    record = RegistryRecord.model_validate(
        {
            "pathology_results": {
                "final_diagnosis": "Adenocarcinoma",
                "specimen_results": [
                    {
                        "specimen_label": "A",
                        "specimen_type": "tbna",
                        "station": "7",
                        "result_category": "Malignant",
                        "diagnosis_text": "Adenocarcinoma",
                    }
                ],
            }
        }
    )
    dumped = record.model_dump(exclude_none=True, mode="json")
    assert dumped["pathology_results"]["specimen_results"][0]["specimen_type"] == "tbna"


# --- CXR LLM fallback trigger ----------------------------------------------------


def test_cxr_llm_fallback_triggers_only_without_structured_findings(monkeypatch) -> None:
    from app.registry.application import case_aggregator as ca

    monkeypatch.setattr(ca, "_should_attempt_llm_fallback", lambda: True)
    calls: list[str] = []

    def _fake_llm(note_text: str):
        calls.append(note_text)
        return {"pneumothorax": True, "pneumothorax_side": "Left"}

    monkeypatch.setattr(ca, "_llm_extract_cxr_findings", _fake_llm)

    row = SimpleNamespace(
        event_type="imaging",
        source_modality="cxr",
        event_subtype=None,
        event_title=None,
        relative_day_offset=1,
        note_text="Comparison study. Overall appearance is difficult to assess.",
        metadata_json={},
    )
    payload = ca.CaseAggregator()._extract_event(row)  # noqa: SLF001
    assert calls, "LLM fallback should run when deterministic extraction finds nothing"
    assert payload["imaging_snapshot"]["pneumothorax"] is True
    assert "llm_cxr_fallback" in payload["qa_flags"]

    # Structured deterministic findings suppress the fallback.
    calls.clear()
    row.note_text = "Small right pneumothorax, new. Chest tube in satisfactory position."
    payload = ca.CaseAggregator()._extract_event(row)
    assert not calls
    assert payload["imaging_snapshot"]["pneumothorax"] is True
    assert payload["imaging_snapshot"]["pneumothorax_side"] == "Right"
