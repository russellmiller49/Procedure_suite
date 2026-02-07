"""Tests for Code Reconciliation module.

These tests validate the double-check architecture where:
- Path A (Extraction): Registry Extraction → Deterministic CPT Derivation
- Path B (Prediction): ML/LLM → Probabilistic CPT Prediction

The reconciler identifies discrepancies and provides recommendations.
"""

import pytest

from app.coder.reconciliation import (
    CodeReconciler,
    ReconciliationResult,
    DiscrepancyType,
    reconcile_codes,
    ExtractionFirstPipeline,
    PipelineResult,
    run_extraction_first_pipeline,
)
from app.coder.reconciliation.reconciler import (
    CodeDiscrepancy,
    HIGH_VALUE_CODES,
    ADD_ON_CODES,
    CODE_FAMILIES,
)


class TestCodeReconcilerBasics:
    """Test basic reconciliation functionality."""

    @pytest.fixture
    def reconciler(self):
        """Create CodeReconciler instance."""
        return CodeReconciler()

    def test_perfect_match_auto_approves(self, reconciler):
        """Test: When extraction and prediction match exactly → auto_approve."""
        result = reconciler.reconcile(
            derived_codes=["31653", "31624"],
            predicted_codes=["31653", "31624"],
        )

        assert result.recommendation == "auto_approve"
        assert result.matched == ["31624", "31653"]
        assert result.extraction_only == []
        assert result.prediction_only == []
        assert result.discrepancy_type == DiscrepancyType.NONE
        assert result.confidence_score == 1.0

    def test_empty_codes_auto_approves(self, reconciler):
        """Test: Both paths returning empty is valid."""
        result = reconciler.reconcile(
            derived_codes=[],
            predicted_codes=[],
        )

        assert result.recommendation == "auto_approve"
        assert result.confidence_score == 1.0

    def test_extraction_only_codes_flagged(self, reconciler):
        """Test: Codes found by extraction but not ML are flagged."""
        result = reconciler.reconcile(
            derived_codes=["31653", "31624", "31627"],
            predicted_codes=["31653", "31624"],
        )

        assert result.recommendation == "review_needed"
        assert "31627" in result.extraction_only
        assert result.discrepancy_type == DiscrepancyType.EXTRACTION_ONLY

    def test_prediction_only_codes_flagged(self, reconciler):
        """Test: Codes predicted by ML but not extraction are flagged."""
        result = reconciler.reconcile(
            derived_codes=["31653"],
            predicted_codes=["31653", "31625"],
        )

        assert result.recommendation == "review_needed"
        assert "31625" in result.prediction_only
        assert result.discrepancy_type == DiscrepancyType.PREDICTION_ONLY

    def test_both_directions_discrepancy(self, reconciler):
        """Test: Discrepancies in both directions."""
        result = reconciler.reconcile(
            derived_codes=["31653", "31627"],
            predicted_codes=["31653", "31625"],
        )

        assert result.recommendation == "review_needed"
        assert "31627" in result.extraction_only
        assert "31625" in result.prediction_only
        assert result.discrepancy_type == DiscrepancyType.BOTH


class TestHighValueCodeHandling:
    """Test special handling for high-value codes."""

    @pytest.fixture
    def reconciler(self):
        """Create CodeReconciler with high-value flagging enabled."""
        return CodeReconciler(flag_high_value_discrepancies=True)

    def test_high_value_prediction_only_flags_audit(self, reconciler):
        """Test: High-value code predicted but not extracted → flag_for_audit."""
        # 31653 is high-value (EBUS 3+ stations)
        result = reconciler.reconcile(
            derived_codes=["31624"],
            predicted_codes=["31624", "31653"],
        )

        assert result.recommendation == "flag_for_audit"
        assert "31653" in result.prediction_only
        assert any("High-value" in reason for reason in result.review_reasons)

    def test_high_value_extraction_only_flags_audit(self, reconciler):
        """Test: High-value code extracted but not predicted → flag_for_audit."""
        result = reconciler.reconcile(
            derived_codes=["31624", "31653"],
            predicted_codes=["31624"],
        )

        assert result.recommendation == "flag_for_audit"
        assert "31653" in result.extraction_only

    def test_high_value_matched_auto_approves(self, reconciler):
        """Test: High-value code matched by both → auto_approve."""
        result = reconciler.reconcile(
            derived_codes=["31653"],
            predicted_codes=["31653"],
        )

        assert result.recommendation == "auto_approve"
        assert "31653" in result.matched

    def test_high_value_disabled_doesnt_flag_audit(self):
        """Test: With high-value flagging disabled, only review_needed."""
        reconciler = CodeReconciler(flag_high_value_discrepancies=False)

        result = reconciler.reconcile(
            derived_codes=["31624"],
            predicted_codes=["31624", "31653"],
        )

        # Without high-value flagging, single discrepancy is review_needed
        assert result.recommendation == "review_needed"


class TestConfidenceScoring:
    """Test confidence-based handling."""

    @pytest.fixture
    def reconciler(self):
        """Create CodeReconciler with default thresholds."""
        return CodeReconciler(prediction_confidence_threshold=0.5)

    def test_low_confidence_predictions_ignored(self, reconciler):
        """Test: Predictions below threshold are filtered out."""
        result = reconciler.reconcile(
            derived_codes=["31653"],
            predicted_codes=["31653", "31625"],
            prediction_confidences={"31653": 0.95, "31625": 0.3},
        )

        # 31625 should be filtered (below 0.5 threshold)
        assert result.recommendation == "auto_approve"
        assert result.prediction_only == []

    def test_high_confidence_prediction_miss_flags_audit(self, reconciler):
        """Test: High-confidence prediction not in extraction → flag_for_audit."""
        result = reconciler.reconcile(
            derived_codes=["31624"],
            predicted_codes=["31624", "31625"],
            prediction_confidences={"31624": 0.9, "31625": 0.95},
        )

        assert result.recommendation == "flag_for_audit"
        assert any("High-confidence" in reason for reason in result.review_reasons)

    def test_moderate_confidence_prediction_miss_is_review(self, reconciler):
        """Test: Moderate-confidence prediction miss → review_needed."""
        result = reconciler.reconcile(
            derived_codes=["31624"],
            predicted_codes=["31624", "31625"],
            prediction_confidences={"31624": 0.9, "31625": 0.75},
        )

        assert result.recommendation == "review_needed"

    def test_confidence_affects_score(self, reconciler):
        """Test: High-confidence misses reduce confidence score more."""
        # High confidence miss
        result_high = reconciler.reconcile(
            derived_codes=["31624"],
            predicted_codes=["31624", "31625"],
            prediction_confidences={"31624": 0.9, "31625": 0.95},
        )

        # Low confidence miss
        result_low = reconciler.reconcile(
            derived_codes=["31624"],
            predicted_codes=["31624", "31625"],
            prediction_confidences={"31624": 0.9, "31625": 0.55},
        )

        assert result_high.confidence_score < result_low.confidence_score


class TestCodeFamilies:
    """Test handling of related codes (same family)."""

    @pytest.fixture
    def reconciler(self):
        # Disable high-value flagging to test family logic in isolation
        return CodeReconciler(flag_high_value_discrepancies=False)

    def test_same_family_discrepancy_is_low_severity(self, reconciler):
        """Test: EBUS 31652 vs 31653 is same-family discrepancy."""
        result = reconciler.reconcile(
            derived_codes=["31653"],
            predicted_codes=["31652"],
        )

        # Same family = review_needed, not flag_for_audit
        assert result.recommendation == "review_needed"
        assert any("same code family" in r.lower() for r in result.review_reasons)

    def test_biopsy_family_discrepancy_handled(self, reconciler):
        """Test: Biopsy codes (31625, 31628, 31629) are same family."""
        result = reconciler.reconcile(
            derived_codes=["31625"],
            predicted_codes=["31628"],
        )

        assert result.recommendation == "review_needed"


class TestAddOnCodes:
    """Test handling of add-on codes."""

    @pytest.fixture
    def reconciler(self):
        return CodeReconciler()

    def test_addon_code_discrepancy_is_low_severity(self, reconciler):
        """Test: Add-on code discrepancies are low severity."""
        result = reconciler.reconcile(
            derived_codes=["31653", "31627"],
            predicted_codes=["31653"],
        )

        # Navigation (31627) is add-on, discrepancy is low severity
        assert result.recommendation == "review_needed"

        # Find the discrepancy for 31627
        nav_discrepancy = next(
            (d for d in result.discrepancies if d.code == "31627"), None
        )
        assert nav_discrepancy is not None
        assert nav_discrepancy.severity == "low"


class TestMultipleDiscrepancies:
    """Test handling of multiple discrepancies."""

    @pytest.fixture
    def reconciler(self):
        # Disable high-value flagging to test multiple discrepancy logic
        return CodeReconciler(flag_high_value_discrepancies=False)

    def test_three_plus_discrepancies_is_review_needed(self, reconciler):
        """Test: 3+ total discrepancies → review_needed."""
        result = reconciler.reconcile(
            derived_codes=["31653", "31624", "31627"],
            predicted_codes=["31652", "31625"],
        )

        assert result.recommendation == "review_needed"
        assert any("Multiple discrepancies" in reason for reason in result.review_reasons)

    def test_agreement_rate_calculated(self, reconciler):
        """Test: Agreement rate calculation."""
        result = reconciler.reconcile(
            derived_codes=["31653", "31624"],
            predicted_codes=["31653", "31625"],
        )

        # 1 matched (31653), 3 total unique codes
        assert result.agreement_rate == pytest.approx(1/3, rel=0.01)


class TestReconciliationResult:
    """Test ReconciliationResult properties."""

    def test_has_discrepancies_property(self):
        """Test: has_discrepancies property works correctly."""
        result_no_disc = ReconciliationResult(matched=["31653"])
        assert result_no_disc.has_discrepancies is False

        result_with_disc = ReconciliationResult(
            matched=["31653"],
            extraction_only=["31624"],
        )
        assert result_with_disc.has_discrepancies is True

    def test_total_codes_property(self):
        """Test: total_codes counts all unique codes."""
        result = ReconciliationResult(
            matched=["31653"],
            extraction_only=["31624"],
            prediction_only=["31625"],
        )
        assert result.total_codes == 3

    def test_agreement_rate_empty_codes(self):
        """Test: Agreement rate is 1.0 for empty codes."""
        result = ReconciliationResult()
        assert result.agreement_rate == 1.0


class TestConvenienceFunction:
    """Test reconcile_codes convenience function."""

    def test_reconcile_codes_function_works(self):
        """Test: reconcile_codes convenience function."""
        result = reconcile_codes(
            derived_codes=["31653", "31624"],
            predicted_codes=["31653", "31624"],
        )

        assert isinstance(result, ReconciliationResult)
        assert result.recommendation == "auto_approve"


class TestCodeNormalization:
    """Test code normalization (+ prefix handling)."""

    @pytest.fixture
    def reconciler(self):
        return CodeReconciler()

    def test_plus_prefix_normalized(self, reconciler):
        """Test: Add-on codes with + prefix are normalized."""
        result = reconciler.reconcile(
            derived_codes=["+31627", "31653"],
            predicted_codes=["31627", "31653"],
        )

        assert result.recommendation == "auto_approve"
        assert "31627" in result.matched

    def test_mixed_prefix_handling(self, reconciler):
        """Test: Mixed + prefix still matches."""
        result = reconciler.reconcile(
            derived_codes=["31653", "+31654"],
            predicted_codes=["31653", "31654"],
        )

        assert result.recommendation == "auto_approve"


class TestPipelineResult:
    """Test PipelineResult dataclass."""

    def test_needs_review_property(self):
        """Test: needs_review based on recommendation."""
        from app.registry.ml import ClinicalActions

        result_approve = PipelineResult(
            note_text="test",
            actions=ClinicalActions(),
            derived_codes=[],
            recommendation="auto_approve",
        )
        assert result_approve.needs_review is False

        result_review = PipelineResult(
            note_text="test",
            actions=ClinicalActions(),
            derived_codes=[],
            recommendation="review_needed",
        )
        assert result_review.needs_review is True

    def test_audit_trail_structure(self):
        """Test: audit_trail contains expected fields."""
        from app.registry.ml import ClinicalActions
        from app.coder.adapters.registry_coder import DerivedCode

        result = PipelineResult(
            note_text="test note",
            actions=ClinicalActions(),
            derived_codes=[
                DerivedCode(
                    code="31653",
                    description="EBUS-TBNA 3+ stations",
                    rationale="3 stations sampled",
                    evidence_fields=["ebus.stations"],
                )
            ],
            final_codes=["31653"],
            confidence=0.95,
        )

        audit = result.audit_trail
        assert audit["extraction_method"] == "extraction_first_v1"
        assert len(audit["derived_codes"]) == 1
        assert audit["derived_codes"][0]["code"] == "31653"
        assert audit["final_codes"] == ["31653"]
        assert audit["confidence"] == 0.95


class TestExtractionFirstPipeline:
    """Test the full ExtractionFirstPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return ExtractionFirstPipeline()

    def test_pipeline_extracts_ebus(self, pipeline):
        """Test: Pipeline extracts EBUS and derives codes."""
        note = """
        Procedure: EBUS bronchoscopy with TBNA
        EBUS performed with sampling of stations 4R, 7, and 11L.
        """
        result = pipeline.run(note)

        assert result.actions.ebus.performed is True
        assert len(result.actions.ebus.stations) >= 3
        assert "31653" in result.final_codes

    def test_pipeline_extracts_bal(self, pipeline):
        """Test: Pipeline extracts BAL and derives codes."""
        note = """
        Procedure: Diagnostic bronchoscopy
        BAL performed in the RML.
        """
        result = pipeline.run(note)

        assert result.actions.bal.performed is True
        assert "31624" in result.final_codes

    def test_pipeline_with_ml_predictor(self, pipeline):
        """Test: Pipeline integrates ML predictor for validation."""

        class MockMLPredictor:
            def predict(self, text):
                return ["31653", "31624"]

            def predict_proba(self, text):
                return [("31653", 0.95), ("31624", 0.88)]

        note = """
        EBUS bronchoscopy with TBNA at stations 4R, 7, 11L.
        BAL from RML.
        """
        result = pipeline.run(note, ml_predictor=MockMLPredictor())

        assert result.ml_codes == ["31653", "31624"]
        assert result.reconciliation is not None
        assert result.ml_confidences["31653"] == 0.95

    def test_pipeline_reconciliation_flags_discrepancy(self, pipeline):
        """Test: Pipeline flags when ML predicts code not in extraction."""

        class MockMLPredictor:
            def predict_proba(self, text):
                # Predicts an extra code that extraction won't find
                return [("31653", 0.95), ("31625", 0.92)]

        note = """
        EBUS bronchoscopy with TBNA at stations 4R, 7, 11L.
        """
        result = pipeline.run(note, ml_predictor=MockMLPredictor())

        # 31625 (biopsy) predicted but not extracted
        assert result.reconciliation is not None
        assert "31625" in result.reconciliation.prediction_only

    def test_pipeline_empty_note_handles_gracefully(self, pipeline):
        """Test: Empty note returns low confidence result."""
        result = pipeline.run("")

        assert result.confidence == 0.0 or len(result.warnings) > 0
        # Should not crash

    def test_pipeline_returns_audit_trail(self, pipeline):
        """Test: Pipeline result includes audit trail."""
        note = """
        EBUS bronchoscopy with TBNA at stations 4R, 7.
        """
        result = pipeline.run(note)

        audit = result.audit_trail
        assert "extraction_method" in audit
        assert "derived_codes" in audit
        assert "final_codes" in audit


class TestConveniencePipelineFunction:
    """Test run_extraction_first_pipeline convenience function."""

    def test_convenience_function_works(self):
        """Test: run_extraction_first_pipeline convenience function."""
        note = """
        Procedure: EBUS bronchoscopy
        TBNA of stations 4R, 7, 11L.
        """
        result = run_extraction_first_pipeline(note)

        assert isinstance(result, PipelineResult)
        assert result.actions.ebus.performed is True


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def pipeline(self):
        return ExtractionFirstPipeline()

    def test_malformed_ml_predictor_handled(self, pipeline):
        """Test: ML predictor that throws is handled gracefully."""

        class BrokenPredictor:
            def predict(self, text):
                raise RuntimeError("ML model failed")

        note = "EBUS bronchoscopy"
        result = pipeline.run(note, ml_predictor=BrokenPredictor())

        # Should still return extraction results
        assert result.actions is not None
        assert "ML validation unavailable" in str(result.warnings)

    def test_very_long_note_handled(self, pipeline):
        """Test: Very long notes don't crash."""
        long_note = "Procedure: EBUS bronchoscopy. " * 1000
        result = pipeline.run(long_note)

        assert result is not None

    def test_special_characters_in_note(self, pipeline):
        """Test: Notes with special characters handled."""
        note = """
        Procedure: EBUS bronchoscopy™
        Stations: 4R®, 7©, 11L
        "Quoted text" and <tags>
        """
        result = pipeline.run(note)

        # Should not crash
        assert result is not None


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    @pytest.fixture
    def pipeline(self):
        return ExtractionFirstPipeline()

    def test_complex_procedure_extraction_and_coding(self, pipeline):
        """Test: Complex multi-procedure note."""
        note = """
        Procedure: Navigational EBUS bronchoscopy

        Using superDimension navigation, the scope was advanced to the RUL nodule.
        EBUS-TBNA performed at stations 4R, 7, and 11R.
        Transbronchial biopsy obtained from the RUL lesion.
        BAL sent from the lingula.

        Complications: None
        """
        result = pipeline.run(note)

        # Check extractions
        assert result.actions.navigation.performed is True
        assert result.actions.ebus.performed is True
        assert result.actions.ebus.station_count >= 3
        assert result.actions.bal.performed is True
        assert result.actions.biopsy.transbronchial_performed is True

        # Check derived codes
        assert "31653" in result.final_codes  # EBUS 3+ stations
        assert "31627" in result.final_codes  # Navigation add-on
        assert "31624" in result.final_codes  # BAL

    def test_therapeutic_cao_procedure(self, pipeline):
        """Test: CAO therapeutic bronchoscopy."""
        note = """
        Procedure: Therapeutic bronchoscopy for CAO

        Rigid bronchoscopy performed under general anesthesia.
        Near-complete obstruction of the RMS due to tumor.
        APC applied for hemostasis and debulking.
        Balloon bronchoplasty performed.
        """
        result = pipeline.run(note)

        assert result.actions.cao.performed is True
        assert result.actions.cao.thermal_ablation_performed is True
        assert result.actions.cao.dilation_performed is True

    def test_pleural_procedure(self, pipeline):
        """Test: Pleural-only procedure."""
        note = """
        Procedure: Thoracentesis
        1500ml of straw-colored fluid removed from right pleural space.
        """
        result = pipeline.run(note)

        assert result.actions.pleural.thoracentesis_performed is True
        assert result.actions.diagnostic_bronchoscopy is False
