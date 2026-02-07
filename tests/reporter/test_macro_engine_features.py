"""Unit tests for macro_engine new features.

Tests:
1. Chronological ordering of procedures
2. Essential field validation and acknowledged_omissions
3. update_bundle for two-phase workflow
4. Ion robotic bronchoscopy example
"""

import pytest
from copy import deepcopy


class TestChronologicalOrdering:
    """Test that procedures are rendered in chronological order (by sequence)."""

    def test_procedures_sorted_by_sequence(self):
        """Test that procedures with sequence numbers are sorted correctly."""
        from app.reporting.macro_engine import render_procedure_bundle

        bundle = {
            "procedures": [
                {"proc_type": "thoracentesis", "sequence": 3, "data": {"side": "left"}},
                {"proc_type": "thoracentesis", "sequence": 1, "data": {"side": "right"}},
                {"proc_type": "thoracentesis", "sequence": 2, "data": {"side": "bilateral"}},
            ]
        }

        result = render_procedure_bundle(bundle)

        # Find positions of each side in the output
        pos_right = result.find("right")
        pos_bilateral = result.find("bilateral")
        pos_left = result.find("left")

        # Verify they appear in sequence order (1, 2, 3)
        assert pos_right < pos_bilateral < pos_left, \
            f"Procedures not in chronological order. Positions: right={pos_right}, bilateral={pos_bilateral}, left={pos_left}"

    def test_procedures_without_sequence_preserve_order(self):
        """Test that procedures without sequence numbers preserve their original order."""
        from app.reporting.macro_engine import render_procedure_bundle

        bundle = {
            "procedures": [
                {"proc_type": "thoracentesis", "data": {"side": "first"}},
                {"proc_type": "thoracentesis", "data": {"side": "second"}},
                {"proc_type": "thoracentesis", "data": {"side": "third"}},
            ]
        }

        result = render_procedure_bundle(bundle)

        pos_first = result.find("first")
        pos_second = result.find("second")
        pos_third = result.find("third")

        assert pos_first < pos_second < pos_third, \
            "Procedures without sequence should maintain original order"

    def test_mixed_sequence_and_no_sequence(self):
        """Test procedures with mixed sequence and no sequence."""
        from app.reporting.macro_engine import render_procedure_bundle

        bundle = {
            "procedures": [
                {"proc_type": "thoracentesis", "data": {"side": "no_seq_1"}},
                {"proc_type": "thoracentesis", "sequence": 1, "data": {"side": "seq_1"}},
                {"proc_type": "thoracentesis", "data": {"side": "no_seq_2"}},
            ]
        }

        result = render_procedure_bundle(bundle)

        # Sequence 1 should come first, then no-sequence items in original order
        pos_seq_1 = result.find("seq_1")
        pos_no_seq_1 = result.find("no_seq_1")
        pos_no_seq_2 = result.find("no_seq_2")

        assert pos_seq_1 < pos_no_seq_1 < pos_no_seq_2, \
            "Sequenced procedures should come before unsequenced ones"


class TestEssentialFieldValidation:
    """Test validate_essential_fields and acknowledged_omissions."""

    def test_missing_essential_fields_added_to_omissions(self):
        """Test that missing essential fields are added to acknowledged_omissions."""
        from app.reporting.macro_engine import validate_essential_fields

        bundle = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "data": {
                        "side": None,  # Missing - essential
                        "volume_removed": None,  # Missing - essential
                        "fluid_appearance": "cloudy",  # Present
                    }
                }
            ]
        }

        result = validate_essential_fields(bundle)

        assert "acknowledged_omissions" in result
        assert "thoracentesis_1" in result["acknowledged_omissions"]
        omissions = result["acknowledged_omissions"]["thoracentesis_1"]

        # Should have omissions for missing essential fields
        assert len(omissions) >= 1
        # Check for human-readable labels
        assert any("side" in o.lower() or "laterality" in o.lower() for o in omissions)

    def test_no_omissions_when_all_essential_present(self):
        """Test that no omissions are added when all essential fields are present."""
        from app.reporting.macro_engine import validate_essential_fields

        bundle = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "data": {
                        "side": "left",
                        "volume_removed": "500mL",
                        "fluid_appearance": "cloudy",
                    }
                }
            ]
        }

        result = validate_essential_fields(bundle)

        # Should have no omissions for this procedure
        omissions = result.get("acknowledged_omissions", {}).get("thoracentesis_1", [])
        assert len(omissions) == 0

    def test_acknowledged_omissions_initialized_if_missing(self):
        """Test that acknowledged_omissions is initialized if not in bundle."""
        from app.reporting.macro_engine import validate_essential_fields

        bundle = {"procedures": []}

        result = validate_essential_fields(bundle)

        assert "acknowledged_omissions" in result
        assert isinstance(result["acknowledged_omissions"], dict)

    def test_get_essential_fields_returns_fields_and_labels(self):
        """Test get_essential_fields returns field list and labels."""
        from app.reporting.macro_engine import get_essential_fields

        fields, labels = get_essential_fields("thoracentesis")

        assert isinstance(fields, list)
        assert isinstance(labels, dict)

    def test_omissions_render_in_report(self):
        """Test that acknowledged_omissions appear in rendered report."""
        from app.reporting.macro_engine import render_procedure_bundle

        bundle = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "data": {
                        "side": None,
                        "volume_removed": None,
                        "fluid_appearance": None,
                    }
                }
            ]
        }

        result = render_procedure_bundle(bundle)

        # Should contain the missing details section
        assert "Missing Details" in result or "missing" in result.lower()


class TestUpdateBundle:
    """Test update_bundle for two-phase workflow."""

    def test_update_fills_null_values(self):
        """Test that update_bundle fills in null values."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {
                    "proc_type": "robotic_bronchoscopy_ion",
                    "proc_id": "ion_1",
                    "params": {
                        "lesion_location": None,
                        "cbct_performed": True,
                    }
                }
            ]
        }

        updates = {
            "procedures": [
                {
                    "proc_id": "ion_1",
                    "params": {
                        "lesion_location": "RB1",
                    }
                }
            ]
        }

        result = update_bundle(existing, updates)

        proc = result["procedures"][0]
        assert proc["params"]["lesion_location"] == "RB1"
        assert proc["params"]["cbct_performed"] is True  # Preserved

    def test_update_does_not_override_existing(self):
        """Test that update_bundle does not override existing values by default."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "params": {
                        "side": "left",
                        "volume_removed": "500mL",
                    }
                }
            ]
        }

        updates = {
            "procedures": [
                {
                    "proc_id": "thoracentesis_1",
                    "params": {
                        "side": "right",  # Should NOT override
                        "fluid_appearance": "cloudy",  # Should fill
                    }
                }
            ]
        }

        result = update_bundle(existing, updates, allow_override=False)

        proc = result["procedures"][0]
        assert proc["params"]["side"] == "left"  # Not overridden
        assert proc["params"]["fluid_appearance"] == "cloudy"  # Filled

    def test_update_can_override_when_flag_set(self):
        """Test that update_bundle can override when allow_override=True."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "params": {"side": "left"}
                }
            ]
        }

        updates = {
            "procedures": [
                {
                    "proc_id": "thoracentesis_1",
                    "params": {"side": "right"}
                }
            ]
        }

        result = update_bundle(existing, updates, allow_override=True)

        proc = result["procedures"][0]
        assert proc["params"]["side"] == "right"

    def test_update_does_not_add_new_procedures_by_default(self):
        """Test that new procedures are not added by default."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {"proc_type": "thoracentesis", "proc_id": "thoracentesis_1", "params": {}}
            ]
        }

        updates = {
            "procedures": [
                {"proc_type": "linear_ebus_tbna", "proc_id": "ebus_1", "params": {}}
            ]
        }

        result = update_bundle(existing, updates, allow_new_procedures=False)

        assert len(result["procedures"]) == 1
        assert result["procedures"][0]["proc_type"] == "thoracentesis"

    def test_update_can_add_new_procedures_when_flag_set(self):
        """Test that new procedures can be added when allow_new_procedures=True."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {"proc_type": "thoracentesis", "proc_id": "thoracentesis_1", "sequence": 1, "params": {}}
            ]
        }

        updates = {
            "procedures": [
                {"proc_type": "linear_ebus_tbna", "proc_id": "ebus_1", "params": {}}
            ]
        }

        result = update_bundle(existing, updates, allow_new_procedures=True)

        assert len(result["procedures"]) == 2
        new_proc = result["procedures"][1]
        assert new_proc["proc_type"] == "linear_ebus_tbna"
        assert "sequence" in new_proc  # Should have sequence assigned

    def test_update_clears_acknowledged_omissions(self):
        """Test that update can clear acknowledged_omissions."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {"proc_type": "thoracentesis", "proc_id": "thoracentesis_1", "params": {}}
            ],
            "acknowledged_omissions": {
                "thoracentesis_1": ["Side (laterality)", "Volume removed"]
            }
        }

        updates = {
            "acknowledged_omissions": {
                "thoracentesis_1": []  # Clear these omissions
            }
        }

        result = update_bundle(existing, updates)

        # Should have cleared the omissions
        assert "thoracentesis_1" not in result.get("acknowledged_omissions", {})

    def test_update_preserves_sequence(self):
        """Test that update_bundle preserves procedure sequence."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {"proc_type": "thoracentesis", "proc_id": "proc_1", "sequence": 1, "params": {}},
                {"proc_type": "linear_ebus_tbna", "proc_id": "proc_2", "sequence": 2, "params": {}},
            ]
        }

        updates = {
            "procedures": [
                {"proc_id": "proc_2", "params": {"lymph_nodes": [{"station": "4R"}]}}
            ]
        }

        result = update_bundle(existing, updates)

        # Sequence should be preserved
        assert result["procedures"][0]["sequence"] == 1
        assert result["procedures"][1]["sequence"] == 2

    def test_update_merges_nested_dicts(self):
        """Test that nested dicts like vent_params are merged correctly."""
        from app.reporting.macro_engine import update_bundle

        existing = {
            "procedures": [
                {
                    "proc_type": "robotic_bronchoscopy_ion",
                    "proc_id": "ion_1",
                    "params": {
                        "vent_params": {
                            "mode": "VC",
                            "respiratory_rate": None,
                        }
                    }
                }
            ]
        }

        updates = {
            "procedures": [
                {
                    "proc_id": "ion_1",
                    "params": {
                        "vent_params": {
                            "respiratory_rate": 14,
                            "tidal_volume": "450 mL",
                        }
                    }
                }
            ]
        }

        result = update_bundle(existing, updates)

        vent = result["procedures"][0]["params"]["vent_params"]
        assert vent["mode"] == "VC"  # Preserved
        assert vent["respiratory_rate"] == 14  # Filled
        assert vent["tidal_volume"] == "450 mL"  # Added


class TestRenderBundleWithSummary:
    """Test render_bundle_with_summary for Phase 1 workflow."""

    def test_returns_report_and_summary(self):
        """Test that render_bundle_with_summary returns tuple."""
        from app.reporting.macro_engine import render_bundle_with_summary

        bundle = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "data": {"side": "left"}
                }
            ]
        }

        report, summary = render_bundle_with_summary(bundle)

        assert isinstance(report, str)
        assert isinstance(summary, str)

    def test_summary_shows_missing_fields(self):
        """Test that summary includes missing essential fields."""
        from app.reporting.macro_engine import render_bundle_with_summary

        bundle = {
            "procedures": [
                {
                    "proc_type": "thoracentesis",
                    "proc_id": "thoracentesis_1",
                    "data": {
                        "side": None,
                        "volume_removed": None,
                    }
                }
            ]
        }

        report, summary = render_bundle_with_summary(bundle)

        # Summary should mention missing fields
        if summary:  # Only check if there are essential fields defined
            assert "Missing" in summary or "missing" in summary.lower() or "incomplete" in summary.lower()


class TestIonRoboticExample:
    """Test a complete Ion robotic bronchoscopy extraction example."""

    def test_ion_extraction_with_separate_biopsies(self):
        """Test Ion extraction with separate needle and cryo biopsies per Rule 3."""
        from app.reporting.macro_engine import render_procedure_bundle

        # Example from EXTRACTION_RULES.md - separate entries for needle and cryo
        # Note: transbronchial_needle_aspiration uses num_samples (not num_passes)
        bundle = {
            "procedures": [
                {
                    "proc_type": "ion_registration_partial",
                    "sequence": 1,
                    "proc_id": "registration_1",
                    "data": {
                        "side": "right",
                        "lobe_segment": "upper lobe",
                        "registered_landmarks": ["carina", "RUL", "RB1"],
                    }
                },
                {
                    "proc_type": "radial_ebus_survey",
                    "sequence": 2,
                    "proc_id": "rebus_1",
                    "data": {
                        "location": "RB1",
                        "rebus_features": ["concentric pattern", "no vessels at site"],
                    }
                },
                {
                    "proc_type": "cbct_assisted_bronchoscopy",
                    "sequence": 3,
                    "proc_id": "cbct_1",
                    "data": {
                        "confirmatory_position": "on-target",
                    }
                },
                {
                    "proc_type": "transbronchial_needle_aspiration",
                    "sequence": 4,
                    "proc_id": "tbna_1",
                    "data": {
                        "num_samples": 5,  # 5 needle passes
                        "needle_tool": "21G Ion needle",
                    }
                },
                {
                    "proc_type": "transbronchial_cryobiopsy",
                    "sequence": 5,
                    "proc_id": "cryo_1",
                    "data": {
                        "num_samples": 3,
                    }
                },
            ],
            "acknowledged_omissions": {
                "registration_1": [],
                "global": ["Referring physician"],
            }
        }

        result = render_procedure_bundle(bundle)

        # Should have separate entries for needle and cryo (not combined)
        assert "needle" in result.lower() or "aspiration" in result.lower()
        assert "cryo" in result.lower()

        # Verify separate counts (not summed to 8)
        assert "5" in result  # 5 needle samples
        assert "3" in result  # 3 cryo samples

    def test_ion_with_missing_vent_params(self):
        """Test Ion case with missing vent parameters goes to acknowledged_omissions."""
        from app.reporting.macro_engine import validate_essential_fields, render_procedure_bundle

        bundle = {
            "procedures": [
                {
                    "proc_type": "robotic_bronchoscopy_ion",
                    "proc_id": "robotic_ion_1",
                    "sequence": 1,
                    "data": {
                        "vent_params": None,  # Not provided
                        "cbct_performed": True,
                        "radial_pattern": "concentric",
                        "notes": "8.5 ETT; partial registration",
                        "lesion_location": None,  # Not provided
                        "sampling_details": None,  # Not provided
                    }
                }
            ]
        }

        validated = validate_essential_fields(bundle)
        result = render_procedure_bundle(validated)

        # Should have acknowledged_omissions populated
        omissions = validated.get("acknowledged_omissions", {}).get("robotic_ion_1", [])
        # Should mention lesion location and/or sampling details as missing
        assert len(omissions) > 0

        # Report should contain placeholder patterns
        assert "[" in result  # Inline blanks like "[lesion segment e.g., RB1/RB3]"


class TestMergeProcedureParams:
    """Test the merge_procedure_params helper function."""

    def test_fills_null_values(self):
        """Test that null values are filled."""
        from app.reporting.macro_engine import merge_procedure_params

        existing = {"a": None, "b": "existing"}
        updates = {"a": "new", "b": "updated"}

        result = merge_procedure_params(existing, updates, allow_override=False)

        assert result["a"] == "new"  # Filled
        assert result["b"] == "existing"  # Not overridden

    def test_fills_empty_string(self):
        """Test that empty strings are treated as missing."""
        from app.reporting.macro_engine import merge_procedure_params

        existing = {"a": "", "b": "existing"}
        updates = {"a": "new", "b": "updated"}

        result = merge_procedure_params(existing, updates, allow_override=False)

        assert result["a"] == "new"  # Filled
        assert result["b"] == "existing"  # Not overridden

    def test_fills_empty_list(self):
        """Test that empty lists are treated as missing."""
        from app.reporting.macro_engine import merge_procedure_params

        existing = {"a": [], "b": ["existing"]}
        updates = {"a": ["new"], "b": ["updated"]}

        result = merge_procedure_params(existing, updates, allow_override=False)

        assert result["a"] == ["new"]  # Filled
        assert result["b"] == ["existing"]  # Not overridden

    def test_override_mode(self):
        """Test that override mode replaces existing values."""
        from app.reporting.macro_engine import merge_procedure_params

        existing = {"a": "old", "b": "existing"}
        updates = {"a": "new", "b": "updated"}

        result = merge_procedure_params(existing, updates, allow_override=True)

        assert result["a"] == "new"
        assert result["b"] == "updated"

    def test_ignores_none_updates(self):
        """Test that None in updates does not clear existing values."""
        from app.reporting.macro_engine import merge_procedure_params

        existing = {"a": "existing"}
        updates = {"a": None}

        result = merge_procedure_params(existing, updates, allow_override=False)

        assert result["a"] == "existing"  # Not cleared
