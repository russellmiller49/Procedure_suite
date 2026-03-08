from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.common.quality_eval import (
    build_reporting_strategy,
    build_standard_report,
    configure_offline_quality_eval_env,
    evaluate_extraction_expectations,
    evaluate_reporter_expectations,
    load_unified_quality_corpus,
    render_report_markdown,
)
from app.registry.application.registry_service import RegistryService


_CORPUS_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "unified_quality_corpus.json"
_REQUIRED_TAGS = {
    "checkbox_negation",
    "menu_header_leakage",
    "inspection_only_stents",
    "ebus_peripheral_tbna_contamination",
    "tool_without_action",
    "blvr_exchange_removal",
    "wll_vs_bal",
    "pleural_placement_removal_inversion",
    "cryo_vs_forceps_confusion",
    "reporter_rose_misattribution",
}


def _load_cases() -> list[dict[str, Any]]:
    payload = load_unified_quality_corpus(_CORPUS_PATH)
    return list(payload.get("cases") or [])


@pytest.fixture(autouse=True)
def _quality_eval_env(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_offline_quality_eval_env()
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


@pytest.fixture(scope="module")
def _registry_service() -> RegistryService:
    return RegistryService()


@pytest.fixture(scope="module")
def _reporting_strategy():
    return build_reporting_strategy()


def test_unified_quality_corpus_covers_required_risk_tags() -> None:
    cases = _load_cases()
    seen_tags = {str(tag) for case in cases for tag in (case.get("tags") or [])}
    assert _REQUIRED_TAGS <= seen_tags


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: str(case.get("id") or "case"))
def test_unified_quality_matrix_case(
    case: dict[str, Any],
    _registry_service: RegistryService,
    _reporting_strategy: Any,
) -> None:
    note_text = str(case.get("note_text") or "")
    case_id = str(case.get("id") or "unknown_case")

    record, extraction_warnings, _meta = _registry_service.extract_record(note_text, note_id=case_id)
    predicted_codes, _rationales, derive_warnings = derive_all_codes_with_meta(record)
    extraction_case = evaluate_extraction_expectations(
        case=case,
        record_dict=record.model_dump(exclude_none=False),
        predicted_codes=predicted_codes,
        warnings=[*extraction_warnings, *derive_warnings],
    )
    assert extraction_case["status"] == "passed", json.dumps(extraction_case, indent=2, ensure_ascii=False)

    markdown, report_payload = render_report_markdown(
        note_text=note_text,
        registry_service=_registry_service,
        reporting_strategy=_reporting_strategy,
    )
    reporter_case = evaluate_reporter_expectations(
        case=case,
        markdown=markdown,
        report_payload=report_payload,
    )
    assert reporter_case["status"] == "passed", json.dumps(reporter_case, indent=2, ensure_ascii=False)


def test_unified_quality_standard_report_shape(
    _registry_service: RegistryService,
    _reporting_strategy: Any,
) -> None:
    cases = _load_cases()[:2]
    extraction_results: list[dict[str, Any]] = []
    reporter_results: list[dict[str, Any]] = []

    for case in cases:
        record, extraction_warnings, _meta = _registry_service.extract_record(str(case["note_text"]), note_id=str(case["id"]))
        predicted_codes, _rationales, derive_warnings = derive_all_codes_with_meta(record)
        extraction_results.append(
            evaluate_extraction_expectations(
                case=case,
                record_dict=record.model_dump(exclude_none=False),
                predicted_codes=predicted_codes,
                warnings=[*extraction_warnings, *derive_warnings],
            )
        )

        markdown, report_payload = render_report_markdown(
            note_text=str(case["note_text"]),
            registry_service=_registry_service,
            reporting_strategy=_reporting_strategy,
        )
        reporter_results.append(
            evaluate_reporter_expectations(
                case=case,
                markdown=markdown,
                report_payload=report_payload,
            )
        )

    extraction_report = build_standard_report(
        kind="extraction",
        input_path=str(_CORPUS_PATH),
        output_path=None,
        source_format="unified_quality_corpus",
        corpus_name="unified_quality_corpus",
        per_case=extraction_results,
        summary_metrics={"exact_code_match_cases": 2, "exact_code_match_rate": 1.0},
    )
    reporter_report = build_standard_report(
        kind="reporter",
        input_path=str(_CORPUS_PATH),
        output_path=None,
        source_format="unified_quality_corpus",
        corpus_name="unified_quality_corpus",
        per_case=reporter_results,
        summary_metrics={
            "successful_cases": 2,
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "generated_full_shell_rate": 0.0,
        },
    )

    expected_top_level_keys = {
        "schema_version",
        "kind",
        "input_path",
        "output_path",
        "source_format",
        "corpus_name",
        "created_at",
        "runtime",
        "summary",
        "per_case",
        "failures",
    }
    assert set(extraction_report) == expected_top_level_keys
    assert set(reporter_report) == expected_top_level_keys
