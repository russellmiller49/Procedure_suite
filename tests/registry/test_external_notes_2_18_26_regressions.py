from __future__ import annotations

from app.registry.deterministic_extractors import (
    extract_demographics,
    extract_therapeutic_aspiration,
    extract_therapeutic_injection,
)
from app.registry.postprocess import enrich_bal_from_procedure_detail
from app.registry.processing.cao_interventions_detail import extract_cao_interventions_detail
from app.registry.schema import RegistryRecord


def test_extract_demographics_does_not_anchor_to_page_number() -> None:
    note = "Patient Name: X\nAge: 70\nPage 1 of 2\nGender: Female\n"
    demo = extract_demographics(note)
    assert demo.get("patient_age") == 70
    assert demo.get("gender") == "Female"


def test_extract_demographics_parses_provation_header_table_age_gender() -> None:
    note = (
        "Procedure Date:\n"
        "SSN:\n"
        "Date of Birth:\n"
        "Age:\n"
        "Gender:\n"
        "[DATE: REDACTED] [DATE: REDACTED]\n"
        "570-74-4675\n"
        "[DATE: REDACTED]\n"
        "83\n"
        "Male\n"
    )
    demo = extract_demographics(note)
    assert demo.get("patient_age") == 83
    assert demo.get("gender") == "Male"


def test_extract_therapeutic_injection_does_not_trigger_on_bal_volume_only_sentence() -> None:
    note = "80 ml of fluid were instilled."
    assert extract_therapeutic_injection(note) == {}


def test_extract_therapeutic_aspiration_detects_clot_removal() -> None:
    note = "The stent lumen was completely obstructed by a blood clot. The clot was successfully removed."
    result = extract_therapeutic_aspiration(note)
    assert result.get("therapeutic_aspiration", {}).get("performed") is True
    assert result.get("therapeutic_aspiration", {}).get("material") == "Blood/clot"


def test_extract_therapeutic_aspiration_detects_therapeutic_suctioning() -> None:
    note = "Therapeutic suctioning was performed in the trachea. Mucus was removed from the airway."
    result = extract_therapeutic_aspiration(note)
    assert result.get("therapeutic_aspiration", {}).get("performed") is True


def test_extract_cao_interventions_detail_preserves_line_wrapped_location_context() -> None:
    note = (
        "Left Lung Abnormalities: A stent was found in the left mainstem bronchus.\n"
        "The stent lumen is completely obstructed by a blot clot and clear retained secretions.\n"
        "A nearly completely obstructing (greater than 90%\n"
        "obstructed) airway abnormality was found in the left lower lobe, due to malignant extrinsec compression.\n"
    )
    details = extract_cao_interventions_detail(note)
    by_loc = {d.get("location"): d for d in details if isinstance(d, dict)}
    assert by_loc.get("LMS", {}).get("pre_obstruction_pct") == 100
    assert by_loc.get("LLL", {}).get("pre_obstruction_pct") == 90


def test_enrich_bal_from_procedure_detail_captures_return_volume_and_cleans_location() -> None:
    note = (
        "BAL was performed in the RML medial segment (B5) of the lung and sent for cell count, bacterial culture.\n"
        "80 ml of fluid were instilled. 15 ml were returned.\n"
        "BAL was performed in the RLL lateral basal segment (B9) of the lung and sent for cell count.\n"
        "80 ml of fluid were instilled. 15 ml were returned.\n"
    )
    record = RegistryRecord.model_validate({"procedures_performed": {"bal": {"performed": True}}})
    enrich_bal_from_procedure_detail(record, note)

    assert record.procedures_performed is not None
    bal = record.procedures_performed.bal
    assert bal is not None
    assert bal.performed is True
    assert bal.volume_instilled_ml == 80
    assert bal.volume_recovered_ml == 15
    assert isinstance(bal.location, str)
    assert "rml" in bal.location.lower()
    assert "rll" in bal.location.lower()
    assert "sent for" not in bal.location.lower()


def test_airway_stent_action_type_is_kept_consistent_with_action() -> None:
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"airway_stent": {"performed": True, "action": "Assessment only", "action_type": "removal"}}}
    )
    assert record.procedures_performed is not None
    stent = record.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Assessment only"
    assert stent.action_type == "assessment_only"
