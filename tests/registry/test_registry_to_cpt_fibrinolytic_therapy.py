from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.schema import RegistryRecord


def test_registry_to_cpt_derives_32561_for_fibrinolysis_initial_day() -> None:
    record = RegistryRecord(pleural_procedures={"fibrinolytic_therapy": {"performed": True, "number_of_doses": 1}})
    codes, rationales, warnings = derive_all_codes_with_meta(record)

    assert "32561" in codes
    assert "32562" not in codes
    assert rationales["32561"] == "pleural_procedures.fibrinolytic_therapy.performed=true"
    assert warnings == []


def test_registry_to_cpt_derives_32562_for_fibrinolysis_subsequent_day() -> None:
    record = RegistryRecord(pleural_procedures={"fibrinolytic_therapy": {"performed": True, "number_of_doses": 3}})
    codes, rationales, warnings = derive_all_codes_with_meta(record)

    assert "32562" in codes
    assert "32561" not in codes
    assert (
        rationales["32562"]
        == "pleural_procedures.fibrinolytic_therapy.performed=true and number_of_doses>=2 (subsequent day)"
    )
    assert warnings == []

