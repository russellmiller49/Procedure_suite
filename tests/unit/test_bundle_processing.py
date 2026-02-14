from __future__ import annotations

from app.api.services.bundle_processing import (
    count_date_like_strings,
    extract_doc_t_offset_days,
    strip_system_header,
)


def test_count_date_like_strings_scans_inside_bracket_tokens() -> None:
    text = "[SYSTEM: DOC_DATE=2024-01-01]\nNo other dates."
    assert count_date_like_strings(text) == 1


def test_extract_doc_t_offset_days_prefers_system_header() -> None:
    text = "[DATE: T+99 DAYS]\n[SYSTEM: ROLE=FOLLOW_UP SEQ=1 DOC_OFFSET=T+5 DAYS]\nFollow-up note."
    assert extract_doc_t_offset_days(text) == 5


def test_strip_system_header_removes_leading_header_line() -> None:
    text = "[SYSTEM: ROLE=INDEX_PROCEDURE SEQ=1 DOC_OFFSET=T+0 DAYS]\n\nBronchoscopy performed."
    assert strip_system_header(text).startswith("Bronchoscopy performed.")
