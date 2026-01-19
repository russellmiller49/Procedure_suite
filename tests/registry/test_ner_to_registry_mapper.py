from __future__ import annotations

from modules.ner.inference import NEREntity, NERExtractionResult
from modules.registry.ner_mapping.entity_to_registry import NERToRegistryMapper


def test_mapper_uses_field_paths_for_pleural_procedures() -> None:
    entity = NEREntity(
        text="pigtail catheter",
        label="PROC_METHOD",
        start_char=0,
        end_char=15,
        confidence=0.9,
    )
    ner_result = NERExtractionResult(
        entities=[entity],
        entities_by_type={"PROC_METHOD": [entity]},
        raw_text="pigtail catheter",
    )

    result = NERToRegistryMapper().map_entities(ner_result)
    record = result.record

    assert record.pleural_procedures is not None
    assert record.pleural_procedures.chest_tube is not None
    assert record.pleural_procedures.chest_tube.performed is True


def test_mapper_uses_device_hints_for_airway_stent() -> None:
    entity = NEREntity(
        text="Dumon stent",
        label="DEV_STENT",
        start_char=0,
        end_char=10,
        confidence=0.9,
    )
    ner_result = NERExtractionResult(
        entities=[entity],
        entities_by_type={"DEV_STENT": [entity]},
        raw_text="Dumon stent",
    )

    result = NERToRegistryMapper().map_entities(ner_result)
    record = result.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.airway_stent is not None
    assert record.procedures_performed.airway_stent.performed is True

