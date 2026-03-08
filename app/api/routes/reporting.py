"""Interactive reporting route handlers."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import get_registry_service
from app.api.phi_dependencies import get_phi_scrubber
from app.api.phi_redaction import apply_phi_redaction
from app.api.readiness import require_ready
from app.api.schemas import (
    QuestionsRequest,
    QuestionsResponse,
    RenderRequest,
    RenderResponse,
    SeedFromTextRequest,
    SeedFromTextResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.infra.executors import run_cpu
from app.registry.application.registry_service import RegistryService
from app.reporting import build_questions
from app.reporting.engine import build_procedure_bundle_from_extraction
from app.reporting.seed_pipeline import (
    BundleJsonPatchError,
    apply_render_patch,
    debug_template_selection,
    render_bundle_markdown,
    run_reporter_seed_pipeline,
    seed_outcome_from_llm_findings_seed,
    seed_outcome_from_registry_result,
    verify_bundle,
)

router = APIRouter(tags=["reporting"])

_ready_dep = Depends(require_ready)
_registry_service_dep = Depends(get_registry_service)
_phi_scrubber_dep = Depends(get_phi_scrubber)


@router.post("/report/verify", response_model=VerifyResponse)
async def report_verify(req: VerifyRequest) -> VerifyResponse:
    bundle = build_procedure_bundle_from_extraction(req.extraction)
    bundle, issues, warnings, suggestions, notes = verify_bundle(bundle)
    return VerifyResponse(
        bundle=bundle,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
        inference_notes=notes,
    )


@router.post("/report/questions", response_model=QuestionsResponse)
async def report_questions(req: QuestionsRequest) -> QuestionsResponse:
    bundle, issues, warnings, suggestions, notes = verify_bundle(req.bundle)
    questions = build_questions(bundle, issues)
    return QuestionsResponse(
        bundle=bundle,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
        inference_notes=notes,
        questions=questions,
    )


@router.post("/report/seed_from_text", response_model=SeedFromTextResponse)
async def report_seed_from_text(
    req: SeedFromTextRequest,
    request: Request,
    _ready: None = _ready_dep,
    registry_service: RegistryService = _registry_service_dep,
    phi_scrubber=_phi_scrubber_dep,
) -> SeedFromTextResponse:
    debug_enabled = bool(req.debug or req.include_debug)
    debug_notes: list[dict[str, Any]] | None = [] if debug_enabled else None

    redaction = apply_phi_redaction(
        req.text,
        phi_scrubber,
        already_scrubbed=bool(req.already_scrubbed),
    )
    note_text = redaction.text

    seed_strategy = os.getenv("REPORTER_SEED_STRATEGY", "registry_extract_fields").strip().lower()
    llm_strict_raw = os.getenv("REPORTER_SEED_LLM_STRICT", "0").strip().lower()
    llm_strict = llm_strict_raw in {"1", "true", "yes", "y"}

    seed_warnings: list[str] = []
    seed_outcome = None

    if debug_notes is not None:
        debug_notes.append(
            {
                "type": "seed_strategy",
                "strategy": seed_strategy,
                "already_scrubbed": bool(req.already_scrubbed),
                "redaction": {
                    "was_scrubbed": bool(redaction.was_scrubbed),
                    "entity_count": int(redaction.entity_count),
                    "warning": redaction.warning,
                },
            }
        )

    if seed_strategy == "llm_findings":
        try:
            from app.reporting.llm_findings import (
                ReporterFindingsError,
                build_record_payload_for_reporting,
                seed_registry_record_from_llm_findings,
            )

            seed = seed_registry_record_from_llm_findings(note_text)
            seed_warnings.extend(list(seed.warnings or []))
            seed_outcome = seed_outcome_from_llm_findings_seed(
                seed,
                reporting_payload=build_record_payload_for_reporting(seed),
            )
        except ReporterFindingsError as exc:
            seed_warnings.append(
                f"REPORTER_SEED_FALLBACK: llm_findings_failed ({type(exc).__name__})"
            )
            if llm_strict:
                raise HTTPException(status_code=502, detail="LLM findings seeding failed") from exc
            seed_strategy = "registry_extract_fields"
        except Exception as exc:  # noqa: BLE001
            seed_warnings.append(
                f"REPORTER_SEED_FALLBACK: llm_findings_failed ({type(exc).__name__})"
            )
            if llm_strict:
                raise HTTPException(status_code=502, detail="LLM findings seeding failed") from exc
            seed_strategy = "registry_extract_fields"

    extraction_result = None
    if seed_strategy != "llm_findings":
        extraction_result = await run_cpu(request.app, registry_service.extract_fields, note_text)
        seed_outcome = seed_outcome_from_registry_result(
            extraction_result,
            masked_seed_text=note_text,
        )

    if seed_outcome is None:
        raise HTTPException(status_code=500, detail="Reporter seed outcome was not created")

    if seed_warnings:
        seed_outcome.warnings = [*seed_warnings, *list(seed_outcome.warnings or [])]

    pipeline_result = run_reporter_seed_pipeline(
        seed_outcome,
        note_text=note_text,
        metadata=req.metadata,
        strict=req.strict,
        debug_enabled=debug_enabled,
    )
    return SeedFromTextResponse(
        bundle=pipeline_result.bundle,
        markdown=pipeline_result.markdown,
        issues=pipeline_result.issues,
        warnings=pipeline_result.warnings,
        inference_notes=pipeline_result.inference_notes,
        suggestions=pipeline_result.suggestions,
        questions=pipeline_result.questions,
        missing_field_prompts=pipeline_result.missing_field_prompts,
        debug_notes=(list(debug_notes or []) + list(pipeline_result.debug_notes or []))
        if debug_enabled
        else None,
    )


@router.post("/report/render", response_model=RenderResponse)
async def report_render(req: RenderRequest) -> RenderResponse:
    debug_enabled = bool(req.debug or req.include_debug)
    debug_notes: list[dict[str, Any]] | None = [] if debug_enabled else None

    bundle = req.bundle
    try:
        bundle = apply_render_patch(bundle, req.patch)
    except BundleJsonPatchError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    bundle, issues, warnings, suggestions, notes = verify_bundle(bundle, debug_notes=debug_notes)
    if debug_notes is not None:
        debug_notes.append(debug_template_selection(bundle))
    markdown, _render_fallback_used = render_bundle_markdown(
        bundle,
        issues=issues,
        warnings=warnings,
        strict=req.strict,
        embed_metadata=req.embed_metadata,
        debug_notes=debug_notes,
    )
    return RenderResponse(
        bundle=bundle,
        markdown=markdown,
        issues=issues,
        warnings=warnings,
        inference_notes=notes,
        suggestions=suggestions,
        debug_notes=debug_notes if debug_enabled else None,
    )


def _verify_bundle(*args, **kwargs):
    return verify_bundle(*args, **kwargs)


def _render_bundle_markdown(*args, **kwargs):
    markdown, _fallback_used = render_bundle_markdown(*args, **kwargs)
    return markdown


def _debug_template_selection(*args, **kwargs):
    return debug_template_selection(*args, **kwargs)


def _apply_render_patch(bundle, req):
    return apply_render_patch(bundle, req.patch)


__all__ = ["router"]
