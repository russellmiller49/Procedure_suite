from __future__ import annotations

from app.registry.processing.navigation_fiducials import apply_navigation_fiducials


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


def test_apply_navigation_fiducials_overwrites_unknown_target_location() -> None:
    data: dict[str, object] = {
        "granular_data": {
            "navigation_targets": [
                {"target_number": 1, "target_location_text": "Unknown target"},
            ]
        }
    }
    note_text = (
        "Robotic navigation bronchoscopy performed.\n"
        "Ion robotic catheter was used to engage the Superior Segment of RLL (RB6).\n"
        "Fiducial marker was loaded and placed under fluoroscopy guidance.\n"
    )

    changed = apply_navigation_fiducials(data, note_text)

    assert changed is True
    granular = data.get("granular_data")
    assert isinstance(granular, dict)
    targets = granular.get("navigation_targets")
    assert isinstance(targets, list)
    assert targets
    assert targets[0].get("target_location_text") != "Unknown target"
    assert targets[0].get("target_lobe") == "RLL"


def test_apply_navigation_fiducials_treats_placed_with_failed_retention_as_placed() -> None:
    data: dict[str, object] = {}
    note_text = (
        "Robotic navigation bronchoscopy performed.\n"
        "The Ion robotic catheter was used to engage the Lateral Segment of RML (RB4).\n"
        "Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance. "
        "However, this fiducial marker appeared to fall out and did not enter the nodule.\n"
    )

    changed = apply_navigation_fiducials(data, note_text)

    assert changed is True
    granular = data.get("granular_data")
    assert isinstance(granular, dict)
    targets = granular.get("navigation_targets")
    assert isinstance(targets, list)
    assert targets
    assert targets[0].get("fiducial_marker_placed") is True


def test_apply_navigation_fiducials_reads_target_in_segment_sentence() -> None:
    data: dict[str, object] = {
        "granular_data": {
            "navigation_targets": [
                {"target_number": 1, "target_location_text": "Unknown target"},
            ]
        }
    }
    note_text = (
        "Robotic navigation completed.\n"
        "Navigation completed to target in LLL posterior basal segment. Radial EBUS confirmed position.\n"
        "Three fiducials deployed around lesion margins under fluoroscopy.\n"
    )

    changed = apply_navigation_fiducials(data, note_text)

    assert changed is True
    granular = data.get("granular_data")
    assert isinstance(granular, dict)
    targets = granular.get("navigation_targets")
    assert isinstance(targets, list)
    assert targets
    assert targets[0].get("target_location_text") == "LLL posterior basal segment"
    assert targets[0].get("target_lobe") == "LLL"


def test_apply_navigation_fiducials_reads_target_in_was_reached_sentence() -> None:
    data: dict[str, object] = {
        "granular_data": {
            "navigation_targets": [
                {"target_number": 1, "target_location_text": "Unknown target"},
            ]
        }
    }
    note_text = (
        "Computer-assisted guided bronchoscopy performed.\n"
        "Target in the apicoposterior LUL was reached with guided bronchoscopy.\n"
        "Fiducials were placed adjacent to the lesion after tissue sampling.\n"
    )

    changed = apply_navigation_fiducials(data, note_text)

    assert changed is True
    granular = data.get("granular_data")
    assert isinstance(granular, dict)
    targets = granular.get("navigation_targets")
    assert isinstance(targets, list)
    assert targets
    assert targets[0].get("target_location_text") == "apicoposterior LUL"
    assert targets[0].get("target_lobe") == "LUL"
