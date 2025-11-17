"""Pydantic data structures for the coder pipeline."""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from modules.common.spans import Span

__all__ = [
    "DetectedIntent",
    "CodeDecision",
    "BundleDecision",
    "CoderOutput",
]


class DetectedIntent(BaseModel):
    """Represents an intermediate intent inferred from the note."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    intent: str
    value: str | None = None
    payload: dict[str, Any] | None = None
    confidence: float | None = None
    evidence: List[Span] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)


class CodeDecision(BaseModel):
    """Finalized CPT decision including bundles and MER metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cpt: str
    description: str
    modifiers: list[str] = Field(default_factory=list)
    rationale: str = ""
    evidence: List[Span] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    mer_role: str | None = None
    mer_allowed: float | None = None
    confidence: float = 0.0
    rule_trace: List[str] = Field(default_factory=list)


class BundleDecision(BaseModel):
    """Explains how bundling/NCCI edits affected the code set."""

    pair: tuple[str, str]
    action: str
    reason: str
    rule: str | None = None


class CoderOutput(BaseModel):
    """Top-level payload returned by the coder pipeline."""

    codes: list[CodeDecision]
    intents: list[DetectedIntent] = Field(default_factory=list)
    mer_summary: dict[str, Any] | None = None
    ncci_actions: list[BundleDecision] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    version: str = "0.1.0"
