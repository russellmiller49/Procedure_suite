"""Tests for the /health endpoint.

These tests verify that the health endpoint works correctly
regardless of NLP warmup status, metrics configuration, etc.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from modules.api.fastapi_app import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_ok(self, client):
        """Test that /health returns 200 with ok=true."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data == {"ok": True}

    def test_health_independent_of_metrics_backend(self, client):
        """Test that /health works regardless of METRICS_BACKEND setting."""
        # Test with null backend
        with patch.dict(os.environ, {"METRICS_BACKEND": "null"}, clear=False):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"ok": True}

        # Test with prometheus backend
        with patch.dict(os.environ, {"METRICS_BACKEND": "prometheus"}, clear=False):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"ok": True}

    def test_health_is_fast(self, client):
        """Test that /health responds quickly (no heavy operations)."""
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should respond in under 100ms (very generous for a simple endpoint)
        assert elapsed < 0.1, f"/health took {elapsed:.3f}s, expected < 0.1s"
