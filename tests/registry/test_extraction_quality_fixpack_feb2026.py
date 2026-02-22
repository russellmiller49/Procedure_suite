from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.deterministic_extractors import run_deterministic_extractors
from app.registry.postprocess import reconcile_ebus_sampling_from_narrative
from app.registry.postprocess.complications_reconcile import reconcile_complications_from_narrative
from app.registry.schema import RegistryRecord


def test_thoracentesis_guidance_backfill_from_chest_ultrasound_derives_32555() -> None:
    note_text = (
        "PROCEDURE:\n"
        "76604 Ultrasound, chest (includes mediastinum), real time with image documentation\n"
        "Thoracentesis was performed.\n"
    )
    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32555" in codes
    assert "32554" not in codes


def test_stent_placement_not_misclassified_as_removal_when_scope_removed() -> None:
    note_text = (
        "Rigid bronchoscope was removed and an Aero SEMS stent was advanced into the left mainstem and deployed."
    )
    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31636" in codes
    assert "31638" not in codes


def test_airway_dilation_prefers_explicit_max_diameter_over_kit_sequence() -> None:
    note_text = (
        "Balloon dilation was performed using a 12/13.5/15 mm Merritt dilatation balloon. "
        "The airway was dilated to a maximal diameter of 13.5 mm."
    )
    seed = run_deterministic_extractors(note_text)
    dilation = seed.get("procedures_performed", {}).get("airway_dilation") or {}
    assert dilation.get("performed") is True
    assert dilation.get("balloon_diameter_mm") == 13.5


def test_airway_dilation_location_prefers_nearest_mention() -> None:
    note_text = (
        "Left upper lobe was inspected. "
        "Balloon dilation was performed on the left lower lobe main bronchus."
    )
    seed = run_deterministic_extractors(note_text)
    dilation = seed.get("procedures_performed", {}).get("airway_dilation") or {}
    assert dilation.get("performed") is True
    assert dilation.get("location") == "LLL"


def test_reconcile_ebus_sampling_multiline_station_list_sets_passes_each_station() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {"station": "4L", "action": "inspected_only", "outcome": None, "evidence_quote": "4L"},
                        {"station": "7", "action": "inspected_only", "outcome": None, "evidence_quote": "7"},
                        {"station": "4R", "action": "inspected_only", "outcome": None, "evidence_quote": "4R"},
                    ],
                }
            }
        }
    )
    note_text = (
        "Sampling by transbronchial needle aspiration was performed beginning with the 4L lymph node,\n"
        "followed by the 7 and then 4R.\n"
        "A total of 5 biopsies was performed at each station.\n"
    )

    warnings = reconcile_ebus_sampling_from_narrative(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.linear_ebus is not None
    events = record.procedures_performed.linear_ebus.node_events or []
    by_station = {e.station.strip().upper(): e for e in events if e.station}

    for station in ("4L", "7", "4R"):
        assert station in by_station
        assert by_station[station].action == "needle_aspiration"
        assert by_station[station].passes == 5

    assert any("passes=5" in str(w) for w in warnings)


def test_blocker_prevent_blood_soiling_derives_nashville_grade_3() -> None:
    record = RegistryRecord.model_validate({})
    note_text = (
        "There was significant bleeding from biopsy sites. "
        "An endobronchial blocker was placed to prevent blood soiling of the contralateral lung."
    )

    _warnings = reconcile_complications_from_narrative(record, note_text)
    assert record.complications is not None
    assert record.complications.bleeding is not None
    assert record.complications.bleeding.bleeding_grade_nashville == 3


def test_blvr_inspection_only_visualized_valves_treated_as_not_performed() -> None:
    note_text = "Previously placed endobronchial valves were visualized and appeared well placed."
    record = RegistryRecord(procedures_performed={"blvr": {"performed": True, "procedure_type": "Valve placement"}})

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.blvr is not None
    assert updated.procedures_performed.blvr.performed is False


def test_blvr_valve_removal_clears_foreign_body_removal() -> None:
    note_text = "A Spiration valve was placed and subsequently removed because it was too large."
    record = RegistryRecord(
        procedures_performed={
            "blvr": {"performed": True, "procedure_type": "Valve placement"},
            "foreign_body_removal": {"performed": True},
        }
    )

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.foreign_body_removal is not None
    assert updated.procedures_performed.foreign_body_removal.performed is False

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31635" not in codes


def test_radial_ebus_not_visualized_suppresses_31654() -> None:
    record = RegistryRecord(
        procedures_performed={
            "bal": {"performed": True},
            "radial_ebus": {"performed": True, "probe_position": "Not visualized"},
        }
    )
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31624" in codes
    assert "31654" not in codes


def test_guardrails_strip_volume_prefix_from_therapeutic_injection_medication() -> None:
    note_text = "5 mL of Kenalog 10 mg/milliliter solution was injected."
    record = RegistryRecord(procedures_performed={"therapeutic_injection": {"performed": True, "medication": "mL of Kenalog"}})
    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.therapeutic_injection is not None
    assert updated.procedures_performed.therapeutic_injection.medication == "Kenalog"


def test_guardrails_downgrade_purulent_secretions_without_purulence_language() -> None:
    note_text = "Therapeutic aspiration was performed to remove thick secretions."
    record = RegistryRecord(procedures_performed={"therapeutic_aspiration": {"performed": True, "material": "Purulent secretions"}})
    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.therapeutic_aspiration is not None
    assert updated.procedures_performed.therapeutic_aspiration.material == "Mucus"

