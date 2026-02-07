import csv
import json
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_export_registry_file_mode_outputs_multi_hot_csv(tmp_path: Path):
    from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id
    from scripts import prodigy_export_registry as exporter

    input_jsonl = tmp_path / "prodigy_export.jsonl"
    _write_jsonl(
        input_jsonl,
        [
            {
                "text": "note a",
                "answer": "accept",
                "accept": ["bal", "ipc"],
                "meta": {"encounter_id": "E1", "source_file": "src.jsonl"},
            },
            {
                "text": "note b",
                "answer": "reject",
                "accept": ["bal"],
            },
            {
                "text": "note c",
                "answer": "accept",
                "accept": [],
            },
        ],
    )

    out_csv = tmp_path / "out.csv"
    exporter.main(
        [
            "--input-jsonl",
            str(input_jsonl),
            "--output-csv",
            str(out_csv),
        ]
    )

    with open(out_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # note b rejected; note c dropped because accept empty by default
    assert len(rows) == 1
    row = rows[0]
    assert row["note_text"] == "note a"
    assert row["encounter_id"] == compute_encounter_id("note a")
    assert row["label_source"] == "human"
    assert row["label_confidence"] == "1.0"
    assert row["bal"] == "1"
    assert row["ipc"] == "1"

    # A label not selected should be 0.
    assert row["pleural_biopsy"] == "0"

    # Now include empty accept examples as all-zero rows.
    out_csv_2 = tmp_path / "out2.csv"
    exporter.main(
        [
            "--input-jsonl",
            str(input_jsonl),
            "--output-csv",
            str(out_csv_2),
            "--include-empty-accept",
        ]
    )

    with open(out_csv_2, "r", encoding="utf-8") as f:
        rows2 = list(csv.DictReader(f))

    assert {r["note_text"] for r in rows2} == {"note a", "note c"}
    note_c = [r for r in rows2 if r["note_text"] == "note c"][0]
    assert all(note_c[label] == "0" for label in REGISTRY_LABELS)
