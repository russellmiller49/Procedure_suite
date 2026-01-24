import os

import pytest

from modules.registry.engine import RegistryEngine


def _get_linear_ebus_field(record, field_name):
    """Safely access linear_ebus nested fields with null-safety."""
    pp = record.procedures_performed
    if pp is None:
        return None
    linear = pp.linear_ebus
    if linear is None:
        return None
    return getattr(linear, field_name, None)


@pytest.fixture
def engine():
    os.environ["REGISTRY_USE_STUB_LLM"] = "true"
    return RegistryEngine()


def test_ebus_pass_counts_and_elastography(engine):
    note = """
    PROCEDURE: EBUS with TBNA

    TECHNIQUE:
    Linear EBUS performed. Station 4R sampled with three passes using a 22G needle.
    Station 7 sampled with two passes. Elastography demonstrated predominantly blue pattern.
    """
    record = engine.run(note)

    assert "EBUS" in record.procedure_families
    # Use nested path: procedures_performed.linear_ebus.stations_planned
    stations_planned = _get_linear_ebus_field(record, "stations_planned")
    assert stations_planned and set(stations_planned) >= {"4R", "7"}
    # Use nested path: procedures_performed.linear_ebus.needle_gauge
    assert _get_linear_ebus_field(record, "needle_gauge") == "22G"
    # Use nested path: procedures_performed.linear_ebus.elastography_pattern
    assert _get_linear_ebus_field(record, "elastography_pattern") is not None

    # Use nested path: procedures_performed.linear_ebus.stations_detail
    stations_detail = _get_linear_ebus_field(record, "stations_detail") or []
    detail_by_station = {d["station"]: d for d in stations_detail if d.get("station")}
    assert detail_by_station.get("4R", {}).get("passes") == 3
    assert detail_by_station.get("7", {}).get("passes") == 2


def test_parse_ebus_station_passes_without_station_keyword(engine):
    note = """
    EBUS-Findings:
    11L... tissue. Five needle passes.
    """
    passes = engine._parse_ebus_station_passes(note)
    assert passes.get("11L") == 5


def test_parse_ebus_station_passes_passes_before_station(engine):
    note = "Five needle passes at station 11L were obtained."
    passes = engine._parse_ebus_station_passes(note)
    assert passes.get("11L") == 5


def test_parse_ebus_station_passes_station7_label_style(engine):
    note = """
    EBUS-Findings:
    7 (subcarinal) sampled with two passes.
    """
    passes = engine._parse_ebus_station_passes(note)
    assert passes.get("7") == 2


def test_parse_ebus_station_passes_samples_collected(engine):
    note = "A total of 7 samples were collected from station 2R."
    passes = engine._parse_ebus_station_passes(note)
    assert passes.get("2R") == 7


def test_parse_ebus_station_passes_biopsies_wording(engine):
    note = "Station 11L: 5 biopsies were performed."
    passes = engine._parse_ebus_station_passes(note)
    assert passes.get("11L") == 5


def test_parse_ebus_station_passes_does_not_false_positive_age(engine):
    note = "Age 7 years. Five needle passes were performed."
    passes = engine._parse_ebus_station_passes(note)
    assert passes == {}
