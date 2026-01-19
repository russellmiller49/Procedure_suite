from __future__ import annotations

from modules.registry.processing.navigation_fiducials import apply_navigation_fiducials


def test_apply_navigation_fiducials_populates_target() -> None:
    data: dict[str, object] = {}
    note_text = (
        "PROCEDURE:\n"
        "Electromagnetic navigation bronchoscopy performed.\n"
        "Target lesion in RUL anterior segment.\n"
        "Fiducial markers placed.\n"
    )

    changed = apply_navigation_fiducials(data, note_text)

    assert changed is True
    granular = data.get("granular_data")
    assert isinstance(granular, dict)
    targets = granular.get("navigation_targets")
    assert isinstance(targets, list)
    assert targets and targets[0].get("fiducial_marker_placed") is True
    assert targets[0].get("target_number") == 1
    assert targets[0].get("target_lobe") == "RUL"
