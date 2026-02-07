from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
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
class _StubParallelPathwayResult:
    final_codes: list[str]
    final_confidences: dict[str, float]
    path_a_result: _StubPathwayResult
    path_b_result: _StubPathwayResult
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
    explanations: dict[str, str] = field(default_factory=dict)
    total_time_ms: float = 0.0


class _StubParallelPathwayOrchestrator:
    def __init__(self, *, seed_record: dict[str, Any] | None = None) -> None:
        self._seed_record = seed_record or {}

    def process(self, note_text: str, ml_predictor: object | None = None) -> _StubParallelPathwayResult:  # noqa: ARG002
        record = RegistryRecord.model_validate(self._seed_record)
        details = {
            "record": record,
            "ner_entities": [],
            "ner_entity_count": 0,
            "stations_sampled_count": 0,
        }
        return _StubParallelPathwayResult(
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


def _load_regression_cases() -> list[dict[str, Any]]:
    path = Path(__file__).with_name("regression_cases.jsonl")
    cases: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        cases.append(json.loads(line))
    return cases


@pytest.mark.parametrize("case", _load_regression_cases(), ids=lambda c: c.get("id", "case"))
def test_extraction_regression_pack(case: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    expect = case.get("expect") or {}
    note_text = case.get("note_text") or ""

    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    env_overrides = case.get("env") or {}
    if isinstance(env_overrides, dict):
        for key, value in env_overrides.items():
            if isinstance(key, str) and key.strip():
                monkeypatch.setenv(key, str(value))

    seed_record = case.get("seed_record") if isinstance(case.get("seed_record"), dict) else None
    orchestrator = _StubParallelPathwayOrchestrator(seed_record=seed_record)
    service = RegistryService(parallel_orchestrator=orchestrator)
    service._get_registry_ml_predictor = lambda: None  # type: ignore[method-assign]

    result = service.extract_fields(note_text)

    codes = {str(c) for c in (result.cpt_codes or []) if str(c).strip()}
    must_have_codes = expect.get("must_have_codes") or []
    must_not_have_codes = expect.get("must_not_have_codes") or []

    for code in must_have_codes:
        assert str(code) in codes
    for code in must_not_have_codes:
        assert str(code) not in codes

    warnings = [str(w) for w in (result.warnings or [])]
    must_have_warn = expect.get("must_have_warnings_substrings") or []
    must_not_have_warn = expect.get("must_not_have_warnings_substrings") or []

    for snippet in must_have_warn:
        needle = str(snippet).lower()
        assert any(needle in w.lower() for w in warnings)
    for snippet in must_not_have_warn:
        needle = str(snippet).lower()
        assert not any(needle in w.lower() for w in warnings)

    if any(str(s).startswith("NEEDS_REVIEW:") for s in must_have_warn):
        assert result.needs_manual_review is True
