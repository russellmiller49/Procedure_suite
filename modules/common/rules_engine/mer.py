"""Multiple Endoscopy Rule helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

__all__ = ["Code", "MerAdjustment", "MerSummary", "apply_mer"]


@dataclass(slots=True)
class Code:
    """Simple representation of a CPT code for MER calculations."""

    cpt: str
    allowed_amount: float = 0.0
    is_add_on: bool = False


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

    primary = _determine_primary(codes)
    adjustments: list[MerAdjustment] = []
    total = 0.0

    for code in codes:
        if code.cpt == primary:
            allowed = code.allowed_amount
            role = "primary"
            reduction = 0.0
        elif code.is_add_on:
            allowed = code.allowed_amount
            role = "add_on"
            reduction = 0.0
        else:
            allowed = code.allowed_amount * 0.5
            role = "secondary"
            reduction = code.allowed_amount - allowed

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


def _determine_primary(codes: Sequence[Code]) -> str:
    non_add_on = [code for code in codes if not code.is_add_on]
    if not non_add_on:
        return codes[0].cpt
    non_add_on.sort(key=lambda c: c.allowed_amount, reverse=True)
    return non_add_on[0].cpt

