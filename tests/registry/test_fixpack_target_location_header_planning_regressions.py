from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.application.registry_service import RegistryService


def _march_2026_notes_dir() -> Path:
    return Path(__file__).resolve().parents[2].parent / "proc_suite_notes" / "new_synthetic_notes_3_5_26"


def _load_march_2026_note(*, batch: str, note_name: str) -> str:
    note_path = _march_2026_notes_dir() / batch / f"{note_name}.txt"
    if not note_path.is_file():
        raise FileNotFoundError(note_path)
    return note_path.read_text(encoding="utf-8")


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    return RegistryService().extract_fields(note_text)


@pytest.mark.parametrize(
    ("batch", "note_name", "expected_fragment"),
    [
        ("batch_4", "note_011", "lll nodule"),
        ("batch_4", "note_015", "lll nodule"),
        ("batch_6", "note_005", "lll"),
    ],
)
def test_real_notes_navigation_targets_do_not_use_header_or_planning_prose(
    monkeypatch: pytest.MonkeyPatch,
    batch: str,
    note_name: str,
    expected_fragment: str,
) -> None:
    try:
        note_text = _load_march_2026_note(batch=batch, note_name=note_name)
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.granular_data is not None

    targets = record.granular_data.navigation_targets or []
    assert len(targets) == 1

    target = targets[0]
    location_text = str(target.target_location_text or "")
    lowered = location_text.lower()

    assert "year-old" not in lowered
    assert "robotic bronchoscopy performed" not in lowered
    assert "robotic bronchoscopy note" not in lowered
    assert "planning" not in lowered
    assert "preoperative ct" not in lowered
    assert "operator note" not in lowered
    assert expected_fragment in lowered
    assert target.target_lobe == "LLL"
