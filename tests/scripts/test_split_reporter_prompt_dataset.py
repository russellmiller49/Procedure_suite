from __future__ import annotations

from ml.scripts import split_reporter_prompt_dataset as mod


def _rows() -> list[dict]:
    rows: list[dict] = []
    for fam in range(12):
        note_family = f"note_{fam:03d}"
        for idx in range(2):
            rows.append(
                {
                    "id": f"{note_family}_{idx}",
                    "note_family": note_family,
                    "prompt_text": "prompt",
                    "completion_canonical": "completion",
                }
            )
    return rows


def test_split_rows_by_note_family_is_deterministic_and_leakage_free() -> None:
    rows = _rows()
    train_a, val_a, test_a, manifest_a = mod.split_rows_by_note_family(
        rows,
        seed=42,
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1,
    )
    train_b, val_b, test_b, manifest_b = mod.split_rows_by_note_family(
        rows,
        seed=42,
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1,
    )

    fam_train = {row["note_family"] for row in train_a}
    fam_val = {row["note_family"] for row in val_a}
    fam_test = {row["note_family"] for row in test_a}

    assert fam_train.isdisjoint(fam_val)
    assert fam_train.isdisjoint(fam_test)
    assert fam_val.isdisjoint(fam_test)

    assert [row["id"] for row in train_a] == [row["id"] for row in train_b]
    assert [row["id"] for row in val_a] == [row["id"] for row in val_b]
    assert [row["id"] for row in test_a] == [row["id"] for row in test_b]

    assert manifest_a["rows"]["total"] == len(rows)
    assert manifest_a["rows"]["train"] + manifest_a["rows"]["val"] + manifest_a["rows"]["test"] == len(rows)
    assert manifest_a["families"]["counts"] == manifest_b["families"]["counts"]

