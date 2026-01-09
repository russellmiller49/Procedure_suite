"""Tests for NCCI bundling gatekeeper."""

from __future__ import annotations

from modules.autocode.coder import EnhancedCPTCoder
from modules.coder.ncci import (
    NCCIEngine,
    NCCI_BUNDLED_REASON_PREFIX,
    load_ncci_ptp,
)
from modules.coder.rules_engine import CodingRulesEngine
from modules.coder.types import CodeCandidate


def test_ncci_engine_bundles_column2_when_both_present():
    engine = NCCIEngine(ptp_cfg=load_ncci_ptp())
    result = engine.apply({"31653", "31645"})

    assert "31653" in result.allowed
    assert "31645" not in result.allowed
    assert result.bundled.get("31645") == "31653"


def test_ncci_engine_does_not_bundle_when_primary_missing():
    engine = NCCIEngine(ptp_cfg=load_ncci_ptp())
    result = engine.apply({"31645"})

    assert "31645" in result.allowed
    assert "31645" not in result.bundled


def test_rules_engine_marks_bundled_code_and_ignores_confidence():
    engine = CodingRulesEngine()
    candidates = [
        CodeCandidate(code="31653", confidence=0.4),
        CodeCandidate(code="31645", confidence=0.99),
    ]

    ruled = engine.apply(candidates, note_text="synthetic bronchoscopy note")
    bundled = [c for c in ruled if c.code == "31645"]
    assert bundled
    reason = bundled[0].reason or ""
    assert f"{NCCI_BUNDLED_REASON_PREFIX}31653" in reason


def test_enhanced_cptcoder_drops_bundled_codes_from_final_list():
    coder = EnhancedCPTCoder.__new__(EnhancedCPTCoder)  # type: ignore[misc]
    candidates = [
        CodeCandidate(code="31653", confidence=0.6),
        CodeCandidate(
            code="31645",
            confidence=0.9,
            reason=f"{NCCI_BUNDLED_REASON_PREFIX}31653",
        ),
    ]

    suggestions = coder._select_final_codes(candidates)
    assert [s.cpt for s in suggestions] == ["31653"]
