from __future__ import annotations

from app.registry.deterministic_extractors import run_deterministic_extractors


def test_run_deterministic_extractors_populates_outcomes_follow_up_and_completion() -> None:
    note_text = (
        "DISPOSITION: Recovery area, post-procedure chest radiograph, discharge if stable.\n"
        "Follow-up: Pathology results to be reviewed in 5-7 days.\n"
        "The patient tolerated the procedure well without immediate complications.\n"
    )

    seed = run_deterministic_extractors(note_text)
    outcomes = seed.get("outcomes") or {}
    assert outcomes.get("procedure_completed") is True
    assert outcomes.get("disposition") == "Outpatient discharge"
    assert "post-procedure chest radiograph" in (outcomes.get("follow_up_plan_text") or "")
