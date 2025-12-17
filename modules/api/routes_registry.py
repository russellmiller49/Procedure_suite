"""FastAPI Router for Registry Extraction Service.

This router provides endpoints for:
- Hybrid-first registry field extraction from procedure notes

Integration:
    Add to your main FastAPI app:

    from modules.api.routes_registry import router as registry_extract_router
    app.include_router(registry_extract_router)
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from modules.api.dependencies import get_registry_service
from modules.api.readiness import require_ready
from modules.infra.executors import run_cpu
from modules.common.exceptions import LLMError
from modules.registry.application.registry_service import (
    RegistryService,
    RegistryExtractionResult,
)

logger = logging.getLogger(__name__)


def _prune_none(obj: Any) -> Any:
    """Recursively remove None values from dict/list structures."""
    if isinstance(obj, dict):
        cleaned: dict[str, Any] = {}
        for key, value in obj.items():
            if value is None:
                continue
            cleaned[key] = _prune_none(value)
        return cleaned
    if isinstance(obj, list):
        return [_prune_none(item) for item in obj if item is not None]
    return obj


# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/api/registry",
    tags=["registry"],
    responses={
        500: {"description": "Internal server error"},
    },
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class RegistryExtractRequest(BaseModel):
    """Request payload for registry field extraction."""

    note_text: str = Field(
        ...,
        description="The raw procedure note text to extract registry fields from",
        min_length=10,
    )


class RegistryExtractResponse(BaseModel):
    """Response from registry field extraction.

    Contains extracted registry record, CPT codes, validation metadata,
    and ML hybrid audit results.
    """

    record: dict[str, Any] = Field(
        ...,
        description="Extracted registry record fields",
    )
    cpt_codes: list[str] = Field(
        ...,
        description="CPT codes identified by the hybrid coder",
    )
    coder_difficulty: str = Field(
        ...,
        description="Case difficulty: HIGH_CONF, GRAY_ZONE, or LOW_CONF",
    )
    coder_source: str = Field(
        ...,
        description="Source of codes: ml_rules_fastpath or hybrid_llm_fallback",
    )
    mapped_fields: dict[str, Any] = Field(
        ...,
        description="Registry fields derived from CPT code mapping",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking warnings about the extraction",
    )
    needs_manual_review: bool = Field(
        default=False,
        description=(
            "True when ML registry predictions conflict with CPT-derived fields "
            "or other validation issues require human review"
        ),
    )
    validation_errors: list[str] = Field(
        default_factory=list,
        description="Validation errors found during CPT-registry reconciliation",
    )
    audit_warnings: list[str] = Field(
        default_factory=list,
        description=(
            "List of human-readable warnings describing ML vs CPT discrepancies. "
            "These indicate procedures the ML model detected with high confidence "
            "that were not captured by the CPT-derived flags."
        ),
    )

    @classmethod
    def from_domain(cls, result: RegistryExtractionResult) -> "RegistryExtractResponse":
        """Convert domain result to API response.

        Args:
            result: RegistryExtractionResult from the service layer.

        Returns:
            RegistryExtractResponse suitable for JSON serialization.
        """
        record = _prune_none(result.record.model_dump(exclude_none=True))
        mapped_fields = _prune_none(result.mapped_fields)

        # Output shaping helpers (keep PHI-safe; no response text logging)
        from modules.api.normalization import simplify_billing_cpt_codes
        from modules.registry.summarize import add_procedure_summaries

        simplify_billing_cpt_codes(record)
        add_procedure_summaries(record)

        return cls(
            record=record,
            cpt_codes=result.cpt_codes,
            coder_difficulty=result.coder_difficulty,
            coder_source=result.coder_source,
            mapped_fields=mapped_fields,
            warnings=result.warnings,
            needs_manual_review=result.needs_manual_review,
            validation_errors=result.validation_errors,
            audit_warnings=result.audit_warnings,
        )


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/extract",
    response_model=RegistryExtractResponse,
    response_model_exclude_none=True,
    summary="Extract registry fields from procedure note",
    description=(
        "Runs the hybrid-first extraction pipeline:\n"
        "1. SmartHybridOrchestrator determines CPT codes (ML → Rules → LLM fallback)\n"
        "2. CPT codes are mapped to registry boolean flags\n"
        "3. RegistryEngine extracts structured fields from note text\n"
        "4. CPT-registry consistency checks are performed\n"
        "5. Returns combined result with manual review flags if needed"
    ),
)
async def extract_registry_fields(
    payload: RegistryExtractRequest,
    request: Request,
    _ready: None = Depends(require_ready),
    registry_service: RegistryService = Depends(get_registry_service),
) -> RegistryExtractResponse:
    """
    Extract registry fields from a procedure note using hybrid-first pipeline.

    This endpoint uses the SmartHybridOrchestrator for ML-first CPT coding,
    maps codes to registry fields, extracts structured data via RegistryEngine,
    and performs validation to flag cases needing manual review.

    Args:
        payload: Request containing the procedure note text.
        registry_service: Injected RegistryService instance.

    Returns:
        RegistryExtractResponse with extracted fields and validation metadata.

    Raises:
        HTTPException: If extraction fails due to missing orchestrator or errors.
    """
    try:
        result = await run_cpu(request.app, registry_service.extract_fields, payload.note_text)
        return RegistryExtractResponse.from_domain(result)

    except ValueError as e:
        # ValueError raised when hybrid_orchestrator is not configured
        logger.error(f"Registry extraction configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )

    except Exception as e:
        if isinstance(e, httpx.HTTPStatusError) and e.response is not None and e.response.status_code == 429:
            retry_after = e.response.headers.get("Retry-After") or "10"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Upstream LLM rate limited",
                headers={"Retry-After": str(retry_after)},
            )
        if isinstance(e, LLMError) and "429" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Upstream LLM rate limited",
                headers={"Retry-After": "10"},
            )
        logger.error(f"Registry extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registry extraction failed: {str(e)}",
        )
