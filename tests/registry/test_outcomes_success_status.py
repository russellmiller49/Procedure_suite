from __future__ import annotations

from modules.registry.postprocess import enrich_procedure_success_status
from modules.registry.postprocess import enrich_outcomes_complication_details
from modules.registry.schema import RegistryRecord


def test_enrich_procedure_success_status_marks_partial_success_from_suboptimal_radial_probe() -> None:
    record = RegistryRecord()
    note_text = "Although we were able to navigate directly to the lesion, the radial probe view was suboptimal.\n"

    warnings = enrich_procedure_success_status(record, note_text)
    assert any("AUTO_OUTCOMES_STATUS" in w for w in warnings)

    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Partial success"
    assert "suboptimal" in (record.outcomes.aborted_reason or "").lower()

    evidence = record.evidence
    assert evidence.get("outcomes.procedure_success_status")
    assert evidence.get("outcomes.aborted_reason")

    span = evidence["outcomes.procedure_success_status"][0]
    snippet = note_text[span.start:span.end].lower()
    assert "radial" in snippet and "suboptimal" in snippet


def test_enrich_procedure_success_status_marks_aborted_and_extracts_reason() -> None:
    record = RegistryRecord()
    note_text = "The procedure was aborted due to hypoxia and desaturation.\n"

    warnings = enrich_procedure_success_status(record, note_text)
    assert any("AUTO_OUTCOMES_STATUS" in w for w in warnings)

    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Aborted"
    assert record.outcomes.aborted_reason == "hypoxia and desaturation"
    assert record.outcomes.procedure_aborted_reason == "hypoxia and desaturation"

    evidence = record.evidence
    assert evidence.get("outcomes.procedure_success_status")
    assert evidence.get("outcomes.aborted_reason")
    assert evidence.get("outcomes.procedure_aborted_reason")


def test_enrich_procedure_success_status_marks_partial_when_failed_substep_but_completed() -> None:
    record = RegistryRecord(outcomes={"procedure_completed": True})
    note_text = (
        "Attempts to reposition the metallic stent more proximally were unsuccessful. "
        "The bronchoscope was removed and the procedure was completed."
    )

    warnings = enrich_procedure_success_status(record, note_text)
    assert any("AUTO_OUTCOMES_STATUS" in w for w in warnings)

    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Partial success"
    assert "unsuccessful" in (record.outcomes.aborted_reason or "").lower()


def test_enrich_outcomes_complication_details_captures_duration_and_intervention_with_evidence() -> None:
    record = RegistryRecord()
    note_text = (
        "Bleeding occurred and was controlled with cold saline and epinephrine.\n"
        "Bleeding total time: 5 minutes.\n"
    )

    warnings = enrich_outcomes_complication_details(record, note_text)
    assert any("AUTO_COMPLICATION_DETAILS" in w for w in warnings)

    assert record.outcomes is not None
    assert record.outcomes.complication_intervention == "cold saline and epinephrine"
    assert record.outcomes.complication_duration == "5 minutes"

    evidence = record.evidence
    assert evidence.get("outcomes.complication_duration")
    assert evidence.get("outcomes.complication_intervention")
