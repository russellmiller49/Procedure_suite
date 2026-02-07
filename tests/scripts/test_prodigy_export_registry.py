import csv
import json
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_prodigy_export_registry_writes_canonical_columns(tmp_path: Path) -> None:
    from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id
    from ml.scripts import prodigy_export_registry as exporter

    input_jsonl = tmp_path / "prodigy_export.jsonl"
    _write_jsonl(
        input_jsonl,
        [
            {"text": "note a", "answer": "accept", "accept": ["bal", "ipc"], "meta": {"source_file": "src.jsonl"}},
            {"text": "note a", "answer": "accept", "accept": ["bal"], "meta": {"source_file": "src2.jsonl"}},
        ],
    )

    out_csv = tmp_path / "out.csv"
    exporter.main(
        [
            "--input-jsonl",
            str(input_jsonl),
            "--output-csv",
            str(out_csv),
            "--label-source",
            "human",
            "--label-confidence",
            "1.0",
        ]
    )

    with open(out_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Dedup by encounter_id, last write wins -> only one row for note a.
    assert len(rows) == 1
    row = rows[0]
    assert row["note_text"] == "note a"
    assert row["encounter_id"] == compute_encounter_id("note a")
    assert row["label_source"] == "human"
    assert row["label_confidence"] == "1.0"

    assert row["bal"] == "1"
    assert row["ipc"] == "0"

    # Ensure all canonical label columns exist.
    for label in REGISTRY_LABELS:
        assert label in row
