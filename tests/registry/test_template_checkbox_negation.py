from __future__ import annotations

from modules.registry.postprocess.template_checkbox_negation import apply_template_checkbox_negation
from modules.registry.schema import RegistryRecord


def test_apply_template_checkbox_negation_forces_false_and_emits_warnings() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {"airway_dilation": {"performed": True}},
            "pleural_procedures": {"chest_tube": {"performed": True}, "ipc": {"performed": True}},
        }
    )

    note_text = (
        "0- Chest tube\n"
        "[ ] Tunneled Pleural Catheter\n"
        "☐ Airway dilation\n"
    )

    updated, warnings = apply_template_checkbox_negation(note_text, record)

    assert updated.pleural_procedures is not None
    assert updated.pleural_procedures.chest_tube is not None
    assert updated.pleural_procedures.chest_tube.performed is False
    assert updated.pleural_procedures.ipc is not None
    assert updated.pleural_procedures.ipc.performed is False
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.airway_dilation is not None
    assert updated.procedures_performed.airway_dilation.performed is False
    assert any(str(w).startswith("CHECKBOX_NEGATIVE:") for w in warnings)
