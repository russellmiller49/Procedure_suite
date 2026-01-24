from modules.registry.schema_granular import derive_procedures_from_granular


def test_derive_procedures_from_granular_up_propagates_navigation_performed() -> None:
    granular_data = {
        "navigation_targets": [
            {
                "target_number": 1,
                "target_location_text": "RUL apical segment lesion",
            }
        ]
    }
    existing_procedures = {
        "navigational_bronchoscopy": {"performed": False}
    }

    updated, _warnings = derive_procedures_from_granular(
        granular_data=granular_data,
        existing_procedures=existing_procedures,
    )

    assert updated["navigational_bronchoscopy"]["performed"] is True


def test_derive_procedures_from_granular_up_propagates_linear_ebus_performed() -> None:
    granular_data = {
        "linear_ebus_stations_detail": [
            {"station": "7", "sampled": True}
        ]
    }
    existing_procedures = {
        "linear_ebus": {"performed": False}
    }

    updated, warnings = derive_procedures_from_granular(
        granular_data=granular_data,
        existing_procedures=existing_procedures,
    )

    assert updated["linear_ebus"]["performed"] is True
    assert updated["linear_ebus"]["stations_sampled"] == ["7"]
    assert not any("procedures_performed.linear_ebus.performed=true" in w for w in warnings)


def test_derive_procedures_from_granular_up_propagates_bal_performed() -> None:
    granular_data = {
        "specimens_collected": [
            {
                "specimen_number": 1,
                "source_procedure": "BAL",
                "source_location": "RLL",
                "specimen_count": 1,
            }
        ]
    }
    existing_procedures = {
        "bal": {"performed": False}
    }

    updated, _warnings = derive_procedures_from_granular(
        granular_data=granular_data,
        existing_procedures=existing_procedures,
    )

    assert updated["bal"]["performed"] is True


def test_derive_procedures_from_granular_up_propagates_sampling_tools_paths() -> None:
    granular_data = {
        "navigation_targets": [
            {
                "target_number": 1,
                "target_location_text": "RUL posterior segment lesion",
                "sampling_tools_used": ["Needle", "Forceps"],
                "number_of_needle_passes": 4,
                "number_of_forceps_biopsies": 3,
            }
        ],
        "specimens_collected": [
            {
                "specimen_number": 1,
                "source_procedure": "Bronchial wash",
                "source_location": "RUL",
                "specimen_count": 1,
            }
        ],
    }

    updated, warnings = derive_procedures_from_granular(
        granular_data=granular_data,
        existing_procedures={},
    )

    assert updated["peripheral_tbna"]["performed"] is True
    assert "RUL posterior segment lesion" in (updated["peripheral_tbna"].get("targets_sampled") or [])
    assert updated["transbronchial_biopsy"]["performed"] is True
    assert updated["transbronchial_biopsy"]["number_of_samples"] == 3
    assert updated["bronchial_wash"]["performed"] is True
    assert updated["bronchial_wash"]["location"] == "RUL"
    assert not any("performed=true but" in w for w in warnings)


def test_derive_procedures_from_granular_filters_invalid_navigation_sampling_tools() -> None:
    granular_data = {
        "navigation_targets": [
            {
                "target_number": 1,
                "target_location_text": "RUL posterior segment lesion",
                "sampling_tools_used": ["BAL", "Needle", "forcep"],
            }
        ]
    }
    existing_procedures = {
        "navigational_bronchoscopy": {"performed": True, "sampling_tools_used": ["BAL"]}
    }

    updated, _warnings = derive_procedures_from_granular(
        granular_data=granular_data,
        existing_procedures=existing_procedures,
    )

    assert updated["navigational_bronchoscopy"]["sampling_tools_used"] == ["Forceps", "Needle"]


def test_derive_procedures_from_granular_warns_on_ebus_performed_without_stations() -> None:
    granular_data = {
        "linear_ebus_stations_detail": [
            {"station": "7", "sampled": False}
        ]
    }
    existing_procedures = {
        "linear_ebus": {"performed": True}
    }

    _updated, warnings = derive_procedures_from_granular(
        granular_data=granular_data,
        existing_procedures=existing_procedures,
    )

    assert any("procedures_performed.linear_ebus.performed=true" in w for w in warnings)
