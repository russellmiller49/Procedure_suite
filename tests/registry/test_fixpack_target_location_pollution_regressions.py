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


def test_real_note_003_navigation_target_ignores_planning_table_and_impression_pollution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_3", note_name="note_003")
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

    assert "preoperative ct chest" not in lowered
    assert "technically successful robotic" not in lowered
    assert "impression" not in lowered
    assert "lull 2.8 cm target" not in lowered
    assert "lul" in lowered or "left upper lobe" in lowered
    assert "apical" in lowered
    assert "posterior" in lowered
    assert target.target_lobe == "LUL"
