from __future__ import annotations

from app.registry.aggregation.clinical.patch_clinical_update import patch_clinical_update
from app.registry.aggregation.imaging.patch_imaging import patch_imaging_update


def test_imaging_followup_dedupes_by_title_key() -> None:
    registry_json: dict = {}

    extracted = {
        "imaging_snapshot": {
            "relative_day_offset": 14,
            "modality": "ct",
            "subtype": "followup",
            "response": "Stable",
            "overall_impression_text": "Stable nodule.",
            "qa_flags": [],
        },
        "targets_update": {"peripheral_targets": [], "mediastinal_targets": []},
        "qa_flags": [],
    }
    changed_1, _ = patch_imaging_update(
        registry_json,
        extracted=extracted,
        event_id="00000000-0000-0000-0000-000000000001",
        relative_day_offset=14,
        event_subtype="followup",
        event_title="Week 2 CT",
        source_modality="ct",
        manual_overrides={},
    )
    assert changed_1 is True

    extracted_again = {
        "imaging_snapshot": {
            "relative_day_offset": 14,
            "modality": "ct",
            "subtype": "followup",
            "response": "Stable",
            "overall_impression_text": "No interval change.",
            "qa_flags": [],
        },
        "targets_update": {"peripheral_targets": [], "mediastinal_targets": []},
        "qa_flags": [],
    }
    changed_2, _ = patch_imaging_update(
        registry_json,
        extracted=extracted_again,
        event_id="00000000-0000-0000-0000-000000000002",
        relative_day_offset=14,
        event_subtype="followup",
        event_title="Week 2 CT",
        source_modality="ct",
        manual_overrides={},
    )
    assert changed_2 is False

    followups = ((registry_json.get("imaging_summary") or {}).get("followups") or [])
    assert len(followups) == 1
    assert followups[0]["event_title"] == "Week 2 CT"


def test_clinical_updates_dedupe_by_title_key() -> None:
    registry_json: dict = {}

    extracted = {
        "clinical_update": {
            "relative_day_offset": 10,
            "update_type": "clinical_update",
            "summary_text": "Symptoms stable.",
            "qa_flags": [],
        },
        "qa_flags": [],
    }

    changed_1, _ = patch_clinical_update(
        registry_json,
        extracted=extracted,
        event_title="Clinic Follow-up",
        manual_overrides={},
    )
    assert changed_1 is True

    extracted_again = {
        "clinical_update": {
            "relative_day_offset": 10,
            "update_type": "clinical_update",
            "summary_text": "No change in symptoms.",
            "qa_flags": [],
        },
        "qa_flags": [],
    }
    changed_2, _ = patch_clinical_update(
        registry_json,
        extracted=extracted_again,
        event_title="Clinic Follow-up",
        manual_overrides={},
    )
    assert changed_2 is False

    updates = ((registry_json.get("clinical_course") or {}).get("updates") or [])
    assert len(updates) == 1
    assert updates[0]["event_title"] == "Clinic Follow-up"
