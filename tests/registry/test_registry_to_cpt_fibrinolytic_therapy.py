from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.common.spans import Span
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


def test_registry_to_cpt_maps_to_32562_when_subsequent_token_found_in_indication() -> None:
    record = RegistryRecord.model_validate(
        {
            "clinical_context": {"primary_indication": "Empyema - subsequent day 2 tPA instillation."},
            "pleural_procedures": {"fibrinolytic_therapy": {"performed": True}},
        }
    )
    codes, rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32562" in codes
    assert "32561" not in codes
    assert "subsequent-day token" in rationales["32562"]


def test_registry_to_cpt_emits_audit_warning_when_32561_selected_but_tube_inserted_prior_day() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedure_date": "2026-01-26",
            "pleural_procedures": {"fibrinolytic_therapy": {"performed": True, "number_of_doses": 1}},
            "evidence": {
                "pleural_procedures.fibrinolytic_therapy.performed": [
                    Span(text="Date of chest tube insertion: 2026-01-25", start=0, end=10)
                ]
            },
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "32561" in codes
    assert any("audit_warning" in str(w).lower() for w in warnings)
