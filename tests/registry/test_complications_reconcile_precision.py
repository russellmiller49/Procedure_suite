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


def test_prophylactic_cold_saline_language_does_not_create_bleeding_complication() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "Transbronchial cryobiopsy was performed in the RLL.\n"
        "Cold saline was available to control any distal bleeding should bleeding occur.\n"
        "No active bleeding was seen at the end of the procedure.\n"
        "COMPLICATIONS: None.\n"
        "EBL: 5 mL.\n"
    )

    _warnings = reconcile_complications_from_narrative(record, note_text)

    if record.complications is not None:
        assert record.complications.any_complication is not True
        if record.complications.bleeding is not None:
            assert record.complications.bleeding.occurred is not True
            assert record.complications.bleeding.bleeding_grade_nashville in (None, 0)


def test_txa_hemostasis_with_no_complications_does_not_create_bleeding_event() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "Minor mucosal oozing was treated with topical TXA and epinephrine with hemostasis achieved. "
        "No active bleeding remained. Complications: none procedural."
    )

    warnings = reconcile_complications_from_narrative(record, note_text)

    assert record.complications is None or record.complications.bleeding is None
    assert any("ROUTINE_HEMOSTASIS_SUPPRESSED" in str(w) for w in warnings)


def test_narrative_promotes_airway_injury_and_dental_injury() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "During rigid intubation a full thickness posterior membrane tear was identified in the trachea. "
        "Two teeth were lost during intubation.\n"
    )

    warnings = reconcile_complications_from_narrative(record, note_text)

    assert record.complications is not None
    assert record.complications.any_complication is True
    assert "Other" in (record.complications.complication_list or [])
    assert "tear" in str(record.complications.other_complication_details or "").lower()
    event_types = {str(event.type) for event in (record.complications.events or [])}
    assert "Airway injury" in event_types
    assert "Dental injury" in event_types
    assert any("QUALITY_SIGNAL:" in str(w) for w in warnings)


def test_narrative_promotes_aspiration_arrest_death_with_rescue_interventions() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "The patient aspirated emesis during the procedure and then developed PEA arrest. "
        "A left chest tube was placed followed by a right chest tube. "
        "Despite resuscitation efforts the patient was declared dead.\n"
    )

    warnings = reconcile_complications_from_narrative(record, note_text)

    assert record.complications is not None
    complications = set(record.complications.complication_list or [])
    assert {"Aspiration", "Cardiac arrest", "Death"}.issubset(complications)
    events = list(record.complications.events or [])
    by_type = {str(event.type): event for event in events}
    assert "Aspiration" in by_type
    assert "Cardiac arrest" in by_type
    assert "Death" in by_type
    assert "Bilateral chest tubes" in (by_type["Cardiac arrest"].interventions or [])
    assert any("QUALITY_SIGNAL:" in str(w) for w in warnings)
