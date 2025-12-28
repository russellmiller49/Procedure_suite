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
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from modules.api.dependencies import get_registry_service
from modules.api.phi_dependencies import get_phi_scrubber
from modules.api.phi_redaction import apply_phi_redaction
from modules.api.readiness import require_ready
from modules.api.schemas import (
    CodeSuggestionSummary,
    UnifiedProcessRequest,
    UnifiedProcessResponse,
)
from modules.infra.executors import run_cpu
from modules.registry.application.registry_service import (
    RegistryExtractionResult,
    RegistryService,
)

router = APIRouter(tags=["process"])
logger = logging.getLogger(__name__)


def _to_code_suggestion(cpt: str, difficulty: str) -> CodeSuggestionSummary:
    """Helper to create a basic CodeSuggestionSummary from a CPT code."""
    # NOTE: To get real descriptions/confidence, we'd need to fetch from KB or
    # parse from HybridCoderResult metadata. For now, we populate basics
    # to satisfy the UI contract.
    return CodeSuggestionSummary(
        code=cpt,
        description=f"CPT {cpt}",  # Placeholder; UI might enrich this
        confidence=1.0 if difficulty == "HIGH_CONF" else 0.8,
        rationale="Derived from hybrid pipeline",
    )


@router.post(
    "/v1/process",
    response_model=UnifiedProcessResponse,
    response_model_exclude_none=True,
    summary="Unified PHI-safe extraction and coding pipeline",
)
async def unified_process(
    payload: UnifiedProcessRequest,
    request: Request,
    _ready: None = Depends(require_ready),
    registry_service: RegistryService = Depends(get_registry_service),
    phi_scrubber=Depends(get_phi_scrubber),
) -> UnifiedProcessResponse:
    """Run the unified extraction pipeline."""
    # 1. PHI Redaction (if not already scrubbed)
    if payload.already_scrubbed:
        note_text = payload.note
    else:
        redaction = apply_phi_redaction(payload.note, phi_scrubber)
        note_text = redaction.text

    # 2. Run Registry Extraction (includes CPT Coding via Hybrid Orchestrator)
    try:
        # We assume registry_service is configured with a hybrid_orchestrator
        # so extracting fields will also yield CPT codes.
        result: RegistryExtractionResult = await run_cpu(
            request.app, registry_service.extract_fields, note_text
        )
    except ValueError as e:
        logger.error(f"Unified process configuration error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unified process failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal processing error")

    # 3. Shape Response
    # Convert extracted record to dict, pruning Nones
    registry_data = result.record.model_dump(exclude_none=True)
    
    # Transform CPT codes to suggestions
    suggestions = [
        _to_code_suggestion(cpt, result.coder_difficulty)
        for cpt in result.cpt_codes
    ]

    return UnifiedProcessResponse(
        registry=registry_data,
        evidence={},  # Evidence extraction can be complex; omitting for now unless strictly needed
        cpt_codes=result.cpt_codes,
        suggestions=suggestions,
        pipeline_mode="extraction_first", # or "hybrid_registry"
        coder_difficulty=result.coder_difficulty,
        needs_manual_review=result.needs_manual_review,
        audit_warnings=result.audit_warnings,
        validation_errors=result.validation_errors,
    )
