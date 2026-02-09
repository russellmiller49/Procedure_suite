from __future__ import annotations

from ml.scripts import build_reporter_prompt_dataset as mod


def test_canonicalize_completion_removes_preamble_and_normalizes_date() -> None:
    raw = "\n".join(
        [
            "NOTE_ID: note_001",
            "SOURCE_FILE: note_001.txt",
            "",
            "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
            "DATE OF PROCEDURE: September 07, 2025",
            "PROCEDURE IN DETAIL",
        ]
    )
    canonical, had_preamble = mod.canonicalize_completion(raw)

    assert had_preamble is True
    assert "NOTE_ID:" not in canonical
    assert "SOURCE_FILE:" not in canonical
    assert "DATE OF PROCEDURE: [Date]" in canonical


def test_build_quality_flags_detects_expected_issues() -> None:
    text = "\n".join(
        [
            "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
            "PROCEDURE",
            "PROCEDURE IN DETAIL",
            "IMPRESSION / PLAN",
            "Contains None and placeholder [NOT_ALLOWED].",
        ]
    )

    flags = mod.build_quality_flags(text, contains_note_id_preamble=False)
    assert "CONSENT" in flags["missing_required_sections"]
    assert flags["disallowed_placeholders"] == ["NOT_ALLOWED"]
    assert flags["literal_none_present"] is True
    assert flags["contains_note_id_preamble"] is False


def test_infer_source_metadata_parses_note_family_and_split() -> None:
    family, split = mod.infer_source_metadata("note_105_valid.jsonl")
    assert family == "note_105"
    assert split == "valid"

