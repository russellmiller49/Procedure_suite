"""Helpers for asserting PHI is not leaked in responses/logs during tests."""

from __future__ import annotations


def assert_no_raw_phi_in_text(text: str, raw_fragments: list[str]) -> None:
    for frag in raw_fragments:
        assert frag not in text, f"Found raw PHI fragment in text: {frag}"


__all__ = ["assert_no_raw_phi_in_text"]
