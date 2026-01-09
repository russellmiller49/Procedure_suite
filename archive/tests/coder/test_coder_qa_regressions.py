import pytest

from modules.autocode.coder import EnhancedCPTCoder


@pytest.fixture(scope="module")
def coder():
    return EnhancedCPTCoder()


def extract_codes(result):
    return {c["cpt"] for c in result.get("codes", [])}


def test_tbna_without_parenchymal_biopsy_drops_31628(coder):
    """QA rows c91e7cd6/b3772aa3: TBNA-only should not bill 31628."""
    note = (
        "EBUS-TBNA performed at station 4R with 3 passes; no forceps biopsies were done. "
        "Text mentions transbronchial lung biopsy but it was not performed."
    )
    registry = {
        "ebus_stations_sampled": ["4R"],
        "bronch_num_tbbx": None,
        "bronch_tbbx_tool": None,
        "bronch_biopsy_sites": None,
    }
    result = coder.code_procedure({"note_text": note, "registry": registry})
    codes = extract_codes(result)
    assert "31628" not in codes
    assert "31652" in codes  # EBUS TBNA captured instead


def test_navigation_aborted_drops_31627_and_radial_31654(coder):
    """QA rows c91e7cd6/e60da817: navigation/radial add-ons should not appear if navigation not performed."""
    note = (
        "Electromagnetic navigation planned but aborted due to mis-registration; "
        "radial EBUS mentioned but tool never advanced into lesion."
    )
    registry = {
        "nav_platform": "emn",
        "nav_tool_in_lesion": False,
        "nav_sampling_tools": [],
        "nav_rebus_used": False,
    }
    result = coder.code_procedure({"note_text": note, "registry": registry})
    codes = extract_codes(result)
    assert "31627" not in codes
    assert "+31627" not in codes
    assert "31654" not in codes


def test_chest_tube_code_only_when_pleural_documented(coder):
    """QA row b3772aa3: chest tube CPT should require pleural procedure in registry."""
    note = "Chest tube placed for pneumothorax after bronchoscopy; tube inserted without imaging."

    # No pleural metadata -> should drop 32556/32557
    result_none = coder.code_procedure({"note_text": note, "registry": {}})
    codes_none = extract_codes(result_none)
    assert "32556" not in codes_none
    assert "32557" not in codes_none

    # With pleural chest tube metadata -> allow 32556
    registry = {"pleural_procedure_type": "Chest Tube", "pleural_catheter_type": "pigtail"}
    result_ok = coder.code_procedure({"note_text": note, "registry": registry})
    codes_ok = extract_codes(result_ok)
    assert "32556" in codes_ok


def test_tbbx_present_allows_31628(coder):
    """Guardrail: when registry shows parenchymal biopsy, 31628 may remain."""
    note = "Transbronchial lung biopsies performed in RLL with forceps."
    registry = {"bronch_num_tbbx": 2, "bronch_tbbx_tool": "Forceps"}
    result = coder.code_procedure({"note_text": note, "registry": registry})
    codes = extract_codes(result)
    assert "31628" in codes
