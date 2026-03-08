from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from app.coder.domain_rules.registry_to_cpt.engine import apply as derive_registry_to_cpt
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.heuristics import (
    CaoDetailHeuristic,
    LinearEbusStationDetailHeuristic,
    NavigationTargetHeuristic,
    apply_heuristics,
    reconcile_granular_validation_warnings,
)
from app.registry.processing.masking import mask_extraction_noise, mask_offset_preserving
from app.registry.schema import RegistryRecord
from app.registry.self_correction.keyword_guard import apply_required_overrides, scan_for_omissions


def _signal_code_from_warning(text: str) -> str:
    head = str(text or "").split(":", 1)[0].strip().upper()
    normalized = re.sub(r"[^A-Z0-9_]+", "_", head).strip("_")
    return normalized or "WARNING"


def _signal_severity_from_warning(text: str) -> Literal["info", "warning", "review"]:
    warning = str(text or "")
    if warning.startswith("NEEDS_REVIEW:") or warning.startswith("SILENT_FAILURE:"):
        return "review"
    if warning.startswith("DETERMINISTIC_UPLIFT:") or warning.startswith("AUTO_"):
        return "info"
    return "warning"


@dataclass(frozen=True)
class QualitySignal:
    version: str
    phase: str
    signal_type: str
    code: str
    severity: Literal["info", "warning", "review"]
    message: str
    legacy_warning: str | None = None
    emitted_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_warning(
        cls,
        *,
        phase: str,
        warning: str,
        emitted_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "QualitySignal":
        text = str(warning or "")
        return cls(
            version="quality_signal.v1",
            phase=phase,
            signal_type="legacy_warning",
            code=_signal_code_from_warning(text),
            severity=_signal_severity_from_warning(text),
            message=text,
            legacy_warning=text,
            emitted_by=emitted_by,
            metadata=dict(metadata or {}),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "phase": self.phase,
            "signal_type": self.signal_type,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "legacy_warning": self.legacy_warning,
            "emitted_by": self.emitted_by,
            "metadata": dict(self.metadata or {}),
        }


def quality_signals_to_legacy_warnings(signals: list[QualitySignal]) -> list[str]:
    warnings: list[str] = []
    for signal in signals:
        if isinstance(signal.legacy_warning, str) and signal.legacy_warning:
            warnings.append(signal.legacy_warning)
    return warnings


@dataclass
class QualityContext:
    raw_note_text: str
    record: RegistryRecord
    masked_note_text: str = ""
    source_type: str = "raw_note_text"
    extraction_text: str | None = None
    quality_signals: list[QualitySignal] = field(default_factory=list)
    phases_run: list[str] = field(default_factory=list)
    omission_warnings: list[str] = field(default_factory=list)
    derivation: Any | None = None
    derived_codes: list[str] = field(default_factory=list)
    record_guardrail_needs_review: bool = False
    code_guardrail_needs_review: bool = False

    def add_signal(self, signal: QualitySignal) -> None:
        self.quality_signals.append(signal)

    def add_warning_signals(
        self,
        *,
        phase: str,
        warnings: list[str] | tuple[str, ...] | None,
        emitted_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        for warning in warnings or []:
            text = str(warning or "")
            if not text:
                continue
            self.quality_signals.append(
                QualitySignal.from_warning(
                    phase=phase,
                    warning=text,
                    emitted_by=emitted_by,
                    metadata=metadata,
                )
            )

    def remove_warning_signals(self, warnings: list[str] | tuple[str, ...] | None) -> None:
        removed = {str(item) for item in (warnings or []) if str(item)}
        if not removed:
            return
        self.quality_signals = [
            signal
            for signal in self.quality_signals
            if not (signal.signal_type == "legacy_warning" and signal.legacy_warning in removed)
        ]

    @property
    def legacy_warnings(self) -> list[str]:
        return quality_signals_to_legacy_warnings(self.quality_signals)

    @property
    def needs_manual_review(self) -> bool:
        return bool(self.omission_warnings) or self.record_guardrail_needs_review or self.code_guardrail_needs_review


QualityPhase = Callable[[QualityContext], None]


@dataclass
class OrderedQualityPhaseRunner:
    phases: list[tuple[str, QualityPhase]]

    def run(self, context: QualityContext) -> QualityContext:
        for phase_name, phase in self.phases:
            context.phases_run.append(phase_name)
            phase(context)
        return context


class ExtractionQualityPassRunner:
    def __init__(
        self,
        *,
        clinical_guardrails: ClinicalGuardrails,
        granular_propagator: Callable[[RegistryRecord], tuple[RegistryRecord, list[str]]],
    ) -> None:
        self.clinical_guardrails = clinical_guardrails
        self.granular_propagator = granular_propagator
        self.runner = OrderedQualityPhaseRunner(
            phases=[
                ("masked_text_prep", self._masked_text_prep),
                ("deterministic_uplift", self._deterministic_uplift),
                ("narrative_template_reconciliation", self._narrative_template_reconciliation),
                ("precision_guardrails", self._precision_guardrails),
                ("evidence_verification", self._evidence_verification),
                ("cpt_derivation", self._cpt_derivation),
                ("omission_audit", self._omission_audit),
            ]
        )

    def run(
        self,
        *,
        raw_note_text: str,
        record: RegistryRecord,
        extraction_warnings: list[str] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> QualityContext:
        metadata = dict(meta or {})
        masked_note_text, _mask_meta = mask_extraction_noise(raw_note_text)
        if isinstance(metadata.get("masked_note_text"), str):
            masked_note_text = str(metadata["masked_note_text"])

        context = QualityContext(
            raw_note_text=raw_note_text,
            record=record,
            masked_note_text=masked_note_text,
            source_type="masked_note_text" if masked_note_text != (raw_note_text or "") else "raw_note_text",
            extraction_text=metadata.get("extraction_text")
            if isinstance(metadata.get("extraction_text"), str)
            else None,
        )
        context.add_warning_signals(
            phase="extract_record",
            warnings=extraction_warnings,
            emitted_by="extract_record",
        )
        self.runner.run(context)
        return context

    def _masked_text_prep(self, context: QualityContext) -> None:
        context.add_signal(
            QualitySignal(
                version="quality_signal.v1",
                phase="masked_text_prep",
                signal_type="source_type",
                code="SOURCE_TYPE",
                severity="info",
                message=f"source_type={context.source_type}",
                emitted_by="mask_extraction_noise",
                metadata={
                    "source_type": context.source_type,
                    "masked_text_changed": context.masked_note_text != (context.raw_note_text or ""),
                },
            )
        )

    def _deterministic_uplift(self, context: QualityContext) -> None:
        context.record, override_warnings = apply_required_overrides(context.masked_note_text, context.record)
        context.add_warning_signals(
            phase="deterministic_uplift",
            warnings=override_warnings,
            emitted_by="apply_required_overrides",
        )

        nav_scan_text = mask_offset_preserving(context.raw_note_text or "")
        context.record, nav_ebus_warnings = apply_heuristics(
            note_text=nav_scan_text,
            record=context.record,
            heuristics=(
                NavigationTargetHeuristic(),
                LinearEbusStationDetailHeuristic(),
            ),
        )
        context.add_warning_signals(
            phase="deterministic_uplift",
            warnings=nav_ebus_warnings,
            emitted_by="apply_heuristics",
        )

        context.record, cao_detail_warnings = CaoDetailHeuristic().apply(
            context.masked_note_text,
            context.record,
        )
        context.add_warning_signals(
            phase="deterministic_uplift",
            warnings=cao_detail_warnings,
            emitted_by="CaoDetailHeuristic",
        )

        context.record, granular_warnings = self.granular_propagator(context.record)
        context.add_warning_signals(
            phase="deterministic_uplift",
            warnings=granular_warnings,
            emitted_by="granular_propagator",
        )

    def _narrative_template_reconciliation(self, context: QualityContext) -> None:
        from app.registry.postprocess import (
            cull_hollow_ebus_claims,
            cull_tbna_conventional_against_ebus_sampling,
            enrich_bal_from_procedure_detail,
            enrich_ebus_node_event_outcomes,
            enrich_ebus_node_event_sampling_details,
            enrich_eus_b_sampling_details,
            enrich_linear_ebus_needle_gauge,
            enrich_medical_thoracoscopy_biopsies_taken,
            enrich_outcomes_complication_details,
            enrich_procedure_success_status,
            enrich_specimens_from_specimen_section,
            populate_ebus_node_events_fallback,
            reconcile_aborted_targets,
            reconcile_ebus_inspected_only_stations,
            reconcile_ebus_sampling_from_narrative,
            reconcile_ebus_sampling_from_specimen_log,
            reconcile_peripheral_tbna_against_nodal_context,
            sanitize_ebus_events,
        )
        from app.registry.postprocess.complications_reconcile import (
            reconcile_complications_from_narrative,
        )

        def _apply(
            emitted_by: str,
            func: Callable[..., list[str]],
            *args: Any,
        ) -> None:
            warnings = func(*args)
            context.add_warning_signals(
                phase="narrative_template_reconciliation",
                warnings=warnings,
                emitted_by=emitted_by,
            )

        _apply("populate_ebus_node_events_fallback", populate_ebus_node_events_fallback, context.record, context.masked_note_text)
        _apply("sanitize_ebus_events", sanitize_ebus_events, context.record, context.masked_note_text)
        _apply("reconcile_ebus_sampling_from_narrative", reconcile_ebus_sampling_from_narrative, context.record, context.masked_note_text)
        _apply("reconcile_ebus_sampling_from_specimen_log", reconcile_ebus_sampling_from_specimen_log, context.record, context.masked_note_text)
        _apply("sanitize_ebus_events", sanitize_ebus_events, context.record, context.masked_note_text)
        _apply("reconcile_ebus_inspected_only_stations", reconcile_ebus_inspected_only_stations, context.record, context.masked_note_text)
        _apply(
            "reconcile_peripheral_tbna_against_nodal_context",
            reconcile_peripheral_tbna_against_nodal_context,
            context.record,
            context.masked_note_text,
        )
        _apply(
            "cull_tbna_conventional_against_ebus_sampling",
            cull_tbna_conventional_against_ebus_sampling,
            context.record,
            context.masked_note_text,
        )
        _apply(
            "enrich_ebus_node_event_sampling_details",
            enrich_ebus_node_event_sampling_details,
            context.record,
            context.masked_note_text,
        )
        _apply(
            "enrich_ebus_node_event_outcomes",
            enrich_ebus_node_event_outcomes,
            context.record,
            context.masked_note_text,
        )
        _apply("enrich_linear_ebus_needle_gauge", enrich_linear_ebus_needle_gauge, context.record, context.masked_note_text)
        _apply("enrich_eus_b_sampling_details", enrich_eus_b_sampling_details, context.record, context.masked_note_text)
        _apply("cull_hollow_ebus_claims", cull_hollow_ebus_claims, context.record, context.masked_note_text)
        _apply(
            "enrich_medical_thoracoscopy_biopsies_taken",
            enrich_medical_thoracoscopy_biopsies_taken,
            context.record,
            context.masked_note_text,
        )
        _apply("enrich_bal_from_procedure_detail", enrich_bal_from_procedure_detail, context.record, context.masked_note_text)
        _apply("enrich_specimens_from_specimen_section", enrich_specimens_from_specimen_section, context.record, context.raw_note_text or "")
        _apply("reconcile_aborted_targets", reconcile_aborted_targets, context.record, context.masked_note_text)
        _apply("enrich_procedure_success_status", enrich_procedure_success_status, context.record, context.masked_note_text)
        _apply("enrich_outcomes_complication_details", enrich_outcomes_complication_details, context.record, context.masked_note_text)
        _apply("reconcile_complications_from_narrative", reconcile_complications_from_narrative, context.record, context.masked_note_text)

    def _precision_guardrails(self, context: QualityContext) -> None:
        from app.registry.postprocess.template_checkbox_negation import apply_template_checkbox_negation

        guardrail_outcome = self.clinical_guardrails.apply_record_guardrails(
            context.masked_note_text,
            context.record,
        )
        context.record = guardrail_outcome.record or context.record
        context.record_guardrail_needs_review = bool(guardrail_outcome.needs_review)
        context.add_warning_signals(
            phase="precision_guardrails",
            warnings=guardrail_outcome.warnings,
            emitted_by="apply_record_guardrails",
        )

        context.record, checkbox_warnings = apply_template_checkbox_negation(
            context.raw_note_text or "",
            context.record,
        )
        context.add_warning_signals(
            phase="precision_guardrails",
            warnings=checkbox_warnings,
            emitted_by="apply_template_checkbox_negation",
        )

        context.record, removed_granular_warnings = reconcile_granular_validation_warnings(context.record)
        context.remove_warning_signals(removed_granular_warnings)

    def _evidence_verification(self, context: QualityContext) -> None:
        from app.registry.evidence.verifier import verify_evidence_integrity

        context.record, verifier_warnings = verify_evidence_integrity(
            context.record,
            context.raw_note_text or context.masked_note_text,
        )
        context.add_warning_signals(
            phase="evidence_verification",
            warnings=verifier_warnings,
            emitted_by="verify_evidence_integrity",
        )

    def _cpt_derivation(self, context: QualityContext) -> None:
        context.derivation = derive_registry_to_cpt(context.record)
        context.derived_codes = [code.code for code in context.derivation.codes]

    def _omission_audit(self, context: QualityContext) -> None:
        omission_warnings = scan_for_omissions(context.masked_note_text, context.record)
        context.omission_warnings = [str(item) for item in omission_warnings if str(item)]
        context.add_warning_signals(
            phase="omission_audit",
            warnings=context.omission_warnings,
            emitted_by="scan_for_omissions",
        )

        code_guardrail = self.clinical_guardrails.apply_code_guardrails(
            context.masked_note_text,
            context.derived_codes,
        )
        context.code_guardrail_needs_review = bool(code_guardrail.needs_review)
        context.add_warning_signals(
            phase="omission_audit",
            warnings=code_guardrail.warnings,
            emitted_by="apply_code_guardrails",
        )


__all__ = [
    "ExtractionQualityPassRunner",
    "OrderedQualityPhaseRunner",
    "QualityContext",
    "QualitySignal",
    "quality_signals_to_legacy_warnings",
]
