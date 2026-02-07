"""Tests for registry enum normalization.

These tests verify that the normalization layer correctly transforms
variant enum values into canonical forms expected by Pydantic models.
"""

import pytest

from app.registry.normalization import (
    normalize_gender,
    normalize_bronchus_sign,
    normalize_nav_imaging_verification,
    normalize_pleurodesis_agent,
    normalize_ipc_action,
    normalize_forceps_type,
    normalize_sedation_type,
    normalize_airway_type,
    normalize_asa_class,
    normalize_cao_etiology,
    normalize_pleural_biopsy_location,
    normalize_bleeding_severity,
    normalize_registry_enums,
)


class TestNormalizeGender:
    """Tests for gender normalization."""

    def test_male_variations(self):
        """Various male representations should normalize to 'Male'."""
        assert normalize_gender("M") == "Male"
        assert normalize_gender("m") == "Male"
        assert normalize_gender("male") == "Male"
        assert normalize_gender("Male") == "Male"
        assert normalize_gender("MALE") == "Male"
        assert normalize_gender("Male ") == "Male"
        assert normalize_gender(" M ") == "Male"

    def test_female_variations(self):
        """Various female representations should normalize to 'Female'."""
        assert normalize_gender("F") == "Female"
        assert normalize_gender("f") == "Female"
        assert normalize_gender("female") == "Female"
        assert normalize_gender("Female") == "Female"
        assert normalize_gender("FEMALE") == "Female"

    def test_unknown_values(self):
        """Unknown values should return 'Unknown'."""
        assert normalize_gender("X") == "Unknown"
        assert normalize_gender("Other") == "Unknown"
        assert normalize_gender("Non-binary") == "Unknown"

    def test_none_and_empty(self):
        """None and empty strings should return None."""
        assert normalize_gender(None) is None
        assert normalize_gender("") is None
        assert normalize_gender("   ") is None


class TestNormalizeBronchuSign:
    """Tests for bronchus sign normalization."""

    def test_boolean_true(self):
        """Boolean True should normalize to 'Positive'."""
        assert normalize_bronchus_sign(True) == "Positive"

    def test_boolean_false(self):
        """Boolean False should normalize to 'Negative'."""
        assert normalize_bronchus_sign(False) == "Negative"

    def test_string_true_variations(self):
        """String true variations should normalize to 'Positive'."""
        assert normalize_bronchus_sign("true") == "Positive"
        assert normalize_bronchus_sign("True") == "Positive"
        assert normalize_bronchus_sign("TRUE") == "Positive"
        assert normalize_bronchus_sign("yes") == "Positive"
        assert normalize_bronchus_sign("positive") == "Positive"
        assert normalize_bronchus_sign("present") == "Positive"

    def test_string_false_variations(self):
        """String false variations should normalize to 'Negative'."""
        assert normalize_bronchus_sign("false") == "Negative"
        assert normalize_bronchus_sign("False") == "Negative"
        assert normalize_bronchus_sign("no") == "Negative"
        assert normalize_bronchus_sign("negative") == "Negative"
        assert normalize_bronchus_sign("absent") == "Negative"

    def test_none_and_empty(self):
        """None and empty strings should return None."""
        assert normalize_bronchus_sign(None) is None
        assert normalize_bronchus_sign("") is None


class TestNormalizeNavImagingVerification:
    """Tests for navigation imaging verification normalization."""

    def test_cbct_variations(self):
        """CBCT variations should normalize to 'CBCT'."""
        assert normalize_nav_imaging_verification("Cone Beam CT") == "CBCT"
        assert normalize_nav_imaging_verification("Cone-beam CT") == "CBCT"
        assert normalize_nav_imaging_verification("CBCT") == "CBCT"
        assert normalize_nav_imaging_verification("cone beam") == "CBCT"

    def test_fluoro_variations(self):
        """Fluoroscopy variations should normalize to 'Fluoroscopy'."""
        assert normalize_nav_imaging_verification("fluoro") == "Fluoroscopy"
        assert normalize_nav_imaging_verification("Fluoro") == "Fluoroscopy"
        assert normalize_nav_imaging_verification("Fluoroscopy") == "Fluoroscopy"
        assert normalize_nav_imaging_verification("fluoroscopic") == "Fluoroscopy"

    def test_none_value(self):
        """'none' should normalize to 'None'."""
        assert normalize_nav_imaging_verification("none") == "None"

    def test_unknown_preserved(self):
        """Unknown values should be preserved."""
        assert normalize_nav_imaging_verification("CT guidance") == "CT guidance"


class TestNormalizePleurodesiAgent:
    """Tests for pleurodesis agent normalization."""

    def test_talc_variations(self):
        """Talc variations should normalize to 'Talc Slurry'."""
        assert normalize_pleurodesis_agent("Talc") == "Talc Slurry"
        assert normalize_pleurodesis_agent("talc") == "Talc Slurry"
        assert normalize_pleurodesis_agent("Talc Slurry") == "Talc Slurry"
        assert normalize_pleurodesis_agent("talc slurry") == "Talc Slurry"
        assert normalize_pleurodesis_agent("Sterile talc") == "Talc Slurry"

    def test_other_agents(self):
        """Other agents should normalize correctly."""
        assert normalize_pleurodesis_agent("Doxycycline") == "Doxycycline"
        assert normalize_pleurodesis_agent("doxycycline") == "Doxycycline"
        assert normalize_pleurodesis_agent("Bleomycin") == "Bleomycin"


class TestNormalizeIPCAction:
    """Tests for IPC action normalization."""

    def test_insertion_variations(self):
        """Insertion variations should normalize to 'Insertion'."""
        assert normalize_ipc_action("insert") == "Insertion"
        assert normalize_ipc_action("Insertion") == "Insertion"
        assert normalize_ipc_action("placement") == "Insertion"
        assert normalize_ipc_action("placed") == "Insertion"
        assert normalize_ipc_action("tunneled catheter placed") == "Insertion"

    def test_removal_variations(self):
        """Removal variations should normalize to 'Removal'."""
        assert normalize_ipc_action("remove") == "Removal"
        assert normalize_ipc_action("Removal") == "Removal"
        assert normalize_ipc_action("removed") == "Removal"
        assert normalize_ipc_action("pulled") == "Removal"

    def test_fibrinolytic_variations(self):
        """Fibrinolytic variations should normalize correctly."""
        assert normalize_ipc_action("tPA") == "Fibrinolytic instillation"
        assert normalize_ipc_action("fibrinolytic") == "Fibrinolytic instillation"
        assert normalize_ipc_action("alteplase") == "Fibrinolytic instillation"


class TestNormalizeSedationType:
    """Tests for sedation type normalization."""

    def test_general_variations(self):
        """General anesthesia variations should normalize to 'General'."""
        assert normalize_sedation_type("general") == "General"
        assert normalize_sedation_type("General anesthesia") == "General"
        assert normalize_sedation_type("GA") == "General"

    def test_moderate_variations(self):
        """Moderate sedation variations should normalize to 'Moderate'."""
        assert normalize_sedation_type("moderate") == "Moderate"
        assert normalize_sedation_type("Moderate sedation") == "Moderate"
        assert normalize_sedation_type("conscious sedation") == "Moderate"

    def test_local_variations(self):
        """Local anesthesia variations should normalize to 'Local Only'."""
        assert normalize_sedation_type("local") == "Local Only"
        assert normalize_sedation_type("Local Only") == "Local Only"
        assert normalize_sedation_type("local anesthesia") == "Local Only"
        assert normalize_sedation_type("topical") == "Local Only"

    def test_mac(self):
        """MAC variations should normalize to 'MAC'."""
        assert normalize_sedation_type("MAC") == "MAC"
        assert normalize_sedation_type("monitored anesthesia care") == "MAC"


class TestNormalizeAirwayType:
    """Tests for airway type normalization."""

    def test_ett_variations(self):
        """ETT variations should normalize to 'ETT'."""
        assert normalize_airway_type("ETT") == "ETT"
        assert normalize_airway_type("ett") == "ETT"
        assert normalize_airway_type("endotracheal tube") == "ETT"
        assert normalize_airway_type("intubated") == "ETT"

    def test_lma(self):
        """LMA variations should normalize to 'LMA'."""
        assert normalize_airway_type("LMA") == "LMA"
        assert normalize_airway_type("laryngeal mask") == "LMA"

    def test_native_variations(self):
        """Native airway variations should normalize to 'Native'."""
        assert normalize_airway_type("Native") == "Native"
        assert normalize_airway_type("native") == "Native"
        assert normalize_airway_type("natural") == "Native"
        assert normalize_airway_type("none") == "Native"
        assert normalize_airway_type("nasal") == "Native"

    def test_tracheostomy(self):
        """Tracheostomy variations should normalize to 'Tracheostomy'."""
        assert normalize_airway_type("trach") == "Tracheostomy"
        assert normalize_airway_type("Tracheostomy") == "Tracheostomy"


class TestNormalizeASAClass:
    """Tests for ASA class normalization."""

    def test_integer_values(self):
        """Integer values should be preserved if valid."""
        assert normalize_asa_class(1) == 1
        assert normalize_asa_class(3) == 3
        assert normalize_asa_class(6) == 6

    def test_invalid_integers(self):
        """Invalid integers should return None."""
        assert normalize_asa_class(0) is None
        assert normalize_asa_class(7) is None
        assert normalize_asa_class(-1) is None

    def test_roman_numerals(self):
        """Roman numerals should convert to integers."""
        assert normalize_asa_class("I") == 1
        assert normalize_asa_class("II") == 2
        assert normalize_asa_class("III") == 3
        assert normalize_asa_class("IV") == 4
        assert normalize_asa_class("V") == 5

    def test_string_numbers(self):
        """String numbers should convert to integers."""
        assert normalize_asa_class("1") == 1
        assert normalize_asa_class("3") == 3

    def test_asa_prefix(self):
        """ASA prefix should be stripped."""
        assert normalize_asa_class("ASA II") == 2
        assert normalize_asa_class("ASA 3") == 3

    def test_emergency_suffix(self):
        """Emergency suffix should be stripped."""
        assert normalize_asa_class("III-E") == 3
        assert normalize_asa_class("IV-E") == 4


class TestNormalizeCAOEtiology:
    """Tests for CAO etiology normalization."""

    def test_malignant(self):
        """Malignant variations should normalize correctly."""
        assert normalize_cao_etiology("Malignant") == "Malignant"
        assert normalize_cao_etiology("malignancy") == "Malignant"
        assert normalize_cao_etiology("cancer") == "Malignant"
        assert normalize_cao_etiology("tumor") == "Malignant"

    def test_benign(self):
        """Benign variations should normalize correctly."""
        assert normalize_cao_etiology("Benign") == "Benign"
        assert normalize_cao_etiology("benign stricture") == "Benign"

    def test_benign_other_to_other(self):
        """Benign - other should normalize to 'Other'."""
        assert normalize_cao_etiology("Benign - other") == "Other"

    def test_infectious_to_other(self):
        """Infectious should normalize to 'Other'."""
        assert normalize_cao_etiology("Infectious") == "Other"


class TestNormalizeBleedingSeverity:
    """Tests for bleeding severity normalization."""

    def test_none_variations(self):
        """No bleeding variations should normalize to 'None'."""
        assert normalize_bleeding_severity("None") == "None"
        assert normalize_bleeding_severity("none") == "None"
        assert normalize_bleeding_severity("no significant bleeding") == "None"
        assert normalize_bleeding_severity("minimal") == "None"

    def test_mild_variations(self):
        """Mild variations should normalize correctly."""
        assert normalize_bleeding_severity("Mild") == "Mild"
        assert normalize_bleeding_severity("mild") == "Mild"
        assert normalize_bleeding_severity("Mild (<50mL)") == "Mild (<50mL)"

    def test_moderate_and_severe(self):
        """Moderate and severe should normalize correctly."""
        assert normalize_bleeding_severity("Moderate") == "Moderate"
        assert normalize_bleeding_severity("Severe") == "Severe"
        assert normalize_bleeding_severity("massive") == "Severe"


class TestNormalizeRegistryEnums:
    """Tests for the main normalize_registry_enums function."""

    def test_normalizes_top_level_fields(self):
        """Should normalize top-level fields correctly."""
        raw = {
            "gender": "M",
            "bronchus_sign": True,
            "nav_imaging_verification": "Cone Beam CT",
            "pleurodesis_agent": "talc",
            "sedation_type": "general anesthesia",
            "airway_type": "ETT",
            "asa_class": "III",
            "bleeding_severity": "no significant bleeding",
        }

        result = normalize_registry_enums(raw)

        assert result["gender"] == "Male"
        assert result["bronchus_sign"] == "Positive"
        assert result["nav_imaging_verification"] == "CBCT"
        assert result["pleurodesis_agent"] == "Talc Slurry"
        assert result["sedation_type"] == "General"
        assert result["airway_type"] == "ETT"
        assert result["asa_class"] == 3
        assert result["bleeding_severity"] == "None"

    def test_normalizes_nested_pleural_fields(self):
        """Should normalize nested pleural_procedures fields."""
        raw = {
            "pleural_procedures": {
                "ipc": {
                    "action": "placement",
                },
                "pleurodesis": {
                    "agent": "Talc",
                },
            }
        }

        result = normalize_registry_enums(raw)

        assert result["pleural_procedures"]["ipc"]["action"] == "Insertion"
        assert result["pleural_procedures"]["pleurodesis"]["agent"] == "Talc Slurry"

    def test_normalizes_cao_etiology(self):
        """Should normalize CAO etiology."""
        raw = {
            "cao_interventions_detail": {
                "etiology": "Benign - other",
            }
        }

        result = normalize_registry_enums(raw)

        assert result["cao_interventions_detail"]["etiology"] == "Other"

    def test_preserves_unknown_fields(self):
        """Should preserve fields that aren't normalized."""
        raw = {
            "gender": "M",
            "custom_field": "some value",
            "another_field": 123,
        }

        result = normalize_registry_enums(raw)

        assert result["gender"] == "Male"
        assert result["custom_field"] == "some value"
        assert result["another_field"] == 123

    def test_handles_none_values(self):
        """Should handle None values gracefully."""
        raw = {
            "gender": None,
            "sedation_type": None,
            "asa_class": None,
        }

        result = normalize_registry_enums(raw)

        assert result["gender"] is None
        assert result["sedation_type"] is None
        assert result["asa_class"] is None

    def test_does_not_modify_original(self):
        """Should not modify the original dict."""
        raw = {"gender": "M"}
        result = normalize_registry_enums(raw)

        assert raw["gender"] == "M"
        assert result["gender"] == "Male"
