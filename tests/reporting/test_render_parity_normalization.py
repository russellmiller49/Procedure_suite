"""Legacy filename retained for continuity.

Authoritative reporter parity now lives in the dual-path evaluation matrix and
shared compare artifacts. This module covers the verify-and-render wrapper path:
normalization, validation, and strict rendering should stay actionable and
fallback-free on the fixed smoke cases below.
"""

from __future__ import annotations

from proc_schemas.clinical import BundlePatch

from app.api.routes.reporting import _verify_bundle
from app.registry.application.registry_service import RegistryService
from app.reporting.engine import apply_bundle_patch, build_procedure_bundle_from_extraction
from app.reporting.seed_pipeline import render_bundle_markdown


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


def _verify_and_render(bundle) -> str:
    bundle, issues, warnings, _suggestions, _notes = _verify_bundle(bundle)
    markdown, fallback_used, fallback_info = render_bundle_markdown(
        bundle,
        issues=issues,
        warnings=warnings,
        strict=True,
        embed_metadata=False,
    )
    assert fallback_used is False
    assert fallback_info is None
    assert "{{" not in markdown
    assert "}}" not in markdown
    return markdown


def test_render_smoke__seed_from_text_ebus_station7(monkeypatch) -> None:
    _configure_env(monkeypatch)

    note_text = "EBUS biopsied station 7"
    extraction_result = RegistryService().extract_fields(note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)

    markdown = _verify_and_render(bundle)

    assert "Endobronchial Ultrasound-Guided Transbronchial Needle Aspiration (EBUS-TBNA) (Stations 7)" in markdown
    assert "A systematic EBUS survey was performed." in markdown
    assert "Station: 7" in markdown
    assert "[indication]" not in markdown


def test_render_smoke__render_thoracentesis_cxr_ordered(monkeypatch) -> None:
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
    patch = BundlePatch.model_validate(
        {"procedures": [{"proc_id": proc_id, "updates": {"cxr_ordered": True}}]}
    )
    bundle = apply_bundle_patch(bundle, patch)

    markdown = _verify_and_render(bundle)

    assert "Thoracentesis (Detailed)" in markdown
    assert "A post-procedure chest x-ray was ordered." in markdown
    assert "Successful left thoracentesis with 900 mL removed (serous)." in markdown
    assert "Await final pathology and cytology." not in markdown


def test_render_smoke__seed_from_text_ion_nav_tbna_cryo(monkeypatch) -> None:
    _configure_env(monkeypatch)

    note_text = (
        "Ion bronchoscopy RUL 2.2 cm nodule. Tool in lesion confirmed with CBCT. "
        "TBNA and cryobiopsy. ROSE + for malignancy"
    )
    extraction_result = RegistryService().extract_fields(note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)

    markdown = _verify_and_render(bundle)

    assert "Robotic navigational bronchoscopy (Ion) to RUL target" in markdown
    assert "Transbronchial Cryobiopsy (RUL)" in markdown
    assert "TBNA of RUL target" in markdown
    assert "Tool-in-lesion was confirmed with Cone Beam CT." in markdown
    assert "Successful transbronchial cryobiopsy of RUL for diagnostic evaluation of peripheral lung lesion." in markdown
