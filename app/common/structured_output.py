"""Shared structured-output schema specs for LLM wrappers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StructuredOutputSpec:
    """Normalized structured-output schema spec."""

    name: str
    schema: dict[str, Any]
    strict: bool = True


def structured_output_cache_token(spec: StructuredOutputSpec | None) -> str:
    """Build a stable cache token for schema-aware calls."""
    if spec is None:
        return ""
    payload = {
        "name": str(spec.name),
        "strict": bool(spec.strict),
        "schema": spec.schema,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["StructuredOutputSpec", "structured_output_cache_token"]
