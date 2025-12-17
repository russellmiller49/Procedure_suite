from __future__ import annotations

from pathlib import Path

from modules.phi.adapters.presidio_scrubber import (
    DEFAULT_ENTITY_SCORE_THRESHOLDS,
    DEFAULT_RELATIVE_DATE_TIME_PHRASES,
    Detection,
    redact_with_audit,
)


def _span(text: str, needle: str) -> tuple[int, int]:
    start = text.index(needle)
    return start, start + len(needle)


def test_phi_redaction_contract_example_note():
    text = Path("tests/fixtures/notes/phi_example_note.txt").read_text(encoding="utf-8")

    detections = [
        # Must redact: patient name after Patient:
        Detection(entity_type="PERSON", start=_span(text, "Fisher, Sarah")[0], end=_span(text, "Fisher, Sarah")[1], score=0.95),
        # Must redact: explicit procedure date
        Detection(entity_type="DATE_TIME", start=_span(text, "05/10/2022")[0], end=_span(text, "05/10/2022")[1], score=0.90),
        # Provider name safe zones (should NOT redact)
        Detection(entity_type="PERSON", start=_span(text, "Jordan Parks")[0], end=_span(text, "Jordan Parks")[1], score=0.90),
        Detection(entity_type="PERSON", start=_span(text, "Michael Manson")[0], end=_span(text, "Michael Manson")[1], score=0.90),
        # Signature block safe zone (should NOT redact)
        Detection(entity_type="PERSON", start=_span(text, "Jonathan Lee")[0], end=_span(text, "Jonathan Lee")[1], score=0.90),
        # Device/model suppressor (should NOT redact)
        Detection(entity_type="US_DRIVER_LICENSE", start=_span(text, "T190")[0], end=_span(text, "T190")[1], score=0.80),
        # Allowlist (should NOT redact)
        Detection(entity_type="LOCATION", start=_span(text, "Kenalog")[0], end=_span(text, "Kenalog")[1], score=0.90),
        Detection(entity_type="LOCATION", start=_span(text, "nonobstructive")[0], end=_span(text, "nonobstructive")[1], score=0.90),
        # DATE_TIME exclusions (should NOT redact)
        Detection(entity_type="DATE_TIME", start=_span(text, "30 second")[0], end=_span(text, "30 second")[1], score=0.90),
        Detection(entity_type="DATE_TIME", start=_span(text, "about a week")[0], end=_span(text, "about a week")[1], score=0.90),
    ]

    scrub_result, audit = redact_with_audit(
        text=text,
        detections=detections,
        enable_driver_license_recognizer=False,
        score_thresholds=DEFAULT_ENTITY_SCORE_THRESHOLDS,
        relative_datetime_phrases=DEFAULT_RELATIVE_DATE_TIME_PHRASES,
        nlp_backend=None,
        nlp_model=None,
    )

    # Must redact
    assert "Fisher, Sarah" not in scrub_result.scrubbed_text
    assert "Patient: <PERSON>" in scrub_result.scrubbed_text
    assert "05/10/2022" not in scrub_result.scrubbed_text
    assert "<DATE_TIME>" in scrub_result.scrubbed_text

    # Must preserve
    assert "Jordan Parks" in scrub_result.scrubbed_text
    assert "Michael Manson" in scrub_result.scrubbed_text
    assert "Jonathan Lee" in scrub_result.scrubbed_text
    assert "T190" in scrub_result.scrubbed_text
    assert "Kenalog" in scrub_result.scrubbed_text
    assert "nonobstructive" in scrub_result.scrubbed_text
    assert "30 second" in scrub_result.scrubbed_text
    assert "about a week" in scrub_result.scrubbed_text

    # Audit JSON contract
    assert audit["redacted_text"] == scrub_result.scrubbed_text
    assert isinstance(audit["detections"], list)
    assert isinstance(audit["removed_detections"], list)

    removed_by_reason = {}
    for item in audit["removed_detections"]:
        removed_by_reason.setdefault(item["reason"], []).append(item["detected_text"])

    assert "provider_context" in removed_by_reason
    assert any("Jordan Parks" in t for t in removed_by_reason["provider_context"])
    assert any("Michael Manson" in t for t in removed_by_reason["provider_context"])
    assert any("Jonathan Lee" in t for t in removed_by_reason["provider_context"])

    assert removed_by_reason.get("device_model") == ["T190"]
    assert "allowlist" in removed_by_reason
    assert "Kenalog" in " ".join(removed_by_reason["allowlist"])
    assert "nonobstructive" in " ".join(removed_by_reason["allowlist"])
    assert "duration_datetime" in removed_by_reason
    assert "30 second" in " ".join(removed_by_reason["duration_datetime"])
    assert "about a week" in " ".join(removed_by_reason["duration_datetime"])


def test_phi_redaction_contract_low_score_location_dropped():
    text = "Patient: Fisher, Sarah visited Paris on 05/10/2022."
    paris_start, paris_end = _span(text, "Paris")
    name_start, name_end = _span(text, "Fisher, Sarah")
    date_start, date_end = _span(text, "05/10/2022")

    detections = [
        Detection(entity_type="PERSON", start=name_start, end=name_end, score=0.95),
        Detection(entity_type="DATE_TIME", start=date_start, end=date_end, score=0.90),
        Detection(entity_type="LOCATION", start=paris_start, end=paris_end, score=0.10),
    ]

    scrub_result, audit = redact_with_audit(
        text=text,
        detections=detections,
        enable_driver_license_recognizer=False,
        score_thresholds=DEFAULT_ENTITY_SCORE_THRESHOLDS,
        relative_datetime_phrases=DEFAULT_RELATIVE_DATE_TIME_PHRASES,
    )

    assert "Fisher, Sarah" not in scrub_result.scrubbed_text
    assert "05/10/2022" not in scrub_result.scrubbed_text
    assert "Paris" in scrub_result.scrubbed_text

    removed = [d for d in audit["removed_detections"] if d["reason"] == "low_score"]
    assert any(d["detected_text"] == "Paris" for d in removed)
