"""QA Pipeline Service - orchestrates registry, reporter, and coder modules.

This service layer extracts the business logic from the /qa/run endpoint
into a testable, reusable service with proper error handling.
"""

from __future__ import annotations

import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

from modules.common.spans import Span

logger = logging.getLogger(__name__)


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


class ReporterStrategyError(RuntimeError):
    """Raised when the structured reporter pipeline fails."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "REPORTER_STRUCTURED_RENDER_ERROR",
        fallback_reason: str | None = None,
        reporter_errors: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.fallback_reason = fallback_reason
        self.reporter_errors = reporter_errors or []


@dataclass
class ModuleOutcome:
    """Internal representation of a module execution result.

    Attributes:
        ok: Whether the module executed successfully
        data: Module output data (dict)
        error_code: Machine-readable error code on failure
        error_message: Human-readable error description on failure
        skipped: Whether the module was skipped (not requested)
    """

    ok: bool = False
    data: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    skipped: bool = False


@dataclass
class QAPipelineResult:
    """Aggregated result from pipeline execution.

    Attributes:
        registry: Registry module outcome
        reporter: Reporter module outcome
        coder: Coder module outcome
    """

    registry: ModuleOutcome = field(default_factory=ModuleOutcome)
    reporter: ModuleOutcome = field(default_factory=ModuleOutcome)
    coder: ModuleOutcome = field(default_factory=ModuleOutcome)


class SimpleReporterStrategy:
    """Simple reporter using text-based composition.

    Falls back to compose_report_from_text when registry data is unavailable.
    """

    def render(
        self,
        text: str,
        procedure_type: str | None = None,
        *,
        fallback_reason: str | None = None,
        reporter_errors: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a simple text-based report.

        Args:
            text: Raw procedure note text
            procedure_type: Optional procedure type hint

        Returns:
            Dict with markdown, procedure_core, indication, postop
        """
        from modules.reporting.engine import compose_report_from_text

        hints: dict[str, Any] = {}
        if procedure_type:
            hints["procedure_type"] = procedure_type

        report, markdown = compose_report_from_text(text, hints)
        proc_core = report.procedure_core

        return {
            "markdown": markdown,
            "procedure_core": (
                proc_core.model_dump() if hasattr(proc_core, "model_dump") else {}
            ),
            "indication": report.indication,
            "postop": report.postop,
            "fallback_used": True,
            "render_mode": "simple_fallback",
            "fallback_reason": fallback_reason,
            "reporter_errors": reporter_errors or [],
        }


class ReportingStrategy:
    """Registry-aware reporting strategy.

    Uses structured registry data when available, falls back to simple
    reporter when registry extraction fails or is unavailable.
    """

    def __init__(
        self,
        reporter_engine: Any,
        inference_engine: Any,
        validation_engine: Any,
        registry_engine: Any,
        simple_strategy: SimpleReporterStrategy,
    ):
        """Initialize reporting strategy.

        Args:
            reporter_engine: ReporterEngine for structured reports
            inference_engine: InferenceEngine for bundle enrichment
            validation_engine: ValidationEngine for issue detection
            registry_engine: RegistryEngine for fallback extraction
            simple_strategy: Fallback strategy for text-only reports
        """
        self.reporter_engine = reporter_engine
        self.inference_engine = inference_engine
        self.validation_engine = validation_engine
        self.registry_engine = registry_engine
        self.simple_strategy = simple_strategy
        self.allow_simple_fallback = _env_enabled(
            "QA_REPORTER_ALLOW_SIMPLE_FALLBACK"
        )

    def render(
        self,
        text: str,
        registry_data: dict[str, Any] | None = None,
        procedure_type: str | None = None,
    ) -> dict[str, Any]:
        """Render a procedure report.

        If registry_data is provided and contains a record, generates a
        structured report with bundle, issues, and warnings.

        If registry_data is None or empty, attempts a lightweight registry
        extraction first. If that fails, falls back to simple text-based
        report generation.

        Args:
            text: Raw procedure note text
            registry_data: Optional pre-computed registry data
            procedure_type: Optional procedure type hint

        Returns:
            Dict with report data (markdown, bundle/issues/warnings or
            procedure_core/indication/postop for fallback)
        """

        # Case 1: We have registry data with a record
        if registry_data and registry_data.get("record"):
            try:
                return self._render_structured(registry_data["record"])
            except ReporterStrategyError as exc:
                return self._handle_structured_failure(
                    text=text,
                    procedure_type=procedure_type,
                    error_code=exc.error_code,
                    fallback_reason=exc.fallback_reason or "structured_render_failed",
                    reporter_errors=exc.reporter_errors or [str(exc)],
                )
            except Exception as exc:  # pragma: no cover - defensive guard
                return self._handle_structured_failure(
                    text=text,
                    procedure_type=procedure_type,
                    error_code="REPORTER_STRUCTURED_RENDER_ERROR",
                    fallback_reason="structured_render_failed",
                    reporter_errors=[str(exc)],
                )

        # Case 2: No registry data - try lightweight extraction
        registry_errors: list[str] = []
        try:
            logger.debug("Running lightweight registry extraction for reporter")
            reg_result = self.registry_engine.run(text, explain=False)
            if isinstance(reg_result, tuple):
                reg_record, _ = reg_result
            else:
                reg_record = reg_result

            if hasattr(reg_record, "model_dump"):
                reg_dict = reg_record.model_dump()
            elif isinstance(reg_record, dict):
                reg_dict = reg_record
            else:
                reg_dict = {}

            if reg_dict:
                try:
                    return self._render_structured(reg_dict)
                except ReporterStrategyError as exc:
                    return self._handle_structured_failure(
                        text=text,
                        procedure_type=procedure_type,
                        error_code=exc.error_code,
                        fallback_reason=exc.fallback_reason
                        or "structured_render_failed",
                        reporter_errors=exc.reporter_errors or [str(exc)],
                    )
                except Exception as exc:  # pragma: no cover - defensive guard
                    return self._handle_structured_failure(
                        text=text,
                        procedure_type=procedure_type,
                        error_code="REPORTER_STRUCTURED_RENDER_ERROR",
                        fallback_reason="structured_render_failed",
                        reporter_errors=[str(exc)],
                    )
            registry_errors.append(
                "Lightweight registry extraction returned an empty record."
            )
        except Exception as exc:
            registry_errors.append(str(exc))
            logger.warning(
                "Lightweight registry extraction failed for reporter: %s", exc
            )

        # Case 3: All structured approaches failed.
        return self._handle_structured_failure(
            text=text,
            procedure_type=procedure_type,
            error_code="REPORTER_STRUCTURED_RENDER_ERROR",
            fallback_reason="structured_unavailable",
            reporter_errors=registry_errors
            or ["Structured reporter could not produce output."],
        )

    def _handle_structured_failure(
        self,
        *,
        text: str,
        procedure_type: str | None,
        error_code: str,
        fallback_reason: str,
        reporter_errors: list[str],
    ) -> dict[str, Any]:
        message = "; ".join([msg for msg in reporter_errors if msg]) or fallback_reason
        if self.allow_simple_fallback:
            logger.warning(
                "Structured reporter failed; using simple fallback (%s): %s",
                fallback_reason,
                message,
            )
            return self.simple_strategy.render(
                text,
                procedure_type,
                fallback_reason=fallback_reason,
                reporter_errors=reporter_errors,
            )
        raise ReporterStrategyError(
            message or "Structured reporter failed",
            error_code=error_code,
            fallback_reason=fallback_reason,
            reporter_errors=reporter_errors,
        )

    def _serialize_issue(self, issue: Any) -> dict[str, Any]:
        if hasattr(issue, "model_dump"):
            dumped = issue.model_dump()
            if isinstance(dumped, dict):
                return dumped
            raise TypeError("model_dump() did not return a dict")
        if is_dataclass(issue):
            dumped = asdict(issue)
            if isinstance(dumped, dict):
                return dumped
            raise TypeError("dataclass serialization did not return a dict")
        if isinstance(issue, dict):
            return issue
        raise TypeError(
            f"Unsupported reporter issue type for serialization: {type(issue)!r}"
        )

    def _serialize_issues(self, issues: list[Any]) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for issue in issues:
            try:
                serialized.append(self._serialize_issue(issue))
            except Exception as exc:
                raise ReporterStrategyError(
                    f"Failed to serialize reporter validation issue: {exc}",
                    error_code="REPORTER_ISSUE_SERIALIZATION_ERROR",
                    fallback_reason="issue_serialization_failed",
                    reporter_errors=[str(exc)],
                ) from exc
        return serialized

    def _render_structured(self, record: dict[str, Any]) -> dict[str, Any]:
        """Render structured report from registry record.

        Args:
            record: Registry extraction record dict

        Returns:
            Dict with markdown, bundle, issues, warnings
        """
        from modules.reporting.engine import (
            apply_patch_result,
            build_procedure_bundle_from_extraction,
        )

        # Build bundle from registry extraction
        bundle = build_procedure_bundle_from_extraction(record)

        # Run inference to enrich the bundle
        inference_result = self.inference_engine.infer_bundle(bundle)
        bundle = apply_patch_result(bundle, inference_result)

        # Validate and get issues/warnings
        issues = self.validation_engine.list_missing_critical_fields(bundle)
        warnings = self.validation_engine.apply_warn_if_rules(bundle)

        # Generate structured report
        try:
            structured = self.reporter_engine.compose_report_with_metadata(
                bundle,
                strict=False,
                embed_metadata=False,
                validation_issues=issues,
                warnings=warnings,
            )
        except Exception as exc:
            raise ReporterStrategyError(
                f"Structured report rendering failed: {exc}",
                error_code="REPORTER_STRUCTURED_RENDER_ERROR",
                fallback_reason="structured_render_failed",
                reporter_errors=[str(exc)],
            ) from exc

        return {
            "markdown": structured.text,
            "bundle": bundle.model_dump() if hasattr(bundle, "model_dump") else {},
            "issues": self._serialize_issues(issues) if issues else [],
            "warnings": warnings,
            "fallback_used": False,
            "render_mode": "structured",
            "fallback_reason": None,
            "reporter_errors": [],
        }


class QAPipelineService:
    """Orchestrates the QA pipeline: registry -> reporter -> coder.

    This service coordinates the execution of registry extraction,
    report generation, and code suggestion modules.
    """

    def __init__(
        self,
        registry_engine: Any,
        reporting_strategy: ReportingStrategy,
        coding_service: Any,
    ):
        """Initialize the QA pipeline service.

        Args:
            registry_engine: RegistryEngine for procedure extraction
            reporting_strategy: Strategy for report generation
            coding_service: CodingService for code suggestions
        """
        self.registry_engine = registry_engine
        self.reporting_strategy = reporting_strategy
        self.coding_service = coding_service

    def run_pipeline(
        self,
        text: str,
        modules: str = "all",
        procedure_type: str | None = None,
    ) -> QAPipelineResult:
        """Execute the QA pipeline on procedure note text.

        Args:
            text: Raw procedure note text
            modules: Which modules to run ("all", "registry", "reporter", "coder")
            procedure_type: Optional procedure type hint

        Returns:
            QAPipelineResult with outcomes for each module
        """
        result = QAPipelineResult()

        # Determine which modules to run
        run_registry = modules in ("registry", "all")
        run_reporter = modules in ("reporter", "all")
        run_coder = modules in ("coder", "all")

        # Mark skipped modules
        if not run_registry:
            result.registry = ModuleOutcome(skipped=True)
        if not run_reporter:
            result.reporter = ModuleOutcome(skipped=True)
        if not run_coder:
            result.coder = ModuleOutcome(skipped=True)

        registry_data: dict[str, Any] | None = None

        # Overlap independent work (registry + coder) to reduce wall-clock latency.
        registry_future = None
        coder_future = None

        with ThreadPoolExecutor(max_workers=2) as pool:
            if run_registry:
                registry_future = pool.submit(self._run_registry, text)
            if run_coder:
                coder_future = pool.submit(self._run_coder, text, procedure_type)

            # Registry result (needed for reporter)
            if registry_future is not None:
                result.registry = registry_future.result()
                if result.registry.ok and result.registry.data:
                    registry_data = result.registry.data

            # Reporter (depends on registry_data, but can run while coder is still in-flight)
            if run_reporter:
                result.reporter = self._run_reporter(text, registry_data, procedure_type)

            # Coder result (independent)
            if coder_future is not None:
                result.coder = coder_future.result()

        return result

    def _run_registry(self, text: str) -> ModuleOutcome:
        """Run registry extraction.

        Args:
            text: Raw procedure note text

        Returns:
            ModuleOutcome with registry data or error
        """
        try:
            result = self.registry_engine.run(text, explain=True)
            if isinstance(result, tuple):
                record, evidence = result
            else:
                record, evidence = result, getattr(result, "evidence", {})

            return ModuleOutcome(
                ok=True,
                data={
                    "record": (
                        record.model_dump()
                        if hasattr(record, "model_dump")
                        else dict(record)
                    ),
                    "evidence": self._serialize_evidence(evidence),
                },
            )
        except ValueError as ve:
            logger.error(f"Registry validation error: {ve}")
            return ModuleOutcome(
                ok=False,
                error_code="REGISTRY_VALIDATION_ERROR",
                error_message=f"Registry validation failed: {str(ve)}",
            )
        except Exception as e:
            logger.error(f"Registry extraction error: {e}")
            return ModuleOutcome(
                ok=False,
                error_code="REGISTRY_ERROR",
                error_message=f"Registry extraction failed: {str(e)}",
            )

    def _run_reporter(
        self,
        text: str,
        registry_data: dict[str, Any] | None,
        procedure_type: str | None,
    ) -> ModuleOutcome:
        """Run reporter module.

        Args:
            text: Raw procedure note text
            registry_data: Optional registry extraction data
            procedure_type: Optional procedure type hint

        Returns:
            ModuleOutcome with reporter data or error
        """
        try:
            data = self.reporting_strategy.render(
                text, registry_data, procedure_type
            )
            return ModuleOutcome(ok=True, data=data)
        except ReporterStrategyError as exc:
            logger.error("Reporter structured error: %s", exc)
            return ModuleOutcome(
                ok=False,
                error_code=exc.error_code,
                error_message=f"Report generation failed: {str(exc)}",
            )
        except Exception as e:
            logger.error(f"Reporter error: {e}")
            return ModuleOutcome(
                ok=False,
                error_code="REPORTER_ERROR",
                error_message=f"Report generation failed: {str(e)}",
            )

    def _run_coder(
        self, text: str, procedure_type: str | None
    ) -> ModuleOutcome:
        """Run coder module.

        Args:
            text: Raw procedure note text
            procedure_type: Optional procedure type hint

        Returns:
            ModuleOutcome with coder data or error
        """
        try:
            procedure_id = str(uuid.uuid4())

            result = self.coding_service.generate_result(
                procedure_id=procedure_id,
                report_text=text,
                use_llm=True,
                procedure_type=procedure_type,
            )

            codes = [
                {
                    "cpt": s.code,
                    "description": s.description,
                    "confidence": s.final_confidence,
                    "source": s.source,
                    "hybrid_decision": s.hybrid_decision,
                    # QA schema expects a boolean; treat required/recommended as needing review.
                    "review_flag": str(getattr(s, "review_flag", "")).lower()
                    in ("required", "recommended"),
                }
                for s in result.suggestions
            ]

            return ModuleOutcome(
                ok=True,
                data={
                    "codes": codes,
                    "total_work_rvu": None,
                    "estimated_payment": None,
                    "bundled_codes": [],
                    "kb_version": result.kb_version,
                    "policy_version": result.policy_version,
                    "model_version": result.model_version,
                    "processing_time_ms": (
                        int(result.processing_time_ms)
                        if result.processing_time_ms is not None
                        else None
                    ),
                },
            )
        except Exception as e:
            logger.error(f"Coder error: {e}")
            return ModuleOutcome(
                ok=False,
                error_code="CODER_ERROR",
                error_message=f"Code suggestion failed: {str(e)}",
            )

    def _serialize_evidence(
        self, evidence: dict[str, list[Span]] | None
    ) -> dict[str, list[dict[str, Any]]]:
        """Serialize evidence spans to JSON-compatible structure.

        Args:
            evidence: Field-to-spans mapping

        Returns:
            JSON-serializable evidence dict
        """
        from dataclasses import asdict

        serialized: dict[str, list[dict[str, Any]]] = {}
        for field_name, spans in (evidence or {}).items():
            serialized[field_name] = [asdict(span) for span in spans]
        return serialized


__all__ = [
    "ModuleOutcome",
    "QAPipelineResult",
    "QAPipelineService",
    "ReporterStrategyError",
    "ReportingStrategy",
    "SimpleReporterStrategy",
]
