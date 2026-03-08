from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel

from app.registry.application.quality_passes import QualitySignal
from app.reporting import MissingFieldIssue, ProcedureBundle, build_questions
from app.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    apply_bundle_patch,
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from app.reporting.inference import InferenceEngine
from app.reporting.json_patch import BundleJsonPatchError, apply_bundle_json_patch
from app.reporting.macro_registry import get_macro_registry
from app.reporting.normalization.normalize import normalize_bundle
from app.reporting.validation import ValidationEngine

logger = logging.getLogger(__name__)


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
class ReporterSeedQualityFlag:
    version: str
    code: str
    severity: Literal["info", "warning", "review"]
    source: str
    message: str
    legacy_warning: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "code": self.code,
            "severity": self.severity,
            "source": self.source,
            "message": self.message,
            "legacy_warning": self.legacy_warning,
            "metadata": dict(self.metadata or {}),
        }


@dataclass
class ReporterSeedOutcome:
    record: Any
    masked_seed_text: str
    warnings: list[str]
    seed_path: Literal["registry_extract_fields", "llm_findings"]
    quality_flags: list[ReporterSeedQualityFlag] = field(default_factory=list)
    needs_review: bool = False
    reporting_payload: Any | None = None
    debug_metadata: dict[str, Any] = field(default_factory=dict)

    def debug_note(self) -> dict[str, Any]:
        return {
            "type": "reporter_seed",
            "seed_path": self.seed_path,
            "needs_review": bool(self.needs_review),
            "warnings_count": int(len(self.warnings or [])),
            "quality_flags": [flag.to_payload() for flag in self.quality_flags],
            "metadata": dict(self.debug_metadata or {}),
        }


@dataclass
class ReporterSeedPipelineResult:
    bundle: ProcedureBundle
    markdown: str
    issues: list[MissingFieldIssue]
    warnings: list[str]
    inference_notes: list[str]
    suggestions: list[str]
    questions: list[Any]
    missing_field_prompts: list[dict[str, Any]]
    debug_notes: list[dict[str, Any]] | None
    render_fallback_used: bool = False


def _quality_flag_from_warning(
    warning: str,
    *,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> ReporterSeedQualityFlag:
    text = str(warning or "")
    return ReporterSeedQualityFlag(
        version="reporter_seed_flag.v1",
        code=_signal_code_from_warning(text),
        severity=_signal_severity_from_warning(text),
        source=source,
        message=text,
        legacy_warning=text or None,
        metadata=dict(metadata or {}),
    )


def _quality_flag_from_signal(signal: QualitySignal) -> ReporterSeedQualityFlag:
    return ReporterSeedQualityFlag(
        version="reporter_seed_flag.v1",
        code=str(signal.code or "QUALITY_SIGNAL"),
        severity=signal.severity,
        source="registry_quality_signal",
        message=str(signal.message or ""),
        legacy_warning=signal.legacy_warning,
        metadata={
            "phase": signal.phase,
            "signal_type": signal.signal_type,
            "emitted_by": signal.emitted_by,
            **dict(signal.metadata or {}),
        },
    )


def _ensure_review_flag(
    flags: list[ReporterSeedQualityFlag],
    *,
    seed_path: str,
    message: str,
) -> list[ReporterSeedQualityFlag]:
    if any(flag.severity == "review" for flag in flags):
        return flags
    return [
        *flags,
        ReporterSeedQualityFlag(
            version="reporter_seed_flag.v1",
            code="SEED_NEEDS_REVIEW",
            severity="review",
            source=seed_path,
            message=message,
            metadata={},
        ),
    ]


def seed_outcome_from_registry_result(
    result: Any,
    *,
    masked_seed_text: str,
) -> ReporterSeedOutcome:
    quality_signals = list(getattr(result, "quality_signals", []) or [])
    quality_flags = [_quality_flag_from_signal(signal) for signal in quality_signals]
    if not quality_flags:
        for warning in list(getattr(result, "warnings", []) or []):
            quality_flags.append(
                _quality_flag_from_warning(
                    str(warning),
                    source="registry_extract_fields",
                )
            )

    needs_review = bool(getattr(result, "needs_manual_review", False))
    if needs_review:
        quality_flags = _ensure_review_flag(
            quality_flags,
            seed_path="registry_extract_fields",
            message="Registry extraction requires manual review.",
        )

    return ReporterSeedOutcome(
        record=getattr(result, "record", None),
        reporting_payload=getattr(result, "record", None),
        masked_seed_text=masked_seed_text,
        warnings=[],
        seed_path="registry_extract_fields",
        quality_flags=quality_flags,
        needs_review=needs_review,
        debug_metadata={
            "coder_source": getattr(result, "coder_source", None),
            "coder_difficulty": getattr(result, "coder_difficulty", None),
            "quality_phase_order": list(getattr(result, "quality_phase_order", []) or []),
            "derived_cpt_codes": [str(code) for code in list(getattr(result, "cpt_codes", []) or [])],
        },
    )


def seed_outcome_from_llm_findings_seed(
    seed: Any,
    *,
    reporting_payload: Any,
) -> ReporterSeedOutcome:
    warnings = [str(item) for item in list(getattr(seed, "warnings", []) or []) if str(item)]
    quality_flags = [
        _quality_flag_from_warning(
            warning,
            source="llm_findings_warning",
        )
        for warning in warnings
    ]
    needs_review = bool(getattr(seed, "needs_review", False))
    if needs_review:
        quality_flags = _ensure_review_flag(
            quality_flags,
            seed_path="llm_findings",
            message="LLM findings seed requires manual review.",
        )

    return ReporterSeedOutcome(
        record=getattr(seed, "record", None),
        reporting_payload=reporting_payload,
        masked_seed_text=str(getattr(seed, "masked_prompt_text", "") or ""),
        warnings=warnings,
        seed_path="llm_findings",
        quality_flags=quality_flags,
        needs_review=needs_review,
        debug_metadata={
            "accepted_findings": int(getattr(seed, "accepted_findings", 0) or 0),
            "dropped_findings": int(getattr(seed, "dropped_findings", 0) or 0),
            "derived_cpt_count": int(len(list(getattr(seed, "cpt_codes", []) or []))),
        },
    )


def verify_bundle(
    bundle: ProcedureBundle,
    *,
    debug_notes: list[dict[str, Any]] | None = None,
) -> tuple[
    ProcedureBundle,
    list[MissingFieldIssue],
    list[str],
    list[str],
    list[str],
]:
    normalized = normalize_bundle(bundle)
    bundle = normalized.bundle
    if debug_notes is not None:
        debug_notes.append(
            {
                "type": "normalization",
                "notes": [
                    {
                        "kind": note.kind,
                        "path": note.path,
                        "message": note.message,
                        "source": note.source,
                    }
                    for note in normalized.notes
                ],
            }
        )
    templates = default_template_registry()
    schemas = default_schema_registry()
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    warnings = validator.apply_warn_if_rules(bundle)
    suggestions = validator.list_suggestions(bundle)
    return bundle, issues, warnings, suggestions, inference_result.notes


def render_bundle_markdown(
    bundle: ProcedureBundle,
    *,
    issues: list[MissingFieldIssue],
    warnings: list[str],
    strict: bool,
    embed_metadata: bool,
    debug_notes: list[dict[str, Any]] | None = None,
) -> tuple[str, bool]:
    templates = default_template_registry()
    schemas = default_schema_registry()
    engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
        render_style="builder",
        macro_registry=get_macro_registry(),
    )
    fallback_used = False
    try:
        structured = engine.compose_report_with_metadata(
            bundle,
            strict=strict,
            embed_metadata=embed_metadata,
            validation_issues=issues,
            warnings=warnings,
        )
    except ValueError as exc:
        message = str(exc)
        if not strict:
            raise
        if not (
            message.startswith("Style validation failed:")
            or message.startswith("Missing required fields for")
        ):
            raise
        fallback_used = True
        if debug_notes is not None:
            debug_notes.append(
                {
                    "type": "strict_fallback",
                    "error": message,
                    "action": "fallback_to_non_strict_preview",
                }
            )
        logger.warning(
            "Strict report render failed; falling back to non-strict preview",
            extra={"error": message},
        )
        structured = engine.compose_report_with_metadata(
            bundle,
            strict=False,
            embed_metadata=embed_metadata,
            validation_issues=issues,
            warnings=warnings,
        )
    return structured.text, fallback_used


def apply_reporter_completeness_uplift(record: Any, note_text: str) -> Any:
    """Best-effort uplift for reporter addendum values (age/ASA/ECOG + EBUS detail)."""
    if not note_text or record is None:
        return record

    try:
        from app.registry.schema import RegistryRecord
    except Exception:
        return record

    is_dict = isinstance(record, dict)
    if not isinstance(record, RegistryRecord) and not is_dict:
        return record

    try:
        from app.registry.deterministic_extractors import run_deterministic_extractors
        from app.registry.heuristics.linear_ebus_station_detail import (
            apply_linear_ebus_station_detail_heuristics,
        )
    except Exception:
        return record

    seed = run_deterministic_extractors(note_text)
    if not isinstance(seed, dict):
        seed = {}

    data = record.model_dump(exclude_none=False) if isinstance(record, RegistryRecord) else record
    changed = False

    age = seed.get("patient_age")
    gender = seed.get("gender")
    if age is not None or gender:
        demo = data.get("patient_demographics") or {}
        if not isinstance(demo, dict):
            demo = {}
        if age is not None and demo.get("age_years") is None:
            demo["age_years"] = age
            changed = True
        if gender and not demo.get("gender"):
            g = str(gender).strip()
            if g.lower() == "m":
                g = "Male"
            elif g.lower() == "f":
                g = "Female"
            demo["gender"] = g
            changed = True
        if changed:
            data["patient_demographics"] = demo

        patient = data.get("patient") or {}
        if not isinstance(patient, dict):
            patient = {}
        patient_changed = False
        if age is not None and patient.get("age") is None:
            patient["age"] = age
            patient_changed = True
        if gender and not patient.get("sex"):
            g = str(gender).strip()
            g_lower = g.lower()
            if g_lower in {"male", "m"}:
                g = "M"
            elif g_lower in {"female", "f"}:
                g = "F"
            else:
                g = "O"
            patient["sex"] = g
            patient_changed = True
        if patient_changed:
            data["patient"] = patient
            changed = True

    asa_val = seed.get("asa_class")
    if asa_val is not None and re.search(r"(?i)\bASA\b", note_text):
        clinical = data.get("clinical_context") or {}
        if not isinstance(clinical, dict):
            clinical = {}
        if clinical.get("asa_class") is None:
            clinical["asa_class"] = asa_val
            data["clinical_context"] = clinical
            changed = True

        risk = data.get("risk_assessment") or {}
        if not isinstance(risk, dict):
            risk = {}
        if risk.get("asa_class") is None:
            risk["asa_class"] = asa_val
            data["risk_assessment"] = risk
            changed = True

    ecog_score = seed.get("ecog_score")
    ecog_text = seed.get("ecog_text")
    if (ecog_score is not None or ecog_text) and re.search(r"(?i)\b(?:ECOG|Zubrod)\b", note_text):
        clinical = data.get("clinical_context") or {}
        if not isinstance(clinical, dict):
            clinical = {}
        if clinical.get("ecog_score") is None and not clinical.get("ecog_text"):
            if ecog_score is not None:
                clinical["ecog_score"] = ecog_score
                changed = True
            elif isinstance(ecog_text, str) and ecog_text.strip():
                clinical["ecog_text"] = ecog_text.strip()
                changed = True
        if changed:
            data["clinical_context"] = clinical

    if is_dict:
        if age is not None and data.get("patient_age") in (None, "", [], {}):
            data["patient_age"] = age
        if gender and data.get("gender") in (None, "", [], {}):
            g = str(gender).strip()
            if g.lower() == "m":
                g = "Male"
            elif g.lower() == "f":
                g = "Female"
            data["gender"] = g
        if asa_val is not None and data.get("asa_class") in (None, "", [], {}):
            data["asa_class"] = asa_val
        if ecog_score is not None and data.get("ecog_score") in (None, "", [], {}):
            data["ecog_score"] = ecog_score
        if ecog_text and data.get("ecog_text") in (None, "", [], {}):
            data["ecog_text"] = ecog_text

        try:
            from app.registry.processing.linear_ebus_stations_detail import (
                extract_linear_ebus_stations_detail,
            )

            parsed = extract_linear_ebus_stations_detail(note_text)
            if parsed:
                granular = data.get("granular_data") or {}
                if not isinstance(granular, dict):
                    granular = {}
                existing_raw = granular.get("linear_ebus_stations_detail")
                existing = (
                    [dict(item) for item in existing_raw if isinstance(item, dict)]
                    if isinstance(existing_raw, list)
                    else []
                )
                by_station: dict[str, dict[str, Any]] = {}
                order: list[str] = []
                for item in existing:
                    station = str(item.get("station") or "").strip()
                    if not station:
                        continue
                    if station not in by_station:
                        order.append(station)
                    by_station[station] = item
                for item in parsed:
                    if not isinstance(item, dict):
                        continue
                    station = str(item.get("station") or "").strip()
                    if not station:
                        continue
                    existing_item = by_station.get(station)
                    if existing_item is None:
                        by_station[station] = dict(item)
                        order.append(station)
                        continue
                    for key, value in item.items():
                        if key == "station":
                            continue
                        if value in (None, "", [], {}):
                            continue
                        if existing_item.get(key) in (None, "", [], {}):
                            existing_item[key] = value
                    by_station[station] = existing_item
                merged = [by_station[s] for s in order if s in by_station]
                if merged:
                    granular["linear_ebus_stations_detail"] = merged
                    stations = [str(item.get("station")) for item in merged if item.get("station")]
                    if stations and data.get("linear_ebus_stations") in (None, "", [], {}):
                        data["linear_ebus_stations"] = stations
                    if stations and data.get("ebus_stations_sampled") in (None, "", [], {}):
                        data["ebus_stations_sampled"] = stations
                    data["granular_data"] = granular
        except Exception:
            pass
        return data

    record_out = record
    if changed:
        try:
            record_out = RegistryRecord(**data)
        except Exception:
            record_out = record

    try:
        record_out, _ = apply_linear_ebus_station_detail_heuristics(note_text, record_out)
    except Exception:
        pass

    return record_out


def debug_template_selection(bundle: ProcedureBundle) -> dict[str, Any]:
    templates = default_template_registry()
    macros = get_macro_registry()
    procedures: list[dict[str, Any]] = []
    for proc in bundle.procedures:
        metas = templates.find_for_procedure(proc.proc_type, proc.cpt_candidates)
        procedures.append(
            {
                "proc_id": proc.proc_id or proc.schema_id,
                "proc_type": proc.proc_type,
                "cpt_candidates": [str(code) for code in (proc.cpt_candidates or [])],
                "template_ids": [meta.id for meta in metas],
                "macro_exists": macros.maybe_get(proc.proc_type) is not None,
            }
        )
    return {"type": "selection", "procedures": procedures}


def apply_seed_metadata(bundle: ProcedureBundle, metadata: dict[str, Any]) -> ProcedureBundle:
    if not metadata:
        return bundle

    def _as_text(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value)

    payload = bundle.model_dump(exclude_none=False)
    encounter = payload.get("encounter") or {}

    indication = _as_text(metadata.get("indication_text") or metadata.get("indication"))
    if indication:
        payload["indication_text"] = indication

    preop = _as_text(metadata.get("preop_diagnosis_text") or metadata.get("preop_diagnosis"))
    if preop:
        payload["preop_diagnosis_text"] = preop

    postop = _as_text(metadata.get("postop_diagnosis_text") or metadata.get("postop_diagnosis"))
    if postop:
        payload["postop_diagnosis_text"] = postop

    impression = _as_text(
        metadata.get("impression_plan") or metadata.get("plan") or metadata.get("disposition")
    )
    if impression:
        payload["impression_plan"] = impression

    attending = _as_text(metadata.get("attending"))
    if attending:
        encounter["attending"] = attending
    location = _as_text(metadata.get("location"))
    if location:
        encounter["location"] = location
    date_value = _as_text(metadata.get("date") or metadata.get("procedure_date"))
    if date_value:
        encounter["date"] = date_value
    encounter_id = _as_text(metadata.get("encounter_id"))
    if encounter_id:
        encounter["encounter_id"] = encounter_id

    payload["encounter"] = encounter
    return ProcedureBundle.model_validate(payload)


def apply_render_patch(
    bundle: ProcedureBundle,
    patch_payload: Any,
) -> ProcedureBundle:
    if not patch_payload:
        return bundle
    if isinstance(patch_payload, list):
        ops: list[dict[str, Any]] = []
        for op in patch_payload:
            if isinstance(op, BaseModel):
                ops.append(op.model_dump(exclude_none=False))
            else:
                ops.append(dict(op))
        return apply_bundle_json_patch(bundle, ops)
    return apply_bundle_patch(bundle, patch_payload)


def run_reporter_seed_pipeline(
    outcome: ReporterSeedOutcome,
    *,
    note_text: str,
    metadata: dict[str, Any] | None,
    strict: bool,
    debug_enabled: bool,
) -> ReporterSeedPipelineResult:
    debug_notes: list[dict[str, Any]] | None = [] if debug_enabled else None
    if debug_notes is not None:
        debug_notes.append(outcome.debug_note())

    seed_record_for_completeness = apply_reporter_completeness_uplift(
        outcome.record,
        note_text,
    )
    extraction_source = apply_reporter_completeness_uplift(
        outcome.reporting_payload if outcome.reporting_payload is not None else outcome.record,
        note_text,
    )

    bundle = build_procedure_bundle_from_extraction(
        extraction_source,
        source_text=outcome.masked_seed_text,
    )
    bundle = apply_seed_metadata(bundle, metadata or {})
    if not bundle.free_text_hint:
        bundle_payload = bundle.model_dump(exclude_none=False)
        bundle_payload["free_text_hint"] = outcome.masked_seed_text
        bundle = ProcedureBundle.model_validate(bundle_payload)

    bundle, issues, warnings, suggestions, notes = verify_bundle(bundle, debug_notes=debug_notes)
    warnings = list(outcome.warnings) + list(warnings or [])
    missing_field_prompts: list[dict[str, Any]] = []
    try:
        from app.registry.completeness import generate_missing_field_prompts

        completeness_prompts = generate_missing_field_prompts(seed_record_for_completeness)
        if completeness_prompts:
            missing_field_prompts = [
                {
                    "group": prompt.group,
                    "path": prompt.path,
                    "target_path": prompt.target_path,
                    "label": prompt.label,
                    "severity": prompt.severity,
                    "message": prompt.message,
                }
                for prompt in completeness_prompts
            ]
            suggestions = list(suggestions or [])
            for prompt in completeness_prompts:
                suggestions.append(
                    f"Completeness ({prompt.severity}): {prompt.label} — {prompt.message}"
                )
    except Exception:
        missing_field_prompts = []
    if debug_notes is not None:
        debug_notes.append(debug_template_selection(bundle))
    questions = build_questions(bundle, issues)
    markdown, render_fallback_used = render_bundle_markdown(
        bundle,
        issues=issues,
        warnings=warnings,
        strict=strict,
        embed_metadata=False,
        debug_notes=debug_notes,
    )
    return ReporterSeedPipelineResult(
        bundle=bundle,
        markdown=markdown,
        issues=issues,
        warnings=warnings,
        inference_notes=notes,
        suggestions=suggestions,
        questions=questions,
        missing_field_prompts=missing_field_prompts,
        debug_notes=debug_notes if debug_enabled else None,
        render_fallback_used=render_fallback_used,
    )


__all__ = [
    "BundleJsonPatchError",
    "ReporterSeedOutcome",
    "ReporterSeedPipelineResult",
    "ReporterSeedQualityFlag",
    "apply_render_patch",
    "apply_reporter_completeness_uplift",
    "apply_seed_metadata",
    "debug_template_selection",
    "render_bundle_markdown",
    "run_reporter_seed_pipeline",
    "seed_outcome_from_llm_findings_seed",
    "seed_outcome_from_registry_result",
    "verify_bundle",
]
