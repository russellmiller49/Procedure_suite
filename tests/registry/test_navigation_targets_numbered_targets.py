from __future__ import annotations

from modules.registry.processing.navigation_targets import extract_navigation_targets


def test_extract_navigation_targets_supports_numbered_targets() -> None:
    note_text = (
        "Target 1: RUL nodule\n"
        "Forceps biopsies x3\n"
        "Target 2: RLL nodule\n"
        "Forceps biopsies x2\n"
    )
    targets = extract_navigation_targets(note_text)

    assert len(targets) == 2
    assert targets[0]["target_number"] == 1
    assert targets[1]["target_number"] == 2

    assert targets[0].get("target_lobe") == "RUL"
    assert targets[1].get("target_lobe") == "RLL"

    assert "Unknown target" not in str(targets[0].get("target_location_text"))
    assert "Unknown target" not in str(targets[1].get("target_location_text"))

    assert "Forceps" in (targets[0].get("sampling_tools_used") or [])
    assert "Forceps" in (targets[1].get("sampling_tools_used") or [])
