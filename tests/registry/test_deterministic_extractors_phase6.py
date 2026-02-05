import pytest

from modules.registry.deterministic_extractors import (
    extract_chest_tube,
    extract_endobronchial_biopsy,
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


def test_forceps_biopsy_in_cavity_triggers_endobronchial_biopsy() -> None:
    note_text = (
        "During lavage, a cavity was visualized in the superior segment of the right lower lobe "
        "containing a well-demarcated soft tissue mass consistent with a mycetoma. "
        "Multiple forceps biopsies were obtained from the mass within the cavity."
    )
    out = extract_endobronchial_biopsy(note_text)
    assert out == {"endobronchial_biopsy": {"performed": True}}


def test_run_deterministic_extractors_airway_dilation_target_anatomy_with_evidence() -> None:
    note_text = "Balloon dilation was performed for tracheal stenosis using a 12 mm balloon."
    seed = run_deterministic_extractors(note_text)
    dilation = seed.get("procedures_performed", {}).get("airway_dilation") or {}
    assert dilation.get("performed") is True
    assert dilation.get("target_anatomy") == "Stenosis"

    evidence = seed.get("evidence") or {}
    assert evidence.get("procedures_performed.airway_dilation.target_anatomy")
    span = evidence["procedures_performed.airway_dilation.target_anatomy"][0]
    assert "stenosis" in note_text[span.start:span.end].lower()


def test_run_deterministic_extractors_balloon_occlusion_fields_with_evidence() -> None:
    note_text = (
        "Serial occlusion was performed using a 7 Fr Arndt endobronchial blocker positioned in the RUL bronchus. "
        "Air leak resolved after balloon occlusion."
    )
    seed = run_deterministic_extractors(note_text)
    balloon = seed.get("procedures_performed", {}).get("balloon_occlusion") or {}
    assert balloon.get("performed") is True
    assert "RUL bronchus" in (balloon.get("occlusion_location") or "")
    assert "air leak" in (balloon.get("air_leak_result") or "").lower()
    assert "7" in (balloon.get("device_size") or "")

    evidence = seed.get("evidence") or {}
    assert evidence.get("procedures_performed.balloon_occlusion.occlusion_location")
    assert evidence.get("procedures_performed.balloon_occlusion.air_leak_result")
    assert evidence.get("procedures_performed.balloon_occlusion.device_size")
