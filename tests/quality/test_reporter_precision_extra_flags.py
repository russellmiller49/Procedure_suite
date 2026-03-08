from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.common.reporter_seed_eval import extract_flags_and_cpt
from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord
from app.reporting.llm_findings import LLMFindingsSeedResult, build_record_payload_for_reporting
from app.reporting.seed_pipeline import (
    run_reporter_seed_pipeline,
    seed_outcome_from_llm_findings_seed,
    seed_outcome_from_registry_result,
)

_PRECISION_CASES_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_extra_flag_precision_cases.json"
_DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_golden_dataset.json"
_LLM_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "reporter_seed_eval_llm_fixture_full.json"


@pytest.fixture(autouse=True)
def _reporter_precision_env(monkeypatch: pytest.MonkeyPatch) -> None:
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


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_precision_cases() -> list[dict[str, str]]:
    payload = _load_json(_PRECISION_CASES_PATH)
    assert isinstance(payload, dict)
    return [case for case in payload.get("cases") or [] if isinstance(case, dict)]


def _load_dataset_map() -> dict[str, dict[str, str]]:
    payload = _load_json(_DATASET_PATH)
    assert isinstance(payload, list)
    return {
        str(case.get("id")): case
        for case in payload
        if isinstance(case, dict) and case.get("id")
    }


def _load_llm_fixture_map() -> dict[str, dict[str, object]]:
    payload = _load_json(_LLM_FIXTURE_PATH)
    assert isinstance(payload, dict)
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


def test_reporter_precision_extra_flag_fixtures() -> None:
    cases = _load_precision_cases()
    dataset_map = _load_dataset_map()
    llm_fixture_map = _load_llm_fixture_map()
    registry_service = RegistryService()

    for case in cases:
        source_case_id = str(case["source_case_id"])
        prompt_text = str(dataset_map[source_case_id]["input_text"])
        family = str(case["family"])
        mode = str(case["mode"])

        registry_outcome = seed_outcome_from_registry_result(
            registry_service.extract_fields(prompt_text),
            masked_seed_text=prompt_text,
        )
        registry_result = run_reporter_seed_pipeline(
            registry_outcome,
            note_text=prompt_text,
            metadata={},
            strict=True,
            debug_enabled=True,
        )

        llm_seed = _seed_from_fixture(source_case_id, prompt_text, llm_fixture_map)
        llm_outcome = seed_outcome_from_llm_findings_seed(
            llm_seed,
            reporting_payload=build_record_payload_for_reporting(llm_seed),
        )
        llm_result = run_reporter_seed_pipeline(
            llm_outcome,
            note_text=prompt_text,
            metadata={},
            strict=True,
            debug_enabled=True,
        )

        registry_flags, _ = extract_flags_and_cpt(registry_result.markdown, registry_service)
        llm_flags, _ = extract_flags_and_cpt(llm_result.markdown, registry_service)

        flag = str(case.get("expected_present") or case.get("expected_absent") or family)
        assertion_payload = {
            "fixture_id": case["id"],
            "source_case_id": source_case_id,
            "family": family,
            "mode": mode,
            "flag": flag,
        }

        if mode == "suppress":
            assert flag not in registry_flags, json.dumps(
                assertion_payload | {"path": "registry_extract_fields", "markdown": registry_result.markdown},
                indent=2,
            )
            assert flag not in llm_flags, json.dumps(
                assertion_payload | {"path": "llm_findings", "markdown": llm_result.markdown},
                indent=2,
            )
        else:
            assert flag in registry_flags, json.dumps(
                assertion_payload | {"path": "registry_extract_fields", "markdown": registry_result.markdown},
                indent=2,
            )
            assert flag in llm_flags, json.dumps(
                assertion_payload | {"path": "llm_findings", "markdown": llm_result.markdown},
                indent=2,
            )

        assert (flag in registry_flags) == (flag in llm_flags), json.dumps(
            assertion_payload
            | {
                "registry_has": flag in registry_flags,
                "llm_has": flag in llm_flags,
            },
            indent=2,
        )
