"""
Pytest Configuration and Shared Fixtures for Procedure Suite ML Advisor Tests

This conftest.py provides:
- Shared fixtures for common test data
- Mock implementations for external dependencies
- Test environment configuration
- Custom pytest markers and hooks

Usage:
    Place this file in the tests/ directory alongside your test files.
    Fixtures will be automatically available to all test modules.

Run tests with:
    pytest tests/ -v
    pytest tests/ -v -m "not integration"  # Skip integration tests
    pytest tests/ -v -m "slow"  # Run only slow tests
    pytest tests/ -v --cov=modules  # With coverage
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Import schemas (adjust import path as needed for your project structure)
from proc_ml_advisor_schemas import (
    # Enums
    AdvisorBackend,
    CodingPolicy,
    CodeType,
    ConfidenceLevel,
    ProcedureCategory,
    # Code-level models
    CodeWithConfidence,
    CodeModifier,
    NCCIWarning,
    # Structured report models
    SamplingStation,
    PleuralProcedureDetails,
    BronchoscopyProcedureDetails,
    SedationDetails,
    StructuredProcedureReport,
    # ML Advisor models
    MLAdvisorInput,
    MLAdvisorSuggestion,
    # Hybrid result models
    RuleEngineResult,
    HybridCodingResult,
    # Coding trace model
    CodingTrace,
    # API models
    CodeRequest,
    CodeResponse,
    EvaluationMetrics,
)


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require external services)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "gemini: marks tests that require Gemini API access"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, no external deps)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically add markers based on test location and name.
    
    - Tests in test_*_integration.py get 'integration' marker
    - Tests with 'slow' in name get 'slow' marker
    """
    for item in items:
        # Add integration marker for integration test files
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker for tests with 'slow' in name
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Add unit marker for tests not marked as integration or slow
        if not any(marker.name in ["integration", "slow"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# =============================================================================
# ENVIRONMENT FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def test_env():
    """
    Session-scoped fixture that sets up test environment variables.
    
    Restores original values after all tests complete.
    """
    original_env = os.environ.copy()
    
    # Set test environment
    os.environ.update({
        "ENABLE_ML_ADVISOR": "true",
        "ADVISOR_BACKEND": "stub",
        "ENABLE_CODING_TRACE": "true",
        "PIPELINE_VERSION": "test-v1",
    })
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def advisor_disabled_env(monkeypatch):
    """Fixture that disables the ML advisor."""
    monkeypatch.setenv("ENABLE_ML_ADVISOR", "false")
    monkeypatch.setenv("ADVISOR_BACKEND", "stub")


@pytest.fixture
def advisor_gemini_env(monkeypatch):
    """Fixture that configures Gemini advisor (without real API key)."""
    monkeypatch.setenv("ENABLE_ML_ADVISOR", "true")
    monkeypatch.setenv("ADVISOR_BACKEND", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")


@pytest.fixture
def trace_disabled_env(monkeypatch):
    """Fixture that disables trace logging."""
    monkeypatch.setenv("ENABLE_CODING_TRACE", "false")


# =============================================================================
# TEMPORARY FILE/DIRECTORY FIXTURES
# =============================================================================

@pytest.fixture
def tmp_trace_file(tmp_path) -> Path:
    """Temporary trace file for testing logging."""
    return tmp_path / "test_traces.jsonl"


@pytest.fixture
def tmp_trace_dir(tmp_path) -> Path:
    """Temporary directory for trace files."""
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    return trace_dir


@pytest.fixture
def populated_trace_file(tmp_trace_file) -> Path:
    """Trace file pre-populated with sample traces."""
    traces = [
        CodingTrace(
            trace_id=f"trace-{i}",
            report_text=f"Test procedure {i}",
            autocode_codes=["31622", "31653"] if i % 2 == 0 else ["32555"],
            autocode_confidence={"31622": 0.95, "31653": 0.90} if i % 2 == 0 else {"32555": 0.92},
            advisor_candidate_codes=["31622", "31653", "31625"] if i % 3 == 0 else [],
            advisor_disagreements=["31625"] if i % 3 == 0 else [],
            source="test.fixture",
        )
        for i in range(10)
    ]
    
    with open(tmp_trace_file, "w") as f:
        for trace in traces:
            f.write(trace.model_dump_json() + "\n")
    
    return tmp_trace_file


# =============================================================================
# SAMPLING STATION FIXTURES
# =============================================================================

@pytest.fixture
def station_4r() -> SamplingStation:
    """Single sampling station 4R."""
    return SamplingStation(
        station="4R",
        needle_gauge=22,
        passes=3,
        rose_result="Adequate, lymphocytes",
        adequate=True,
    )


@pytest.fixture
def station_7() -> SamplingStation:
    """Single sampling station 7."""
    return SamplingStation(
        station="7",
        needle_gauge=22,
        passes=2,
        rose_result="Adequate",
        adequate=True,
    )


@pytest.fixture
def station_11l() -> SamplingStation:
    """Single sampling station 11L."""
    return SamplingStation(
        station="11L",
        needle_gauge=21,
        passes=2,
        adequate=True,
    )


@pytest.fixture
def three_stations(station_4r, station_7, station_11l) -> list[SamplingStation]:
    """List of three sampling stations (triggers 31653)."""
    return [station_4r, station_7, station_11l]


@pytest.fixture
def two_stations(station_4r, station_7) -> list[SamplingStation]:
    """List of two sampling stations (triggers 31652)."""
    return [station_4r, station_7]


@pytest.fixture
def sample_stations_dict() -> list[dict]:
    """Sampling stations as dictionaries (for model creation)."""
    return [
        {"station": "4R", "needle_gauge": 22, "passes": 3, "adequate": True},
        {"station": "7", "needle_gauge": 22, "passes": 2, "adequate": True},
        {"station": "11L", "needle_gauge": 21, "passes": 2, "adequate": True},
    ]


# =============================================================================
# PROCEDURE DETAIL FIXTURES
# =============================================================================

@pytest.fixture
def bronchoscopy_ebus(three_stations) -> BronchoscopyProcedureDetails:
    """EBUS bronchoscopy with 3 stations."""
    return BronchoscopyProcedureDetails(
        scope_type="flexible",
        navigation_used=False,
        ebus_performed=True,
        ebus_type="linear",
        stations_sampled=three_stations,
        bal_performed=True,
        biopsy_sites=["RUL", "RML"],
    )


@pytest.fixture
def bronchoscopy_navigation() -> BronchoscopyProcedureDetails:
    """Navigation bronchoscopy."""
    return BronchoscopyProcedureDetails(
        scope_type="flexible",
        navigation_used=True,
        navigation_system="Ion",
        ebus_performed=False,
        bal_performed=False,
        biopsy_sites=["RUL peripheral nodule"],
    )


@pytest.fixture
def bronchoscopy_diagnostic() -> BronchoscopyProcedureDetails:
    """Simple diagnostic bronchoscopy."""
    return BronchoscopyProcedureDetails(
        scope_type="flexible",
        navigation_used=False,
        ebus_performed=False,
        bal_performed=True,
    )


@pytest.fixture
def pleural_thoracentesis() -> PleuralProcedureDetails:
    """Standard thoracentesis with ultrasound."""
    return PleuralProcedureDetails(
        laterality="right",
        volume_ml=1500,
        fluid_appearance="straw-colored, clear",
        imaging_guidance=True,
        imaging_modality="ultrasound",
        permanent_image=True,
    )


@pytest.fixture
def pleural_bilateral() -> PleuralProcedureDetails:
    """Bilateral thoracentesis."""
    return PleuralProcedureDetails(
        laterality="bilateral",
        volume_ml=2500,
        fluid_appearance="bloody bilateral",
        imaging_guidance=True,
        imaging_modality="ultrasound",
        permanent_image=True,
    )


@pytest.fixture
def pleural_ipc() -> PleuralProcedureDetails:
    """IPC (tunneled pleural catheter) placement."""
    return PleuralProcedureDetails(
        laterality="left",
        volume_ml=800,
        fluid_appearance="serosanguinous",
        imaging_guidance=True,
        imaging_modality="ultrasound",
        permanent_image=True,
        catheter_french=15,
        tunneled=True,
    )


@pytest.fixture
def sedation_45min() -> SedationDetails:
    """45 minutes of moderate sedation."""
    return SedationDetails(
        sedation_provided=True,
        start_time="10:00",
        end_time="10:45",
        total_minutes=45,
        independent_observer=True,
    )


# =============================================================================
# STRUCTURED REPORT FIXTURES
# =============================================================================

@pytest.fixture
def report_ebus(bronchoscopy_ebus, sedation_45min) -> StructuredProcedureReport:
    """Complete EBUS procedure report."""
    return StructuredProcedureReport(
        report_id="rpt-ebus-001",
        encounter_id="enc-12345",
        procedure_category=ProcedureCategory.EBUS,
        procedure_types=["EBUS-TBNA", "BAL"],
        raw_text="Bronchoscopy with EBUS-TBNA sampling of stations 4R, 7, and 11L. BAL performed in RML.",
        bronchoscopy=bronchoscopy_ebus,
        sedation=sedation_45min,
        procedure_date=datetime(2025, 11, 29, 10, 0, tzinfo=timezone.utc),
        facility_type="facility",
    )


@pytest.fixture
def report_thoracentesis(pleural_thoracentesis) -> StructuredProcedureReport:
    """Thoracentesis procedure report."""
    return StructuredProcedureReport(
        report_id="rpt-thora-001",
        procedure_category=ProcedureCategory.PLEURAL,
        procedure_types=["Thoracentesis"],
        raw_text="Ultrasound-guided thoracentesis of right pleural effusion. 1500mL straw-colored fluid removed.",
        pleural=pleural_thoracentesis,
        facility_type="facility",
    )


@pytest.fixture
def report_navigation(bronchoscopy_navigation) -> StructuredProcedureReport:
    """Navigation bronchoscopy report."""
    return StructuredProcedureReport(
        report_id="rpt-nav-001",
        procedure_category=ProcedureCategory.NAVIGATION,
        procedure_types=["Robotic bronchoscopy", "Peripheral biopsy"],
        raw_text="Ion robotic bronchoscopy with biopsy of RUL peripheral nodule.",
        bronchoscopy=bronchoscopy_navigation,
        facility_type="facility",
    )


@pytest.fixture
def report_dict_ebus(sample_stations_dict) -> dict:
    """EBUS report as dictionary (for API testing)."""
    return {
        "report_id": "rpt-ebus-dict",
        "procedure_category": "ebus",
        "procedure_types": ["EBUS-TBNA"],
        "raw_text": "EBUS with sampling of 4R, 7, 11L",
        "bronchoscopy": {
            "scope_type": "flexible",
            "ebus_performed": True,
            "ebus_type": "linear",
            "stations_sampled": sample_stations_dict,
        },
        "facility_type": "facility",
    }


# =============================================================================
# CODE FIXTURES
# =============================================================================

@pytest.fixture
def code_31622() -> CodeWithConfidence:
    """Diagnostic bronchoscopy code."""
    return CodeWithConfidence(
        code="31622",
        code_type=CodeType.CPT,
        confidence=0.95,
        confidence_level=ConfidenceLevel.HIGH,
        description="Diagnostic bronchoscopy",
        is_addon=False,
    )


@pytest.fixture
def code_31653() -> CodeWithConfidence:
    """EBUS-TBNA 3+ stations code."""
    return CodeWithConfidence(
        code="31653",
        code_type=CodeType.CPT,
        confidence=0.92,
        confidence_level=ConfidenceLevel.HIGH,
        description="EBUS-guided TBNA, 3+ stations",
        is_addon=False,
    )


@pytest.fixture
def code_31652() -> CodeWithConfidence:
    """EBUS-TBNA 1-2 stations code."""
    return CodeWithConfidence(
        code="31652",
        code_type=CodeType.CPT,
        confidence=0.90,
        description="EBUS-guided TBNA, 1-2 stations",
        is_addon=False,
    )


@pytest.fixture
def code_31625() -> CodeWithConfidence:
    """BAL code."""
    return CodeWithConfidence(
        code="31625",
        code_type=CodeType.CPT,
        confidence=0.88,
        description="Bronchoscopy with BAL",
        is_addon=False,
    )


@pytest.fixture
def code_31627_addon() -> CodeWithConfidence:
    """Navigation add-on code."""
    return CodeWithConfidence(
        code="31627",
        code_type=CodeType.CPT,
        confidence=0.85,
        description="Computer-assisted navigation",
        is_addon=True,
        primary_code="31622",
    )


@pytest.fixture
def code_32555() -> CodeWithConfidence:
    """Thoracentesis with imaging code."""
    return CodeWithConfidence(
        code="32555",
        code_type=CodeType.CPT,
        confidence=0.95,
        description="Thoracentesis with imaging guidance",
        is_addon=False,
    )


@pytest.fixture
def ebus_codes(code_31622, code_31653, code_31625) -> list[CodeWithConfidence]:
    """Standard EBUS code set."""
    return [code_31622, code_31653, code_31625]


@pytest.fixture
def bronch_modifiers() -> list[CodeModifier]:
    """Common bronchoscopy modifiers."""
    return [
        CodeModifier(modifier="-51", reason="Multiple endoscopy procedures"),
    ]


@pytest.fixture
def bilateral_modifier() -> CodeModifier:
    """Bilateral procedure modifier."""
    return CodeModifier(modifier="-50", reason="Bilateral procedure")


# =============================================================================
# NCCI WARNING FIXTURES
# =============================================================================

@pytest.fixture
def ncci_warning_bundled() -> NCCIWarning:
    """NCCI bundling warning."""
    return NCCIWarning(
        warning_id="ncci_31622_ebus",
        codes_involved=["31622", "31653"],
        message="31622 typically bundled with EBUS codes per NCCI",
        severity="info",
        resolution="May be separately billable with modifier -59 for distinct service",
        citation="NCCI Policy Manual Chapter 4",
    )


@pytest.fixture
def ncci_warning_error() -> NCCIWarning:
    """NCCI error-level warning."""
    return NCCIWarning(
        warning_id="ncci_never_together",
        codes_involved=["31640", "31641"],
        message="Cannot bill excision and destruction at same site",
        severity="error",
        resolution="Select one code that best describes the procedure",
    )


# =============================================================================
# ML ADVISOR FIXTURES
# =============================================================================

@pytest.fixture
def advisor_input_ebus(report_ebus) -> MLAdvisorInput:
    """ML advisor input for EBUS procedure."""
    return MLAdvisorInput(
        trace_id="test-advisor-ebus",
        report_id=report_ebus.report_id,
        report_text=report_ebus.raw_text or "",
        structured_report=report_ebus.model_dump(),
        autocode_codes=["31622", "31653"],
        procedure_category=report_ebus.procedure_category,
    )


@pytest.fixture
def advisor_suggestion_agreement() -> MLAdvisorSuggestion:
    """Advisor suggestion that agrees with rules."""
    return MLAdvisorSuggestion(
        candidate_codes=["31622", "31653"],
        code_confidence={"31622": 0.92, "31653": 0.88},
        explanation="Codes align with rule engine assessment",
        additions=[],
        removals=[],
        model_name="gemini-1.5-pro",
        latency_ms=450.0,
        tokens_used=1250,
    )


@pytest.fixture
def advisor_suggestion_with_additions() -> MLAdvisorSuggestion:
    """Advisor suggestion with additional codes."""
    return MLAdvisorSuggestion(
        candidate_codes=["31622", "31653", "31625", "31627"],
        code_confidence={
            "31622": 0.92,
            "31653": 0.88,
            "31625": 0.75,
            "31627": 0.65,
        },
        explanation="Consider adding 31625 for BAL and 31627 for navigation if documented",
        additions=["31625", "31627"],
        removals=[],
        model_name="gemini-1.5-pro",
        latency_ms=520.0,
    )


@pytest.fixture
def advisor_suggestion_with_removals() -> MLAdvisorSuggestion:
    """Advisor suggestion that questions rule codes."""
    return MLAdvisorSuggestion(
        candidate_codes=["31653"],
        code_confidence={"31653": 0.90},
        explanation="31622 may be bundled; consider removing",
        additions=[],
        removals=["31622"],
        model_name="gemini-1.5-pro",
        latency_ms=480.0,
    )


@pytest.fixture
def advisor_suggestion_stub() -> MLAdvisorSuggestion:
    """Stub advisor suggestion."""
    return MLAdvisorSuggestion(
        candidate_codes=["31622", "31653"],
        code_confidence={"31622": 0.5, "31653": 0.5},
        explanation="ML advisor not configured (stub mode)",
        model_name="stub",
    )


# =============================================================================
# HYBRID RESULT FIXTURES
# =============================================================================

@pytest.fixture
def rule_engine_result(ebus_codes, bronch_modifiers, ncci_warning_bundled) -> RuleEngineResult:
    """Rule engine result for EBUS."""
    return RuleEngineResult(
        codes=ebus_codes,
        modifiers=bronch_modifiers,
        ncci_warnings=[ncci_warning_bundled],
        mer_applied=True,
        rationales={
            "31622": "Diagnostic bronchoscopy performed",
            "31653": "EBUS-TBNA with 3+ stations sampled",
            "31625": "BAL documented",
        },
    )


@pytest.fixture
def hybrid_result_no_disagreements(
    ebus_codes, advisor_suggestion_agreement
) -> HybridCodingResult:
    """Hybrid result with no disagreements."""
    return HybridCodingResult(
        final_codes=["31622", "31653", "31625"],
        rule_codes=["31622", "31653", "31625"],
        rule_confidence={"31622": 0.95, "31653": 0.92, "31625": 0.88},
        advisor_candidate_codes=advisor_suggestion_agreement.candidate_codes,
        advisor_code_confidence=advisor_suggestion_agreement.code_confidence,
        advisor_explanation=advisor_suggestion_agreement.explanation,
        disagreements=[],
        policy=CodingPolicy.RULES_ONLY,
        advisor_model="gemini-1.5-pro",
    )


@pytest.fixture
def hybrid_result_with_disagreements(
    advisor_suggestion_with_additions,
) -> HybridCodingResult:
    """Hybrid result with disagreements."""
    return HybridCodingResult(
        final_codes=["31622", "31653"],  # Rules win
        rule_codes=["31622", "31653"],
        rule_confidence={"31622": 0.95, "31653": 0.92},
        advisor_candidate_codes=advisor_suggestion_with_additions.candidate_codes,
        advisor_code_confidence=advisor_suggestion_with_additions.code_confidence,
        advisor_explanation=advisor_suggestion_with_additions.explanation,
        disagreements=["31625", "31627"],
        advisor_additions=["31625", "31627"],
        policy=CodingPolicy.RULES_ONLY,
        advisor_model="gemini-1.5-pro",
    )


# =============================================================================
# CODING TRACE FIXTURES
# =============================================================================

@pytest.fixture
def trace_ebus() -> CodingTrace:
    """Complete EBUS coding trace."""
    return CodingTrace(
        trace_id="trace-ebus-001",
        report_id="rpt-ebus-001",
        report_text="EBUS with stations 4R, 7, 11L",
        structured_report={"procedure_category": "ebus"},
        procedure_category="ebus",
        autocode_codes=["31622", "31653"],
        autocode_confidence={"31622": 0.95, "31653": 0.92},
        autocode_rationales={"31622": "Diagnostic", "31653": "3+ stations"},
        ncci_warnings=["31622 bundled with EBUS"],
        mer_applied=True,
        advisor_candidate_codes=["31622", "31653", "31625"],
        advisor_code_confidence={"31622": 0.92, "31653": 0.88, "31625": 0.75},
        advisor_explanation="Consider BAL code",
        advisor_disagreements=["31625"],
        advisor_model="gemini-1.5-pro",
        advisor_latency_ms=450.0,
        source="api.code_with_advisor",
        pipeline_version="v4",
    )


@pytest.fixture
def trace_with_human_review() -> CodingTrace:
    """Coding trace with human-reviewed final codes."""
    return CodingTrace(
        trace_id="trace-reviewed-001",
        report_text="Reviewed procedure",
        autocode_codes=["31622", "31653"],
        autocode_confidence={"31622": 0.95, "31653": 0.92},
        advisor_candidate_codes=["31622", "31653", "31625"],
        advisor_disagreements=["31625"],
        final_codes=["31622", "31653", "31625"],  # Human added 31625
        human_override=True,
        source="qa.human_review",
    )


# =============================================================================
# API REQUEST/RESPONSE FIXTURES
# =============================================================================

@pytest.fixture
def code_request_text() -> CodeRequest:
    """Code request with raw text."""
    return CodeRequest(
        report_text="Bronchoscopy with EBUS-TBNA of stations 4R, 7, 11L",
        procedure_category=ProcedureCategory.EBUS,
        facility_type="facility",
        include_advisor=True,
    )


@pytest.fixture
def code_request_structured(report_ebus) -> CodeRequest:
    """Code request with structured report."""
    return CodeRequest(
        structured_report=report_ebus,
        include_advisor=True,
    )


@pytest.fixture
def code_response_ebus(ebus_codes) -> CodeResponse:
    """Code response for EBUS procedure."""
    return CodeResponse(
        final_codes=["31622", "31653", "31625"],
        codes=ebus_codes,
        modifiers=["-51"],
        ncci_warnings=["31622 bundled with EBUS per NCCI"],
        mer_applied=True,
        advisor_suggestions={"31627": 0.65},
        advisor_explanation="Consider navigation code if documented",
        disagreements=["31627"],
        trace_id="test-response-001",
    )


# =============================================================================
# EVALUATION METRICS FIXTURES
# =============================================================================

@pytest.fixture
def metrics_basic() -> EvaluationMetrics:
    """Basic evaluation metrics."""
    return EvaluationMetrics(
        total_traces=100,
        traces_with_advisor=80,
        traces_with_final=50,
        full_agreement=60,
        advisor_suggested_extras=15,
        advisor_suggested_removals=5,
        unique_rule_codes=25,
        unique_advisor_codes=30,
    )


@pytest.fixture
def metrics_with_accuracy() -> EvaluationMetrics:
    """Evaluation metrics with accuracy data."""
    return EvaluationMetrics(
        total_traces=100,
        traces_with_advisor=80,
        traces_with_final=50,
        full_agreement=60,
        advisor_suggested_extras=15,
        advisor_suggested_removals=5,
        unique_rule_codes=25,
        unique_advisor_codes=30,
        rule_precision=0.92,
        rule_recall=0.88,
        advisor_precision=0.85,
        advisor_recall=0.90,
    )


# =============================================================================
# FASTAPI TEST CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """
    FastAPI test client for API testing.
    
    Creates a fresh client for each test.
    """
    from ml_advisor_router import create_app
    
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_client_with_traces(
    test_client, populated_trace_file, monkeypatch
) -> TestClient:
    """Test client with pre-populated traces."""
    monkeypatch.setenv("TRACE_FILE_PATH", str(populated_trace_file))
    return test_client


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "candidate_codes": ["31622", "31653", "31625"],
        "code_confidence": {"31622": 0.92, "31653": 0.88, "31625": 0.75},
        "explanation": "Standard EBUS codes with BAL",
        "additions": ["31625"],
        "removals": [],
        "warnings": [],
    }


@pytest.fixture
def mock_genai(mock_gemini_response):
    """
    Mock google.generativeai module.
    
    Use this to test Gemini integration without API calls.
    """
    with patch("google.generativeai") as mock:
        # Mock the model
        mock_model = MagicMock()
        mock.GenerativeModel.return_value = mock_model
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_gemini_response)
        mock_response.usage_metadata.total_token_count = 1250
        mock_model.generate_content.return_value = mock_response
        
        yield mock


@pytest.fixture
def mock_rule_engine():
    """
    Mock rule engine function.
    
    Returns predictable codes for testing.
    """
    def _mock_rule_engine(report=None, report_text=None, procedure_category=None):
        codes = [
            CodeWithConfidence(code="31622", confidence=0.95),
            CodeWithConfidence(code="31653", confidence=0.92),
        ]
        modifiers = [CodeModifier(modifier="-51", reason="MER")]
        warnings = []
        mer_applied = True
        return codes, modifiers, warnings, mer_applied
    
    return _mock_rule_engine


@pytest.fixture
def mock_advisor():
    """
    Mock ML advisor function.
    
    Returns predictable suggestions for testing.
    """
    def _mock_advisor(input_data, backend="stub"):
        return MLAdvisorSuggestion(
            candidate_codes=input_data.autocode_codes + ["31625"],
            code_confidence={
                **{c: 0.85 for c in input_data.autocode_codes},
                "31625": 0.75,
            },
            explanation="Mock advisor suggestion",
            additions=["31625"],
            model_name=f"mock-{backend}",
            latency_ms=100.0,
        )
    
    return _mock_advisor


# =============================================================================
# HELPER FUNCTIONS (Available to tests)
# =============================================================================

@pytest.fixture
def create_trace():
    """Factory fixture to create coding traces with custom data."""
    def _create_trace(**kwargs) -> CodingTrace:
        defaults = {
            "report_text": "Test procedure",
            "autocode_codes": ["31622"],
            "source": "test",
        }
        defaults.update(kwargs)
        return CodingTrace(**defaults)
    
    return _create_trace


@pytest.fixture
def create_code():
    """Factory fixture to create codes with custom data."""
    def _create_code(code: str, **kwargs) -> CodeWithConfidence:
        defaults = {
            "code": code,
            "confidence": 0.90,
        }
        defaults.update(kwargs)
        return CodeWithConfidence(**defaults)
    
    return _create_code


@pytest.fixture
def assert_valid_trace():
    """Helper to validate trace structure."""
    def _assert_valid_trace(trace: CodingTrace):
        assert trace.trace_id
        assert trace.timestamp
        assert isinstance(trace.autocode_codes, list)
        # Validate UUID format
        uuid.UUID(trace.trace_id)
    
    return _assert_valid_trace


@pytest.fixture
def assert_valid_response():
    """Helper to validate API response structure."""
    def _assert_valid_response(response: CodeResponse):
        assert response.final_codes is not None
        assert isinstance(response.final_codes, list)
        assert isinstance(response.codes, list)
        for code in response.codes:
            assert code.code
            assert 0 <= code.confidence <= 1
    
    return _assert_valid_response
