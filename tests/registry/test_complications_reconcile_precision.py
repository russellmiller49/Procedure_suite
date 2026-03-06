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


def test_minor_trach_ooze_with_platelet_support_is_not_overcalled_as_grade4() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "Post-insertion bronchoscopy: mild ooze at entry site, controlled with direct pressure.\n"
        "Platelets: 1 unit random-donor platelets transfused intraoperatively due to Plt 89k and ooze at site.\n"
        "Complications: Minor procedural hemorrhage at trach entry site; controlled with compression. "
        "EBL: approximately 15-20 mL. No pneumothorax.\n"
    )

    _warnings = reconcile_complications_from_narrative(record, note_text)

    assert record.complications is not None
    assert record.complications.bleeding is not None
    assert record.complications.bleeding.bleeding_grade_nashville == 1
    assert "Bleeding - Severe" not in (record.complications.complication_list or [])
