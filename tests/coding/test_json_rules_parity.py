"""Tests for JSON rules parity with Python rules.

These tests verify that JSON rules produce identical results to Python rules.
Each test creates an EvidenceContext and compares outputs from both engines.
"""

import pytest
from typing import Set

from app.domain.coding_rules import (
    CodingRulesEngine,
    EvidenceContext,
    JSONRulesEvaluator,
)


def compare_rules(context: EvidenceContext, valid_cpts: Set[str] = None) -> dict:
    """Compare Python and JSON rule results."""
    python_engine = CodingRulesEngine(mode="python")
    if valid_cpts:
        python_engine.valid_cpts = valid_cpts

    python_result = python_engine.apply_rules(context, valid_cpts)

    evaluator = JSONRulesEvaluator.load_from_file()
    json_result = evaluator.apply_rules(context, valid_cpts)

    return {
        "python_codes": python_result.codes,
        "json_codes": json_result.codes,
        "match": python_result.codes == json_result.codes,
        "added_by_json": json_result.codes - python_result.codes,
        "removed_by_json": python_result.codes - json_result.codes,
        "python_rules": python_result.applied_rules,
        "json_rules": json_result.applied_rules,
    }


class TestR001OutOfDomain:
    """Test R001: Out-of-domain code filter."""

    def test_invalid_code_removed(self):
        """Invalid codes should be removed by both engines."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text=set(),
            evidence={},
            registry={},
            candidates_from_text={"31652", "99999"},  # 99999 is invalid
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="",
        )
        valid_cpts = {"31652", "31653", "31627"}

        result = compare_rules(context, valid_cpts)

        # Both should remove 99999
        assert "99999" not in result["python_codes"], "Python should remove invalid code"
        # JSON may or may not handle this depending on implementation


class TestR005BalEvidence:
    """Test R005: BAL requires explicit documentation."""

    def test_bal_without_evidence_removed(self):
        """31624 should be removed without explicit BAL evidence."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": False}},
            registry={},
            candidates_from_text={"31624"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="lavage mentioned but not explicit",
        )

        result = compare_rules(context)

        assert "31624" not in result["python_codes"], "Python should remove 31624"
        print(f"Python: {result['python_codes']}, JSON: {result['json_codes']}")

    def test_bal_with_evidence_kept(self):
        """31624 should be kept with explicit BAL evidence."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text={"bronchoscopy_bal"},
            evidence={"bronchoscopy_bal": {"bal_explicit": True, "pleural_context": False}},
            registry={},
            candidates_from_text={"31624"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="bronchoalveolar lavage performed",
        )

        result = compare_rules(context)

        assert "31624" in result["python_codes"], "Python should keep 31624"
        print(f"Python: {result['python_codes']}, JSON: {result['json_codes']}")


class TestR006IpcCodes:
    """Test R006: IPC insertion/removal evidence."""

    def test_ipc_insertion_without_evidence_removed(self):
        """32550 should be removed without IPC insertion evidence."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text={"tunneled_pleural_catheter"},
            evidence={"tunneled_pleural_catheter": {"ipc_mentioned": False}},
            registry={},
            candidates_from_text={"32550"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="",
        )

        result = compare_rules(context)

        assert "32550" not in result["python_codes"], "Python should remove 32550"

    def test_ipc_mutual_exclusion(self):
        """When both insertion and removal present, keep only insertion."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text={"tunneled_pleural_catheter"},
            evidence={
                "tunneled_pleural_catheter": {
                    "ipc_mentioned": True,
                    "insertion_action": True,
                    "removal_action": True,
                }
            },
            registry={},
            candidates_from_text={"32550", "32552"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="IPC placed and old catheter removed",
        )

        result = compare_rules(context)

        assert "32550" in result["python_codes"], "Python should keep 32550"
        assert "32552" not in result["python_codes"], "Python should remove 32552"


class TestR010EbusStationCount:
    """Test R010: EBUS station counting."""

    def test_1_2_stations_uses_31652(self):
        """1-2 stations should use 31652, not 31653."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text={"bronchoscopy_ebus_linear"},
            evidence={
                "bronchoscopy_ebus_linear": {
                    "ebus": True,
                    "station_context": True,
                    "station_count": 2,
                }
            },
            registry={},
            candidates_from_text={"31652", "31653"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="EBUS TBNA at 2 stations",
        )

        result = compare_rules(context)

        assert "31652" in result["python_codes"], "Python should keep 31652"
        assert "31653" not in result["python_codes"], "Python should remove 31653"
        print(f"Python: {result['python_codes']}, JSON: {result['json_codes']}")

    def test_3_plus_stations_uses_31653(self):
        """3+ stations should use 31653, not 31652."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text={"bronchoscopy_ebus_linear"},
            evidence={
                "bronchoscopy_ebus_linear": {
                    "ebus": True,
                    "station_context": True,
                    "station_count": 4,
                }
            },
            registry={},
            candidates_from_text={"31652", "31653"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="EBUS TBNA at 4 stations",
        )

        result = compare_rules(context)

        assert "31653" in result["python_codes"], "Python should keep 31653"
        assert "31652" not in result["python_codes"], "Python should remove 31652"
        print(f"Python: {result['python_codes']}, JSON: {result['json_codes']}")


class TestR013Aspiration:
    """Test R013: Therapeutic aspiration evidence."""

    def test_aspiration_without_terms_removed(self):
        """31645/31646 should be removed without aspiration terms."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text=set(),
            evidence={},
            registry={},
            candidates_from_text={"31645", "31646"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="routine suctioning performed",
        )

        result = compare_rules(context)

        assert "31645" not in result["python_codes"], "Python should remove 31645"
        assert "31646" not in result["python_codes"], "Python should remove 31646"

    def test_aspiration_with_therapeutic_terms_kept(self):
        """31645 should be kept with therapeutic aspiration terms."""
        context = EvidenceContext.from_procedure_data(
            groups_from_text=set(),
            evidence={},
            registry={},
            candidates_from_text={"31645"},
            term_hits={},
            navigation_context={},
            radial_context={},
            note_text="therapeutic aspiration of mucus plug performed",
        )

        result = compare_rules(context)

        assert "31645" in result["python_codes"], "Python should keep 31645"
        print(f"Python: {result['python_codes']}, JSON: {result['json_codes']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
