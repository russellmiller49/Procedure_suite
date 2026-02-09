from __future__ import annotations

from pathlib import Path

from proc_schemas.clinical import BundlePatch

from app.api.routes.reporting import _verify_bundle
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


_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "reporting"


def _read_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def _pipeline_engine() -> ReporterEngine:
    templates = default_template_registry()
    schemas = default_schema_registry()
    return ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
        render_style="builder",
    )


def test_pipeline_parity__seed_from_text_ebus_station7(monkeypatch) -> None:
    env_overrides = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        "ENABLE_UMLS_LINKER": "false",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "engine",
        "REGISTRY_SCHEMA_VERSION": "v3",
        "REGISTRY_AUDITOR_SOURCE": "raw_ml",
        "REGISTRY_USE_STUB_LLM": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REPORTER_DISABLE_LLM": "1",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)

    note_text = "EBUS biopsied station 7"
    expected = _read_fixture("seed_from_text_ebus_station7.md")

    extraction_result = RegistryService().extract_fields(note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)
    bundle, _issues, _warnings, _suggestions, _notes = _verify_bundle(bundle)

    engine = _pipeline_engine()
    report = ReportPipeline(engine).run(bundle, strict=False, embed_metadata=False)
    assert report.text.rstrip() == expected.rstrip()


def test_pipeline_parity__render_thoracentesis_cxr_ordered(monkeypatch) -> None:
    env_overrides = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        "ENABLE_UMLS_LINKER": "false",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "engine",
        "REGISTRY_SCHEMA_VERSION": "v3",
        "REGISTRY_AUDITOR_SOURCE": "raw_ml",
        "REGISTRY_USE_STUB_LLM": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REPORTER_DISABLE_LLM": "1",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)

    expected = _read_fixture("render_thoracentesis_cxr_ordered.md")

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

    bundle, _issues, _warnings, _suggestions, _notes = _verify_bundle(bundle)

    engine = _pipeline_engine()
    report = ReportPipeline(engine).run(bundle, strict=False, embed_metadata=False)
    assert report.text.rstrip() == expected.rstrip()


def test_pipeline_parity__seed_from_text_ion_nav_tbna_cryo(monkeypatch) -> None:
    env_overrides = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
        "ENABLE_UMLS_LINKER": "false",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SCHEMA_VERSION": "v3",
        "REGISTRY_AUDITOR_SOURCE": "raw_ml",
        "REGISTRY_USE_STUB_LLM": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REPORTER_DISABLE_LLM": "1",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)

    note_text = (
        "Ion bronchoscopy RUL 2.2 cm nodule. Tool in lesion confirmed with CBCT. "
        "TBNA and cryobiopsy. ROSE + for malignancy"
    )
    expected = _read_fixture("seed_from_text_ion_nav_tbna_cryo.md")

    extraction_result = RegistryService().extract_fields(note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)
    bundle, _issues, _warnings, _suggestions, _notes = _verify_bundle(bundle)

    engine = _pipeline_engine()
    report = ReportPipeline(engine).run(bundle, strict=False, embed_metadata=False)
    assert report.text.rstrip() == expected.rstrip()

