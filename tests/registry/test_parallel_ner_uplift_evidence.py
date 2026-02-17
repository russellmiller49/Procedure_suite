from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


@dataclass
class _StubPathwayResult:
    source: str
    codes: list[str]
    confidences: dict[str, float]
    processing_time_ms: float
    details: dict


@dataclass
class _StubParallelResult:
    path_a_result: _StubPathwayResult
    path_b_result: _StubPathwayResult
    final_codes: list[str]
    final_confidences: dict[str, float]
    needs_review: bool
    review_reasons: list[str]
    total_time_ms: float


class _StubParallelOrchestrator:
    def process(self, _note_text: str, ml_predictor=None):  # type: ignore[no-untyped-def]
        record = RegistryRecord()
        path_a = _StubPathwayResult(
            source="ner_rules",
            codes=[],
            confidences={},
            processing_time_ms=1.0,
            details={
                "record": record,
                "ner_entities": [],
                "ner_entity_count": 0,
                "stations_sampled_count": 0,
            },
        )
        path_b = _StubPathwayResult(
            source="ml_classification",
            codes=[],
            confidences={},
            processing_time_ms=1.0,
            details={},
        )
        return _StubParallelResult(
            path_a_result=path_a,
            path_b_result=path_b,
            final_codes=[],
            final_confidences={},
            needs_review=False,
            review_reasons=[],
            total_time_ms=2.0,
        )

    def _build_ner_evidence(self, _ner_entities):  # type: ignore[no-untyped-def]
        return {}


class _StubParallelOrchestratorWithRecord:
    def __init__(self, record: RegistryRecord) -> None:
        self._record = record

    def process(self, _note_text: str, ml_predictor=None):  # type: ignore[no-untyped-def]
        path_a = _StubPathwayResult(
            source="ner_rules",
            codes=[],
            confidences={},
            processing_time_ms=1.0,
            details={
                "record": self._record,
                "ner_entities": [],
                "ner_entity_count": 0,
                "stations_sampled_count": 0,
            },
        )
        path_b = _StubPathwayResult(
            source="ml_classification",
            codes=[],
            confidences={},
            processing_time_ms=1.0,
            details={},
        )
        return _StubParallelResult(
            path_a_result=path_a,
            path_b_result=path_b,
            final_codes=[],
            final_confidences={},
            needs_review=False,
            review_reasons=[],
            total_time_ms=2.0,
        )

    def _build_ner_evidence(self, _ner_entities):  # type: ignore[no-untyped-def]
        return {}


class _StubParallelOrchestratorWithReviewReason:
    def __init__(self, record: RegistryRecord, reason: str) -> None:
        self._record = record
        self._reason = reason

    def process(self, _note_text: str, ml_predictor=None):  # type: ignore[no-untyped-def]
        path_a = _StubPathwayResult(
            source="ner_rules",
            codes=[],
            confidences={},
            processing_time_ms=1.0,
            details={
                "record": self._record,
                "ner_entities": [],
                "ner_entity_count": 0,
                "stations_sampled_count": 0,
            },
        )
        path_b = _StubPathwayResult(
            source="ml_classification",
            codes=["31645"],
            confidences={"31645": 0.99},
            processing_time_ms=1.0,
            details={},
        )
        return _StubParallelResult(
            path_a_result=path_a,
            path_b_result=path_b,
            final_codes=["31645"],
            final_confidences={"31645": 0.95},
            needs_review=True,
            review_reasons=[self._reason],
            total_time_ms=2.0,
        )

    def _build_ner_evidence(self, _ner_entities):  # type: ignore[no-untyped-def]
        return {}


def test_parallel_ner_deterministic_uplift_adds_evidence_and_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
INDICATION FOR OPERATION: 74 year old female who presents with tracheal stenosis.

ANESTHESIA:
General Anesthesia

INSTRUMENT:
Flexible Therapeutic Bronchoscope

PROCEDURE:
31622 Dx bronchoscopy/cell washing

PROCEDURE IN DETAIL:
The airway was inspected. The vocal cords were normal appearing.
The previous tracheostomy site was noted. There were some secretions noted throughout the airway.
Some malacia noted.
""".strip()

    result = service.extract_fields(note_text)

    record = result.record
    assert record.procedures_performed is not None
    assert record.procedures_performed.diagnostic_bronchoscopy is not None
    assert record.procedures_performed.diagnostic_bronchoscopy.performed is True

    assert record.sedation is not None
    assert record.sedation.type == "General"

    assert record.clinical_context is not None
    assert record.clinical_context.primary_indication
    assert "tracheal stenosis" in record.clinical_context.primary_indication.lower()
    assert record.clinical_context.indication_category == "Stricture/Stenosis"

    evidence = record.evidence
    assert evidence, "expected evidence spans to be populated"
    assert any(key.startswith("procedures_performed.diagnostic_bronchoscopy.performed") for key in evidence.keys())
    assert "clinical_context.primary_indication" in evidence
    assert "sedation.type" in evidence
    assert "code_evidence" in evidence


def test_parallel_ner_deterministic_uplift_extracts_bronchus_sign_ecog_and_radial_view_with_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
INDICATION: Peripheral RLL nodule. CT review: bronchus sign was negative. ECOG 2.

ANESTHESIA:
General anesthesia

PROCEDURE IN DETAIL:
Radial EBUS showed concentric view of the lesion.
""".strip()

    result = service.extract_fields(note_text)
    record = result.record

    assert record.clinical_context is not None
    assert record.clinical_context.bronchus_sign == "Negative"
    assert record.clinical_context.ecog_score == 2

    assert record.procedures_performed is not None
    assert record.procedures_performed.radial_ebus is not None
    assert record.procedures_performed.radial_ebus.performed is True
    assert record.procedures_performed.radial_ebus.probe_position == "Concentric"

    evidence = record.evidence
    assert "clinical_context.bronchus_sign" in evidence
    assert "clinical_context.ecog_score" in evidence
    assert "procedures_performed.radial_ebus.probe_position" in evidence


def test_parallel_ner_nav_target_tier2_extracts_ct_characteristics_pleural_distance_suv_and_bronchus_sign_with_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
PROCEDURE IN DETAIL:
Ion robotic bronchoscopy was performed.
Target 1: RLL subsolid nodule with increasing density, 5 mm from pleura. Air bronchogram present. SUV max 4.2.
""".strip()

    result = service.extract_fields(note_text)
    record = result.record

    assert record.granular_data is not None
    targets = record.granular_data.navigation_targets or []
    assert targets, "expected navigation_targets to be populated"

    t0 = targets[0]
    assert t0.ct_characteristics == "Part-solid"
    assert t0.distance_from_pleura_mm == 5.0
    assert t0.pet_suv_max == 4.2
    assert t0.bronchus_sign == "Positive"

    evidence = record.evidence
    assert evidence, "expected evidence spans to be populated"
    assert "granular_data.navigation_targets.0.ct_characteristics" in evidence
    assert "granular_data.navigation_targets.0.distance_from_pleura_mm" in evidence
    assert "granular_data.navigation_targets.0.pet_suv_max" in evidence
    assert "granular_data.navigation_targets.0.bronchus_sign" in evidence


def test_parallel_ner_nav_target_tier2_extracts_registration_error_and_tool_in_lesion_with_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
PROCEDURE IN DETAIL:
Ion robotic bronchoscopy was performed.
Target 1: RLL solid nodule. Registration error 3 mm. Tool-in-lesion confirmed with CBCT.
""".strip()

    result = service.extract_fields(note_text)
    record = result.record

    assert record.granular_data is not None
    targets = record.granular_data.navigation_targets or []
    assert targets, "expected navigation_targets to be populated"

    t0 = targets[0]
    assert t0.registration_error_mm == 3.0
    assert t0.tool_in_lesion_confirmed is True
    assert t0.confirmation_method == "CBCT"
    assert t0.cbct_til_confirmed is True

    evidence = record.evidence
    assert evidence, "expected evidence spans to be populated"
    assert "granular_data.navigation_targets.0.registration_error_mm" in evidence
    assert "granular_data.navigation_targets.0.tool_in_lesion_confirmed" in evidence
    assert "granular_data.navigation_targets.0.confirmation_method" in evidence

    assert record.procedures_performed is not None
    assert record.procedures_performed.navigational_bronchoscopy is not None
    assert record.procedures_performed.navigational_bronchoscopy.tool_in_lesion_confirmed is True
    assert record.procedures_performed.navigational_bronchoscopy.confirmation_method == "CBCT"
    assert "procedures_performed.navigational_bronchoscopy.tool_in_lesion_confirmed" in evidence
    assert "procedures_performed.navigational_bronchoscopy.confirmation_method" in evidence


def test_parallel_ner_reconcile_complications_derives_nashville_bleeding_grade_with_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
PROCEDURE IN DETAIL:
There was moderate bleeding from biopsy sites. Bleeding controlled with suction, cold saline flushes, and endobronchial epinephrine.

COMPLICATIONS: None
""".strip()

    result = service.extract_fields(note_text)
    record = result.record

    assert record.complications is not None
    assert record.complications.bleeding is not None
    assert record.complications.bleeding.bleeding_grade_nashville == 2
    assert record.complications.any_complication is True
    assert "Bleeding - Moderate" in (record.complications.complication_list or [])

    assert "complications.bleeding.bleeding_grade_nashville" in record.evidence


def test_parallel_ner_reconcile_complications_derives_pneumothorax_intervention_with_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
PROCEDURE IN DETAIL:
Post-procedure small pneumothorax was noted. A pigtail catheter was placed.

COMPLICATIONS: None
""".strip()

    result = service.extract_fields(note_text)
    record = result.record

    assert record.complications is not None
    assert record.complications.pneumothorax is not None
    assert record.complications.pneumothorax.occurred is True
    assert record.complications.pneumothorax.intervention == ["Pigtail catheter"]

    evidence = record.evidence
    assert evidence, "expected evidence spans to be populated"
    assert "complications.pneumothorax.intervention" in evidence


def test_parallel_ner_ebus_station_detail_heuristics_adds_lymphocytes_present_with_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    note_text = """
PROCEDURE IN DETAIL:
Linear EBUS performed.
Station 11Rs: measured 12 x 8 mm by EBUS; biopsied with a 22-gauge needle, 4 passes. ROSE: adequate lymphocytes.
""".strip()

    result = service.extract_fields(note_text)
    record = result.record

    assert record.granular_data is not None
    details = record.granular_data.linear_ebus_stations_detail or []
    assert details, "expected linear_ebus_stations_detail to be populated"

    idx = next(i for i, d in enumerate(details) if str(getattr(d, "station", "")).upper() in {"11R", "11RS"})
    assert details[idx].lymphocytes_present is True
    assert details[idx].needle_gauge == 22
    assert details[idx].number_of_passes == 4
    assert details[idx].short_axis_mm == 8
    assert details[idx].long_axis_mm == 12

    evidence = record.evidence
    assert evidence, "expected evidence spans to be populated"
    assert f"granular_data.linear_ebus_stations_detail.{idx}.lymphocytes_present" in evidence
    assert f"granular_data.linear_ebus_stations_detail.{idx}.needle_gauge" in evidence
    assert f"granular_data.linear_ebus_stations_detail.{idx}.number_of_passes" in evidence
    assert f"granular_data.linear_ebus_stations_detail.{idx}.short_axis_mm" in evidence
    assert f"granular_data.linear_ebus_stations_detail.{idx}.long_axis_mm" in evidence


def test_parallel_ner_deterministic_uplift_upgrades_stent_action_to_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")

    base_record = RegistryRecord(
        procedures_performed={
            "airway_stent": {
                "performed": True,
                "action": "Removal",
                "action_type": "removal",
                "airway_stent_removal": True,
            }
        }
    )
    service = RegistryService(
        parallel_orchestrator=_StubParallelOrchestratorWithRecord(base_record)
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    def _seed_revision(_text: str):  # type: ignore[no-untyped-def]
        return {
            "procedures_performed": {
                "airway_stent": {
                    "performed": True,
                    "action": "Revision/Repositioning",
                    "action_type": "revision",
                    "airway_stent_removal": True,
                }
            }
        }

    monkeypatch.setattr(
        "app.registry.deterministic_extractors.run_deterministic_extractors",
        _seed_revision,
    )

    record, _warnings, _meta = service.extract_record(
        "Stent was removed and exchanged with a new stent."
    )
    stent = record.procedures_performed.airway_stent  # type: ignore[union-attr]

    assert stent is not None
    assert stent.action == "Revision/Repositioning"
    assert stent.action_type == "revision"
    assert stent.airway_stent_removal is True


def test_parallel_ner_filters_stale_ml_only_review_reasons_after_uplift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")

    service = RegistryService(
        parallel_orchestrator=_StubParallelOrchestratorWithReviewReason(
            RegistryRecord(),
            "31645: ML detected procedure, but specific device/anatomy was not found in text.",
        )
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)

    def _seed_aspiration(_text: str):  # type: ignore[no-untyped-def]
        return {"procedures_performed": {"therapeutic_aspiration": {"performed": True}}}

    monkeypatch.setattr(
        "app.registry.deterministic_extractors.run_deterministic_extractors",
        _seed_aspiration,
    )

    _record, warnings, _meta = service.extract_record(
        "Therapeutic aspiration of secretions was performed."
    )

    assert not any("31645: ML detected procedure" in w for w in warnings)
