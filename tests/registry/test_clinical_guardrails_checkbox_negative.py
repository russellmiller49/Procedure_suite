from __future__ import annotations

from modules.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from modules.registry.schema import RegistryRecord


def test_checkbox_negative_guardrail_forces_false_for_unchecked_items() -> None:
    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "airway_dilation": {"performed": True},
            },
            "pleural_procedures": {
                "ipc": {"performed": True},
                "chest_tube": {"performed": True},
            },
            "complications": {"pneumothorax": {"occurred": True}},
        }
    )

    note_text = (
        "0- Tunneled Pleural Catheter\n"
        "[ ] Chest tube\n"
        "0- Pneumothorax\n"
        "☐ Airway dilation\n"
    )

    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert outcome.changed is True
    assert updated.pleural_procedures is not None
    assert updated.pleural_procedures.ipc is not None
    assert updated.pleural_procedures.ipc.performed is False
    assert updated.pleural_procedures.chest_tube is not None
    assert updated.pleural_procedures.chest_tube.performed is False
    assert updated.complications is not None
    assert updated.complications.pneumothorax is not None
    assert updated.complications.pneumothorax.occurred is False
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.airway_dilation is not None
    assert updated.procedures_performed.airway_dilation.performed is False
    assert any(str(w).startswith("CHECKBOX_NEGATIVE:") for w in outcome.warnings)
