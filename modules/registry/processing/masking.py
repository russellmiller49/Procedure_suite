from __future__ import annotations

import re
from typing import Iterable

from modules.common.text_cleaning import (
    DEFAULT_TABLE_TOOL_KEYWORDS,
    find_empty_table_row_spans,
)


PATTERNS: list[str] = [
    r"(?ims)^IP\b[^\n]{0,60}CODE\s+MOD\s+DETAILS.*?(?=^\\s*(?:ANESTHESIA|MONITORING|INSTRUMENT|ESTIMATED\\s+BLOOD\\s+LOSS|COMPLICATIONS|PROCEDURE\\s+IN\\s+DETAIL|DESCRIPTION\\s+OF\\s+PROCEDURE)\\b|\\Z)",
    r"(?ims)^CPT\s+CODES?:.*?(?=\n\n|\Z)",
    r"(?ims)^BILLING:.*?(?=\n\n|\Z)",
    r"(?ims)^CODING\s+SUMMARY.*?(?=\n\n|\Z)",
    r"(?im)^\s*(?:CPT:?)?\s*\d{5}\b.*$",
]

NON_PROCEDURAL_HEADINGS: tuple[str, ...] = (
    "INDICATION",
    "INDICATIONS",
    "HISTORY",
    "CONSENT",
    "PLAN",
    "RECOMMENDATION",
    "RECOMMENDATIONS",
    "ASSESSMENT",
)

_HEADING_INLINE_RE = re.compile(
    r"^(?P<header>[A-Za-z][A-Za-z /_-]{0,80})\s*:\s*(?P<rest>.*)$",
    re.MULTILINE,
)


def mask_offset_preserving(text: str, patterns: Iterable[str] = PATTERNS) -> str:
    """Mask matched spans with spaces while preserving length and newlines."""
    masked = text or ""
    for pat in patterns:
        for match in re.finditer(pat, masked):
            start, end = match.span()
            chunk = masked[start:end]
            chunk_mask = re.sub(r"[^\n]", " ", chunk)
            masked = masked[:start] + chunk_mask + masked[end:]
    return masked


def mask_extraction_noise(text: str) -> tuple[str, dict[str, object]]:
    """Mask template noise and non-procedural sections for extraction."""
    base = mask_offset_preserving(text or "")
    sections = _find_non_procedural_section_spans(text or "")
    section_spans = [(start, end) for start, end, _ in sections]
    table_spans = find_empty_table_row_spans(text or "", keywords=DEFAULT_TABLE_TOOL_KEYWORDS)
    spans = section_spans + table_spans

    masked = _mask_spans(base, spans)
    meta = {
        "masked_non_procedural_sections": sorted({title for _, _, title in sections}),
        "masked_non_procedural_section_count": len(sections),
        "masked_empty_table_rows": len(table_spans),
    }
    return masked, meta


def _normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).upper()


def _is_non_procedural_heading(header: str) -> bool:
    if header in NON_PROCEDURAL_HEADINGS:
        return True
    return any(
        header.startswith(prefix)
        for token in NON_PROCEDURAL_HEADINGS
        for prefix in (f"{token} ", f"{token}/", f"{token} -")
    )


def _find_non_procedural_section_spans(text: str) -> list[tuple[int, int, str]]:
    matches = list(_HEADING_INLINE_RE.finditer(text or ""))
    spans: list[tuple[int, int, str]] = []
    if not matches:
        return spans

    for idx, match in enumerate(matches):
        header = _normalize_heading(match.group("header"))
        if not _is_non_procedural_heading(header):
            continue
        body_start = match.start("rest")
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        if body_end <= body_start:
            continue
        spans.append((body_start, body_end, header))
    return spans


def _mask_spans(text: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return text
    masked = list(text)
    text_len = len(masked)
    for start, end in spans:
        if start >= text_len or end <= 0:
            continue
        s = max(0, start)
        e = min(text_len, end)
        for idx in range(s, e):
            if masked[idx] != "\n":
                masked[idx] = " "
    return "".join(masked)


__all__ = [
    "PATTERNS",
    "NON_PROCEDURAL_HEADINGS",
    "mask_offset_preserving",
    "mask_extraction_noise",
]
