from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.schema import RegistryRecord


def test_registry_to_cpt_derives_31640_from_mechanical_debulking() -> None:
    record = RegistryRecord(procedures_performed={"mechanical_debulking": {"performed": True, "material_type": "tumor"}})
    codes, rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" in codes
    assert rationales["31640"] == "mechanical_debulking.material_type=tumor"
    assert warnings == []


def test_registry_to_cpt_retains_31640_and_31641_when_same_site_overlap_is_not_explicit() -> None:
    record = RegistryRecord(
        procedures_performed={
            "mechanical_debulking": {"performed": True, "material_type": "tumor"},
            "thermal_ablation": {"performed": True},
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" in codes
    assert "31641" in codes
    assert any(
        "same-site destruction/excision overlap was not explicit" in str(warning)
        for warning in warnings
    )


def test_registry_to_cpt_allows_31640_and_31641_when_locations_distinct() -> None:
    record = RegistryRecord(
        procedures_performed={
            "mechanical_debulking": {"performed": True, "location": "RUL", "material_type": "tumor"},
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


def test_registry_to_cpt_suppresses_31640_for_non_tumor_mechanical_debulking() -> None:
    record = RegistryRecord(
        procedures_performed={"mechanical_debulking": {"performed": True, "material_type": "granulation"}}
    )

    codes, _rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" not in codes
    assert any("not billable as 31640" in str(warning) for warning in warnings)
