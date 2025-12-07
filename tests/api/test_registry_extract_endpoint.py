"""API integration tests for the /api/registry/extract endpoint.

Tests the FastAPI endpoint for hybrid-first registry extraction.
"""

import os

# Ensure stub LLM is used during tests
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "1")
os.environ.setdefault("PHI_SCRUBBER_MODE", "stub")

import pytest
import pytest_asyncio
import httpx
from unittest.mock import MagicMock
from typing import Any

from modules.api.fastapi_app import app
from modules.api.dependencies import get_registry_service
from modules.registry.application.registry_service import (
    RegistryService,
    RegistryExtractionResult,
)
from modules.registry.schema import RegistryRecord
from modules.coder.application.smart_hybrid_policy import HybridCoderResult
from modules.ml_coder.thresholds import CaseDifficulty


# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def api_client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def make_mock_extraction_result(
    cpt_codes: list[str],
    coder_difficulty: str = "high_confidence",
    coder_source: str = "ml_rules_fastpath",
    mapped_fields: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    needs_manual_review: bool = False,
    validation_errors: list[str] | None = None,
    record_data: dict[str, Any] | None = None,
) -> RegistryExtractionResult:
    """Create a mock RegistryExtractionResult for testing."""
    record = RegistryRecord(**(record_data or {}))
    return RegistryExtractionResult(
        record=record,
        cpt_codes=cpt_codes,
        coder_difficulty=coder_difficulty,
        coder_source=coder_source,
        mapped_fields=mapped_fields or {},
        warnings=warnings or [],
        needs_manual_review=needs_manual_review,
        validation_errors=validation_errors or [],
    )


# ============================================================================
# Basic Endpoint Tests
# ============================================================================


class TestRegistryExtractEndpoint:
    """Tests for POST /api/registry/extract endpoint."""

    @pytest.mark.asyncio
    async def test_endpoint_returns_200_with_valid_input(self, api_client: httpx.AsyncClient) -> None:
        """Valid note text should return 200 with expected response structure."""
        response = await api_client.post(
            "/api/registry/extract",
            json={
                "note_text": "PROCEDURE: Diagnostic bronchoscopy\n\nThe patient underwent diagnostic bronchoscopy. Airways were inspected. No abnormalities noted."
            },
        )

        # Should return 200 (may be 503 if orchestrator not configured, which is acceptable)
        assert response.status_code in (200, 503)

        if response.status_code == 200:
            data = response.json()
            # Verify response structure
            assert "record" in data
            assert "cpt_codes" in data
            assert "coder_difficulty" in data
            assert "coder_source" in data
            assert "mapped_fields" in data
            assert "warnings" in data
            assert "needs_manual_review" in data
            assert "validation_errors" in data

    @pytest.mark.asyncio
    async def test_endpoint_rejects_short_note(self, api_client: httpx.AsyncClient) -> None:
        """Note text below minimum length should be rejected."""
        response = await api_client.post(
            "/api/registry/extract",
            json={"note_text": "Short"},  # Less than 10 chars
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_endpoint_rejects_missing_note(self, api_client: httpx.AsyncClient) -> None:
        """Missing note_text field should be rejected."""
        response = await api_client.post(
            "/api/registry/extract",
            json={},
        )

        assert response.status_code == 422  # Validation error


# ============================================================================
# Mocked Service Integration Tests
# ============================================================================


class TestRegistryExtractWithMockedService:
    """Tests with mocked RegistryService using FastAPI dependency overrides."""

    @pytest.mark.asyncio
    async def test_ebus_codes_reflected_in_response(self) -> None:
        """EBUS CPT codes from service should appear in response."""
        mock_result = make_mock_extraction_result(
            cpt_codes=["31653", "31627"],
            coder_difficulty="high_confidence",
            coder_source="ml_rules_fastpath",
            mapped_fields={
                "procedures_performed": {
                    "linear_ebus": {"performed": True},
                    "navigational_bronchoscopy": {"performed": True},
                }
            },
            needs_manual_review=False,
            record_data={
                "procedures_performed": {
                    "linear_ebus": {"performed": True},
                    "navigational_bronchoscopy": {"performed": True},
                }
            },
        )

        mock_service = MagicMock(spec=RegistryService)
        mock_service.extract_fields.return_value = mock_result

        # Use FastAPI dependency override
        app.dependency_overrides[get_registry_service] = lambda: mock_service

        try:
            transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/registry/extract",
                    json={
                        "note_text": "PROCEDURE: EBUS-TBNA with Navigation\n\nThe patient underwent EBUS-TBNA of stations 4R, 7, and 11L. Navigation bronchoscopy was used."
                    },
                )

                assert response.status_code == 200
                data = response.json()

                # Verify CPT codes are in response
                assert data["cpt_codes"] == ["31653", "31627"]
                assert data["coder_difficulty"] == "high_confidence"
                assert data["coder_source"] == "ml_rules_fastpath"

                # Verify mapped fields
                assert "procedures_performed" in data["mapped_fields"]
                assert data["mapped_fields"]["procedures_performed"]["linear_ebus"]["performed"] is True

                # Verify no manual review needed for high confidence
                assert data["needs_manual_review"] is False
        finally:
            # Clean up override
            app.dependency_overrides.pop(get_registry_service, None)

    @pytest.mark.asyncio
    async def test_low_conf_triggers_manual_review(self) -> None:
        """LOW_CONF difficulty should set needs_manual_review=True."""
        mock_result = make_mock_extraction_result(
            cpt_codes=["31622"],
            coder_difficulty="low_confidence",
            coder_source="hybrid_llm_fallback",
            mapped_fields={},
            needs_manual_review=True,
            validation_errors=["Hybrid coder marked this case as LOW_CONF; manual review required."],
        )

        mock_service = MagicMock(spec=RegistryService)
        mock_service.extract_fields.return_value = mock_result

        app.dependency_overrides[get_registry_service] = lambda: mock_service

        try:
            transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/registry/extract",
                    json={"note_text": "Some ambiguous procedure note that is hard to code."},
                )

                assert response.status_code == 200
                data = response.json()

                assert data["needs_manual_review"] is True
                assert data["coder_difficulty"] == "low_confidence"
                assert len(data["validation_errors"]) > 0
        finally:
            app.dependency_overrides.pop(get_registry_service, None)

    @pytest.mark.asyncio
    async def test_validation_errors_in_response(self) -> None:
        """Validation errors should appear in response."""
        mock_result = make_mock_extraction_result(
            cpt_codes=["31652"],
            coder_difficulty="high_confidence",
            coder_source="ml_rules_fastpath",
            mapped_fields={"procedures_performed": {"linear_ebus": {"performed": True}}},
            warnings=["Some warning"],
            needs_manual_review=True,
            validation_errors=[
                "CPT 31652 present but procedures_performed.linear_ebus is not marked."
            ],
        )

        mock_service = MagicMock(spec=RegistryService)
        mock_service.extract_fields.return_value = mock_result

        app.dependency_overrides[get_registry_service] = lambda: mock_service

        try:
            transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/registry/extract",
                    json={"note_text": "EBUS procedure but extractor missed the field."},
                )

                assert response.status_code == 200
                data = response.json()

                assert data["needs_manual_review"] is True
                assert "31652" in data["validation_errors"][0]
                assert "warnings" in data
                assert len(data["warnings"]) > 0
        finally:
            app.dependency_overrides.pop(get_registry_service, None)

    @pytest.mark.asyncio
    async def test_pleural_codes_mapping(self) -> None:
        """Pleural CPT codes should map to pleural_procedures section."""
        mock_result = make_mock_extraction_result(
            cpt_codes=["32555"],
            coder_difficulty="high_confidence",
            coder_source="ml_rules_fastpath",
            mapped_fields={"pleural_procedures": {"thoracentesis": {"performed": True}}},
            needs_manual_review=False,
            record_data={
                "pleural_procedures": {"thoracentesis": {"performed": True}},
            },
        )

        mock_service = MagicMock(spec=RegistryService)
        mock_service.extract_fields.return_value = mock_result

        app.dependency_overrides[get_registry_service] = lambda: mock_service

        try:
            transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/registry/extract",
                    json={"note_text": "Thoracentesis performed under ultrasound guidance. 1200mL removed."},
                )

                assert response.status_code == 200
                data = response.json()

                # Verify pleural procedures mapping
                assert "pleural_procedures" in data["mapped_fields"]
                assert data["mapped_fields"]["pleural_procedures"]["thoracentesis"]["performed"] is True
        finally:
            app.dependency_overrides.pop(get_registry_service, None)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestRegistryExtractErrorHandling:
    """Tests for error handling in the endpoint."""

    @pytest.mark.asyncio
    async def test_service_exception_returns_500(self) -> None:
        """Service exceptions should return 500."""
        mock_service = MagicMock(spec=RegistryService)
        mock_service.extract_fields.side_effect = Exception("Internal error")

        app.dependency_overrides[get_registry_service] = lambda: mock_service

        try:
            transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/registry/extract",
                    json={"note_text": "Some procedure note that causes an error."},
                )

                assert response.status_code == 500
        finally:
            app.dependency_overrides.pop(get_registry_service, None)

    @pytest.mark.asyncio
    async def test_invalid_json_returns_422(self, api_client: httpx.AsyncClient) -> None:
        """Invalid JSON payload should return 422."""
        response = await api_client.post(
            "/api/registry/extract",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422


# ============================================================================
# Response Schema Validation Tests
# ============================================================================


class TestResponseSchemaValidation:
    """Tests that verify response schema matches documentation."""

    @pytest.mark.asyncio
    async def test_response_has_all_documented_fields(self) -> None:
        """Response should contain all fields documented in Registry_API.md."""
        mock_result = make_mock_extraction_result(
            cpt_codes=["31622"],
            coder_difficulty="high_confidence",
            coder_source="ml_rules_fastpath",
            mapped_fields={},
            needs_manual_review=False,
        )

        mock_service = MagicMock(spec=RegistryService)
        mock_service.extract_fields.return_value = mock_result

        app.dependency_overrides[get_registry_service] = lambda: mock_service

        try:
            transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/registry/extract",
                    json={"note_text": "Diagnostic bronchoscopy performed."},
                )

                assert response.status_code == 200
                data = response.json()

                # All documented fields must be present
                required_fields = [
                    "record",
                    "cpt_codes",
                    "coder_difficulty",
                    "coder_source",
                    "mapped_fields",
                    "warnings",
                    "needs_manual_review",
                    "validation_errors",
                ]

                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"

                # Verify types
                assert isinstance(data["record"], dict)
                assert isinstance(data["cpt_codes"], list)
                assert isinstance(data["coder_difficulty"], str)
                assert isinstance(data["coder_source"], str)
                assert isinstance(data["mapped_fields"], dict)
                assert isinstance(data["warnings"], list)
                assert isinstance(data["needs_manual_review"], bool)
                assert isinstance(data["validation_errors"], list)
        finally:
            app.dependency_overrides.pop(get_registry_service, None)
