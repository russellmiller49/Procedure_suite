from __future__ import annotations

from modules.registry.schema.adapters.v3_to_v2 import convert_v3_to_v2
from modules.registry.schema.ebus_events import NodeInteraction
from modules.registry.schema.ip_v3_extraction import EvidenceSpan, IPRegistryV3, ProcedureEvent, ProcedureTarget


def test_schema_refactor_imports_smoke() -> None:
    import modules.registry.schema  # noqa: F401
    import modules.registry.schema.ebus_events  # noqa: F401
    import modules.registry.schema.granular_logic  # noqa: F401
    import modules.registry.schema.granular_models  # noqa: F401
    import modules.registry.schema.ip_v3_extraction  # noqa: F401
    import modules.registry.schema.v2_dynamic  # noqa: F401
    import proc_schemas.registry.ip_v3  # noqa: F401

    node = NodeInteraction(
        station="7",
        action="needle_aspiration",
        outcome="benign",
        evidence_quote="FNA of station 7 performed.",
    )
    dumped = node.model_dump()
    assert dumped["station"] == "7"
    assert dumped["action"] == "needle_aspiration"


def test_v3_extraction_to_v2_projection_smoke() -> None:
    v3 = IPRegistryV3(
        note_id="note_1",
        source_filename="note_1.txt",
        procedures=[
            ProcedureEvent(
                event_id="e1",
                type="linear_ebus",
                target=ProcedureTarget(station="4R"),
                evidence=EvidenceSpan(quote="EBUS TBNA of station 4R."),
            ),
            ProcedureEvent(
                event_id="e2",
                type="linear_ebus",
                target=ProcedureTarget(station="7"),
                evidence=EvidenceSpan(quote="EBUS TBNA of station 7."),
            ),
            ProcedureEvent(
                event_id="e3",
                type="linear_ebus",
                target=ProcedureTarget(station="7"),
                evidence=EvidenceSpan(quote="Repeat sampling of station 7."),
            ),
        ],
    )

    v2 = convert_v3_to_v2(v3)
    assert v2.procedures_performed is not None
    assert v2.procedures_performed.linear_ebus is not None
    assert v2.procedures_performed.linear_ebus.performed is True
    assert v2.procedures_performed.linear_ebus.stations_sampled == ["4R", "7"]
    assert v2.linear_ebus_stations == ["4R", "7"]
    assert v2.ebus_stations_sampled == ["4R", "7"]

