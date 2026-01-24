from __future__ import annotations

from modules.registry.postprocess import populate_ebus_node_events_fallback
from modules.registry.schema import RegistryRecord


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

