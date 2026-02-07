from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.ner.inference import NEREntity, NERExtractionResult
from app.registry.ner_mapping.entity_to_registry import NERToRegistryMapper


def _result_for_entities(text: str, entities: list[NEREntity]) -> NERExtractionResult:
    entities_by_type: dict[str, list[NEREntity]] = {}
    for entity in entities:
        entities_by_type.setdefault(entity.label, []).append(entity)
    return NERExtractionResult(
        entities=entities,
        entities_by_type=entities_by_type,
        raw_text=text,
    )


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


def test_mapper_suppresses_context_only_stent_labels_and_avoids_31636() -> None:
    text = "Known silicone stent is in good position and remains patent."
    dev_start = text.index("silicone")
    dev_end = dev_start + len("silicone stent")
    ctx_start = text.index("stent")
    ctx_end = len(text)

    entities = [
        NEREntity(
            text="silicone stent",
            label="DEV_STENT",
            start_char=dev_start,
            end_char=dev_end,
            confidence=0.9,
        ),
        NEREntity(
            text=text[ctx_start:ctx_end],
            label="CTX_STENT_PRESENT",
            start_char=ctx_start,
            end_char=ctx_end,
            confidence=0.9,
        ),
    ]
    ner_result = _result_for_entities(text, entities)

    result = NERToRegistryMapper().map_entities(ner_result)
    record = result.record
    airway_stent = record.procedures_performed.airway_stent if record.procedures_performed else None

    assert airway_stent is None or airway_stent.performed is not True
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31636" not in codes


def test_mapper_keeps_actionable_stent_placement_and_derives_31636() -> None:
    text = "Existing stent in place. New Dumon stent was placed in the distal trachea."
    dev_start = text.index("Dumon stent")
    dev_end = dev_start + len("Dumon stent")
    ctx_end = text.index(".")

    entities = [
        NEREntity(
            text="Dumon stent",
            label="DEV_STENT",
            start_char=dev_start,
            end_char=dev_end,
            confidence=0.9,
        ),
        NEREntity(
            text=text[:ctx_end],
            label="CTX_STENT_PRESENT",
            start_char=0,
            end_char=ctx_end,
            confidence=0.9,
        ),
    ]
    ner_result = _result_for_entities(text, entities)

    result = NERToRegistryMapper().map_entities(ner_result)
    record = result.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.airway_stent is not None
    assert record.procedures_performed.airway_stent.performed is True
    assert record.procedures_performed.airway_stent.action == "Placement"

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31636" in codes
