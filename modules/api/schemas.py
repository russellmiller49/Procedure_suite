"""Pydantic schemas for the FastAPI integration layer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from modules.coder.schema import CoderOutput
from modules.common.spans import Span
from modules.registry.schema import RegistryRecord
from modules.reporter.schema import StructuredReport


class CoderRequest(BaseModel):
    note: str
    allow_weak_sedation_docs: bool = False
    explain: bool = False


CoderResponse = CoderOutput


class RegistryRequest(BaseModel):
    note: str
    explain: bool = False


class RegistryResponse(RegistryRecord):
    evidence: dict[str, list[Span]] = Field(default_factory=dict)


class ReporterRequest(BaseModel):
    note: str
    template: Literal["bronchoscopy", "pleural", "blvr"] = "bronchoscopy"


class ReporterResponse(BaseModel):
    report: str
    struct: StructuredReport


class KnowledgeMeta(BaseModel):
    version: str
    sha256: str


__all__ = [
    "CoderRequest",
    "CoderResponse",
    "RegistryRequest",
    "RegistryResponse",
    "ReporterRequest",
    "ReporterResponse",
    "KnowledgeMeta",
]
