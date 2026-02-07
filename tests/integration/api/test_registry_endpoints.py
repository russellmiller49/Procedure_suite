"""Integration tests for the registry export API endpoints.

Tests the registry export workflow:
- POST /procedures/{id}/registry/export
- GET  /procedures/{id}/registry/preview
- GET  /procedures/{id}/registry/export
"""

import os

# Avoid network-bound LLM calls during tests
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "1")

import pytest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.fastapi_app import app
from app.api.routes.procedure_codes import clear_procedure_stores
from app.api.dependencies import (
    get_coding_service,
    get_registry_service,
    get_procedure_store,
    reset_coding_service_cache,
    reset_registry_service_cache,
    reset_procedure_store,
)
from app.coder.adapters.persistence.inmemory_procedure_store import InMemoryProcedureStore
from app.registry.application.registry_service import RegistryService
from app.registry.adapters.schema_registry import get_schema_registry
from proc_schemas.coding import FinalCode
from proc_schemas.reasoning import ReasoningFields


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def registry_service():
    """Create a RegistryService for testing."""
    return RegistryService(
        schema_registry=get_schema_registry(),
        default_version="v2",
    )


@pytest.fixture
def test_store():
    """Create an in-memory store for testing."""
    return InMemoryProcedureStore()


@pytest.fixture
def client(registry_service, test_store):
    """Create a TestClient with RegistryService and ProcedureStore injected."""
    # Reset stores before each test
    reset_procedure_store()
    reset_registry_service_cache()

    # Use FastAPI's dependency_overrides
    app.dependency_overrides[get_registry_service] = lambda: registry_service
    app.dependency_overrides[get_procedure_store] = lambda: test_store

    yield TestClient(app), test_store

    # Clean up after test
    app.dependency_overrides.clear()
    reset_procedure_store()


def create_final_code(code: str, description: str = "") -> FinalCode:
    """Helper to create a FinalCode for testing."""
    return FinalCode(
        code=code,
        description=description or f"Description for {code}",
        source="hybrid",
        reasoning=ReasoningFields(
            kb_version="test_kb_v1",
            policy_version="smart_hybrid_v2",
            confidence=0.9,
        ),
        procedure_id="test-proc",
    )


# ============================================================================
# Test Scenarios
# ============================================================================


class TestRegistryExportEndpoint:
    """Tests for POST /procedures/{id}/registry/export."""

    def test_export_happy_path_v2(self, client):
        """Test successful export with v2 schema."""
        http_client, store = client
        proc_id = "test-export-001"

        # Setup: Add final codes via store
        store.add_final_code(proc_id, create_final_code("31652", "EBUS-TBNA 1-2 stations"))
        store.add_final_code(proc_id, create_final_code("31624", "Bronchoalveolar lavage"))

        # Export with metadata
        response = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={
                "registry_version": "v2",
                "procedure_metadata": {
                    "patient": {
                        "patient_id": "P12345",
                        "mrn": "MRN001",
                        "age": 65,
                        "sex": "M",
                    },
                    "procedure": {
                        "procedure_date": "2024-01-15",
                        "procedure_type": "diagnostic_bronchoscopy",
                        "indication": "Lung mass, suspected malignancy",
                        "urgency": "routine",
                    },
                },
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["procedure_id"] == proc_id
        assert data["registry_id"] == "ip_registry"
        assert data["schema_version"] == "v2"
        assert data["status"] in ("success", "partial")
        assert "export_id" in data
        assert "export_timestamp" in data
        assert "bundle" in data

        # Verify bundle has expected fields
        bundle = data["bundle"]
        assert bundle["schema_version"] == "v2"
        assert bundle["ebus_performed"] is True
        assert bundle["bal_performed"] is True
        assert bundle["patient"]["patient_id"] == "P12345"

    def test_export_with_v3_schema(self, client):
        """Test export with v3 schema."""
        http_client, store = client
        proc_id = "test-export-002"

        # Setup: Add final codes via store
        store.add_final_code(proc_id, create_final_code("31653", "EBUS-TBNA 3+ stations"))
        store.add_final_code(proc_id, create_final_code("31627", "Navigation bronchoscopy"))

        response = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={
                "registry_version": "v3",
                "procedure_metadata": {
                    "patient": {"patient_id": "P99999"},
                    "procedure": {"indication": "Staging"},
                },
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["schema_version"] == "v3"
        bundle = data["bundle"]
        assert bundle["schema_version"] == "v3"
        assert bundle["ebus_performed"] is True
        assert bundle["navigation_performed"] is True

    def test_export_no_final_codes_404(self, client):
        """Test 404 when no final codes exist."""
        http_client, store = client
        response = http_client.post(
            "/api/v1/procedures/unknown-proc/registry/export",
            json={"registry_version": "v2"},
        )

        assert response.status_code == 404
        assert "No final codes found" in response.json()["detail"]

    def test_export_persisted_and_retrievable(self, client):
        """Test that export is persisted and can be retrieved."""
        http_client, store = client
        proc_id = "test-export-003"

        # Setup via store
        store.add_final_code(proc_id, create_final_code("31628", "Transbronchial biopsy"))

        # Export
        post_response = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={"registry_version": "v2"},
        )
        assert post_response.status_code == 200
        export_id = post_response.json()["export_id"]

        # Retrieve
        get_response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/export")
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert get_data["export_id"] == export_id
        assert get_data["bundle"]["tblb_performed"] is True

    def test_export_with_minimal_metadata(self, client):
        """Test export with minimal metadata generates warnings."""
        http_client, store = client
        proc_id = "test-export-004"

        store.add_final_code(proc_id, create_final_code("31652", "EBUS-TBNA"))

        response = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={"registry_version": "v2", "procedure_metadata": {}},
        )

        assert response.status_code == 200
        data = response.json()

        # Should have warnings about missing fields
        assert len(data["warnings"]) > 0
        # Status may be partial due to low completeness
        assert data["status"] in ("success", "partial")


class TestRegistryPreviewEndpoint:
    """Tests for GET /procedures/{id}/registry/preview."""

    def test_preview_with_final_codes(self, client):
        """Test preview with existing final codes."""
        http_client, store = client
        proc_id = "test-preview-001"

        store.add_final_code(proc_id, create_final_code("31652", "EBUS-TBNA 1-2 stations"))

        response = http_client.get(
            f"/api/v1/procedures/{proc_id}/registry/preview",
            params={"registry_version": "v2"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["procedure_id"] == proc_id
        assert data["status"] == "preview"
        assert data["schema_version"] == "v2"
        assert "completeness_score" in data
        assert "missing_fields" in data
        assert "warnings" in data

        # Bundle should have EBUS mapped
        assert data["bundle"]["ebus_performed"] is True

    def test_preview_without_final_codes(self, client):
        """Test preview works even without final codes."""
        http_client, store = client
        proc_id = "test-preview-002"

        # No final codes added
        response = http_client.get(
            f"/api/v1/procedures/{proc_id}/registry/preview",
            params={"registry_version": "v2"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return a skeleton entry
        assert data["status"] == "preview"
        assert data["completeness_score"] < 1.0  # Should be low
        assert len(data["missing_fields"]) > 0

    def test_preview_v3_schema(self, client):
        """Test preview with v3 schema."""
        http_client, store = client
        proc_id = "test-preview-003"

        store.add_final_code(proc_id, create_final_code("31627", "Navigation bronchoscopy"))

        response = http_client.get(
            f"/api/v1/procedures/{proc_id}/registry/preview",
            params={"registry_version": "v3"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["schema_version"] == "v3"
        assert data["bundle"]["schema_version"] == "v3"
        assert data["bundle"]["navigation_performed"] is True

    def test_preview_shows_suggested_values(self, client):
        """Test preview includes suggested values based on CPT hints."""
        http_client, store = client
        proc_id = "test-preview-004"

        # 31653 hints at 3+ stations
        store.add_final_code(proc_id, create_final_code("31653", "EBUS-TBNA 3+ stations"))

        response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/preview")

        assert response.status_code == 200
        data = response.json()

        # Should have suggestions based on CPT mapping hints
        # (e.g., station_count_hint from 31653)
        assert "suggested_values" in data


class TestGetRegistryExportEndpoint:
    """Tests for GET /procedures/{id}/registry/export (retrieve existing)."""

    def test_get_export_not_found(self, client):
        """Test 404 when no export exists."""
        http_client, store = client
        response = http_client.get("/api/v1/procedures/nonexistent/registry/export")

        assert response.status_code == 404
        assert "No registry export found" in response.json()["detail"]

    def test_get_export_after_post(self, client):
        """Test retrieving export after creation."""
        http_client, store = client
        proc_id = "test-get-001"

        # Setup and create export via store
        store.add_final_code(proc_id, create_final_code("31652", "EBUS-TBNA"))

        post_response = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={"registry_version": "v2"},
        )
        assert post_response.status_code == 200

        # Get the export
        get_response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/export")
        assert get_response.status_code == 200

        # Compare key fields
        post_data = post_response.json()
        get_data = get_response.json()

        assert post_data["export_id"] == get_data["export_id"]
        assert post_data["bundle"] == get_data["bundle"]
        assert post_data["status"] == get_data["status"]


class TestRegistryExportFullWorkflow:
    """End-to-end workflow tests for registry export."""

    def test_full_workflow_suggest_review_export(self, client):
        """Test complete workflow: suggest → review → export."""
        from tests.integration.api.test_procedure_codes_endpoints import (
            create_mock_coding_service,
            MockLLMAdvisor,
            mock_apply_ncci_edits,
            mock_apply_mer_rules,
        )

        http_client, store = client
        proc_id = "test-workflow-001"

        # Setup mock coding service
        mock_llm = MockLLMAdvisor(codes_to_return={"31652": 0.9})
        mock_service = create_mock_coding_service(mock_llm)
        app.dependency_overrides[get_coding_service] = lambda: mock_service

        with patch("app.coder.application.coding_service.apply_ncci_edits", mock_apply_ncci_edits), \
             patch("app.coder.application.coding_service.apply_mer_rules", mock_apply_mer_rules):

            # Step 1: Suggest codes
            suggest_response = http_client.post(
                f"/api/v1/procedures/{proc_id}/codes/suggest",
                json={
                    "report_text": "EBUS-TBNA performed at station 4R.",
                    "use_llm": False,
                },
            )
            assert suggest_response.status_code == 200
            suggestions = suggest_response.json()["suggestions"]
            assert len(suggestions) >= 1

            # Step 2: Accept suggestions
            for suggestion in suggestions:
                review_response = http_client.post(
                    f"/api/v1/procedures/{proc_id}/codes/review",
                    json={
                        "suggestion_id": suggestion["suggestion_id"],
                        "action": "accept",
                        "reviewer_id": "dr-test",
                    },
                )
                assert review_response.status_code == 200

            # Step 3: Verify final codes exist
            final_response = http_client.get(f"/api/v1/procedures/{proc_id}/codes/final")
            assert final_response.status_code == 200
            assert len(final_response.json()) >= 1

            # Step 4: Preview registry entry
            preview_response = http_client.get(
                f"/api/v1/procedures/{proc_id}/registry/preview"
            )
            assert preview_response.status_code == 200
            preview = preview_response.json()
            assert preview["status"] == "preview"
            assert preview["bundle"]["ebus_performed"] is True

            # Step 5: Export to registry
            export_response = http_client.post(
                f"/api/v1/procedures/{proc_id}/registry/export",
                json={
                    "registry_version": "v2",
                    "procedure_metadata": {
                        "patient": {"patient_id": "P001", "age": 60},
                        "procedure": {
                            "procedure_date": "2024-01-15",
                            "indication": "Lung mass",
                        },
                    },
                },
            )
            assert export_response.status_code == 200
            export = export_response.json()
            assert export["status"] in ("success", "partial")
            assert export["bundle"]["ebus_performed"] is True

            # Step 6: Retrieve the export
            get_export_response = http_client.get(
                f"/api/v1/procedures/{proc_id}/registry/export"
            )
            assert get_export_response.status_code == 200
            assert get_export_response.json()["export_id"] == export["export_id"]

    def test_multiple_exports_overwrite(self, client):
        """Test that re-exporting overwrites the previous export."""
        http_client, store = client
        proc_id = "test-overwrite-001"

        store.add_final_code(proc_id, create_final_code("31624", "BAL"))

        # First export
        response1 = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={"registry_version": "v2"},
        )
        assert response1.status_code == 200
        export_id_1 = response1.json()["export_id"]

        # Second export (overwrites)
        response2 = http_client.post(
            f"/api/v1/procedures/{proc_id}/registry/export",
            json={"registry_version": "v2"},
        )
        assert response2.status_code == 200
        export_id_2 = response2.json()["export_id"]

        # Export IDs should be different
        assert export_id_1 != export_id_2

        # Get should return the latest
        get_response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/export")
        assert get_response.json()["export_id"] == export_id_2


class TestCPTToRegistryMapping:
    """Tests verifying CPT code to registry field mapping."""

    def test_ebus_mapping(self, client):
        """Test EBUS CPT codes map to ebus_performed."""
        http_client, store = client
        proc_id = "test-cpt-ebus"

        # 31652 = EBUS 1-2 stations
        store.add_final_code(proc_id, create_final_code("31652", "EBUS-TBNA 1-2 stations"))

        response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/preview")
        assert response.status_code == 200
        assert response.json()["bundle"]["ebus_performed"] is True

    def test_bal_mapping(self, client):
        """Test BAL CPT code maps to bal_performed."""
        http_client, store = client
        proc_id = "test-cpt-bal"

        store.add_final_code(proc_id, create_final_code("31624", "Bronchoalveolar lavage"))

        response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/preview")
        assert response.status_code == 200
        assert response.json()["bundle"]["bal_performed"] is True

    def test_tblb_mapping(self, client):
        """Test TBLB CPT code maps to tblb_performed."""
        http_client, store = client
        proc_id = "test-cpt-tblb"

        store.add_final_code(proc_id, create_final_code("31628", "Transbronchial lung biopsy"))

        response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/preview")
        assert response.status_code == 200
        assert response.json()["bundle"]["tblb_performed"] is True

    def test_navigation_mapping(self, client):
        """Test navigation CPT code maps to navigation_performed."""
        http_client, store = client
        proc_id = "test-cpt-nav"

        store.add_final_code(proc_id, create_final_code("31627", "Navigation bronchoscopy"))

        response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/preview")
        assert response.status_code == 200
        assert response.json()["bundle"]["navigation_performed"] is True

    def test_multiple_codes_aggregate(self, client):
        """Test multiple CPT codes aggregate correctly."""
        http_client, store = client
        proc_id = "test-cpt-multi"

        store.add_final_code(proc_id, create_final_code("31653", "EBUS-TBNA 3+ stations"))
        store.add_final_code(proc_id, create_final_code("31628", "Transbronchial biopsy"))
        store.add_final_code(proc_id, create_final_code("31624", "BAL"))

        response = http_client.get(f"/api/v1/procedures/{proc_id}/registry/preview")
        assert response.status_code == 200

        bundle = response.json()["bundle"]
        assert bundle["ebus_performed"] is True
        assert bundle["tblb_performed"] is True
        assert bundle["bal_performed"] is True
