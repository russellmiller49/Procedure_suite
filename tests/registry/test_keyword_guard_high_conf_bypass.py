from __future__ import annotations

from app.registry.self_correction.keyword_guard import keyword_guard_check


def test_keyword_guard_allows_high_conf_bypass_for_blvr_codes() -> None:
    ok, reason = keyword_guard_check(cpt="31647", evidence_text="(masked)", ml_prob=0.95)
    assert ok is True
    assert "bypass" in reason.lower()


def test_keyword_guard_does_not_bypass_below_threshold() -> None:
    ok, reason = keyword_guard_check(cpt="31647", evidence_text="(masked)", ml_prob=0.89)
    assert ok is False
    assert "keyword" in reason.lower()

