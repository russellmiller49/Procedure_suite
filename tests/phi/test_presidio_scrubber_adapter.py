"""Tests for the PresidioScrubber adapter (skips if Presidio not installed)."""

from __future__ import annotations

import os

import pytest


class _SpanResult:
    def __init__(self, *, entity_type: str, start: int, end: int, score: float = 0.5):
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score

pytest.importorskip("presidio_analyzer")

from app.phi.adapters.presidio_scrubber import PresidioScrubber, filter_allowlisted_terms, filter_cpt_codes


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
    assert "SURGEON: John Smith, MD" in result.scrubbed_text
    assert "<LOCATION>" not in result.scrubbed_text


def test_presidio_scrubber_redacts_patient_header_name_and_mrn_preserves_providers():
    os.environ.setdefault("PRESIDIO_NLP_MODEL", "en_core_web_lg")
    scrubber = PresidioScrubber()
    text = (
        "Aronson, Gary MRN: 11207396 PREOPERATIVE DIAGNOSIS: X "
        "SURGEON: George Cheng MD ASSISTANT: Russell Miller, MD Sedation: General Anesthesia"
    )
    result = scrubber.scrub(text)

    assert "Aronson, Gary" not in result.scrubbed_text
    assert "11207396" not in result.scrubbed_text
    assert "<PERSON> MRN: <MRN>" in result.scrubbed_text
    assert "SURGEON: George Cheng MD" in result.scrubbed_text
    assert "ASSISTANT: Russell Miller, MD" in result.scrubbed_text
    assert "General Anesthesia" in result.scrubbed_text
    assert "<LOCATION>" not in result.scrubbed_text


def test_provider_credential_at_end_of_note_does_not_disable_patient_redaction():
    os.environ.setdefault("PRESIDIO_NLP_MODEL", "en_core_web_lg")
    scrubber = PresidioScrubber()
    text = "Aronson, Gary MRN: 11207396 SURGEON: George Cheng MD"
    result = scrubber.scrub(text)

    assert "<PERSON> MRN: <MRN>" in result.scrubbed_text
    assert "SURGEON: George Cheng MD" in result.scrubbed_text


def test_filter_cpt_codes_drops_detections_overlapping_cpt_numbers():
    text = "PROCEDURE PERFORMED:\nCPT 31641 Bronchoscopy\nCPT 31624 BAL\n"
    d1 = _SpanResult(entity_type="DATE_TIME", start=text.index("31641"), end=text.index("31641") + 5)
    d2 = _SpanResult(entity_type="DATE_TIME", start=text.index("31624"), end=text.index("31624") + 5)
    kept = filter_cpt_codes(text, [d1, d2])
    assert kept == []


def test_filter_allowlisted_terms_drops_known_clinical_false_positives():
    text = "Target: Lung Nodule\nStation 11Rs\nUS guidance\nNS flush\nMC routing\n"
    results = [
        _SpanResult(entity_type="PERSON", start=text.index("Lung Nodule"), end=text.index("Lung Nodule") + len("Lung Nodule")),
        _SpanResult(entity_type="DATE_TIME", start=text.index("11Rs"), end=text.index("11Rs") + len("11Rs")),
        _SpanResult(entity_type="LOCATION", start=text.index("US"), end=text.index("US") + len("US")),
        _SpanResult(entity_type="LOCATION", start=text.index("NS"), end=text.index("NS") + len("NS")),
        _SpanResult(entity_type="LOCATION", start=text.index("MC"), end=text.index("MC") + len("MC")),
        _SpanResult(entity_type="PERSON", start=text.index("Target"), end=text.index("Target") + len("Target")),
    ]
    kept = filter_allowlisted_terms(text, results)
    assert kept == []
