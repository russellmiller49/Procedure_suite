from __future__ import annotations

import re

from rapidfuzz.fuzz import partial_ratio

from modules.common.spans import Span
from modules.registry.deterministic_extractors import (
    ROUTINE_SUCTION_PATTERNS,
    THERAPEUTIC_ASPIRATION_PATTERNS,
)
from modules.registry.schema import RegistryRecord
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


def _normalized_contains(haystack: str, needle: str) -> bool:
    if not haystack or not needle:
        return False
    return normalize_text(needle) in normalize_text(haystack)


def _verify_quote_in_text(quote: str, full_text: str, *, fuzzy_threshold: int = 85) -> bool:
    quote_clean = (quote or "").strip()
    if not quote_clean:
        return False
    if quote_clean in (full_text or ""):
        return True
    lowered_quote = quote_clean.lower()
    lowered_text = (full_text or "").lower()
    if lowered_quote in lowered_text:
        return True
    if _normalized_contains(full_text or "", quote_clean):
        return True

    normalized_quote = normalize_text(quote_clean)
    if len(normalized_quote) < 12:
        return False

    score = partial_ratio(normalized_quote, normalize_text(full_text or ""))
    return score >= fuzzy_threshold


def _evidence_texts_for_prefix(record: RegistryRecord, prefix: str) -> list[str]:
    evidence = getattr(record, "evidence", None) or {}
    if not isinstance(evidence, dict):
        return []

    texts: list[str] = []
    for key, spans in evidence.items():
        if not isinstance(key, str) or not key:
            continue
        if key != prefix and not key.startswith(prefix + "."):
            continue
        if not isinstance(spans, list):
            continue
        for span in spans:
            if not isinstance(span, Span):
                continue
            text = (span.text or "").strip()
            if text:
                texts.append(text)
    return texts


def _drop_evidence_prefix(record: RegistryRecord, prefix: str) -> None:
    evidence = getattr(record, "evidence", None)
    if not isinstance(evidence, dict) or not evidence:
        return
    to_drop = [k for k in evidence.keys() if isinstance(k, str) and (k == prefix or k.startswith(prefix + "."))]
    for key in to_drop:
        evidence.pop(key, None)


def _find_therapeutic_aspiration_anchor(full_text: str) -> tuple[str, int, int] | None:
    text_lower = (full_text or "").lower()
    if not text_lower:
        return None

    for pattern in THERAPEUTIC_ASPIRATION_PATTERNS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if not match:
            continue
        negation_check = r"\b(?:no|not|without)\b[^.]{0,80}" + pattern
        if re.search(negation_check, text_lower, re.IGNORECASE):
            continue
        return (match.group(0).strip(), match.start(), match.end())

    routine_suction_present = any(re.search(pattern, text_lower) for pattern in ROUTINE_SUCTION_PATTERNS)
    contextual_patterns = [
        r"\b(?:copious|large\s+amount\s+of|thick|tenacious|purulent|bloody|blood-tinged)\s+secretions?\b[^.]{0,80}\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared|remov(?:ed|al))\b",
        r"\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared|remov(?:ed|al))\b[^.]{0,80}\b(?:copious|large\s+amount\s+of|thick|tenacious|purulent|bloody|blood-tinged)\s+secretions?\b",
        r"\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared|remov(?:ed|al))\b[^.]{0,80}\b(?:mucus\s+plug|clot|blood)\b",
    ]
    if not routine_suction_present:
        contextual_patterns.append(
            r"\b(?:airway|tracheobronchial\s+tree)\b[^.]{0,80}\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared)\b"
        )
        contextual_patterns.extend(
            [
                r"\bsecretions?\b[^.]{0,80}\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b",
                r"\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b[^.]{0,80}\bsecretions?\b",
            ]
        )

    for pattern in contextual_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if not match:
            continue
        negation_check = r"\b(?:no|not|without)\b[^.]{0,80}" + pattern
        if re.search(negation_check, text_lower, re.IGNORECASE):
            continue
        return (match.group(0).strip(), match.start(), match.end())

    return None


def verify_evidence_integrity(record: RegistryRecord, full_note_text: str) -> tuple[RegistryRecord, list[str]]:
    """Apply Python-side guardrails against hallucinated performed events/details.

    This is intentionally conservative: if a high-risk performed=true procedure
    cannot be supported by extractable evidence, it is flipped to performed=false
    and dependent details are wiped.
    """

    warnings: list[str] = []
    full_text = full_note_text or ""

    procedures = getattr(record, "procedures_performed", None)
    if procedures is None:
        return record, warnings

    # ------------------------------------------------------------------
    # High-risk: therapeutic aspiration (frequent false-positives)
    # ------------------------------------------------------------------
    ta = getattr(procedures, "therapeutic_aspiration", None)
    if getattr(ta, "performed", None) is True:
        prefixes = [
            "procedures_performed.therapeutic_aspiration",
            "therapeutic_aspiration",
        ]
        candidate_quotes: list[str] = []
        for prefix in prefixes:
            candidate_quotes.extend(_evidence_texts_for_prefix(record, prefix))

        verified = any(_verify_quote_in_text(q, full_text) for q in candidate_quotes)
        if not verified:
            anchor = _find_therapeutic_aspiration_anchor(full_text)
            if anchor is not None:
                anchor_text, start, end = anchor
                record.evidence.setdefault("procedures_performed.therapeutic_aspiration.performed", []).append(
                    Span(text=anchor_text, start=start, end=end)
                )
                verified = True

        if not verified:
            setattr(ta, "performed", False)
            for dependent_field in ("material", "location"):
                if hasattr(ta, dependent_field):
                    setattr(ta, dependent_field, None)
            for prefix in prefixes:
                _drop_evidence_prefix(record, prefix)
            warnings.append("WIPED_VERIFICATION_FAILED: procedures_performed.therapeutic_aspiration")

    # ------------------------------------------------------------------
    # High-risk: hallucinated percutaneous trach device name (e.g., Portex)
    # ------------------------------------------------------------------
    trach = getattr(procedures, "percutaneous_tracheostomy", None)
    device_name = getattr(trach, "device_name", None)
    if isinstance(device_name, str) and device_name.strip():
        if not _normalized_contains(full_text, device_name):
            setattr(trach, "device_name", None)
            warnings.append("WIPED_DEVICE_NAME_NOT_IN_TEXT: procedures_performed.percutaneous_tracheostomy.device_name")

    return record, warnings


__all__ = ["normalize_text", "verify_registry", "verify_evidence_integrity"]
