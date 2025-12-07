"""
Tests for registry ML data preparation functions.

Verifies:
- V2 → V3 registry boolean mapping
- Rare label filtering
- Registry data prep pipeline
"""

import pytest

from modules.ml_coder.data_prep import (
    REGISTRY_TARGET_FIELDS,
    _extract_registry_booleans,
    _filter_rare_registry_labels,
)


class TestExtractRegistryBooleans:
    """Tests for _extract_registry_booleans V2 → V3 mapper."""

    def test_empty_entry_returns_all_zeros(self):
        """Empty entry should return all zeros."""
        result = _extract_registry_booleans({})

        assert set(result.keys()) == set(REGISTRY_TARGET_FIELDS)
        assert all(v == 0 for v in result.values())

    def test_thoracentesis_mapping(self):
        """V2 pleural_procedure_type 'Thoracentesis' → thoracentesis flag."""
        entry = {"pleural_procedure_type": "Thoracentesis"}
        result = _extract_registry_booleans(entry)

        assert result["thoracentesis"] == 1
        assert result["chest_tube"] == 0
        assert result["ipc"] == 0

    def test_chest_tube_mapping(self):
        """V2 pleural_procedure_type 'Chest Tube' → chest_tube flag."""
        entry = {"pleural_procedure_type": "Chest Tube"}
        result = _extract_registry_booleans(entry)

        assert result["chest_tube"] == 1
        assert result["thoracentesis"] == 0

    def test_tube_thoracostomy_maps_to_chest_tube(self):
        """V2 'Tube Thoracostomy' variant → chest_tube flag."""
        entry = {"pleural_procedure_type": "Tube Thoracostomy"}
        result = _extract_registry_booleans(entry)

        assert result["chest_tube"] == 1

    def test_tunneled_catheter_maps_to_ipc(self):
        """V2 'Tunneled Catheter' → ipc flag."""
        entry = {"pleural_procedure_type": "Tunneled Catheter"}
        result = _extract_registry_booleans(entry)

        assert result["ipc"] == 1
        assert result["chest_tube"] == 0

    def test_medical_thoracoscopy_mapping(self):
        """V2 'Medical Thoracoscopy' → medical_thoracoscopy flag."""
        entry = {"pleural_procedure_type": "Medical Thoracoscopy"}
        result = _extract_registry_booleans(entry)

        assert result["medical_thoracoscopy"] == 1
        assert result["thoracentesis"] == 0

    def test_linear_ebus_from_stations_sampled(self):
        """V2 ebus_stations_sampled non-empty → linear_ebus flag."""
        entry = {"ebus_stations_sampled": ["4R", "7", "11R"]}
        result = _extract_registry_booleans(entry)

        assert result["linear_ebus"] == 1
        assert result["diagnostic_bronchoscopy"] == 1

    def test_linear_ebus_from_linear_stations(self):
        """V2 linear_ebus_stations non-empty → linear_ebus flag."""
        entry = {"linear_ebus_stations": "4R, 7"}
        result = _extract_registry_booleans(entry)

        assert result["linear_ebus"] == 1

    def test_radial_ebus_from_nav_rebus(self):
        """V2 nav_rebus_used=True → radial_ebus flag."""
        entry = {"nav_rebus_used": True}
        result = _extract_registry_booleans(entry)

        assert result["radial_ebus"] == 1
        assert result["diagnostic_bronchoscopy"] == 1

    def test_navigational_bronchoscopy(self):
        """V2 nav_platform present → navigational_bronchoscopy flag."""
        entry = {"nav_platform": "Ion robotic bronchoscopy"}
        result = _extract_registry_booleans(entry)

        assert result["navigational_bronchoscopy"] == 1
        assert result["diagnostic_bronchoscopy"] == 1

    def test_peripheral_ablation(self):
        """V2 ablation_peripheral_performed=True → peripheral_ablation flag."""
        entry = {"ablation_peripheral_performed": True}
        result = _extract_registry_booleans(entry)

        assert result["peripheral_ablation"] == 1
        assert result["diagnostic_bronchoscopy"] == 1

    def test_blvr_from_valve_count(self):
        """V2 blvr_number_of_valves present → blvr flag."""
        entry = {"blvr_number_of_valves": 4}
        result = _extract_registry_booleans(entry)

        assert result["blvr"] == 1

    def test_blvr_from_target_lobe(self):
        """V2 blvr_target_lobe present → blvr flag."""
        entry = {"blvr_target_lobe": "LUL"}
        result = _extract_registry_booleans(entry)

        assert result["blvr"] == 1

    def test_airway_stent(self):
        """V2 stent_type present → airway_stent flag."""
        entry = {"stent_type": "Silicone"}
        result = _extract_registry_booleans(entry)

        assert result["airway_stent"] == 1

    def test_thermal_ablation_from_cao(self):
        """V2 cao_primary_modality with thermal keywords → thermal_ablation."""
        for modality in ["Electrocautery", "Argon plasma", "Laser ablation"]:
            entry = {"cao_primary_modality": modality}
            result = _extract_registry_booleans(entry)
            assert result["thermal_ablation"] == 1, f"Failed for {modality}"

    def test_cryotherapy_from_cao(self):
        """V2 cao_primary_modality with cryo → cryotherapy flag."""
        entry = {"cao_primary_modality": "Cryotherapy"}
        result = _extract_registry_booleans(entry)

        assert result["cryotherapy"] == 1

    def test_airway_dilation_from_cao(self):
        """V2 cao_primary_modality with dilation → airway_dilation flag."""
        entry = {"cao_primary_modality": "Balloon dilation"}
        result = _extract_registry_booleans(entry)

        assert result["airway_dilation"] == 1

    def test_transbronchial_cryobiopsy(self):
        """V2 nav_cryobiopsy_for_nodule=True → transbronchial_cryobiopsy."""
        entry = {"nav_cryobiopsy_for_nodule": True}
        result = _extract_registry_booleans(entry)

        assert result["transbronchial_cryobiopsy"] == 1

    def test_whole_lung_lavage(self):
        """V2 wll_volume_instilled_l present → whole_lung_lavage flag."""
        entry = {"wll_volume_instilled_l": 15.0}
        result = _extract_registry_booleans(entry)

        assert result["whole_lung_lavage"] == 1

    def test_foreign_body_removal(self):
        """V2 fb_removal_success=True → foreign_body_removal flag."""
        entry = {"fb_removal_success": True}
        result = _extract_registry_booleans(entry)

        assert result["foreign_body_removal"] == 1

    def test_bronchial_thermoplasty(self):
        """V2 bt_lobe_treated present → bronchial_thermoplasty flag."""
        entry = {"bt_lobe_treated": "RLL"}
        result = _extract_registry_booleans(entry)

        assert result["bronchial_thermoplasty"] == 1

    def test_pleurodesis(self):
        """V2 pleurodesis_performed=True → pleurodesis flag."""
        entry = {"pleurodesis_performed": True}
        result = _extract_registry_booleans(entry)

        assert result["pleurodesis"] == 1

    def test_missing_fields_default_to_zero(self):
        """Missing or null fields should not set flags."""
        entry = {
            "pleural_procedure_type": None,
            "ablation_peripheral_performed": None,
            "blvr_number_of_valves": None,
        }
        result = _extract_registry_booleans(entry)

        assert result["thoracentesis"] == 0
        assert result["peripheral_ablation"] == 0
        assert result["blvr"] == 0

    def test_nav_sampling_tools_brush(self):
        """V2 nav_sampling_tools with 'brush' → brushings flag."""
        entry = {"nav_sampling_tools": ["brush", "forceps"]}
        result = _extract_registry_booleans(entry)

        assert result["brushings"] == 1
        assert result["transbronchial_biopsy"] == 1

    def test_bronch_tbbx_tool_cryo(self):
        """V2 bronch_tbbx_tool with 'cryo' → transbronchial_cryobiopsy."""
        entry = {"bronch_tbbx_tool": "cryoprobe"}
        result = _extract_registry_booleans(entry)

        assert result["transbronchial_cryobiopsy"] == 1

    def test_transbronchial_biopsy_from_count(self):
        """V2 bronch_num_tbbx > 0 → transbronchial_biopsy flag."""
        entry = {"bronch_num_tbbx": 6}
        result = _extract_registry_booleans(entry)

        assert result["transbronchial_biopsy"] == 1

    def test_combined_procedures(self):
        """Test entry with multiple procedures."""
        entry = {
            "pleural_procedure_type": "Medical Thoracoscopy",
            "pleurodesis_performed": True,
            "linear_ebus_stations": ["7", "4R"],
        }
        result = _extract_registry_booleans(entry)

        assert result["medical_thoracoscopy"] == 1
        assert result["pleurodesis"] == 1
        assert result["linear_ebus"] == 1
        assert result["diagnostic_bronchoscopy"] == 1


class TestFilterRareRegistryLabels:
    """Tests for _filter_rare_registry_labels function."""

    def test_empty_labels_returns_empty(self):
        """Empty input should return empty output."""
        filtered, kept = _filter_rare_registry_labels([])
        assert filtered == []
        assert kept == []

    def test_filters_below_threshold(self):
        """Labels with counts below min_count should be removed."""
        # Create synthetic labels: 10 examples, 29 labels
        # First 3 labels have counts >= 5, rest have < 5
        labels = []
        for i in range(10):
            row = [0] * len(REGISTRY_TARGET_FIELDS)
            # First 3 fields always positive
            row[0] = 1
            row[1] = 1
            row[2] = 1
            # Fourth field only positive for first 3 examples
            if i < 3:
                row[3] = 1
            labels.append(row)

        filtered, kept = _filter_rare_registry_labels(labels, min_count=5)

        # Should keep first 3 fields (count=10 each), drop the rest
        assert len(kept) == 3
        assert kept == REGISTRY_TARGET_FIELDS[:3]
        assert len(filtered) == 10
        assert all(len(row) == 3 for row in filtered)

    def test_keeps_labels_at_threshold(self):
        """Labels with count exactly at min_count should be kept."""
        # Create labels where first field has exactly 5 positives
        labels = []
        for i in range(10):
            row = [0] * len(REGISTRY_TARGET_FIELDS)
            if i < 5:
                row[0] = 1
            labels.append(row)

        filtered, kept = _filter_rare_registry_labels(labels, min_count=5)

        assert REGISTRY_TARGET_FIELDS[0] in kept
        assert len(kept) == 1

    def test_custom_threshold(self):
        """Custom min_count threshold should be respected."""
        # First field has 3 positives
        labels = []
        for i in range(10):
            row = [0] * len(REGISTRY_TARGET_FIELDS)
            if i < 3:
                row[0] = 1
            labels.append(row)

        # With threshold 3, should keep
        filtered_3, kept_3 = _filter_rare_registry_labels(labels, min_count=3)
        assert len(kept_3) == 1

        # With threshold 4, should filter out
        filtered_4, kept_4 = _filter_rare_registry_labels(labels, min_count=4)
        assert len(kept_4) == 0

    def test_preserves_label_ordering(self):
        """Kept labels should maintain original ordering."""
        # Make fields at indices 0, 5, 10 have enough positives
        labels = []
        for i in range(10):
            row = [0] * len(REGISTRY_TARGET_FIELDS)
            row[0] = 1
            row[5] = 1
            row[10] = 1
            labels.append(row)

        filtered, kept = _filter_rare_registry_labels(labels, min_count=5)

        expected_order = [
            REGISTRY_TARGET_FIELDS[0],
            REGISTRY_TARGET_FIELDS[5],
            REGISTRY_TARGET_FIELDS[10],
        ]
        assert kept == expected_order
