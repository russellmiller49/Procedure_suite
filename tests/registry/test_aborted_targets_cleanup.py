from __future__ import annotations

from app.registry.postprocess import reconcile_aborted_targets
from app.registry.schema import RegistryRecord


def test_reconcile_aborted_targets_removes_inferred_segment_token_from_brushings() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "brushings": {
                    "performed": True,
                    "locations": ["LB3", "RB9"],
                }
            }
        }
    )

    note_text = (
        "Ion robotic catheter was used to engage the Anterior Segment of LUL (LB3).\n"
        "Second RLL target was attempted.\n"
        "Ion robotic catheter was used to engage the Lateral-basal Segment of RLL (RB9).\n"
        "2 spins were done to assess the area and the RLL nodule was not identified on the system. "
        "Due to inability to identify the nodule, we aborted the procedure.\n"
    )

    warnings = reconcile_aborted_targets(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.brushings is not None
    assert record.procedures_performed.brushings.locations == ["LB3"]
    assert any("ABORTED_TARGETS" in str(w) for w in warnings)

