import pytest
from fastapi.testclient import TestClient
from modules.api.fastapi_app import app
from unittest.mock import patch, MagicMock
from modules.registry.application.registry_service import RegistryExtractionResult, RegistryRecord
from proc_schemas.registry.ip_v2 import IPRegistryV2
from modules.api.dependencies import get_registry_service
from modules.api.phi_dependencies import get_phi_scrubber

client = TestClient(app)

@pytest.fixture
def mock_registry_service():
    service_mock = MagicMock()
    app.dependency_overrides[get_registry_service] = lambda: service_mock
    yield service_mock
    app.dependency_overrides.pop(get_registry_service, None)

@pytest.fixture
def mock_phi_scrubber():
    scrubber_mock = MagicMock()
    app.dependency_overrides[get_phi_scrubber] = lambda: scrubber_mock
    yield scrubber_mock
    app.dependency_overrides.pop(get_phi_scrubber, None)

def test_unified_process_already_scrubbed(mock_registry_service, mock_phi_scrubber):
    # Setup mock return
    mock_record = IPRegistryV2(
        patient={"patient_id": "123"},
        procedure={"procedure_date": "2023-01-01", "indication": "Test"}
    )
    # We need a full RegistryRecord wrapping the V2 entry
    full_record = RegistryRecord(
        patient=mock_record.patient,
        procedure=mock_record.procedure,
        # minimal fields to satisfy validation
    )
    
    extraction_result = RegistryExtractionResult(
        record=full_record,
        cpt_codes=["31622"],
        coder_difficulty="HIGH_CONF",
        coder_source="ml_rules_fastpath",
        mapped_fields={},
        needs_manual_review=False
    )
    
    mock_registry_service.extract_fields.return_value = extraction_result

    payload = {
        "note": "Already scrubbed text",
        "already_scrubbed": True
    }
    
    response = client.post("/api/v1/process", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["cpt_codes"] == ["31622"]
    assert data["coder_difficulty"] == "HIGH_CONF"
    assert len(data["suggestions"]) == 1
    assert data["suggestions"][0]["code"] == "31622"
    
    # Verify proper call to service
    mock_registry_service.extract_fields.assert_called_once_with("Already scrubbed text")

def test_unified_process_needs_scrubbing(mock_registry_service):
    # Mock extract_fields to return something valid
    mock_record = IPRegistryV2(
        patient={"patient_id": "123"},
        procedure={"procedure_date": "2023-01-01", "indication": "Test"}
    )
    full_record = RegistryRecord(
        patient=mock_record.patient,
        procedure=mock_record.procedure,
    )
    extraction_result = RegistryExtractionResult(
        record=full_record,
        cpt_codes=[],
        coder_difficulty="LOW_CONF",
        coder_source="test",
        mapped_fields={}
    )
    mock_registry_service.extract_fields.return_value = extraction_result

    # Mock redaction to happen
    with patch("modules.api.routes.unified_process.apply_phi_redaction") as mock_redact:
        mock_redact.return_value.text = "Scrubbed text"
        
        payload = {
            "note": "Raw PHI note",
            "already_scrubbed": False
        }
        
        response = client.post("/api/v1/process", json=payload)
        
        assert response.status_code == 200
        # Check that we called the scrubber
        mock_redact.assert_called_once()
        # Verify call to service passes scrubbed text
        mock_registry_service.extract_fields.assert_called_once_with("Scrubbed text")
