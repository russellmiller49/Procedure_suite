from __future__ import annotations

from app.registry.deterministic_extractors import (
    _has_populated_cryotherapy_table_row,
    _has_populated_mechanical_debulking_table_row,
    extract_cryotherapy,
    extract_mechanical_debulking,
)
from app.registry.schema.granular_logic import derive_procedures_from_granular


def test_prose_paragraph_with_double_spaces_is_not_a_cryotherapy_table_row() -> None:
    # Typographic double spaces after periods must not turn a narrative
    # paragraph into a "table row" that triggers whole-note location scanning.
    text = (
        "The left mainstem was normal.  At the takeoff of the left lower lobe there was a mass. "
        "Using the 1.9 mm cryoprobe we extracted some of the tissue after which we used forceps "
        "to slowly debulk the tumor.  The airway was then inspected."
    )
    assert _has_populated_cryotherapy_table_row(text) is False


def test_real_tab_delimited_cryotherapy_table_row_still_detected() -> None:
    line = "Cryoprobe\t1.7mm\tCryotherapy\t15 sec freeze thaw, multiple cycles\ttreated"
    assert _has_populated_cryotherapy_table_row(line) is True
    result = extract_cryotherapy("PROCEDURE IN DETAIL:\n" + line + "\n")
    assert result.get("cryotherapy", {}).get("performed") is True


def test_mechanical_debulking_table_row_requires_multicell_line() -> None:
    prose = (
        "On the right there was a small focus of tumor.  The electrocautery snare was used to "
        "remove the proximal portion of the left upper lobe tumor and forceps debulking of "
        "charred tumor was performed."
    )
    assert _has_populated_mechanical_debulking_table_row(prose) is False


def test_normal_airway_sentences_do_not_contribute_debulking_locations() -> None:
    text = (
        "DESCRIPTION OF PROCEDURE: The trachea was normal. The right sided airways were normal. "
        "The left mainstem was normal. At the takeoff of the left lower lobe there was a vascular "
        "endobronchial mass causing complete airway obstruction. The electrocautery snare was used "
        "to debulk the proximal portion of the left lower lobe tumor."
    )
    proc = extract_mechanical_debulking(text).get("mechanical_debulking") or {}
    assert proc.get("performed") is True
    location = proc.get("location") or ""
    assert "LLL" in location
    assert "Trachea" not in location
    assert "LMS" not in location


def test_scope_navigation_sentences_do_not_contribute_locations() -> None:
    text = (
        "The rigid bronchoscope was inserted and advanced to the distal trachea and attached to "
        "the jet ventilator. Tumor debulking was performed with APC and flexible forceps at the "
        "right upper lobe orifice with improvement in luminal patency."
    )
    proc = extract_mechanical_debulking(text).get("mechanical_debulking") or {}
    assert proc.get("performed") is True
    location = proc.get("location") or ""
    assert "RUL" in location
    assert "Trachea" not in location


def test_material_type_found_in_preceding_sentence() -> None:
    text = (
        "There was complete obstruction of the left lower lobe orifice secondary to adherent "
        "necrotic tissue. We then utilized flexible forceps to slowly debulk the abnormal tissue "
        "obstructing the airway."
    )
    proc = extract_mechanical_debulking(text).get("mechanical_debulking") or {}
    assert proc.get("performed") is True
    assert proc.get("material_type") == "necrotic_inflammatory"
    location = proc.get("location") or ""
    assert "Trachea" not in location


def test_granular_cao_mechanical_location_limited_to_mechanical_sites() -> None:
    granular = {
        "cao_interventions_detail": [
            {
                "location": "Trachea",
                "modalities_applied": [{"modality": "APC"}],
            },
            {
                "location": "LLL",
                "modalities_applied": [{"modality": "Mechanical debulking"}],
            },
        ]
    }
    procedures, _warnings = derive_procedures_from_granular(granular, {})
    mechanical = procedures.get("mechanical_debulking") or {}
    assert mechanical.get("performed") is True
    assert mechanical.get("location") == "LLL"
