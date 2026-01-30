from __future__ import annotations

from pathlib import Path

import pytest

from modules.registry.application.registry_service import RegistryService


def _get_linear_ebus(record):
    procedures = getattr(record, "procedures_performed", None)
    return getattr(procedures, "linear_ebus", None) if procedures is not None else None


def _collect_station_labels(linear):
    stations: set[str] = set()
    if linear is None:
        return stations

    for station in (getattr(linear, "stations_sampled", None) or []):
        if station:
            stations.add(str(station).upper())

    for event in (getattr(linear, "node_events", None) or []):
        station = getattr(event, "station", None)
        if station:
            stations.add(str(station).upper())

    return stations


def test_note_002_regression(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")

    note_path = Path("data/granular annotations/notes_text/note_002.txt")
    if not note_path.is_file():
        pytest.skip(f"Fixture note not available: {note_path}")
    note_text = note_path.read_text(encoding="utf-8")

    result = RegistryService().extract_fields(note_text)
    record = result.record

    assert record.granular_data is not None
    nav_targets = record.granular_data.navigation_targets or []
    assert len(nav_targets) >= 3

    linear = _get_linear_ebus(record)
    assert linear is not None
    assert linear.performed is True

    stations = _collect_station_labels(linear)
    assert len(stations) >= 3
    for station in ("11L", "7", "11RS", "11RI"):
        assert station in stations

    assert "31653" in result.cpt_codes

    procedures = getattr(record, "procedures_performed", None)
    if procedures is not None and hasattr(procedures, "eus_b"):
        eus_b = getattr(procedures, "eus_b")
        assert eus_b is not None
        assert getattr(eus_b, "performed", False) is True
        assert "43238" in result.cpt_codes
