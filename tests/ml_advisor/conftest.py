"""
Pytest Configuration and Shared Fixtures for ML Advisor Tests

This conftest.py provides:
- Shared fixtures for common test data
- Mock implementations for external dependencies
- Test environment configuration
- Custom pytest markers and hooks

Usage:
    pytest tests/ml_advisor/ -v
    pytest tests/ml_advisor/ -v -m "not integration"
    pytest tests/ml_advisor/ -v --cov=modules.proc_ml_advisor
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

from modules.proc_ml_advisor.schemas import (
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


# =============================================================================
# ENVIRONMENT FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def test_env():
    """Session-scoped fixture that sets up test environment variables."""
    original_env = os.environ.copy()

    os.environ.update({
        "ENABLE_ML_ADVISOR": "true",
        "ADVISOR_BACKEND": "stub",
        "ENABLE_CODING_TRACE": "true",
        "PIPELINE_VERSION": "test-v1",
    })

    yield os.environ

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
def ebus_codes(code_31622, code_31653, code_31625) -> list[CodeWithConfidence]:
    """Standard EBUS code set."""
    return [code_31622, code_31653, code_31625]


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


# =============================================================================
# HYBRID RESULT FIXTURES
# =============================================================================

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
        pipeline_version="v5",
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


# =============================================================================
# FASTAPI TEST CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """FastAPI test client for API testing."""
    from modules.api.fastapi_app import app

    with TestClient(app) as client:
        yield client


# =============================================================================
# HELPER FIXTURES
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
