"""Strict validator for registry self-correction patches."""

from __future__ import annotations

import os
from typing import Any

ALLOWED_PATHS: set[str] = {
    # Performed flags
    "/procedures_performed/bal/performed",
    "/procedures_performed/brushings/performed",
    "/procedures_performed/transbronchial_biopsy/performed",
    "/procedures_performed/transbronchial_cryobiopsy/performed",
    "/procedures_performed/tbna_conventional/performed",
    "/procedures_performed/linear_ebus/performed",
    "/procedures_performed/radial_ebus/performed",
    "/procedures_performed/navigational_bronchoscopy/performed",
    "/pleural_procedures/ipc/performed",
    "/pleural_procedures/thoracentesis/performed",
    "/pleural_procedures/chest_tube/performed",
    # Add other safe fields as needed
}


def validate_proposal(
    proposal: Any,
    raw_note_text: str,
    *,
    max_patch_ops: int | None = None,
) -> tuple[bool, str]:
    """Return (is_valid, reason)."""

    quote = getattr(proposal, "evidence_quote", "")
    if not isinstance(quote, str) or not quote.strip():
        return False, "Missing evidence quote"
    quote = quote.strip()

    text = raw_note_text or ""
    if quote not in text:
        return False, f"Quote not found verbatim in text: '{quote[:50]}...'"

    patches = getattr(proposal, "json_patch", [])
    if not isinstance(patches, list) or not patches:
        return False, "Empty patch"

    if max_patch_ops is None:
        max_patch_ops = _env_int("REGISTRY_SELF_CORRECT_MAX_PATCH_OPS", 5)

    if len(patches) > max_patch_ops:
        return False, f"Patch too large: {len(patches)} ops (max {max_patch_ops})"

    allowed_paths = _allowed_paths_from_env(default=ALLOWED_PATHS)

    for op in patches:
        if not isinstance(op, dict):
            return False, "Patch operation must be an object"

        path = op.get("path")
        if path not in allowed_paths:
            return False, f"Path not allowed: {path}"

        verb = op.get("op")
        if verb not in ("add", "replace"):
            return False, f"Op not allowed: {verb}"

    return True, "Valid"


def _allowed_paths_from_env(*, default: set[str]) -> set[str]:
    raw = os.getenv("REGISTRY_SELF_CORRECT_ALLOWLIST", "")
    if not raw.strip():
        return set(default)
    parsed = {p.strip() for p in raw.split(",") if p.strip()}
    return parsed or set(default)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


__all__ = ["ALLOWED_PATHS", "validate_proposal"]

