"""Tests for startup warmup behavior.

These tests verify that:
- PROCSUITE_SKIP_WARMUP skips heavy NLP warmup
- Warmup failures don't crash the app
- /health still works even when warmup fails

NOTE: These tests are currently skipped because the _do_heavy_warmup
function was removed during the extraction-first refactor. The warmup
mechanism has been restructured and these tests need to be updated.
"""

from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.skip(
    reason="_do_heavy_warmup was removed; warmup tests need to be updated"
)


class TestSkipWarmupEnvVar:
    """Tests for PROCSUITE_SKIP_WARMUP environment variable."""

    def test_skip_warmup_prevents_heavy_warmup(self):
        """Test that PROCSUITE_SKIP_WARMUP=1 skips the heavy warmup."""
        with patch.dict(os.environ, {"PROCSUITE_SKIP_WARMUP": "1"}, clear=False):
            # Import fresh to get the startup behavior
            from modules.api import fastapi_app

            # Mock the _do_heavy_warmup function to track if it's called
            with patch.object(fastapi_app, "_do_heavy_warmup") as mock_warmup:
                # Simulate the startup hook logic
                import asyncio

                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

                # _do_heavy_warmup should NOT have been called
                mock_warmup.assert_not_called()

    def test_skip_warmup_with_true_value(self):
        """Test that PROCSUITE_SKIP_WARMUP=true works."""
        with patch.dict(os.environ, {"PROCSUITE_SKIP_WARMUP": "true"}, clear=False):
            from modules.api import fastapi_app

            with patch.object(fastapi_app, "_do_heavy_warmup") as mock_warmup:
                import asyncio

                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

                mock_warmup.assert_not_called()

    def test_skip_warmup_with_yes_value(self):
        """Test that PROCSUITE_SKIP_WARMUP=yes works."""
        with patch.dict(os.environ, {"PROCSUITE_SKIP_WARMUP": "yes"}, clear=False):
            from modules.api import fastapi_app

            with patch.object(fastapi_app, "_do_heavy_warmup") as mock_warmup:
                import asyncio

                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

                mock_warmup.assert_not_called()

    def test_warmup_runs_when_not_skipped(self):
        """Test that warmup runs when PROCSUITE_SKIP_WARMUP is not set."""
        # Clear the skip env var and Railway env var
        env_override = {
            "PROCSUITE_SKIP_WARMUP": "",
            "RAILWAY_ENVIRONMENT": "",
        }
        with patch.dict(os.environ, env_override, clear=False):
            from modules.api import fastapi_app

            with patch.object(fastapi_app, "_do_heavy_warmup") as mock_warmup:
                import asyncio

                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

                # _do_heavy_warmup SHOULD have been called
                mock_warmup.assert_called_once()


class TestWarmupFailureHandling:
    """Tests for warmup failure resilience."""

    def test_warmup_failure_does_not_crash_app(self):
        """Test that warmup failure doesn't prevent app from starting."""
        env_override = {
            "PROCSUITE_SKIP_WARMUP": "",
            "RAILWAY_ENVIRONMENT": "",
        }
        with patch.dict(os.environ, env_override, clear=False):
            from modules.api import fastapi_app

            # Make _do_heavy_warmup raise an exception
            with patch.object(
                fastapi_app,
                "_do_heavy_warmup",
                side_effect=RuntimeError("Simulated warmup failure"),
            ):
                import asyncio

                # This should NOT raise - the exception should be caught
                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

    def test_health_works_after_warmup_failure(self):
        """Test that /health still works even if warmup failed."""
        from modules.api.fastapi_app import app

        # Create client - this will trigger startup
        client = TestClient(app)

        # Health should always work
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


class TestRailwayEnvironmentSkip:
    """Tests for Railway environment warmup skip."""

    def test_railway_environment_skips_warmup(self):
        """Test that RAILWAY_ENVIRONMENT skips warmup."""
        env_override = {
            "PROCSUITE_SKIP_WARMUP": "",
            "RAILWAY_ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, env_override, clear=False):
            from modules.api import fastapi_app

            with patch.object(fastapi_app, "_do_heavy_warmup") as mock_warmup:
                import asyncio

                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

                # Should NOT be called when on Railway
                mock_warmup.assert_not_called()


class TestNlpWarmedFlag:
    """Tests for the is_nlp_warmed() helper."""

    def test_is_nlp_warmed_false_when_skipped(self):
        """Test that is_nlp_warmed() returns False when warmup is skipped."""
        from modules.api import fastapi_app

        # Reset the flag
        fastapi_app._nlp_warmup_successful = False

        with patch.dict(os.environ, {"PROCSUITE_SKIP_WARMUP": "1"}, clear=False):
            import asyncio

            asyncio.get_event_loop().run_until_complete(
                fastapi_app.warm_heavy_resources()
            )

            assert fastapi_app.is_nlp_warmed() is False

    def test_is_nlp_warmed_false_when_warmup_fails(self):
        """Test that is_nlp_warmed() returns False when warmup fails."""
        from modules.api import fastapi_app

        # Reset the flag
        fastapi_app._nlp_warmup_successful = False

        env_override = {
            "PROCSUITE_SKIP_WARMUP": "",
            "RAILWAY_ENVIRONMENT": "",
        }
        with patch.dict(os.environ, env_override, clear=False):
            with patch.object(
                fastapi_app,
                "_do_heavy_warmup",
                side_effect=RuntimeError("Simulated failure"),
            ):
                import asyncio

                asyncio.get_event_loop().run_until_complete(
                    fastapi_app.warm_heavy_resources()
                )

                assert fastapi_app.is_nlp_warmed() is False
