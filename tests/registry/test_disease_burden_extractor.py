from __future__ import annotations

from app.registry.processing.disease_burden import (
    apply_disease_burden_overrides,
    extract_unambiguous_lesion_size_mm,
    extract_unambiguous_target_lesion_axes_mm,
)
from app.registry.schema import RegistryRecord


def test_extract_target_lesion_axes_mm_parses_multi_dim_cm() -> None:
    note = "CT shows a 2.5 x 1.7 cm mass in the right upper lobe."
    axes, warnings = extract_unambiguous_target_lesion_axes_mm(note)
    assert warnings == []
    assert axes is not None
    assert axes.long_axis_mm == 25.0
    assert axes.short_axis_mm == 17.0
    assert "2.5" in axes.size_text


def test_extract_target_lesion_axes_mm_parses_multi_dim_cm_by() -> None:
    note = "CT shows a 2.5 by 1.7 cm mass in the right upper lobe."
    axes, warnings = extract_unambiguous_target_lesion_axes_mm(note)
    assert warnings == []
    assert axes is not None
    assert axes.long_axis_mm == 25.0
    assert axes.short_axis_mm == 17.0


def test_extract_lesion_size_mm_does_not_pick_single_value_when_multi_lesions_present() -> None:
    note = "CT shows a 2.5 x 1.7 cm mass and a 12 mm nodule."
    extracted, warnings = extract_unambiguous_lesion_size_mm(note)
    assert extracted is None
    assert any("AMBIGUOUS_DISEASE_BURDEN: lesion_size_mm" in w for w in warnings)


def test_apply_disease_burden_overrides_populates_axes_and_therapeutic_outcomes() -> None:
    record = RegistryRecord(
        clinical_context={"lesion_size_mm": 30.0},
        procedures_performed={"therapeutic_outcomes": {"pre_obstruction_pct": 50, "post_obstruction_pct": 50}},
        granular_data={"cao_interventions_detail": [{"location": "Trachea", "pre_obstruction_pct": 50}]},
    )

    note = (
        "CT shows a 2.5 x 1.7 cm mass. PET SUV max 10.3.\n"
        "INDICATIONS: Tracheal Obstruction\n"
        "There were lesions blocking about 90% of the airway.\n"
        "At the end of the procedure the trachea was approximately 90% open.\n"
    )

    updated, warnings = apply_disease_burden_overrides(record, note_text=note)

    assert updated.clinical_context is not None
    assert updated.clinical_context.lesion_size_mm == 25.0
    assert updated.clinical_context.target_lesion is not None
    assert updated.clinical_context.target_lesion.long_axis_mm == 25.0
    assert updated.clinical_context.target_lesion.short_axis_mm == 17.0

    assert updated.procedures_performed is not None
    assert updated.procedures_performed.therapeutic_outcomes is not None
    assert updated.procedures_performed.therapeutic_outcomes.pre_obstruction_pct == 90
    assert updated.procedures_performed.therapeutic_outcomes.post_obstruction_pct == 10

    assert any("OVERRIDE_LLM_NUMERIC: clinical_context.lesion_size_mm" in w for w in warnings)
    assert any(
        "OVERRIDE_LLM_NUMERIC: procedures_performed.therapeutic_outcomes.pre_obstruction_pct" in w for w in warnings
    )


def test_apply_disease_burden_overrides_does_not_override_therapeutic_outcomes_when_ambiguous() -> None:
    record = RegistryRecord(procedures_performed={"therapeutic_outcomes": {"pre_obstruction_pct": 50}})
    note = "Trachea was about 70% obstructed. Trachea was about 80% obstructed."

    updated, warnings = apply_disease_burden_overrides(record, note_text=note)

    assert updated.procedures_performed is not None
    assert updated.procedures_performed.therapeutic_outcomes is not None
    assert updated.procedures_performed.therapeutic_outcomes.pre_obstruction_pct == 50
    assert any(
        "AMBIGUOUS_DISEASE_BURDEN: procedures_performed.therapeutic_outcomes.pre_obstruction_pct" in w
        for w in warnings
    )


def test_apply_disease_burden_overrides_populates_target_lesion_morphology_with_evidence() -> None:
    record = RegistryRecord()
    note = (
        "INDICATION:\n"
        "Spiculated ground glass nodule in the right upper lobe.\n"
        "FINDINGS:\n"
        "A spiculated lesion is again seen.\n"
    )

    updated, _warnings = apply_disease_burden_overrides(record, note_text=note)

    assert updated.clinical_context is not None
    assert updated.clinical_context.target_lesion is not None
    assert updated.clinical_context.target_lesion.morphology == "Spiculated; Ground Glass"

    evidence = updated.evidence
    assert evidence.get("clinical_context.target_lesion.morphology")
    spans = evidence["clinical_context.target_lesion.morphology"]
    assert any("spicul" in note[span.start : span.end].lower() for span in spans)
