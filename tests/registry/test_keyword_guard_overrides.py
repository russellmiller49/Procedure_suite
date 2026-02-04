from __future__ import annotations

from modules.registry.schema import RegistryRecord
from modules.registry.self_correction.keyword_guard import apply_required_overrides


def test_apply_required_overrides_does_not_force_peripheral_tbna_from_ebus_station_list() -> None:
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"linear_ebus": {"performed": True, "stations_sampled": ["11L"]}}}
    )
    note_text = (
        "Linear EBUS: Multiple EBUS-TBNA passes were obtained from the following station(s):\n\n"
        "11L (abnormally large lymph node versus mass)\n"
    )
    updated, warnings = apply_required_overrides(note_text, record)

    pp = updated.procedures_performed
    assert pp is not None
    assert pp.peripheral_tbna is None or pp.peripheral_tbna.performed is not True
    assert not any("peripheral/lung tbna" in w.lower() for w in warnings)


def test_apply_required_overrides_adds_transbronchial_biopsy_for_radial_ebus_forceps_biopsy_language() -> None:
    record = RegistryRecord()
    note_text = (
        "The bronchoscope was inserted into the airway and advanced into the left upper lobe. "
        "A large sheath catheter with radial ultrasound to the area of known nodule and a concentric view "
        "of the lesion was identified with the radial EBUS. Biopsies were then performed with a variety of "
        "instruments to include peripheral needle forceps and brush with fluoroscopic guidance through the sheath."
    )
    updated, warnings = apply_required_overrides(note_text, record)

    pp = updated.procedures_performed
    assert pp is not None
    assert pp.transbronchial_biopsy is not None
    assert pp.transbronchial_biopsy.performed is True
    assert any("transbronchial" in w.lower() for w in warnings)


def test_apply_required_overrides_adds_peripheral_tbna_for_endobronchial_needle_biopsy_distinct_from_ebus() -> None:
    record = RegistryRecord.model_validate({"procedures_performed": {"linear_ebus": {"performed": True}}})
    note_text = (
        "A shiny vascular obstructive endobronchial tumor was visualized. "
        "Subsequently 6 endobronchial needle biopsies of the nodule were performed. "
        + ("x" * 500)
        + " The UC180F convex probe EBUS bronchoscope was introduced. Sampling by transbronchial needle aspiration "
        "was performed in station 4L and station 7."
    )

    updated, warnings = apply_required_overrides(note_text, record)
    pp = updated.procedures_performed
    assert pp is not None
    assert pp.peripheral_tbna is not None
    assert pp.peripheral_tbna.performed is True
    assert any("needle biopsy of a lesion" in w.lower() for w in warnings)


def test_apply_required_overrides_sets_fibrinolysis_without_chest_tube_insertion_for_date_of_insertion_line() -> None:
    record = RegistryRecord()
    note_text = (
        "PROCEDURE:\n"
        "32562 Instillation(s), via chest tube/catheter, agent for fibrinolysis; subsequent day\n\n"
        "Date of chest tube insertion: 12/15/25\n"
        "10 mg/5 mg tPA/DNase dose #: 3\n"
    )

    updated, warnings = apply_required_overrides(note_text, record)
    pleural = updated.pleural_procedures
    assert pleural is not None
    assert pleural.fibrinolytic_therapy is not None
    assert pleural.fibrinolytic_therapy.performed is True
    assert set(pleural.fibrinolytic_therapy.agents or []) == {"tPA", "DNase"}
    assert pleural.fibrinolytic_therapy.tpa_dose_mg == 10.0
    assert pleural.fibrinolytic_therapy.dnase_dose_mg == 5.0
    assert pleural.fibrinolytic_therapy.number_of_doses == 3
    assert pleural.chest_tube is None or pleural.chest_tube.performed is not True
    assert any("fibrinolytic_therapy.performed" in w for w in warnings)


def test_apply_required_overrides_adds_mechanical_debulking_for_snare_en_bloc_language() -> None:
    record = RegistryRecord()
    note_text = (
        "An electrocautery snare was utilized to ensnare the endobronchial tumor and remove it from its stalk. "
        "The mass was removed en bloc with the bronchoscope.\n"
    )

    updated, warnings = apply_required_overrides(note_text, record)
    pp = updated.procedures_performed
    assert pp is not None
    assert pp.mechanical_debulking is not None
    assert pp.mechanical_debulking.performed is True
    assert any("mechanical_debulking" in w for w in warnings)


def test_apply_required_overrides_does_not_force_mechanical_debulking_for_mucus_cleanout() -> None:
    record = RegistryRecord()
    note_text = (
        "The patient's known Silicone Y-stent was well positioned. "
        "Through a combination of mechanical debulking with the bronchoscope tip and forceps debulking, "
        "the adhesive mucous was slowly removed, with near complete recanalization of the stents."
    )

    updated, warnings = apply_required_overrides(note_text, record)
    pp = updated.procedures_performed
    assert pp is None or pp.mechanical_debulking is None or pp.mechanical_debulking.performed is not True
    assert not any("mechanical_debulking" in w for w in warnings)
