from __future__ import annotations

from app.registry.postprocess.complications_reconcile import reconcile_complications_from_narrative
from app.registry.schema import RegistryRecord


def test_suctioning_blood_with_no_active_bleeding_does_not_overcall_complication() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "Following completion of bronchoscopy, after suctioning blood and secretions there was no evidence of active bleeding.\n"
        "Complications: No immediate complications.\n"
    )

    _warnings = reconcile_complications_from_narrative(record, note_text)
    assert record.complications is not None
    assert record.complications.any_complication is not True
    if record.complications.bleeding is not None:
        assert record.complications.bleeding.bleeding_grade_nashville in (None, 0)
        assert record.complications.bleeding.occurred is not True
