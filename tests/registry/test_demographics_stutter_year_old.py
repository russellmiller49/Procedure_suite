from __future__ import annotations

from app.registry.deterministic_extractors import extract_demographics


def test_extract_demographics_parses_stuttered_year_old_gender_male() -> None:
    note_text = "INDICATION: [REDACTED] is a 66 year old-year-old male who presents with COPD."
    demo = extract_demographics(note_text)
    assert demo.get("patient_age") == 66
    assert demo.get("gender") == "Male"


def test_extract_demographics_parses_stuttered_year_old_gender_female() -> None:
    note_text = "INDICATION: [REDACTED] is a 77 year old-year-old female who presents with lung nodule."
    demo = extract_demographics(note_text)
    assert demo.get("patient_age") == 77
    assert demo.get("gender") == "Female"

