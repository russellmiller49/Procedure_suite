import json
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_export_relations_file_mode_outputs_labeled_edges(tmp_path: Path):
    from ml.scripts import prodigy_export_relations as exporter

    input_jsonl = tmp_path / "prodigy_relations_export.jsonl"
    _write_jsonl(
        input_jsonl,
        [
            {
                "answer": "accept",
                "accept": ["accept"],
                "edge": {
                    "entity_id": "spec_1",
                    "linked_to_id": "lesion_1",
                    "relation": "specimen_from_lesion",
                    "confidence": 0.9,
                    "reasoning_short": "match",
                },
                "source_entity": {"entity_id": "spec_1", "label": "Specimen 1"},
                "target_entity": {"entity_id": "lesion_1", "label": "Lesion 1"},
                "meta": {"case_id": "case_a", "edge_id": "edge_a", "edge_source": "merged"},
            },
            {
                "answer": "accept",
                "accept": ["reject"],
                "edge": {
                    "entity_id": "spec_2",
                    "linked_to_id": "lesion_2",
                    "relation": "specimen_from_lesion",
                    "confidence": 0.2,
                    "reasoning_short": "weak",
                },
                "meta": {"case_id": "case_a", "edge_id": "edge_b", "edge_source": "merged"},
            },
            # Unlabeled when accept list doesn't contain accept/reject; dropped by default.
            {
                "answer": "accept",
                "accept": [],
                "edge": {
                    "entity_id": "spec_3",
                    "linked_to_id": "lesion_3",
                    "relation": "specimen_from_lesion",
                    "confidence": 0.5,
                    "reasoning_short": "n/a",
                },
                "meta": {"case_id": "case_b", "edge_id": "edge_c"},
            },
            # Fallback: answer=reject without a selection is treated as label=0.
            {
                "answer": "reject",
                "edge": {
                    "entity_id": "spec_4",
                    "linked_to_id": "lesion_4",
                    "relation": "specimen_from_lesion",
                    "confidence": 0.5,
                    "reasoning_short": "n/a",
                },
                "meta": {"case_id": "case_b", "edge_id": "edge_d"},
            },
        ],
    )

    out_jsonl = tmp_path / "labeled_edges.jsonl"
    exporter.main(["--input-jsonl", str(input_jsonl), "--output-jsonl", str(out_jsonl)])

    rows = [json.loads(line) for line in out_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert {r["edge_id"] for r in rows} == {"edge_a", "edge_b", "edge_d"}
    by_id = {r["edge_id"]: r for r in rows}
    assert by_id["edge_a"]["label"] == 1
    assert by_id["edge_b"]["label"] == 0
    assert by_id["edge_d"]["label"] == 0

    # Include unlabeled when requested.
    out_jsonl_2 = tmp_path / "labeled_edges_with_nulls.jsonl"
    exporter.main(
        [
            "--input-jsonl",
            str(input_jsonl),
            "--output-jsonl",
            str(out_jsonl_2),
            "--include-unlabeled",
        ]
    )
    rows2 = [json.loads(line) for line in out_jsonl_2.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert {r["edge_id"] for r in rows2} == {"edge_a", "edge_b", "edge_c", "edge_d"}
    assert {r["label"] for r in rows2 if r["edge_id"] == "edge_c"} == {None}

