from __future__ import annotations

from ml.scripts import split_reporter_gold_dataset as split_mod


def _build_rows() -> list[dict]:
    rows: list[dict] = []
    for patient_idx in range(10):
        pid = f"P{patient_idx:02d}"
        for syn_idx in range(3):
            rows.append(
                {
                    "id": f"{pid}_syn_{syn_idx + 1}",
                    "patient_base_id": pid,
                    "input_text": f"input {pid} {syn_idx}",
                    "ideal_output": f"ideal {pid} {syn_idx}",
                }
            )
    return rows


def test_split_records_by_patient_has_no_leakage_and_is_deterministic() -> None:
    rows = _build_rows()

    train_a, val_a, test_a, manifest_a = split_mod.split_records_by_patient(
        rows,
        seed=42,
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1,
    )
    train_b, val_b, test_b, manifest_b = split_mod.split_records_by_patient(
        rows,
        seed=42,
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1,
    )

    train_patients_a = {r["patient_base_id"] for r in train_a}
    val_patients_a = {r["patient_base_id"] for r in val_a}
    test_patients_a = {r["patient_base_id"] for r in test_a}

    assert train_patients_a.isdisjoint(val_patients_a)
    assert train_patients_a.isdisjoint(test_patients_a)
    assert val_patients_a.isdisjoint(test_patients_a)

    assert train_patients_a == {r["patient_base_id"] for r in train_b}
    assert val_patients_a == {r["patient_base_id"] for r in val_b}
    assert test_patients_a == {r["patient_base_id"] for r in test_b}

    assert len(train_a) + len(val_a) + len(test_a) == len(rows)
    assert manifest_a["rows"]["total"] == len(rows)
    assert manifest_a["rows"]["train"] == len(train_a)
    assert manifest_a["rows"]["val"] == len(val_a)
    assert manifest_a["rows"]["test"] == len(test_a)
    assert manifest_a["patients"]["counts"] == manifest_b["patients"]["counts"]

