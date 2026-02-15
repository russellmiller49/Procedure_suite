from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

from app.api.services.qa_pipeline import ReportingStrategy, SimpleReporterStrategy
from app.reporting.inference import PatchResult
from proc_schemas.clinical.common import ProcedureBundle

if os.getenv("RUN_REPORTER_PROMPT_SEED_TESTS", "").strip().lower() not in {"1", "true", "yes"}:
    pytest.skip(
        "Reporter prompt seed tests are opt-in (set RUN_REPORTER_PROMPT_SEED_TESTS=1).",
        allow_module_level=True,
    )


def _minimal_record() -> dict:
    return {
        "patient": {},
        "encounter": {},
        "procedures": [
            {
                "proc_type": "other",
                "schema_id": "other.v1",
                "data": {},
            }
        ],
        "source_text": "seed source text",
    }


def _minimal_bundle() -> ProcedureBundle:
    return ProcedureBundle.model_validate(
        {
            "patient": {},
            "encounter": {},
            "procedures": [
                {
                    "proc_type": "other",
                    "schema_id": "other.v1",
                    "data": {},
                }
            ],
        }
    )


@dataclass
class _StructuredOut:
    text: str = "structured markdown"


class _DummyReporterEngine:
    def compose_report_with_metadata(self, *_args, **_kwargs):  # noqa: ANN001
        return _StructuredOut()


class _DummyInferenceEngine:
    def infer_bundle(self, _bundle):  # noqa: ANN001
        return PatchResult()


class _DummyValidationEngine:
    def list_missing_critical_fields(self, _bundle):  # noqa: ANN001
        return []

    def apply_warn_if_rules(self, _bundle):  # noqa: ANN001
        return []


class _NeverRegistryEngine:
    def run(self, *_args, **_kwargs):  # noqa: ANN001
        raise AssertionError("Registry engine should not be called in these tests")


class _SeedSuccess:
    def generate_bundle(self, _prompt_text: str):
        return _minimal_bundle(), ["used_balanced_object_extraction"]


class _SeedFailure:
    def generate_bundle(self, _prompt_text: str):
        raise ValueError("simulated parse failure")


def _build_strategy(seed_model) -> ReportingStrategy:
    return ReportingStrategy(
        reporter_engine=_DummyReporterEngine(),
        inference_engine=_DummyInferenceEngine(),
        validation_engine=_DummyValidationEngine(),
        registry_engine=_NeverRegistryEngine(),
        simple_strategy=SimpleReporterStrategy(),
        reporter_prompt_bundle_seeder=seed_model,
    )


def test_reporting_strategy_uses_prompt_seed_for_prompt_like_input() -> None:
    strategy = _build_strategy(_SeedSuccess())
    result = strategy.render(
        text="Generate an operative report for a 63 year old male with stent surveillance.",
        registry_data={"record": _minimal_record()},
    )

    assert result["render_mode"] == "structured_ml_seed"
    assert result["fallback_used"] is False
    assert any(str(item).startswith("REPORTER_PROMPT_MODEL_PARSE:") for item in result["warnings"])


def test_reporting_strategy_falls_back_to_structured_when_prompt_seed_fails() -> None:
    strategy = _build_strategy(_SeedFailure())
    result = strategy.render(
        text="Generate an operative report for a 70 year old female with airway findings.",
        registry_data={"record": _minimal_record()},
    )

    assert result["render_mode"] == "structured"
    assert result["fallback_used"] is False
    assert any("REPORTER_PROMPT_MODEL_FALLBACK" in str(item) for item in result["warnings"])
