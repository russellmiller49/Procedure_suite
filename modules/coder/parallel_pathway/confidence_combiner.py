"""Confidence combination for parallel pathway results.

Combines deterministic (NER+Rules) and probabilistic (ML Classification)
signals into final confidence scores with agreement analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ConfidenceFactors:
    """Factors that contribute to final code confidence."""

    deterministic_found: bool
    """Path A (NER+Rules) derived this code."""

    ml_probability: float
    """Path B (ML Classification) probability (0-1)."""

    entity_confidence: float
    """Average NER confidence for supporting entities."""

    agreement: bool
    """Both paths agree on this code."""


@dataclass
class CodeConfidence:
    """Final confidence and explanation for a code."""

    code: str
    confidence: float
    explanation: str
    needs_review: bool
    review_reason: str | None


class ConfidenceCombiner:
    """Combine deterministic and probabilistic confidence scores.

    Strategy:
    - Agreement between paths: high confidence
    - Path A found, Path B missed: medium confidence, flag if ML prob was low
    - Path B found, Path A missed: flag for review (NER may have missed evidence)
    """

    # Weights for confidence combination
    DETERMINISTIC_WEIGHT = 0.6
    ML_WEIGHT = 0.3
    ENTITY_WEIGHT = 0.1

    # Bonuses/penalties
    AGREEMENT_BONUS = 0.10
    DISAGREEMENT_PENALTY = 0.15

    # Thresholds for review flagging
    ML_HIGH_CONF_THRESHOLD = 0.8
    ML_LOW_CONF_THRESHOLD = 0.5

    def combine(
        self,
        code: str,
        deterministic_found: bool,
        ml_probability: float,
        entity_confidence: float = 0.5,
    ) -> CodeConfidence:
        """
        Calculate final confidence for a code.

        Args:
            code: The CPT code
            deterministic_found: Whether Path A derived this code
            ml_probability: Path B probability for this code
            entity_confidence: Average confidence of NER entities (default 0.5)

        Returns:
            CodeConfidence with score, explanation, and review flags
        """
        agreement = deterministic_found and ml_probability >= self.ML_LOW_CONF_THRESHOLD

        if deterministic_found and agreement:
            # Best case: both paths agree
            base = (
                self.DETERMINISTIC_WEIGHT * 1.0 +
                self.ML_WEIGHT * ml_probability +
                self.ENTITY_WEIGHT * entity_confidence
            )
            confidence = min(0.99, base + self.AGREEMENT_BONUS)
            explanation = (
                f"Both pathways agree (NER+Rules: found, ML: {ml_probability:.2f})"
            )
            needs_review = False
            review_reason = None

        elif deterministic_found and not agreement:
            # Path A found, Path B missed or low confidence
            base = (
                self.DETERMINISTIC_WEIGHT * 1.0 +
                self.ML_WEIGHT * ml_probability +
                self.ENTITY_WEIGHT * entity_confidence
            )
            confidence = max(0.50, base - self.DISAGREEMENT_PENALTY)

            if ml_probability < 0.3:
                explanation = (
                    f"NER+Rules derived code but ML had low confidence "
                    f"(ML prob: {ml_probability:.2f}) - verify NER entities"
                )
                needs_review = True
                review_reason = f"Path A/B disagreement: ML prob={ml_probability:.2f}"
            else:
                explanation = (
                    f"NER+Rules derived code, ML moderately confident "
                    f"(ML prob: {ml_probability:.2f})"
                )
                needs_review = False
                review_reason = None

        elif not deterministic_found and ml_probability >= self.ML_HIGH_CONF_THRESHOLD:
            # Path B found with high confidence, Path A missed
            confidence = ml_probability * 0.7  # Penalize for missing deterministic
            explanation = (
                f"ML predicted with high confidence ({ml_probability:.2f}) "
                f"but NER+Rules did not derive - NER may have missed evidence"
            )
            needs_review = True
            review_reason = f"ML confident ({ml_probability:.2f}) but NER missed"

        elif not deterministic_found and ml_probability >= self.ML_LOW_CONF_THRESHOLD:
            # Path B found with moderate confidence, Path A missed
            confidence = ml_probability * 0.5
            explanation = (
                f"ML predicted with moderate confidence ({ml_probability:.2f}) "
                f"but NER+Rules did not derive"
            )
            needs_review = True
            review_reason = f"ML moderate ({ml_probability:.2f}), NER missed"

        else:
            # Neither path confident
            confidence = max(ml_probability * 0.3, 0.10)
            explanation = "Low confidence from both pathways"
            needs_review = ml_probability > 0.3
            review_reason = "Low confidence overall" if needs_review else None

        return CodeConfidence(
            code=code,
            confidence=confidence,
            explanation=explanation,
            needs_review=needs_review,
            review_reason=review_reason,
        )

    def combine_all(
        self,
        path_a_codes: List[str],
        path_b_probabilities: Dict[str, float],
        entity_confidences: Dict[str, float] | None = None,
    ) -> Tuple[List[CodeConfidence], List[str]]:
        """
        Combine results for all codes from both pathways.

        Args:
            path_a_codes: Codes derived by NER+Rules
            path_b_probabilities: Code -> probability from ML classification
            entity_confidences: Code -> average NER entity confidence

        Returns:
            (list of CodeConfidence, list of review reasons)
        """
        if entity_confidences is None:
            entity_confidences = {}

        # Get all unique codes
        all_codes = set(path_a_codes) | set(path_b_probabilities.keys())

        results: List[CodeConfidence] = []
        review_reasons: List[str] = []

        for code in sorted(all_codes):
            deterministic_found = code in path_a_codes
            ml_prob = path_b_probabilities.get(code, 0.0)
            entity_conf = entity_confidences.get(code, 0.5)

            code_conf = self.combine(
                code=code,
                deterministic_found=deterministic_found,
                ml_probability=ml_prob,
                entity_confidence=entity_conf,
            )

            results.append(code_conf)

            if code_conf.needs_review and code_conf.review_reason:
                review_reasons.append(f"{code}: {code_conf.review_reason}")

        # Sort by confidence (highest first)
        results.sort(key=lambda c: c.confidence, reverse=True)

        return results, review_reasons
