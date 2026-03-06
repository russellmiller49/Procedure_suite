from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.processing.masking import mask_offset_preserving
from app.registry.deterministic_extractors import (
    extract_bleeding_intervention_required,
    run_deterministic_extractors,
)
from app.registry.postprocess import enrich_eus_b_sampling_details
from app.registry.postprocess.complications_reconcile import reconcile_complications_from_narrative
from app.registry.schema import RegistryRecord


def test_whole_lung_lavage_derives_32997_and_suppresses_bal() -> None:
    note_text = """
    WHOLE LUNG LAVAGE - PROCEDURE NOTE
    Pre/Post Dx: Pulmonary alveolar proteinosis.
    Procedure: Whole lung lavage (right lung)
    Double-lumen tube placement.
    Under general anesthesia with lung isolation, the right lung was lavaged with warmed normal saline
    in repeated aliquots until effluent cleared.
    Complications: none
    Disposition: ICU for post-procedure monitoring.
    """

    seed = run_deterministic_extractors(note_text)
    seed.setdefault("procedures_performed", {})["bal"] = {"performed": True}
    record = RegistryRecord(**seed)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.whole_lung_lavage is not None
    assert updated.procedures_performed.whole_lung_lavage.performed is True
    assert updated.procedures_performed.whole_lung_lavage.side == "Right"
    assert updated.procedures_performed.bal is not None
    assert updated.procedures_performed.bal.performed is False

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "32997" in codes
    assert "31624" not in codes


def test_bronchial_thermoplasty_session_extracts_and_derives_31660() -> None:
    note_text = """
    BRONCHIAL THERMOPLASTY - SESSION 2
    Anesthesia: Moderate sedation
    Scope advanced to right lower lobe bronchi.
    Thermoplasty catheter used; RF activations delivered to segmental/subsegmental airways per protocol.
    Total activations: 42.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.procedures_performed is not None
    assert record.procedures_performed.bronchial_thermoplasty is not None
    bt = record.procedures_performed.bronchial_thermoplasty
    assert bt.performed is True
    assert bt.session_number == 2
    assert bt.number_of_activations == 42
    assert bt.areas_treated == ["RLL"]

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31660" in codes
    assert "31661" not in codes


def test_transthoracic_core_biopsy_clears_peripheral_tbna_and_derives_32408() -> None:
    note_text = """
    ULTRASOUND-GUIDED TRANSTHORACIC NEEDLE BIOPSY - PROCEDURE NOTE
    Indication: Pleural-based RLL mass abutting chest wall.
    Procedure: Ultrasound-guided transthoracic core needle biopsy.
    Technique: Ultrasound used to identify pleural-based lesion and avoid intercostal vessels.
    Using real-time ultrasound guidance, coaxial technique used to obtain 4 core samples.
    """

    seed = run_deterministic_extractors(note_text)
    seed.setdefault("procedures_performed", {})["peripheral_tbna"] = {
        "performed": True,
        "targets_sampled": ["RLL", "Lung Mass"],
    }
    record = RegistryRecord(**seed)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.peripheral_tbna is not None
    assert updated.procedures_performed.peripheral_tbna.performed is False
    assert updated.pleural_procedures is not None
    assert updated.pleural_procedures.pleural_biopsy is not None
    biopsy = updated.pleural_procedures.pleural_biopsy
    assert biopsy.performed is True
    assert biopsy.guidance == "Ultrasound"
    assert biopsy.needle_type == "Cutting needle"
    assert biopsy.number_of_samples == 4

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "32408" in codes
    assert "31629" not in codes


def test_dynamic_bronchoscopy_for_airway_collapse_derives_31622() -> None:
    note_text = """
    PROCEDURE(S):
    Dynamic bronchoscopy with forced expiratory maneuver.
    CPAP titration during bronchoscopy.
    FINDINGS/DETAIL:
    Bronchoscopy performed with dynamic assessment at baseline and during forced exhalation.
    Severe posterior membrane invagination noted in distal trachea and bilateral main bronchi with >80% expiratory collapse.
    CPAP applied via mask and titrated; collapse improved substantially.
    No endobronchial lesion.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)
    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record

    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.diagnostic_bronchoscopy is not None
    assert updated.procedures_performed.diagnostic_bronchoscopy.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31622" in codes


def test_short_mucus_plug_note_derives_therapeutic_aspiration() -> None:
    note_text = (
        "[PATIENT] 57-year-old female with mucus plugging and lobar atelectasis. "
        "Bronchoscopy under moderate sedation. Large tenacious plug extracted from LLL with suction + forceps. "
        "Airways otherwise clear. No complications."
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.procedures_performed is not None
    assert record.procedures_performed.therapeutic_aspiration is not None
    aspiration = record.procedures_performed.therapeutic_aspiration
    assert aspiration.performed is True
    assert aspiration.material == "Mucus plug"
    assert aspiration.location == "LLL"

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31645" in codes


def test_presenting_hemoptysis_tamponade_note_does_not_trigger_31500_or_bleeding_complication() -> None:
    note_text = """
    BRONCHOSCOPY WITH ENDOBRONCHIAL TAMPONADE - MASSIVE HEMOPTYSIS
    Indication: 65-year-old male with brisk hemoptysis and respiratory compromise.
    Pre Dx: Massive hemoptysis
    Procedure(s): Emergency bronchoscopy; Selective intubation / endobronchial tamponade.
    Findings: Active bleeding from RUL; large clot burden.
    Technique: Airway suctioned; clot extracted. Bronchial blocker positioned to isolate RUL with cessation of spillover.
    Topical vasoconstrictor applied.
    Complications: none procedural
    """

    assert extract_bleeding_intervention_required(note_text) is None

    seed = run_deterministic_extractors(note_text)
    assert seed.get("procedures_performed", {}).get("intubation") in (None, {})

    record = RegistryRecord(**seed)
    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None

    warnings = reconcile_complications_from_narrative(updated, note_text)
    assert not any("BLEEDING_GRADE_DERIVED" in w for w in warnings)
    assert updated.complications is None or updated.complications.bleeding is None

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31500" not in codes
    assert "31645" in codes


def test_pal_valve_note_with_existing_chest_tube_does_not_bill_32551() -> None:
    note_text = """
    ENDOBRONCHIAL VALVES FOR PNEUMOTHORAX - PROCEDURE NOTE
    Indication: Persistent air leak after secondary spontaneous pneumothorax with chest tube in place.
    Procedure(s): Flexible bronchoscopy. Balloon occlusion localization. Endobronchial valve placement for air leak control.
    Technique: Sequential balloon occlusion performed to localize air leak based on chest tube bubbling reduction.
    Greatest reduction with occlusion of RUL. Two valves deployed. Plan: Continue chest tube to water seal trial.
    """

    seed = run_deterministic_extractors(note_text)
    seed.setdefault("pleural_procedures", {})["chest_tube"] = {"performed": True, "action": "Insertion"}
    record = RegistryRecord(**seed)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31647" in codes
    assert "32551" not in codes


def test_ultra_short_pal_valve_localization_note_derives_31647_and_suppresses_31634() -> None:
    note_text = """
    Plan first: keep chest tube, daily CXR, assess for removal once leak resolved.
    41-year-old male with PAL after pneumothorax. Bronchoscopy under moderate sedation.
    Balloon occlusion localized leak to LUL; 2 valves deployed; bubbling decreased significantly.
    No bleeding. EBL minimal.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.procedures_performed is not None
    assert record.procedures_performed.blvr is not None
    assert record.procedures_performed.blvr.performed is True
    assert record.procedures_performed.blvr.procedure_type == "Valve placement"
    assert record.procedures_performed.blvr.target_lobe == "LUL"
    assert record.procedures_performed.blvr.number_of_valves == 2

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31647" in codes
    assert "31634" not in codes


def test_us_guided_transthoracic_core_biopsy_header_variant_extracts_samples_and_code() -> None:
    note_text = """
    PRE/POST DX: Pleural-based nodule (R91.1)
    PROCEDURE: US-guided transthoracic biopsy (core)
    ANESTHESIA: Local only
    DETAIL:
    Ultrasound identified superficial lesion along left lateral chest wall.
    Three cores obtained. No immediate pneumothorax.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.pleural_procedures is not None
    assert record.pleural_procedures.pleural_biopsy is not None
    biopsy = record.pleural_procedures.pleural_biopsy
    assert biopsy.performed is True
    assert biopsy.guidance == "Ultrasound"
    assert biopsy.side == "Left"
    assert biopsy.number_of_samples == 3

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32408" in codes


def test_header_only_optional_bal_is_cleared_in_foreign_body_note() -> None:
    note_text = """
    BRONCHOSCOPY - FOREIGN BODY REMOVAL
    Procedure(s):
    * Flexible bronchoscopy
    * Foreign body retrieval
    * BAL (optional)
    Findings:
    Metallic fragment visualized in RLL basal segment.
    Retrieval basket used. Fragment captured and removed en bloc.
    Specimens: Foreign body only.
    Complications: none
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)
    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record

    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.bal is not None
    assert updated.procedures_performed.bal.performed is False

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31624" not in codes
    assert "31635" in codes


def test_cryospray_note_derives_cryotherapy_code() -> None:
    note_text = """
    Cryospray airway ablation note: 52-year-old female with recurrent airway papillomatosis.
    Flexible bronchoscopy with cryospray applied to supraglottic/tracheal lesions.
    Lesions treated in short bursts; airway patent at end.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    assert record.procedures_performed is not None
    assert record.procedures_performed.cryotherapy is not None
    assert record.procedures_performed.cryotherapy.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31641" in codes


def test_thermoplasty_lingula_is_not_double_billed_as_multilobar() -> None:
    note_text = """
    BRONCHIAL THERMOPLASTY - SESSION 3 (LUL)
    TAB:
    Lobe Activations
    LUL 38
    Lingula 12
    Flexible bronchoscopy performed. Thermoplasty catheter used to deliver activations as above.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31660" in codes
    assert "31661" not in codes


def test_masked_fungal_material_debulking_is_preserved_and_low_grade_bleeding_cleared() -> None:
    note_text = """
    PROCEDURE:
    * Bronchoscopy with debulking and removal of obstructing material
    * BAL
    DETAIL:
    60-year-old female with obstructing lesion in RUL bronchus. Bronchoscopy revealed necrotic/fungal-appearing material partially occluding segmental airway.
    Material removed with forceps and suction; BAL performed. Minimal mucosal bleeding controlled. Airway patent at conclusion.
    Specimens: endobronchial debris + BAL to micro/path.
    EBL minimal; complications none.
    """

    seed = run_deterministic_extractors(mask_offset_preserving(note_text))
    seed["complications"] = {
        "any_complication": True,
        "complication_list": ["Bleeding - Mild"],
        "events": [{"type": "Bleeding", "notes": "Minimal mucosal bleeding controlled"}],
        "bleeding": {"occurred": True, "bleeding_grade_nashville": 1},
    }
    record = RegistryRecord(**seed)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.mechanical_debulking is not None
    assert updated.procedures_performed.mechanical_debulking.performed is True

    warnings = reconcile_complications_from_narrative(updated, note_text)
    assert not any("BLEEDING_GRADE_DERIVED" in w for w in warnings)
    assert updated.complications is not None
    assert updated.complications.bleeding is not None
    assert updated.complications.bleeding.occurred is False
    assert updated.complications.bleeding.bleeding_grade_nashville == 0

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31640" in codes
    assert "31624" in codes


def test_eus_b_passes_parser_ignores_station_number_artifact() -> None:
    note_text = (
        "EUS-B (via esophagus) staging: EUS-B performed; nodes sampled: station 7 and 4L (3 passes each). "
        "Doppler negative. No complications."
    )
    record = RegistryRecord(procedures_performed={"eus_b": {"performed": True}})

    warnings = enrich_eus_b_sampling_details(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.eus_b is not None
    assert record.procedures_performed.eus_b.passes == 3
    assert any("AUTO_EUS_B_DETAIL" in w for w in warnings)
