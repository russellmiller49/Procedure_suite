"""Nashville grade for blockers/balloons: established bleeding vs prophylactic placement.

Preserve (grade 3): a blocker or balloon used in response to bleeding, including when the
bleeding is reported in the sentence immediately before the device sentence, and when a
prophylactically placed device is later used for established bleeding.
Suppress: a device positioned prophylactically (before sampling, "in case"/"in the event of"
bleeding), or for a non-bleeding purpose such as lung isolation for whole lung lavage, is not a
grade 3 bleeding complication. Each case pins the exact grade (None = no bleeding record).
"""

from __future__ import annotations

import pytest

from app.registry.postprocess.complications_reconcile import reconcile_complications_from_narrative
from app.registry.schema import RegistryRecord


def _nashville_grade(note_text: str) -> int | None:
    record = RegistryRecord.model_validate({})
    reconcile_complications_from_narrative(record, note_text)
    if record.complications is None or record.complications.bleeding is None:
        return None
    return record.complications.bleeding.bleeding_grade_nashville


@pytest.mark.parametrize(
    ("note_text", "expected"),
    [
        # --- preserve: device used for established bleeding -> grade 3 ---
        pytest.param(
            "There was significant bleeding from biopsy sites. "
            "An endobronchial blocker was placed to prevent blood soiling of the contralateral lung.",
            3,
            id="bleeding_then_blocker_next_sentence",
        ),
        pytest.param(
            "Brisk bleeding was encountered. The endobronchial blocker was inflated for 5 minutes with hemostasis.",
            3,
            id="brisk_bleeding_then_blocker_inflated",
        ),
        pytest.param(
            "Mild bleeding was noted after biopsy. An endobronchial blocker was placed to tamponade.",
            3,
            id="minor_bleeding_then_blocker_for_tamponade",
        ),
        pytest.param(
            "Brisk bleeding from RB6 required placement of an endobronchial blocker for tamponade.",
            3,
            id="bleeding_and_blocker_same_sentence",
        ),
        pytest.param(
            "Significant bleeding occurred after the cryobiopsy. "
            "The prophylactically placed blocker was inflated to tamponade the bleeding.",
            3,
            id="prophylactic_blocker_later_inflated_for_bleeding",
        ),
        pytest.param(
            "Despite prophylactic balloon placement, brisk bleeding required balloon tamponade for 5 minutes.",
            3,
            id="despite_prophylactic_balloon_brisk_bleeding",
        ),
        pytest.param(
            "Moderate bleeding occurred after the third cryobiopsy and was controlled with the "
            "prophylactically placed blocker.",
            3,
            id="bleeding_controlled_with_prophylactic_blocker",
        ),
        # --- suppress: prophylactic or non-bleeding device use -> not grade 3 ---
        pytest.param(
            "An endobronchial blocker was placed prophylactically before cryobiopsy to protect the "
            "contralateral lung in the event of bleeding. No significant bleeding occurred.",
            0,
            id="prophylactic_in_the_event_of_bleeding",
        ),
        pytest.param(
            "Prior to cryobiopsy, an Arndt blocker was positioned to prevent blood soiling of the "
            "contralateral lung. There was no bleeding.",
            0,
            id="prophylactic_prevent_soiling_no_bleeding",
        ),
        pytest.param(
            "A blocker was positioned in the left mainstem in case of bleeding. Cryobiopsies were obtained.",
            None,
            id="prophylactic_in_case_of_bleeding",
        ),
        pytest.param(
            "The blocker was inflated prophylactically after each cryobiopsy, with no significant bleeding.",
            0,
            id="inflated_prophylactically_no_significant_bleeding",
        ),
        pytest.param(
            "A prophylactic blocker was inflated after each biopsy; there was no bleeding.",
            0,
            id="prophylactic_blocker_each_biopsy_no_bleeding",
        ),
        pytest.param(
            "No significant bleeding. A blocker was positioned in the right mainstem prior to cryobiopsy.",
            0,
            id="no_bleeding_then_blocker_before_sampling",
        ),
        pytest.param(
            "No bleeding was observed. "
            "An endobronchial blocker was placed to isolate the left lung for whole lung lavage.",
            0,
            id="negated_bleeding_then_isolation_blocker",
        ),
        pytest.param(
            "Minimal bleeding resolved with suction. "
            "An endobronchial blocker was then placed to isolate the left lung for whole lung lavage.",
            1,
            id="minimal_resolved_bleeding_then_isolation_blocker",
        ),
    ],
)
def test_nashville_grade_for_blocker_context(note_text: str, expected: int | None) -> None:
    assert _nashville_grade(note_text) == expected
