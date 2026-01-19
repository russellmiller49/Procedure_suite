"""Strict validator for registry self-correction patches."""

from __future__ import annotations

import os
import re
from typing import Any

ALLOWED_PATHS: set[str] = {
    # Performed flags
    "/procedures_performed/bal/performed",
    "/procedures_performed/brushings/performed",
    "/procedures_performed/mechanical_debulking/performed",
    "/procedures_performed/transbronchial_biopsy/performed",
    "/procedures_performed/transbronchial_cryobiopsy/performed",
    "/procedures_performed/tbna_conventional/performed",
    "/procedures_performed/linear_ebus/performed",
    "/procedures_performed/radial_ebus/performed",
    "/procedures_performed/navigational_bronchoscopy/performed",
    "/procedures_performed/airway_dilation/performed",
    "/procedures_performed/airway_stent/performed",
    "/procedures_performed/foreign_body_removal/performed",
    "/procedures_performed/eus_b/performed",
    "/pleural_procedures/ipc/performed",
    "/pleural_procedures/thoracentesis/performed",
    "/pleural_procedures/chest_tube/performed",
    # Add other safe fields as needed
}

ALLOWED_PATH_PREFIXES: set[str] = {
    "/procedures_performed/navigational_bronchoscopy",
    "/procedures_performed/tbna_conventional",
    "/procedures_performed/brushings",
    "/procedures_performed/mechanical_debulking",
    "/procedures_performed/transbronchial_cryobiopsy",
    "/procedures_performed/thermal_ablation",
    "/procedures_performed/peripheral_ablation",
    "/procedures_performed/airway_dilation",
    "/procedures_performed/airway_stent",
    "/procedures_performed/foreign_body_removal",
    "/procedures_performed/eus_b",
    "/pleural_procedures/ipc",
    "/pleural_procedures/thoracentesis",
    "/pleural_procedures/chest_tube",
    "/granular_data",
}

_WS_RE = re.compile(r"\s+")


def _normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    return _WS_RE.sub(" ", text).strip()


def validate_proposal(
    proposal: Any,
    raw_note_text: str,
    *,
    extraction_text: str | None = None,
    max_patch_ops: int | None = None,
) -> tuple[bool, str]:
    """Return (is_valid, reason)."""

    quote = getattr(proposal, "evidence_quote", "")
    if not isinstance(quote, str) or not quote.strip():
        return False, "Missing evidence quote"
    quote = quote.strip()

    if extraction_text is not None and extraction_text.strip():
        text = extraction_text
        text_label = "focused procedure text"
    else:
        text = raw_note_text or ""
        text_label = "raw note text"
    if quote not in text:
        normalized_quote = _normalize_whitespace(quote)
        normalized_text = _normalize_whitespace(text)
        if not normalized_quote or normalized_quote not in normalized_text:
            return False, f"Quote not found verbatim in {text_label}: '{quote[:50]}...'"

    patches = getattr(proposal, "json_patch", [])
    if not isinstance(patches, list) or not patches:
        return False, "Empty patch"

    if max_patch_ops is None:
        max_patch_ops = _env_int("REGISTRY_SELF_CORRECT_MAX_PATCH_OPS", 5)

    if len(patches) > max_patch_ops:
        return False, f"Patch too large: {len(patches)} ops (max {max_patch_ops})"

    allowed_paths, allowed_prefixes = _allowed_paths_from_env(
        default_paths=ALLOWED_PATHS,
        default_prefixes=ALLOWED_PATH_PREFIXES,
    )

    for op in patches:
        if not isinstance(op, dict):
            return False, "Patch operation must be an object"

        path = op.get("path")
        if not _path_allowed(path, allowed_paths, allowed_prefixes):
            return False, f"Path not allowed: {path}"

        verb = op.get("op")
        if verb not in ("add", "replace"):
            return False, f"Op not allowed: {verb}"

    return True, "Valid"


def _allowed_paths_from_env(
    *,
    default_paths: set[str],
    default_prefixes: set[str],
) -> tuple[set[str], set[str]]:
    raw = os.getenv("REGISTRY_SELF_CORRECT_ALLOWLIST", "")
    if not raw.strip():
        return set(default_paths), set(default_prefixes)

    parsed_paths: set[str] = set()
    parsed_prefixes: set[str] = set()
    for entry in raw.split(","):
        cleaned = entry.strip()
        if not cleaned:
            continue
        if cleaned.endswith("/*"):
            prefix = cleaned[:-2].rstrip("/")
            if prefix:
                parsed_prefixes.add(prefix)
            continue
        parsed_paths.add(cleaned)

    if not parsed_paths and not parsed_prefixes:
        return set(default_paths), set(default_prefixes)
    return parsed_paths, parsed_prefixes


def _path_allowed(path: object, allowed_paths: set[str], allowed_prefixes: set[str]) -> bool:
    if not isinstance(path, str):
        return False
    if path in allowed_paths:
        return True
    for prefix in allowed_prefixes:
        if path == prefix or path.startswith(f"{prefix}/"):
            return True
    return False


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


__all__ = ["ALLOWED_PATHS", "ALLOWED_PATH_PREFIXES", "validate_proposal"]
