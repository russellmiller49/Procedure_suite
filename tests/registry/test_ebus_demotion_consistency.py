from __future__ import annotations

from app.registry.postprocess import (
    reconcile_ebus_node_event_consistency,
    sanitize_ebus_events,
)
from app.registry.schema import RegistryRecord


def _record_with_events() -> RegistryRecord:
    return RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["4R", "10R"],
                    "node_events": [
                        {
                            "station": "4R",
                            "action": "needle_aspiration",
                            "rose_result": "malig",
                            "evidence_quote": "EBUS-TBNA sampling of station 4R was performed with 4 passes.",
                        },
                        {
                            "station": "10R",
                            "action": "needle_aspiration",
                            "rose_result": "malig",
                            "evidence_quote": "Station 10R met sampling criteria.",
                        },
                    ],
                }
            },
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "4R", "sampled": True},
                    {"station": "10R", "sampled": True},
                ]
            },
        }
    )


NOTE_TEXT = (
    "EBUS survey performed. Station 10R measured 6 mm and met sampling criteria but was not sampled.\n"
    "EBUS-TBNA sampling of station 4R was performed with 4 passes. ROSE malignant at 4R.\n"
)


def test_demoted_station_loses_rose_and_granular_sampled_flag() -> None:
    record = _record_with_events()
    warnings = sanitize_ebus_events(record, NOTE_TEXT)
    warnings.extend(reconcile_ebus_node_event_consistency(record, NOTE_TEXT))

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    by_station = {str(e.station).upper(): e for e in (linear.node_events or [])}

    assert by_station["4R"].action == "needle_aspiration"
    assert by_station["4R"].rose_result == "malig"

    assert by_station["10R"].action == "inspected_only"
    # An inspected-only node cannot carry a needle-cytology result.
    assert by_station["10R"].rose_result is None

    assert linear.stations_sampled == ["4R"]

    detail = {str(d.station).upper(): d for d in (record.granular_data.linear_ebus_stations_detail or [])}  # type: ignore[union-attr]
    assert detail["4R"].sampled is True
    assert detail["10R"].sampled is False


def test_consistency_pass_is_noop_when_events_are_coherent() -> None:
    record = _record_with_events()
    # Only 4R sampled per note; run sanitize first so state is already coherent.
    sanitize_ebus_events(record, NOTE_TEXT)
    warnings = reconcile_ebus_node_event_consistency(record, NOTE_TEXT)
    warnings2 = reconcile_ebus_node_event_consistency(record, NOTE_TEXT)
    # Second run has nothing left to fix.
    assert not any("EBUS_NODE_EVENT_CONSISTENCY" in str(w) for w in warnings2)
