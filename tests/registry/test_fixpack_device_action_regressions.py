from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes_with_meta,
    derive_units_for_codes,
)
from modules.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.schema import RegistryRecord


def test_doxycycline_instillation_sets_pleurodesis_and_does_not_code_chest_tube_insertion() -> None:
    note_text = (
        "Date of chest tube/TPC insertion: 01/01/2020\n"
        "1000 mg doxycycline was instilled through the chest tube.\n"
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    # Simulate a hallucinated new chest tube insertion that must be negated.
    record_data = record.model_dump()
    record_data.setdefault("pleural_procedures", {})["chest_tube"] = {"performed": True, "action": "Insertion"}
    record = RegistryRecord(**record_data)

    guardrails = ClinicalGuardrails()
    outcome = guardrails.apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None
    assert updated.pleural_procedures is not None
    assert updated.pleural_procedures.pleurodesis is not None
    assert updated.pleural_procedures.pleurodesis.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "32560" in codes
    assert "32551" not in codes
    assert "32556" not in codes
    assert "32557" not in codes


def test_stent_removal_language_overrides_false_placement_action() -> None:
    note_text = "Using forceps we were able to remove the stent en bloc."
    record = RegistryRecord(procedures_performed={"airway_stent": {"performed": True, "action": "Placement"}})

    guardrails = ClinicalGuardrails()
    updated = guardrails.apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Removal"

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31638" in codes
    assert "31636" not in codes


def test_stent_obstruction_cleanout_treated_as_assessment_only() -> None:
    note_text = "The stent was 60% obstructed with mucous. Once this was cleared, it was patent."
    record = RegistryRecord(procedures_performed={"airway_stent": {"performed": True, "action": "Placement"}})

    guardrails = ClinicalGuardrails()
    updated = guardrails.apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Assessment only"

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31636" not in codes
    assert "31638" not in codes


def test_peg_note_suppresses_bronchoscopy_procedures() -> None:
    note_text = (
        "PROCEDURE: EGD with PEG placement.\n"
        "A gastroscope was advanced into the stomach. Transillumination was used and a PEG was placed.\n"
    )
    record = RegistryRecord(procedures_performed={"diagnostic_bronchoscopy": {"performed": True}})

    guardrails = ClinicalGuardrails()
    updated = guardrails.apply_record_guardrails(note_text, record).record
    assert updated is not None

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31622" not in codes
    assert "31624" not in codes
    assert "31645" not in codes


def test_elastography_targets_drive_76982_76983_units_and_suppress_76981() -> None:
    record = RegistryRecord(
        procedures_performed={
            "linear_ebus": {
                "performed": True,
                "stations_sampled": ["11L", "4L", "4R"],
                "elastography_used": True,
            }
        }
    )
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "76982" in codes
    assert "76983" in codes
    assert "76981" not in codes

    units = derive_units_for_codes(record, codes)
    assert units.get("76983") == 2


def test_tbbx_and_tbna_multilobe_units_derive_for_addon_codes() -> None:
    record = RegistryRecord(
        procedures_performed={
            "transbronchial_cryobiopsy": {
                "performed": True,
                "locations_biopsied": ["RUL", "RLL", "LUL"],
            },
            "peripheral_tbna": {
                "performed": True,
                "targets_sampled": ["RUL", "RLL", "LUL"],
            },
        }
    )

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31628" in codes
    assert "31629" in codes
    assert "31632" in codes
    assert "31633" in codes

    units = derive_units_for_codes(record, codes)
    assert units.get("31632") == 2
    assert units.get("31633") == 2


def test_stent_site_dilation_bundles_31630_into_31636_by_default() -> None:
    record = RegistryRecord(
        procedures_performed={
            "airway_stent": {"performed": True, "action": "Placement"},
            "airway_dilation": {"performed": True, "method": "Balloon"},
        }
    )

    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "31636" in codes
    assert "31630" not in codes
    assert any("31630 (dilation) bundled into 31636" in w for w in warnings)


def test_stent_dilation_distinct_location_keeps_31630() -> None:
    record = RegistryRecord(
        procedures_performed={
            "airway_stent": {"performed": True, "action": "Placement", "location": "Trachea"},
            "airway_dilation": {"performed": True, "method": "Balloon", "location": "RML"},
        }
    )

    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "31636" in codes
    assert "31630" in codes
    assert not any("31630 (dilation) bundled into 31636" in w for w in warnings)


def test_ncci_suppresses_31645_when_ebus_tbna_present() -> None:
    record = RegistryRecord(
        procedures_performed={
            "linear_ebus": {"performed": True, "stations_sampled": ["11L", "4L", "4R"]},
            "therapeutic_aspiration": {"performed": True, "material": "Mucus plug"},
        }
    )
    codes, _rationales, warnings = derive_all_codes_with_meta(record)
    assert "31653" in codes
    assert "31645" not in codes
    assert any("Suppressed 31645" in w for w in warnings)
