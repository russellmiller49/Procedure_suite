from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.deterministic_extractors import extract_ipc
from app.registry.schema import RegistryRecord


def test_blvr_checkbox_selection_corrects_valve_type_procedure_type_and_valve_count() -> None:
    note_text = (
        "INDICATION: COPD for bronchoscopic lung volume reduction.\n"
        "Chartis System was used to confirm no/minimal collateral ventilation\n"
        "1\u200c YES 0\u200c NO\n"
        "The following lobes were intervened:\n"
        "0\u200c Left Upper\n"
        "1\u200c Left Lower\n"
        "0\u200c Right Upper\n"
        "0\u200c Right Middle\n"
        "0\u200c Right Lower\n"
        "The following valve were used:\n"
        "1\u200c Spiration (Olympus)\n"
        "0\u200c Zephyr (Pulmonx)\n"
        "Valve sizes used and corresponding segments below:\n"
        "Airway\tValve\n"
        "LLL anterior subsegment\tOlympus Spiration size 5\n"
        "LLL posterior subsegement\tOlympus Spiration size 7\n"
        "LLL lateral subsegment\tOlympus Spiration size 7\n"
        "LLL medial/accessory subsegment\tOlympus Spiration size 7\n"
        "LLL superior subsegment\tOlympus Spiration size 9 placed initially then removed.\n"
        "Olympus Spiration size 7 placed\n"
        "IMPRESSION: Endobronchial valves were placed without immediate complication.\n"
    )

    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {
                    "performed": True,
                    "procedure_type": "Valve assessment",
                    "valve_type": "Zephyr (Pulmonx)",
                    "number_of_valves": 3,
                }
            }
        }
    )

    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    blvr = updated.procedures_performed.blvr
    assert blvr is not None
    assert blvr.performed is True
    assert blvr.procedure_type == "Valve placement"
    assert blvr.valve_type == "Spiration (Olympus)"
    assert blvr.target_lobe == "LLL"
    assert blvr.number_of_valves == 5
    assert blvr.collateral_ventilation_assessment == "Chartis negative"

    # Removal of a placed valve should surface as foreign body removal.
    fbr = updated.procedures_performed.foreign_body_removal
    assert fbr is not None
    assert fbr.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31647" in codes
    assert "31635" in codes


def test_blvr_guardrails_do_not_promote_valve_placement_for_previously_placed_valves_in_inventory_list() -> None:
    note_text = (
        "Procedures performed:\n"
        "1. Flexible bronchoscopy with therapeutic aspiration\n"
        "2. Endobronchial glue installation\n"
        "\n"
        "Within the right upper lobe the previously placed endobronchial valves were visualized. "
        "The apical and anterior segment size 7 endobronchial valves appeared well placed. "
        "The posterior size 6 valve appeared to have migrated somewhat distally.\n"
    )

    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {
                    "performed": True,
                    "procedure_type": "Valve placement",
                    "valve_type": "Spiration (Olympus)",
                    "number_of_valves": 6,
                    "valve_sizes": ["6", "7"],
                }
            }
        }
    )

    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    blvr = updated.procedures_performed.blvr
    assert blvr is not None

    assert blvr.procedure_type == "Valve assessment"
    assert blvr.number_of_valves in (None, 0)
    assert blvr.valve_type in (None, "")

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31647" not in codes


def test_thoracoscopy_note_does_not_hallucinate_ipc_from_unchecked_checkbox() -> None:
    note_text = (
        "INDICATION: Complicated Effusion.\n"
        "PROCEDURE IN DETAIL:\n"
        "Initial thoracoscopic survey demonstrates multiple adhesions covering the pleura.\n"
        "Biopsy Taken: 0\u200c No 1\u200c Yes, number: 6\n"
        "There was extensive lysis of adhesions.\n"
        "Chest tube/s: 0\u200c 12FR 1\u200c 14Fr existing was left in place 0\u200c Tunneled Pleural Catheter\n"
    )

    # Deterministic IPC extractor should not fire when checkbox indicates 0.
    assert extract_ipc(note_text) == {}

    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {"chest_ultrasound": {"performed": True}},
            # Simulate a hallucinated IPC that must be corrected.
            "pleural_procedures": {"ipc": {"performed": True, "action": "Insertion"}},
        }
    )
    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.pleural_procedures is not None
    assert updated.pleural_procedures.ipc is not None
    assert updated.pleural_procedures.ipc.performed is False

    # Thoracoscopy should be detected and coded from the narrative and checkbox line.
    thor = updated.pleural_procedures.medical_thoracoscopy
    assert thor is not None
    assert thor.performed is True
    assert thor.biopsies_taken is True
    assert thor.adhesiolysis_performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "32609" in codes
    assert "32653" in codes
