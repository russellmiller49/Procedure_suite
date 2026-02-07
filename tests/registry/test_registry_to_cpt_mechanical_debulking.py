from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.schema import RegistryRecord


def test_registry_to_cpt_derives_31640_from_mechanical_debulking() -> None:
    record = RegistryRecord(procedures_performed={"mechanical_debulking": {"performed": True}})
    codes, rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" in codes
    assert rationales["31640"] == "mechanical_debulking.performed=true"
    assert warnings == []


def test_registry_to_cpt_bundles_31641_into_31640_by_default_when_location_unknown() -> None:
    record = RegistryRecord(
        procedures_performed={
            "mechanical_debulking": {"performed": True},
            "thermal_ablation": {"performed": True},
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" in codes
    assert "31641" not in codes
    assert any(
        str(warning).startswith("31641 (destruction) bundled into 31640")
        for warning in warnings
    )


def test_registry_to_cpt_allows_31640_and_31641_when_locations_distinct() -> None:
    record = RegistryRecord(
        procedures_performed={
            "mechanical_debulking": {"performed": True, "location": "RUL"},
            "thermal_ablation": {"performed": True, "location": "LLL"},
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" in codes
    assert "31641" in codes
    assert any(
        str(warning).startswith("31641 requires Modifier 59")
        for warning in warnings
    )
