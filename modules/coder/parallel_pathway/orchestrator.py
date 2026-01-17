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
from modules.coder.parallel_pathway.reconciler import CodeReconciler, ReconciledCode

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
        reconciler: Optional[CodeReconciler] = None,
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
        self.reconciler = reconciler or CodeReconciler()

        logger.info(
            "ParallelPathwayOrchestrator initialized: NER=%s, ML=%s",
            "available" if self.ner_predictor.available else "unavailable",
            "available" if self.ml_predictor else "unavailable",
        )

    def process(
        self,
        note_text: str,
        ml_predictor: Optional[Any] = None,
    ) -> ParallelPathwayResult:
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
        path_b_result = self._run_path_b(note_text, ml_predictor=ml_predictor)

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

    def run_parallel_process(
        self,
        note_text: str,
        ml_predictor: Optional[Any] = None,
    ):
        """Run parallel NER + ML reconciliation and return a RegistryExtractionResult."""
        path_a_result = self._run_path_a(note_text)
        record = path_a_result.details.get("record")

        if record is None:
            from modules.registry.schema import RegistryRecord

            record = RegistryRecord()

        ml_probabilities = self._predict_ml_probabilities(note_text, ml_predictor=ml_predictor)
        ml_candidates = {code for code, prob in ml_probabilities.items() if prob > 0.5}
        all_codes = sorted(set(path_a_result.codes) | ml_candidates)

        audit_warnings: list[str] = []
        finalized_codes: list[str] = []
        needs_manual_review = False

        for code in all_codes:
            ner_code = code if code in path_a_result.codes else None
            reconciled = self.reconciler.reconcile(ner_code, ml_probabilities.get(code, 0.0))
            if not reconciled.code:
                reconciled = ReconciledCode(
                    code=code,
                    status=reconciled.status,
                    review_required=reconciled.review_required,
                    message=reconciled.message,
                )

            if reconciled.status == "FINALIZED":
                finalized_codes.append(reconciled.code)
            if reconciled.review_required:
                needs_manual_review = True
                if reconciled.message:
                    audit_warnings.append(f"{reconciled.code}: {reconciled.message}")

        from modules.registry.application.cpt_registry_mapping import aggregate_registry_fields
        from modules.registry.application.registry_service import RegistryExtractionResult

        mapped_fields = (
            aggregate_registry_fields(finalized_codes, version="v3")
            if finalized_codes
            else {}
        )

        warnings = list(path_a_result.details.get("mapping_warnings", []))
        derivation_warnings = list(path_a_result.details.get("rules_warnings", []))

        return RegistryExtractionResult(
            record=record,
            cpt_codes=sorted(finalized_codes),
            coder_difficulty="unknown",
            coder_source="parallel_ner",
            mapped_fields=mapped_fields,
            code_rationales=path_a_result.rationales,
            derivation_warnings=derivation_warnings,
            warnings=warnings,
            needs_manual_review=needs_manual_review,
            audit_warnings=audit_warnings,
        )

    def _ensure_ml_predictor(self) -> Any | None:
        if self.ml_predictor is not None:
            return self.ml_predictor
        try:
            from modules.ml_coder.registry_predictor import RegistryMLPredictor

            predictor = RegistryMLPredictor()
            if predictor.available:
                self.ml_predictor = predictor
                return predictor
        except Exception as exc:
            logger.debug("RegistryMLPredictor unavailable: %s", exc)
        return None

    def _predict_ml_probabilities(
        self,
        note_text: str,
        ml_predictor: Optional[Any] = None,
    ) -> Dict[str, float]:
        predictor = ml_predictor or self._ensure_ml_predictor()
        if predictor is None:
            return {}
        if hasattr(predictor, "available") and not predictor.available:
            return {}
        if not hasattr(predictor, "predict_proba"):
            return {}

        try:
            preds = predictor.predict_proba(note_text)
        except Exception as exc:
            logger.debug("ML probability prediction failed: %s", exc)
            return {}

        from modules.registry.audit.raw_ml_auditor import FLAG_TO_CPT_MAP

        ml_probabilities: Dict[str, float] = {}
        for pred in preds:
            if isinstance(pred, dict):
                field = pred.get("field") or pred.get("flag_name")
                prob = pred.get("probability") or pred.get("prob")
            else:
                field = getattr(pred, "field", None) or getattr(pred, "flag_name", None)
                prob = getattr(pred, "probability", None)
            if field is None or prob is None:
                continue
            for code in FLAG_TO_CPT_MAP.get(str(field), []):
                ml_probabilities[code] = max(ml_probabilities.get(code, 0.0), float(prob))

        return ml_probabilities

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

    def _run_path_b(
        self,
        note_text: str,
        ml_predictor: Optional[Any] = None,
    ) -> PathwayResult:
        """Run Path B: ML Classification."""
        start_time = time.time()

        codes: List[str] = []
        confidences: Dict[str, float] = {}
        rationales: Dict[str, str] = {}
        details: Dict[str, Any] = {}

        predictor = ml_predictor or self.ml_predictor
        try:
            if predictor and predictor.available:
                # Run ML prediction
                result = predictor.predict(note_text)

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

    async def process_async(
        self,
        note_text: str,
        ml_predictor: Optional[Any] = None,
    ) -> ParallelPathwayResult:
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
        path_b_task = loop.run_in_executor(None, self._run_path_b, note_text, ml_predictor)

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
