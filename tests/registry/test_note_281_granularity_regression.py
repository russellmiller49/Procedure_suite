from __future__ import annotations

from pathlib import Path

from app.registry.deterministic_extractors import run_deterministic_extractors
from app.registry.postprocess import enrich_ebus_node_event_sampling_details
from app.registry.processing.masking import mask_offset_preserving
from app.registry.schema import RegistryRecord


def test_note_281_bal_includes_location_and_volumes_in_seed() -> None:
    note_text = Path("tests/fixtures/notes/note_281.txt").read_text(encoding="utf-8")
    seed_text = mask_offset_preserving(note_text)

    seed = run_deterministic_extractors(seed_text)
    procs = seed.get("procedures_performed") or {}
    assert isinstance(procs, dict)

    bal = procs.get("bal") or {}
    assert isinstance(bal, dict)
    assert bal.get("performed") is True
    assert "RML" in str(bal.get("location") or "").upper()
    assert "RB4" in str(bal.get("location") or "").upper()
    assert bal.get("volume_instilled_ml") == 40
    assert bal.get("volume_recovered_ml") == 17


def test_note_281_ebus_node_events_capture_passes_and_elastography() -> None:
    note_text = Path("tests/fixtures/notes/note_281.txt").read_text(encoding="utf-8")

    record = RegistryRecord(
        **{
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "11L",
                            "action": "needle_aspiration",
                            "outcome": None,
                            "evidence_quote": "Station 11L, 4L, 4R TBNA (cyto, flow cytometry)",
                        },
                        {
                            "station": "4L",
                            "action": "needle_aspiration",
                            "outcome": None,
                            "evidence_quote": "Station 11L, 4L, 4R TBNA (cyto, flow cytometry)",
                        },
                        {
                            "station": "4R",
                            "action": "needle_aspiration",
                            "outcome": None,
                            "evidence_quote": "Station 11L, 4L, 4R TBNA (cyto, flow cytometry)",
                        },
                    ],
                }
            }
        }
    )

    warnings = enrich_ebus_node_event_sampling_details(record, note_text)
    assert any("AUTO_EBUS_GRANULARITY" in w for w in warnings)

    ebus = record.procedures_performed.linear_ebus
    by_station = {e.station.upper(): e for e in (ebus.node_events or [])}

    assert by_station["11L"].passes == 5
    assert (by_station["11L"].elastography_pattern or "").startswith("Type 2")
    assert "Type 2" in (by_station["11L"].evidence_quote or "")
    assert "SPECIMEN" not in (by_station["11L"].evidence_quote or "").upper()

    assert by_station["4L"].passes == 5
    assert (by_station["4L"].elastography_pattern or "").startswith("Type 1")

    assert by_station["4R"].passes == 6
    assert (by_station["4R"].elastography_pattern or "").startswith("Type 1")

