from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.deterministic_extractors import (
    classify_stent_action,
    extract_endobronchial_biopsy,
    extract_sedation_airway,
)
from app.registry.postprocess import enrich_procedure_success_status
from app.registry.postprocess.complications_reconcile import _infer_nashville_bleeding_grade
from app.registry.schema import RegistryRecord


# --- bleeding-context window fallback (grade fabrication) --------------------


def test_blocker_for_blood_soiling_still_grade_3() -> None:
    text = (
        "There was significant bleeding from biopsy sites. "
        "An endobronchial blocker was placed to prevent blood soiling of the contralateral lung."
    )
    grade, _ = _infer_nashville_bleeding_grade(text)
    assert grade == 3


def test_unrelated_surgery_mention_does_not_upgrade_bleeding_grade() -> None:
    text = (
        "Moderate bleeding was encountered at the biopsy site and controlled with epinephrine "
        "and cold saline. The mass will be discussed at tumor board for possible surgery."
    )
    grade, _ = _infer_nashville_bleeding_grade(text)
    assert grade == 2


def test_preop_transfusion_with_negated_bleeding_stays_grade_0() -> None:
    text = (
        "There was no significant bleeding. The patient was transfused two units "
        "preoperatively for chronic anemia."
    )
    grade, _ = _infer_nashville_bleeding_grade(text)
    assert grade in (None, 0)


def test_status_post_cabg_does_not_upgrade_mild_oozing() -> None:
    text = (
        "Mild oozing at the biopsy site resolved with suction. The patient is status post "
        "coronary artery bypass surgery."
    )
    grade, _ = _infer_nashville_bleeding_grade(text)
    assert grade == 1


# --- EBUS stations/structures counting ---------------------------------------


def _ev(d: dict) -> dict:
    d.setdefault("evidence_quote", "EBUS-TBNA sampling documented.")
    return d


def test_same_lesion_does_not_double_bill_31629_and_31652() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        _ev({"station": None, "target_text": "right upper lobe mass", "action": "needle_aspiration"})
                    ],
                },
                "peripheral_tbna": {"performed": True, "targets_sampled": ["right upper lobe mass"]},
            }
        }
    )
    codes, _r, _w = derive_all_codes_with_meta(record)
    assert not ("31629" in codes and "31652" in codes)


def test_nonstation_target_does_not_upcode_two_stations_to_31653() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        _ev({"station": "7", "action": "needle_aspiration"}),
                        _ev({"station": "4R", "action": "needle_aspiration"}),
                        _ev({"station": None, "target_text": "subcarinal mass", "action": "needle_aspiration"}),
                    ],
                }
            }
        }
    )
    codes, _r, _w = derive_all_codes_with_meta(record)
    assert "31652" in codes
    assert "31653" not in codes


def test_pure_nonstation_structure_still_derives_31652() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        _ev({"station": None, "target_text": "left pulmonary artery mass", "action": "needle_aspiration"})
                    ],
                }
            }
        }
    )
    codes, _r, _w = derive_all_codes_with_meta(record)
    assert "31652" in codes


# --- transbronchial forceps biopsies are not endobronchial biopsy ------------


def test_transbronchial_forceps_biopsies_not_misrouted_to_ebbx() -> None:
    text = (
        "PROCEDURE: A right lower lobe mass was seen on CT. The bronchoscope was introduced. "
        "Transbronchial forceps biopsies were obtained from the right lower lobe under "
        "fluoroscopic guidance."
    )
    assert extract_endobronchial_biopsy(text) == {}


def test_guide_sheath_forceps_biopsies_not_misrouted_to_ebbx() -> None:
    text = (
        "The guide sheath was advanced to the left lower lobe mass under fluoroscopic "
        "guidance. Multiple forceps biopsies were obtained."
    )
    assert extract_endobronchial_biopsy(text) == {}


# --- stent removal with scope-as-instrument phrasing --------------------------


def test_scope_as_instrument_removal_still_detected() -> None:
    classified = classify_stent_action(
        "The rigid bronchoscope was used to remove the stent from the left mainstem."
    )
    assert classified["removal"] is True


def test_using_scope_we_removed_stent_still_detected() -> None:
    classified = classify_stent_action(
        "Using the flexible bronchoscope, we removed the migrated stent with forceps."
    )
    assert classified["removal"] is True


# --- negated partial-achievement language stays Failed ------------------------


def test_negated_reopen_percent_language_stays_failed() -> None:
    text = "We were unable to reopen the airway to 50% of normal and the procedure failed to achieve recanalization."
    record = RegistryRecord.model_validate({})
    enrich_procedure_success_status(record, text)
    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Failed"


# --- failed LMA then intubated is ETT -----------------------------------------


def test_failed_lma_then_intubated_is_ett() -> None:
    result = extract_sedation_airway(
        "General anesthesia. The LMA was removed due to poor seal and the patient was intubated by anesthesia."
    )
    assert result.get("airway_type") == "ETT"
