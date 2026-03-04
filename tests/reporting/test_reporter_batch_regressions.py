from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.api.services.qa_pipeline import ReportingStrategy, SimpleReporterStrategy
from app.registry.application.registry_service import RegistryService
from app.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    default_schema_registry,
    default_template_registry,
)
from app.reporting.inference import InferenceEngine
from app.reporting.validation import ValidationEngine


_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "reporter_batch_regression_fixture.json"


_FOCUSED_CASES: list[dict[str, Any]] = [
    {
        "id": "focused_ebus_negation_no_malignant_rose",
        "prompt": (
            "EBUS-TBNA stations 4R and 7 sampled with adequate material. "
            "ROSE adequate lymphocytes at both stations. All stations negative for malignancy."
        ),
        "expected": {
            "must_contain_groups": [["ROSE Results: Adequate lymphocytes"]],
            "must_not_contain": ["ROSE Results: Malignant"],
        },
    },
    {
        "id": "focused_blvr_placement_chartis",
        "prompt": (
            "BLVR RUL with Zephyr valves. Chartis assessment CV negative confirmed. "
            "Placed RB1 5.5, RB2 4.0, RB3 4.0. Complete lobar occlusion confirmed."
        ),
        "expected": {
            "must_contain_groups": [["Endobronchial Valve", "Valves deployed"], ["Chartis"]],
            "must_not_contain": ["See procedure details below"],
        },
    },
    {
        "id": "focused_blvr_removal",
        "prompt": (
            "BLVR valve removal for persistent pneumothorax. "
            "All 3 valves in RUL removed without difficulty."
        ),
        "expected": {
            "must_contain_groups": [["Removal performed", "valves removed"]],
            "must_not_contain": ["Image-Guided Chest Tube"],
        },
    },
    {
        "id": "focused_blvr_chartis_candidacy",
        "prompt": (
            "Therapeutic bronchoscopy and BLVR assessment. First addressed mucoid impaction LLL with suctioning and lavage. "
            "Then performed Chartis assessment of both upper lobes for BLVR candidacy. "
            "RUL CV negative, LUL CV positive. Plan to proceed with RUL BLVR with Zephyr valves at next procedure."
        ),
        "expected": {
            "must_contain_groups": [["Chartis"], ["collateral ventilation", "CV negative", "CV positive"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_talc_slurry_via_tunneled_catheter",
        "prompt": (
            "PleurX catheter placement left side followed by talc slurry pleurodesis through the catheter. "
            "1200 mL drained initially. 5 g talc slurry instilled."
        ),
        "expected": {
            "must_contain_groups": [["talc", "pleurodesis"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_ebus_plus_tunneled_pleural_catheter",
        "prompt": (
            "Flex bronch with EBUS-TBNA restaging and right tunneled pleural catheter placement "
            "with 1400 mL serosanguinous fluid drained."
        ),
        "expected": {
            "must_contain_groups": [["tunneled pleural", "PleurX", "Indwelling Tunneled Pleural Catheter"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_chest_tube_tpa_dnase",
        "prompt": (
            "Ultrasound guided right pigtail chest tube placement for complicated effusion. "
            "tPA 10 mg and DNase 5 mg q12h x3 days initiated."
        ),
        "expected": {
            "must_contain_groups": [["tPA", "DNase", "fibrinolytic"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_thoracentesis_no_structured_failure",
        "prompt": (
            "Ultrasound guided thoracentesis left side with 1800 mL straw colored fluid removed. "
            "No pneumothorax and no immediate complications."
        ),
        "expected": {
            "must_contain_groups": [["Thoracentesis"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_cryo_nodule_no_ild_default",
        "prompt": (
            "Robotic bronchoscopy RLL mass. Tool in lesion confirmed. "
            "Five TBNA passes and four cryobiopsies with 1.1 mm probe."
        ),
        "expected": {
            "must_contain_groups": [],
            "must_not_contain": ["ILD evaluation"],
        },
    },
]


def load_fixture() -> list[dict[str, Any]]:
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return list(payload.get("cases") or [])


def assert_expected(markdown: str, expected: dict[str, Any], case_id: str) -> None:
    preview = markdown[:500]
    for idx, group in enumerate(expected.get("must_contain_groups") or [], start=1):
        options = [str(item) for item in group if str(item)]
        if not options:
            continue
        if not any(option in markdown for option in options):
            raise AssertionError(
                f"[{case_id}] missing must_contain group {idx}: {options!r}\n"
                f"markdown preview:\n{preview}"
            )

    for forbidden in expected.get("must_not_contain") or []:
        token = str(forbidden)
        if token and token in markdown:
            raise AssertionError(
                f"[{case_id}] found forbidden substring: {token!r}\n"
                f"markdown preview:\n{preview}"
            )


@pytest.fixture(autouse=True)
def _regression_env(monkeypatch: pytest.MonkeyPatch) -> None:
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
            raise AssertionError("Batch regressions should provide registry_data explicitly")

    return ReportingStrategy(
        reporter_engine=reporter_engine,
        inference_engine=inference_engine,
        validation_engine=validation_engine,
        registry_engine=_NeverRegistryEngine(),
        simple_strategy=SimpleReporterStrategy(),
    )


@pytest.fixture(scope="module")
def _registry_service() -> RegistryService:
    return RegistryService()


def _render_markdown(
    *,
    prompt: str,
    registry_service: RegistryService,
    reporting_strategy: ReportingStrategy,
) -> str:
    extraction_result = registry_service.extract_fields_extraction_first(prompt)
    record_dict = extraction_result.record.model_dump(exclude_none=True)
    report = reporting_strategy.render(text=prompt, registry_data={"record": record_dict})
    markdown = str(report.get("markdown") or "")
    assert markdown.strip(), "Rendered markdown should be non-empty"
    return markdown


def test_reporter_batch_regressions_fixture(
    _registry_service: RegistryService,
    _reporting_strategy: ReportingStrategy,
) -> None:
    for case in load_fixture():
        case_id = str(case.get("id") or "unknown_case")
        prompt = str(case.get("prompt") or "")
        expected = case.get("expected") or {}

        markdown = _render_markdown(
            prompt=prompt,
            registry_service=_registry_service,
            reporting_strategy=_reporting_strategy,
        )
        assert_expected(markdown, expected, case_id)


@pytest.mark.parametrize("case", _FOCUSED_CASES, ids=[str(item["id"]) for item in _FOCUSED_CASES])
def test_reporter_batch_regressions_focused_prompts(
    case: dict[str, Any],
    _registry_service: RegistryService,
    _reporting_strategy: ReportingStrategy,
) -> None:
    case_id = str(case["id"])
    markdown = _render_markdown(
        prompt=str(case["prompt"]),
        registry_service=_registry_service,
        reporting_strategy=_reporting_strategy,
    )
    assert_expected(markdown, case["expected"], case_id)
