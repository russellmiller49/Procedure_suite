from __future__ import annotations

from scripts.build_model_agnostic_phi_spans import filter_detections
from scripts.sanitize_platinum_spans import init_counters, should_drop_span


def _run_filter(note_text: str, detections: list[dict[str, object]], provider_policy: str = "drop"):
    counters = {
        "spans_dropped_provider": 0,
        "spans_dropped_cpt": 0,
        "spans_dropped_temperature": 0,
        "spans_dropped_protected_geo": 0,
        "spans_dropped_protected_person": 0,
        "spans_dropped_ln_station": 0,
        "spans_dropped_device_keyword": 0,
        "spans_dropped_station_adjacent_digits": 0,
        "spans_dropped_unplausible_address": 0,
    }
    spans = filter_detections(
        note_text,
        detections,
        label_schema="standard",
        provider_policy=provider_policy,
        provider_label="PROVIDER",
        counters=counters,
    )
    return spans, counters


def test_platinum_drops_cpt_geo_in_code_context() -> None:
    text = "Codes Submitted: 31654"
    start = text.index("31654")
    detections = [{"start": start, "end": start + 5, "type": "LOCATION", "text": "31654"}]

    spans, counters = _run_filter(text, detections)

    assert spans == []
    assert counters["spans_dropped_cpt"] == 1


def test_platinum_keeps_zipcode_in_address() -> None:
    text = "La Jolla, CA 92037"
    start = text.index("92037")
    detections = [{"start": start, "end": start + 5, "type": "LOCATION", "text": "92037"}]

    spans, counters = _run_filter(text, detections)

    assert len(spans) == 1
    assert spans[0]["label"] == "GEO"
    assert counters["spans_dropped_cpt"] == 0


def test_platinum_drops_temperature_span() -> None:
    text = "RFA at 105C for 10 min"
    start = text.index("105C")
    detections = [{"start": start, "end": start + 4, "type": "LOCATION", "text": "105C"}]

    spans, counters = _run_filter(text, detections)

    assert spans == []
    assert counters["spans_dropped_temperature"] == 1


def test_platinum_drops_station_geo_span() -> None:
    text = "Stations 4R and 7 sampled"
    start = text.index("4R")
    detections = [{"start": start, "end": start + 2, "type": "LOCATION", "text": "4R"}]

    spans, counters = _run_filter(text, detections)

    assert spans == []
    assert counters["spans_dropped_ln_station"] == 1


def test_platinum_drops_provider_context_name() -> None:
    text = "ATTENDING: John Smith, MD"
    start = text.index("John")
    end = start + len("John Smith")
    detections = [{"start": start, "end": end, "type": "PATIENT_NAME", "text": "John Smith"}]

    spans, counters = _run_filter(text, detections)

    assert spans == []
    assert counters["spans_dropped_provider"] == 1


def test_platinum_keeps_patient_name() -> None:
    text = "Patient: John Smith"
    start = text.index("John")
    end = start + len("John Smith")
    detections = [{"start": start, "end": end, "type": "PATIENT_NAME", "text": "John Smith"}]

    spans, counters = _run_filter(text, detections)

    assert len(spans) == 1
    assert spans[0]["label"] == "PATIENT"
    assert counters["spans_dropped_provider"] == 0


def test_platinum_drops_station_number_as_person() -> None:
    text = "Station 7 sampled"
    start = text.index("7")
    detections = [{"start": start, "end": start + 1, "type": "PATIENT_NAME", "text": "7"}]

    spans, counters = _run_filter(text, detections)

    assert spans == []
    assert counters["spans_dropped_protected_person"] == 1


def test_platinum_sanitizer_drops_cpt_like_geo_span_in_code_line() -> None:
    text = "Codes submitted: 31654"
    start = text.index("31654")
    span = {"start": start, "end": start + 5, "label": "GEO", "text": "31654"}
    counters = init_counters()

    should_drop = should_drop_span(span, text, counters)

    assert should_drop is True
    assert counters["spans_dropped_cpt"] == 1


def test_platinum_sanitizer_keeps_zip_in_address_line() -> None:
    text = "La Jolla, CA 92037"
    start = text.index("92037")
    span = {"start": start, "end": start + 5, "label": "GEO", "text": "92037"}
    counters = init_counters()

    should_drop = should_drop_span(span, text, counters)

    assert should_drop is False
