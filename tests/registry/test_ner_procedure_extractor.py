from __future__ import annotations

from modules.ner.inference import NEREntity, NERExtractionResult
from modules.registry.ner_mapping.procedure_extractor import ProcedureExtractor


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
