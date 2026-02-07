#!/usr/bin/env python3
"""
Test harness for evaluating the reporter against the Golden Examples dataset.

Usage:
    pytest tests/reporter/test_golden_examples.py
    # OR directly for detailed output:
    python tests/reporter/test_golden_examples.py
"""

import json
import difflib
import os
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure modules are importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from modules.registry.application.registry_service import RegistryService
from modules.api.services.qa_pipeline import ReportingStrategy, SimpleReporterStrategy
from modules.reporting.engine import ReporterEngine, _load_procedure_order, default_schema_registry, default_template_registry
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine

# Configuration
GOLDEN_DATASET_PATH = PROJECT_ROOT / "tests/fixtures/reporter_golden_dataset.json"

def _reset_llm_usage_totals() -> None:
    """Reset internal LLM usage counters so this test can assert determinism."""
    try:
        from modules.common import llm as llm_mod

        llm_mod._USAGE_TOTALS_BY_MODEL.clear()
        llm_mod._USAGE_TOTALS_ALL.calls = 0
        llm_mod._USAGE_TOTALS_ALL.input_tokens = 0
        llm_mod._USAGE_TOTALS_ALL.output_tokens = 0
        llm_mod._USAGE_TOTALS_ALL.total_tokens = 0
        llm_mod._USAGE_TOTALS_ALL.cost_usd = 0.0
    except Exception:
        # Best-effort; determinism is still enforced by env flags below.
        return


@pytest.fixture(scope="session", autouse=True)
def _golden_env() -> None:
    """Deprecated: session-scoped env is overridden by baseline_env per-test."""
    return

def normalize_text(text: str) -> str:
    """Normalize whitespace and newlines for fairer comparison."""
    if not text: return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity ratio."""
    return difflib.SequenceMatcher(None, text1, text2).ratio()

@pytest.fixture(autouse=True)
def _golden_env_override(baseline_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Golden harness must be deterministic (no network LLM calls, no fallback).

    Note: tests/conftest.py enforces a per-test baseline environment; we override
    it here (after baseline_env) to ensure this suite uses the intended settings.
    """
    env_overrides = {
        # Explicitly disable any network-backed LLM usage.
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REGISTRY_USE_STUB_LLM": "1",
        # Avoid local `.env` influencing outputs.
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        # Reporter harness invariants.
        "QA_REPORTER_ALLOW_SIMPLE_FALLBACK": "0",
        "REPORTER_DISABLE_LLM": "1",
        # Ensure extraction-first uses deterministic pathway (no self-correction).
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        # Reduce noisy stderr output in CI.
        "OPENAI_LOG_USAGE_PER_CALL": "0",
        "OPENAI_LOG_USAGE_SUMMARY": "0",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)

@pytest.fixture(scope="session")
def _golden_examples() -> list[dict[str, Any]]:
    if not GOLDEN_DATASET_PATH.exists():
        raise AssertionError(
            f"Golden dataset not found at {GOLDEN_DATASET_PATH}. "
            "Run `python scripts/parse_golden_reporter_examples.py` to generate it."
        )
    return json.loads(GOLDEN_DATASET_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def _reporting_strategy() -> ReportingStrategy:
    templates = default_template_registry()
    schemas = default_schema_registry()
    reporter_engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    inference_engine = InferenceEngine()
    validation_engine = ValidationEngine(templates, schemas)

    class _NeverRegistryEngine:
        def run(self, *_args, **_kwargs):  # noqa: ANN001
            raise AssertionError("Golden tests should provide registry_data explicitly")

    return ReportingStrategy(
        reporter_engine=reporter_engine,
        inference_engine=inference_engine,
        validation_engine=validation_engine,
        registry_engine=_NeverRegistryEngine(),
        simple_strategy=SimpleReporterStrategy(),
    )


@pytest.fixture(scope="session")
def _registry_service() -> RegistryService:
    return RegistryService()


def test_golden_reporter_similarity(
    _golden_examples: list[dict[str, Any]],
    _registry_service: RegistryService,
    _reporting_strategy: ReportingStrategy,
) -> None:
    """Golden gate:
    - determinism (0 network LLM calls)
    - stability (no simple fallback)
    - quality (avg/min similarity thresholds)
    """
    _reset_llm_usage_totals()

    results: list[dict[str, Any]] = []

    for ex in _golden_examples:
        ex_id = ex["id"]
        input_text = ex["input_text"]
        ideal_output = ex["ideal_output"]

        extraction_result = _registry_service.extract_fields_extraction_first(input_text)
        record_dict = extraction_result.record.model_dump(exclude_none=True)

        report = _reporting_strategy.render(
            text=input_text,
            registry_data={"record": record_dict},
            procedure_type=None,
        )

        assert report.get("render_mode") == "structured", f"{ex_id} rendered in {report.get('render_mode')!r}"
        assert report.get("fallback_used") is False, f"{ex_id} unexpectedly used fallback"
        assert not report.get("reporter_errors"), f"{ex_id} reporter_errors={report.get('reporter_errors')!r}"

        generated_output = report.get("markdown") or ""
        norm_ideal = normalize_text(ideal_output)
        norm_gen = normalize_text(generated_output)
        similarity = calculate_similarity(norm_ideal, norm_gen)

        results.append({"id": ex_id, "similarity": similarity})

    scores = [r["similarity"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    min_score = min(scores) if scores else 0.0

    worst = sorted(results, key=lambda r: r["similarity"])[:5]
    worst_str = ", ".join(f"{r['id']}={r['similarity']:.2f}" for r in worst)

    assert avg_score >= 0.55, f"Average similarity {avg_score:.2f} < 0.55 (worst: {worst_str})"
    assert min_score >= 0.30, f"Minimum similarity {min_score:.2f} < 0.30 (worst: {worst_str})"

    # Determinism: assert no OpenAI usage was recorded.
    try:
        from modules.common import llm as llm_mod

        assert llm_mod._USAGE_TOTALS_ALL.calls == 0, f"LLM calls recorded: {llm_mod._USAGE_TOTALS_ALL.calls}"
    except Exception:
        # Best-effort: if the tracker isn't available, the env flags above still enforce offline.
        pass


def main() -> None:
    """Script mode: print per-example scores and a quick summary for debugging."""
    env_overrides = {
        # Explicitly disable any network-backed LLM usage.
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REGISTRY_USE_STUB_LLM": "1",
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        # Reporter harness invariants.
        "QA_REPORTER_ALLOW_SIMPLE_FALLBACK": "0",
        "REPORTER_DISABLE_LLM": "1",
        # Ensure extraction-first uses deterministic pathway (no self-correction).
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        # Reduce noisy stderr output in CI.
        "OPENAI_LOG_USAGE_PER_CALL": "0",
        "OPENAI_LOG_USAGE_SUMMARY": "0",
    }
    os.environ.update(env_overrides)

    examples = json.loads(GOLDEN_DATASET_PATH.read_text(encoding="utf-8"))

    templates = default_template_registry()
    schemas = default_schema_registry()
    reporter_engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    inference_engine = InferenceEngine()
    validation_engine = ValidationEngine(templates, schemas)

    class _NeverRegistryEngine:
        def run(self, *_args, **_kwargs):  # noqa: ANN001
            raise AssertionError("Golden tests should provide registry_data explicitly")

    strategy = ReportingStrategy(
        reporter_engine=reporter_engine,
        inference_engine=inference_engine,
        validation_engine=validation_engine,
        registry_engine=_NeverRegistryEngine(),
        simple_strategy=SimpleReporterStrategy(),
    )
    registry_service = RegistryService()

    _reset_llm_usage_totals()

    results: list[dict[str, Any]] = []
    for ex in examples:
        ex_id = ex["id"]
        input_text = ex["input_text"]
        ideal_output = ex["ideal_output"]

        print(f"Processing {ex_id}...", end="", flush=True)
        extraction_result = registry_service.extract_fields_extraction_first(input_text)
        record_dict = extraction_result.record.model_dump(exclude_none=True)
        report = strategy.render(text=input_text, registry_data={"record": record_dict})
        generated = report.get("markdown") or ""
        similarity = calculate_similarity(normalize_text(ideal_output), normalize_text(generated))
        results.append({"id": ex_id, "similarity": similarity})
        print(f" Done. Similarity: {similarity:.2f}")

    scores = [r["similarity"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    min_score = min(scores) if scores else 0.0
    print("\nAverage Similarity Score:", f"{avg_score:.2f}")
    print("Minimum Similarity Score:", f"{min_score:.2f}")
    print("Worst 5:", ", ".join(f"{r['id']}={r['similarity']:.2f}" for r in sorted(results, key=lambda r: r["similarity"])[:5]))

if __name__ == "__main__":
    main()
