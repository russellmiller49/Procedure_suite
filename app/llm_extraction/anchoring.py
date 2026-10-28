"""Anchor model-quoted evidence to exact source offsets.

Excerpts are always slices of the document, so ``text[start:end] == excerpt``
holds for every anchored span (the clinical review app re-checks this). Fuzzy
alignment is off by default: an unanchored quote is dropped, not guessed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.evidence.quote_anchor import AnchorMethod, anchor_quote

ACCEPTED_METHODS = {
    AnchorMethod.exact,
    AnchorMethod.case_insensitive,
    AnchorMethod.whitespace,
    AnchorMethod.whitespace_case_insensitive,
}


@dataclass(frozen=True)
class AnchoredSpan:
    start: int
    end: int
    excerpt: str
    method: str
    occurrences: int


def _occurrences(document: str, quote: str) -> list[tuple[int, int]]:
    tokens = [re.escape(token) for token in quote.split()]
    if not tokens:
        return []
    pattern = re.compile(r"\s+".join(tokens), re.IGNORECASE)
    return [(m.start(), m.end()) for m in pattern.finditer(document)]


def anchor(
    document: str, quote: str, *, near: int | None = None, allow_fuzzy: bool = False
) -> AnchoredSpan | None:
    """Return the span of ``quote`` in ``document``.

    When the quote occurs more than once, the occurrence nearest ``near`` (the
    row's own anchor offset) wins; without a hint the first occurrence is used.
    """
    quote = (quote or "").strip()
    if not quote or not document:
        return None
    spans = _occurrences(document, quote)
    if spans:
        if near is not None and len(spans) > 1:
            start, end = min(spans, key=lambda span: abs(span[0] - near))
        else:
            start, end = spans[0]
        exact = document[start:end] == quote
        return AnchoredSpan(
            start=start,
            end=end,
            excerpt=document[start:end],
            method=AnchorMethod.exact.value if exact else AnchorMethod.whitespace_case_insensitive.value,
            occurrences=len(spans),
        )
    result = anchor_quote(document, quote)
    if result.span is None:
        return None
    if result.method not in ACCEPTED_METHODS and not (
        allow_fuzzy and result.method == AnchorMethod.fuzzy
    ):
        return None
    return AnchoredSpan(
        start=result.span.start,
        end=result.span.end,
        excerpt=document[result.span.start : result.span.end],
        method=result.method.value,
        occurrences=1,
    )


__all__ = ["AnchoredSpan", "anchor"]
