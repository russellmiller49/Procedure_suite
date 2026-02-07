from __future__ import annotations

from dataclasses import dataclass

import pytest
from httpx import AsyncClient

from app.api.dependencies import get_qa_pipeline_service
from app.api.fastapi_app import app
from app.api.services.qa_pipeline import QAPipelineService, ReportingStrategy, SimpleReporterStrategy
from app.reporting.inference import InferenceEngine


@dataclass
class _DummyRecord:
    def model_dump(self) -> dict:
        return {"source_text": "test note"}


class _DummyRegistryEngine:
    def run(self, _text: str, *, explain: bool = False):  # noqa: ANN001
        return _DummyRecord()


class _DummyValidationEngine:
    def list_missing_critical_fields(self, _bundle):  # noqa: ANN001
        return []

    def apply_warn_if_rules(self, _bundle):  # noqa: ANN001
        return []


class _FailingReporterEngine:
    def compose_report_with_metadata(self, *_args, **_kwargs):  # noqa: ANN001
        raise RuntimeError("simulated reporter failure")


pytestmark = pytest.mark.asyncio


async def test_qa_run_returns_error_when_fallback_disabled(monkeypatch: pytest.MonkeyPatch, api_client: AsyncClient) -> None:
    monkeypatch.delenv("QA_REPORTER_ALLOW_SIMPLE_FALLBACK", raising=False)

    def _override_service() -> QAPipelineService:
        registry_engine = _DummyRegistryEngine()
        reporting_strategy = ReportingStrategy(
            reporter_engine=_FailingReporterEngine(),
            inference_engine=InferenceEngine(),
            validation_engine=_DummyValidationEngine(),
            registry_engine=registry_engine,
            simple_strategy=SimpleReporterStrategy(),
        )
        return QAPipelineService(
            registry_engine=registry_engine,
            reporting_strategy=reporting_strategy,
            coding_service=object(),
        )

    app.dependency_overrides[get_qa_pipeline_service] = _override_service
    try:
        response = await api_client.post("/qa/run", json={"note_text": "test note", "modules_run": "reporter"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["overall_status"] == "failed"
        assert payload["reporter"]["status"] == "error"
        assert payload["reporter"]["data"] is None
    finally:
        app.dependency_overrides.clear()


async def test_qa_run_allows_simple_fallback_when_enabled(monkeypatch: pytest.MonkeyPatch, api_client: AsyncClient) -> None:
    monkeypatch.setenv("QA_REPORTER_ALLOW_SIMPLE_FALLBACK", "1")

    def _override_service() -> QAPipelineService:
        registry_engine = _DummyRegistryEngine()
        reporting_strategy = ReportingStrategy(
            reporter_engine=_FailingReporterEngine(),
            inference_engine=InferenceEngine(),
            validation_engine=_DummyValidationEngine(),
            registry_engine=registry_engine,
            simple_strategy=SimpleReporterStrategy(),
        )
        return QAPipelineService(
            registry_engine=registry_engine,
            reporting_strategy=reporting_strategy,
            coding_service=object(),
        )

    app.dependency_overrides[get_qa_pipeline_service] = _override_service
    try:
        response = await api_client.post("/qa/run", json={"note_text": "test note", "modules_run": "reporter"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["overall_status"] == "completed"
        assert payload["reporter"]["status"] == "success"
        data = payload["reporter"]["data"]
        assert data["fallback_used"] is True
        assert data["render_mode"] == "simple_fallback"
        assert data["fallback_reason"]
        assert any("simulated reporter failure" in msg for msg in (data.get("reporter_errors") or []))
        assert data["markdown"]
    finally:
        app.dependency_overrides.clear()
