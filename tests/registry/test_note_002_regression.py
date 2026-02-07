from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.application.registry_service import RegistryService


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
    nav_texts = [t.target_location_text for t in nav_targets if getattr(t, "target_location_text", None)]
    assert any("nodule #1" in t.lower() for t in nav_texts)
    assert any("nodule #2" in t.lower() for t in nav_texts)
    assert any("RB2" in t and "nodule #3" in t.lower() for t in nav_texts)

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
        assert getattr(eus_b, "needle_gauge", None) == "25G"
        assert getattr(eus_b, "passes", None) == 4
        assert "Left adrenal mass" in (getattr(eus_b, "sites_sampled", None) or [])
        assert "43238" in result.cpt_codes

    if procedures is not None:
        peripheral_tbna = getattr(procedures, "peripheral_tbna", None)
        assert peripheral_tbna is not None
        assert getattr(peripheral_tbna, "performed", False) is True
        targets = getattr(peripheral_tbna, "targets_sampled", None) or []
        assert any("RB2" in str(t) for t in targets)

        cryobiopsy = getattr(procedures, "transbronchial_cryobiopsy", None)
        assert cryobiopsy is not None
        assert getattr(cryobiopsy, "performed", False) is True
        locations = getattr(cryobiopsy, "locations_biopsied", None) or []
        assert any("RB2" in str(loc) for loc in locations)

        brushings = getattr(procedures, "brushings", None)
        assert brushings is not None
        assert getattr(brushings, "performed", False) is True
        brush_locations = getattr(brushings, "locations", None) or []
        assert "RB2" in brush_locations

        bal = getattr(procedures, "bal", None)
        assert bal is not None
        assert getattr(bal, "performed", False) is True
        bal_location = getattr(bal, "location", "") or ""
        assert "Apical Segment of RUL (RB1)" in bal_location
        assert "Posterior Segment of RUL (RB2)" in bal_location
        assert getattr(bal, "volume_instilled_ml", None) == 60.0
        assert getattr(bal, "volume_recovered_ml", None) == 15.0

    station7 = None
    if linear is not None:
        for event in (getattr(linear, "node_events", None) or []):
            station = getattr(event, "station", None)
            if station is not None and str(station).strip().upper() == "7":
                station7 = event
                break
    assert station7 is not None
    assert getattr(station7, "passes", None) == 4
    assert getattr(station7, "elastography_pattern", None) == "Type 1"
    assert str(getattr(station7, "evidence_quote", "") or "").startswith("Site 2:")
