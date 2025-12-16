from __future__ import annotations

from modules.coder.application.candidate_expansion import expand_candidates


def test_candidate_expansion_does_not_add_negated_fiducial() -> None:
    note_text = "Fiducial marker not placed."
    codes = expand_candidates(note_text, [])
    assert "31626" not in set(codes)


def test_candidate_expansion_adds_dilation_for_mustang_balloon() -> None:
    note_text = "A 4mm x 20mm mustang balloon was used to dilate the airway."
    codes = expand_candidates(note_text, [])
    assert "31630" in set(codes)


def test_candidate_expansion_adds_therapeutic_aspiration_only() -> None:
    note_text = "Successful therapeutic aspiration was performed."
    codes = expand_candidates(note_text, [])
    assert "31645" in set(codes)
    assert "31646" not in set(codes)

