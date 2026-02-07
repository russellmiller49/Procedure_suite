from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.processing.cao_interventions_detail import extract_cao_interventions_detail


def _notes_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return (
        repo_root.parent
        / "proc_suite_notes"
        / "data"
        / "granular annotations"
        / "notes_text"
    )


def test_note_240_regression_extracts_tracheal_pre_post_obstruction_pct() -> None:
    note_path = _notes_dir() / "note_240.txt"
    if not note_path.exists():
        pytest.skip(f"Fixture note not available: {note_path}")

    text = note_path.read_text(encoding="utf-8")
    details = extract_cao_interventions_detail(text)
    by_loc = {str(item.get("location")): item for item in details if isinstance(item, dict)}

    assert by_loc["Trachea"]["pre_obstruction_pct"] == 80
    assert by_loc["Trachea"]["post_obstruction_pct"] == 5

