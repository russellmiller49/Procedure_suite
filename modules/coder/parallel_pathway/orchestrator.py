"""Parallel pathway orchestrator for CPT coding.

Runs both Path A (NER+Rules) and Path B (ML Classification) and combines
results with reconciliation and review flagging.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from modules.common.logger import get_logger
from modules.ner import GranularNERPredictor, NERExtractionResult
from modules.registry.ner_mapping import NERToRegistryMapper, RegistryMappingResult
from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.coder.parallel_pathway.confidence_combiner import (
    ConfidenceCombiner,
    CodeConfidence,
)

logger = get_logger("coder.parallel_pathway")


@dataclass
class PathwayResult:
    """Result from a single pathway (A or B)."""

    codes: List[str]
    """CPT codes derived/predicted."""

    confidences: Dict[str, float]
    """Code -> confidence score."""

    rationales: Dict[str, str]
    """Code -> explanation."""

    source: Literal["ner_rules", "ml_classification"]
    """Which pathway produced this result."""

    processing_time_ms: float
    """Time taken in milliseconds."""

    # Additional details
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelPathwayResult:
    """Combined result from parallel pathway execution."""

    # Final outputs
    final_codes: List[str]
    """Combined codes with confidence above threshold."""

    final_confidences: Dict[str, float]
    """Code -> final combined confidence."""

    # Per-pathway results
    path_a_result: PathwayResult
    """NER + Rules result."""

    path_b_result: PathwayResult
    """ML Classification result."""

    # Confidence details
    code_confidences: List[CodeConfidence]
    """Detailed confidence for each code."""

    # Review flags
    needs_review: bool
    """True if any code needs human review."""

    review_reasons: List[str]
    """Reasons why review is needed."""

    # Explanations
    explanations: Dict[str, str]
    """Human-readable per-code explanations."""

    # Timing
    total_time_ms: float
    """Total processing time."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "final_codes": self.final_codes,
            "final_confidences": self.final_confidences,
            "pathway_results": {
                "path_a": {
                    "source": self.path_a_result.source,
                    "codes": self.path_a_result.codes,
                    "confidences": self.path_a_result.confidences,
                    "rationales": self.path_a_result.rationales,
                    "time_ms": self.path_a_result.processing_time_ms,
                },
                "path_b": {
                    "source": self.path_b_result.source,
                    "codes": self.path_b_result.codes,
                    "confidences": self.path_b_result.confidences,
                    "time_ms": self.path_b_result.processing_time_ms,
                },
            },
            "needs_review": self.needs_review,
            "review_reasons": self.review_reasons,
            "explanations": self.explanations,
            "total_time_ms": self.total_time_ms,
        }


class ParallelPathwayOrchestrator:
    """Orchestrates parallel NER+Rules and ML Classification pathways.

    Architecture:
        Text -> [Path A] -> NER -> Registry -> Rules -> Codes
             -> [Path B] -> ML Classifier -> Probabilities
                        |
                        v
               [Reconciler/Combiner]
                        |
                        v
               Final Codes + Confidence + Review Flags
    """

    DEFAULT_CONFIDENCE_THRESHOLD = 0.5

    def __init__(
        self,
        ner_predictor: Optional[GranularNERPredictor] = None,
        ner_mapper: Optional[NERToRegistryMapper] = None,
        ml_predictor: Optional[Any] = None,  # TorchRegistryPredictor
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            ner_predictor: NER model for Path A (created if None)
            ner_mapper: NER-to-Registry mapper (created if None)
            ml_predictor: ML classifier for Path B (optional)
            confidence_threshold: Minimum confidence to include code
        """
        self.ner_predictor = ner_predictor or GranularNERPredictor(
            confidence_threshold=0.1  # Lower threshold for NER
        )
        self.ner_mapper = ner_mapper or NERToRegistryMapper()
        self.ml_predictor = ml_predictor
        self.confidence_threshold = confidence_threshold
        self.confidence_combiner = ConfidenceCombiner()

        logger.info(
            "ParallelPathwayOrchestrator initialized: NER=%s, ML=%s",
            "available" if self.ner_predictor.available else "unavailable",
            "available" if self.ml_predictor else "unavailable",
        )

    def process(self, note_text: str) -> ParallelPathwayResult:
        """
        Run both pathways and combine results.

        Args:
            note_text: The procedure note text

        Returns:
            ParallelPathwayResult with combined codes and review flags
        """
        start_time = time.time()

        # Run Path A: NER -> Registry -> Rules
        path_a_result = self._run_path_a(note_text)

        # Run Path B: ML Classification
        path_b_result = self._run_path_b(note_text)

        # Combine results
        code_confidences, review_reasons = self.confidence_combiner.combine_all(
            path_a_codes=path_a_result.codes,
            path_b_probabilities=path_b_result.confidences,
        )

        # Filter by confidence threshold
        final_codes = [
            cc.code for cc in code_confidences
            if cc.confidence >= self.confidence_threshold
        ]

        final_confidences = {
            cc.code: cc.confidence for cc in code_confidences
            if cc.confidence >= self.confidence_threshold
        }

        # Build explanations
        explanations = {cc.code: cc.explanation for cc in code_confidences}

        # Determine if review is needed
        needs_review = any(cc.needs_review for cc in code_confidences)

        total_time = (time.time() - start_time) * 1000

        return ParallelPathwayResult(
            final_codes=final_codes,
            final_confidences=final_confidences,
            path_a_result=path_a_result,
            path_b_result=path_b_result,
            code_confidences=code_confidences,
            needs_review=needs_review,
            review_reasons=review_reasons,
            explanations=explanations,
            total_time_ms=total_time,
        )

    def _run_path_a(self, note_text: str) -> PathwayResult:
        """Run Path A: NER -> Registry -> Rules."""
        start_time = time.time()

        codes: List[str] = []
        confidences: Dict[str, float] = {}
        rationales: Dict[str, str] = {}
        details: Dict[str, Any] = {}

        try:
            # 1. Run NER
            ner_result = self.ner_predictor.predict(note_text)
            details["ner_entity_count"] = len(ner_result.entities)
            details["ner_time_ms"] = ner_result.inference_time_ms

            # 2. Map to Registry
            mapping_result = self.ner_mapper.map_entities(ner_result)
            record = mapping_result.record
            details["record"] = record  # Store for service integration
            details["mapping_result"] = mapping_result  # Full mapping result
            details["stations_sampled_count"] = mapping_result.stations_sampled_count
            details["mapping_warnings"] = mapping_result.warnings

            # 3. Run Rules
            codes_list, rules_rationales, rules_warnings = derive_all_codes_with_meta(record)
            codes = codes_list
            rationales = rules_rationales
            details["rules_warnings"] = rules_warnings

            # Set confidence based on entity confidence (simplified)
            for code in codes:
                # Higher confidence if we have strong NER evidence
                entity_conf = sum(e.confidence for e in ner_result.entities) / max(len(ner_result.entities), 1)
                confidences[code] = min(0.95, 0.5 + entity_conf * 0.5)

        except Exception as e:
            logger.warning("Path A failed: %s", e)
            details["error"] = str(e)

        processing_time = (time.time() - start_time) * 1000

        return PathwayResult(
            codes=codes,
            confidences=confidences,
            rationales=rationales,
            source="ner_rules",
            processing_time_ms=processing_time,
            details=details,
        )

    def _run_path_b(self, note_text: str) -> PathwayResult:
        """Run Path B: ML Classification."""
        start_time = time.time()

        codes: List[str] = []
        confidences: Dict[str, float] = {}
        rationales: Dict[str, str] = {}
        details: Dict[str, Any] = {}

        try:
            if self.ml_predictor and self.ml_predictor.available:
                # Run ML prediction
                result = self.ml_predictor.predict(note_text)

                # Convert predictions to codes using FLAG_TO_CPT_MAP
                from modules.registry.audit.raw_ml_auditor import FLAG_TO_CPT_MAP

                for pred in result.predictions:
                    if pred.is_positive:
                        field_name = pred.field
                        if field_name in FLAG_TO_CPT_MAP:
                            for cpt_code in FLAG_TO_CPT_MAP[field_name]:
                                codes.append(cpt_code)
                                confidences[cpt_code] = pred.probability
                                rationales[cpt_code] = f"ML predicted {field_name}={pred.probability:.2f}"

                details["ml_positive_fields"] = result.positive_fields
                details["ml_difficulty"] = result.difficulty
            else:
                details["ml_available"] = False

        except Exception as e:
            logger.warning("Path B failed: %s", e)
            details["error"] = str(e)

        processing_time = (time.time() - start_time) * 1000

        return PathwayResult(
            codes=codes,
            confidences=confidences,
            rationales=rationales,
            source="ml_classification",
            processing_time_ms=processing_time,
            details=details,
        )

    async def process_async(self, note_text: str) -> ParallelPathwayResult:
        """
        Async version that runs both pathways concurrently.

        Args:
            note_text: The procedure note text

        Returns:
            ParallelPathwayResult with combined codes and review flags
        """
        start_time = time.time()

        # Run both pathways concurrently
        loop = asyncio.get_event_loop()
        path_a_task = loop.run_in_executor(None, self._run_path_a, note_text)
        path_b_task = loop.run_in_executor(None, self._run_path_b, note_text)

        path_a_result, path_b_result = await asyncio.gather(path_a_task, path_b_task)

        # Combine results (same as sync version)
        code_confidences, review_reasons = self.confidence_combiner.combine_all(
            path_a_codes=path_a_result.codes,
            path_b_probabilities=path_b_result.confidences,
        )

        final_codes = [
            cc.code for cc in code_confidences
            if cc.confidence >= self.confidence_threshold
        ]

        final_confidences = {
            cc.code: cc.confidence for cc in code_confidences
            if cc.confidence >= self.confidence_threshold
        }

        explanations = {cc.code: cc.explanation for cc in code_confidences}
        needs_review = any(cc.needs_review for cc in code_confidences)

        total_time = (time.time() - start_time) * 1000

        return ParallelPathwayResult(
            final_codes=final_codes,
            final_confidences=final_confidences,
            path_a_result=path_a_result,
            path_b_result=path_b_result,
            code_confidences=code_confidences,
            needs_review=needs_review,
            review_reasons=review_reasons,
            explanations=explanations,
            total_time_ms=total_time,
        )
