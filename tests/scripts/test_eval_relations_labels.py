import json
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_eval_relations_labels_counts_disagreements(tmp_path: Path) -> None:
    from ml.scripts import eval_relations_labels as evaluator

    labeled = tmp_path / "labeled.jsonl"
    _write_jsonl(
        labeled,
        [
            {
                "edge_source": "merged",
                "case_id": "c1",
                "relation": "specimen_from_lesion",
                "label": 1,
                "edge": {
                    "entity_id": "spec_1",
                    "linked_to_id": "lesion_2",
                    "relation": "specimen_from_lesion",
                },
            },
            {
                "edge_source": "heuristic",
                "case_id": "c1",
                "relation": "specimen_from_lesion",
                "label": 0,
                "edge": {
                    "entity_id": "spec_1",
                    "linked_to_id": "lesion_1",
                    "relation": "specimen_from_lesion",
                },
            },
            {
                "edge_source": "heuristic",
                "case_id": "c2",
                "relation": "linked_to_lesion",
                "label": 1,
                "edge": {
                    "entity_id": "nav_1",
                    "linked_to_id": "lesion_9",
                    "relation": "linked_to_lesion",
                },
            },
        ],
    )

    report = evaluator.evaluate(list(evaluator.iter_jsonl(labeled)))
    assert report["edges_total"] == 3
    assert report["edges_labeled"] == 3
    assert report["by_source"]["merged"]["accepted"] == 1
    assert report["by_source"]["heuristic"]["accepted"] == 1
    assert report["by_source"]["heuristic"]["rejected"] == 1
    assert report["disagreements"]["keys_total"] == 1
    assert report["disagreements"]["merged_wins"] == 1
    assert report["disagreements"]["heuristic_wins"] == 0

