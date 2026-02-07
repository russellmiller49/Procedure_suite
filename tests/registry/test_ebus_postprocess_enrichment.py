from __future__ import annotations

from app.registry.postprocess import (
    enrich_ebus_node_event_outcomes,
    enrich_linear_ebus_needle_gauge,
)
from app.registry.schema import RegistryRecord


def test_enrich_ebus_node_event_outcomes_maps_granulomas_and_lymphocytes_to_benign() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "11L",
                            "action": "needle_aspiration",
                            "outcome": "deferred_to_final_path",
                            "evidence_quote": "11L sampled",
                        },
                        {
                            "station": "7",
                            "action": "needle_aspiration",
                            "outcome": "deferred_to_final_path",
                            "evidence_quote": "7 sampled",
                        },
                    ],
                }
            }
        }
    )

    note_text = (
        "ROSE evaluation yielded multiple granulomas from the 11L station and adequate lymphocytes from station 7."
    )
    warnings = enrich_ebus_node_event_outcomes(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    by_station = {e.station.upper(): e for e in linear.node_events}
    assert by_station["11L"].outcome == "benign"
    assert by_station["7"].outcome == "benign"
    assert any("AUTO_EBUS_OUTCOME" in w for w in warnings)


def test_propagate_linear_ebus_needle_gauge_sets_needle_gauge_string() -> None:
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"linear_ebus": {"performed": True}}}
    )
    warnings = enrich_linear_ebus_needle_gauge(record, "Sampling by transbronchial needle aspiration using a 22 gauge needle.")

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.needle_gauge == "22G"
    assert any("AUTO_EBUS_NEEDLE_GAUGE" in w for w in warnings)
