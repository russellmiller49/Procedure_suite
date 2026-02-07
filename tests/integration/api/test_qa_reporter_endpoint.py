"""Integration tests for /qa/run reporter module behavior."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fastapi.testclient import TestClient

from modules.api.dependencies import get_qa_pipeline_service
from modules.api.fastapi_app import app
from modules.api.services.qa_pipeline import (
    QAPipelineService,
    ReportingStrategy,
    SimpleReporterStrategy,
)
from modules.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    default_schema_registry,
    default_template_registry,
)
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine


# Keep API tests offline and deterministic.
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "1")


class _StaticRegistryEngine:
    def __init__(self, record: dict[str, Any]) -> None:
        self._record = record

    def run(self, text: str, explain: bool = False) -> dict[str, Any]:
        return dict(self._record)


class _FailingRegistryEngine:
    def run(self, text: str, explain: bool = False) -> dict[str, Any]:
        raise RuntimeError("simulated registry failure")


class _DummyCodingService:
    def generate_result(self, **kwargs: Any) -> Any:  # pragma: no cover - not used in reporter-only tests
        raise AssertionError("Coding service should not run in reporter-only tests")


def _sample_record() -> dict[str, Any]:
    return {
        "procedure_date": "2026-01-15",
        "attending_name": "Alex Clinician, MD",
        "referred_physician": "Referring MD",
        "primary_indication": "Peripheral lung nodule with mediastinal adenopathy",
        "procedures": [
            {
                "proc_type": "ebus_tbna",
                "schema_id": "ebus_tbna_v1",
                "proc_id": "ebus_1",
                "data": {
                    "needle_gauge": "22G",
                    "stations": [
                        {
                            "station_name": "4R",
                            "passes": 3,
                            "size_mm": 10,
                            "biopsy_tools": ["TBNA"],
                        }
                    ],
                },
                "cpt_candidates": ["31652"],
            }
        ],
    }


def _build_service(registry_engine: Any) -> QAPipelineService:
    templates = default_template_registry()
    schemas = default_schema_registry()
    reporter_engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    reporting_strategy = ReportingStrategy(
        reporter_engine=reporter_engine,
        inference_engine=InferenceEngine(),
        validation_engine=ValidationEngine(templates, schemas),
        registry_engine=registry_engine,
        simple_strategy=SimpleReporterStrategy(),
    )
    return QAPipelineService(
        registry_engine=registry_engine,
        reporting_strategy=reporting_strategy,
        coding_service=_DummyCodingService(),
    )


@pytest.fixture(autouse=True)
def _clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _reporter_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_BACKEND", "onnx")
    monkeypatch.setenv("PROCSUITE_SKIP_WARMUP", "1")


def test_qa_run_reporter_structured_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QA_REPORTER_ALLOW_SIMPLE_FALLBACK", raising=False)
    service = _build_service(_StaticRegistryEngine(_sample_record()))
    app.dependency_overrides[get_qa_pipeline_service] = lambda: service

    with TestClient(app) as client:
        response = client.post(
            "/qa/run",
            json={
                "note_text": "EBUS-TBNA performed at station 4R.",
                "modules_run": "reporter",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reporter"]["status"] == "success"
    reporter_data = payload["reporter"]["data"]
    assert reporter_data["fallback_used"] is False
    assert reporter_data["render_mode"] == "structured"
    assert reporter_data["fallback_reason"] is None
    assert reporter_data["reporter_errors"] == []
    assert "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT" in reporter_data["markdown"]


def test_qa_run_reporter_structured_error_when_fallback_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("QA_REPORTER_ALLOW_SIMPLE_FALLBACK", raising=False)
    service = _build_service(_FailingRegistryEngine())
    app.dependency_overrides[get_qa_pipeline_service] = lambda: service

    with TestClient(app) as client:
        response = client.post(
            "/qa/run",
            json={
                "note_text": "EBUS-TBNA performed at station 4R.",
                "modules_run": "reporter",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reporter"]["status"] == "error"
    assert (
        payload["reporter"]["error_code"] == "REPORTER_STRUCTURED_RENDER_ERROR"
    )
    assert payload["reporter"]["data"] is None


def test_qa_run_reporter_simple_fallback_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QA_REPORTER_ALLOW_SIMPLE_FALLBACK", "1")
    service = _build_service(_FailingRegistryEngine())
    app.dependency_overrides[get_qa_pipeline_service] = lambda: service

    with TestClient(app) as client:
        response = client.post(
            "/qa/run",
            json={
                "note_text": "EBUS-TBNA performed at station 4R.",
                "modules_run": "reporter",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reporter"]["status"] == "success"
    reporter_data = payload["reporter"]["data"]
    assert reporter_data["fallback_used"] is True
    assert reporter_data["render_mode"] == "simple_fallback"
    assert reporter_data["fallback_reason"] == "structured_unavailable"
    assert reporter_data["reporter_errors"]
