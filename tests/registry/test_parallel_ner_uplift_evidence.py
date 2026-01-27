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
