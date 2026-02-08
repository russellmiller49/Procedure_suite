from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.postprocess import enrich_eus_b_sampling_details
from app.registry.schema import RegistryRecord


def test_enrich_eus_b_sampling_details_does_not_treat_identified_site_as_sampled() -> None:
    note_text = (
        "EUS-B Findings\n"
        "A linear endobronchial ultrasound bronchoscope was advanced into the esophagus.\n"
        "Left Hepatic Lobe was identified. Left Adrenal was identified.\n"
        "Procedure header: 43237 EGD and EUS inspection only.\n"
    )
    record = RegistryRecord(procedures_performed={"eus_b": {"performed": True}})

    warnings = enrich_eus_b_sampling_details(record, note_text)
    eus_b = record.procedures_performed.eus_b if record.procedures_performed else None
    assert eus_b is not None
    assert eus_b.sites_sampled in (None, [])
    assert not any("AUTO_EUS_B_DETAIL" in w for w in warnings)


def test_registry_to_cpt_derives_43237_for_eus_b_without_sampling() -> None:
    record = RegistryRecord(procedures_performed={"eus_b": {"performed": True}})
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "43237" in codes
    assert "43238" not in codes


def test_registry_to_cpt_derives_43238_for_eus_b_with_sampling() -> None:
    record = RegistryRecord(
        procedures_performed={"eus_b": {"performed": True, "sites_sampled": ["Left adrenal mass"]}}
    )
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "43238" in codes
    assert "43237" not in codes
