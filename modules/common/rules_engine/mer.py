"""Multiple Endoscopy Rule helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from modules.common.knowledge import get_knowledge

__all__ = ["Code", "MerAdjustment", "MerSummary", "apply_mer"]


@dataclass(slots=True)
class Code:
    """Simple representation of a CPT code for MER calculations."""

    cpt: str
    allowed_amount: float | None = None
    is_add_on: bool | None = None


@dataclass(slots=True)
class MerAdjustment:
    """Computed MER adjustment for a single CPT code."""

    cpt: str
    role: str
    allowed: float
    reduction: float


@dataclass(slots=True)
class MerSummary:
    """Aggregate MER result."""

    primary_code: str | None
    adjustments: list[MerAdjustment]
    total_allowed: float


def apply_mer(codes: Sequence[Code]) -> MerSummary:
    """Apply the Multiple Endoscopy Rule to *codes*."""

    if not codes:
        return MerSummary(primary_code=None, adjustments=[], total_allowed=0.0)

    config = _load_mer_config()
    add_on_codes = config["add_on_codes"]
    primary = _determine_primary(codes, config)
    adjustments: list[MerAdjustment] = []
    total = 0.0

    for code in codes:
        allowed_amount = code.allowed_amount
        if allowed_amount in (None, 0.0):
            allowed_amount = config["allowed_amounts"].get(code.cpt, 150.0)
        is_add_on = _is_add_on(code, add_on_codes)

        if code.cpt == primary:
            allowed = allowed_amount
            role = "primary"
            reduction = 0.0
        elif is_add_on:
            allowed = allowed_amount
            role = "add_on"
            reduction = 0.0
        else:
            allowed = allowed_amount * 0.5
            role = "secondary"
            reduction = allowed_amount - allowed

        total += allowed
        adjustments.append(
            MerAdjustment(
                cpt=code.cpt,
                role=role,
                allowed=allowed,
                reduction=reduction,
            )
        )

    return MerSummary(primary_code=primary, adjustments=adjustments, total_allowed=total)


def _determine_primary(codes: Sequence[Code], config: dict[str, object]) -> str:
    add_on_codes = config.get("add_on_codes", set())
    non_add_on = [code for code in codes if not _is_add_on(code, add_on_codes)]
    if not non_add_on:
        return codes[0].cpt
    non_add_on.sort(key=lambda c: c.allowed_amount or 0.0, reverse=True)
    return non_add_on[0].cpt


def _is_add_on(code: Code, add_on_codes: set[str]) -> bool:
    if code.is_add_on is not None:
        return code.is_add_on
    return code.cpt in add_on_codes or code.cpt.startswith("+")


_MER_CACHE: dict[str, object] | None = None
_KNOWLEDGE_REF: dict | None = None


def _load_mer_config() -> dict[str, object]:
    global _MER_CACHE, _KNOWLEDGE_REF
    knowledge = get_knowledge()
    if _MER_CACHE is not None and knowledge is _KNOWLEDGE_REF:
        return _MER_CACHE
    mer_section = knowledge.get("mer", {})
    config = {
        "allowed_amounts": {k: float(v) for k, v in mer_section.get("allowed_amounts", {}).items()},
        "add_on_codes": set(mer_section.get("add_on_codes", [])),
    }
    _MER_CACHE = config
    _KNOWLEDGE_REF = knowledge
    return config
