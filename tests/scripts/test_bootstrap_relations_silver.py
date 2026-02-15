import json
from pathlib import Path


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_bootstrap_relations_silver_edge_sources_and_edge_ids(tmp_path: Path) -> None:
    from ml.scripts import bootstrap_relations_silver as bootstrapper

    input_dir = tmp_path / "inputs"
    input_dir.mkdir(parents=True, exist_ok=True)

    bundle = {
        "zk_patient_id": "zk_1",
        "episode_id": "ep_1",
        "entity_ledger": {
            "entities": [
                {"entity_id": "lesion_1", "kind": "canonical_lesion", "label": "Lesion 1"},
                {"entity_id": "lesion_2", "kind": "canonical_lesion", "label": "Lesion 2"},
                {"entity_id": "spec_1", "kind": "specimen", "label": "Specimen 1"},
            ],
            "link_proposals": [],
        },
        "relations_heuristic": [
            {
                "entity_id": "spec_1",
                "linked_to_id": "lesion_1",
                "relation": "specimen_from_lesion",
                "confidence": 0.7,
                "reasoning_short": "heuristic",
            }
        ],
        "relations_ml": [
            {
                "entity_id": "spec_1",
                "linked_to_id": "lesion_2",
                "relation": "specimen_from_lesion",
                "confidence": 0.95,
                "reasoning_short": "ml",
            }
        ],
    }
    _write_json(input_dir / "case.json", bundle)

    out_merged = tmp_path / "merged.jsonl"
    bootstrapper.main(
        [
            "--input",
            str(input_dir),
            "--output",
            str(out_merged),
            "--edge-sources",
            "merged",
        ]
    )
    merged_rows = _read_jsonl(out_merged)
    assert len(merged_rows) == 1
    assert merged_rows[0]["meta"]["edge_source"] == "merged"
    assert merged_rows[0]["edge"]["linked_to_id"] == "lesion_2"
    assert merged_rows[0]["meta"]["edge_id"]

    out_heur = tmp_path / "heuristic.jsonl"
    bootstrapper.main(
        [
            "--input",
            str(input_dir),
            "--output",
            str(out_heur),
            "--edge-sources",
            "heuristic",
        ]
    )
    heur_rows = _read_jsonl(out_heur)
    assert len(heur_rows) == 1
    assert heur_rows[0]["meta"]["edge_source"] == "heuristic"
    assert heur_rows[0]["edge"]["linked_to_id"] == "lesion_1"
    assert heur_rows[0]["meta"]["edge_id"]

    out_all = tmp_path / "all.jsonl"
    bootstrapper.main(
        [
            "--input",
            str(input_dir),
            "--output",
            str(out_all),
            "--edge-sources",
            "all",
        ]
    )
    all_rows = _read_jsonl(out_all)
    # merged and heuristic are distinct edges; ml is deduped against merged.
    assert len(all_rows) == 2
    assert {r["edge"]["linked_to_id"] for r in all_rows} == {"lesion_1", "lesion_2"}

