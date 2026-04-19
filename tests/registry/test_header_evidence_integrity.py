from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


@dataclass
class _StubPathwayResult:
    source: str
    codes: list[str] = field(default_factory=list)
    confidences: dict[str, float] = field(default_factory=dict)
    rationales: dict[str, str] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class _StubParallelResult:
    final_codes: list[str]
    final_confidences: dict[str, float]
    path_a_result: _StubPathwayResult
    path_b_result: _StubPathwayResult
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
    explanations: dict[str, str] = field(default_factory=dict)
    total_time_ms: float = 0.0


class _StubParallelOrchestrator:
    def process(self, note_text: str, ml_predictor: object | None = None) -> _StubParallelResult:  # noqa: ARG002
        record = RegistryRecord()
        details = {
            "record": record,
            "ner_entities": [],
            "ner_entity_count": 0,
            "stations_sampled_count": 0,
        }
        return _StubParallelResult(
            final_codes=[],
            final_confidences={},
            path_a_result=_StubPathwayResult(source="ner_rules", details=details),
            path_b_result=_StubPathwayResult(source="ml_classification"),
            needs_review=False,
            review_reasons=[],
            explanations={},
            total_time_ms=0.0,
        )

    def _build_ner_evidence(self, ner_entities: object | None) -> dict[str, list[object]]:  # noqa: ARG002
        return {}


@pytest.fixture
def _service(monkeypatch: pytest.MonkeyPatch) -> RegistryService:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    service = RegistryService(parallel_orchestrator=_StubParallelOrchestrator())
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)
    return service


def test_header_hints_do_not_become_primary_billing_evidence(_service: RegistryService) -> None:
    note_text = (
        "PROCEDURE:\n"
        "31646 Therapeutic aspiration subsequent episodes\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "Successful therapeutic aspiration was performed to clear mucus from the trachea.\n"
    )

    result = _service.extract_fields(note_text)
    record = result.record

    assert "31646" in (result.cpt_codes or [])
    assert record.evidence is not None
    assert record.evidence.get("header_code_hints")
    assert not any(
        str(span.get("text") if isinstance(span, dict) else getattr(span, "text", ""))
        == "31646"
        for span in (record.evidence.get("code_evidence") or [])
    )

    billing_codes = (record.billing or {}).get("cpt_codes") if isinstance(record.billing, dict) else record.billing.cpt_codes
    assert billing_codes
    code_31646 = next(item for item in billing_codes if str(item.get("code") if isinstance(item, dict) else item.code) == "31646")
    evidence_items = code_31646.get("evidence") if isinstance(code_31646, dict) else code_31646.evidence
    assert evidence_items
    assert all(item.get("text") != "31646" for item in evidence_items if isinstance(item, dict))

    coding_support = record.coding_support or {}
    coding_summary = coding_support.get("coding_summary") if isinstance(coding_support, dict) else getattr(coding_support, "coding_summary", {})
    lines = coding_summary.get("lines") if isinstance(coding_summary, dict) else getattr(coding_summary, "lines", [])
    line_31646 = next(item for item in (lines or []) if str(item.get("code") if isinstance(item, dict) else item.code) == "31646")
    note_spans = line_31646.get("note_spans") if isinstance(line_31646, dict) else line_31646.note_spans
    assert note_spans
    assert all(span.get("snippet") != "31646" for span in note_spans if isinstance(span, dict))
