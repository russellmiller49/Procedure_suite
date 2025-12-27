"""Tests for sectionizer utilities."""

from __future__ import annotations

from modules.coder.sectionizer import (
    accordion_truncate,
    split_into_sections,
)


def test_split_into_sections_identifies_headers():
    text = (
        "HISTORY: Patient history details.\n"
        "PROCEDURE: Bronchoscopy performed.\n"
        "FINDINGS: Station 7 sampled.\n"
    )
    sections = split_into_sections(text)
    names = [s.name for s in sections]
    assert "history" in names
    assert "procedure" in names
    assert "findings" in names


def test_accordion_truncate_prefers_high_priority_sections():
    history = "HISTORY: " + ("hx " * 100) + "\n"
    procedure = "PROCEDURE: Detailed bronchoscopy description.\n"
    findings = "FINDINGS: Station 7 sampled.\n"
    text = history + procedure + findings

    truncated = accordion_truncate(text, max_tokens=30)
    lowered = truncated.lower()
    assert "procedure:" in lowered
    assert "findings:" in lowered
    assert "history:" not in lowered or len(truncated) < len(text)


def test_accordion_truncate_without_headers_returns_original():
    text = "Simple short note without explicit headers."
    assert accordion_truncate(text, max_tokens=1000) == text
