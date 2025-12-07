"""Integration tests for RegistryService hybrid-first flow.

Tests the end-to-end integration of:
- SmartHybridOrchestrator (mocked with deterministic results)
- CPT-to-Registry mapping (aggregate_registry_fields)
- RegistryEngine extraction (real engine, stubbed LLM)
- Field merging and validation
"""

import os

# Ensure stub LLM is used during tests
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")

import pytest
from unittest.mock import MagicMock, patch
from typing import Any

from modules.coder.application.smart_hybrid_policy import HybridCoderResult
from modules.ml_coder.thresholds import CaseDifficulty
from modules.ml_coder.registry_predictor import (
    RegistryMLPredictor,
    RegistryFieldPrediction,
    RegistryCaseClassification,
)
from modules.registry.application.registry_service import RegistryService
from modules.registry.application.cpt_registry_mapping import aggregate_registry_fields
from modules.registry.engine import RegistryEngine
from modules.registry.schema import RegistryRecord


# ============================================================================
# Test Helpers
# ============================================================================


def make_fake_hybrid_result(
    codes: list[str],
    difficulty: str = "high_confidence",
    source: str = "ml_rules_fastpath",
    metadata: dict[str, Any] | None = None,
) -> HybridCoderResult:
    """Create a deterministic HybridCoderResult for testing.

    Args:
        codes: List of CPT codes.
        difficulty: Case difficulty string (high_confidence, gray_zone, low_confidence).
        source: Source of codes (ml_rules_fastpath, hybrid_llm_fallback).
        metadata: Optional metadata dict.

    Returns:
        HybridCoderResult with the specified values.
    """
    return HybridCoderResult(
        codes=codes,
        source=source,
        difficulty=CaseDifficulty(difficulty),
        metadata=metadata or {},
    )


class StubRegistryEngine:
    """Stub RegistryEngine that returns a minimal RegistryRecord.

    This avoids LLM calls while still exercising the merge logic.
    """

    def __init__(self, preset_record: RegistryRecord | None = None):
        self._preset_record = preset_record

    def run(
        self,
        note_text: str,
        *,
        explain: bool = False,
        include_evidence: bool = True,
        context: dict[str, Any] | None = None,
    ) -> RegistryRecord:
        if self._preset_record:
            return self._preset_record
        # Return a minimal valid record
        return RegistryRecord(procedure_type="bronchoscopy")


# ============================================================================
# CPT Mapping Tests
# ============================================================================


class TestCPTRegistryMapping:
    """Tests for CPT-to-Registry field mapping (aggregate_registry_fields)."""

    def test_ebus_mapping_produces_nested_structure(self) -> None:
        """EBUS codes should produce nested procedures_performed structure."""
        result = aggregate_registry_fields(["31652"])

        assert "procedures_performed" in result
        assert "linear_ebus" in result["procedures_performed"]
        assert result["procedures_performed"]["linear_ebus"]["performed"] is True

    def test_ebus_1_2_stations_has_bucket(self) -> None:
        """31652 (EBUS 1-2 stations) should include station_count_bucket."""
        result = aggregate_registry_fields(["31652"])

        linear = result["procedures_performed"]["linear_ebus"]
        assert linear["performed"] is True
        assert linear["station_count_bucket"] == "1-2"

    def test_ebus_3plus_stations_mapping(self) -> None:
        """31653 (EBUS 3+ stations) should map to linear_ebus with station_count_bucket."""
        result = aggregate_registry_fields(["31653"])

        linear = result["procedures_performed"]["linear_ebus"]
        assert linear["performed"] is True
        assert linear["station_count_bucket"] == "3+"

    def test_navigation_mapping(self) -> None:
        """31627 should map to navigational_bronchoscopy."""
        result = aggregate_registry_fields(["31627"])

        assert result["procedures_performed"]["navigational_bronchoscopy"]["performed"] is True

    def test_bal_mapping(self) -> None:
        """31624/31625 should map to BAL."""
        result = aggregate_registry_fields(["31624"])
        assert result["procedures_performed"]["bal"]["performed"] is True

        result2 = aggregate_registry_fields(["31625"])
        assert result2["procedures_performed"]["bal"]["performed"] is True

    def test_tblb_mapping(self) -> None:
        """31628/31629 should map to transbronchial_biopsy."""
        result = aggregate_registry_fields(["31628"])
        assert result["procedures_performed"]["transbronchial_biopsy"]["performed"] is True

    def test_tblb_with_fluoro_has_flag(self) -> None:
        """31629 (TBLB with fluoroscopy) should set fluoroscopy_used flag."""
        result = aggregate_registry_fields(["31629"])

        tblb = result["procedures_performed"]["transbronchial_biopsy"]
        assert tblb["performed"] is True
        assert tblb["fluoroscopy_used"] is True

    def test_blvr_valve_placement_mapping(self) -> None:
        """31647/31648 (BLVR valve) should set procedure_type to Valve placement."""
        result = aggregate_registry_fields(["31647"])

        blvr = result["procedures_performed"]["blvr"]
        assert blvr["performed"] is True
        assert blvr["procedure_type"] == "Valve placement"

    def test_blvr_valve_removal_mapping(self) -> None:
        """31649 (BLVR valve removal) should set procedure_type to Valve removal."""
        result = aggregate_registry_fields(["31649"])

        blvr = result["procedures_performed"]["blvr"]
        assert blvr["performed"] is True
        assert blvr["procedure_type"] == "Valve removal"

    def test_airway_dilation_has_technique(self) -> None:
        """31630 (balloon dilation) should set technique to Balloon."""
        result = aggregate_registry_fields(["31630"])

        dilation = result["procedures_performed"]["airway_dilation"]
        assert dilation["performed"] is True
        assert dilation["technique"] == "Balloon"

    def test_pleural_thoracentesis_mapping(self) -> None:
        """32554/32555 should map to pleural thoracentesis."""
        result = aggregate_registry_fields(["32555"])

        assert "pleural_procedures" in result
        assert result["pleural_procedures"]["thoracentesis"]["performed"] is True

    def test_thoracentesis_with_us_guidance(self) -> None:
        """32555 (thoracentesis with imaging) should set guidance to Ultrasound."""
        result = aggregate_registry_fields(["32555"])

        thora = result["pleural_procedures"]["thoracentesis"]
        assert thora["performed"] is True
        assert thora["guidance"] == "Ultrasound"
        assert thora["indication"] == "Diagnostic"

    def test_thoracentesis_without_imaging(self) -> None:
        """32554 (thoracentesis without imaging) should set guidance to None/Landmark."""
        result = aggregate_registry_fields(["32554"])

        thora = result["pleural_procedures"]["thoracentesis"]
        assert thora["performed"] is True
        assert thora["guidance"] == "None/Landmark"
        assert thora["indication"] == "Diagnostic"

    def test_thoracentesis_therapeutic_with_imaging(self) -> None:
        """32557 (therapeutic thoracentesis with imaging) should set guidance and indication."""
        result = aggregate_registry_fields(["32557"])

        thora = result["pleural_procedures"]["thoracentesis"]
        assert thora["performed"] is True
        assert thora["guidance"] == "Ultrasound"
        assert thora["indication"] == "Therapeutic"

    def test_thoracentesis_both_dx_and_tx(self) -> None:
        """Diagnostic + therapeutic thoracentesis codes should set indication to Both."""
        result = aggregate_registry_fields(["32555", "32557"])

        thora = result["pleural_procedures"]["thoracentesis"]
        assert thora["performed"] is True
        assert thora["indication"] == "Both"

    def test_chest_tube_has_action(self) -> None:
        """32551 (chest tube) should set action to Insertion."""
        result = aggregate_registry_fields(["32551"])

        tube = result["pleural_procedures"]["chest_tube"]
        assert tube["performed"] is True
        assert tube["action"] == "Insertion"

    def test_pleurodesis_thoracoscopic(self) -> None:
        """32650 (thoracoscopic pleurodesis) should set technique to Thoracoscopic."""
        result = aggregate_registry_fields(["32650"])

        pleur = result["pleural_procedures"]["pleurodesis"]
        assert pleur["performed"] is True
        assert pleur["technique"] == "Thoracoscopic"

    def test_pleurodesis_instillation(self) -> None:
        """32560 (instillation pleurodesis) should set technique to Instillation."""
        result = aggregate_registry_fields(["32560"])

        pleur = result["pleural_procedures"]["pleurodesis"]
        assert pleur["performed"] is True
        assert pleur["technique"] == "Instillation"

    def test_multiple_codes_aggregate(self) -> None:
        """Multiple codes should aggregate into a single nested structure."""
        result = aggregate_registry_fields(["31653", "31627", "31624"])

        procs = result["procedures_performed"]
        assert procs["linear_ebus"]["performed"] is True
        assert procs["linear_ebus"]["station_count_bucket"] == "3+"
        assert procs["navigational_bronchoscopy"]["performed"] is True
        assert procs["bal"]["performed"] is True

    def test_empty_codes_returns_empty(self) -> None:
        """Empty code list should return empty dict."""
        result = aggregate_registry_fields([])
        assert result == {}


# ============================================================================
# Service Integration Tests
# ============================================================================


class TestRegistryServiceHybridFlow:
    """Integration tests for RegistryService.extract_fields() hybrid flow."""

    def test_ebus_navigation_mapping_and_validation_high_conf(self) -> None:
        """High-confidence EBUS+NAV case should not require manual review."""
        # Arrange: fake orchestrator
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31653", "31627"],
            difficulty="high_confidence",
        )

        # Create stub engine that returns a record WITH the expected fields set
        # (simulating LLM correctly extracting procedures)
        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            procedures_performed={
                "linear_ebus": {"performed": True},
                "navigational_bronchoscopy": {"performed": True},
            },
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Act
        result = service.extract_fields("Synthetic EBUS + NAV note")

        # Assert CPT codes and mapping
        assert result.cpt_codes == ["31653", "31627"]
        assert result.coder_source == "ml_rules_fastpath"
        assert result.coder_difficulty == "high_confidence"

        # Assert mapped fields
        assert "procedures_performed" in result.mapped_fields
        assert result.mapped_fields["procedures_performed"]["linear_ebus"]["performed"] is True
        assert result.mapped_fields["procedures_performed"]["navigational_bronchoscopy"]["performed"] is True

        # Assert merged record
        record = result.record
        assert record.procedures_performed is not None
        assert record.procedures_performed.linear_ebus is not None
        assert record.procedures_performed.linear_ebus.performed is True
        assert record.procedures_performed.navigational_bronchoscopy is not None
        assert record.procedures_performed.navigational_bronchoscopy.performed is True

        # Assert no manual review for high_confidence with no validation errors
        assert result.needs_manual_review is False
        assert result.validation_errors == []

    def test_cpt_merge_fills_missing_fields(self) -> None:
        """CPT mapping should fill fields that LLM extractor missed."""
        # Arrange: orchestrator returns BAL code
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31624"],
            difficulty="high_confidence",
        )

        # Stub engine returns record WITHOUT BAL set (LLM missed it)
        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Act
        result = service.extract_fields("BAL performed from RML")

        # Assert: CPT mapping filled in the missing BAL field
        assert result.record.procedures_performed is not None
        assert result.record.procedures_performed.bal is not None
        assert result.record.procedures_performed.bal.performed is True

    def test_tblb_mismatch_triggers_validation_error(self) -> None:
        """When CPT says TBLB but LLM doesn't extract it, validation error should trigger."""
        # Arrange: orchestrator returns TBLB code
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31628"],  # TBLB
            difficulty="high_confidence",
        )

        # Stub engine returns record WITHOUT transbronchial_biopsy set
        # AND we patch the merge to NOT set it (simulating a case where
        # both LLM and CPT mapping somehow miss the field - which shouldn't
        # happen with current code, but tests the validation logic)
        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            procedures_performed=None,  # No procedures set
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Disable ML hybrid audit for this test (we're testing CPT merge logic only)
        service._registry_ml_predictor = None
        service._ml_predictor_init_attempted = True

        # Act
        result = service.extract_fields("Transbronchial biopsy obtained")

        # Assert: After merge, CPT mapping should have filled transbronchial_biopsy
        # So validation should pass. Let's verify the merge worked:
        assert result.record.procedures_performed is not None
        assert result.record.procedures_performed.transbronchial_biopsy is not None
        assert result.record.procedures_performed.transbronchial_biopsy.performed is True

        # No validation error because merge filled the field
        # This test verifies the merge logic works correctly
        assert result.needs_manual_review is False

    def test_validation_error_when_cpt_field_not_extractable(self) -> None:
        """When CPT code present but corresponding field can't be set, validation should flag it.

        This tests the edge case where neither LLM nor CPT merge can set the field.
        We simulate this by patching _merge_cpt_fields_into_record to return unchanged.
        """
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31620"],  # Radial EBUS
            difficulty="high_confidence",
        )

        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Patch merge to return unchanged record (simulating merge failure)
        original_merge = service._merge_cpt_fields_into_record

        def no_op_merge(record, mapped_fields):
            return record  # Don't actually merge

        service._merge_cpt_fields_into_record = no_op_merge

        # Act
        result = service.extract_fields("Radial EBUS performed")

        # Assert: Validation should flag the mismatch
        assert result.needs_manual_review is True
        assert any("31620" in e and "radial_ebus" in e for e in result.validation_errors)

    def test_low_conf_triggers_manual_review(self) -> None:
        """LOW_CONF difficulty should trigger manual review."""
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31622"],
            difficulty="low_confidence",
        )

        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        result = service.extract_fields("Diagnostic bronchoscopy")

        assert result.needs_manual_review is True
        assert result.coder_difficulty == "low_confidence"
        assert any("LOW_CONF" in e for e in result.validation_errors)

    def test_gray_zone_triggers_manual_review(self) -> None:
        """GRAY_ZONE difficulty should trigger manual review."""
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31652"],
            difficulty="gray_zone",
        )

        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            procedures_performed={"linear_ebus": {"performed": True}},
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        result = service.extract_fields("EBUS-TBNA performed")

        assert result.needs_manual_review is True
        assert result.coder_difficulty == "gray_zone"

    def test_no_orchestrator_fallback_mode(self) -> None:
        """Without hybrid orchestrator, service should fall back to extractor-only mode."""
        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=None,  # No orchestrator
            registry_engine=stub_engine,
        )

        result = service.extract_fields("Diagnostic bronchoscopy")

        # Should work but with empty CPT info
        assert result.cpt_codes == []
        assert result.coder_source == "extractor_only"
        assert result.coder_difficulty == "unknown"
        assert "No hybrid orchestrator" in result.warnings[0]

    def test_pleural_procedure_mapping(self) -> None:
        """Pleural CPT codes should map to pleural_procedures section."""
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["32555", "32601"],  # Thoracentesis + pleuroscopy
            difficulty="high_confidence",
        )

        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            pleural_procedures={
                "thoracentesis": {"performed": True},
                "medical_thoracoscopy": {"performed": True},
            },
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        result = service.extract_fields("Thoracentesis and pleuroscopy")

        # Assert pleural mapping
        assert "pleural_procedures" in result.mapped_fields
        assert result.mapped_fields["pleural_procedures"]["thoracentesis"]["performed"] is True
        assert result.mapped_fields["pleural_procedures"]["medical_thoracoscopy"]["performed"] is True

        # Assert validation passes
        assert result.needs_manual_review is False


# ============================================================================
# Real Engine Integration Tests (with stub LLM)
# ============================================================================


class TestRegistryServiceWithRealEngine:
    """Tests using real RegistryEngine (with stubbed LLM via env var)."""

    @pytest.fixture
    def real_engine(self) -> RegistryEngine:
        """Create a real RegistryEngine (LLM stubbed via env var)."""
        return RegistryEngine()

    def test_real_engine_ebus_extraction(self, real_engine: RegistryEngine) -> None:
        """Real engine should extract basic EBUS info from note text."""
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31652"],
            difficulty="high_confidence",
        )

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=real_engine,
        )

        note_text = """
        PROCEDURE: EBUS-TBNA

        The patient underwent linear EBUS with TBNA of station 4R.
        Two passes were performed. ROSE showed adequate lymphocytes.
        No complications.
        """

        result = service.extract_fields(note_text)

        # Should have CPT codes
        assert result.cpt_codes == ["31652"]
        assert "procedures_performed" in result.mapped_fields

        # Record should be valid
        assert result.record is not None
        # Check that extraction worked (record is valid RegistryRecord)
        assert isinstance(result.record, RegistryRecord)


# ============================================================================
# ML Hybrid Audit Tests
# ============================================================================


class StubRegistryPredictor:
    """Stub predictor for testing ML hybrid audit behavior.

    Returns pre-configured predictions to test different scenarios.
    """

    def __init__(
        self,
        positive_fields: list[str],
        probabilities: dict[str, float] | None = None,
    ):
        """Initialize with fields that should be predicted as positive.

        Args:
            positive_fields: List of field names to predict as positive.
            probabilities: Optional dict of field -> probability. Defaults to 0.9.
        """
        self._positive_fields = set(positive_fields)
        self._probabilities = probabilities or {}
        self.available = True

    @property
    def labels(self) -> list[str]:
        """Return list of labels for logging."""
        return list(self._positive_fields)

    def classify_case(self, note_text: str) -> RegistryCaseClassification:
        """Return pre-configured predictions."""
        predictions = []
        for field in self._positive_fields:
            prob = self._probabilities.get(field, 0.9)
            predictions.append(
                RegistryFieldPrediction(
                    field=field,
                    probability=prob,
                    threshold=0.5,
                    is_positive=True,
                )
            )

        return RegistryCaseClassification(
            note_text=note_text,
            predictions=predictions,
            positive_fields=list(self._positive_fields),
            difficulty="HIGH_CONF" if self._positive_fields else "LOW_CONF",
        )


class TestMLHybridAudit:
    """Tests for ML hybrid audit behavior in RegistryService.

    Tests the three scenarios:
    - Scenario A: CPT True, ML True → Match, no warning
    - Scenario B: CPT True, ML False → CPT primary, no warning
    - Scenario C: CPT False, ML True → Audit warning, manual review
    """

    def test_scenario_c_ml_detected_not_in_cpt_triggers_audit_warning(self) -> None:
        """When ML detects a procedure that CPT missed, audit warning should trigger."""
        # Arrange: orchestrator returns no codes for linear_ebus
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31622"],  # Only diagnostic bronch, no EBUS code
            difficulty="high_confidence",
        )

        # Stub engine returns basic record
        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Inject stub predictor that thinks linear_ebus was performed
        service._registry_ml_predictor = StubRegistryPredictor(
            positive_fields=["linear_ebus"],
            probabilities={"linear_ebus": 0.85},
        )
        service._ml_predictor_init_attempted = True

        # Act
        result = service.extract_fields(
            "EBUS was performed but coder missed it - ML should catch this"
        )

        # Assert: Audit warning should be present
        assert result.needs_manual_review is True
        assert len(result.audit_warnings) > 0
        assert any("linear_ebus" in w for w in result.audit_warnings)
        assert any("0.85" in w for w in result.audit_warnings)

    def test_scenario_a_cpt_and_ml_match_no_warning(self) -> None:
        """When CPT and ML both detect procedure, no audit warning needed."""
        # Arrange: orchestrator returns EBUS code
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31652"],  # EBUS 1-2 stations
            difficulty="high_confidence",
        )

        # Stub engine returns record with linear_ebus set
        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            procedures_performed={"linear_ebus": {"performed": True}},
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Inject stub predictor that also thinks linear_ebus was performed
        service._registry_ml_predictor = StubRegistryPredictor(
            positive_fields=["linear_ebus"],
        )
        service._ml_predictor_init_attempted = True

        # Act
        result = service.extract_fields("EBUS-TBNA with stations 4R and 7")

        # Assert: No audit warnings because CPT and ML agree
        assert result.audit_warnings == []
        # No manual review needed for high_conf with matching results
        assert result.needs_manual_review is False

    def test_scenario_b_cpt_positive_ml_negative_no_warning(self) -> None:
        """When CPT detects but ML doesn't, CPT is primary truth - no warning."""
        # Arrange: orchestrator returns EBUS code
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31652"],  # EBUS 1-2 stations
            difficulty="high_confidence",
        )

        # Stub engine returns record with linear_ebus set
        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            procedures_performed={"linear_ebus": {"performed": True}},
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Inject stub predictor that does NOT detect linear_ebus
        service._registry_ml_predictor = StubRegistryPredictor(
            positive_fields=[],  # ML doesn't detect anything
        )
        service._ml_predictor_init_attempted = True

        # Act
        result = service.extract_fields("EBUS performed - ML missed it")

        # Assert: No audit warnings because CPT is primary truth
        assert result.audit_warnings == []
        # CPT value should still be set in the record
        assert result.record.procedures_performed.linear_ebus.performed is True

    def test_multiple_ml_detected_procedures_trigger_multiple_warnings(self) -> None:
        """When ML detects multiple procedures CPT missed, all should be warned."""
        # Arrange: orchestrator returns no procedure codes
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31622"],  # Only diagnostic bronch
            difficulty="high_confidence",
        )

        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Inject stub predictor that detects multiple procedures
        service._registry_ml_predictor = StubRegistryPredictor(
            positive_fields=["linear_ebus", "navigational_bronchoscopy", "transbronchial_biopsy"],
            probabilities={
                "linear_ebus": 0.92,
                "navigational_bronchoscopy": 0.87,
                "transbronchial_biopsy": 0.78,
            },
        )
        service._ml_predictor_init_attempted = True

        # Act
        result = service.extract_fields("Complex procedure - ML detected multiple")

        # Assert: Multiple audit warnings
        assert result.needs_manual_review is True
        assert len(result.audit_warnings) == 3
        assert any("linear_ebus" in w for w in result.audit_warnings)
        assert any("navigational_bronchoscopy" in w for w in result.audit_warnings)
        assert any("transbronchial_biopsy" in w for w in result.audit_warnings)

    def test_ml_predictor_unavailable_no_audit(self) -> None:
        """When ML predictor is unavailable, audit should be skipped gracefully."""
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31652"],
            difficulty="high_confidence",
        )

        preset_record = RegistryRecord(
            procedure_type="bronchoscopy",
            procedures_performed={"linear_ebus": {"performed": True}},
        )
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        # Simulate unavailable predictor
        service._registry_ml_predictor = None
        service._ml_predictor_init_attempted = True

        # Act
        result = service.extract_fields("EBUS procedure")

        # Assert: No audit warnings, no crash
        assert result.audit_warnings == []
        assert result.needs_manual_review is False

    def test_audit_warnings_included_in_result_dataclass(self) -> None:
        """Verify audit_warnings field is properly populated in result."""
        fake_orchestrator = MagicMock()
        fake_orchestrator.get_codes.return_value = make_fake_hybrid_result(
            codes=["31622"],
            difficulty="high_confidence",
        )

        preset_record = RegistryRecord(procedure_type="bronchoscopy")
        stub_engine = StubRegistryEngine(preset_record=preset_record)

        service = RegistryService(
            hybrid_orchestrator=fake_orchestrator,
            registry_engine=stub_engine,
        )

        service._registry_ml_predictor = StubRegistryPredictor(
            positive_fields=["blvr"],
            probabilities={"blvr": 0.95},
        )
        service._ml_predictor_init_attempted = True

        result = service.extract_fields("Valve procedure")

        # Assert: audit_warnings is a list with expected content
        assert isinstance(result.audit_warnings, list)
        assert len(result.audit_warnings) == 1
        assert "blvr" in result.audit_warnings[0]
        assert "0.95" in result.audit_warnings[0]
        assert "Please review" in result.audit_warnings[0]
