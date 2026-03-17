from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.application.registry_service import RegistryService
from tests.registry._notes_path import notes_dir_from_env_or_workspace


def _notes_dir() -> Path:
    return notes_dir_from_env_or_workspace(anchor_file=__file__)


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    return RegistryService().extract_fields(note_text)


@pytest.mark.parametrize(
    ("note_name", "expected_start", "expected_end", "expected_minutes", "expected_codes"),
    [
        ("note_003.txt", "09:59", "10:08", 9, set()),
        ("note_010.txt", "14:50", "15:10", 20, {"99152"}),
        ("note_012.txt", "15:00", "15:50", 50, {"99152", "99153"}),
    ],
)
def test_real_notes_preserve_compact_moderate_sedation_times(
    monkeypatch: pytest.MonkeyPatch,
    note_name: str,
    expected_start: str,
    expected_end: str,
    expected_minutes: int,
    expected_codes: set[str],
) -> None:
    note_path = _notes_dir() / note_name
    if not note_path.is_file():
        pytest.skip(f"Fixture note not available: {note_path}")

    note_text = note_path.read_text(encoding="utf-8")
    result = _extract_fields_parallel_ner(monkeypatch, note_text)

    assert result.record.sedation is not None
    assert result.record.sedation.type == "Moderate"
    assert result.record.sedation.anesthesia_provider == "Proceduralist"
    assert result.record.sedation.intraservice_minutes == expected_minutes
    assert result.record.sedation.start_time == expected_start
    assert result.record.sedation.end_time == expected_end

    for code in expected_codes:
        assert code in result.cpt_codes

    unexpected_codes = {"99152", "99153"} - expected_codes
    for code in unexpected_codes:
        assert code not in result.cpt_codes
