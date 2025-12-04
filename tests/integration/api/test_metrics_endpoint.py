"""Tests for the /metrics endpoint.

These tests verify that the metrics endpoint works correctly with
different METRICS_BACKEND configurations.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from modules.api.fastapi_app import app
from observability.metrics import (
    get_metrics_client,
    set_metrics_client,
    reset_metrics_client,
    RegistryMetricsClient,
    NullMetricsClient,
)


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics client before and after each test."""
    reset_metrics_client()
    yield
    reset_metrics_client()


# ============================================================================
# Metrics Status Tests
# ============================================================================


class TestMetricsStatus:
    """Tests for GET /metrics/status."""

    def test_status_with_null_backend(self, client):
        """Test status endpoint with default null backend."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "null"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics/status")

        assert response.status_code == 200
        data = response.json()
        assert data["client_type"] == "NullMetricsClient"
        assert data["backend"] == "null"

    def test_status_with_registry_backend(self, client):
        """Test status endpoint with registry backend."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics/status")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["client_type"] == "RegistryMetricsClient"
        assert "counters_count" in data


# ============================================================================
# Prometheus Export Tests
# ============================================================================


class TestPrometheusExport:
    """Tests for GET /metrics (Prometheus format)."""

    def test_metrics_disabled_returns_404(self, client):
        """Test that metrics endpoint returns 404 when disabled."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "null", "METRICS_ENABLED": "false"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics")

        assert response.status_code == 404
        assert "disabled" in response.text.lower()

    def test_metrics_enabled_with_registry(self, client):
        """Test Prometheus export with registry backend."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "prometheus"}, clear=False):
            reset_metrics_client()

            # Record some metrics
            metrics_client = get_metrics_client()
            assert isinstance(metrics_client, RegistryMetricsClient)

            metrics_client.incr("test.counter", {"label": "value"}, 5)
            metrics_client.timing("test.latency", 150.5, {"endpoint": "test"})

            response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

        # Check Prometheus format
        text = response.text
        assert "# TYPE" in text
        assert "proc_suite_test_counter_total" in text
        assert "proc_suite_test_latency" in text

    def test_metrics_content_type(self, client):
        """Test that Prometheus export uses correct content type."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "version=0.0.4" in response.headers["content-type"]


# ============================================================================
# JSON Export Tests
# ============================================================================


class TestJsonExport:
    """Tests for GET /metrics/json."""

    def test_json_export_disabled(self, client):
        """Test JSON export when metrics disabled."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "null", "METRICS_ENABLED": "false"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics/json")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False

    def test_json_export_with_registry(self, client):
        """Test JSON export with registry backend."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()

            # Record some metrics
            metrics_client = get_metrics_client()
            metrics_client.incr("json.test.counter", {"key": "val"}, 3)
            metrics_client.observe("json.test.gauge", 0.75, {"type": "test"})

            response = client.get("/metrics/json")

        assert response.status_code == 200
        data = response.json()

        assert data["enabled"] is True
        assert data["backend"] == "registry"
        assert "counters" in data
        assert "gauges" in data
        assert "histograms" in data

        # Check counter was recorded
        assert "json.test.counter" in data["counters"]


# ============================================================================
# Registry Metrics Client Unit Tests
# ============================================================================


class TestRegistryMetricsClient:
    """Unit tests for RegistryMetricsClient."""

    def test_counter_increment(self):
        """Test counter increment."""
        client = RegistryMetricsClient()

        client.incr("requests", {"method": "GET"})
        client.incr("requests", {"method": "GET"}, 2)
        client.incr("requests", {"method": "POST"})

        json_data = client.export_json()
        assert json_data["counters"]["requests"]['{method="GET"}'] == 3
        assert json_data["counters"]["requests"]['{method="POST"}'] == 1

    def test_gauge_observation(self):
        """Test gauge observation (last value wins)."""
        client = RegistryMetricsClient()

        client.observe("cpu_usage", 0.5, {"host": "server1"})
        client.observe("cpu_usage", 0.7, {"host": "server1"})

        json_data = client.export_json()
        assert json_data["gauges"]["cpu_usage"]['{host="server1"}'] == 0.7

    def test_histogram_timing(self):
        """Test histogram timing."""
        client = RegistryMetricsClient()

        client.timing("latency", 50.0, {"endpoint": "/api"})
        client.timing("latency", 150.0, {"endpoint": "/api"})
        client.timing("latency", 500.0, {"endpoint": "/api"})

        json_data = client.export_json()
        hist_data = json_data["histograms"]["latency"]['{endpoint="/api"}']

        assert hist_data["_count"] == 3
        assert hist_data["_sum"] == 700.0
        assert hist_data["le_+Inf"] == 3  # All values should be in +Inf bucket

    def test_prometheus_export_format(self):
        """Test Prometheus text format export."""
        client = RegistryMetricsClient()

        client.incr("http_requests", {"status": "200"}, 10)
        client.timing("request_duration", 100.0, {"path": "/test"})

        text = client.export_prometheus()

        # Check counter format
        assert "# TYPE proc_suite_http_requests_total counter" in text
        assert 'proc_suite_http_requests_total{status="200"} 10' in text

        # Check histogram format
        assert "# TYPE proc_suite_request_duration histogram" in text
        assert "proc_suite_request_duration_bucket" in text
        assert "proc_suite_request_duration_sum" in text
        assert "proc_suite_request_duration_count" in text

    def test_reset(self):
        """Test metrics reset."""
        client = RegistryMetricsClient()

        client.incr("counter", value=5)
        client.observe("gauge", 1.0)
        client.timing("timer", 100.0)

        json_before = client.export_json()
        assert len(json_before["counters"]) == 1

        client.reset()

        json_after = client.export_json()
        assert len(json_after["counters"]) == 0
        assert len(json_after["gauges"]) == 0
        assert len(json_after["histograms"]) == 0

    def test_no_tags(self):
        """Test metrics without tags."""
        client = RegistryMetricsClient()

        client.incr("simple_counter")
        client.observe("simple_gauge", 42.0)

        json_data = client.export_json()
        assert json_data["counters"]["simple_counter"][""] == 1
        assert json_data["gauges"]["simple_gauge"][""] == 42.0


# ============================================================================
# Integration with CodingMetrics
# ============================================================================


class TestCodingMetricsIntegration:
    """Test that CodingMetrics work with RegistryMetricsClient."""

    def test_coding_metrics_recorded(self, client):
        """Test that coding metrics are recorded when using registry backend."""
        from observability.coding_metrics import CodingMetrics

        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()

            # Record coding metrics
            CodingMetrics.record_suggestions_generated(
                num_suggestions=3,
                procedure_type="bronch_ebus",
                used_llm=True,
            )
            CodingMetrics.record_pipeline_latency(
                latency_ms=250.5,
                procedure_type="bronch_ebus",
                used_llm=True,
            )

            # Get metrics via endpoint
            response = client.get("/metrics/json")

        assert response.status_code == 200
        data = response.json()

        # Check counter
        assert "coder.suggestions_total" in data["counters"]

        # Check histogram
        assert "coder.pipeline_latency_ms" in data["histograms"]


# ============================================================================
# LLM Drift Metrics Tests
# ============================================================================


class TestLLMDriftEndpoint:
    """Tests for GET /metrics/llm_drift endpoint."""

    def test_llm_drift_disabled_backend(self, client):
        """Test llm_drift endpoint when metrics disabled."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "null", "METRICS_ENABLED": "false"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics/llm_drift")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False

    def test_llm_drift_empty_registry(self, client):
        """Test llm_drift endpoint with no recorded metrics."""
        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()
            response = client.get("/metrics/llm_drift")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["total_reviewed"] == 0
        assert data["total_accepted"] == 0
        assert data["overall_acceptance_rate"] == 0.0
        assert data["by_procedure_type"] == []

    def test_llm_drift_with_acceptance_data(self, client):
        """Test llm_drift endpoint after recording acceptance metrics."""
        from observability.coding_metrics import CodingMetrics

        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()

            # Simulate reviews: 3 accepted, 1 rejected for bronch_ebus
            CodingMetrics.record_llm_acceptance(
                accepted_count=3,
                reviewed_count=4,
                procedure_type="bronch_ebus",
                source="hybrid",
            )

            # Another type: 1 accepted, 1 rejected for pleural
            CodingMetrics.record_llm_acceptance(
                accepted_count=1,
                reviewed_count=2,
                procedure_type="pleural",
                source="llm",
            )

            response = client.get("/metrics/llm_drift")

        assert response.status_code == 200
        data = response.json()

        assert data["enabled"] is True
        assert data["total_reviewed"] == 6
        assert data["total_accepted"] == 4
        # 4/6 = 0.6667
        assert 0.66 <= data["overall_acceptance_rate"] <= 0.67

        # Check breakdown
        assert len(data["by_procedure_type"]) == 2

        # Find bronch_ebus entry
        ebus_entry = next(
            (d for d in data["by_procedure_type"] if d["procedure_type"] == "bronch_ebus"),
            None,
        )
        assert ebus_entry is not None
        assert ebus_entry["reviewed"] == 4
        assert ebus_entry["accepted"] == 3
        assert ebus_entry["acceptance_rate"] == 0.75

    def test_llm_drift_manual_codes_not_counted(self, client):
        """Test that manual codes don't affect LLM drift metrics."""
        from observability.coding_metrics import CodingMetrics

        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()

            # Record some LLM acceptance
            CodingMetrics.record_llm_acceptance(
                accepted_count=2,
                reviewed_count=3,
                procedure_type="bronch_diagnostic",
                source="llm",
            )

            # Manual code additions (these use record_manual_code_added, not record_llm_acceptance)
            CodingMetrics.record_manual_code_added(procedure_type="bronch_diagnostic")
            CodingMetrics.record_manual_code_added(procedure_type="bronch_diagnostic")

            response = client.get("/metrics/llm_drift")

        assert response.status_code == 200
        data = response.json()

        # Only the LLM acceptance should be counted
        assert data["total_reviewed"] == 3
        assert data["total_accepted"] == 2

    def test_record_llm_acceptance_zero_reviewed(self, client):
        """Test that record_llm_acceptance with 0 reviewed is a no-op."""
        from observability.coding_metrics import CodingMetrics

        with patch.dict(os.environ, {"METRICS_BACKEND": "registry"}, clear=False):
            reset_metrics_client()

            # This should be ignored
            CodingMetrics.record_llm_acceptance(
                accepted_count=0,
                reviewed_count=0,
                procedure_type="unknown",
            )

            response = client.get("/metrics/llm_drift")

        assert response.status_code == 200
        data = response.json()
        assert data["total_reviewed"] == 0
