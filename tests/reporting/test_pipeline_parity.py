"""Legacy filename retained for continuity.

Authoritative reporter parity now lives in the shared dual-path evaluation matrix
and compare artifacts. This module is smoke coverage for the direct
``ReportPipeline`` entrypoint only; it should assert focused invariants rather
than whole-note fixture equality.
"""

from __future__ import annotations

from proc_schemas.clinical import BundlePatch

from app.registry.application.registry_service import RegistryService
from app.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    apply_bundle_patch,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from app.reporting.pipeline import ReportPipeline


def _pipeline_engine() -> ReporterEngine:
    templates = default_template_registry()
    schemas = default_schema_registry()
    return ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
        render_style="builder",
    )


def _configure_env(monkeypatch) -> None:
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
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REPORTER_DISABLE_LLM": "1",
        "QA_REPORTER_ALLOW_SIMPLE_FALLBACK": "0",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)


def _render_with_pipeline(bundle) -> str:
    engine = _pipeline_engine()
    report = ReportPipeline(engine).run(bundle, strict=True, embed_metadata=False)
    rerendered = ReportPipeline(engine).run(bundle, strict=True, embed_metadata=False)
    assert report.text == rerendered.text
    return report.text


def _assert_common_render_invariants(markdown: str) -> None:
    assert "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT" in markdown
    assert "{{" not in markdown
    assert "}}" not in markdown
    assert "[indication]" not in markdown


def test_pipeline_smoke__seed_from_text_ebus_station7(monkeypatch) -> None:
    _configure_env(monkeypatch)

    note_text = "EBUS biopsied station 7"
    extraction_result = RegistryService().extract_fields(note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)

    markdown = _render_with_pipeline(bundle)

    _assert_common_render_invariants(markdown)
    assert "Endobronchial Ultrasound-Guided Transbronchial Needle Aspiration (EBUS-TBNA) (Stations 7)" in markdown
    assert "Station: 7" in markdown
    assert "Biopsy Tools: TBNA" in markdown


def test_pipeline_smoke__render_thoracentesis_cxr_ordered(monkeypatch) -> None:
    _configure_env(monkeypatch)

    extraction = {
        "patient_name": "Test Patient",
        "gender": "female",
        "procedure_date": "2024-05-01",
        "pleural_procedure_type": "thoracentesis",
        "pleural_side": "left",
        "pleural_volume_drained_ml": 900,
        "pleural_fluid_appearance": "serous",
        "intercostal_space": "7th",
        "entry_location": "mid-axillary",
        "pleural_guidance": "Ultrasound",
        "cxr_ordered": False,
    }

    bundle = build_procedure_bundle_from_extraction(extraction)
    proc_id = bundle.procedures[0].proc_id
    patch = BundlePatch.model_validate({"procedures": [{"proc_id": proc_id, "updates": {"cxr_ordered": True}}]})
    bundle = apply_bundle_patch(bundle, patch)

    markdown = _render_with_pipeline(bundle)

    _assert_common_render_invariants(markdown)
    assert "Thoracentesis (Detailed)" in markdown
    assert "A total of 900 mL of serous fluid was removed." in markdown
    assert "A post-procedure chest x-ray was ordered." in markdown
    assert "Successful left thoracentesis with 900 mL removed (serous)." in markdown


def test_pipeline_smoke__seed_from_text_ion_nav_tbna_cryo(monkeypatch) -> None:
    _configure_env(monkeypatch)

    note_text = (
        "Ion bronchoscopy RUL 2.2 cm nodule. Tool in lesion confirmed with CBCT. "
        "TBNA and cryobiopsy. ROSE + for malignancy"
    )
    extraction_result = RegistryService().extract_fields(note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)

    markdown = _render_with_pipeline(bundle)

    _assert_common_render_invariants(markdown)
    assert "Robotic navigational bronchoscopy (Ion) to RUL target" in markdown
    assert "Transbronchial Cryobiopsy (RUL)" in markdown
    assert "Cone-beam CT imaging with confirmation" in markdown
    assert "TBNA of RUL target" in markdown
    assert "Tool-in-lesion was confirmed with Cone Beam CT." in markdown
