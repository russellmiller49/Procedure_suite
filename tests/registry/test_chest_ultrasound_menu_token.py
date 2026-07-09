from __future__ import annotations

from app.registry.deterministic_extractors import extract_chest_ultrasound


def test_bare_76604_token_does_not_set_chest_ultrasound_performed() -> None:
    # Header/menu content: CPT tokens alone are not procedure evidence.
    text = "Procedure codes 76604 and 32562. A fibrinolytic was instilled via the existing drain."
    assert extract_chest_ultrasound(text) == {}


def test_cpt_definition_line_with_ultrasound_wording_still_detected() -> None:
    text = (
        "PROCEDURE:\n"
        "76604 Ultrasound, chest (includes mediastinum), real time with image documentation\n"
        "Thoracentesis was performed.\n"
    )
    proc = extract_chest_ultrasound(text).get("chest_ultrasound") or {}
    assert proc.get("performed") is True


def test_narrative_chest_ultrasound_detected() -> None:
    text = "Bedside chest ultrasound was performed to localize the effusion."
    proc = extract_chest_ultrasound(text).get("chest_ultrasound") or {}
    assert proc.get("performed") is True
