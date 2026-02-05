from __future__ import annotations

from modules.registry.postprocess import populate_ebus_node_events_fallback
from modules.registry.schema import RegistryRecord
from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta


def test_populate_ebus_node_events_fallback_parses_following_station_list_with_blank_lines() -> None:
    record = RegistryRecord.model_validate({"procedures_performed": {"linear_ebus": {"performed": True}}})
    note_text = (
        "Linear EBUS: A CP-EBUS survey was performed.\n"
        "Multiple EBUS-TBNA passes were obtained from the following station(s):\n\n"
        "11L (abnormally large lymph node versus mass)\n\n"
        "ROSE was indicative of specimen adequacy.\n"
    )

    warnings = populate_ebus_node_events_fallback(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.stations_sampled == ["11L"]
    assert linear.node_events is not None
    assert len(linear.node_events) == 1
    assert linear.node_events[0].station == "11L"
    assert linear.node_events[0].action == "needle_aspiration"
    assert any("EBUS_REGEX_FALLBACK" in w for w in warnings)

    evidence = record.evidence
    assert evidence.get("procedures_performed.linear_ebus.stations_sampled.0"), "Missing evidence for stations_sampled[0]"
    assert evidence.get("procedures_performed.linear_ebus.node_events.0.station"), "Missing evidence for node_events[0].station"
    assert evidence.get("procedures_performed.linear_ebus.node_events.0.evidence_quote"), "Missing evidence for node_events[0].evidence_quote"

    span = evidence["procedures_performed.linear_ebus.node_events.0.station"][0]
    assert note_text[span.start:span.end].upper() == "11L"


def test_populate_ebus_node_events_fallback_adds_placeholder_when_sampling_documented_without_stations() -> None:
    record = RegistryRecord.model_validate({"procedures_performed": {"linear_ebus": {"performed": True}}})
    note_text = (
        "Endobronchial Ultrasound Findings\n"
        "Lymph node sizing and sampling were performed using endobronchial ultrasound with an Olympus EBUS-TBNA 22-gauge needle.\n"
        "ROSE was consistent with malignancy.\n"
    )

    warnings = populate_ebus_node_events_fallback(record, note_text)
    assert any("EBUS_FALLBACK" in w for w in warnings)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.stations_sampled == ["UNSPECIFIED"]
    assert linear.node_events is not None
    assert len(linear.node_events) == 1
    assert linear.node_events[0].station == "UNSPECIFIED"
    assert linear.node_events[0].action == "needle_aspiration"

    evidence = record.evidence
    assert evidence.get("procedures_performed.linear_ebus.stations_sampled.0"), "Missing evidence for stations_sampled[0]"
    assert evidence.get("procedures_performed.linear_ebus.node_events.0.station"), "Missing evidence for node_events[0].station"
    assert evidence.get("procedures_performed.linear_ebus.node_events.0.evidence_quote"), "Missing evidence for node_events[0].evidence_quote"

    span = evidence["procedures_performed.linear_ebus.node_events.0.evidence_quote"][0]
    assert "EBUS-TBNA" in note_text[span.start:span.end].upper()

    codes, _rationales, _warn = derive_all_codes_with_meta(record)
    assert "31652" in codes


def test_populate_ebus_node_events_fallback_captures_passes_and_rose_with_evidence() -> None:
    record = RegistryRecord.model_validate({"procedures_performed": {"linear_ebus": {"performed": True}}})
    note_text = (
        "Endobronchial Ultrasound Findings\n"
        "Multiple EBUS-TBNA passes were obtained from the following station(s):\n"
        "11L: biopsied with a 22G needle, 5 passes. ROSE: adequate lymphocytes.\n"
    )

    warnings = populate_ebus_node_events_fallback(record, note_text)
    assert any("EBUS_REGEX_FALLBACK" in w for w in warnings)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.node_events is not None
    assert len(linear.node_events) == 1
    assert linear.node_events[0].station == "11L"
    assert linear.node_events[0].passes == 5
    assert linear.node_events[0].pass_count == 5
    assert linear.node_events[0].rose_result == "adequate lymphocytes"

    evidence = record.evidence
    assert evidence.get("procedures_performed.linear_ebus.node_events.0.passes"), "Missing evidence for node_events[0].passes"
    assert evidence.get(
        "procedures_performed.linear_ebus.node_events.0.rose_result"
    ), "Missing evidence for node_events[0].rose_result"

    passes_span = evidence["procedures_performed.linear_ebus.node_events.0.passes"][0]
    assert note_text[passes_span.start:passes_span.end] == "5 passes"

    rose_span = evidence["procedures_performed.linear_ebus.node_events.0.rose_result"][0]
    assert "ROSE" in note_text[rose_span.start:rose_span.end].upper()
    assert "adequate lymphocytes" in note_text[rose_span.start:rose_span.end].lower()
