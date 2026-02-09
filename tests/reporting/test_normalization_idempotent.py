from __future__ import annotations

from proc_schemas.clinical import ProcedureBundle

from app.reporting.normalization.normalize import normalize_bundle


def test_normalize_bundle_idempotent() -> None:
    bundle = ProcedureBundle.model_validate(
        {
            "patient": {},
            "encounter": {},
            "procedures": [
                {
                    "proc_type": "ebus_tbna",
                    "schema_id": "ebus_tbna_v1",
                    "proc_id": None,
                    "data": {},
                    "cpt_candidates": [],
                }
            ],
            "free_text_hint": "Operator: Jane Doe\nService Date: 2024-05-01\nReferred Physician: John Smith\n",
        }
    )

    run1 = normalize_bundle(bundle)
    run2 = normalize_bundle(run1.bundle)

    assert run1.bundle.model_dump(exclude_none=False) == run2.bundle.model_dump(exclude_none=False)
    assert run2.notes == []

    assert run1.bundle.encounter.attending == "Jane Doe"
    assert run1.bundle.encounter.date == "2024-05-01"
    assert run1.bundle.encounter.referred_physician == "John Smith"
    assert run1.bundle.procedures[0].proc_id == "ebus_tbna_1"
