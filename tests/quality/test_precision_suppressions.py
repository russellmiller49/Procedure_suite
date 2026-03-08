from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.common.quality_eval import get_path, normalize_code
from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "precision_suppressions.json"


def _load_cases() -> list[dict[str, Any]]:
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return list(payload.get("cases") or [])


@dataclass
class _StubPathwayResult:
    source: str
    codes: list[str]
    confidences: dict[str, float]
    processing_time_ms: float
    details: dict[str, Any]


@dataclass
class _StubParallelResult:
    path_a_result: _StubPathwayResult
    path_b_result: _StubPathwayResult
    final_codes: list[str]
    final_confidences: dict[str, float]
    needs_review: bool
    review_reasons: list[str]
    total_time_ms: float


class _SeededParallelOrchestrator:
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


@pytest.fixture(autouse=True)
def _quality_env(monkeypatch: pytest.MonkeyPatch) -> None:
    env_overrides = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        "ENABLE_UMLS_LINKER": "false",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SCHEMA_VERSION": "v3",
        "REGISTRY_AUDITOR_SOURCE": "disabled",
        "REGISTRY_USE_STUB_LLM": "1",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)


def _build_service(seed_record: dict[str, Any]) -> RegistryService:
    record = RegistryRecord.model_validate(seed_record)
    service = RegistryService(parallel_orchestrator=_SeededParallelOrchestrator(record))
    service._get_registry_ml_predictor = lambda: None  # type: ignore[method-assign]
    return service


def _normalized_codes(values: list[str]) -> list[str]:
    return sorted({code for code in (normalize_code(item) for item in values) if code})


def _forbidden_field_hits(record_dict: dict[str, Any], expectations: dict[str, Any]) -> int:
    hits = 0
    for path, forbidden in (expectations.get("must_not_have_fields") or {}).items():
        if get_path(record_dict, str(path)) == forbidden:
            hits += 1
    return hits


def _forbidden_code_hits(codes: list[str], expectations: dict[str, Any]) -> int:
    normalized = set(_normalized_codes(codes))
    return sum(1 for code in (expectations.get("must_not_have_codes") or []) if normalize_code(str(code)) in normalized)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: str(case.get("id") or "case"))
def test_precision_suppression_case(case: dict[str, Any]) -> None:
    expectations = dict(case.get("expectations") or {})
    service = _build_service(dict(case.get("seed_record") or {}))
    result = service.extract_fields(str(case.get("note_text") or ""))

    actual_codes = _normalized_codes(result.cpt_codes)
    actual_record = result.record.model_dump(exclude_none=False)
    warning_text = [str(item) for item in (result.warnings or []) if str(item)]
    signal_codes = [str(signal.code) for signal in (result.quality_signals or []) if getattr(signal, "code", None)]

    for code in expectations.get("must_have_codes") or []:
        normalized = normalize_code(str(code))
        assert normalized in actual_codes, (case["id"], actual_codes)

    for code in expectations.get("must_not_have_codes") or []:
        normalized = normalize_code(str(code))
        assert normalized not in actual_codes, (case["id"], actual_codes)

    for path, expected in (expectations.get("must_have_fields") or {}).items():
        assert get_path(actual_record, str(path)) == expected, (case["id"], path, get_path(actual_record, str(path)))

    for path, forbidden in (expectations.get("must_not_have_fields") or {}).items():
        assert get_path(actual_record, str(path)) != forbidden, (case["id"], path, get_path(actual_record, str(path)))

    for snippet in expectations.get("must_have_warnings_substrings") or []:
        needle = str(snippet)
        assert any(needle in warning for warning in warning_text), (case["id"], warning_text)

    for snippet in expectations.get("must_not_have_warnings_substrings") or []:
        needle = str(snippet)
        assert not any(needle in warning for warning in warning_text), (case["id"], warning_text)

    for signal_code in expectations.get("must_have_signal_codes") or []:
        assert str(signal_code) in signal_codes, (case["id"], signal_codes)

    for signal_code in expectations.get("must_not_have_signal_codes") or []:
        assert str(signal_code) not in signal_codes, (case["id"], signal_codes)

    expected_review = expectations.get("needs_manual_review")
    if expected_review is not None:
        assert result.needs_manual_review is bool(expected_review), (case["id"], result.needs_manual_review)


def test_precision_suppression_summary_hits_zero() -> None:
    summary_by_family: dict[str, dict[str, int]] = {}

    for case in _load_cases():
        expectations = dict(case.get("expectations") or {})
        seed_record = RegistryRecord.model_validate(dict(case.get("seed_record") or {}))
        before_codes, _before_rationales, _before_warnings = derive_all_codes_with_meta(seed_record)
        before_record = seed_record.model_dump(exclude_none=False)

        result = _build_service(dict(case.get("seed_record") or {})).extract_fields(str(case.get("note_text") or ""))
        after_codes = result.cpt_codes
        after_record = result.record.model_dump(exclude_none=False)

        family = str(case.get("family") or "unknown")
        bucket = summary_by_family.setdefault(
            family,
            {
                "before_forbidden_code_hits": 0,
                "after_forbidden_code_hits": 0,
                "before_extra_flag_hits": 0,
                "after_extra_flag_hits": 0,
            },
        )
        bucket["before_forbidden_code_hits"] += _forbidden_code_hits(before_codes, expectations)
        bucket["after_forbidden_code_hits"] += _forbidden_code_hits(after_codes, expectations)
        bucket["before_extra_flag_hits"] += _forbidden_field_hits(before_record, expectations)
        bucket["after_extra_flag_hits"] += _forbidden_field_hits(after_record, expectations)

    assert summary_by_family, "expected fixture families"
    for family, metrics in summary_by_family.items():
        assert metrics["after_forbidden_code_hits"] == 0, (family, metrics)
        assert metrics["after_extra_flag_hits"] <= metrics["before_extra_flag_hits"], (family, metrics)
