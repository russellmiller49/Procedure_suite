from __future__ import annotations

from app.registry.processing.navigation_targets import extract_navigation_targets


def test_extract_navigation_targets_inline_target_stops_at_header_and_truncates() -> None:
    long_tail = " very long description" * 20
    note_text = (
        "INDICATION:\n"
        "Pulmonary nodule\n"
        f"Target: 20mm nodule in LLL{long_tail}\n"
        "PROCEDURE:\n"
        "Robotic bronchoscopy performed.\n"
        "Transbronchial needle aspiration performed.\n"
    )

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 1
    loc = targets[0]["target_location_text"]
    assert "PROCEDURE" not in loc
    assert "Transbronchial needle aspiration" not in loc
    assert loc.startswith("20mm nodule in LLL")
    assert targets[0].get("target_lobe") == "LLL"
    assert len(loc) <= 100


def test_extract_navigation_targets_inline_target_supports_literal_backslash_newlines() -> None:
    note_text = (
        "Indication: Suspected lung malignancy\\n"
        "Target: 20mm nodule in LLL\\n\\n"
        "PROCEDURE:\\n"
        "Robotic bronchoscopy performed.\\n"
        "The device was navigated to the LLL.\\n"
    )

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 1
    assert targets[0]["target_location_text"] == "20mm nodule in LLL"
    assert targets[0].get("target_lobe") == "LLL"


def test_extract_navigation_targets_inline_target_ct_characteristics() -> None:
    note_text = (
        "Indication: Lung nodule\\n"
        "Target: 15 mm part-solid nodule in RUL\\n"
        "PROCEDURE:\\n"
        "Robotic bronchoscopy performed.\\n"
    )

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 1
    assert targets[0].get("lesion_size_mm") == 15.0
    assert targets[0].get("ct_characteristics") == "Part-solid"


def test_extract_navigation_targets_single_target_enriches_cryo_and_rose_multiline() -> None:
    note_text = (
        "Indication: Evaluation of suspected lung malignancy\n"
        "Target: 16 mm pulmonary nodule in RUL\n"
        "\n"
        "Radial EBUS:\n"
        "Radial EBUS was performed through the working channel. rEBUS view: Eccentric.\n"
        "\n"
        "Sampling:\n"
        "Transbronchial needle aspiration performed using a 21G needle, 3 passes obtained.\n"
        "Transbronchial cryobiopsy performed using a 1.1 mm cryoprobe. Three samples obtained with freeze time of 4 seconds.\n"
        "\n"
        "ROSE Result:\n"
        "Atypical cells present, concerning for malignancy.\n"
    )

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 1
    target = targets[0]
    assert target.get("target_lobe") == "RUL"
    assert target.get("lesion_size_mm") == 16.0
    assert target.get("rebus_view") == "Eccentric"

    tools = target.get("sampling_tools_used") or []
    assert any("Needle" in t and "21" in t for t in tools)
    assert any("Cryoprobe" in t and "1.1" in t for t in tools)
    assert target.get("number_of_needle_passes") == 3
    assert target.get("number_of_cryo_biopsies") == 3
    assert target.get("rose_result") == "Atypical cells present, concerning for malignancy."
