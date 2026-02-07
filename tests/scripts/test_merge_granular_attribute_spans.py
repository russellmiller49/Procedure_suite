from __future__ import annotations

import json
from pathlib import Path

from ml.scripts import merge_granular_attribute_spans as merge_spans


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_merge_granular_attribute_spans_merges_by_id_then_note_id(tmp_path: Path) -> None:
    base_path = tmp_path / "base.jsonl"
    prodigy_path = tmp_path / "prodigy.jsonl"
    output_path = tmp_path / "merged.jsonl"

    text = "A Dumon stent was placed in the trachea."

    _write_jsonl(
        base_path,
        [
            {
                "id": "note-1",
                "text": text,
                "entities": [
                    {"start": 2, "end": 7, "label": "DEV_STENT", "text": "Dumon"},
                ],
            }
        ],
    )

    _write_jsonl(
        prodigy_path,
        [
            {
                "id": "task-1",
                "text": text,
                "spans": [
                    {"start": 2, "end": 7, "label": "DEV_STENT_TYPE"},
                ],
                "meta": {"note_id": "note-1"},
                "answer": "accept",
            },
            {
                "id": "task-2",
                "text": text,
                "spans": [
                    {"start": 8, "end": 13, "label": "DEV_STENT_DIM"},
                ],
                "meta": {"note_id": "note-1"},
                "answer": "accept",
            },
        ],
    )

    written = merge_spans.merge_attribute_spans(
        prodigy_input=prodigy_path,
        base_input=base_path,
        output_path=output_path,
    )
    assert written == 1

    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1

    merged = rows[0]
    assert merged["id"] == "note-1"
    assert merged["text"] == text

    labels = {entity["label"] for entity in merged.get("entities", [])}
    assert "DEV_STENT" in labels
    assert "DEV_STENT_TYPE" in labels
    assert "DEV_STENT_DIM" in labels
