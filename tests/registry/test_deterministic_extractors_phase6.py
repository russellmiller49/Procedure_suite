import pytest

from modules.registry.deterministic_extractors import (
    extract_chest_tube,
    extract_ipc,
    extract_navigational_bronchoscopy,
    run_deterministic_extractors,
)


def test_navigation_robotic_bronch_abbrev_triggers():
    text = "Proc: EBUS-TBNA + Robotic Bronch (Galaxy)"
    assert extract_navigational_bronchoscopy(text) == {"navigational_bronchoscopy": {"performed": True}}


@pytest.mark.parametrize(
    "text",
    [
        "Robotic Bronch performed.",
        "Galaxy robotic bronch performed.",
        "Noah robotic bronch performed.",
    ],
)
def test_navigation_platforms_trigger_without_bronchoscopy_suffix(text: str):
    assert extract_navigational_bronchoscopy(text) == {"navigational_bronchoscopy": {"performed": True}}


def test_ipc_pleurx_placement_extracts_brand_side_indication():
    text = (
        "Procedure: Rt PleurX Catheter Placement.\n"
        "Indication: Malignant pleural effusion.\n"
        "Steps: Tunnel 7.5cm. Seldinger technique."
    )
    out = extract_ipc(text)
    assert out.get("ipc", {}).get("performed") is True
    assert out.get("ipc", {}).get("action") == "Insertion"
    assert out.get("ipc", {}).get("side") == "Right"
    assert out.get("ipc", {}).get("catheter_brand") == "PleurX"
    assert out.get("ipc", {}).get("tunneled") is True
    assert out.get("ipc", {}).get("indication") == "Malignant effusion"


def test_ipc_does_not_fire_for_pigtail_chest_tube():
    text = "A pigtail catheter was inserted for pleural drainage."
    assert extract_ipc(text) == {}


def test_run_deterministic_extractors_includes_pleural_ipc():
    text = "Procedure: PleurX catheter placement for malignant pleural effusion."
    seed = run_deterministic_extractors(text)
    assert seed.get("pleural_procedures", {}).get("ipc", {}).get("performed") is True


def test_chest_tube_existing_left_in_place_maps_to_repositioning() -> None:
    text = "Existing chest tube was left in place and connected to suction."
    out = extract_chest_tube(text)
    assert out.get("chest_tube", {}).get("performed") is True
    assert out.get("chest_tube", {}).get("action") == "Repositioning"
