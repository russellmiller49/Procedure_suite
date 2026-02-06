from __future__ import annotations

import json
from pathlib import Path

from scripts import bootstrap_granular_attributes as bootstrap


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_bootstrap_granular_attributes_emits_in_bounds_spans(tmp_path: Path) -> None:
    input_path = tmp_path / "notes.jsonl"
    output_path = tmp_path / "silver_attributes.jsonl"

    note_text = (
        "Existing silicone Y-stent measured 10 x 12 mm in the left mainstem. "
        "There was 90% obstruction before treatment and the airway was widely patent afterward. "
        "A 1.2 cm nodule was sampled from the right upper lobe."
    )

    _write_jsonl(
        input_path,
        [
            {
                "note_id": "note-1",
                "source": "unit-test",
                "note_text": note_text,
            }
        ],
    )

    count = bootstrap.write_bootstrap_file(input_path, output_path)
    assert count == 1

    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1

    row = rows[0]
    spans = row.get("spans")
    assert isinstance(spans, list)
    assert spans, "Expected at least one bootstrapped span"

    labels = {span["label"] for span in spans}
    assert bootstrap.LBL_STENT_TYPE in labels or bootstrap.LBL_STENT_DIM in labels
    assert bootstrap.LBL_NODULE_SIZE in labels

    for span in spans:
        start = int(span["start"])
        end = int(span["end"])
        assert 0 <= start < end <= len(note_text)
        assert span["text"] == note_text[start:end]
