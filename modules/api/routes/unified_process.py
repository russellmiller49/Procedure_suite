"""Unified (Registry + Coder) Process Endpoint.

This module provides the `/api/v1/process` endpoint which combines:
1. PHI Scrubbing (optional)
2. Hybrid-first Registry Extraction (RegistryService)
   - CPT Coding (SmartHybridOrchestrator)
   - Registry Field Extraction (RegistryEngine)
3. Response normalization for the UI
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from modules.api.adapters.response_adapter import build_v3_evidence_payload
from modules.api.dependencies import get_coding_service, get_registry_service
from modules.api.phi_dependencies import get_phi_scrubber
from modules.api.phi_redaction import apply_phi_redaction
from modules.api.readiness import require_ready
from modules.api.schemas import (
    CodeSuggestionSummary,
    UnifiedProcessRequest,
    UnifiedProcessResponse,
)
from modules.coder.application.coding_service import CodingService
from modules.coder.phi_gating import is_phi_review_required
from modules.common.exceptions import LLMError
from modules.infra.executors import run_cpu
from modules.registry.application.registry_service import (
    RegistryExtractionResult,
    RegistryService,
)

router = APIRouter(tags=["process"])
logger = logging.getLogger(__name__)
_ready_dep = Depends(require_ready)
_registry_service_dep = Depends(get_registry_service)
_coding_service_dep = Depends(get_coding_service)
_phi_scrubber_dep = Depends(get_phi_scrubber)


@router.post(
    "/v1/process",
    response_model=UnifiedProcessResponse,
    response_model_exclude_none=True,
    summary="Unified PHI-safe extraction and coding pipeline",
)
async def unified_process(
    payload: UnifiedProcessRequest,
    request: Request,
    response: Response,
    _ready: None = _ready_dep,
    registry_service: RegistryService = _registry_service_dep,
    coding_service: CodingService = _coding_service_dep,
    phi_scrubber=_phi_scrubber_dep,
) -> UnifiedProcessResponse:
    """Run the unified extraction pipeline."""
    response.headers["X-Process-Route"] = "router"
    start_time = time.time()

    # 1. PHI Redaction (if not already scrubbed)
    if payload.already_scrubbed:
        note_text = payload.note
    else:
        redaction = apply_phi_redaction(payload.note, phi_scrubber)
        note_text = redaction.text

    # 2. Run Registry Extraction (includes CPT Coding via Hybrid Orchestrator)
    try:
        result: RegistryExtractionResult = await run_cpu(
            request.app, registry_service.extract_fields, note_text
        )
    except httpx.HTTPStatusError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            retry_after = exc.response.headers.get("Retry-After") or "10"
            raise HTTPException(
                status_code=503,
                detail="Upstream LLM rate limited",
                headers={"Retry-After": str(retry_after)},
            ) from exc
        raise
    except LLMError as exc:
        if "429" in str(exc):
            raise HTTPException(
                status_code=503,
                detail="Upstream LLM rate limited",
                headers={"Retry-After": "10"},
            ) from exc
        raise
    except ValueError as exc:
        logger.error("Unified process configuration error: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unified process failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal processing error") from exc

    from config.settings import CoderSettings
    from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta

    record = result.record
    if record is None:
        from modules.registry.schema import RegistryRecord

        record = RegistryRecord.model_validate(result.mapped_fields)

    derived_codes, derived_rationales, derivation_warnings = derive_all_codes_with_meta(record)
    codes = list(result.cpt_codes or derived_codes)
    code_rationales = getattr(result, "code_rationales", None) or derived_rationales

    suggestions: list[CodeSuggestionSummary] = []
    base_confidence = 0.95 if result.coder_difficulty == "HIGH_CONF" else 0.80

    for code in codes:
        proc_info = coding_service.kb_repo.get_procedure_info(code)
        description = proc_info.description if proc_info else ""
        rationale = code_rationales.get(code, "")

        if result.needs_manual_review:
            review_flag = "required"
        elif result.audit_warnings:
            review_flag = "recommended"
        else:
            review_flag = "optional"

        suggestions.append(
            CodeSuggestionSummary(
                code=code,
                description=description,
                confidence=base_confidence,
                rationale=rationale,
                review_flag=review_flag,
            )
        )

    total_work_rvu = None
    estimated_payment = None
    per_code_billing: list[dict[str, Any]] = []

    if payload.include_financials and codes:
        settings = CoderSettings()
        conversion_factor = settings.cms_conversion_factor
        total_work = 0.0
        total_payment = 0.0
        units_by_code: dict[str, int] = {}

        billing = getattr(record, "billing", None)
        cpt_items = []
        if isinstance(billing, dict):
            cpt_items = billing.get("cpt_codes") or []
        else:
            cpt_items = getattr(billing, "cpt_codes", None) or []
        if isinstance(cpt_items, list):
            for item in cpt_items:
                if not isinstance(item, dict):
                    continue
                code = str(item.get("code") or "").strip().lstrip("+")
                if not code:
                    continue
                try:
                    units_by_code[code] = int(item.get("units") or 1)
                except (TypeError, ValueError):
                    units_by_code[code] = 1

        for code in codes:
            proc_info = coding_service.kb_repo.get_procedure_info(code)
            if proc_info:
                work_rvu = proc_info.work_rvu
                total_rvu = proc_info.total_facility_rvu
                units = int(units_by_code.get(code, 1) or 1)
                payment = total_rvu * conversion_factor * units

                total_work += work_rvu * units
                total_payment += payment

                per_code_billing.append(
                    {
                        "cpt_code": code,
                        "description": proc_info.description,
                        "units": units,
                        "work_rvu": work_rvu * units,
                        "total_facility_rvu": total_rvu * units,
                        "facility_payment": round(payment, 2),
                    }
                )

        total_work_rvu = round(total_work, 2)
        estimated_payment = round(total_payment, 2)

    all_warnings: list[str] = []
    all_warnings.extend(result.warnings or [])
    all_warnings.extend(result.audit_warnings or [])
    all_warnings.extend(derivation_warnings)

    deduped_warnings: list[str] = []
    seen_warnings: set[str] = set()
    for warning in all_warnings:
        if warning in seen_warnings:
            continue
        seen_warnings.add(warning)
        deduped_warnings.append(warning)
    all_warnings = deduped_warnings

    evidence_payload = build_v3_evidence_payload(record=record, codes=codes)
    if payload.explain is False and not evidence_payload:
        evidence_payload = {}

    needs_manual_review = result.needs_manual_review
    if is_phi_review_required():
        review_status = "pending_phi_review"
        needs_manual_review = True
    elif needs_manual_review:
        review_status = "unverified"
    else:
        review_status = "finalized"

    processing_time_ms = (time.time() - start_time) * 1000

    return UnifiedProcessResponse(
        registry=record.model_dump(exclude_none=True),
        evidence=evidence_payload,
        cpt_codes=codes,
        suggestions=suggestions,
        total_work_rvu=total_work_rvu,
        estimated_payment=estimated_payment,
        per_code_billing=per_code_billing,
        pipeline_mode="extraction_first",
        coder_difficulty=result.coder_difficulty,
        needs_manual_review=needs_manual_review,
        audit_warnings=all_warnings,
        validation_errors=result.validation_errors or [],
        kb_version=coding_service.kb_repo.version,
        policy_version="extraction_first_v1",
        processing_time_ms=round(processing_time_ms, 2),
        review_status=review_status,
    )
