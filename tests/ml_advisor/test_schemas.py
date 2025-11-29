"""
Test Suite for Procedure Suite ML Advisor Pydantic Schemas

Comprehensive tests covering:
- Model instantiation and defaults
- Validation rules and constraints
- Serialization/deserialization
- Computed properties
- Edge cases and error handling

Run with: pytest tests/ml_advisor/test_schemas.py -v
"""

import json
import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

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

    def test_procedure_category_values(self):
        """ProcedureCategory should have IP-specific categories."""
        categories = [c.value for c in ProcedureCategory]
        assert "bronchoscopy" in categories
        assert "ebus" in categories
        assert "pleural" in categories


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

    def test_addon_code(self):
        """Add-on codes should have + prefix in display."""
        code = CodeWithConfidence(
            code="31627",
            is_addon=True,
            primary_code="31622",
        )
        assert code.display_code == "+31627"
        assert code.primary_code == "31622"

    def test_confidence_bounds(self):
        """Confidence must be between 0.0 and 1.0."""
        CodeWithConfidence(code="31622", confidence=0.0)
        CodeWithConfidence(code="31622", confidence=1.0)

        with pytest.raises(ValidationError):
            CodeWithConfidence(code="31622", confidence=1.5)

        with pytest.raises(ValidationError):
            CodeWithConfidence(code="31622", confidence=-0.1)

    def test_code_length_validation(self):
        """Code must be 4-10 characters."""
        CodeWithConfidence(code="3162")  # 4 chars
        CodeWithConfidence(code="31622")  # 5 chars

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
        CodeModifier(modifier="-50")
        CodeModifier(modifier="-51")
        CodeModifier(modifier="22")

        with pytest.raises(ValidationError):
            CodeModifier(modifier="-123")


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
        valid_stations = ["4R", "4L", "7", "11R", "11L"]
        for station in valid_stations:
            s = SamplingStation(station=station)
            assert s.station == station

    def test_invalid_stations(self):
        """Should reject invalid station names."""
        invalid_stations = ["1", "3", "15"]
        for station in invalid_stations:
            with pytest.raises(ValidationError):
                SamplingStation(station=station)

    def test_needle_gauge_bounds(self):
        """Needle gauge should be between 18-25."""
        SamplingStation(station="7", needle_gauge=22)

        with pytest.raises(ValidationError):
            SamplingStation(station="7", needle_gauge=16)


# =============================================================================
# PLEURAL PROCEDURE TESTS
# =============================================================================

class TestPleuralProcedureDetails:
    """Tests for PleuralProcedureDetails model."""

    def test_basic_thoracentesis(self):
        """Should create basic thoracentesis details."""
        pleural = PleuralProcedureDetails(
            laterality="right",
            volume_ml=1500,
            imaging_guidance=True,
        )
        assert pleural.laterality == "right"
        assert pleural.volume_ml == 1500

    def test_laterality_literal(self):
        """Laterality must be left, right, or bilateral."""
        PleuralProcedureDetails(laterality="left")
        PleuralProcedureDetails(laterality="bilateral")

        with pytest.raises(ValidationError):
            PleuralProcedureDetails(laterality="both")


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

    def test_station_count_property(self, three_stations):
        """Station count should return number of sampled stations."""
        bronch = BronchoscopyProcedureDetails(
            scope_type="flexible",
            ebus_performed=True,
            stations_sampled=three_stations,
        )
        report = StructuredProcedureReport(
            procedure_category=ProcedureCategory.EBUS,
            bronchoscopy=bronch,
        )
        assert report.station_count == 3

    def test_station_count_no_bronchoscopy(self):
        """Station count should return 0 when no bronchoscopy."""
        report = StructuredProcedureReport(
            procedure_category=ProcedureCategory.PLEURAL,
        )
        assert report.station_count == 0


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

    def test_auto_generated_trace_id(self):
        """Trace ID should be auto-generated UUID."""
        input1 = MLAdvisorInput(report_text="Test1", structured_report={})
        input2 = MLAdvisorInput(report_text="Test2", structured_report={})
        assert input1.trace_id != input2.trace_id
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
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622"],
            model_name="gemini-1.5-pro",
        )
        assert suggestion.has_suggestions is True

        stub = MLAdvisorSuggestion(
            candidate_codes=["31622"],
            model_name="stub",
        )
        assert stub.has_suggestions is False


# =============================================================================
# HYBRID RESULT TESTS
# =============================================================================

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

    def test_has_disagreements_property(self):
        """has_disagreements should be True when differences exist."""
        result = HybridCodingResult(
            final_codes=["31622"],
            disagreements=[],
        )
        assert result.has_disagreements is False

        result_with = HybridCodingResult(
            final_codes=["31622"],
            disagreements=["31625"],
        )
        assert result_with.has_disagreements is True


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
        uuid.UUID(trace.trace_id)
        assert trace.timestamp is not None
        assert isinstance(trace.timestamp, datetime)

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

    def test_include_advisor_default(self):
        """include_advisor should default to True."""
        request = CodeRequest(report_text="Test")
        assert request.include_advisor is True


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

    def test_agreement_rate_property(self):
        """Agreement rate should calculate correctly."""
        metrics = EvaluationMetrics(
            traces_with_advisor=80,
            full_agreement=60,
        )
        assert metrics.agreement_rate == 60 / 80

    def test_agreement_rate_no_advisor(self):
        """Agreement rate should be None when no advisor traces."""
        metrics = EvaluationMetrics(
            traces_with_advisor=0,
            full_agreement=0,
        )
        assert metrics.agreement_rate is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_full_coding_workflow(self, report_ebus):
        """Test complete coding workflow with all models."""
        # 1. Create advisor input
        advisor_input = MLAdvisorInput(
            trace_id="test-workflow",
            report_id=report_ebus.report_id,
            report_text=report_ebus.raw_text or "",
            structured_report=report_ebus.model_dump(),
            autocode_codes=["31622", "31653"],
            procedure_category=report_ebus.procedure_category,
        )

        # 2. Create advisor suggestion
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622", "31653", "31625"],
            code_confidence={"31622": 0.92, "31653": 0.88, "31625": 0.75},
            explanation="Consider 31625 for BAL",
            additions=["31625"],
            model_name="gemini-1.5-pro",
            latency_ms=450.0,
        )

        # 3. Create hybrid result
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

        # 4. Create coding trace
        trace = CodingTrace(
            trace_id=advisor_input.trace_id,
            report_id=report_ebus.report_id,
            report_text=advisor_input.report_text,
            structured_report=advisor_input.structured_report,
            procedure_category=report_ebus.procedure_category.value,
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

        jsonl_lines = [t.model_dump_json() for t in traces]

        for line in jsonl_lines:
            data = json.loads(line)
            assert "trace_id" in data
            assert "timestamp" in data
            assert data["autocode_codes"] == ["31622"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
