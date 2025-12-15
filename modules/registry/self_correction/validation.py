"""Phase 6 proposal validation (strict hallucination guard)."""

from __future__ import annotations

import os

from modules.registry.self_correction.types import JudgeProposal, ValidationResult


DEFAULT_SELF_CORRECT_ALLOWLIST: set[str] = {
    "/pleural_procedures/ipc/performed",
    "/pleural_procedures/thoracentesis/performed",
    "/pleural_procedures/chest_tube/performed",
}


def validate_proposal(
    *,
    proposal: JudgeProposal,
    raw_note_text: str,
    extraction_text: str | None,
    allowlist: set[str],
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    max_ops = _env_int("REGISTRY_SELF_CORRECT_MAX_PATCH_OPS", 5)

    if not proposal.patch:
        errors.append("empty patch")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    if len(proposal.patch) > max_ops:
        errors.append(f"patch has {len(proposal.patch)} ops; exceeds max {max_ops}")

    for idx, op in enumerate(proposal.patch):
        if not isinstance(op, dict):
            errors.append(f"patch[{idx}] is not an object")
            continue

        verb = op.get("op")
        if verb not in {"add", "replace"}:
            errors.append(f"patch[{idx}].op='{verb}' is forbidden (allow: add, replace)")

        path = op.get("path")
        if not isinstance(path, str) or not path.startswith("/"):
            errors.append(f"patch[{idx}].path is invalid: {path!r}")
            continue

        if path not in allowlist:
            errors.append(f"patch[{idx}].path '{path}' is not allowlisted")

    if not proposal.evidence_quotes:
        errors.append("missing evidence quotes")

    text_for_validation = extraction_text if (extraction_text and extraction_text.strip()) else raw_note_text
    for idx, quote in enumerate(proposal.evidence_quotes):
        if not isinstance(quote, str) or not quote.strip():
            errors.append(f"evidence_quotes[{idx}] is empty")
            continue
        if quote not in text_for_validation:
            preview = quote if len(quote) <= 80 else quote[:77] + "..."
            errors.append(f"evidence quote missing from text: {preview!r}")
        if not (10 <= len(quote) <= 200):
            warnings.append(f"evidence_quotes[{idx}] length {len(quote)} outside 10-200 chars")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings)


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


def allowlist_from_env(*, default: set[str] | None = None) -> set[str]:
    raw = os.getenv("REGISTRY_SELF_CORRECT_ALLOWLIST")
    if raw is None or not raw.strip():
        return set(default or DEFAULT_SELF_CORRECT_ALLOWLIST)

    allow = {p.strip() for p in raw.split(",") if p.strip()}
    return allow or set(default or DEFAULT_SELF_CORRECT_ALLOWLIST)


__all__ = ["DEFAULT_SELF_CORRECT_ALLOWLIST", "allowlist_from_env", "validate_proposal"]
