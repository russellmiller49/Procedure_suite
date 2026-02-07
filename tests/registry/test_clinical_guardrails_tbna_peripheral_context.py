from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.schema import RegistryRecord


def test_tbna_conventional_without_stations_in_peripheral_context_flips_to_peripheral_tbna() -> None:
    note_text = (
        "Indication: Suspected lung malignancy\n"
        "Target: 16 mm pulmonary nodule in RUL\n"
        "Radial EBUS view: Eccentric\n"
        "Transbronchial needle aspiration performed using a 21G needle, 3 passes obtained.\n"
    )

    record = RegistryRecord(procedures_performed={"tbna_conventional": {"performed": True}})
    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.tbna_conventional is not None
    assert updated.procedures_performed.tbna_conventional.performed is False
    assert updated.procedures_performed.peripheral_tbna is not None
    assert updated.procedures_performed.peripheral_tbna.performed is True
