"""Authoritative reporter parity gate for the fixed PR subset.

If end-to-end reporter parity expectations change, update this matrix, the shared
eval scripts, and the checked-in compare artifacts together.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.common.reporter_seed_eval import extract_flags_and_cpt, load_json
from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord
from app.reporting.llm_findings import LLMFindingsSeedResult, build_record_payload_for_reporting
from app.reporting.seed_pipeline import (
    run_reporter_seed_pipeline,
    seed_outcome_from_llm_findings_seed,
    seed_outcome_from_registry_result,
)

_CASES_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_seed_eval_samples.json"
_LLM_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_seed_eval_llm_fixture.json"


@pytest.fixture(autouse=True)
def _reporter_matrix_env(monkeypatch: pytest.MonkeyPatch) -> None:
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
    return list(payload.get("cases") or [])


def _load_llm_fixture() -> dict[str, dict[str, object]]:
    payload = load_json(_LLM_FIXTURE_PATH)
    return {
        str(case.get("id")): case
        for case in payload.get("cases") or []
        if isinstance(case, dict) and case.get("id")
    }


def _seed_from_fixture(case_id: str, prompt_text: str, fixture_map: dict[str, dict[str, object]]) -> LLMFindingsSeedResult:
    payload = fixture_map[case_id]
    return LLMFindingsSeedResult(
        record=RegistryRecord.model_validate(payload.get("record") or {}),
        masked_prompt_text=str(payload.get("masked_prompt_text") or prompt_text),
        cpt_codes=[str(code) for code in list(payload.get("cpt_codes") or [])],
        warnings=[str(item) for item in list(payload.get("warnings") or []) if str(item)],
        needs_review=bool(payload.get("needs_review")),
        context=None,
        accepted_items=[],
        accepted_findings=int(payload.get("accepted_findings") or 0),
        dropped_findings=int(payload.get("dropped_findings") or 0),
    )


def test_reporter_seed_dual_path_matrix() -> None:
    cases = _load_cases()
    fixture_map = _load_llm_fixture()
    registry_service = RegistryService()

    registry_fallback_count = 0
    llm_fallback_count = 0

    for case in cases:
        case_id = str(case["id"])
        note_text = str(case["prompt_text"])

        registry_outcome = seed_outcome_from_registry_result(
            registry_service.extract_fields(note_text),
            masked_seed_text=note_text,
        )
        registry_result = run_reporter_seed_pipeline(
            registry_outcome,
            note_text=note_text,
            metadata={},
            strict=True,
            debug_enabled=True,
        )

        llm_seed = _seed_from_fixture(case_id, note_text, fixture_map)
        llm_outcome = seed_outcome_from_llm_findings_seed(
            llm_seed,
            reporting_payload=build_record_payload_for_reporting(llm_seed),
        )
        llm_result = run_reporter_seed_pipeline(
            llm_outcome,
            note_text=note_text,
            metadata={},
            strict=True,
            debug_enabled=True,
        )

        registry_flags, _registry_cpt = extract_flags_and_cpt(registry_result.markdown, registry_service)
        llm_flags, _llm_cpt = extract_flags_and_cpt(llm_result.markdown, registry_service)

        for flag in case.get("critical_flags_present") or []:
            flag_text = str(flag)
            assert flag_text in registry_flags, json.dumps(
                {"case_id": case_id, "path": "registry", "missing_flag": flag_text, "markdown": registry_result.markdown},
                indent=2,
            )
            assert flag_text in llm_flags, json.dumps(
                {"case_id": case_id, "path": "llm", "missing_flag": flag_text, "markdown": llm_result.markdown},
                indent=2,
            )

        for flag in case.get("critical_flags_absent") or []:
            flag_text = str(flag)
            assert flag_text not in registry_flags, json.dumps(
                {"case_id": case_id, "path": "registry", "unexpected_flag": flag_text, "markdown": registry_result.markdown},
                indent=2,
            )
            assert flag_text not in llm_flags, json.dumps(
                {"case_id": case_id, "path": "llm", "unexpected_flag": flag_text, "markdown": llm_result.markdown},
                indent=2,
            )

        critical_expected = {
            str(flag)
            for flag in (case.get("critical_flags_present") or [])
        } | {
            str(flag)
            for flag in (case.get("critical_flags_absent") or [])
        }
        for flag in critical_expected:
            assert (flag in registry_flags) == (flag in llm_flags), json.dumps(
                {
                    "case_id": case_id,
                    "flag": flag,
                    "registry_has": flag in registry_flags,
                    "llm_has": flag in llm_flags,
                },
                indent=2,
            )

        for token in case.get("forbidden_artifacts") or []:
            forbidden = str(token)
            assert forbidden not in registry_result.markdown
            assert forbidden not in llm_result.markdown

        registry_fallback_count += int(bool(registry_result.render_fallback_used))
        llm_fallback_count += int(bool(llm_result.render_fallback_used))

    assert llm_fallback_count <= registry_fallback_count
    assert registry_fallback_count < len(cases)
    assert llm_fallback_count < len(cases)
