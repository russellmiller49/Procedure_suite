"""Coding Service - orchestrates the 8-step coding pipeline.

This service coordinates rule-based coding, LLM advisor suggestions,
smart hybrid merge, evidence validation, NCCI/MER compliance, and
produces CodeSuggestion objects for review.

Supports two pipeline modes (controlled by PROCSUITE_PIPELINE_MODE env var):
- "current" (default): 8-step hybrid pipeline (Rules + LLM + ML)
- "extraction_first": Registry extraction → Deterministic CPT derivation → ML audit
"""

from __future__ import annotations

import os
import time
import uuid
from datetime import datetime
from typing import Optional

from config.settings import CoderSettings
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from modules.domain.coding_rules import apply_ncci_edits, apply_mer_rules
from modules.domain.coding_rules.rule_engine import RuleEngine
from modules.coder.adapters.nlp.keyword_mapping_loader import KeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.adapters.llm.gemini_advisor import LLMAdvisorPort
from modules.coder.adapters.ml_ranker import MLRankerPort, MLRankingResult
from modules.coder.application.smart_hybrid_policy import (
    HybridPolicy,
    HybridCandidate,
    HybridDecision,
    RuleResult,
    AdvisorResult,
)
from modules.coder.application.procedure_type_detector import detect_procedure_type
from modules.coder.domain_rules import (
    apply_addon_family_rules,
    apply_all_ncci_bundles,
)
from modules.coder.sectionizer import (
    accordion_truncate,
    sectionizer_enabled,
    max_llm_input_tokens,
)
from modules.phi.ports import PHIScrubberPort
from proc_schemas.coding import CodeSuggestion, CodingResult
from proc_schemas.reasoning import ReasoningFields
from observability.timing import timed
from observability.logging_config import get_logger

logger = get_logger("coding_service")


class CodingService:
    """Orchestrates the 8-step coding pipeline.

    Pipeline Steps:
    1. Rule engine → rule_codes + rule_confidence
    2. (Optional) ML ranker → ml_confidence
    3. LLM advisor → advisor_codes + advisor_confidence
    4. Smart hybrid merge → merged_codes with HybridDecision flags
    5. Evidence validation → verify each code in text
    6. Non-negotiable rules (NCCI/MER) → remove invalid combinations
    7. Confidence aggregation → compute final_confidence, set review_flag
    8. Build CodeSuggestion[] → return for review
    """

    VERSION = "coding_service_v1"

    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        keyword_repo: KeywordMappingRepository,
        negation_detector: SimpleNegationDetector,
        rule_engine: RuleEngine,
        llm_advisor: Optional[LLMAdvisorPort],
        config: CoderSettings,
        phi_scrubber: Optional[PHIScrubberPort] = None,
        ml_ranker: Optional[MLRankerPort] = None,
    ):
        self.kb_repo = kb_repo
        self.keyword_repo = keyword_repo
        self.negation_detector = negation_detector
        self.rule_engine = rule_engine
        self.llm_advisor = llm_advisor
        self.config = config
        self.phi_scrubber = phi_scrubber
        self.ml_ranker = ml_ranker

        # Initialize hybrid policy
        self.hybrid_policy = HybridPolicy(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            config=config,
        )

        # Note: PHI scrubbing is now handled at route level (modules/api/phi_redaction.py).
        # The phi_scrubber parameter is deprecated and ignored.
        if phi_scrubber:
            logger.debug(
                "phi_scrubber parameter is deprecated; PHI redaction is now handled at route level"
            )

        # Log ML ranker status
        if ml_ranker and ml_ranker.available:
            logger.info("ML ranker enabled: %s", ml_ranker.version)
        elif ml_ranker:
            logger.warning("ML ranker provided but not available (models not loaded)")

    def generate_suggestions(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
    ) -> tuple[list[CodeSuggestion], float]:
        """Generate code suggestions for a procedure note.

        Args:
            procedure_id: Unique identifier for the procedure.
            report_text: The procedure note text.
            use_llm: Whether to use the LLM advisor.

        Returns:
            Tuple of (List of CodeSuggestion objects, LLM latency in ms).
        """
        # Check pipeline mode
        pipeline_mode = os.getenv("PROCSUITE_PIPELINE_MODE", "current").strip().lower()

        if pipeline_mode == "extraction_first":
            return self._generate_suggestions_extraction_first(procedure_id, report_text)

        # Default: existing 8-step hybrid pipeline
        return self._generate_suggestions_hybrid(procedure_id, report_text, use_llm)

    def _generate_suggestions_hybrid(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
    ) -> tuple[list[CodeSuggestion], float]:
        """Hybrid pipeline: Rules + LLM + ML merge (original 8-step pipeline)."""
        llm_latency_ms = 0.0

        # Log input text size for debugging truncation issues
        text_length = len(report_text)
        logger.info(
            "Starting coding pipeline (hybrid mode)",
            extra={
                "procedure_id": procedure_id,
                "text_length_chars": text_length,
                "use_llm": use_llm,
            },
        )
        if text_length > 20000:
            logger.warning(
                f"Large procedure note detected ({text_length} chars). "
                "Potential for truncation in LLM processing.",
                extra={"procedure_id": procedure_id, "text_length_chars": text_length},
            )

        with timed("coding_service.generate_suggestions") as timing:
            # Step 1: Rule-based coding
            rule_result = self._run_rule_engine(report_text)

            # Step 2: Optional ML ranking
            ml_result = self._run_ml_ranker(report_text, rule_result)

            # Step 3: LLM advisor (track latency separately)
            advisor_result, llm_latency_ms = self._run_llm_advisor(report_text, use_llm)

            # Step 4: Smart hybrid merge
            candidates = self._run_hybrid_merge(rule_result, advisor_result, report_text)

            # Step 5: Evidence validation is done in hybrid merge

            # Step 6: NCCI/MER compliance
            candidates, ncci_warnings, mer_warnings = self._apply_compliance_rules(candidates)

            # Step 7-8: Build suggestions
            suggestions = self._build_suggestions(
                candidates=candidates,
                procedure_id=procedure_id,
                ncci_warnings=ncci_warnings,
                mer_warnings=mer_warnings,
            )

        logger.info(
            "Coding complete",
            extra={
                "procedure_id": procedure_id,
                "num_suggestions": len(suggestions),
                "processing_time_ms": timing.elapsed_ms,
                "llm_latency_ms": llm_latency_ms,
            },
        )

        return suggestions, llm_latency_ms

    def generate_result(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
        procedure_type: str | None = None,
    ) -> CodingResult:
        """Generate a complete coding result with metadata.

        Args:
            procedure_id: Unique identifier for the procedure.
            report_text: The procedure note text.
            use_llm: Whether to use the LLM advisor.
            procedure_type: Classification of the procedure (e.g., bronch_diagnostic,
                          bronch_ebus, pleural, blvr). Used for metrics segmentation.
                          If None or "unknown", auto-detection is attempted.

        Returns:
            CodingResult with suggestions and metadata.
        """
        with timed("coding_service.generate_result") as timing:
            suggestions, llm_latency_ms = self.generate_suggestions(
                procedure_id, report_text, use_llm
            )

        # Auto-detect procedure type if not provided
        if not procedure_type or procedure_type == "unknown":
            suggestion_codes = [s.code for s in suggestions]
            detected_type = detect_procedure_type(
                report_text=report_text,
                codes=suggestion_codes,
            )
            procedure_type = detected_type
            logger.debug(
                "Auto-detected procedure type",
                extra={
                    "procedure_id": procedure_id,
                    "detected_type": detected_type,
                    "codes_used": suggestion_codes[:5],  # Log first 5 codes
                },
            )

        return CodingResult(
            procedure_id=procedure_id,
            suggestions=suggestions,
            final_codes=[],  # Populated after review
            procedure_type=procedure_type,
            warnings=[],
            ncci_notes=[],
            mer_notes=[],
            kb_version=self.kb_repo.version,
            policy_version=self.hybrid_policy.version,
            model_version=self.llm_advisor.version if self.llm_advisor else "",
            processing_time_ms=timing.elapsed_ms,
            llm_latency_ms=llm_latency_ms,
        )

    def _run_rule_engine(self, report_text: str) -> RuleResult:
        """Step 1: Run the rule-based coding engine."""
        with timed("coding_service.rule_engine"):
            result = self.rule_engine.generate_candidates(report_text)

        return RuleResult(
            codes=result.codes,
            confidence=result.confidence,
        )

    def _run_ml_ranker(
        self,
        report_text: str,
        rule_result: RuleResult,
    ) -> Optional[MLRankingResult]:
        """Step 2: Run the ML ranker to get confidence scores.

        If an ML ranker is configured, this augments rule-based codes with
        ML-derived confidence scores. High-confidence ML predictions may
        also be added if not already present from rules.

        Args:
            report_text: The procedure note text.
            rule_result: Result from the rule engine (Step 1).

        Returns:
            MLRankingResult with predictions and confidence scores,
            or None if ML ranker is not available.
        """
        if not self.ml_ranker or not self.ml_ranker.available:
            return None

        with timed("coding_service.ml_ranker"):
            ml_result = self.ml_ranker.rank_codes(
                note_text=report_text,
                candidate_codes=None,  # Score all known codes
            )

        # Log ML ranking results
        logger.info(
            "ML ranking complete",
            extra={
                "difficulty": ml_result.difficulty,
                "high_conf_count": len(ml_result.high_conf_codes),
                "gray_zone_count": len(ml_result.gray_zone_codes),
                "total_predictions": len(ml_result.predictions),
            },
        )

        # Augment rule result confidence with ML scores
        for code in rule_result.codes:
            if code in ml_result.confidence_map:
                ml_conf = ml_result.confidence_map[code]
                rule_conf = rule_result.confidence.get(code, 0.0)
                # Boost confidence if ML agrees, average otherwise
                if ml_conf > 0.5:
                    rule_result.confidence[code] = max(rule_conf, ml_conf * 0.9)
                logger.debug(
                    "ML augmented rule confidence",
                    extra={
                        "code": code,
                        "rule_conf": rule_conf,
                        "ml_conf": ml_conf,
                        "final_conf": rule_result.confidence[code],
                    },
                )

        return ml_result

    def _run_llm_advisor(self, report_text: str, use_llm: bool) -> tuple[AdvisorResult, float]:
        """Step 3: Run the LLM advisor.

        NOTE: PHI redaction is now handled at the API route handler level.
        The report_text passed here should already be scrubbed. The phi_scrubber
        parameter on CodingService is deprecated and ignored.

        Returns:
            Tuple of (AdvisorResult, latency_ms)
        """
        if not use_llm or not self.llm_advisor:
            return AdvisorResult(codes=[], confidence={}), 0.0

        text_for_llm = self._prepare_llm_context(report_text)

        with timed("coding_service.llm_advisor") as timing:
            suggestions = self.llm_advisor.suggest_codes(text_for_llm)

        return AdvisorResult(
            codes=[s.code for s in suggestions],
            confidence={s.code: s.confidence for s in suggestions},
        ), timing.elapsed_ms

    def _run_hybrid_merge(
        self,
        rule_result: RuleResult,
        advisor_result: AdvisorResult,
        report_text: str,
    ) -> list:
        """Step 4: Run the smart hybrid merge."""
        with timed("coding_service.hybrid_merge"):
            candidates = self.hybrid_policy.merge(
                rule_result=rule_result,
                advisor_result=advisor_result,
                report_text=report_text,
            )

        return candidates

    def _apply_compliance_rules(
        self,
        candidates: list[HybridCandidate],
    ) -> tuple[list[HybridCandidate], list[str], list[str]]:
        """Step 6: Apply domain rules and NCCI/MER compliance rules.

        This applies rules in the following order:
        1. Add-on family consistency (e.g., 31636 -> +31637 when 31631 present)
        2. EBUS-Aspiration bundling (31645/31646 bundled into 31652/31653)
        3. NCCI edits from knowledge base
        4. MER (Multiple Endoscopy Rule) reductions
        """
        # Get accepted codes for compliance checking
        accepted_codes = self.hybrid_policy.get_accepted_codes(candidates)

        # Step 6a: Apply add-on family rules (hierarchy fix)
        # This ensures codes like 31636 become +31637 when 31631 is present
        family_result = apply_addon_family_rules(accepted_codes)
        for original, converted, reason in family_result.conversions:
            # Update the candidate code
            for candidate in candidates:
                if candidate.code == original:
                    candidate.code = converted
                    candidate.flags.append(f"FAMILY_CONVERSION: {reason}")
                    logger.info(
                        "Applied family conversion",
                        extra={"original": original, "converted": converted, "reason": reason},
                    )
                    break  # Only convert first occurrence per conversion

        # Refresh accepted codes after family conversions
        accepted_codes = self.hybrid_policy.get_accepted_codes(candidates)

        # Step 6b: Apply all NCCI bundling rules
        # This removes:
        # - Aspiration codes (31645/31646) when EBUS codes (31652/31653) are present
        # - Thoracentesis codes (32554/32555) when IPC placement (32550) is present
        # - Tumor excision (31640) when destruction (31641) is present
        bundle_result = apply_all_ncci_bundles(accepted_codes)
        bundled_codes = set(bundle_result.removed_codes)

        ncci_warnings: list[str] = []
        for primary, removed, reason in bundle_result.bundle_reasons:
            ncci_warnings.append(f"NCCI_BUNDLE: {removed} bundled into {primary} - {reason}")
            logger.info(
                "Applied NCCI bundle",
                extra={"primary": primary, "removed": removed, "reason": reason},
            )

        # Mark bundled candidates as rejected
        for candidate in candidates:
            if candidate.code in bundled_codes:
                candidate.decision = HybridDecision.REJECTED_HYBRID
                candidate.flags.append(f"NCCI_BUNDLED: Code bundled into primary procedure")

        # Refresh accepted codes after bundling
        accepted_codes = self.hybrid_policy.get_accepted_codes(candidates)

        # Step 6c: Apply NCCI edits from knowledge base
        ncci_result = apply_ncci_edits(accepted_codes, self.kb_repo)
        ncci_warnings.extend(ncci_result.warnings)

        # Step 6d: Apply MER rules
        mer_result = apply_mer_rules(ncci_result.kept_codes, self.kb_repo)
        mer_warnings = mer_result.warnings

        # Filter candidates based on compliance results
        final_codes = set(mer_result.kept_codes)
        filtered_candidates: list[HybridCandidate] = []

        for candidate in candidates:
            if candidate.code in final_codes:
                filtered_candidates.append(candidate)
            elif candidate.code in bundled_codes:
                # Already marked as rejected above
                filtered_candidates.append(candidate)
            elif candidate.code in ncci_result.removed_codes:
                # Update the candidate to show it was removed by NCCI
                candidate.decision = HybridDecision.REJECTED_HYBRID
                candidate.flags.append(f"NCCI_REMOVED: {ncci_warnings}")
                filtered_candidates.append(candidate)
            elif candidate.code in mer_result.removed_codes:
                # Update the candidate to show it was removed by MER
                candidate.decision = HybridDecision.REJECTED_HYBRID
                candidate.flags.append(f"MER_REMOVED: {mer_warnings}")
                filtered_candidates.append(candidate)
            else:
                filtered_candidates.append(candidate)

        return filtered_candidates, ncci_warnings, mer_warnings

    def _build_suggestions(
        self,
        candidates: list,
        procedure_id: str,
        ncci_warnings: list[str],
        mer_warnings: list[str],
    ) -> list[CodeSuggestion]:
        """Steps 7-8: Build CodeSuggestion objects."""
        suggestions = []

        for candidate in candidates:
            # Determine source
            if candidate.decision == HybridDecision.ACCEPTED_AGREEMENT:
                source = "hybrid"
            elif candidate.decision in (
                HybridDecision.ACCEPTED_HYBRID,
                HybridDecision.HUMAN_REVIEW_REQUIRED,
            ):
                source = "llm"
            elif candidate.decision in (
                HybridDecision.KEPT_RULE_PRIORITY,
                HybridDecision.DROPPED_LOW_CONFIDENCE,
            ):
                source = "rule"
            else:
                source = "hybrid"

            # Compute final confidence
            rule_conf = candidate.rule_confidence or 0.0
            llm_conf = candidate.llm_confidence or 0.0

            if candidate.decision == HybridDecision.ACCEPTED_AGREEMENT:
                # Agreement boosts confidence
                final_confidence = max(rule_conf, llm_conf) * 1.1
            elif candidate.decision == HybridDecision.ACCEPTED_HYBRID:
                final_confidence = llm_conf
            elif candidate.decision == HybridDecision.KEPT_RULE_PRIORITY:
                final_confidence = rule_conf
            else:
                final_confidence = max(rule_conf, llm_conf, 0.5)

            final_confidence = min(1.0, final_confidence)  # Cap at 1.0

            # Determine review flag
            if candidate.decision == HybridDecision.HUMAN_REVIEW_REQUIRED:
                review_flag = "required"
            elif candidate.decision in (
                HybridDecision.DROPPED_LOW_CONFIDENCE,
                HybridDecision.REJECTED_HYBRID,
            ):
                review_flag = "recommended"
            elif final_confidence < 0.8:
                review_flag = "recommended"
            else:
                review_flag = "optional"

            # Get procedure info for description
            proc_info = self.kb_repo.get_procedure_info(candidate.code)
            description = proc_info.description if proc_info else ""

            # Build reasoning
            reasoning = ReasoningFields(
                trigger_phrases=candidate.trigger_phrases,
                rule_paths=candidate.flags,
                confidence=final_confidence,
                kb_version=self.kb_repo.version,
                policy_version=self.hybrid_policy.version,
                model_version=self.llm_advisor.version if self.llm_advisor else "",
                keyword_map_version=self.keyword_repo.version,
                negation_detector_version=self.negation_detector.version,
                ncci_notes="; ".join(ncci_warnings) if ncci_warnings else "",
                mer_notes="; ".join(mer_warnings) if mer_warnings else "",
            )

            suggestion = CodeSuggestion(
                code=candidate.code,
                description=description,
                source=source,
                hybrid_decision=candidate.decision.value,
                rule_confidence=candidate.rule_confidence,
                llm_confidence=candidate.llm_confidence,
                final_confidence=final_confidence,
                reasoning=reasoning,
                review_flag=review_flag,
                trigger_phrases=candidate.trigger_phrases,
                evidence_verified=candidate.evidence_verified,
                suggestion_id=str(uuid.uuid4()),
                procedure_id=procedure_id,
            )

            suggestions.append(suggestion)

        return suggestions
    def _prepare_llm_context(self, scrubbed_text: str) -> str:
        if not scrubbed_text:
            return scrubbed_text
        if not sectionizer_enabled():
            return scrubbed_text
        tokens = max_llm_input_tokens()
        return accordion_truncate(scrubbed_text, tokens)

    def _generate_suggestions_extraction_first(
        self,
        procedure_id: str,
        report_text: str,
    ) -> tuple[list[CodeSuggestion], float]:
        """Extraction-first pipeline: Registry → Deterministic CPT → ML Audit.

        This pipeline:
        1. Extracts a RegistryRecord from the note text
        2. Derives CPT codes deterministically from the registry fields
        3. Optionally audits the derived codes against raw ML predictions

        Returns:
            Tuple of (List of CodeSuggestion objects, processing latency in ms).
        """
        from modules.registry.application.registry_service import RegistryService
        from modules.coder.domain_rules.registry_to_cpt.coding_rules import (
            derive_all_codes_with_meta,
        )
        from modules.registry.schema import RegistryRecord

        start_time = time.time()

        logger.info(
            "Starting coding pipeline (extraction-first mode)",
            extra={
                "procedure_id": procedure_id,
                "text_length_chars": len(report_text),
            },
        )

        # Step 1: Extract registry fields
        registry_service = RegistryService()
        extraction_result = registry_service.extract_fields(report_text)

        # Step 2: Derive CPT codes from registry fields
        if extraction_result.record:
            record = extraction_result.record
        else:
            # Build a minimal RegistryRecord from mapped_fields
            record = RegistryRecord.model_validate(extraction_result.mapped_fields)

        codes, rationales, derivation_warnings = derive_all_codes_with_meta(record)

        # Step 3: Build audit warnings
        audit_warnings: list[str] = list(extraction_result.audit_warnings or [])
        audit_warnings.extend(derivation_warnings)

        # Determine difficulty level
        if extraction_result.coder_difficulty == "HIGH_CONF":
            base_confidence = 0.95
        elif extraction_result.coder_difficulty == "MEDIUM":
            base_confidence = 0.80
        else:
            base_confidence = 0.70

        # Step 4: Build CodeSuggestion objects
        suggestions: list[CodeSuggestion] = []
        for code in codes:
            rationale = rationales.get(code, "")

            # Format audit warnings for mer_notes
            mer_notes = ""
            if audit_warnings:
                mer_notes = "AUDIT FLAGS:\n" + "\n".join(f"• {w}" for w in audit_warnings)

            reasoning = ReasoningFields(
                trigger_phrases=[],
                evidence_spans=[],
                rule_paths=[f"DETERMINISTIC: {rationale}"],
                ncci_notes="",
                mer_notes=mer_notes,
                confidence=base_confidence,
                kb_version=self.kb_repo.version,
                policy_version="extraction_first_v1",
            )

            # Determine review flag
            if extraction_result.needs_manual_review:
                review_flag = "required"
            elif audit_warnings:
                review_flag = "recommended"
            else:
                review_flag = "optional"

            # Get procedure description
            proc_info = self.kb_repo.get_procedure_info(code)
            description = proc_info.description if proc_info else ""

            suggestion = CodeSuggestion(
                code=code,
                description=description,
                source="hybrid",  # Extraction-first is a form of hybrid
                hybrid_decision="EXTRACTION_FIRST",
                rule_confidence=base_confidence,
                llm_confidence=None,
                final_confidence=base_confidence,
                reasoning=reasoning,
                review_flag=review_flag,
                trigger_phrases=[],
                evidence_verified=True,
                suggestion_id=str(uuid.uuid4()),
                procedure_id=procedure_id,
            )
            suggestions.append(suggestion)

        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            "Coding complete (extraction-first mode)",
            extra={
                "procedure_id": procedure_id,
                "num_suggestions": len(suggestions),
                "processing_time_ms": latency_ms,
                "codes": codes,
            },
        )

        return suggestions, latency_ms
