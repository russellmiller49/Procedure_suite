from __future__ import annotations

from app.registry.application.coding_support_builder import default_evidence_prefixes_for_code


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
