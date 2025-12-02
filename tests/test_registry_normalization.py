"""Tests for registry payload normalization."""

from __future__ import annotations

import pytest

from modules.api.normalization import (
    ASSISTANT_ROLE_MAP,
    PROBE_POSITION_MAP,
    normalize_registry_payload,
)


class TestStripUnitSuffix:
    """Test unit suffix stripping functionality."""

    def test_strip_mm_suffix(self) -> None:
        payload = {
            "equipment": {
                "bronchoscope_outer_diameter_mm": "12 mm",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["equipment"]["bronchoscope_outer_diameter_mm"] == 12.0

    def test_strip_mm_suffix_no_space(self) -> None:
        payload = {
            "equipment": {
                "bronchoscope_outer_diameter_mm": "6.2mm",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["equipment"]["bronchoscope_outer_diameter_mm"] == 6.2

    def test_strip_mm_suffix_uppercase(self) -> None:
        payload = {
            "equipment": {
                "bronchoscope_outer_diameter_mm": "5.5 MM",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["equipment"]["bronchoscope_outer_diameter_mm"] == 5.5

    def test_numeric_value_unchanged(self) -> None:
        payload = {
            "equipment": {
                "bronchoscope_outer_diameter_mm": 12.0,
            }
        }
        result = normalize_registry_payload(payload)
        assert result["equipment"]["bronchoscope_outer_diameter_mm"] == 12.0

    def test_none_value_unchanged(self) -> None:
        payload = {
            "equipment": {
                "bronchoscope_outer_diameter_mm": None,
            }
        }
        result = normalize_registry_payload(payload)
        assert result["equipment"]["bronchoscope_outer_diameter_mm"] is None


class TestAssistantRoleNormalization:
    """Test assistant role normalization."""

    def test_fellow_to_resident(self) -> None:
        payload = {
            "providers": {
                "assistant_role": "fellow",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["providers"]["assistant_role"] == "Resident"

    def test_pulm_fellow_to_resident(self) -> None:
        payload = {
            "providers": {
                "assistant_role": "pulm fellow",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["providers"]["assistant_role"] == "Resident"

    def test_pulmonary_fellow_to_resident(self) -> None:
        payload = {
            "providers": {
                "assistant_role": "Pulmonary Fellow",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["providers"]["assistant_role"] == "Resident"

    def test_rn_case_insensitive(self) -> None:
        payload = {
            "providers": {
                "assistant_role": "RN",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["providers"]["assistant_role"] == "RN"

    def test_nurse_to_rn(self) -> None:
        payload = {
            "providers": {
                "assistant_role": "nurse",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["providers"]["assistant_role"] == "RN"

    def test_unknown_role_preserved(self) -> None:
        payload = {
            "providers": {
                "assistant_role": "Unknown Role",
            }
        }
        result = normalize_registry_payload(payload)
        # Unknown roles are preserved as-is (may fail validation, which is intended)
        assert result["providers"]["assistant_role"] == "Unknown Role"

    def test_none_role_unchanged(self) -> None:
        payload = {
            "providers": {
                "assistant_role": None,
            }
        }
        result = normalize_registry_payload(payload)
        assert result["providers"]["assistant_role"] is None


class TestProbePositionNormalization:
    """Test radial EBUS probe position normalization."""

    def test_aerated_lung_to_not_visualized(self) -> None:
        payload = {
            "procedures_performed": {
                "radial_ebus": {
                    "probe_position": "Aerated lung on radial EBUS",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["radial_ebus"]["probe_position"] == "Not visualized"

    def test_concentric_preserved(self) -> None:
        payload = {
            "procedures_performed": {
                "radial_ebus": {
                    "probe_position": "Concentric",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["radial_ebus"]["probe_position"] == "Concentric"

    def test_eccentric_case_insensitive(self) -> None:
        payload = {
            "procedures_performed": {
                "radial_ebus": {
                    "probe_position": "ECCENTRIC",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["radial_ebus"]["probe_position"] == "Eccentric"

    def test_adjacent_normalized(self) -> None:
        payload = {
            "procedures_performed": {
                "radial_ebus": {
                    "probe_position": "adjacent",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["radial_ebus"]["probe_position"] == "Adjacent"


class TestDemographicsNormalization:
    """Test patient demographics normalization."""

    def test_height_cm_normalization(self) -> None:
        payload = {
            "patient_demographics": {
                "height_cm": "175 cm",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["patient_demographics"]["height_cm"] == 175.0

    def test_weight_kg_normalization(self) -> None:
        payload = {
            "patient_demographics": {
                "weight_kg": "80 kg",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["patient_demographics"]["weight_kg"] == 80.0


class TestClinicalContextNormalization:
    """Test clinical context normalization."""

    def test_lesion_size_mm_normalization(self) -> None:
        payload = {
            "clinical_context": {
                "lesion_size_mm": "25 mm",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["clinical_context"]["lesion_size_mm"] == 25.0

    def test_lesion_size_cm_to_mm_conversion(self) -> None:
        payload = {
            "clinical_context": {
                "lesion_size_mm": "2.5 cm",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["clinical_context"]["lesion_size_mm"] == 25.0


class TestPleuralNormalization:
    """Test pleural procedure normalization."""

    def test_volume_removed_ml_normalization(self) -> None:
        payload = {
            "pleural_procedures": {
                "thoracentesis": {
                    "volume_removed_ml": "1500 mL",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["pleural_procedures"]["thoracentesis"]["volume_removed_ml"] == 1500.0

    def test_volume_removed_cc_normalization(self) -> None:
        payload = {
            "pleural_procedures": {
                "thoracentesis": {
                    "volume_removed_ml": "800 cc",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["pleural_procedures"]["thoracentesis"]["volume_removed_ml"] == 800.0


class TestEmptyPayload:
    """Test handling of empty or minimal payloads."""

    def test_empty_payload(self) -> None:
        result = normalize_registry_payload({})
        assert result == {}

    def test_payload_without_normalization_targets(self) -> None:
        payload = {
            "patient_mrn": "12345",
            "procedure_date": "2024-01-15",
        }
        result = normalize_registry_payload(payload)
        assert result == payload


class TestRoleMappingCoverage:
    """Test that the role mapping covers common variations."""

    @pytest.mark.parametrize(
        "input_role,expected",
        [
            ("fellow", "Resident"),
            ("pulm fellow", "Resident"),
            ("ip fellow", "Resident"),
            ("pgy4", "Resident"),
            ("pgy5", "Resident"),
            ("intern", "Resident"),
            ("rn", "RN"),
            ("nurse", "RN"),
            ("rt", "RT"),
            ("respiratory therapist", "RT"),
            ("tech", "Tech"),
            ("technician", "Tech"),
            ("pa", "PA"),
            ("pa-c", "PA"),
            ("np", "NP"),
            ("aprn", "NP"),
            ("medical student", "Medical Student"),
            ("med student", "Medical Student"),
        ],
    )
    def test_role_mapping(self, input_role: str, expected: str) -> None:
        assert ASSISTANT_ROLE_MAP.get(input_role.lower()) == expected


class TestProbePositionMappingCoverage:
    """Test that the probe position mapping covers common variations."""

    @pytest.mark.parametrize(
        "input_pos,expected",
        [
            ("aerated lung on radial ebus", "Not visualized"),
            ("not visualized", "Not visualized"),
            ("no lesion seen", "Not visualized"),
            ("concentric", "Concentric"),
            ("central", "Concentric"),
            ("within lesion", "Concentric"),
            ("eccentric", "Eccentric"),
            ("off-center", "Eccentric"),
            ("adjacent", "Adjacent"),
            ("beside lesion", "Adjacent"),
        ],
    )
    def test_probe_position_mapping(self, input_pos: str, expected: str) -> None:
        assert PROBE_POSITION_MAP.get(input_pos.lower()) == expected


class TestForcepsTypeNormalization:
    """Test forceps_type normalization for transbronchial biopsy."""

    def test_needle_cryoprobe_to_cryoprobe(self) -> None:
        """Test that 'Needle, Cryoprobe' normalizes to 'Cryoprobe'."""
        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "forceps_type": "Needle, Cryoprobe",
                }
            }
        }
        result = normalize_registry_payload(payload)
        tbbx = result["procedures_performed"]["transbronchial_biopsy"]
        assert tbbx["forceps_type"] == "Cryoprobe"

    def test_standard_preserved(self) -> None:
        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "forceps_type": "Standard",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["transbronchial_biopsy"]["forceps_type"] == "Standard"

    def test_cryoprobe_preserved(self) -> None:
        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "forceps_type": "Cryoprobe",
                }
            }
        }
        result = normalize_registry_payload(payload)
        tbbx = result["procedures_performed"]["transbronchial_biopsy"]
        assert tbbx["forceps_type"] == "Cryoprobe"

    def test_forceps_to_standard(self) -> None:
        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "forceps_type": "forceps",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["transbronchial_biopsy"]["forceps_type"] == "Standard"

    def test_unknown_with_cryo_becomes_cryoprobe(self) -> None:
        """Unknown values containing 'cryo' should become Cryoprobe."""
        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "forceps_type": "some cryo thing",
                }
            }
        }
        result = normalize_registry_payload(payload)
        tbbx = result["procedures_performed"]["transbronchial_biopsy"]
        assert tbbx["forceps_type"] == "Cryoprobe"

    def test_unknown_without_cryo_becomes_standard(self) -> None:
        """Unknown values without 'cryo' should become Standard."""
        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "forceps_type": "some unknown value",
                }
            }
        }
        result = normalize_registry_payload(payload)
        assert result["procedures_performed"]["transbronchial_biopsy"]["forceps_type"] == "Standard"


class TestPathologyResultsNormalization:
    """Test pathology_results normalization."""

    def test_string_to_dict(self) -> None:
        """Test that string pathology_results is converted to proper dict."""
        payload = {
            "pathology_results": "ROSE malignant",
        }
        result = normalize_registry_payload(payload)
        assert isinstance(result["pathology_results"], dict)
        assert result["pathology_results"]["final_diagnosis"] == "ROSE malignant"
        assert result["pathology_results"]["rose_result"] == "ROSE malignant"

    def test_string_without_rose(self) -> None:
        """Test string without ROSE keyword."""
        payload = {
            "pathology_results": "Adenocarcinoma",
        }
        result = normalize_registry_payload(payload)
        assert isinstance(result["pathology_results"], dict)
        assert result["pathology_results"]["final_diagnosis"] == "Adenocarcinoma"
        assert result["pathology_results"]["rose_result"] is None

    def test_dict_unchanged(self) -> None:
        """Test that dict pathology_results is not modified."""
        payload = {
            "pathology_results": {
                "final_diagnosis": "Adenocarcinoma",
                "histology": "Non-small cell",
            }
        }
        result = normalize_registry_payload(payload)
        assert result["pathology_results"]["final_diagnosis"] == "Adenocarcinoma"
        assert result["pathology_results"]["histology"] == "Non-small cell"

    def test_none_unchanged(self) -> None:
        """Test that None pathology_results stays None."""
        payload = {
            "pathology_results": None,
        }
        result = normalize_registry_payload(payload)
        assert result["pathology_results"] is None

    def test_empty_string(self) -> None:
        """Test empty string pathology_results."""
        payload = {
            "pathology_results": "",
        }
        result = normalize_registry_payload(payload)
        assert isinstance(result["pathology_results"], dict)
        assert result["pathology_results"]["final_diagnosis"] is None
