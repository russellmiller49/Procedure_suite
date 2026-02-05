from __future__ import annotations

from pathlib import Path

import pytest

from modules.registry.processing.cao_interventions_detail import extract_cao_interventions_detail
from modules.registry.processing.disease_burden import extract_unambiguous_lesion_size_mm


def _notes_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return (
        repo_root.parent
        / "proc_suite_notes"
        / "data"
        / "granular annotations"
        / "notes_text"
    )


def test_note_164_regression_extracts_lesion_size_and_extrinsic_cao_pct() -> None:
    note_path = _notes_dir() / "note_164.txt"
    if not note_path.exists():
        pytest.skip(f"Fixture note not available: {note_path}")

    text = note_path.read_text(encoding="utf-8")

    lesion, warnings = extract_unambiguous_lesion_size_mm(text)
    assert warnings == []
    assert lesion is not None
    assert lesion.value == pytest.approx(48.0, abs=0.1)

    details = extract_cao_interventions_detail(text)
    by_loc = {str(item.get("location")): item for item in details if isinstance(item, dict)}
    assert by_loc["RMS"]["pre_obstruction_pct"] == 85
    assert by_loc["RMS"]["obstruction_type"] == "Extrinsic"

