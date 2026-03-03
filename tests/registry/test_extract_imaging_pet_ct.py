from __future__ import annotations

from pathlib import Path

from app.registry.aggregation.imaging.extract_pet_ct import extract_pet_ct_event


_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "case_events"


def _read(name: str) -> str:
    return (_FIXTURE_DIR / name).read_text()


def test_extract_pet_ct_dual_timepoint_suv() -> None:
    payload = extract_pet_ct_event(
        _read("pet_ct_dual_timepoint_suv.txt"),
        relative_day_offset=14,
        event_subtype="followup",
    )

    snapshot = payload["imaging_snapshot"]
    assert snapshot["modality"] == "pet_ct"
    assert snapshot["subtype"] == "followup"
    assert snapshot["relative_day_offset"] == 14

    qa_flags = set(payload["qa_flags"])
    assert "no_hypermetabolic_thoracic_nodes" in qa_flags

    targets = payload["targets_update"]["peripheral_targets"]
    assert targets
    first = targets[0]
    assert first["pet_suvmax"] == 4.1
    assert first["pet_delayed_suvmax"] == 6.1
    assert first["pet_avid"] is True
