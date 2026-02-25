from __future__ import annotations

from pathlib import Path

from app.registry.aggregation.imaging.extract_ct import extract_ct_event


_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "case_events"


def _read(name: str) -> str:
    return (_FIXTURE_DIR / name).read_text()


def test_extract_ct_preop_nodule_growth() -> None:
    payload = extract_ct_event(
        _read("ct_preop_nodule_growth.txt"),
        relative_day_offset=-7,
        event_subtype="preop",
    )

    snapshot = payload["imaging_snapshot"]
    assert snapshot["modality"] == "ct"
    assert snapshot["subtype"] == "preop"
    assert snapshot["relative_day_offset"] == -7
    assert snapshot["response"] in {"Progression", "Mixed"}

    qa_flags = set(payload["qa_flags"])
    assert "no_mediastinal_adenopathy" in qa_flags

    targets = payload["targets_update"]["peripheral_targets"]
    assert targets
    first = targets[0]
    assert first["lobe"] == "RLL"
    assert first["size_mm_long"] == 22
    assert first["size_mm_short"] == 19
    assert first["size_mm_cc"] == 21
