from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.schema import RegistryRecord


def test_note272_stent_assessment_only_suppresses_31636() -> None:
    note_text = (
        "Left Lung: Stent well-seated. Defect seen in stent. Reassessment of stent position performed.\n"
        "Successful therapeutic aspiration was performed to clean out the trachea from mucus.\n"
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    # Simulate the failure mode: stent incorrectly labeled as a new placement.
    record_data = record.model_dump()
    record_data.setdefault("procedures_performed", {})["airway_stent"] = {
        "performed": True,
        "action": "Placement",
        "airway_stent_removal": False,
    }
    record = RegistryRecord(**record_data)

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.performed is True
    assert stent.action == "Assessment only"
    assert stent.airway_stent_removal is False
    assert any("Stent inspection-only" in warning for warning in outcome.warnings)

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31636" not in codes
    assert "31645" in codes


def test_note276_blvr_multi_lobe_drives_31647_31651_and_chartis_capture() -> None:
    note_text = """
    PROCEDURE:
    Bronchoscopic lung volume reduction (BLVR) with endobronchial valves.

    Balloon Occlusion: 1 Yes
    Chartis System: 1 Yes
    No/minimal collateral ventilation was present.

    Valve sizes used
    Airway\tValve
    RUL Apical\tZephyr size 4.0
    RML Medial\tSpiration size 9
    RML Lateral\tSpiration size 7
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)
    record_data = record.model_dump()
    record_data.setdefault("procedures_performed", {}).setdefault("blvr", {})["performed"] = True
    record = RegistryRecord(**record_data)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.granular_data is not None
    assert updated.granular_data.blvr_valve_placements is not None

    valve_lobes = {placement.target_lobe for placement in updated.granular_data.blvr_valve_placements}
    assert valve_lobes == {"RUL", "RML"}

    assert updated.granular_data.blvr_chartis_measurements is not None
    chartis_lobes = {m.lobe_assessed for m in updated.granular_data.blvr_chartis_measurements}
    assert chartis_lobes == {"RUL", "RML"}

    codes, _rationales, warnings = derive_all_codes_with_meta(updated)
    assert "31647" in codes
    assert "31651" in codes
    assert "31634" not in codes
    assert any("Suppressed 31634" in warning for warning in warnings)


def test_radial_marker_concentric_stenosis_does_not_trigger_radial_ebus() -> None:
    note_text = "Trachea: Proximal tracheal with concentric stenosis."
    record = RegistryRecord()

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is None or updated.procedures_performed.radial_ebus is None
    assert not any("Radial EBUS inferred" in warning for warning in outcome.warnings)

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31654" not in codes


def test_radial_marker_concentric_view_triggers_radial_ebus() -> None:
    note_text = "Radial EBUS showed a concentric view of the lesion."
    record = RegistryRecord(procedures_performed={"bal": {"performed": True}})

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.radial_ebus is not None
    assert updated.procedures_performed.radial_ebus.performed is True
    assert any("concentric/eccentric view" in warning for warning in outcome.warnings)

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31624" in codes
    assert "31654" in codes


def test_note274_intubation_31500_and_aspiration_material_location_and_stent_semantics() -> None:
    note_text = """
    INDICATION: recurrent hemoptysis with blood in the airway.

    PROCEDURE IN DETAIL:
    Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3) and Right Mainstem from mucus.
    Fiberoptic intubation via oral pathway was performed to introduce a 5.0 MLT ETT into the right mainstem bronchus.
    Pulmonary forceps were used to grasp the vascular plug and bring it more proximally.
    """

    seed = run_deterministic_extractors(note_text)
    assert seed.get("procedures_performed", {}).get("therapeutic_aspiration", {}).get("material") == "Mucus plug"
    assert "Trachea" in (seed.get("procedures_performed", {}).get("therapeutic_aspiration", {}).get("location") or "")
    assert seed.get("procedures_performed", {}).get("intubation", {}).get("performed") is True

    record_data = seed
    record_data.setdefault("procedures_performed", {})["airway_stent"] = {
        "performed": True,
        "action": "Revision/Repositioning",
        "airway_stent_removal": True,
    }
    record = RegistryRecord(**record_data)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Revision/Repositioning"
    assert stent.airway_stent_removal is False

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31500" in codes
    assert "31645" in codes
    assert "31638" in codes


def test_note352_aspiration_material_location_and_y_stent_type_capture() -> None:
    note_text = """
    ESTIMATED BLOOD LOSS: None

    PROCEDURE IN DETAIL:
    The stent remained in good position and the segments were patent in the Y stent.
    Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Right Mainstem, and Carina from mucus.
    """

    seed = run_deterministic_extractors(note_text)
    assert seed.get("procedures_performed", {}).get("therapeutic_aspiration", {}).get("material") == "Mucus plug"
    assert "Trachea" in (seed.get("procedures_performed", {}).get("therapeutic_aspiration", {}).get("location") or "")

    record_data = seed
    record_data.setdefault("procedures_performed", {})["airway_stent"] = {
        "performed": True,
        "action": "Assessment only",
    }
    record = RegistryRecord(**record_data)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Assessment only"
    assert stent.stent_type == "Y-Stent"

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31645" in codes
    assert "31636" not in codes
    assert "31638" not in codes


def test_stent_discussed_but_refused_clears_31636() -> None:
    note_text = (
        "Of note we considered airway stent placement; however the patient was reluctant to have stent placed.\n"
        "If I need to debulk again I will strongly advocate for placement of a covered tracheal stent.\n"
    )

    record = RegistryRecord(procedures_performed={"airway_stent": {"performed": True, "action": "Placement"}})
    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.performed is False

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31636" not in codes


def test_routine_anesthesia_ett_does_not_trigger_31500() -> None:
    note_text = "Following induction of general anesthesia a 7.5 ETT was placed and secured."

    seed = run_deterministic_extractors(note_text)
    assert seed.get("procedures_performed", {}).get("intubation") in (None, {})

    record = RegistryRecord(procedures_performed={"intubation": {"performed": True}})
    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.intubation is not None
    assert updated.procedures_performed.intubation.performed is False

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31500" not in codes
