from __future__ import annotations

import uuid

from app.registry.schema import RegistryRecord


def test_registry_record_retains_clinical_followup_fields() -> None:
    event_id = str(uuid.uuid4())
    payload = {
        "clinical_course": {
            "updates": [
                {
                    "relative_day_offset": 7,
                    "update_type": "clinical_update",
                    "hospital_admission": True,
                    "icu_admission": None,
                    "deceased": None,
                    "disease_status": "Stable",
                    "source_event_id": event_id,
                    "summary_text": "Follow-up visit.",
                }
            ],
            "current_state": {
                "relative_day_offset": 7,
                "hospital_admission": True,
                "icu_admission": None,
                "deceased": None,
                "disease_status": "Stable",
                "source_event_id": event_id,
                "summary_text": "Follow-up visit.",
            },
        }
    }

    record = RegistryRecord(**payload)
    dumped = record.model_dump(exclude_none=True, mode="json")
    clinical = dumped.get("clinical_course") or {}
    assert isinstance(clinical, dict)

    updates = clinical.get("updates") or []
    assert isinstance(updates, list)
    assert len(updates) == 1
    assert isinstance(updates[0], dict)
    assert updates[0].get("hospital_admission") is True
    assert updates[0].get("disease_status") == "Stable"
    assert str(updates[0].get("source_event_id")) == event_id

    current = clinical.get("current_state") or {}
    assert isinstance(current, dict)
    assert current.get("hospital_admission") is True
    assert current.get("disease_status") == "Stable"
    assert str(current.get("source_event_id")) == event_id

