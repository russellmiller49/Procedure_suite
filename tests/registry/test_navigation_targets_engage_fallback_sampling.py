from __future__ import annotations

from app.registry.processing.navigation_targets import extract_navigation_targets


def test_extract_navigation_targets_engage_fallback_extracts_sampling_counts_and_gauges() -> None:
    note_text = (
        "Robotic navigation bronchoscopy was performed with Ion platform.\n"
        "Ion robotic catheter was used to engage the Anterior Segment of RUL (RB3).\n"
        "Target lesion is about 1 cm in diameter.\n"
        "Transbronchial needle aspiration was performed with 21G Needle and 23G Needle through the catheter. "
        "Total 6 samples were collected.\n"
        "Transbronchial cryobiopsy was performed with 1.1mm cryoprobe. Freeze time of 6 seconds were used. "
        "Total 7 samples were collected.\n"
        "Transbronchial brushing was performed with cytology brush.\n"
        "\n"
        "EBUS-Findings\n"
        "Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle.\n"
    )

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 1
    target = targets[0]
    assert target.get("target_lobe") == "RUL"

    tools = target.get("sampling_tools_used") or []
    assert any("Needle" in t and "21G" in t and "23G" in t for t in tools)
    assert "Cryoprobe" in tools
    assert "Brush" in tools
    assert target.get("number_of_needle_passes") == 6
    assert target.get("number_of_cryo_biopsies") == 7


def test_extract_navigation_targets_prefers_confirmed_procedural_target_before_impression() -> None:
    note_text = """
    PROCEDURE IN DETAIL:
    Robotic navigation plan loaded from preoperative CT chest.
    Catheter navigated to right [sic] upper lobe target - operator note:
    target confirmed LEFT upper lobe, apical-posterior segment (LB1+2).
    Radial EBUS concentric and fluoroscopic spot image confirmed position.

    Nodule characteristics on radial EBUS:
    Target\tSize (CT)\trEBUS signal
    LUL apical-posterior\t2.8 cm\tConcentric

    IMPRESSION/PLAN:
    1. Technically successful robotic navigational bronchoscopy with rEBUS confirmation of LUL 2.8 cm target.
    """.strip()

    targets = extract_navigation_targets(note_text)

    assert len(targets) == 1
    assert targets[0]["target_location_text"] == "LUL apical-posterior segment (LB1+2)"
    assert targets[0]["target_lobe"] == "LUL"
