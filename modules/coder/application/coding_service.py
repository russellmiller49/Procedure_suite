"""Coding Service - orchestrates the 8-step coding pipeline.

This service coordinates rule-based coding, LLM advisor suggestions,
smart hybrid merge, evidence validation, NCCI/MER compliance, and
produces CodeSuggestion objects for review.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import os

from config.settings import CoderSettings
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from modules.domain.coding_rules import apply_ncci_edits, apply_mer_rules
from modules.domain.coding_rules.rule_engine import RuleEngine
from modules.coder.adapters.nlp.keyword_mapping_loader import KeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.adapters.llm.gemini_advisor import LLMAdvisorPort
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
    ):
        self.kb_repo = kb_repo
        self.keyword_repo = keyword_repo
        self.negation_detector = negation_detector
        self.rule_engine = rule_engine
        self.llm_advisor = llm_advisor
        self.config = config
        self.phi_scrubber = phi_scrubber

        # Initialize hybrid policy
        self.hybrid_policy = HybridPolicy(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            config=config,
        )

        # Log PHI scrubber status
        if llm_advisor and not phi_scrubber:
            logger.warning(
                "LLM advisor enabled but no PHI scrubber configured. "
                "Raw text may be sent to external LLM service."
            )

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
        llm_latency_ms = 0.0

        # Log input text size for debugging truncation issues
        text_length = len(report_text)
        logger.info(
            "Starting coding pipeline",
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

            # Step 2: Optional ML ranking (not implemented yet)
            # ml_result = self._run_ml_ranker(rule_result)

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

    def _run_llm_advisor(self, report_text: str, use_llm: bool) -> tuple[AdvisorResult, float]:
        """Step 3: Run the LLM advisor.

        PHI Guardrail: If a PHI scrubber is configured, the text is scrubbed
        before being sent to the external LLM service. This prevents PHI
        from being transmitted to third-party APIs.

        Returns:
            Tuple of (AdvisorResult, latency_ms)
        """
        if not use_llm or not self.llm_advisor:
            return AdvisorResult(codes=[], confidence={}), 0.0

        # PHI Guardrail: Scrub text before sending to LLM
        text_for_llm = report_text
        if self.phi_scrubber:
            try:
                scrub_result = self.phi_scrubber.scrub(report_text)
                text_for_llm = scrub_result.scrubbed_text
                logger.debug(
                    "PHI scrubbed before LLM call",
                    extra={"entities_found": len(scrub_result.entities)},
                )
            except Exception as e:
                logger.error(f"PHI scrubbing failed: {e}", exc_info=True)
                # Fail safely: don't send potentially unscrubbed text to LLM
                logger.warning("Skipping LLM advisor due to scrubbing failure")
                return AdvisorResult(codes=[], confidence={}), 0.0

        text_for_llm = self._prepare_llm_context(text_for_llm)

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
