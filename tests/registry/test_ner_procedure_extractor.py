from __future__ import annotations

from modules.ner.inference import NEREntity, NERExtractionResult
from modules.registry.ner_mapping.procedure_extractor import ProcedureExtractor


def _entity(text: str, label: str, *, start: int, end: int) -> NEREntity:
    return NEREntity(
        text=text,
        label=label,
        start_char=start,
        end_char=end,
        confidence=0.9,
    )


def _result_with_entities(text: str, entities: list[NEREntity]) -> NERExtractionResult:
    entities_by_type: dict[str, list[NEREntity]] = {}
    for entity in entities:
        entities_by_type.setdefault(entity.label, []).append(entity)
    return NERExtractionResult(
        entities=entities,
        entities_by_type=entities_by_type,
        raw_text=text,
    )


def _result_with_proc_method(text: str) -> NERExtractionResult:
    entity = NEREntity(
        text=text,
        label="PROC_METHOD",
        start_char=0,
        end_char=len(text),
        confidence=0.9,
    )
    return NERExtractionResult(
        entities=[entity],
        entities_by_type={"PROC_METHOD": [entity]},
        raw_text=text,
    )


def test_procedure_extractor_does_not_false_positive_navigation_from_ion_substring() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("Therapeutic aspiration")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("therapeutic_aspiration") is True
    assert "navigational_bronchoscopy" not in extracted.procedure_flags


def test_procedure_extractor_matches_ion_when_standalone_word() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("ION robotic bronchoscopy")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("navigational_bronchoscopy") is True


def test_procedure_extractor_does_not_false_positive_bal_from_balloon() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("Balloon dilation performed")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("airway_dilation") is True
    assert "bal" not in extracted.procedure_flags


def test_procedure_extractor_matches_monarch_navigation() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("Monarch robotic bronchoscopy")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("navigational_bronchoscopy") is True


def test_procedure_extractor_matches_tbna_conventional() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("TBNA performed for station 7")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("tbna_conventional") is True


def test_procedure_extractor_matches_brushings() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("Brushings obtained from the lesion")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("brushings") is True


def test_procedure_extractor_does_not_mark_linear_ebus_from_radial_ebus() -> None:
    extractor = ProcedureExtractor()
    result = _result_with_proc_method("Radial EBUS performed to confirm lesion location")

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("radial_ebus") is True
    assert "linear_ebus" not in extracted.procedure_flags


def test_procedure_extractor_suppresses_airway_stent_from_context_only_labels() -> None:
    extractor = ProcedureExtractor()
    text = "Known silicone stent is in good position and remains widely patent."
    dev_start = text.index("silicone")
    dev_end = dev_start + len("silicone stent")
    ctx_start = text.index("stent")
    ctx_end = text.index("widely") + len("widely patent")
    result = _result_with_entities(
        text,
        [
            _entity("silicone stent", "DEV_STENT", start=dev_start, end=dev_end),
            _entity(text[ctx_start:ctx_end], "CTX_STENT_PRESENT", start=ctx_start, end=ctx_end),
        ],
    )

    extracted = extractor.extract(result)

    assert "airway_stent" not in extracted.procedure_flags
    assert any("suppressed airway_stent" in warning.lower() for warning in extracted.warnings)


def test_procedure_extractor_suppresses_airway_stent_from_neg_stent_label() -> None:
    extractor = ProcedureExtractor()
    text = "No airway stent was placed during this bronchoscopy."
    dev_start = text.index("airway stent")
    dev_end = dev_start + len("airway stent")
    result = _result_with_entities(
        text,
        [
            _entity("airway stent", "DEV_STENT", start=dev_start, end=dev_end),
            _entity("No airway stent was placed", "NEG_STENT", start=0, end=len("No airway stent was placed")),
        ],
    )

    extracted = extractor.extract(result)

    assert "airway_stent" not in extracted.procedure_flags
    assert any("ctx_stent_present/neg_stent" in warning.lower() for warning in extracted.warnings)


def test_procedure_extractor_keeps_airway_stent_with_action_cues_even_with_context_label() -> None:
    extractor = ProcedureExtractor()
    text = "Existing stent was noted. A second Dumon stent was placed in the distal trachea."
    dev_start = text.index("Dumon stent")
    dev_end = dev_start + len("Dumon stent")
    ctx_start = text.index("Existing")
    ctx_end = text.index(".")  # first sentence only
    result = _result_with_entities(
        text,
        [
            _entity("Dumon stent", "DEV_STENT", start=dev_start, end=dev_end),
            _entity(text[ctx_start:ctx_end], "CTX_STENT_PRESENT", start=ctx_start, end=ctx_end),
        ],
    )

    extracted = extractor.extract(result)

    assert extracted.procedure_flags.get("airway_stent") is True
    assert extracted.procedure_attributes.get("airway_stent", {}).get("action") == "Placement"
    assert extracted.procedure_attributes.get("airway_stent", {}).get("airway_stent_removal") is False
