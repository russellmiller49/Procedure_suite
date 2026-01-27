from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.common.spans import Span
from modules.registry.schema import RegistryRecord


def test_blvr_valve_placement_addon_lobe_and_chartis_distinct_lobe_allows_31634() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {
                    "performed": True,
                    "procedure_type": "Valve placement",
                    "target_lobe": "LUL",
                }
            },
            "granular_data": {
                "blvr_valve_placements": [
                    {
                        "valve_number": 1,
                        "target_lobe": "LUL",
                        "segment": "LB1+2",
                        "valve_size": "4.0",
                        "valve_type": "Zephyr (Pulmonx)",
                        "deployment_successful": True,
                    },
                    {
                        "valve_number": 2,
                        "target_lobe": "LLL",
                        "segment": "LB6",
                        "valve_size": "4.0",
                        "valve_type": "Zephyr (Pulmonx)",
                        "deployment_successful": True,
                    },
                ],
                "blvr_chartis_measurements": [
                    {"lobe_assessed": "LUL", "cv_result": "CV Negative"},
                    {"lobe_assessed": "RUL", "cv_result": "CV Negative"},
                ],
            },
        }
    )

    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "31647" in codes
    assert "31651" in codes  # additional lobe
    assert "31634" in codes  # Chartis allowed due to distinct lobe (RUL)
    assert any("modifier" in str(w).lower() for w in warnings)


def test_chartis_same_lobe_as_valves_suppresses_31634() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {
                    "performed": True,
                    "procedure_type": "Valve placement",
                    "target_lobe": "LUL",
                }
            },
            "granular_data": {
                "blvr_valve_placements": [
                    {
                        "valve_number": 1,
                        "target_lobe": "LUL",
                        "segment": "LB1+2",
                        "valve_size": "4.0",
                        "valve_type": "Zephyr (Pulmonx)",
                        "deployment_successful": True,
                    }
                ],
                "blvr_chartis_measurements": [{"lobe_assessed": "LUL", "cv_result": "CV Negative"}],
            },
        }
    )

    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "31647" in codes
    assert "31634" not in codes
    assert any("suppressed 31634" in str(w).lower() for w in warnings)


def test_moderate_sedation_under_10_minutes_is_suppressed() -> None:
    record = RegistryRecord.model_validate(
        {
            "sedation": {
                "type": "Moderate",
                "anesthesia_provider": "Proceduralist",
                "intraservice_minutes": 9,
            }
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "99152" not in codes
    assert "99153" not in codes
    assert any("suppress" in str(w).lower() and "99152" in str(w) for w in warnings)


def test_moderate_sedation_uses_times_when_minutes_missing() -> None:
    record = RegistryRecord.model_validate(
        {
            "sedation": {
                "type": "Moderate",
                "anesthesia_provider": "Proceduralist",
                "start_time": "10:15",
                "end_time": "10:45",
            }
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "99152" in codes
    assert "99153" in codes  # 30 minutes implies add-on time beyond initial 15
    assert not any("not deriving 99152" in str(w).lower() for w in warnings)


def test_blvr_fallback_derives_31647_when_granular_missing_and_family_blvr() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedure_families": ["BLVR"],
            "procedures_performed": {"blvr": {"performed": True}},
        }
    )

    codes, rationales, warnings = derive_all_codes_with_meta(record)
    assert "31647" in codes
    assert "31651" not in codes
    assert "31648" not in codes
    assert "procedure_families includes BLVR" in rationales["31647"]
    assert not any("chartis" in str(w).lower() for w in warnings)


def test_blvr_mixed_manufacturer_emits_needs_review_warning() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {"performed": True, "procedure_type": "Valve placement", "valve_type": "Zephyr (Pulmonx)"}
            },
            "evidence": {
                "procedures_performed.blvr.valve_type": [
                    Span(text="Spiration valve also referenced", start=0, end=10)
                ]
            },
        }
    )

    _codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert any("mixed blvr valve manufacturers" in str(w).lower() for w in warnings)
