from __future__ import annotations

from app.registry.postprocess import reconcile_ebus_sampling_from_narrative
from app.registry.schema import RegistryRecord


def test_reconcile_ebus_sampling_from_site_block_upgrades_node_events() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "11L",
                            "action": "inspected_only",
                            "outcome": None,
                            "evidence_quote": "Station 11L inspected only.",
                        }
                    ],
                }
            }
        }
    )

    note_text = (
        "Site 1: station 11L - 8mm node\n"
        "The site was sampled with TBNA.\n"
    )

    warnings = reconcile_ebus_sampling_from_narrative(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.linear_ebus is not None
    events = record.procedures_performed.linear_ebus.node_events
    assert events
    assert events[0].station.upper() == "11L"
    assert events[0].action == "needle_aspiration"
    assert "sample" in (events[0].evidence_quote or "").lower() or "tbna" in (events[0].evidence_quote or "").lower()
    assert any("EBUS_NARRATIVE_RECONCILE" in str(w) for w in warnings)


def test_reconcile_ebus_sampling_normalizes_substation_event_key() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "11Rs",
                            "action": "inspected_only",
                            "outcome": None,
                            "evidence_quote": "Station 11Rs inspected only.",
                        }
                    ],
                }
            }
        }
    )

    note_text = (
        "Site 1: The 11Rs lymph node was sampled.\n"
        "Four EBUS-TBNA passes were performed.\n"
    )

    warnings = reconcile_ebus_sampling_from_narrative(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.linear_ebus is not None
    events = record.procedures_performed.linear_ebus.node_events
    assert events
    assert events[0].station == "11RS"
    assert events[0].action == "needle_aspiration"
    assert any("EBUS_NARRATIVE_RECONCILE" in str(w) for w in warnings)


def test_reconcile_ebus_sampling_does_not_treat_total_samples_as_station_seven() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "7",
                            "action": "inspected_only",
                            "outcome": None,
                            "evidence_quote": "7 (subcarinal) node",
                        }
                    ],
                }
            }
        }
    )

    note_text = (
        "Transbronchial cryobiopsy was performed with 1.1mm cryoprobe.\n"
        "Freeze time of 6 seconds were used.\n"
        "Total 7 samples were collected.\n"
    )

    warnings = reconcile_ebus_sampling_from_narrative(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.linear_ebus is not None
    events = record.procedures_performed.linear_ebus.node_events
    assert events
    assert events[0].station.strip().upper() == "7"
    assert events[0].action == "inspected_only"
    assert not any("EBUS_NARRATIVE_RECONCILE" in str(w) for w in warnings)
