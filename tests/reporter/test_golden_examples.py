from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
import re
from typing import Any

import pytest

from modules.api.services.qa_pipeline import ReportingStrategy, SimpleReporterStrategy
from modules.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    default_schema_registry,
    default_template_registry,
)
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine


class _UnusedRegistryEngine:
    def run(self, text: str, explain: bool = False) -> dict[str, Any]:  # pragma: no cover - defensive
        raise AssertionError("Registry engine should not be called when registry_data is provided")


def _normalize_for_similarity(text: str) -> str:
    lines = []
    for line in (text or "").splitlines():
        compact = re.sub(r"\s+", " ", line.strip())
        if compact:
            lines.append(compact.lower())
    return "\n".join(lines)


def _missing_lines(golden: str, generated: str, limit: int = 6) -> list[str]:
    generated_lines = set(
        re.sub(r"\s+", " ", line.strip()).lower()
        for line in (generated or "").splitlines()
        if line.strip()
    )
    missing: list[str] = []
    for line in (golden or "").splitlines():
        compact = re.sub(r"\s+", " ", line.strip()).lower()
        if not compact:
            continue
        if compact not in generated_lines:
            missing.append(line.strip())
        if len(missing) >= limit:
            break
    return missing


def _build_reporting_strategy() -> ReportingStrategy:
    templates = default_template_registry()
    schemas = default_schema_registry()
    reporter_engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    return ReportingStrategy(
        reporter_engine=reporter_engine,
        inference_engine=InferenceEngine(),
        validation_engine=ValidationEngine(templates, schemas),
        registry_engine=_UnusedRegistryEngine(),
        simple_strategy=SimpleReporterStrategy(),
    )


def test_reporter_golden_examples(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QA_REPORTER_ALLOW_SIMPLE_FALLBACK", raising=False)
    dataset_path = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_golden_dataset.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    assert dataset, f"Golden dataset is empty: {dataset_path}"

    strategy = _build_reporting_strategy()
    scores: list[tuple[str, float]] = []
    diagnostics: list[dict[str, Any]] = []

    for entry in dataset:
        example_id = entry["example_id"]
        golden = entry["golden_markdown"]
        result = strategy.render(
            text=entry.get("note_text", ""),
            registry_data={"record": entry["extraction"]},
            procedure_type=None,
        )
        assert result.get("fallback_used") is False, f"{example_id}: unexpected fallback"
        assert result.get("render_mode") == "structured", f"{example_id}: unexpected render mode"

        generated = result.get("markdown", "")
        score = SequenceMatcher(
            None,
            _normalize_for_similarity(golden),
            _normalize_for_similarity(generated),
        ).ratio()
        scores.append((example_id, score))
        diagnostics.append(
            {
                "example_id": example_id,
                "score": score,
                "missing_lines": _missing_lines(golden, generated),
            }
        )

    average_score = sum(score for _, score in scores) / len(scores)
    min_example_id, min_score = min(scores, key=lambda item: item[1])

    if average_score < 0.55 or min_score < 0.30:
        low = sorted(diagnostics, key=lambda item: item["score"])[:3]
        details: list[str] = []
        for item in low:
            details.append(f"{item['example_id']} score={item['score']:.2f}")
            for line in item["missing_lines"]:
                details.append(f"  - {line}")
        pytest.fail(
            "Reporter golden thresholds failed.\n"
            f"Average score: {average_score:.2f} (required >= 0.55)\n"
            f"Minimum score: {min_score:.2f} (example {min_example_id}, required >= 0.30)\n"
            "Top misses:\n"
            + "\n".join(details)
        )
