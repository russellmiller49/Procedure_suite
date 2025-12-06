"""Tests for hierarchy normalization in CodingRulesEngine."""

from __future__ import annotations

from modules.coder.code_families import load_code_families
from modules.coder.rules_engine import CodingRulesEngine
from modules.coder.types import CodeCandidate


def _engine() -> CodingRulesEngine:
    return CodingRulesEngine(families_cfg=load_code_families())


def test_tracheal_and_bronchial_stent_triggers_conversion():
    engine = _engine()
    candidates = [
        CodeCandidate(code="31631", confidence=0.9),
        CodeCandidate(code="31636", confidence=0.8),
    ]

    out = engine.apply(candidates, note_text="stent note")
    codes = [c.code for c in out]

    assert "31631" in codes
    assert "31637" in codes
    assert "31636" not in codes


def test_bronchial_stent_without_tracheal_is_not_converted():
    engine = _engine()
    candidates = [CodeCandidate(code="31636", confidence=0.7)]

    out = engine.apply(candidates, note_text="stent note")

    assert [c.code for c in out] == ["31636"]


def test_existing_additional_bronchial_stent_not_duplicated():
    engine = _engine()
    candidates = [
        CodeCandidate(code="31631", confidence=0.9),
        CodeCandidate(code="31636", confidence=0.8),
        CodeCandidate(code="31637", confidence=0.7),
    ]

    out = engine.apply(candidates, note_text="stent note")
    codes = [c.code for c in out]

    assert codes.count("31631") == 1
    assert codes.count("31637") == 1
    assert "31636" not in codes
