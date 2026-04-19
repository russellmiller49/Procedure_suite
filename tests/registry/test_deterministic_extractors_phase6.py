import pytest

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.deterministic_extractors import (
    extract_airway_stent,
    extract_blvr,
    extract_bpf_sealant,
    extract_chest_tube,
    extract_endobronchial_biopsy,
    extract_ipc,
    extract_navigational_bronchoscopy,
    extract_primary_indication,
    extract_therapeutic_aspiration,
    extract_transbronchial_cryobiopsy,
    run_deterministic_extractors,
)
from app.registry.schema import RegistryRecord


def test_navigation_robotic_bronch_abbrev_triggers():
    text = "Proc: EBUS-TBNA + Robotic Bronch (Galaxy)"
    assert extract_navigational_bronchoscopy(text) == {"navigational_bronchoscopy": {"performed": True}}


def test_extract_primary_indication_strips_header_residue_and_consent_boilerplate() -> None:
    note_text = (
        "INDICATION FOR OPERATION: [REDACTED]is a 73 year old-year-old male who presents with "
        "lung mass, multiple lung nodules, mediastinal/hilar lymphadenopathy, and LLL lobar atelectasis. "
        "The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient "
        "or surrogate in detail. Patient or surrogate indicated a wish to proceed with surgery and informed consent was signed.\n"
        "PREOPERATIVE DIAGNOSIS: R91.8\n"
    )

    indication = extract_primary_indication(note_text)
    assert indication is not None
    assert indication.lower().startswith("lung mass")
    assert "for operation" not in indication.lower()
    assert "informed consent" not in indication.lower()


def test_extract_primary_indication_prefers_operation_header_over_ebus_indications_label() -> None:
    note_text = (
        "NOTE_ID: note_032 SOURCE_FILE: note_032.txt INDICATION FOR OPERATION: This is a 73 year old male who presents with "
        "lung mass and mediastinal adenopathy.\n"
        "EBUS-Findings\n"
        "Indications: Diagnostic and Staging\n"
    )

    indication = extract_primary_indication(note_text)
    assert indication == "lung mass and mediastinal adenopathy"


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
    ebx = out.get("endobronchial_biopsy") or {}
    assert ebx.get("performed") is True
    assert ebx.get("locations") == ["RLL"]


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


def test_run_deterministic_extractors_marks_inspection_only_ebus_and_elastography() -> None:
    note_text = (
        "INSTRUMENT:\n"
        "Linear EBUS\n"
        "\n"
        "EBUS-Findings\n"
        "Indications: Diagnostic\n"
        "Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node\n"
        "11Ri lymph node\n"
        "No biopsies taken based upon ultrasound appearance\n"
        "Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.\n"
        "Lymph Nodes Evaluated:\n"
        "Site 5: The 11Ri lymph node was < 10 mm on CT. "
        "The site was not sampled: Sampling this lymph node was not clinically indicated. "
        "Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. "
        "The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.\n"
    )

    seed = run_deterministic_extractors(note_text)
    linear = seed.get("procedures_performed", {}).get("linear_ebus") or {}

    assert linear.get("performed") is True
    assert linear.get("elastography_used") is True
    assert not (linear.get("stations_sampled") or [])


def test_run_deterministic_extractors_extracts_fibrinolytic_therapy_from_subsequent_day_note() -> None:
    note_text = (
        "PROCEDURE:\n"
        "32562 Instillation(s), via chest tube/catheter, agent for fibrinolysis; subsequent day\n"
        "Date of chest tube insertion: 12/15/25\n"
        "10 mg/5 mg tPA/DNase dose #: 4\n"
        "Instillation of agents for fibrinolysis (subsequent)\n"
    )

    seed = run_deterministic_extractors(note_text)
    fibrinolytic = seed.get("pleural_procedures", {}).get("fibrinolytic_therapy") or {}

    assert fibrinolytic.get("performed") is True
    assert set(fibrinolytic.get("agents") or []) == {"tPA", "DNase"}
    assert fibrinolytic.get("tpa_dose_mg") == 10.0
    assert fibrinolytic.get("dnase_dose_mg") == 5.0
    assert fibrinolytic.get("number_of_doses") == 4


def test_extract_transbronchial_cryobiopsy_does_not_fire_for_cryoprobe_clot_removal_with_endobronchial_pathology_word() -> None:
    note_text = (
        "Left Lung Proximal Airways: No evidence of mass, lesions, bleeding or other endobronchial pathology.\n"
        "Cryoprobe 1.1mm Cryoprobe used for excellent clot removal.\n"
    )
    assert extract_transbronchial_cryobiopsy(note_text) == {}


def test_extract_transbronchial_cryobiopsy_does_not_fire_when_specimen_none_is_present_and_cryoprobe_is_therapeutic() -> None:
    note_text = (
        "Right Lung Proximal Airways: No evidence of mass, lesions, bleeding or other endobronchial pathology.\n"
        "Cryoprobe 1.1mm Cryoprobe used for excellent clot removal.\n"
        "SPECIMEN(S): --None\n"
    )

    assert extract_transbronchial_cryobiopsy(note_text) == {}

    seed = run_deterministic_extractors(note_text)
    assert seed.get("procedures_performed", {}).get("transbronchial_cryobiopsy") is None
    assert seed.get("procedures_performed", {}).get("cryotherapy", {}).get("performed") is True


def test_extract_blvr_does_not_fire_for_previously_placed_valves_in_good_position() -> None:
    note_text = (
        "Within the right upper lobe the previously placed endobronchial valves were visualized. "
        "The valves appeared well placed and in good position."
    )
    assert extract_blvr(note_text) == {}


def test_extract_airway_stent_removal_only_not_revision_from_previously_placed_stent() -> None:
    note_text = (
        "Findings: the previously placed stent in place with 90% obstruction.\n"
        "We elected to remove the stent currently in place.\n"
        "We elected not to place a stent at this point in time.\n"
    )

    out = extract_airway_stent(note_text)
    stent = out.get("airway_stent") or {}
    assert stent.get("performed") is True
    assert stent.get("action") == "Removal"
    assert stent.get("action_type") == "removal"
    assert stent.get("airway_stent_removal") is True


def test_extract_therapeutic_aspiration_detects_thereapeutic_typo() -> None:
    note_text = (
        "Thereapeutic aspiration performed at the end of the procedure for retained blood and secretions."
    )
    out = extract_therapeutic_aspiration(note_text)
    assert out.get("therapeutic_aspiration", {}).get("performed") is True


def test_extract_bpf_sealant_fires_for_alveolar_pleural_fistula_glue_instillation() -> None:
    note_text = (
        "Preoperative diagnosis: Alveolar pleural fistula.\n"
        "A catheter was advanced and fibrin glue was instilled to seal the fistula.\n"
    )
    out = extract_bpf_sealant(note_text)
    assert out.get("bpf_sealant", {}).get("performed") is True


def test_run_deterministic_extractors_derives_cryotherapy_from_cryoprobe_ablation_row() -> None:
    note_text = (
        "Endobronchial obstruction at RML was treated with the following modalities:\n"
        "Modality  Tools  Setting/Mode  Duration  Results\n"
        "Cryoprobe  1.7mm probe    30sec freeze-thaw cycles; total 6 applications  Ablation\n"
        "Balloon dilation was performed at RML.\n"
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.procedures_performed is not None
    assert record.procedures_performed.cryotherapy is not None
    assert record.procedures_performed.cryotherapy.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31641" in codes


def test_run_deterministic_extractors_derives_mechanical_debulking_from_granulation_row() -> None:
    note_text = (
        "Area of stenosis at the right middle lobe was treated with the following modalities:\n"
        "Modality  Tools  Setting/Mode  Duration  Results\n"
        "Mechanical  Pulmonary alligator forceps  N/A  N/A  Good granulation tissue removal from distal RML bronchus\n"
        "Cryospray  Cryospray cryotherapy catheter  Low-flow  10-second application x 5 total applications  "
        "Excellent application of spray cryotherapy to proximal RML bronchus and around the RML take-off\n"
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.procedures_performed is not None
    assert record.procedures_performed.mechanical_debulking is not None
    assert record.procedures_performed.mechanical_debulking.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31640" in codes


def test_run_deterministic_extractors_extracts_navigation_imaging_equipment() -> None:
    note_text = (
        "Robotic navigation bronchoscopy was performed with Ion platform.\n"
        "Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation. "
        "Cios Spin system was used for evaluation of nodule location. "
        "Low dose spin was performed to acquire CT imaging. "
        "This was passed on to Ion platform system for reconstruction and nodule location. "
        "The 3D images was interpreted on an independent workstation (Ion). "
        "Fiducial marker was loaded with bone wax and placed under fluoroscopy guidance.\n"
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.equipment is not None
    assert record.equipment.navigation_platform == "Ion"
    assert record.equipment.cbct_used is True
    assert record.equipment.augmented_fluoroscopy is True
    assert record.equipment.fluoroscopy_used is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "77012" in codes
    assert "76377" in codes
