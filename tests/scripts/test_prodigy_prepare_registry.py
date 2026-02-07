import json
from pathlib import Path

import pytest


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _write_exclude_csv(path: Path, note_texts: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("note_text\n")
        for t in note_texts:
            f.write(f"{t}\n")


def test_prepare_registry_builds_tasks_and_respects_exclusions_and_manifest(tmp_path: Path, monkeypatch):
    from ml.lib.ml_coder.registry_label_schema import compute_encounter_id
    from scripts import prodigy_prepare_registry as prep

    input_path = tmp_path / "unlabeled.jsonl"
    _write_jsonl(
        input_path,
        [
            {"note_text": "note a", "note_id": "A"},
            {"text": "note b", "note_id": "B"},
            {"note": "note c", "note_id": "C"},
        ],
    )

    exclude_csv = tmp_path / "exclude.csv"
    _write_exclude_csv(exclude_csv, ["note b"])

    manifest_path = tmp_path / "manifest.json"
    out_path = tmp_path / "batch.jsonl"

    class StubPredictor:
        backend = "stub"
        thresholds = {"bal": 0.5}
        thresholds_path = None

        def predict_proba(self, note_text: str) -> dict[str, float]:
            # Pre-check BAL for note a only
            if "note a" in note_text:
                return {"bal": 0.9}
            return {"bal": 0.1}

    monkeypatch.setattr(prep, "load_predictor", lambda _model_dir: StubPredictor())

    # First run: 3 inputs, 1 excluded => 2 tasks written.
    prep.main(
        [
            "--input-file",
            str(input_path),
            "--output-file",
            str(out_path),
            "--count",
            "10",
            "--strategy",
            "random",
            "--seed",
            "123",
            "--manifest",
            str(manifest_path),
            "--exclude-csv",
            str(exclude_csv),
            "--train-csv",
            str(tmp_path / "missing_train.csv"),
            "--model-dir",
            str(tmp_path / "missing_model_dir"),
        ]
    )

    tasks = [json.loads(line) for line in out_path.read_text().splitlines() if line.strip()]
    assert len(tasks) == 2

    for task in tasks:
        assert task.get("_view_id") == "textcat"
        assert set(task["cats"].keys()) == set(prep.REGISTRY_LABELS)
        assert all(int(v) in (0, 1) for v in task["cats"].values())
        assert task.get("meta", {}).get("encounter_id") == compute_encounter_id(task["text"])

    assert {t["text"] for t in tasks} == {"note a", "note c"}
    task_by_text = {t["text"]: t for t in tasks}
    assert task_by_text["note a"]["cats"]["bal"] == 1
    assert task_by_text["note c"]["cats"]["bal"] == 0

    # Second run should produce nothing because the manifest prevents re-sampling.
    out_path_2 = tmp_path / "batch2.jsonl"
    prep.main(
        [
            "--input-file",
            str(input_path),
            "--output-file",
            str(out_path_2),
            "--count",
            "10",
            "--strategy",
            "random",
            "--seed",
            "123",
            "--manifest",
            str(manifest_path),
            "--exclude-csv",
            str(exclude_csv),
            "--train-csv",
            str(tmp_path / "missing_train.csv"),
            "--model-dir",
            str(tmp_path / "missing_model_dir"),
        ]
    )

    assert not out_path_2.exists()
    manifest = json.loads(manifest_path.read_text())
    assert len(manifest.get("seen_encounter_ids", [])) == 2
