from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.schema import RegistryRecord


def test_registry_to_cpt_does_not_bill_stent_for_assessment_only() -> None:
    record = RegistryRecord(
        procedures_performed={"airway_stent": {"performed": True, "action": "Assessment only"}}
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)

    assert "31636" not in codes
    assert "31638" not in codes
    assert warnings == []

