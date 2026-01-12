from __future__ import annotations

import re

from modules.registry.schema.ip_v3 import IPRegistryV3, ProcedureEvent


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize text for robust substring matching.

    - lowercase
    - remove punctuation (keep a-z, 0-9)
    - collapse whitespace to single spaces
    """
    lowered = (text or "").lower()
    no_punct = _NON_ALNUM_RE.sub(" ", lowered)
    collapsed = _WS_RE.sub(" ", no_punct).strip()
    return collapsed


def verify_registry(registry: IPRegistryV3, full_source_text: str) -> IPRegistryV3:
    """Drop events whose evidence quote cannot be verified in the full source note text."""
    normalized_source = normalize_text(full_source_text or "")

    kept: list[ProcedureEvent] = []
    for event in registry.procedures:
        evidence = getattr(event, "evidence", None)
        quote = getattr(evidence, "quote", None) if evidence is not None else None
        if not quote or not str(quote).strip():
            continue

        normalized_quote = normalize_text(str(quote))
        if not normalized_quote:
            continue

        if normalized_quote in normalized_source:
            kept.append(event)

    return registry.model_copy(update={"procedures": kept})


__all__ = ["normalize_text", "verify_registry"]

