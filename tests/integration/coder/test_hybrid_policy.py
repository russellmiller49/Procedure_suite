"""Integration tests for the HybridPolicy.

Tests the smart hybrid merge logic that combines rule-based
and LLM advisor codes with confidence-based decisions.
"""

import pytest
from dataclasses import dataclass, field
from typing import Optional

from app.coder.application.smart_hybrid_policy import (
    HybridPolicy,
    HybridDecision,
    RuleResult,
    AdvisorResult,
)
from config.settings import CoderSettings


# ============================================================================
# Mock implementations for testing
# ============================================================================


@dataclass
class MockProcedureInfo:
    """Mock procedure info for testing."""

    code: str
    description: str = ""


class MockKnowledgeBaseRepository:
    """Mock KB repo with a fixed set of valid CPT codes."""

    def __init__(self, valid_codes: set[str] | None = None):
        self._valid_codes = valid_codes or {
            "31622",  # Bronchoscopy with BAL
            "31623",  # Bronchoscopy with brushing
            "31624",  # Bronchoscopy with biopsy
            "31652",  # EBUS-TBNA
            "31653",  # EBUS-TBNA additional sites
            "99999",  # Invalid test code
        }
        self.version = "mock_kb_v1"

    def get_all_codes(self) -> list[str]:
        return list(self._valid_codes)

    def get_procedure_info(self, code: str) -> Optional[MockProcedureInfo]:
        if code in self._valid_codes:
            return MockProcedureInfo(code=code, description=f"Description for {code}")
        return None


@dataclass
class MockKeywordMapping:
    """Mock keyword mapping for a CPT code."""

    code: str
    positive_phrases: list[str] = field(default_factory=list)
    negative_phrases: list[str] = field(default_factory=list)
    context_window_chars: int = 200


class MockKeywordMappingRepository:
    """Mock keyword mapping repository."""

    def __init__(self):
        self.version = "mock_keyword_v1"
        self._mappings = {
            "31622": MockKeywordMapping(
                code="31622",
                positive_phrases=["bronchoalveolar lavage", "bal", "wash"],
                negative_phrases=["no bal", "without lavage"],
            ),
            "31624": MockKeywordMapping(
                code="31624",
                positive_phrases=["biopsy", "transbronchial biopsy", "tblb"],
                negative_phrases=["no biopsy", "without biopsy"],
            ),
            "31652": MockKeywordMapping(
                code="31652",
                positive_phrases=["ebus", "endobronchial ultrasound", "tbna"],
                negative_phrases=["no ebus", "without ebus"],
            ),
        }

    def get_mapping(self, code: str) -> Optional[MockKeywordMapping]:
        return self._mappings.get(code)


class MockNegationDetector:
    """Mock negation detector."""

    def __init__(self):
        self.version = "mock_negation_v1"

    def is_negated_simple(self, context: str, negative_phrases: list[str]) -> bool:
        context_lower = context.lower()
        for neg in negative_phrases:
            if neg.lower() in context_lower:
                return True
        return False


# ============================================================================
# Test fixtures
# ============================================================================


@pytest.fixture
def kb_repo() -> MockKnowledgeBaseRepository:
    return MockKnowledgeBaseRepository()


@pytest.fixture
def keyword_repo() -> MockKeywordMappingRepository:
    return MockKeywordMappingRepository()


@pytest.fixture
def negation_detector() -> MockNegationDetector:
    return MockNegationDetector()


@pytest.fixture
def config() -> CoderSettings:
    return CoderSettings(
        advisor_confidence_auto_accept=0.85,
        rule_confidence_low_threshold=0.6,
        context_window_chars=200,
    )


@pytest.fixture
def hybrid_policy(
    kb_repo: MockKnowledgeBaseRepository,
    keyword_repo: MockKeywordMappingRepository,
    negation_detector: MockNegationDetector,
    config: CoderSettings,
) -> HybridPolicy:
    return HybridPolicy(
        kb_repo=kb_repo,
        keyword_repo=keyword_repo,
        negation_detector=negation_detector,
        config=config,
    )


# ============================================================================
# Tests: Agreement (rule ∩ advisor)
# ============================================================================


class TestHybridPolicyAgreement:
    """Tests for when rule-based and LLM advisor agree."""

    def test_agreement_both_suggest_same_code(
        self, hybrid_policy: HybridPolicy
    ) -> None:
        """Both engines suggest the same code → ACCEPTED_AGREEMENT."""
        rule_result = RuleResult(codes=["31622"], confidence={"31622": 0.9})
        advisor_result = AdvisorResult(codes=["31622"], confidence={"31622": 0.95})

        candidates = hybrid_policy.merge(
            rule_result, advisor_result, "Patient underwent BAL."
        )

        assert len(candidates) == 1
        assert candidates[0].code == "31622"
        assert candidates[0].decision == HybridDecision.ACCEPTED_AGREEMENT
        assert candidates[0].evidence_verified is True

    def test_agreement_multiple_codes(self, hybrid_policy: HybridPolicy) -> None:
        """Both engines agree on multiple codes."""
        rule_result = RuleResult(
            codes=["31622", "31624"],
            confidence={"31622": 0.9, "31624": 0.85},
        )
        advisor_result = AdvisorResult(
            codes=["31622", "31624"],
            confidence={"31622": 0.95, "31624": 0.9},
        )

        candidates = hybrid_policy.merge(
            rule_result,
            advisor_result,
            "BAL performed. Transbronchial biopsy obtained.",
        )

        assert len(candidates) == 2
        for c in candidates:
            assert c.decision == HybridDecision.ACCEPTED_AGREEMENT


# ============================================================================
# Tests: LLM additions (advisor-only codes)
# ============================================================================


class TestHybridPolicyAdvisorAdditions:
    """Tests for codes suggested only by the LLM advisor."""

    def test_advisor_addition_high_conf_verified(
        self, hybrid_policy: HybridPolicy
    ) -> None:
        """High-conf advisor suggestion with keyword verification → ACCEPTED_HYBRID."""
        rule_result = RuleResult(codes=[], confidence={})
        advisor_result = AdvisorResult(codes=["31652"], confidence={"31652": 0.92})

        # Text contains EBUS keyword
        report_text = "EBUS-TBNA was performed at station 4R."

        candidates = hybrid_policy.merge(rule_result, advisor_result, report_text)

        assert len(candidates) == 1
        assert candidates[0].code == "31652"
        assert candidates[0].decision == HybridDecision.ACCEPTED_HYBRID
        assert candidates[0].evidence_verified is True
        assert len(candidates[0].trigger_phrases) > 0

    def test_advisor_addition_high_conf_not_verified(
        self, hybrid_policy: HybridPolicy
    ) -> None:
        """High-conf advisor suggestion without keyword → HUMAN_REVIEW_REQUIRED."""
        rule_result = RuleResult(codes=[], confidence={})
        advisor_result = AdvisorResult(codes=["31652"], confidence={"31652": 0.90})

        # Text does NOT contain EBUS keyword
        report_text = "Normal bronchoscopy performed."

        candidates = hybrid_policy.merge(rule_result, advisor_result, report_text)

        assert len(candidates) == 1
        assert candidates[0].code == "31652"
        assert candidates[0].decision == HybridDecision.HUMAN_REVIEW_REQUIRED

    def test_advisor_addition_low_conf_rejected(
        self, hybrid_policy: HybridPolicy
    ) -> None:
        """Low-conf advisor suggestion → REJECTED_HYBRID."""
        rule_result = RuleResult(codes=[], confidence={})
        advisor_result = AdvisorResult(
            codes=["31652"], confidence={"31652": 0.60}  # Below threshold
        )

        candidates = hybrid_policy.merge(
            rule_result, advisor_result, "EBUS performed at 4R."
        )

        assert len(candidates) == 1
        assert candidates[0].code == "31652"
        assert candidates[0].decision == HybridDecision.REJECTED_HYBRID

    def test_advisor_suggests_invalid_code(self, hybrid_policy: HybridPolicy) -> None:
        """Advisor suggests a code not in the KB → REJECTED_HYBRID."""
        rule_result = RuleResult(codes=[], confidence={})
        # 12345 is not in valid_cpt_set
        advisor_result = AdvisorResult(codes=["12345"], confidence={"12345": 0.99})

        candidates = hybrid_policy.merge(rule_result, advisor_result, "Some text.")

        assert len(candidates) == 1
        assert candidates[0].code == "12345"
        assert candidates[0].decision == HybridDecision.REJECTED_HYBRID
        assert "DISCARDED_INVALID_CODE" in candidates[0].flags[0]


# ============================================================================
# Tests: Rule-only codes (omissions from LLM)
# ============================================================================


class TestHybridPolicyRuleOnly:
    """Tests for codes suggested only by the rule engine."""

    def test_rule_only_high_conf_kept(self, hybrid_policy: HybridPolicy) -> None:
        """High-conf rule code not suggested by advisor → KEPT_RULE_PRIORITY."""
        rule_result = RuleResult(codes=["31622"], confidence={"31622": 0.85})
        advisor_result = AdvisorResult(codes=[], confidence={})

        candidates = hybrid_policy.merge(
            rule_result, advisor_result, "BAL was performed."
        )

        assert len(candidates) == 1
        assert candidates[0].code == "31622"
        assert candidates[0].decision == HybridDecision.KEPT_RULE_PRIORITY
        assert candidates[0].evidence_verified is True

    def test_rule_only_low_conf_dropped(self, hybrid_policy: HybridPolicy) -> None:
        """Low-conf rule code not suggested by advisor → DROPPED_LOW_CONFIDENCE."""
        rule_result = RuleResult(
            codes=["31622"], confidence={"31622": 0.40}  # Below threshold
        )
        advisor_result = AdvisorResult(codes=[], confidence={})

        candidates = hybrid_policy.merge(rule_result, advisor_result, "Some text.")

        assert len(candidates) == 1
        assert candidates[0].code == "31622"
        assert candidates[0].decision == HybridDecision.DROPPED_LOW_CONFIDENCE


# ============================================================================
# Tests: Negation detection
# ============================================================================


class TestHybridPolicyNegation:
    """Tests for negation detection in keyword verification."""

    def test_negated_keyword_not_verified(self, hybrid_policy: HybridPolicy) -> None:
        """Keyword found but negated → verification fails."""
        rule_result = RuleResult(codes=[], confidence={})
        advisor_result = AdvisorResult(codes=["31622"], confidence={"31622": 0.92})

        # Contains "bal" but also "no bal"
        report_text = "No BAL was performed during this procedure."

        candidates = hybrid_policy.merge(rule_result, advisor_result, report_text)

        # Should require human review since keyword is negated
        assert len(candidates) == 1
        assert candidates[0].decision == HybridDecision.HUMAN_REVIEW_REQUIRED


# ============================================================================
# Tests: Policy modes
# ============================================================================


class TestHybridPolicyModes:
    """Tests for different policy modes."""

    def test_rules_only_mode(self, hybrid_policy: HybridPolicy) -> None:
        """rules_only mode ignores advisor."""
        rule_result = RuleResult(
            codes=["31622", "31624"],
            confidence={"31622": 0.9, "31624": 0.8},
        )
        advisor_result = AdvisorResult(
            codes=["31652"],  # Different codes
            confidence={"31652": 0.99},
        )

        candidates = hybrid_policy.merge(
            rule_result, advisor_result, "Some text.", policy="rules_only"
        )

        # Only rule codes should be present
        codes = {c.code for c in candidates}
        assert codes == {"31622", "31624"}
        assert all(c.decision == HybridDecision.KEPT_RULE_PRIORITY for c in candidates)

    def test_unknown_policy_raises(self, hybrid_policy: HybridPolicy) -> None:
        """Unknown policy raises ValueError."""
        rule_result = RuleResult(codes=[], confidence={})
        advisor_result = AdvisorResult(codes=[], confidence={})

        with pytest.raises(ValueError, match="Unknown policy"):
            hybrid_policy.merge(
                rule_result, advisor_result, "text", policy="unknown_policy"
            )


# ============================================================================
# Tests: Helper methods
# ============================================================================


class TestHybridPolicyHelpers:
    """Tests for helper methods."""

    def test_get_accepted_codes(self, hybrid_policy: HybridPolicy) -> None:
        """get_accepted_codes returns only accepted codes."""
        rule_result = RuleResult(
            codes=["31622", "31624"],
            confidence={"31622": 0.9, "31624": 0.4},  # 31624 is low conf
        )
        advisor_result = AdvisorResult(codes=["31622"], confidence={"31622": 0.9})

        candidates = hybrid_policy.merge(rule_result, advisor_result, "BAL performed.")

        accepted = hybrid_policy.get_accepted_codes(candidates)

        # 31622 should be accepted (agreement)
        # 31624 should be dropped (low conf + advisor omit)
        assert "31622" in accepted
        assert "31624" not in accepted

    def test_get_review_required_codes(self, hybrid_policy: HybridPolicy) -> None:
        """get_review_required_codes returns codes needing review."""
        rule_result = RuleResult(codes=[], confidence={})
        advisor_result = AdvisorResult(codes=["31652"], confidence={"31652": 0.90})

        # No EBUS keyword → needs review
        candidates = hybrid_policy.merge(
            rule_result, advisor_result, "Normal bronchoscopy."
        )

        review_needed = hybrid_policy.get_review_required_codes(candidates)

        assert "31652" in review_needed
