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
            "must_contain_groups": [
                ["Chartis"],
                ["collateral ventilation", "CV negative", "CV positive"],
                ["No endobronchial valves were deployed", "No valves were deployed"],
            ],
            "must_not_contain": ["Valves deployed"],
        },
    },
    {
        "id": "focused_blvr_chartis_aborted_no_valves",
        "prompt": (
            "BLVR candidacy evaluation. Chartis assessment performed for BLVR candidacy. "
            "RUL CV negative. Procedure aborted due to bronchospasm. "
            "Plan for RUL BLVR with Zephyr valves at next procedure."
        ),
        "expected": {
            "must_contain_groups": [["Chartis"], ["Procedure aborted"], ["No endobronchial valves were deployed"]],
            "must_not_contain": ["Valves deployed"],
        },
    },
    {
        "id": "focused_tunneled_pleural_catheter_removal_no_inversion",
        "prompt": (
            "Right indwelling pleural catheter (PleurX) removal today. Catheter removed intact. "
            "Spontaneous pleurodesis achieved. Site sutured."
        ),
        "expected": {
            "must_contain_groups": [["tunneled pleural catheter", "PleurX"], ["removed"]],
            "must_not_contain": ["Chemical pleurodesis", "Image-Guided Chest Tube"],
        },
    },
    {
        "id": "focused_ebus_staging_no_peripheral_tbna",
        "prompt": (
            "EBUS-TBNA staging. Station 4R and station 7 sampled. TBNA x 6. "
            "ROSE adequate lymphocytes. Known RUL squamous cell carcinoma for staging."
        ),
        "expected": {
            "must_contain_groups": [["EBUS-TBNA Staging"], ["Station 4R", "Station: 4R"], ["Station 7", "Station: 7"]],
            # Guardrail: prevent an extra *peripheral* TBNA section from being fabricated from EBUS station sampling.
            "must_not_contain": ["\nTransbronchial Needle Aspiration\n"],
        },
    },
    {
        "id": "focused_whole_lung_lavage_not_bal",
        "prompt": (
            "Whole lung lavage (WLL) performed on the right lung for pulmonary alveolar proteinosis (PAP). "
            "Total lavage volume 15 L warmed saline; return initially turbid then clear."
        ),
        "expected": {
            "must_contain_groups": [["Whole lung lavage", "Whole Lung Lavage"], ["15", "15.0"], ["right lung", "right"] ],
            "must_not_contain": ["Bronchoalveolar Lavage"],
        },
    },
    {
        "id": "focused_medical_thoracoscopy_biopsies_and_talc",
        "prompt": (
            "Left medical thoracoscopy performed. 10 pleural biopsies obtained. "
            "Talc poudrage pleurodesis with 5 g talc. 24 Fr chest tube placed."
        ),
        "expected": {
            "must_contain_groups": [["Diagnostic Thoracoscopy"], ["Pleural biopsies"], ["Talc poudrage", "talc"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_foreign_body_chicken_bone",
        "prompt": (
            "Rigid bronchoscopy performed. Chicken bone foreign body removed from the right mainstem bronchus using forceps."
        ),
        "expected": {
            "must_contain_groups": [["foreign body"], ["Chicken bone"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_blvr_valve_exchange_mentions_replacement",
        "prompt": (
            "BLVR valve exchange. Removed 4 Zephyr valves from the RUL and replaced with 4 new Zephyr valves. "
            "Replacement sizes: 5.5, 4.0, 4.0, 4.0."
        ),
        "expected": {
            "must_contain_groups": [["Removal performed", "valves removed"], ["Exchange performed", "replaced"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_pleural_biopsy_abrams_not_blank",
        "prompt": (
            "Ultrasound guided pleural biopsy performed with an Abrams needle. 6 passes obtained. "
            "CXR ordered."
        ),
        "expected": {
            "must_contain_groups": [["Core needle biopsy was performed"], ["Abrams needle"], ["6 samples", "6 passes", "6"]],
            "must_not_contain": ["hemothorax"],
        },
    },
    {
        "id": "focused_cryobiopsy_bleeding_management_not_overwritten",
        "prompt": (
            "Transbronchial cryobiopsy performed for ILD evaluation in the RLL. Four cryobiopsies obtained. "
            "Moderate bleeding managed with bronchial blocker and cold saline lavage."
        ),
        "expected": {
            "must_contain_groups": [["Transbronchial Cryobiopsy"], ["Bleeding managed", "bronchial blocker", "cold saline"]],
            "must_not_contain": ["no clinically significant bleeding"],
        },
    },
    {
        "id": "focused_bilateral_tunneled_catheter_split_volumes",
        "prompt": (
            "Bilateral tunneled pleural catheter (PleurX) placement. Right side drained 1100 mL. "
            "Left side drained 900 mL."
        ),
        "expected": {
            "must_contain_groups": [["Hemithorax: Right"], ["Hemithorax: Left"], ["Fluid Removed: 1100 mL"], ["Fluid Removed: 900 mL"]],
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
    {
        "id": "focused_nav_chronology_no_rebus_prep_header",
        "prompt": (
            "Robotic bronchoscopy (Ion) to LUL nodule. Navigation successful, radial probe eccentric view, "
            "TIL confirmed with CBCT after catheter adjustment to concentric. TBNA x 5. Cryobiopsy x 4 with 1.1 mm probe."
        ),
        "expected": {
            "must_contain_groups": [["Tool-in-lesion was confirmed"], ["eccentric"], ["Transbronchial Cryobiopsy"]],
            "must_not_contain": [
                "Radial EBUS & Preparation",
                "Airway Inspection The bronchoscope was introduced",
                "pattern. Tool-in-lesion was confirmed",
            ],
        },
    },
    {
        "id": "focused_thoracentesis_stopped_due_to_cough_preserved",
        "prompt": (
            "Ultrasound guided thoracentesis left side at the 8th intercostal space along the midaxillary line. "
            "500 mL straw colored fluid removed. Stopped due to patient cough. CXR ordered."
        ),
        "expected": {
            "must_contain_groups": [["stopped due to patient cough"]],
            "must_not_contain": ["tolerated the procedure well", "tolerated the procedure without cough"],
        },
    },
    {
        "id": "focused_ebus_airway_finding_extrinsic_compression",
        "prompt": (
            "EBUS-TBNA staging. Airway inspection: extrinsic compression of RUL orifice but patent. "
            "Station 4R and station 7 sampled. ROSE adequate lymphocytes."
        ),
        "expected": {
            "must_contain_groups": [["extrinsic compression"], ["EBUS-TBNA Staging"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_chartis_rul_cv_positive_not_negative",
        "prompt": (
            "BLVR candidacy evaluation. Chartis assessment of RUL showed collateral ventilation positive. "
            "RLL CV negative. Procedure aborted for today. Plan to schedule RLL BLVR."
        ),
        "expected": {
            "must_contain_groups": [["RUL: CV positive"], ["RLL: CV negative"], ["No endobronchial valves were deployed"]],
            "must_not_contain": ["RUL: CV negative"],
        },
    },
    {
        "id": "focused_blvr_admit_ptx_watch_plan_not_dropped",
        "prompt": (
            "BLVR RUL with Zephyr valves. Placed RB1 5.5, RB2 4.0, RB3 4.0. "
            "Complete lobar occlusion confirmed. Admitted for 3 day pneumothorax watch."
        ),
        "expected": {
            "must_contain_groups": [["pneumothorax watch"]],
            "must_not_contain": ["Await final pathology"],
        },
    },
    {
        "id": "focused_robotic_bronchoscopy_two_targets_not_truncated",
        "prompt": (
            "Ion robotic bronchoscopy for two targets: RUL 1.3cm nodule and LUL 1.8cm nodule. "
            "Navigation, rEBUS confirmation, and sampling were performed at both targets."
        ),
        "expected": {
            "must_contain_groups": [["RUL", "Right Upper Lobe"], ["LUL", "Left Upper Lobe"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_bal_tbbx_multi_lobe_not_merged",
        "prompt": (
            "Bronchoscopy for suspected rejection post bilateral lung transplant. "
            "BAL from RML and LLL. TBBx x8 from RLL and LLL."
        ),
        "expected": {
            "must_contain_groups": [["RML and LLL"], ["RLL and LLL"], ["8 samples", "8 passes", "x8", "8"]],
            "must_not_contain": ["RML (8"],
        },
    },
    {
        "id": "focused_thoracentesis_bilateral_volumes_not_zero_or_merged",
        "prompt": (
            "Bilateral thoracentesis performed. Right side 1200 mL removed. "
            "Left side 800 mL removed. Clear fluid."
        ),
        "expected": {
            "must_contain_groups": [["Right side", "right side"], ["1200 mL"], ["Left side", "left side"], ["800 mL"]],
            "must_not_contain": ["A total of 0 mL"],
        },
    },
    {
        "id": "focused_thoracentesis_small_volume_not_zero",
        "prompt": "Thoracentesis right side. 50ml straw colored fluid obtained.",
        "expected": {
            "must_contain_groups": [["50 mL", "50ml"], ["straw"]],
            "must_not_contain": ["A total of 0 mL"],
        },
    },
    {
        "id": "focused_therapeutic_injection_bevacizumab_rendered",
        "prompt": (
            "Rigid bronchoscopy for airway papillomatosis. Microdebrider debridement performed. "
            "Bevacizumab injection x4 sites 100mg total."
        ),
        "expected": {
            "must_contain_groups": [["Therapeutic injection", "injection"], ["Bevacizumab"], ["100"], ["x4", "4 sites"]],
            "must_not_contain": [],
        },
    },
    {
        "id": "focused_conventional_tbna_details_preserved",
        "prompt": "Conventional TBNA 22g performed with 4 passes. ROSE result: small cell carcinoma.",
        "expected": {
            "must_contain_groups": [["22G"], ["4 passes", "4 pass"], ["ROSE"], ["small cell carcinoma"]],
            "must_not_contain": [],
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
