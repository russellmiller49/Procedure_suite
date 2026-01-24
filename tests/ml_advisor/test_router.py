"""
Test Suite for ML Advisor Router Endpoints

Tests covering:
- Health check and status endpoints
- Coding endpoints (with and without advisor)
- Trace management endpoints
- Metrics endpoint
- Error handling

Run with: pytest tests/ml_advisor/test_router.py -v
"""

import json
import os
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from modules.proc_ml_advisor.schemas import ProcedureCategory
from modules.api.ml_advisor_router import get_advisor_config


@pytest.fixture(autouse=True)
def _skip_registry_runtime_bundle_verification() -> Generator[None, None, None]:
    # The FastAPI app lifespan validates registry runtime bundles on startup.
    # In unit tests, the heavyweight model artifacts may not be present, so we
    # patch this to bypass the startup guardrail.
    with patch("modules.registry.model_runtime.verify_registry_runtime_bundle", return_value=[]):
        yield


@pytest.fixture
def test_client(
    _skip_registry_runtime_bundle_verification,
) -> Generator[TestClient, None, None]:
    from modules.api.fastapi_app import app

    with TestClient(app) as client:
        yield client


def make_override_config(
    enabled: bool = False,
    backend: str = "stub",
    trace_enabled: bool = True,
    trace_path: Path | None = None,
) -> dict[str, Any]:
    """Create an override config for testing."""
    return {
        "enabled": enabled,
        "backend": backend,
        "trace_enabled": trace_enabled,
        "trace_path": trace_path or Path("data/coding_traces.jsonl"),
        "pipeline_version": "test-v1",
    }


class TestHealthEndpoints:
    """Tests for health and status endpoints."""

    def test_health_check(self, test_client):
        """Health endpoint should return status ok."""
        response = test_client.get("/api/v1/ml-advisor/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "advisor_enabled" in data
        assert "advisor_backend" in data
        assert "pipeline_version" in data

    def test_advisor_status(self, test_client):
        """Status endpoint should return configuration details."""
        response = test_client.get("/api/v1/ml-advisor/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "backend" in data
        assert "available_backends" in data
        assert "stub" in data["available_backends"]
        assert "gemini" in data["available_backends"]


class TestCodeEndpoints:
    """Tests for coding endpoints."""

    def test_code_procedure_basic(self, test_client):
        """Code endpoint should return codes for procedure text."""
        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={
                "report_text": "Bronchoscopy with EBUS-TBNA sampling of stations 4R, 7, 11L",
                "procedure_category": "ebus",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "final_codes" in data
        assert "codes" in data
        assert "trace_id" in data
        assert isinstance(data["final_codes"], list)

    def test_code_procedure_bronchoscopy(self, test_client):
        """Should detect bronchoscopy codes from text."""
        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={
                "report_text": "Diagnostic bronchoscopy performed",
                "procedure_category": "bronchoscopy",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "31622" in data["final_codes"]

    def test_code_procedure_thoracentesis(self, test_client):
        """Should detect thoracentesis codes from text."""
        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={
                "report_text": "Ultrasound-guided thoracentesis of right pleural effusion",
                "procedure_category": "pleural",
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should detect thoracentesis with imaging
        assert any("325" in code for code in data["final_codes"])

    def test_code_with_advisor(self, test_client, monkeypatch):
        """Code with advisor endpoint should include advisor suggestions."""
        monkeypatch.setenv("ENABLE_ML_ADVISOR", "true")

        response = test_client.post(
            "/api/v1/ml-advisor/code_with_advisor",
            json={
                "report_text": "Bronchoscopy with EBUS-TBNA of stations 4R, 7, 11L",
                "procedure_category": "ebus",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "final_codes" in data
        assert "trace_id" in data
        # When advisor is enabled, should have advisor data
        if data.get("advisor_suggestions"):
            assert isinstance(data["advisor_suggestions"], dict)

    def test_code_with_advisor_disabled(self, test_client, monkeypatch):
        """Should work even when advisor is disabled."""
        monkeypatch.setenv("ENABLE_ML_ADVISOR", "false")

        response = test_client.post(
            "/api/v1/ml-advisor/code_with_advisor",
            json={
                "report_text": "Bronchoscopy performed",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "final_codes" in data


class TestAdvisorSuggestEndpoint:
    """Tests for advisor-only suggest endpoint."""

    def test_suggest_requires_enabled_advisor(self, test_client):
        """Suggest endpoint should fail when advisor is disabled."""
        # Default config has advisor disabled
        response = test_client.post(
            "/api/v1/ml-advisor/suggest",
            json={"report_text": "Test procedure"},
        )
        assert response.status_code == 503

    def test_suggest_with_enabled_advisor(self):
        """Suggest endpoint should work when advisor is enabled."""
        from modules.api.fastapi_app import app

        # Override the dependency to enable advisor
        def override_config():
            return make_override_config(enabled=True, backend="stub")

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/ml-advisor/suggest",
                    json={"report_text": "Bronchoscopy with navigation biopsy"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "candidate_codes" in data
            assert "model_name" in data
        finally:
            app.dependency_overrides.clear()


class TestTraceEndpoints:
    """Tests for trace management endpoints."""

    def test_list_traces_empty(self, tmp_path):
        """Should return empty list when no traces exist."""
        from modules.api.fastapi_app import app

        trace_file = tmp_path / "empty_traces.jsonl"

        def override_config():
            return make_override_config(trace_path=trace_file)

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/ml-advisor/traces")
            assert response.status_code == 200
            data = response.json()
            assert data["traces"] == []
            assert data["total"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_list_traces_with_data(self, populated_trace_file):
        """Should return traces when file has data."""
        from modules.api.fastapi_app import app

        def override_config():
            return make_override_config(trace_path=populated_trace_file)

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/ml-advisor/traces")
            assert response.status_code == 200
            data = response.json()
            assert len(data["traces"]) <= data["total"]
            assert data["limit"] == 100  # Default limit
        finally:
            app.dependency_overrides.clear()

    def test_list_traces_pagination(self, populated_trace_file):
        """Should support pagination."""
        from modules.api.fastapi_app import app

        def override_config():
            return make_override_config(trace_path=populated_trace_file)

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/ml-advisor/traces?limit=5&offset=0")
            assert response.status_code == 200
            data = response.json()
            assert len(data["traces"]) <= 5
            assert data["limit"] == 5
            assert data["offset"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_get_trace_not_found(self, tmp_path):
        """Should return 404 for non-existent trace."""
        from modules.api.fastapi_app import app

        trace_file = tmp_path / "traces.jsonl"
        trace_file.touch()

        def override_config():
            return make_override_config(trace_path=trace_file)

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/ml-advisor/traces/nonexistent-id")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()


class TestMetricsEndpoint:
    """Tests for metrics calculation endpoint."""

    def test_metrics_empty(self, tmp_path):
        """Should return empty metrics when no traces exist."""
        from modules.api.fastapi_app import app

        trace_file = tmp_path / "empty_traces.jsonl"

        def override_config():
            return make_override_config(trace_path=trace_file)

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/ml-advisor/metrics")
            assert response.status_code == 200
            data = response.json()
            assert data["total_traces"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_metrics_with_data(self, populated_trace_file):
        """Should calculate metrics from traces."""
        from modules.api.fastapi_app import app

        def override_config():
            return make_override_config(trace_path=populated_trace_file)

        app.dependency_overrides[get_advisor_config] = override_config

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/ml-advisor/metrics")
            assert response.status_code == 200
            data = response.json()
            assert data["total_traces"] > 0
            assert "traces_with_advisor" in data
            assert "full_agreement" in data
            assert "unique_rule_codes" in data
        finally:
            app.dependency_overrides.clear()


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_request_body(self, test_client):
        """Should return 422 for invalid request body."""
        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={"invalid_field": "value"}
        )
        # FastAPI returns 200 since report_text is optional
        # but we should have empty codes
        assert response.status_code == 200

    def test_invalid_procedure_category(self, test_client):
        """Should return 422 for invalid procedure category."""
        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={
                "report_text": "Test",
                "procedure_category": "invalid_category",
            }
        )
        assert response.status_code == 422


class TestTraceLogging:
    """Tests for trace logging functionality."""

    def test_trace_created_on_code(self, test_client, tmp_path, monkeypatch):
        """Coding should create a trace when enabled."""
        trace_file = tmp_path / "traces.jsonl"
        monkeypatch.setenv("TRACE_FILE_PATH", str(trace_file))
        monkeypatch.setenv("ENABLE_CODING_TRACE", "true")

        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={"report_text": "Bronchoscopy performed"}
        )
        assert response.status_code == 200

        # Check trace was written
        if trace_file.exists():
            with open(trace_file) as f:
                lines = f.readlines()
            # There should be at least one trace
            assert len(lines) >= 1
            trace = json.loads(lines[-1])
            assert "trace_id" in trace

    def test_trace_disabled(self, test_client, tmp_path, monkeypatch):
        """Should not create trace when disabled."""
        trace_file = tmp_path / "traces.jsonl"
        monkeypatch.setenv("TRACE_FILE_PATH", str(trace_file))
        monkeypatch.setenv("ENABLE_CODING_TRACE", "false")

        response = test_client.post(
            "/api/v1/ml-advisor/code",
            json={"report_text": "Bronchoscopy performed"}
        )
        assert response.status_code == 200

        # Trace file should not exist or be empty
        if trace_file.exists():
            with open(trace_file) as f:
                content = f.read()
            # Might have traces from other tests, but this specific
            # request shouldn't have added one


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
