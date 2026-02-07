from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.schema import RegistryRecord


def test_clinical_guardrails_sets_stent_to_assessment_only_for_inspection_language() -> None:
    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"airway_stent": {"performed": True, "action": "Placement"}}}
    )
    note_text = (
        "Initial airway inspection. Inspection shows a BMS that is patent in the RMSB with good aeration through the stent."
    )

    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.performed is True
    assert stent.action == "Assessment only"
    assert stent.airway_stent_removal is False
    assert outcome.changed is True


def test_clinical_guardrails_treats_well_positioned_known_stent_as_assessment_only() -> None:
    guardrails = ClinicalGuardrails()
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"airway_stent": {"performed": True, "action": "Placement"}}}
    )
    note_text = "The patient's known Silicone Y-stent was well positioned."

    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Assessment only"
