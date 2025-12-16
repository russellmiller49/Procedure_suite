"""Base Pydantic schemas for the FastAPI integration layer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from modules.coder.schema import CoderOutput
from modules.common.spans import Span
from modules.registry.schema import RegistryRecord
from modules.reporting import BundlePatch, MissingFieldIssue, ProcedureBundle


class CoderRequest(BaseModel):
    note: str
    allow_weak_sedation_docs: bool = False
    explain: bool = False
    locality: str = "00"
    setting: str = "facility"
    mode: str | None = None
    use_ml_first: bool = Field(
        default=False,
        description=(
            "If True, use ML-first hybrid pipeline (SmartHybridOrchestrator) "
            "with ternary classification (HIGH_CONF/GRAY_ZONE/LOW_CONF). "
            "If False, use legacy rule+LLM union merge."
        ),
    )


class HybridPipelineMetadata(BaseModel):
    """Metadata from the ML-first hybrid pipeline."""

    difficulty: str = Field(
        "", description="ML case difficulty: high_confidence, gray_zone, or low_confidence"
    )
    source: str = Field(
        "", description="Decision source: ml_rules_fastpath or hybrid_llm_fallback"
    )
    llm_used: bool = Field(False, description="Whether LLM was called for this case")
    ml_candidates: list[str] = Field(
        default_factory=list, description="CPT codes suggested by ML model"
    )
    fallback_reason: str | None = Field(
        None, description="Why LLM fallback was triggered (if applicable)"
    )
    rules_error: str | None = Field(
        None, description="Rules validation error message (if any)"
    )


CoderResponse = CoderOutput


class RegistryRequest(BaseModel):
    note: str
    explain: bool = False


class RegistryResponse(RegistryRecord):
    evidence: dict[str, list[Span]] = Field(default_factory=dict)


class VerifyRequest(BaseModel):
    extraction: dict[str, Any]
    strict: bool = False


class VerifyResponse(BaseModel):
    bundle: ProcedureBundle
    issues: list[MissingFieldIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    inference_notes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class RenderRequest(BaseModel):
    bundle: ProcedureBundle
    patch: BundlePatch
    embed_metadata: bool = False
    strict: bool = False


class RenderResponse(BaseModel):
    bundle: ProcedureBundle
    markdown: str | None
    issues: list[MissingFieldIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    inference_notes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class KnowledgeMeta(BaseModel):
    version: str
    sha256: str


class QARunRequest(BaseModel):
    """Request schema for QA sandbox endpoint."""

    note_text: str
    modules_run: str = "all"  # "reporter", "coder", "registry", or "all"
    procedure_type: str | None = None


class UnifiedProcessRequest(BaseModel):
    """Request schema for unified registry + coder endpoint (extraction-first)."""

    note: str = Field(..., description="The procedure note text to process")
    locality: str = Field("00", description="Geographic locality for RVU calculations")
    include_financials: bool = Field(True, description="Whether to include RVU/payment info")
    explain: bool = Field(False, description="Include extraction evidence/rationales")


class CodeSuggestionSummary(BaseModel):
    """Simplified code suggestion for unified response."""

    code: str
    description: str
    confidence: float
    rationale: str = ""
    review_flag: str = "optional"


class UnifiedProcessResponse(BaseModel):
    """Response schema combining registry extraction and CPT coding."""

    # Registry output
    registry: dict[str, Any] = Field(default_factory=dict, description="Extracted registry fields")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Extraction evidence spans")

    # Coder output
    cpt_codes: list[str] = Field(default_factory=list, description="Derived CPT codes")
    suggestions: list[CodeSuggestionSummary] = Field(
        default_factory=list, description="Code suggestions with confidence"
    )

    # Financials (optional)
    total_work_rvu: float | None = None
    estimated_payment: float | None = None
    per_code_billing: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    pipeline_mode: str = "extraction_first"
    coder_difficulty: str = ""
    needs_manual_review: bool = False
    audit_warnings: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)

    # Versions
    kb_version: str = ""
    policy_version: str = ""
    processing_time_ms: float = 0.0


__all__ = [
    "CoderRequest",
    "CoderResponse",
    "CodeSuggestionSummary",
    "HybridPipelineMetadata",
    "KnowledgeMeta",
    "QARunRequest",
    "RegistryRequest",
    "RegistryResponse",
    "RenderRequest",
    "RenderResponse",
    "UnifiedProcessRequest",
    "UnifiedProcessResponse",
    "VerifyRequest",
    "VerifyResponse",
]
