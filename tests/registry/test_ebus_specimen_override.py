from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.postprocess import reconcile_ebus_sampling_from_specimen_log
from app.registry.schema import RegistryRecord


def test_reconcile_ebus_sampling_from_specimen_log_restricts_station_count() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["4L", "4R", "7"],
                    "node_events": [
                        {"station": "4L", "action": "forceps_biopsy", "outcome": None, "evidence_quote": "4L - 4 passes"},
                        {"station": "4R", "action": "forceps_biopsy", "outcome": None, "evidence_quote": "4R - 6.0mm"},
                        {"station": "7", "action": "forceps_biopsy", "outcome": None, "evidence_quote": "7 - 8 passes"},
                    ],
                }
            }
        }
    )

    note_text = (
        "Node stations and sizes were as follows:\n"
        "4L - 5.5mm, 4 passes\n"
        "4R - 6.0mm\n"
        "7 - 7.5mm, 8 passes\n\n"
        "SPECIMENS SENT TO THE LABORATORY:\n"
        "--TBNA of 4L node station\n"
        "--TBNA of 7 node station\n"
        "-- Forceps Biopsies of the RLL (6 passes)\n"
    )

    warnings = reconcile_ebus_sampling_from_specimen_log(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.stations_sampled == ["4L", "7"]

    by_station = {e.station.upper(): e for e in (linear.node_events or [])}
    assert by_station["4L"].action == "needle_aspiration"
    assert by_station["7"].action == "needle_aspiration"
    assert by_station["4R"].action == "inspected_only"

    # Specimen log should restrict stations sampled, but must not overwrite
    # richer narrative evidence already present in node_events.
    assert by_station["4L"].evidence_quote == "4L - 4 passes"
    assert by_station["7"].evidence_quote == "7 - 8 passes"

    assert any("EBUS_SPECIMEN_OVERRIDE" in w for w in warnings)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31652" in codes
    assert "31653" not in codes

    evidence = record.evidence
    assert evidence.get("procedures_performed.linear_ebus.stations_sampled.0"), "Missing evidence for stations_sampled[0]"
    assert evidence.get("procedures_performed.linear_ebus.stations_sampled.1"), "Missing evidence for stations_sampled[1]"
    assert evidence.get("procedures_performed.linear_ebus.node_events.0.station"), "Missing evidence for node_events[0].station"
    assert evidence.get("procedures_performed.linear_ebus.node_events.2.station"), "Missing evidence for node_events[2].station"

    span_4l = evidence["procedures_performed.linear_ebus.stations_sampled.0"][0]
    span_7 = evidence["procedures_performed.linear_ebus.stations_sampled.1"][0]
    assert note_text[span_4l.start:span_4l.end].upper() == "4L"
    assert note_text[span_7.start:span_7.end] == "7"
