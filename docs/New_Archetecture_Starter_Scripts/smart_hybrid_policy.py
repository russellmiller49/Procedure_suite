# modules/coder/application/smart_hybrid_policy.py

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from config.settings import CoderSettings
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from modules.coder.adapters.nlp.keyword_mapping_loader import KeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import NegationDetectionPort


class HybridDecision(str, Enum):
    ACCEPTED_AGREEMENT = "accepted_agreement"        # rule ∩ advisor
    ACCEPTED_HYBRID = "accepted_hybrid"              # advisor-only, verified
    KEPT_RULE_PRIORITY = "kept_rule_priority"        # rule-only, high confidence
    REJECTED_HYBRID = "rejected_hybrid"              # advisor-only, failed verification
    DROPPED_LOW_CONFIDENCE = "dropped_low_conf"      # rule-only, low conf + advisor omit
    HUMAN_REVIEW_REQUIRED = "human_review"           # high conf but verification failed


@dataclass
class RuleResult:
    codes: List[str]
    confidence: Dict[str, float]


@dataclass
class AdvisorResult:
    codes: List[str]
    confidence: Dict[str, float]


@dataclass
class HybridCandidate:
    code: str
    decision: HybridDecision
    rule_confidence: Optional[float]
    llm_confidence: Optional[float]
    flags: List[str]


class HybridPolicy:
    """
    Smart hybrid policy that merges rule-based and LLM advisor codes.

    This is effectively the merge_autocode_and_advisor() logic from your prototype,
    adapted to use:
      - KnowledgeBaseRepository for VALID_CPT_LIST
      - KeywordMappingRepository for positive/negative phrases + context window
      - NegationDetectionPort (hook for future negation models)
      - Thresholds from CoderSettings
    """

    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        keyword_repo: KeywordMappingRepository,
        negation_detector: NegationDetectionPort,
        config: CoderSettings,
    ) -> None:
        self.kb_repo = kb_repo
        self.keyword_repo = keyword_repo
        self.negation_detector = negation_detector
        self.config = config

        # Defensive filter to block hallucinated codes
        self.valid_cpt_set: Set[str] = set(kb_repo.get_all_codes())

    # ---- Public API -----------------------------------------------------

    def merge(
        self,
        rule_result: RuleResult,
        advisor_result: AdvisorResult,
        report_text: str,
        policy: str = "smart_hybrid",
    ) -> List[HybridCandidate]:
        if policy == "rules_only":
            return [
                HybridCandidate(
                    code=c,
                    decision=HybridDecision.KEPT_RULE_PRIORITY,
                    rule_confidence=rule_result.confidence.get(c, 1.0),
                    llm_confidence=None,
                    flags=["rules_only_mode"],
                )
                for c in sorted(set(rule_result.codes))
            ]

        if policy != "smart_hybrid":
            raise ValueError(
                f"Unknown policy: {policy}. Use 'rules_only' or 'smart_hybrid'."
            )

        rule_codes = list(rule_result.codes)
        rule_conf = dict(rule_result.confidence)
        advisor_codes = list(advisor_result.codes)
        advisor_conf = dict(advisor_result.confidence)

        candidates: Dict[str, HybridCandidate] = {}
        rule_set = set(rule_codes)
        advisor_set = set(advisor_codes)

        # 1. Agreement (rule ∩ advisor)
        agreement = rule_set.intersection(advisor_set)
        for code in agreement:
            candidates[code] = HybridCandidate(
                code=code,
                decision=HybridDecision.ACCEPTED_AGREEMENT,
                rule_confidence=rule_conf.get(code),
                llm_confidence=advisor_conf.get(code),
                flags=["rules_and_advisor_agree"],
            )

        # 2. LLM additions (advisor-only codes)
        additions = advisor_set - rule_set
        for code in additions:
            llm_conf = advisor_conf.get(code, 0.0)

            # 2A. Validate CPT code
            if code not in self.valid_cpt_set:
                candidates[code] = HybridCandidate(
                    code=code,
                    decision=HybridDecision.REJECTED_HYBRID,
                    rule_confidence=None,
                    llm_confidence=llm_conf,
                    flags=[
                        f"DISCARDED_INVALID_CODE: Advisor suggested invalid CPT {code}"
                    ],
                )
                continue

            # 2B. Confidence + verification
            if llm_conf >= self.config.advisor_confidence_auto_accept:
                verified = self._verify_code_in_text(code, report_text)
                if verified:
                    candidates[code] = HybridCandidate(
                        code=code,
                        decision=HybridDecision.ACCEPTED_HYBRID,
                        rule_confidence=None,
                        llm_confidence=llm_conf,
                        flags=[
                            f"ACCEPTED_HYBRID: advisor_conf={llm_conf:.2f}, "
                            "verified_by_keywords"
                        ],
                    )
                else:
                    candidates[code] = HybridCandidate(
                        code=code,
                        decision=HybridDecision.HUMAN_REVIEW_REQUIRED,
                        rule_confidence=None,
                        llm_confidence=llm_conf,
                        flags=[
                            "HUMAN_REVIEW_REQUIRED: high_conf_advisor_but_verification_failed"
                        ],
                    )
            else:
                candidates[code] = HybridCandidate(
                    code=code,
                    decision=HybridDecision.REJECTED_HYBRID,
                    rule_confidence=None,
                    llm_confidence=llm_conf,
                    flags=[
                        f"REJECTED_LOW_CONF_ADVISOR: llm_conf={llm_conf:.2f} "
                        "below_auto_accept"
                    ],
                )

        # 3. Rule-only codes (omissions from LLM)
        omissions = rule_set - advisor_set
        for code in omissions:
            rule_c = rule_conf.get(code, 0.0)

            if rule_c >= self.config.rule_confidence_low_threshold:
                # Trust rules when confidence is acceptable
                candidates[code] = HybridCandidate(
                    code=code,
                    decision=HybridDecision.KEPT_RULE_PRIORITY,
                    rule_confidence=rule_c,
                    llm_confidence=None,
                    flags=[
                        f"KEPT_RULE_PRIORITY: rule_conf={rule_c:.2f}, "
                        "advisor_omitted_code"
                    ],
                )
            else:
                # Low confidence rule that advisor also omitted → drop
                candidates[code] = HybridCandidate(
                    code=code,
                    decision=HybridDecision.DROPPED_LOW_CONFIDENCE,
                    rule_confidence=rule_c,
                    llm_confidence=None,
                    flags=[
                        f"DROPPED_LOW_CONF: rule_conf={rule_c:.2f}, "
                        "advisor_omitted_code"
                    ],
                )

        # Return in sorted code order for determinism
        return [candidates[c] for c in sorted(candidates.keys())]

    # ---- Internal helpers -----------------------------------------------

    def _verify_code_in_text(self, code: str, report_text: str) -> bool:
        """
        Verify that a CPT code is actually supported by the text, using
        YAML-backed positive/negative phrases and a context window.

        This is the generalized version of your verify_code_in_text().
        """
        mapping = self.keyword_repo.get_mapping(code)
        if not mapping:
            # Fail-safe: if we don't know how to verify, return False (no auto-accept)
            return False

        positive_phrases = mapping.positive_phrases
        negative_phrases = mapping.negative_phrases
        context_window = (
            mapping.context_window_chars or self.config.context_window_chars
        )

        text_lower = report_text.lower()

        for pos in positive_phrases:
            # Find all occurrences of the positive phrase
            pattern = r"\b" + re.escape(pos.lower()) + r"\b"
            for match in re.finditer(pattern, text_lower):
                start_idx = max(0, match.start() - context_window)
                end_idx = min(len(text_lower), match.end() + context_window)
                context = text_lower[start_idx:end_idx]

                # Use negation detector to see if this span is negated / future / planned
                if self.negation_detector.is_negated(context, negative_phrases):
                    continue

                # Found at least one non-negated positive phrase
                return True

        return False
