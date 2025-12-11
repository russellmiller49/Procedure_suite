"""
Test Suite for Procedure Suite ML Advisor Pydantic Schemas

Comprehensive tests covering:
- Model instantiation and defaults
- Validation rules and constraints
- Serialization/deserialization
- Computed properties
- Edge cases and error handling

Run with: pytest test_proc_ml_advisor_schemas.py -v
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from pydantic import ValidationError

# Import all models to test
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
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_stations() -> list[dict]:
    """Sample EBUS sampling stations."""
    return [
        {"station": "4R", "needle_gauge": 22, "passes": 3, "adequate": True},
        {"station": "7", "needle_gauge": 22, "passes": 2, "adequate": True},
        {"station": "11L", "needle_gauge": 21, "passes": 2, "adequate": True},
    ]


@pytest.fixture
def sample_bronchoscopy_details(sample_stations) -> dict:
    """Sample bronchoscopy procedure details."""
    return {
        "scope_type": "flexible",
        "navigation_used": False,
        "ebus_performed": True,
        "ebus_type": "linear",
        "stations_sampled": sample_stations,
        "bal_performed": True,
        "biopsy_sites": ["RUL", "RML"],
    }


@pytest.fixture
def sample_pleural_details() -> dict:
    """Sample pleural procedure details."""
    return {
        "laterality": "right",
        "volume_ml": 1500,
        "fluid_appearance": "straw-colored, clear",
        "imaging_guidance": True,
        "imaging_modality": "ultrasound",
        "permanent_image": True,
    }


@pytest.fixture
def sample_structured_report(sample_bronchoscopy_details) -> dict:
    """Sample structured procedure report."""
    return {
        "report_id": "rpt-12345",
        "procedure_category": "ebus",
        "procedure_types": ["EBUS-TBNA", "BAL"],
        "raw_text": "Bronchoscopy with EBUS-TBNA sampling of stations 4R, 7, and 11L...",
        "bronchoscopy": sample_bronchoscopy_details,
        "facility_type": "facility",
    }


@pytest.fixture
def sample_rule_codes() -> list[dict]:
    """Sample rule engine code results."""
    return [
        {
            "code": "31622",
            "code_type": "CPT",
            "confidence": 0.95,
            "description": "Diagnostic bronchoscopy",
            "is_addon": False,
        },
        {
            "code": "31653",
            "code_type": "CPT",
            "confidence": 0.92,
            "description": "EBUS-guided TBNA, 3+ stations",
            "is_addon": False,
        },
        {
            "code": "31625",
            "code_type": "CPT",
            "confidence": 0.88,
            "description": "Bronchoscopy with BAL",
            "is_addon": False,
        },
    ]


# =============================================================================
# ENUM TESTS
# =============================================================================

class TestEnums:
    """Tests for enum types."""

    def test_advisor_backend_values(self):
        """AdvisorBackend should have expected values."""
        assert AdvisorBackend.STUB.value == "stub"
        assert AdvisorBackend.GEMINI.value == "gemini"

    def test_coding_policy_values(self):
        """CodingPolicy should have expected values."""
        assert CodingPolicy.RULES_ONLY.value == "rules_only"
        assert CodingPolicy.ADVISOR_AUGMENTS.value == "advisor_augments"
        assert CodingPolicy.HUMAN_REVIEW.value == "human_review"

    def test_code_type_values(self):
        """CodeType should have expected values."""
        assert CodeType.CPT.value == "CPT"
        assert CodeType.HCPCS.value == "HCPCS"
        assert CodeType.ICD10_CM.value == "ICD10-CM"
        assert CodeType.ICD10_PCS.value == "ICD10-PCS"

    def test_procedure_category_values(self):
        """ProcedureCategory should have IP-specific categories."""
        categories = [c.value for c in ProcedureCategory]
        assert "bronchoscopy" in categories
        assert "ebus" in categories
        assert "pleural" in categories
        assert "valve" in categories
        assert "stent" in categories


# =============================================================================
# CODE-LEVEL MODEL TESTS
# =============================================================================

class TestCodeWithConfidence:
    """Tests for CodeWithConfidence model."""

    def test_basic_creation(self):
        """Should create with minimal required fields."""
        code = CodeWithConfidence(code="31622")
        assert code.code == "31622"
        assert code.code_type == CodeType.CPT
        assert code.confidence == 1.0
        assert code.is_addon is False

    def test_full_creation(self):
        """Should create with all fields."""
        code = CodeWithConfidence(
            code="31653",
            code_type=CodeType.CPT,
            confidence=0.95,
            confidence_level=ConfidenceLevel.HIGH,
            description="EBUS-guided TBNA, 3+ stations",
            is_addon=False,
        )
        assert code.confidence == 0.95
        assert code.confidence_level == ConfidenceLevel.HIGH
        assert code.description == "EBUS-guided TBNA, 3+ stations"

    def test_addon_code(self):
        """Add-on codes should have + prefix in display."""
        code = CodeWithConfidence(
            code="31627",
            is_addon=True,
            primary_code="31622",
        )
        assert code.display_code == "+31627"
        assert code.primary_code == "31622"

    def test_non_addon_display(self):
        """Non-add-on codes should not have + prefix."""
        code = CodeWithConfidence(code="31622", is_addon=False)
        assert code.display_code == "31622"

    def test_confidence_bounds(self):
        """Confidence must be between 0.0 and 1.0."""
        # Valid bounds
        CodeWithConfidence(code="31622", confidence=0.0)
        CodeWithConfidence(code="31622", confidence=1.0)
        CodeWithConfidence(code="31622", confidence=0.5)

        # Invalid - too high
        with pytest.raises(ValidationError):
            CodeWithConfidence(code="31622", confidence=1.5)

        # Invalid - negative
        with pytest.raises(ValidationError):
            CodeWithConfidence(code="31622", confidence=-0.1)

    def test_code_length_validation(self):
        """Code must be 4-10 characters."""
        # Valid lengths
        CodeWithConfidence(code="3162")  # 4 chars
        CodeWithConfidence(code="31622")  # 5 chars
        CodeWithConfidence(code="C9751")  # 5 chars HCPCS

        # Too short
        with pytest.raises(ValidationError):
            CodeWithConfidence(code="316")

    def test_frozen_model(self):
        """Model should be immutable after creation."""
        code = CodeWithConfidence(code="31622")
        with pytest.raises(ValidationError):
            code.code = "31623"

    def test_serialization(self):
        """Should serialize to dict/JSON correctly."""
        code = CodeWithConfidence(
            code="31653",
            confidence=0.92,
            description="EBUS-TBNA",
        )
        data = code.model_dump()
        assert data["code"] == "31653"
        assert data["confidence"] == 0.92

        # JSON round-trip
        json_str = code.model_dump_json()
        restored = CodeWithConfidence.model_validate_json(json_str)
        assert restored.code == code.code


class TestCodeModifier:
    """Tests for CodeModifier model."""

    def test_basic_modifier(self):
        """Should create basic modifier."""
        mod = CodeModifier(modifier="-50", reason="Bilateral procedure")
        assert mod.modifier == "-50"
        assert mod.reason == "Bilateral procedure"

    def test_modifier_pattern_validation(self):
        """Modifier must match expected pattern."""
        # Valid modifiers
        CodeModifier(modifier="-50")
        CodeModifier(modifier="-51")
        CodeModifier(modifier="-59")
        CodeModifier(modifier="22")  # Without dash
        CodeModifier(modifier="-22")

        # Invalid - too long
        with pytest.raises(ValidationError):
            CodeModifier(modifier="-123")

        # Invalid - not numeric
        with pytest.raises(ValidationError):
            CodeModifier(modifier="-XX")


class TestNCCIWarning:
    """Tests for NCCIWarning model."""

    def test_basic_warning(self):
        """Should create NCCI warning."""
        warning = NCCIWarning(
            warning_id="ncci_31622_31653",
            codes_involved=["31622", "31653"],
            message="31622 bundled with 31653 per NCCI",
            severity="warning",
        )
        assert warning.warning_id == "ncci_31622_31653"
        assert len(warning.codes_involved) == 2
        assert warning.severity == "warning"

    def test_severity_literal(self):
        """Severity must be info, warning, or error."""
        NCCIWarning(warning_id="test", message="test", severity="info")
        NCCIWarning(warning_id="test", message="test", severity="warning")
        NCCIWarning(warning_id="test", message="test", severity="error")

        with pytest.raises(ValidationError):
            NCCIWarning(warning_id="test", message="test", severity="critical")


# =============================================================================
# SAMPLING STATION TESTS
# =============================================================================

class TestSamplingStation:
    """Tests for SamplingStation model."""

    def test_valid_stations(self):
        """Should accept valid IASLC station names."""
        valid_stations = ["2R", "2L", "4R", "4L", "5", "6", "7", "8", "9",
                         "10R", "10L", "11R", "11L", "12R", "12L", "13", "14"]
        for station in valid_stations:
            s = SamplingStation(station=station)
            assert s.station == station

    def test_invalid_stations(self):
        """Should reject invalid station names."""
        invalid_stations = ["1", "3", "15", "4", "11", "XX", "4RR"]
        for station in invalid_stations:
            with pytest.raises(ValidationError):
                SamplingStation(station=station)

    def test_needle_gauge_bounds(self):
        """Needle gauge should be between 18-25."""
        SamplingStation(station="7", needle_gauge=18)
        SamplingStation(station="7", needle_gauge=22)
        SamplingStation(station="7", needle_gauge=25)

        with pytest.raises(ValidationError):
            SamplingStation(station="7", needle_gauge=16)

        with pytest.raises(ValidationError):
            SamplingStation(station="7", needle_gauge=28)

    def test_passes_positive(self):
        """Passes must be positive."""
        SamplingStation(station="7", passes=1)
        SamplingStation(station="7", passes=5)

        with pytest.raises(ValidationError):
            SamplingStation(station="7", passes=0)

        with pytest.raises(ValidationError):
            SamplingStation(station="7", passes=-1)


# =============================================================================
# PLEURAL PROCEDURE TESTS
# =============================================================================

class TestPleuralProcedureDetails:
    """Tests for PleuralProcedureDetails model."""

    def test_basic_thoracentesis(self, sample_pleural_details):
        """Should create basic thoracentesis details."""
        pleural = PleuralProcedureDetails(**sample_pleural_details)
        assert pleural.laterality == "right"
        assert pleural.volume_ml == 1500
        assert pleural.imaging_guidance is True

    def test_laterality_literal(self):
        """Laterality must be left, right, or bilateral."""
        PleuralProcedureDetails(laterality="left")
        PleuralProcedureDetails(laterality="right")
        PleuralProcedureDetails(laterality="bilateral")

        with pytest.raises(ValidationError):
            PleuralProcedureDetails(laterality="both")

    def test_imaging_modality_literal(self):
        """Imaging modality must be valid option."""
        PleuralProcedureDetails(laterality="left", imaging_modality="ultrasound")
        PleuralProcedureDetails(laterality="left", imaging_modality="fluoroscopy")
        PleuralProcedureDetails(laterality="left", imaging_modality="CT")
        PleuralProcedureDetails(laterality="left", imaging_modality="none")

        with pytest.raises(ValidationError):
            PleuralProcedureDetails(laterality="left", imaging_modality="MRI")

    def test_ipc_details(self):
        """Should support IPC-specific fields."""
        ipc = PleuralProcedureDetails(
            laterality="right",
            catheter_french=15,
            tunneled=True,
        )
        assert ipc.catheter_french == 15
        assert ipc.tunneled is True

    def test_catheter_french_bounds(self):
        """Catheter French size should be 6-32."""
        PleuralProcedureDetails(laterality="left", catheter_french=6)
        PleuralProcedureDetails(laterality="left", catheter_french=32)

        with pytest.raises(ValidationError):
            PleuralProcedureDetails(laterality="left", catheter_french=4)


# =============================================================================
# BRONCHOSCOPY PROCEDURE TESTS
# =============================================================================

class TestBronchoscopyProcedureDetails:
    """Tests for BronchoscopyProcedureDetails model."""

    def test_basic_bronchoscopy(self):
        """Should create basic bronchoscopy details."""
        bronch = BronchoscopyProcedureDetails(scope_type="flexible")
        assert bronch.scope_type == "flexible"
        assert bronch.navigation_used is False
        assert bronch.ebus_performed is False

    def test_ebus_bronchoscopy(self, sample_stations):
        """Should create EBUS bronchoscopy with stations."""
        stations = [SamplingStation(**s) for s in sample_stations]
        bronch = BronchoscopyProcedureDetails(
            scope_type="flexible",
            ebus_performed=True,
            ebus_type="linear",
            stations_sampled=stations,
        )
        assert bronch.ebus_performed is True
        assert bronch.ebus_type == "linear"
        assert len(bronch.stations_sampled) == 3

    def test_navigation_bronchoscopy(self):
        """Should create navigation bronchoscopy."""
        bronch = BronchoscopyProcedureDetails(
            scope_type="flexible",
            navigation_used=True,
            navigation_system="Ion",
        )
        assert bronch.navigation_used is True
        assert bronch.navigation_system == "Ion"

    def test_scope_type_literal(self):
        """Scope type must be flexible, rigid, or combined."""
        BronchoscopyProcedureDetails(scope_type="flexible")
        BronchoscopyProcedureDetails(scope_type="rigid")
        BronchoscopyProcedureDetails(scope_type="combined")

        with pytest.raises(ValidationError):
            BronchoscopyProcedureDetails(scope_type="video")


# =============================================================================
# STRUCTURED PROCEDURE REPORT TESTS
# =============================================================================

class TestStructuredProcedureReport:
    """Tests for StructuredProcedureReport model."""

    def test_basic_report(self):
        """Should create basic structured report."""
        report = StructuredProcedureReport(
            procedure_category=ProcedureCategory.BRONCHOSCOPY,
        )
        assert report.procedure_category == ProcedureCategory.BRONCHOSCOPY
        assert report.procedure_types == []

    def test_full_report(self, sample_structured_report):
        """Should create full structured report."""
        report = StructuredProcedureReport(**sample_structured_report)
        assert report.report_id == "rpt-12345"
        assert report.procedure_category == ProcedureCategory.EBUS
        assert "EBUS-TBNA" in report.procedure_types
        assert report.bronchoscopy is not None
        assert report.bronchoscopy.ebus_performed is True

    def test_station_count_property(self, sample_structured_report):
        """Station count should return number of sampled stations."""
        report = StructuredProcedureReport(**sample_structured_report)
        assert report.station_count == 3

    def test_station_count_no_bronchoscopy(self):
        """Station count should return 0 when no bronchoscopy."""
        report = StructuredProcedureReport(
            procedure_category=ProcedureCategory.PLEURAL,
        )
        assert report.station_count == 0

    def test_facility_type_literal(self):
        """Facility type must be valid option."""
        StructuredProcedureReport(
            procedure_category=ProcedureCategory.BRONCHOSCOPY,
            facility_type="facility",
        )
        StructuredProcedureReport(
            procedure_category=ProcedureCategory.BRONCHOSCOPY,
            facility_type="non-facility",
        )
        StructuredProcedureReport(
            procedure_category=ProcedureCategory.BRONCHOSCOPY,
            facility_type="asc",
        )

        with pytest.raises(ValidationError):
            StructuredProcedureReport(
                procedure_category=ProcedureCategory.BRONCHOSCOPY,
                facility_type="hospital",
            )


# =============================================================================
# ML ADVISOR INPUT/OUTPUT TESTS
# =============================================================================

class TestMLAdvisorInput:
    """Tests for MLAdvisorInput model."""

    def test_basic_input(self):
        """Should create basic advisor input."""
        input_data = MLAdvisorInput(
            report_text="Bronchoscopy with EBUS...",
            structured_report={"procedure": "ebus"},
        )
        assert input_data.report_text == "Bronchoscopy with EBUS..."
        assert input_data.trace_id  # Should auto-generate UUID

    def test_with_rule_codes(self):
        """Should accept rule codes for context."""
        input_data = MLAdvisorInput(
            report_text="Test",
            structured_report={},
            autocode_codes=["31622", "31653"],
        )
        assert input_data.autocode_codes == ["31622", "31653"]

    def test_auto_generated_trace_id(self):
        """Trace ID should be auto-generated UUID."""
        input1 = MLAdvisorInput(report_text="Test1", structured_report={})
        input2 = MLAdvisorInput(report_text="Test2", structured_report={})
        assert input1.trace_id != input2.trace_id
        # Should be valid UUID
        uuid.UUID(input1.trace_id)


class TestMLAdvisorSuggestion:
    """Tests for MLAdvisorSuggestion model."""

    def test_basic_suggestion(self):
        """Should create basic suggestion."""
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622", "31653"],
            code_confidence={"31622": 0.95, "31653": 0.90},
        )
        assert suggestion.candidate_codes == ["31622", "31653"]
        assert suggestion.code_confidence["31622"] == 0.95

    def test_with_disagreements(self):
        """Should track additions and removals."""
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622", "31653", "31625"],
            code_confidence={"31622": 0.95, "31653": 0.90, "31625": 0.75},
            additions=["31625"],
            removals=["31627"],
        )
        assert suggestion.additions == ["31625"]
        assert suggestion.removals == ["31627"]
        assert suggestion.disagreements == ["31625", "31627"]

    def test_disagreements_property(self):
        """Disagreements should combine additions and removals."""
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622"],
            additions=["A", "B"],
            removals=["C"],
        )
        assert suggestion.disagreements == ["A", "B", "C"]

    def test_has_suggestions_property(self):
        """has_suggestions should be True when meaningful suggestions exist."""
        # Has suggestions
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622"],
            model_name="gemini-1.5-pro",
        )
        assert suggestion.has_suggestions is True

        # Stub mode - no meaningful suggestions
        stub = MLAdvisorSuggestion(
            candidate_codes=["31622"],
            model_name="stub",
        )
        assert stub.has_suggestions is False

        # Empty suggestions
        empty = MLAdvisorSuggestion(candidate_codes=[], model_name="gemini")
        assert empty.has_suggestions is False

    def test_metadata_fields(self):
        """Should track model metadata."""
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622"],
            model_name="gemini-1.5-pro",
            latency_ms=450.5,
            tokens_used=1250,
        )
        assert suggestion.model_name == "gemini-1.5-pro"
        assert suggestion.latency_ms == 450.5
        assert suggestion.tokens_used == 1250


# =============================================================================
# HYBRID RESULT TESTS
# =============================================================================

class TestRuleEngineResult:
    """Tests for RuleEngineResult model."""

    def test_basic_result(self, sample_rule_codes):
        """Should create basic rule engine result."""
        codes = [CodeWithConfidence(**c) for c in sample_rule_codes]
        result = RuleEngineResult(codes=codes)
        assert len(result.codes) == 3
        assert result.code_list == ["31622", "31653", "31625"]

    def test_code_list_property(self, sample_rule_codes):
        """code_list should return simple list of code strings."""
        codes = [CodeWithConfidence(**c) for c in sample_rule_codes]
        result = RuleEngineResult(codes=codes)
        assert result.code_list == ["31622", "31653", "31625"]

    def test_confidence_dict_property(self, sample_rule_codes):
        """confidence_dict should map codes to confidence."""
        codes = [CodeWithConfidence(**c) for c in sample_rule_codes]
        result = RuleEngineResult(codes=codes)
        conf = result.confidence_dict
        assert conf["31622"] == 0.95
        assert conf["31653"] == 0.92


class TestHybridCodingResult:
    """Tests for HybridCodingResult model."""

    def test_basic_result(self):
        """Should create basic hybrid result."""
        result = HybridCodingResult(
            final_codes=["31622", "31653"],
            rule_codes=["31622", "31653"],
            rule_confidence={"31622": 0.95, "31653": 0.90},
        )
        assert result.final_codes == ["31622", "31653"]
        assert result.policy == CodingPolicy.RULES_ONLY

    def test_with_advisor_data(self):
        """Should include advisor suggestions."""
        result = HybridCodingResult(
            final_codes=["31622", "31653"],
            rule_codes=["31622", "31653"],
            advisor_candidate_codes=["31622", "31653", "31625"],
            advisor_code_confidence={"31622": 0.92, "31653": 0.88, "31625": 0.75},
            advisor_explanation="Consider adding 31625 for BAL",
            disagreements=["31625"],
            advisor_additions=["31625"],
        )
        assert result.advisor_candidate_codes == ["31622", "31653", "31625"]
        assert result.has_disagreements is True

    def test_has_disagreements_property(self):
        """has_disagreements should be True when differences exist."""
        # No disagreements
        result = HybridCodingResult(
            final_codes=["31622"],
            disagreements=[],
        )
        assert result.has_disagreements is False

        # Has disagreements
        result_with = HybridCodingResult(
            final_codes=["31622"],
            disagreements=["31625"],
        )
        assert result_with.has_disagreements is True

    def test_serialization(self):
        """Should serialize correctly for API response."""
        result = HybridCodingResult(
            final_codes=["31622", "31653"],
            rule_codes=["31622", "31653"],
            rule_confidence={"31622": 0.95, "31653": 0.90},
            policy=CodingPolicy.RULES_ONLY,
        )
        data = result.model_dump()
        assert data["final_codes"] == ["31622", "31653"]
        assert data["policy"] == "rules_only"


# =============================================================================
# CODING TRACE TESTS
# =============================================================================

class TestCodingTrace:
    """Tests for CodingTrace model."""

    def test_basic_trace(self):
        """Should create basic coding trace."""
        trace = CodingTrace(
            report_text="Test bronchoscopy",
            autocode_codes=["31622"],
            source="api.autocode",
        )
        assert trace.report_text == "Test bronchoscopy"
        assert trace.autocode_codes == ["31622"]
        assert trace.trace_id  # Should auto-generate

    def test_auto_generated_fields(self):
        """Trace ID and timestamp should auto-generate."""
        trace = CodingTrace(report_text="Test")
        
        # Should have valid UUID
        uuid.UUID(trace.trace_id)
        
        # Should have recent timestamp
        assert trace.timestamp is not None
        assert isinstance(trace.timestamp, datetime)

    def test_full_trace(self):
        """Should create full trace with all fields."""
        trace = CodingTrace(
            trace_id="test-trace-123",
            report_id="rpt-456",
            report_text="EBUS procedure",
            structured_report={"category": "ebus"},
            procedure_category="ebus",
            autocode_codes=["31622", "31653"],
            autocode_confidence={"31622": 0.95, "31653": 0.90},
            autocode_rationales={"31622": "Diagnostic bronch", "31653": "3+ stations"},
            ncci_warnings=["31622 bundled"],
            mer_applied=True,
            advisor_candidate_codes=["31622", "31653", "31625"],
            advisor_code_confidence={"31625": 0.75},
            advisor_explanation="Consider BAL code",
            advisor_disagreements=["31625"],
            advisor_model="gemini-1.5-pro",
            advisor_latency_ms=450.0,
            final_codes=["31622", "31653"],
            human_override=False,
            source="api.code_with_advisor",
            pipeline_version="v4.1.0",
        )
        assert trace.trace_id == "test-trace-123"
        assert trace.mer_applied is True
        assert trace.advisor_model == "gemini-1.5-pro"
        assert trace.human_override is False

    def test_frozen_model(self):
        """Trace should be immutable."""
        trace = CodingTrace(report_text="Test")
        with pytest.raises(ValidationError):
            trace.report_text = "Modified"

    def test_json_serialization(self):
        """Should serialize to JSON for JSONL logging."""
        trace = CodingTrace(
            report_text="Test",
            autocode_codes=["31622"],
            source="test",
        )
        json_str = trace.model_dump_json()
        data = json.loads(json_str)
        assert data["report_text"] == "Test"
        assert data["autocode_codes"] == ["31622"]


# =============================================================================
# API MODEL TESTS
# =============================================================================

class TestCodeRequest:
    """Tests for CodeRequest model."""

    def test_with_raw_text(self):
        """Should accept raw text input."""
        request = CodeRequest(
            report_text="Bronchoscopy with EBUS...",
            procedure_category=ProcedureCategory.EBUS,
        )
        assert request.report_text == "Bronchoscopy with EBUS..."
        assert request.structured_report is None

    def test_with_structured_report(self, sample_structured_report):
        """Should accept structured report input."""
        report = StructuredProcedureReport(**sample_structured_report)
        request = CodeRequest(structured_report=report)
        assert request.structured_report is not None
        assert request.structured_report.report_id == "rpt-12345"

    def test_include_advisor_default(self):
        """include_advisor should default to True."""
        request = CodeRequest(report_text="Test")
        assert request.include_advisor is True

    def test_facility_type_default(self):
        """facility_type should default to facility."""
        request = CodeRequest(report_text="Test")
        assert request.facility_type == "facility"


class TestCodeResponse:
    """Tests for CodeResponse model."""

    def test_basic_response(self):
        """Should create basic response."""
        response = CodeResponse(
            final_codes=["31622", "31653"],
            codes=[
                CodeWithConfidence(code="31622", confidence=0.95),
                CodeWithConfidence(code="31653", confidence=0.90),
            ],
        )
        assert response.final_codes == ["31622", "31653"]
        assert len(response.codes) == 2

    def test_with_advisor_data(self):
        """Should include advisor suggestions."""
        response = CodeResponse(
            final_codes=["31622", "31653"],
            advisor_suggestions={"31625": 0.75},
            advisor_explanation="Consider BAL code",
            disagreements=["31625"],
        )
        assert response.advisor_suggestions == {"31625": 0.75}
        assert "31625" in response.disagreements

    def test_serialization_for_api(self):
        """Should serialize correctly for FastAPI response."""
        response = CodeResponse(
            final_codes=["31622"],
            codes=[CodeWithConfidence(code="31622", confidence=0.95)],
            modifiers=["-51"],
            ncci_warnings=["Bundling warning"],
            mer_applied=True,
            trace_id="test-123",
        )
        data = response.model_dump()
        assert data["final_codes"] == ["31622"]
        assert data["modifiers"] == ["-51"]
        assert data["mer_applied"] is True


# =============================================================================
# EVALUATION METRICS TESTS
# =============================================================================

class TestEvaluationMetrics:
    """Tests for EvaluationMetrics model."""

    def test_basic_metrics(self):
        """Should create basic metrics."""
        metrics = EvaluationMetrics(
            total_traces=100,
            traces_with_advisor=80,
            full_agreement=60,
        )
        assert metrics.total_traces == 100
        assert metrics.traces_with_advisor == 80
        assert metrics.full_agreement == 60

    def test_agreement_rate_property(self):
        """Agreement rate should calculate correctly."""
        metrics = EvaluationMetrics(
            total_traces=100,
            traces_with_advisor=80,
            full_agreement=60,
        )
        assert metrics.agreement_rate == 60 / 80

    def test_agreement_rate_no_advisor(self):
        """Agreement rate should be None when no advisor traces."""
        metrics = EvaluationMetrics(
            total_traces=100,
            traces_with_advisor=0,
            full_agreement=0,
        )
        assert metrics.agreement_rate is None

    def test_precision_recall_fields(self):
        """Should support precision/recall metrics."""
        metrics = EvaluationMetrics(
            total_traces=100,
            traces_with_final=50,
            rule_precision=0.92,
            rule_recall=0.88,
            advisor_precision=0.85,
            advisor_recall=0.90,
        )
        assert metrics.rule_precision == 0.92
        assert metrics.advisor_recall == 0.90


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_full_coding_workflow(self, sample_structured_report, sample_rule_codes):
        """Test complete coding workflow with all models."""
        # 1. Create structured report
        report = StructuredProcedureReport(**sample_structured_report)

        # 2. Create advisor input
        advisor_input = MLAdvisorInput(
            trace_id="test-workflow",
            report_id=report.report_id,
            report_text=report.raw_text or "",
            structured_report=report.model_dump(),
            autocode_codes=["31622", "31653"],
            procedure_category=report.procedure_category,
        )

        # 3. Create advisor suggestion
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622", "31653", "31625"],
            code_confidence={"31622": 0.92, "31653": 0.88, "31625": 0.75},
            explanation="Consider 31625 for BAL",
            additions=["31625"],
            model_name="gemini-1.5-pro",
            latency_ms=450.0,
        )

        # 4. Create hybrid result
        hybrid = HybridCodingResult(
            final_codes=["31622", "31653"],  # Rules win
            rule_codes=["31622", "31653"],
            rule_confidence={"31622": 0.95, "31653": 0.90},
            advisor_candidate_codes=suggestion.candidate_codes,
            advisor_code_confidence=suggestion.code_confidence,
            advisor_explanation=suggestion.explanation,
            disagreements=suggestion.disagreements,
            advisor_additions=suggestion.additions,
            policy=CodingPolicy.RULES_ONLY,
            advisor_model=suggestion.model_name,
        )

        # 5. Create coding trace
        trace = CodingTrace(
            trace_id=advisor_input.trace_id,
            report_id=report.report_id,
            report_text=advisor_input.report_text,
            structured_report=advisor_input.structured_report,
            procedure_category=report.procedure_category.value,
            autocode_codes=hybrid.rule_codes,
            autocode_confidence=hybrid.rule_confidence,
            advisor_candidate_codes=hybrid.advisor_candidate_codes,
            advisor_code_confidence=hybrid.advisor_code_confidence,
            advisor_explanation=hybrid.advisor_explanation,
            advisor_disagreements=hybrid.disagreements,
            advisor_model=hybrid.advisor_model,
            source="test.workflow",
        )

        # Verify the workflow
        assert hybrid.final_codes == ["31622", "31653"]
        assert hybrid.has_disagreements is True
        assert trace.advisor_disagreements == ["31625"]

    def test_api_request_response_cycle(self, sample_structured_report):
        """Test API request/response models work together."""
        # Create request
        report = StructuredProcedureReport(**sample_structured_report)
        request = CodeRequest(
            structured_report=report,
            include_advisor=True,
        )

        # Simulate response creation
        response = CodeResponse(
            final_codes=["31622", "31653", "31625"],
            codes=[
                CodeWithConfidence(code="31622", confidence=0.95, description="Diagnostic bronch"),
                CodeWithConfidence(code="31653", confidence=0.92, description="EBUS 3+ stations"),
                CodeWithConfidence(code="31625", confidence=0.88, description="BAL"),
            ],
            modifiers=["-51"],
            mer_applied=True,
            advisor_suggestions={"31627": 0.65},
            advisor_explanation="Navigation code may apply if documented",
            disagreements=["31627"],
            trace_id="api-test-123",
        )

        # Verify serialization works for API
        response_json = response.model_dump_json()
        assert "31622" in response_json
        assert "api-test-123" in response_json

    def test_jsonl_trace_format(self):
        """Verify traces serialize correctly for JSONL logging."""
        traces = []
        for i in range(3):
            trace = CodingTrace(
                report_text=f"Procedure {i}",
                autocode_codes=["31622"],
                source="test",
            )
            traces.append(trace)

        # Simulate JSONL writing
        jsonl_lines = [t.model_dump_json() for t in traces]
        
        # Verify each line is valid JSON
        for line in jsonl_lines:
            data = json.loads(line)
            assert "trace_id" in data
            assert "timestamp" in data
            assert data["autocode_codes"] == ["31622"]


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
