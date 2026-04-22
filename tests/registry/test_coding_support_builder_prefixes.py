from __future__ import annotations

from app.registry.application.coding_support_builder import build_coding_support_payload, default_evidence_prefixes_for_code
from app.registry.quality_signals import make_quality_signal_warning
from app.registry.schema import RegistryRecord


def test_elastography_codes_have_traceability_prefixes() -> None:
    p76982 = default_evidence_prefixes_for_code("76982")
    p76983 = default_evidence_prefixes_for_code("76983")

    assert "granular_data.linear_ebus_stations_detail" in p76982
    assert "procedures_performed.linear_ebus" in p76982
    assert "linear_ebus_stations" in p76982

    assert "granular_data.linear_ebus_stations_detail" in p76983
    assert "procedures_performed.linear_ebus" in p76983
    assert "linear_ebus_stations" in p76983


def test_navigation_imaging_codes_have_equipment_traceability_prefixes() -> None:
    p77012 = default_evidence_prefixes_for_code("77012")
    p76377 = default_evidence_prefixes_for_code("76377")

    assert "equipment.cbct_used" in p77012
    assert "equipment.fluoroscopy_used" in p77012

    assert "equipment.augmented_fluoroscopy" in p76377
    assert "equipment.cbct_used" in p76377


def test_coding_support_payload_includes_structured_quality_pass_signals() -> None:
    payload = build_coding_support_payload(
        record=RegistryRecord(),
        codes=[],
        derivation_warnings=[],
        quality_signal_warnings=[
            make_quality_signal_warning(
                "therapeutic_injection_cpt31573_ineligible",
                field="procedures_performed.therapeutic_injection",
                action="suppressed",
                detail="Structured therapeutic injection is present but explicitly marked cpt31573_eligible=false.",
                source="registry_to_cpt",
            )
        ],
    )

    quality_pass = payload.get("quality_pass") or {}
    signals = quality_pass.get("signals") or []

    assert len(signals) == 1
    assert signals[0]["signal"] == "therapeutic_injection_cpt31573_ineligible"
    assert signals[0]["field"] == "procedures_performed.therapeutic_injection"
