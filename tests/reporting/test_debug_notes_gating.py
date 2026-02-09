from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI

import app.api.routes.reporting as reporting_routes
from app.api.routes.reporting import report_render, report_seed_from_text
from app.api.schemas import RenderRequest, SeedFromTextRequest
from app.reporting.engine import ReporterEngine, build_procedure_bundle_from_extraction


def _set_reporting_env(monkeypatch) -> None:
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


def _thoracentesis_extraction() -> dict[str, object]:
    return {
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


@pytest.mark.asyncio
async def test_render_response_debug_notes_omitted_by_default(monkeypatch) -> None:
    _set_reporting_env(monkeypatch)
    bundle = build_procedure_bundle_from_extraction(_thoracentesis_extraction())

    resp = await report_render(RenderRequest(bundle=bundle))
    payload = resp.model_dump()

    assert resp.debug_notes is None
    assert "debug_notes" not in payload


@pytest.mark.asyncio
async def test_render_response_debug_notes_included_when_enabled(monkeypatch) -> None:
    _set_reporting_env(monkeypatch)
    bundle = build_procedure_bundle_from_extraction(_thoracentesis_extraction())

    resp = await report_render(RenderRequest(bundle=bundle, debug=True))
    payload = resp.model_dump()

    assert "debug_notes" in payload
    note_types = {note.get("type") for note in payload["debug_notes"]}
    assert "normalization" in note_types
    assert "selection" in note_types


@pytest.mark.asyncio
async def test_strict_fallback_reason_included_in_debug_notes(monkeypatch) -> None:
    _set_reporting_env(monkeypatch)
    bundle = build_procedure_bundle_from_extraction(_thoracentesis_extraction())

    original = ReporterEngine.compose_report_with_metadata

    def _patched_compose(self, bundle, *, strict: bool = False, **kwargs):
        if strict:
            raise ValueError("Style validation failed: forced for debug note test")
        return original(self, bundle, strict=strict, **kwargs)

    monkeypatch.setattr(ReporterEngine, "compose_report_with_metadata", _patched_compose)

    resp = await report_render(RenderRequest(bundle=bundle, strict=True, debug=True))
    payload = resp.model_dump()

    assert "debug_notes" in payload
    note_types = {note.get("type") for note in payload["debug_notes"]}
    assert "strict_fallback" in note_types


@pytest.mark.asyncio
async def test_seed_from_text_debug_notes_gated(monkeypatch) -> None:
    _set_reporting_env(monkeypatch)

    extraction = _thoracentesis_extraction()

    async def _fake_run_cpu(app, fn, *args, **kwargs):
        return SimpleNamespace(record=extraction)

    monkeypatch.setattr(reporting_routes, "run_cpu", _fake_run_cpu)

    dummy_request = SimpleNamespace(app=FastAPI())
    dummy_registry_service = SimpleNamespace(extract_fields=lambda _text: None)

    resp = await report_seed_from_text(
        SeedFromTextRequest(text="Thoracentesis performed."),
        request=dummy_request,
        _ready=None,
        registry_service=dummy_registry_service,
        phi_scrubber=None,
    )
    payload = resp.model_dump()
    assert resp.debug_notes is None
    assert "debug_notes" not in payload

    resp_debug = await report_seed_from_text(
        SeedFromTextRequest(text="Thoracentesis performed.", debug=True),
        request=dummy_request,
        _ready=None,
        registry_service=dummy_registry_service,
        phi_scrubber=None,
    )
    payload_debug = resp_debug.model_dump()
    assert "debug_notes" in payload_debug
    note_types = {note.get("type") for note in payload_debug["debug_notes"]}
    assert "normalization" in note_types
    assert "selection" in note_types
