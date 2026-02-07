from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.processing.cao_interventions_detail import extract_cao_interventions_detail
from tests.registry._notes_path import notes_dir_from_env_or_workspace


def _notes_dir() -> Path:
    return notes_dir_from_env_or_workspace(anchor_file=__file__)


def test_note_240_regression_extracts_tracheal_pre_post_obstruction_pct() -> None:
    note_path = _notes_dir() / "note_240.txt"
    if not note_path.exists():
        pytest.skip(f"Fixture note not available: {note_path}")

    text = note_path.read_text(encoding="utf-8")
    details = extract_cao_interventions_detail(text)
    by_loc = {str(item.get("location")): item for item in details if isinstance(item, dict)}

    assert by_loc["Trachea"]["pre_obstruction_pct"] == 80
    assert by_loc["Trachea"]["post_obstruction_pct"] == 5
