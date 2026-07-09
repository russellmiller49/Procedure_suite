"""CHEST ULTRASOUND FINDINGS gating for pleural (fibrinolytic) reporter renders.

Suppress: ultrasound-adjacent shorthand in a fibrinolytic note (e.g. header/menu
style "US findings: Large volume" as in the reporter seed eval gold
`seed_from_text_pleural_fibrinolytic_existing_drain`) must not fabricate a
CHEST ULTRASOUND FINDINGS block when the registry does not document a chest
ultrasound exam. The ultrasound narrative sentence must be preserved.

Preserve: the block still renders when the exam is actually documented — the
registry has chest_ultrasound.performed, the note carries an explicit CHEST
ULTRASOUND FINDINGS section, or active-voice narrative documents the exam
("We performed a bedside ultrasound... Ultrasound showed ...").
"""

from copy import deepcopy

from app.reporting.engine import (
    build_procedure_bundle_from_extraction,
    compose_structured_report,
)

# Mirrors tests/fixtures/reporter_seed_eval_samples.json
# (seed_from_text_pleural_fibrinolytic_existing_drain), whose gold canonical is
# narrative-only.
_EVAL_STYLE_NOTE = (
    "Procedure codes 76604 and 32562. 64 year old female. Dx: Empyema. "
    "left hemithorax US findings: Large volume. Meds: 5 mg tPA / 5 mg DNase. Comps: None."
)

_NARRATIVE_SENTENCE = (
    "Thoracic ultrasound of the left hemithorax was documented prior to fibrinolytic instillation."
)


def _fibrinolytic_extraction(note_text: str = _EVAL_STYLE_NOTE) -> dict:
    return {
        "procedures_performed": {"chest_ultrasound": None},
        "pleural_procedures": {
            "fibrinolytic_therapy": {
                "performed": True,
                "agents": ["tPA", "DNase"],
                "number_of_doses": 2,
            },
            "chest_tube": None,
        },
        "source_text": note_text,
    }


def _render(extraction: dict) -> str:
    note_text = str(extraction.get("source_text") or "")
    bundle = build_procedure_bundle_from_extraction(extraction, source_text=note_text)
    return compose_structured_report(bundle)


def test_fibrinolytic_without_documented_ultrasound_suppresses_findings_block() -> None:
    markdown = _render(_fibrinolytic_extraction())

    assert "CHEST ULTRASOUND FINDINGS" not in markdown
    # The ultrasound narrative sentence must survive the suppression.
    assert _NARRATIVE_SENTENCE in markdown


def test_registry_documented_chest_ultrasound_preserves_findings_block() -> None:
    extraction = deepcopy(_fibrinolytic_extraction())
    extraction["procedures_performed"]["chest_ultrasound"] = {"performed": True}

    markdown = _render(extraction)

    assert "CHEST ULTRASOUND FINDINGS:" in markdown
    assert "Pleural Effusion Volume: Large volume" in markdown


def test_explicit_findings_section_in_note_preserves_findings_block() -> None:
    note_text = (
        _EVAL_STYLE_NOTE + "\n\nCHEST ULTRASOUND FINDINGS:\nHemithorax: Left\nVolume: Large\n"
    )

    markdown = _render(_fibrinolytic_extraction(note_text))

    assert "CHEST ULTRASOUND FINDINGS:" in markdown
    assert "Pleural Effusion Volume: Large volume" in markdown


def test_active_voice_ultrasound_narrative_preserves_findings_block() -> None:
    # Mirrors tests/fixtures/reporter_clinical_fidelity_cases.json
    # (case_10_subsequent_pleural_fibrinolytic): the narrative explicitly documents
    # performing the exam, so its findings block must keep rendering.
    note_text = (
        "We performed a bedside ultrasound and subsequent fibrinolytic instillation on "
        "the left. Ultrasound showed Small volume with Thick loculations. "
        "We gave dose number 6 of tPA / DNase."
    )

    markdown = _render(_fibrinolytic_extraction(note_text))

    assert "CHEST ULTRASOUND FINDINGS:" in markdown
    assert "Pleural Effusion Volume: Small volume" in markdown
    assert "Loculations: Thick Loculations" in markdown
