from __future__ import annotations

from modules.coder.parallel_pathway.confidence_combiner import ConfidenceCombiner


def test_confidence_combiner_does_not_flag_low_ml_prob_for_low_risk_code() -> None:
    combiner = ConfidenceCombiner()
    cc = combiner.combine(code="31630", deterministic_found=True, ml_probability=0.0, entity_confidence=0.9)
    assert cc.needs_review is False
    assert cc.review_reason is None
    assert cc.confidence >= combiner.AUTO_CODE_CONFIDENCE


def test_confidence_combiner_flags_low_ml_prob_for_history_prone_code() -> None:
    combiner = ConfidenceCombiner()
    cc = combiner.combine(code="32551", deterministic_found=True, ml_probability=0.0, entity_confidence=0.9)
    assert cc.needs_review is True
    assert cc.review_reason is not None
    assert "very low" in cc.review_reason.lower()

