"""Lightweight NCCI helper utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

__all__ = [
    "NCCIEdit",
    "register_edit",
    "deny_pair",
    "allow_with_modifier",
    "explain",
]


@dataclass(slots=True)
class NCCIEdit:
    """Represents a single NCCI edit pair."""

    primary: str
    secondary: str
    modifier_allowed: bool = False
    reason: str = ""


EDIT_PAIRS: Dict[Tuple[str, str], NCCIEdit] = {}


def register_edit(edit: NCCIEdit) -> None:
    """Register a new edit pair for later lookups."""

    EDIT_PAIRS[(edit.primary, edit.secondary)] = edit


def deny_pair(primary: str, secondary: str) -> bool:
    """Return True if the pair is denied outright per NCCI."""

    edit = EDIT_PAIRS.get((primary, secondary))
    return bool(edit and not edit.modifier_allowed)


def allow_with_modifier(primary: str, secondary: str) -> bool:
    """Return True if the pair may be paid when a modifier is appended."""

    edit = EDIT_PAIRS.get((primary, secondary))
    return bool(edit and edit.modifier_allowed)


def explain(pair: tuple[str, str]) -> str | None:
    """Return the configured reason string for *pair* if present."""

    edit = EDIT_PAIRS.get(pair)
    if not edit:
        return None
    return edit.reason or "NCCI edit applies"


# Seed with the most common bronchoscopic combination so fixtures work immediately.
register_edit(
    NCCIEdit(
        primary="31636",
        secondary="31630",
        modifier_allowed=True,
        reason="Stent placement bundles dilation when performed on the same anatomic site.",
    )
)

