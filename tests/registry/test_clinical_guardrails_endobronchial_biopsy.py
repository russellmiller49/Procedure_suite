from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.schema import RegistryRecord


def test_clinical_guardrails_clears_endobronchial_biopsy_in_peripheral_case_with_no_lesions() -> None:
    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"endobronchial_biopsy": {"performed": True}}}
    )
    note_text = (
        "Bronchial mucosa and anatomy were normal; there are no endobronchial lesions. "
        "Navigational bronchoscopy was performed to a right lower lobe nodule. Radial probe used. "
        "Biopsies were performed with forceps."
    )

    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    ebbx = updated.procedures_performed.endobronchial_biopsy
    assert ebbx is not None
    assert ebbx.performed is False
    assert outcome.changed is True
    assert any("Endobronchial biopsy excluded" in w for w in outcome.warnings)

