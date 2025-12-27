"""Comprehensive validation tests for Python vs JSON coding rules parity.

This module tests all 14 rule clusters with multiple scenarios each to ensure
the JSON rules produce identical results to the Python implementation.
"""

import pytest
from typing import Set, Dict, Any, List

from modules.domain.coding_rules import (
    CodingRulesEngine,
    EvidenceContext,
    JSONRulesEvaluator,
    RulesResult,
)


class RulesValidator:
    """Helper class to compare Python and JSON rule results."""

    def __init__(self):
        self.python_engine = CodingRulesEngine(mode="python")
        self.json_evaluator = JSONRulesEvaluator.load_from_file()

    def validate(
        self,
        groups: Set[str] = None,
        evidence: Dict[str, Any] = None,
        registry: Dict[str, Any] = None,
        candidates: Set[str] = None,
        term_hits: Dict[str, List[str]] = None,
        navigation_context: Dict[str, Any] = None,
        radial_context: Dict[str, Any] = None,
        text: str = "",
        valid_cpts: Set[str] = None,
    ) -> Dict[str, Any]:
        """Run both engines and compare results."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text=groups or set(),
            evidence=evidence or {},
            registry=registry or {},
            candidates_from_text=candidates or set(),
            term_hits=term_hits or {},
            navigation_context=navigation_context or {},
            radial_context=radial_context or {},
            note_text=text,
        )

        py_result = self.python_engine.apply_rules(context, valid_cpts)
        json_result = self.json_evaluator.apply_rules(context, valid_cpts)

        return {
            "match": py_result.codes == json_result.codes,
            "python_codes": py_result.codes,
            "json_codes": json_result.codes,
            "added_by_json": json_result.codes - py_result.codes,
            "removed_by_json": py_result.codes - json_result.codes,
            "python_rules": py_result.applied_rules,
            "json_rules": json_result.applied_rules,
        }


@pytest.fixture
def validator():
    return RulesValidator()


# =============================================================================
# R001: OUT-OF-DOMAIN CODE FILTER
# =============================================================================

class TestR001OutOfDomain:
    """Validate R001: Out-of-domain code filter."""

    def test_valid_codes_kept(self, validator):
        """Valid CPT codes with proper evidence should be retained."""
        # Use BAL codes which only need bal_explicit evidence
        result = validator.validate(
            groups={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": True}},
            candidates={"31624"},
            valid_cpts={"31624", "31627"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31624" in result["python_codes"]

    def test_invalid_codes_removed(self, validator):
        """Invalid CPT codes should be removed by R001."""
        # Note: Other rules may also remove codes. Use codes that won't be filtered by other rules.
        # BAL with explicit evidence but invalid code
        result = validator.validate(
            groups={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": True}},
            candidates={"31624", "99999"},
            valid_cpts={"31624"},  # 99999 not in valid set
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31624" in result["python_codes"]
        assert "99999" not in result["python_codes"]

    def test_empty_valid_cpts_keeps_all(self, validator):
        """With no valid_cpts filter, all candidates should be kept (subject to other rules)."""
        # Use BAL with explicit evidence
        result = validator.validate(
            groups={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": True}},
            candidates={"31624"},
            valid_cpts=None,
        )
        # When valid_cpts is empty/None, R001 doesn't filter
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31624" in result["python_codes"]


# =============================================================================
# R002: LINEAR vs RADIAL EBUS LOGIC
# =============================================================================

class TestR002EbusLogic:
    """Validate R002: Linear vs Radial EBUS logic."""

    def test_linear_ebus_upgrades_31629_to_31652(self, validator):
        """Linear EBUS group should upgrade 31629 to 31652."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {"ebus": True, "station_context": True, "station_count": 2}},
            candidates={"31629"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31629" not in result["python_codes"]
        assert "31652" in result["python_codes"]

    def test_linear_ebus_adds_31652_if_not_present(self, validator):
        """Linear EBUS group should add 31652 even without 31629."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {"ebus": True, "station_context": True, "station_count": 2}},
            candidates={"31624"},  # Some other code, not 31629
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31652" in result["python_codes"]

    def test_radial_only_excludes_linear_codes(self, validator):
        """Radial-only cases should exclude linear EBUS codes."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_radial"},  # Radial only, no linear
            evidence={"bronchoscopy_ebus_radial": {"radial": True}},
            candidates={"31652", "31653", "31654"},
            radial_context={"performed": True},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31652" not in result["python_codes"]
        assert "31653" not in result["python_codes"]

    def test_both_linear_and_radial_keeps_linear(self, validator):
        """Both linear and radial present should keep linear codes."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear", "bronchoscopy_ebus_radial"},
            evidence={
                "bronchoscopy_ebus_linear": {"ebus": True, "station_context": True, "station_count": 2},
                "bronchoscopy_ebus_radial": {"radial": True},
            },
            candidates={"31652", "31654"},
            radial_context={"performed": True},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31652" in result["python_codes"]  # Linear kept


# =============================================================================
# R003: NAVIGATION (31627)
# =============================================================================

class TestR003Navigation:
    """Validate R003: Navigation evidence requirements."""

    def test_navigation_with_full_evidence_kept(self, validator):
        """31627 with platform + concept should be kept."""
        result = validator.validate(
            groups={"bronchoscopy_navigation"},
            evidence={"bronchoscopy_navigation": {"platform": "ION", "concept": True}},
            candidates={"31627"},
            navigation_context={"performed": True},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31627" in result["python_codes"]

    def test_navigation_missing_platform_removed(self, validator):
        """31627 without platform evidence should be removed."""
        result = validator.validate(
            groups={"bronchoscopy_navigation"},
            evidence={"bronchoscopy_navigation": {"concept": True}},  # No platform
            candidates={"31627"},
            navigation_context={"performed": True},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31627" not in result["python_codes"]

    def test_navigation_missing_concept_and_direct_removed(self, validator):
        """31627 without concept or direct evidence should be removed."""
        result = validator.validate(
            groups={"bronchoscopy_navigation"},
            evidence={"bronchoscopy_navigation": {"platform": "ION"}},  # No concept/direct
            candidates={"31627"},
            navigation_context={"performed": True},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31627" not in result["python_codes"]

    def test_navigation_not_performed_removed(self, validator):
        """31627 without navigation performed should be removed."""
        result = validator.validate(
            groups=set(),
            evidence={"bronchoscopy_navigation": {"platform": "ION", "concept": True}},
            candidates={"31627"},
            navigation_context={"performed": False},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31627" not in result["python_codes"]


# =============================================================================
# R004: STENT 4-GATE EVIDENCE
# =============================================================================

class TestR004Stent:
    """Validate R004: Stent 4-gate evidence requirements."""

    def test_stent_all_gates_pass_kept(self, validator):
        """Stent with all 4 gates passed should be kept."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "tracheal_location": True,
                "stent_negated": False,
            }},
            candidates={"31631"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31631" in result["python_codes"]

    def test_stent_missing_stent_word_removed(self, validator):
        """Stent without stent_word should be removed."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "placement_action": True,
                "tracheal_location": True,
            }},
            candidates={"31631", "31636"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31631" not in result["python_codes"]
        assert "31636" not in result["python_codes"]

    def test_stent_negated_removed(self, validator):
        """Stent with negation should be removed."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "tracheal_location": True,
                "stent_negated": True,  # Negated!
            }},
            candidates={"31631"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31631" not in result["python_codes"]

    def test_stent_tracheal_only(self, validator):
        """Tracheal stent only should keep 31631, remove 31636."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "tracheal_location": True,
                "bronchial_location": False,
            }},
            candidates={"31631", "31636"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31631" in result["python_codes"]
        assert "31636" not in result["python_codes"]

    def test_stent_bronchial_only(self, validator):
        """Bronchial stent only should keep 31636, remove 31631."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "bronchial_location": True,
                "tracheal_location": False,
            }},
            candidates={"31631", "31636"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31636" in result["python_codes"]
        assert "31631" not in result["python_codes"]

    def test_stent_multiple_requires_evidence(self, validator):
        """Additional bronchial stent (+31637) requires multiple_stents evidence."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "bronchial_location": True,
                "multiple_stents": False,
            }},
            candidates={"31636", "31637"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31637" not in result["python_codes"]

    def test_stent_revision_requires_preexisting(self, validator):
        """Stent revision (31638) requires pre-existing + revision action."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "tracheal_location": True,
                "revision_action": True,
                "has_preexisting": False,  # Missing pre-existing
            }},
            candidates={"31631", "31638"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31638" not in result["python_codes"]


# =============================================================================
# R005: BAL (31624)
# =============================================================================

class TestR005Bal:
    """Validate R005: BAL evidence requirements."""

    def test_bal_explicit_kept(self, validator):
        """BAL with explicit evidence should be kept."""
        result = validator.validate(
            groups={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": True}},
            candidates={"31624"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31624" in result["python_codes"]

    def test_bal_not_explicit_removed(self, validator):
        """BAL without explicit evidence should be removed."""
        result = validator.validate(
            groups={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": False}},
            candidates={"31624"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31624" not in result["python_codes"]

    def test_bal_pleural_context_removed(self, validator):
        """BAL with pleural context should be removed."""
        result = validator.validate(
            groups={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": True, "pleural_context": True}},
            candidates={"31624"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31624" not in result["python_codes"]


# =============================================================================
# R006: IPC (32550/32552)
# =============================================================================

class TestR006Ipc:
    """Validate R006: IPC insertion/removal requirements."""

    def test_ipc_insertion_with_evidence_kept(self, validator):
        """IPC insertion with proper evidence should be kept."""
        result = validator.validate(
            groups={"tunneled_pleural_catheter"},
            evidence={"tunneled_pleural_catheter": {
                "ipc_mentioned": True,
                "insertion_action": True,
            }},
            candidates={"32550"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32550" in result["python_codes"]

    def test_ipc_insertion_missing_action_removed(self, validator):
        """IPC insertion without insertion_action should be removed."""
        result = validator.validate(
            groups={"tunneled_pleural_catheter"},
            evidence={"tunneled_pleural_catheter": {"ipc_mentioned": True}},
            candidates={"32550"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32550" not in result["python_codes"]

    def test_ipc_removal_without_action_removed(self, validator):
        """IPC removal without removal_action should be removed."""
        result = validator.validate(
            groups={"tunneled_pleural_catheter"},
            evidence={"tunneled_pleural_catheter": {"ipc_mentioned": True}},
            candidates={"32552"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32552" not in result["python_codes"]

    def test_ipc_mutual_exclusion_insertion_wins(self, validator):
        """When both insertion and removal present, insertion wins."""
        result = validator.validate(
            groups={"tunneled_pleural_catheter"},
            evidence={"tunneled_pleural_catheter": {
                "ipc_mentioned": True,
                "insertion_action": True,
                "removal_action": True,
            }},
            candidates={"32550", "32552"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32550" in result["python_codes"]
        assert "32552" not in result["python_codes"]


# =============================================================================
# R007: PLEURAL DRAINAGE (32556/32557)
# =============================================================================

class TestR007PleuralDrainage:
    """Validate R007: Pleural drainage registry requirements."""

    def test_pleural_no_registry_removed(self, validator):
        """Pleural codes without registry evidence should be removed."""
        result = validator.validate(
            candidates={"32556", "32557"},
            registry={},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32556" not in result["python_codes"]
        assert "32557" not in result["python_codes"]

    def test_pleural_chest_tube_registry_kept(self, validator):
        """Pleural codes with chest tube registry should be kept."""
        result = validator.validate(
            candidates={"32556"},
            registry={"pleural_procedure_type": "Chest Tube"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32556" in result["python_codes"]

    def test_pleural_catheter_type_registry_kept(self, validator):
        """Pleural codes with catheter type registry should be kept."""
        result = validator.validate(
            candidates={"32557"},
            registry={"pleural_catheter_type": "pigtail"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32557" in result["python_codes"]


# =============================================================================
# R008: ADDITIONAL LOBE TBLB (+31632)
# =============================================================================

class TestR008AdditionalLobe:
    """Validate R008: Additional lobe TBLB requirements."""

    def test_single_lobe_removed(self, validator):
        """Single lobe should not produce +31632."""
        result = validator.validate(
            groups={"bronchoscopy_biopsy_additional_lobe"},
            evidence={"bronchoscopy_biopsy_additional_lobe": {"lobe_count": 1}},
            candidates={"31632"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31632" not in result["python_codes"]

    def test_two_lobes_kept(self, validator):
        """Two lobes should keep +31632."""
        result = validator.validate(
            groups={"bronchoscopy_biopsy_additional_lobe"},
            evidence={"bronchoscopy_biopsy_additional_lobe": {"lobe_count": 2}},
            candidates={"31632"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31632" in result["python_codes"]

    def test_explicit_multilobe_kept(self, validator):
        """Explicit multilobe flag should keep +31632."""
        result = validator.validate(
            groups={"bronchoscopy_biopsy_additional_lobe"},
            evidence={"bronchoscopy_biopsy_additional_lobe": {"explicit_multilobe": True}},
            candidates={"31632"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31632" in result["python_codes"]


# =============================================================================
# R009: PARENCHYMAL TBBx (31628)
# =============================================================================

class TestR009Tbbx:
    """Validate R009: TBBx registry requirements."""

    def test_tbbx_no_registry_removed(self, validator):
        """TBBx without registry evidence should be removed."""
        result = validator.validate(
            candidates={"31628", "+31632"},
            registry={},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31628" not in result["python_codes"]
        assert "+31632" not in result["python_codes"]

    def test_tbbx_with_num_samples_kept(self, validator):
        """TBBx with bronch_num_tbbx > 0 should be kept."""
        result = validator.validate(
            candidates={"31628"},
            registry={"bronch_num_tbbx": 3},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31628" in result["python_codes"]

    def test_tbbx_with_tool_kept(self, validator):
        """TBBx with bronch_tbbx_tool should be kept."""
        result = validator.validate(
            candidates={"31628"},
            registry={"bronch_tbbx_tool": "Forceps"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31628" in result["python_codes"]


# =============================================================================
# R010: LINEAR EBUS STATION COUNTING
# =============================================================================

class TestR010StationCount:
    """Validate R010: EBUS station count logic."""

    def test_1_station_uses_31652(self, validator):
        """1 station should use 31652."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {
                "ebus": True,
                "station_context": True,
                "station_count": 1,
            }},
            candidates={"31652", "31653"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31652" in result["python_codes"]
        assert "31653" not in result["python_codes"]

    def test_2_stations_uses_31652(self, validator):
        """2 stations should use 31652."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {
                "ebus": True,
                "station_context": True,
                "station_count": 2,
            }},
            candidates={"31652", "31653"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31652" in result["python_codes"]
        assert "31653" not in result["python_codes"]

    def test_3_stations_uses_31653(self, validator):
        """3 stations should use 31653."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {
                "ebus": True,
                "station_context": True,
                "station_count": 3,
            }},
            candidates={"31652", "31653"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31653" in result["python_codes"]
        assert "31652" not in result["python_codes"]

    def test_5_stations_uses_31653(self, validator):
        """5 stations should use 31653."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {
                "ebus": True,
                "station_context": True,
                "station_count": 5,
            }},
            candidates={"31652", "31653"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31653" in result["python_codes"]
        assert "31652" not in result["python_codes"]

    def test_no_station_context_removes_both(self, validator):
        """No station context should remove both EBUS codes."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_linear"},
            evidence={"bronchoscopy_ebus_linear": {"ebus": True}},  # No station_context
            candidates={"31652", "31653"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31652" not in result["python_codes"]
        assert "31653" not in result["python_codes"]


# =============================================================================
# R011: RADIAL EBUS (+31654)
# =============================================================================

class TestR011RadialEbus:
    """Validate R011: Radial EBUS requirements."""

    def test_radial_with_text_and_group_kept(self, validator):
        """Radial EBUS with group + radial evidence should be kept."""
        result = validator.validate(
            groups={"bronchoscopy_ebus_radial"},
            evidence={"bronchoscopy_ebus_radial": {"radial": True}},
            candidates={"31654"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31654" in result["python_codes"]

    def test_radial_with_registry_kept(self, validator):
        """Radial EBUS with registry confirmation should be kept."""
        result = validator.validate(
            groups=set(),
            evidence={"bronchoscopy_ebus_radial": {"radial": True}},
            candidates={"31654"},
            radial_context={"performed": True},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31654" in result["python_codes"]

    def test_radial_no_confirmation_removed(self, validator):
        """Radial EBUS without confirmation should be removed."""
        result = validator.validate(
            groups=set(),
            evidence={"bronchoscopy_ebus_radial": {"radial": False}},
            candidates={"31654"},
            radial_context={},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31654" not in result["python_codes"]


# =============================================================================
# R012: TUMOR DEBULKING (31640/31641)
# =============================================================================

class TestR012Debulking:
    """Validate R012: Tumor debulking requirements."""

    def test_debulking_bundled_with_stent(self, validator):
        """Debulking should be bundled when stent is placed."""
        result = validator.validate(
            groups={"bronchoscopy_therapeutic_stent"},
            evidence={"bronchoscopy_therapeutic_stent": {
                "stent_word": True,
                "placement_action": True,
                "tracheal_location": True,
            }},
            candidates={"31631", "31640", "31641"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31640" not in result["python_codes"]
        assert "31641" not in result["python_codes"]
        assert "31631" in result["python_codes"]

    def test_debulking_ablation_selects_31641(self, validator):
        """Ablation technique should select 31641."""
        result = validator.validate(
            candidates={"31640", "31641"},
            text="apc ablation performed on tumor",
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31641" in result["python_codes"]
        assert "31640" not in result["python_codes"]

    def test_debulking_mechanical_selects_31640(self, validator):
        """Mechanical technique should select 31640."""
        result = validator.validate(
            candidates={"31640", "31641"},
            text="snare excision of tumor performed",
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31640" in result["python_codes"]
        assert "31641" not in result["python_codes"]

    def test_debulking_default_to_31641(self, validator):
        """No clear technique should default to 31641."""
        result = validator.validate(
            candidates={"31640", "31641"},
            text="tumor debulking performed",
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31641" in result["python_codes"]
        assert "31640" not in result["python_codes"]


# =============================================================================
# R013: THERAPEUTIC ASPIRATION (31645/31646)
# =============================================================================

class TestR013Aspiration:
    """Validate R013: Therapeutic aspiration requirements."""

    def test_aspiration_with_therapeutic_terms_kept(self, validator):
        """Aspiration with therapeutic terms should be kept."""
        result = validator.validate(
            candidates={"31645"},
            text="therapeutic aspiration of mucus plug performed",
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31645" in result["python_codes"]

    def test_aspiration_clot_terms_kept(self, validator):
        """Aspiration with clot terms should be kept."""
        result = validator.validate(
            candidates={"31645"},
            text="clot aspiration from the airway",
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31645" in result["python_codes"]

    def test_aspiration_routine_suctioning_removed(self, validator):
        """Routine suctioning should not trigger aspiration codes."""
        result = validator.validate(
            candidates={"31645", "31646"},
            text="routine suctioning performed",
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "31645" not in result["python_codes"]
        assert "31646" not in result["python_codes"]


# =============================================================================
# R014: THORACOSCOPY SITE PRIORITY
# =============================================================================

class TestR014Thoracoscopy:
    """Validate R014: Thoracoscopy site priority requirements."""

    def test_biopsy_trumps_diagnostic(self, validator):
        """Biopsy code should trump diagnostic-only."""
        result = validator.validate(
            groups={"thoracoscopy"},
            evidence={"thoracoscopy": {}},
            candidates={"32601", "32609"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32601" not in result["python_codes"]
        assert "32609" in result["python_codes"]

    def test_pleural_site_priority(self, validator):
        """Pleural site should take priority."""
        result = validator.validate(
            groups={"thoracoscopy"},
            evidence={"thoracoscopy": {"pleural_site": True}},
            candidates={"32604", "32606", "32609"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32609" in result["python_codes"]

    def test_diagnostic_only_kept_when_no_biopsy(self, validator):
        """Diagnostic should be kept when no biopsy codes present."""
        result = validator.validate(
            groups={"thoracoscopy"},
            evidence={"thoracoscopy": {}},
            candidates={"32601"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32601" in result["python_codes"]

    def test_temp_drain_bundled_with_thoracoscopy(self, validator):
        """Temporary drain should be bundled with thoracoscopy."""
        result = validator.validate(
            groups={"thoracoscopy"},
            evidence={"thoracoscopy": {"temporary_drain_bundled": True}},
            candidates={"32609", "32556", "32557"},
        )
        assert result["match"], f"Mismatch: Python={result['python_codes']}, JSON={result['json_codes']}"
        assert "32556" not in result["python_codes"]
        assert "32557" not in result["python_codes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
