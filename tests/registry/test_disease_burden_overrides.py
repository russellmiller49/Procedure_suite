from __future__ import annotations

from modules.registry.processing.disease_burden import (
    apply_disease_burden_overrides,
    extract_unambiguous_lesion_size_mm,
    extract_unambiguous_suv_max,
)
from modules.registry.schema import RegistryRecord


def test_extract_unambiguous_lesion_size_mm_single_value() -> None:
    note = "CT shows a 2.5 cm mass in the right upper lobe."
    extracted, warnings = extract_unambiguous_lesion_size_mm(note)
    assert warnings == []
    assert extracted is not None
    assert extracted.value == 25.0
    assert "2.5 cm mass" in extracted.span.text.lower()


def test_extract_unambiguous_lesion_size_mm_ambiguous() -> None:
    note = "CT shows a 2.5 cm mass and a 12 mm nodule."
    extracted, warnings = extract_unambiguous_lesion_size_mm(note)
    assert extracted is None
    assert any("AMBIGUOUS_DISEASE_BURDEN" in w for w in warnings)


def test_extract_unambiguous_suv_max_single_value() -> None:
    note = "PET: SUV max 10.3 in the RUL lesion."
    extracted, warnings = extract_unambiguous_suv_max(note)
    assert warnings == []
    assert extracted is not None
    assert extracted.value == 10.3


def test_extract_unambiguous_suv_max_ambiguous() -> None:
    note = "PET: SUV max 5.2. Later report: SUV max 7.1."
    extracted, warnings = extract_unambiguous_suv_max(note)
    assert extracted is None
    assert any("AMBIGUOUS_DISEASE_BURDEN" in w for w in warnings)


def test_apply_disease_burden_overrides_overrides_llm_values() -> None:
    record = RegistryRecord(
        clinical_context={"lesion_size_mm": 30.0, "suv_max": 4.0},
        granular_data={
            "cao_interventions_detail": [
                {"location": "Trachea", "pre_obstruction_pct": 50, "post_obstruction_pct": 50}
            ]
        },
    )

    note = (
        "Indication: Lung mass.\n"
        "CT shows a 2.5 cm mass. PET SUV max 10.3.\n"
        "INDICATIONS: Tracheal Obstruction\n"
        "There were lesions blocking about 90% of the airway.\n"
        "At the end of the procedure the trachea was approximately 90% open.\n"
    )

    updated, warnings = apply_disease_burden_overrides(record, note_text=note)

    assert updated.clinical_context is not None
    assert updated.clinical_context.lesion_size_mm == 25.0
    assert updated.clinical_context.suv_max == 10.3

    assert updated.granular_data is not None
    cao = updated.granular_data.cao_interventions_detail
    assert cao is not None
    by_loc = {item.location: item for item in cao}
    assert by_loc["Trachea"].pre_obstruction_pct == 90
    assert by_loc["Trachea"].post_obstruction_pct == 10

    assert any("OVERRIDE_LLM_NUMERIC: clinical_context.lesion_size_mm" in w for w in warnings)
    assert any("OVERRIDE_LLM_NUMERIC: clinical_context.suv_max" in w for w in warnings)
    assert any("OVERRIDE_LLM_NUMERIC: granular_data.cao_interventions_detail[Trachea].pre_obstruction_pct" in w for w in warnings)


def test_apply_disease_burden_overrides_does_not_override_ambiguous_size() -> None:
    record = RegistryRecord(
        clinical_context={"lesion_size_mm": 30.0},
    )
    note = "CT shows a 2.5 cm mass and a 12 mm nodule."

    updated, warnings = apply_disease_burden_overrides(record, note_text=note)

    assert updated.clinical_context is not None
    assert updated.clinical_context.lesion_size_mm == 30.0
    assert any("AMBIGUOUS_DISEASE_BURDEN: lesion_size_mm" in w for w in warnings)


def test_apply_disease_burden_overrides_does_not_override_ambiguous_cao_pct() -> None:
    record = RegistryRecord(
        granular_data={"cao_interventions_detail": [{"location": "Trachea", "pre_obstruction_pct": 50}]}
    )
    note = "Trachea was about 70% obstructed. Trachea was about 80% obstructed."

    updated, warnings = apply_disease_burden_overrides(record, note_text=note)

    assert updated.granular_data is not None
    cao = updated.granular_data.cao_interventions_detail
    assert cao is not None
    by_loc = {item.location: item for item in cao}
    assert by_loc["Trachea"].pre_obstruction_pct == 50
    assert any(
        "AMBIGUOUS_DISEASE_BURDEN: granular_data.cao_interventions_detail[Trachea].pre_obstruction_pct" in w
        for w in warnings
    )
