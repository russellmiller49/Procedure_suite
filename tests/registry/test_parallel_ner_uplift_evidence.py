from __future__ import annotations

from dataclasses import dataclass

import pytest

from modules.registry.application.registry_service import RegistryService
from modules.registry.schema import RegistryRecord


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
        "modules.registry.deterministic_extractors.run_deterministic_extractors",
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
        "modules.registry.deterministic_extractors.run_deterministic_extractors",
        _seed_aspiration,
    )

    _record, warnings, _meta = service.extract_record(
        "Therapeutic aspiration of secretions was performed."
    )

    assert not any("31645: ML detected procedure" in w for w in warnings)
