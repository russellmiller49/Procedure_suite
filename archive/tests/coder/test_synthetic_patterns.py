"""
Test suite for EnhancedCPTCoder based on canonical synthetic_CPT_corrected.json patterns.

This file is the single source of truth for CPT coding logic validation.
Tests iterate over synthetic_CPT_corrected.json and assert that:
1. All billed_codes appear in coder output
2. No excluded_or_bundled_codes appear in output

DO NOT use earlier synthetic CSV/JSON datasets for testing.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Set

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.autocode.coder import EnhancedCPTCoder


# Use the CORRECTED canonical source - synthetic_CPT_corrected.json
DATA_PATH = ROOT / "data" / "synthetic_CPT_corrected.json"

# Minimal fallback patterns so this test suite can run in environments where the
# canonical file is not present (e.g., OSS/CI checkouts).
FALLBACK_PATTERNS: list[dict] = [
    {
        "procedure_id": "fallback_navigation_with_ablation",
        "note_text": (
            "Bronchoscopy with ENB navigation guidance to a right lower lobe "
            "squamous cell carcinoma followed by radiofrequency ablation of the lesion."
        ),
        "coding_and_billing": {
            "billed_codes": [{"cpt_code": "31641"}, {"cpt_code": "+31627"}],
            "excluded_or_bundled_codes": [],
        },
    },
    {
        "procedure_id": "fallback_ipc_placement",
        "note_text": (
            "Ultrasound-guided tunneled PleurX catheter placement for recurrent "
            "right malignant pleural effusion."
        ),
        "coding_and_billing": {
            "billed_codes": [{"cpt_code": "32550"}],
            "excluded_or_bundled_codes": [{"cpt_code": "76942"}],
        },
    },
    {
        "procedure_id": "fallback_ebus_staging_3_stations",
        "note_text": (
            "EBUS bronchoscopy with systematic mediastinal survey. "
            "TBNA performed at stations 4R, 7, and 10R."
        ),
        "coding_and_billing": {
            "billed_codes": [{"cpt_code": "31653"}],
            "excluded_or_bundled_codes": [],
        },
    },
    {
        "procedure_id": "fallback_robotic_navigation_with_radial",
        "note_text": (
            "Robotic Ion navigational bronchoscopy with radial EBUS confirmation "
            "and forceps biopsies of a peripheral left lower lobe nodule."
        ),
        "coding_and_billing": {
            "billed_codes": [{"cpt_code": "+31627"}, {"cpt_code": "+31654"}],
            "excluded_or_bundled_codes": [],
        },
    },
]


def load_canonical_patterns() -> list[dict]:
    """Load the canonical synthetic_CPT_corrected.json patterns."""
    try:
        with DATA_PATH.open() as f:
            patterns = json.load(f)
    except FileNotFoundError:
        warnings.warn(
            f"Canonical patterns file not found at {DATA_PATH}. "
            "Using minimal embedded fallback patterns for this test run.",
            RuntimeWarning,
        )
        return FALLBACK_PATTERNS

    if not isinstance(patterns, list):
        raise TypeError(f"Expected {DATA_PATH} to contain a JSON list, got {type(patterns).__name__}")

    return patterns


def normalize_code(code: str) -> str:
    """Normalize CPT code by stripping + prefix and whitespace."""
    return code.lstrip("+").strip()


def get_expected_codes(pattern: dict) -> Set[str]:
    """Extract expected billed CPT codes from a pattern."""
    coding = pattern.get("coding_and_billing", {})
    billed = coding.get("billed_codes", [])
    return {normalize_code(c.get("cpt_code", "")) for c in billed if c.get("cpt_code")}


def get_excluded_codes(pattern: dict) -> Set[str]:
    """Extract excluded/bundled CPT codes from a pattern."""
    coding = pattern.get("coding_and_billing", {})
    excluded = coding.get("excluded_or_bundled_codes", [])
    codes = set()
    for exc in excluded:
        code = exc.get("cpt_code", "")
        # Handle codes like "31654/+31654" or "N/A" - take first valid code
        if "/" in code:
            code = code.split("/")[0]
        if code and code != "N/A":
            codes.add(normalize_code(code))
    return codes


def extract_coder_codes(result: dict) -> Set[str]:
    """Extract CPT codes from coder output."""
    codes_list = result.get("codes", [])
    return {normalize_code(c.get("cpt", "")) for c in codes_list if c.get("cpt")}


# Load patterns once for parametrization
PATTERNS = load_canonical_patterns()


@pytest.fixture(scope="module")
def coder() -> EnhancedCPTCoder:
    """Create a single coder instance for all tests."""
    return EnhancedCPTCoder(use_llm_advisor=False)


class TestCanonicalPatterns:
    """Test CPT coding against canonical patterns from synthetic_CPT_corrected.json."""

    @pytest.mark.parametrize(
        "pattern",
        PATTERNS,
        ids=[p.get("procedure_id", f"pattern_{i}") for i, p in enumerate(PATTERNS)],
    )
    def test_billed_codes_detected(self, coder: EnhancedCPTCoder, pattern: dict):
        """Assert that all billed_codes appear in coder output."""
        note_text = pattern.get("note_text", "")
        procedure_id = pattern.get("procedure_id", "unknown")
        expected_codes = get_expected_codes(pattern)

        if not expected_codes:
            pytest.skip(f"Pattern {procedure_id} has no billed codes")

        result = coder.code_procedure({
            "note_text": note_text,
            "locality": "00",
            "setting": "facility"
        })
        detected_codes = extract_coder_codes(result)

        missing_codes = expected_codes - detected_codes
        assert not missing_codes, (
            f"Pattern {procedure_id}: Missing billed codes {missing_codes}. "
            f"Expected: {expected_codes}, Got: {detected_codes}"
        )

    @pytest.mark.parametrize(
        "pattern",
        PATTERNS,
        ids=[p.get("procedure_id", f"pattern_{i}") for i, p in enumerate(PATTERNS)],
    )
    def test_excluded_codes_not_present(self, coder: EnhancedCPTCoder, pattern: dict):
        """Assert that no excluded_or_bundled_codes appear in output."""
        note_text = pattern.get("note_text", "")
        procedure_id = pattern.get("procedure_id", "unknown")
        excluded_codes = get_excluded_codes(pattern)

        if not excluded_codes:
            pytest.skip(f"Pattern {procedure_id} has no excluded codes")

        result = coder.code_procedure({
            "note_text": note_text,
            "locality": "00",
            "setting": "facility"
        })
        detected_codes = extract_coder_codes(result)

        incorrectly_included = excluded_codes & detected_codes
        assert not incorrectly_included, (
            f"Pattern {procedure_id}: Incorrectly included bundled/excluded codes "
            f"{incorrectly_included}. These should have been bundled out."
        )


class TestBundlingRulesFromPatterns:
    """Test specific bundling rules derived from excluded_or_bundled_codes."""

    def test_radial_ebus_bundled_with_linear_ebus(self, coder: EnhancedCPTCoder):
        """Radial EBUS (+31654) should not appear with Linear EBUS (31652/31653) without peripheral workflow evidence."""
        note = (
            "Linear EBUS bronchoscopy performed for mediastinal staging. "
            "EBUS-TBNA performed at station 7 with multiple passes. "
            "Radial EBUS probe was used briefly (no peripheral lesion workflow documented)."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        # If linear EBUS present and there is no peripheral-lesion workflow evidence, radial should be excluded.
        peripheral_context_present = bool(detected & {"31627", "31628", "31629", "31626"})
        if ("31652" in detected or "31653" in detected) and not peripheral_context_present:
            assert "31654" not in detected, "31654 bundled with linear EBUS codes (no peripheral context)"

    def test_brushing_bundled_with_tblb(self, coder: EnhancedCPTCoder):
        """Brushing (31623) should be bundled into TBLB (31628) same lobe."""
        note = (
            "Robotic Ion navigational bronchoscopy with radial EBUS confirmation "
            "and forceps biopsies plus brushings of a peripheral left lower lobe nodule."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        if "31628" in detected:
            assert "31623" not in detected, "31623 should be bundled into 31628"

    def test_ipc_bundles_us_guidance(self, coder: EnhancedCPTCoder):
        """US guidance (76942) should be bundled with IPC placement (32550)."""
        note = (
            "Ultrasound-guided tunneled PleurX catheter placement for recurrent "
            "right malignant pleural effusion with large-volume drainage."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        if "32550" in detected:
            assert "76942" not in detected, "76942 bundled with 32550"

    def test_diagnostic_bronch_bundled_with_surgical(self, coder: EnhancedCPTCoder):
        """Diagnostic bronchoscopy (31622) bundled with surgical procedures."""
        note = (
            "Bronchoscopy with ENB and radial EBUS guidance to a right lower lobe "
            "squamous cell carcinoma followed by radiofrequency ablation of the lesion."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        # If any surgical bronchoscopy is present, 31622 should be bundled
        surgical_codes = {"31628", "31629", "31641", "31652", "31653"}
        if detected & surgical_codes:
            assert "31622" not in detected, "31622 bundled with surgical bronchoscopy"

    def test_dilation_bundled_with_stent(self, coder: EnhancedCPTCoder):
        """Balloon dilation (31630) bundled with stent placement (31631/31636)."""
        note = (
            "Bronchoscopy with balloon dilation followed by silicone Y-stent placement "
            "for malignant airway obstruction."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        if "31631" in detected or "31636" in detected:
            assert "31630" not in detected, "31630 bundled with stent placement"


class TestSpecificCodingScenarios:
    """Test specific coding scenarios from canonical patterns."""

    def test_navigation_with_ablation(self, coder: EnhancedCPTCoder):
        """Navigation + RFA should yield 31641 + 31627."""
        note = (
            "Bronchoscopy with ENB navigation guidance to a right lower lobe "
            "squamous cell carcinoma followed by radiofrequency ablation of the lesion."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        assert "31641" in detected, "31641 expected for RFA ablation"
        assert "31627" in detected, "31627 expected for ENB navigation"

    def test_ipc_placement(self, coder: EnhancedCPTCoder):
        """IPC placement should yield 32550."""
        note = (
            "Ultrasound-guided tunneled PleurX catheter placement for recurrent "
            "right malignant pleural effusion."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        assert "32550" in detected, "32550 expected for IPC placement"

    def test_robotic_navigation_with_biopsy(self, coder: EnhancedCPTCoder):
        """Robotic navigation + TBLB should yield 31628 + 31627."""
        note = (
            "Robotic Ion navigational bronchoscopy with radial EBUS confirmation "
            "and forceps biopsies of a peripheral left lower lobe nodule."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        assert "31628" in detected, "31628 expected for TBLB"
        assert "31627" in detected, "31627 expected for robotic navigation"

    def test_ebus_staging(self, coder: EnhancedCPTCoder):
        """EBUS mediastinal staging should yield 31652 or 31653."""
        note = (
            "EBUS bronchoscopy with systematic mediastinal survey. "
            "TBNA performed at stations 4R, 7, and 10R."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        assert "31652" in detected or "31653" in detected, "EBUS staging code expected"


class TestAddOnCodeLogic:
    """Test that add-on codes are properly handled."""

    def test_navigation_addon_requires_primary(self, coder: EnhancedCPTCoder):
        """Navigation (+31627) is an add-on requiring a primary procedure."""
        note = "Robotic navigational bronchoscopy with biopsy of peripheral nodule."
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        # If 31627 is present, a primary code should also be present
        if "31627" in detected:
            primary_codes = {"31628", "31629", "31641", "31652", "31653"}
            assert detected & primary_codes, "31627 requires a primary procedure code"

    def test_radial_ebus_addon(self, coder: EnhancedCPTCoder):
        """Radial EBUS (+31654) is an add-on for peripheral procedures."""
        note = (
            "Robotic navigation to peripheral nodule with radial EBUS confirmation "
            "and forceps biopsy."
        )
        result = coder.code_procedure({"note_text": note})
        detected = extract_coder_codes(result)

        # 31654 should only appear without linear EBUS
        if "31654" in detected:
            assert "31652" not in detected and "31653" not in detected


class TestPatternCoverage:
    """Verify test coverage of canonical patterns."""

    def test_all_patterns_have_billed_codes(self):
        """Every pattern should have at least one billed code."""
        for pattern in PATTERNS:
            expected = get_expected_codes(pattern)
            procedure_id = pattern.get("procedure_id", "unknown")
            assert expected, f"Pattern {procedure_id} has no billed codes"

    def test_pattern_count(self):
        """Verify expected number of canonical patterns."""
        assert len(PATTERNS) > 0, "No patterns loaded from synthetic_CPT_corrected.json"
        print(f"Loaded {len(PATTERNS)} canonical patterns for testing")


# Legacy compatibility - keep single parametrized test for backward compatibility
@pytest.mark.parametrize(
    "case",
    PATTERNS,
    ids=[c.get("procedure_id", f"case_{i}") for i, c in enumerate(PATTERNS)]
)
def test_synthetic_patterns(case: dict, coder: EnhancedCPTCoder) -> None:
    """Legacy test: Combined check for billed and excluded codes."""
    note_text = case.get("note_text", "")
    billed = get_expected_codes(case)
    excluded = get_excluded_codes(case)

    result = coder.code_procedure({
        "note_text": note_text,
        "locality": "00",
        "setting": "facility"
    })
    predicted = extract_coder_codes(result)

    missing = billed - predicted
    unexpected = predicted & excluded

    assert not missing, f"Missing billed codes {missing} for {case.get('procedure_id')}"
    assert not unexpected, f"Found excluded/bundled codes {unexpected} for {case.get('procedure_id')}"
