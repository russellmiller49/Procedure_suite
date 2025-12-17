"""Tests for the PresidioScrubber adapter (skips if Presidio not installed)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("presidio_analyzer")

from modules.phi.adapters.presidio_scrubber import PresidioScrubber


def test_presidio_scrubber_detects_obvious_person_name():
    os.environ.setdefault("PRESIDIO_NLP_MODEL", "en_core_web_lg")
    scrubber = PresidioScrubber()
    text = "Patient Jane Test was seen on 01/02/2099."
    result = scrubber.scrub(text)

    assert result.scrubbed_text != text
    assert result.entities


def test_presidio_scrubber_preserves_anatomical_terms():
    os.environ.setdefault("PRESIDIO_NLP_MODEL", "en_core_web_lg")
    scrubber = PresidioScrubber()
    text = "Right upper lobe nodule biopsied via EBUS."
    result = scrubber.scrub(text)

    assert "right upper lobe" in result.scrubbed_text.lower()
    assert "ebus" in result.scrubbed_text.lower()
    for ent in result.entities:
        span = text[ent["original_start"] : ent["original_end"]].lower()
        assert "right upper lobe" not in span
        assert "ebus" not in span


def test_presidio_scrubber_patient_label_overrides_name():
    os.environ.setdefault("PRESIDIO_NLP_MODEL", "en_core_web_lg")
    scrubber = PresidioScrubber()
    text = "Patient: Fisher, Sarah\nSURGEON: John Smith, MD\n"
    result = scrubber.scrub(text)

    assert "Patient: <PERSON>" in result.scrubbed_text
    assert "Fisher, Sarah" not in result.scrubbed_text
