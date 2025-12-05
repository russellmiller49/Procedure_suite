"""Base Pydantic schemas for the FastAPI integration layer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from modules.coder.schema import CoderOutput
from modules.common.spans import Span
from modules.registry.schema import RegistryRecord
from proc_report import BundlePatch, MissingFieldIssue, ProcedureBundle


class CoderRequest(BaseModel):
    note: str
    allow_weak_sedation_docs: bool = False
    explain: bool = False
    locality: str = "00"
    setting: str = "facility"
    mode: str | None = None


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


__all__ = [
    "CoderRequest",
    "CoderResponse",
    "KnowledgeMeta",
    "QARunRequest",
    "RegistryRequest",
    "RegistryResponse",
    "RenderRequest",
    "RenderResponse",
    "VerifyRequest",
    "VerifyResponse",
]
