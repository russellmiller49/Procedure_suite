from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.common.reporter_seed_eval import load_json
from app.registry.application.registry_service import RegistryService
from app.reporting.seed_pipeline import run_reporter_seed_pipeline, seed_outcome_from_registry_result


_CASES_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_clinical_fidelity_cases.json"


@pytest.fixture(autouse=True)
def _reporter_clinical_env(monkeypatch: pytest.MonkeyPatch) -> None:
    env_overrides = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        "ENABLE_UMLS_LINKER": "false",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SCHEMA_VERSION": "v3",
        "REGISTRY_AUDITOR_SOURCE": "raw_ml",
        "REGISTRY_USE_STUB_LLM": "1",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        "REPORTER_DISABLE_LLM": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "QA_REPORTER_ALLOW_SIMPLE_FALLBACK": "0",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)


def _load_cases() -> list[dict[str, object]]:
    payload = load_json(_CASES_PATH)
    return [case for case in payload.get("cases") or [] if isinstance(case, dict)]


def test_reporter_clinical_fidelity_suite() -> None:
    service = RegistryService()
    failures: list[dict[str, object]] = []

    for case in _load_cases():
        case_id = str(case["id"])
        note_text = str(case["prompt_text"])

        outcome = seed_outcome_from_registry_result(
            service.extract_fields(note_text),
            masked_seed_text=note_text,
        )
        pipeline = run_reporter_seed_pipeline(
            outcome,
            note_text=note_text,
            strict=True,
            debug_enabled=True,
        )

        markdown = pipeline.markdown
        proc_types = {proc.proc_type for proc in pipeline.bundle.procedures}
        blockers = [flag.get("code") for flag in pipeline.quality_flags if flag.get("severity") == "blocker"]
        missing_proc_types = [
            proc_type
            for proc_type in case.get("required_proc_types") or []
            if str(proc_type) not in proc_types
        ]
        missing_text = [
            needle
            for needle in case.get("required_markdown_contains") or []
            if str(needle) not in markdown
        ]
        forbidden_text = [
            needle
            for needle in case.get("forbidden_markdown_contains") or []
            if str(needle) in markdown
        ]

        if blockers or missing_proc_types or missing_text or forbidden_text:
            failures.append(
                {
                    "id": case_id,
                    "blockers": blockers,
                    "needs_manual_review": pipeline.needs_manual_review,
                    "missing_proc_types": missing_proc_types,
                    "missing_text": missing_text,
                    "forbidden_text": forbidden_text,
                    "proc_types": sorted(proc_types),
                    "markdown_excerpt": markdown[:1200],
                }
            )

    assert not failures, json.dumps(failures, indent=2)
