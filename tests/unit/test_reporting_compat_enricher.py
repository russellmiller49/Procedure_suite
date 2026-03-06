from app.reporting.normalization.compat_enricher import _add_compat_flat_fields


def test_add_compat_flat_fields_brushings_counts_text_does_not_require_brushings_object() -> None:
    raw = {"procedures_performed": {}, "source_text": "Brush x 2"}
    out = _add_compat_flat_fields(raw)
    assert out is raw
    assert isinstance(raw.get("bronchial_brushings"), dict)
    assert raw["bronchial_brushings"]["samples_collected"] == 2
    assert raw["bronchial_brushings"]["brush_tool"] is None


def test_add_compat_flat_fields_blvr_nested_maps_flat_fields() -> None:
    raw = {
        "procedures_performed": {
            "blvr": {
                "performed": True,
                "procedure_type": "Valve placement",
                "valve_type": "Zephyr (Pulmonx)",
                "number_of_valves": 3,
                "target_lobe": "RUL",
                "segments_treated": ["RB1", "RB2", "RB3"],
                "valve_sizes": ["5.5", "4.0", "4.0"],
                "collateral_ventilation_assessment": "Chartis negative",
            }
        },
        "source_text": "BLVR with Zephyr valves and Chartis negative in RUL.",
    }
    out = _add_compat_flat_fields(raw)
    assert out is raw
    assert raw["blvr_procedure_type"] == "Valve placement"
    assert raw["blvr_valve_type"] == "Zephyr (Pulmonx)"
    assert raw["blvr_number_of_valves"] == 3
    assert raw["blvr_target_lobe"] == "RUL"
    assert raw["blvr_segments_treated"] == ["RB1", "RB2", "RB3"]
    assert raw["blvr_valve_sizes"] == ["5.5", "4.0", "4.0"]
    assert raw["blvr_chartis_used"] is True
    assert raw["blvr_collateral_ventilation_absent"] is True


def test_add_compat_flat_fields_blvr_text_fallback_detects_removal() -> None:
    raw = {
        "procedures_performed": {
            "blvr": {
                "performed": True,
                "procedure_type": "Valve placement",
                "target_lobe": "RUL",
                "number_of_valves": 4,
            }
        },
        "source_text": "BLVR valve removal for persistent pneumothorax. All 3 valves RUL removed.",
    }
    out = _add_compat_flat_fields(raw)
    assert out is raw
    assert raw["blvr_procedure_type"] == "Valve removal"
    assert raw["blvr_valves_removed"] == 3
    assert "RUL" in raw["blvr_removal_locations"]
