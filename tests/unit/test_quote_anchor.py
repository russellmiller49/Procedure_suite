from __future__ import annotations

from app.evidence.quote_anchor import AnchorMethod, anchor_quote


def test_anchor_quote_exact_match() -> None:
    doc = "Hello world.\nBronchoscopy was performed.\nDone."
    quote = "Bronchoscopy was performed."
    result = anchor_quote(doc, quote)

    assert result.span is not None
    assert result.method == AnchorMethod.exact
    assert doc[result.span.start : result.span.end] == quote


def test_anchor_quote_case_insensitive_match() -> None:
    doc = "Bronchoscopy was performed."
    quote = "bronchoscopy was performed."
    result = anchor_quote(doc, quote)

    assert result.span is not None
    assert result.method == AnchorMethod.case_insensitive
    assert result.span.text == "Bronchoscopy was performed."


def test_anchor_quote_whitespace_flexible_match() -> None:
    doc = "BAL performed at RUL.\nInstilled 40 cc.\nReturned 17 cc."
    quote = "BAL performed at RUL. Instilled 40 cc. Returned 17 cc."
    result = anchor_quote(doc, quote)

    assert result.span is not None
    assert result.method in {AnchorMethod.whitespace, AnchorMethod.whitespace_case_insensitive}
    assert "Instilled 40 cc" in result.span.text


def test_anchor_quote_fuzzy_match() -> None:
    doc = "Aspirated thick secretions; suctioned clear."
    quote = "Aspirated thick secretions suctioned clear"
    result = anchor_quote(doc, quote, fuzzy_threshold=90.0)

    assert result.span is not None
    assert result.method == AnchorMethod.fuzzy
    assert "secretions" in result.span.text.lower()

