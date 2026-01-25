from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.schema import RegistryRecord


def test_registry_to_cpt_derives_31640_from_mechanical_debulking() -> None:
    record = RegistryRecord(procedures_performed={"mechanical_debulking": {"performed": True}})
    codes, rationales, warnings = derive_all_codes_with_meta(record)

    assert "31640" in codes
    assert rationales["31640"] == "mechanical_debulking.performed=true"
    assert warnings == []


def test_registry_to_cpt_allows_31640_and_31641_when_both_modalities_present() -> None:
    record = RegistryRecord(
        procedures_performed={
            "mechanical_debulking": {"performed": True},
            "thermal_ablation": {"performed": True},
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)

    assert "31641" in codes
    assert "31640" in codes
    assert any("both excision (31640) and destruction (31641)" in warning.lower() for warning in warnings)
