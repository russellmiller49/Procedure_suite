from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_registry_service
from app.api.fastapi_app import app
from app.api.phi_dependencies import get_phi_scrubber
from app.api.phi_redaction import RedactionResult
from app.registry.application.registry_service import RegistryExtractionResult, RegistryRecord
from app.registry.schema.ip_v3_extraction import IPRegistryV3
from proc_schemas.registry.ip_v2 import IPRegistryV2

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

    # Completeness prompts should be present and include global missing fields.
    prompts = data.get("missing_field_prompts") or []
    assert isinstance(prompts, list)
    prompt_paths = {p.get("path") for p in prompts if isinstance(p, dict)}
    assert "patient_demographics.age_years" in prompt_paths
    assert "clinical_context.asa_class" in prompt_paths
    assert "clinical_context.ecog_score" in prompt_paths
    
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
    with patch("app.api.services.unified_pipeline.apply_phi_redaction") as mock_redact:
        mock_redact.return_value = RedactionResult(
            text="Scrubbed text",
            was_scrubbed=True,
            entity_count=1,
            warning=None,
        )
        
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


def test_unified_process_surfaces_registry_warnings(mock_registry_service, mock_phi_scrubber):
    mock_record = IPRegistryV2(
        patient={"patient_id": "123"},
        procedure={"procedure_date": "2023-01-01", "indication": "Test"},
    )
    full_record = RegistryRecord(
        patient=mock_record.patient,
        procedure=mock_record.procedure,
    )

    extraction_result = RegistryExtractionResult(
        record=full_record,
        cpt_codes=["31622"],
        coder_difficulty="HIGH_CONF",
        coder_source="extraction_first",
        mapped_fields={},
        warnings=["SILENT_FAILURE: Text mentions 'laser'."],
        audit_warnings=[
            "RAW_ML_AUDIT[HIGH_CONF]: model suggests 31641 (prob=0.99), "
            "but deterministic derivation missed it"
        ],
        needs_manual_review=True,
    )

    mock_registry_service.extract_fields.return_value = extraction_result

    payload = {
        "note": "Already scrubbed text",
        "already_scrubbed": True,
    }
    response = client.post("/api/v1/process", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert any("SILENT_FAILURE" in w for w in data["audit_warnings"])
    assert any("RAW_ML_AUDIT" in w for w in data["audit_warnings"])


def test_unified_process_applies_multiple_endoscopy_rule_to_financials(
    mock_registry_service, mock_phi_scrubber
):
    from config.settings import CoderSettings
    from app.registry.application.coding_support_builder import get_kb_repo

    kb = get_kb_repo()
    conversion_factor = CoderSettings().cms_conversion_factor

    codes = ["31623", "31624", "31627", "31628", "31629", "31654"]

    mock_record = IPRegistryV2(
        patient={"patient_id": "123"},
        procedure={"procedure_date": "2023-01-01", "indication": "Test"},
    )
    full_record = RegistryRecord(
        patient=mock_record.patient,
        procedure=mock_record.procedure,
    )

    extraction_result = RegistryExtractionResult(
        record=full_record,
        cpt_codes=codes,
        coder_difficulty="HIGH_CONF",
        coder_source="extraction_first",
        mapped_fields={},
        needs_manual_review=False,
    )

    mock_registry_service.extract_fields.return_value = extraction_result

    payload = {
        "note": "Already scrubbed text",
        "already_scrubbed": True,
        "include_financials": True,
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 200
    data = response.json()

    billing_by_code = {row["cpt_code"]: row for row in data.get("per_code_billing") or []}

    def base_payment(code: str) -> float:
        info = kb.get_procedure_info(code)
        assert info is not None
        return info.total_facility_rvu * conversion_factor

    # Multiple endoscopy applies to the bronchoscopy endoscopy family:
    # - primary (highest total RVU): 31629 @ 100%
    # - other non-add-on family codes: 50%
    # - add-ons (e.g., 31627, 31654): no reduction
    expected_per_code = {
        "31629": round(base_payment("31629"), 2),
        "31628": round(base_payment("31628") * 0.5, 2),
        "31624": round(base_payment("31624") * 0.5, 2),
        "31623": round(base_payment("31623") * 0.5, 2),
        "31627": round(base_payment("31627"), 2),
        "31654": round(base_payment("31654"), 2),
    }

    for code, expected in expected_per_code.items():
        assert billing_by_code[code]["facility_payment"] == expected

    expected_total = round(sum(expected_per_code.values()), 2)
    assert data["estimated_payment"] == expected_total
    assert any("MULTIPLE_ENDOSCOPY_RULE" in w for w in data.get("audit_warnings") or [])


def test_unified_process_include_v3_event_log(mock_registry_service, mock_phi_scrubber):
    mock_record = IPRegistryV2(
        patient={"patient_id": "123"},
        procedure={"procedure_date": "2023-01-01", "indication": "Test"},
    )
    full_record = RegistryRecord(
        patient=mock_record.patient,
        procedure=mock_record.procedure,
    )
    extraction_result = RegistryExtractionResult(
        record=full_record,
        cpt_codes=["31622"],
        coder_difficulty="HIGH_CONF",
        coder_source="extraction_first",
        mapped_fields={},
    )
    mock_registry_service.extract_fields.return_value = extraction_result

    v3_payload = IPRegistryV3(
        note_id="test-note",
        source_filename="inline",
        procedures=[
            {
                "event_id": "evt_1",
                "type": "airway stent removal",
                "evidence": {"quote": "removed en bloc"},
            }
        ],
    )

    with patch(
        "app.registry.pipelines.v3_pipeline.run_v3_extraction",
        return_value=v3_payload,
    ):
        payload = {
            "note": "Already scrubbed text",
            "already_scrubbed": True,
            "include_v3_event_log": True,
        }
        response = client.post("/api/v1/process", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["cpt_codes"] == ["31622"]
    assert "registry_v3_event_log" in data
    assert data["registry_v3_event_log"]["schema_version"] == "v3"
    assert len(data["registry_v3_event_log"]["procedures"]) == 1
    assert data["registry_v3_event_log"]["procedures"][0]["type"] == "airway stent removal"
