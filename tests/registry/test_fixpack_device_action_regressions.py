from __future__ import annotations

from dataclasses import dataclass, field
from app.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes_with_meta,
    derive_units_for_codes,
)
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.application.registry_service import RegistryService
from app.registry.deterministic_extractors import run_deterministic_extractors
from app.registry.schema import RegistryRecord
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


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


def test_stent_exchange_language_keeps_revision_semantics() -> None:
    note_text = (
        "The previously placed Y-stent was removed en bloc. "
        "A custom silicone Y-stent was inserted and seated appropriately."
    )
    record = RegistryRecord(
        procedures_performed={"airway_stent": {"performed": True, "action": "Revision/Repositioning", "airway_stent_removal": True}}
    )

    guardrails = ClinicalGuardrails()
    updated = guardrails.apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Revision/Repositioning"
    assert stent.airway_stent_removal is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31638" in codes


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
    assert "31631" in codes
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


@dataclass
class _StubPathwayResult:
    source: str
    codes: list[str] = field(default_factory=list)
    confidences: dict[str, float] = field(default_factory=dict)
    rationales: dict[str, str] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class _StubParallelResult:
    final_codes: list[str] = field(default_factory=list)
    final_confidences: dict[str, float] = field(default_factory=dict)
    path_a_result: _StubPathwayResult = field(default_factory=lambda: _StubPathwayResult(source="ner_rules"))
    path_b_result: _StubPathwayResult = field(default_factory=lambda: _StubPathwayResult(source="ml_classification"))
    code_confidences: list[Any] = field(default_factory=list)
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
    explanations: dict[str, str] = field(default_factory=dict)
    total_time_ms: float = 0.0


class _StubParallelOrchestrator:
    def process(self, note_text: str, ml_predictor: Any | None = None) -> _StubParallelResult:  # noqa: ARG002
        record = RegistryRecord()
        details = {
            "record": record,
            "ner_entities": [],
            "ner_entity_count": 0,
            "stations_sampled_count": 0,
        }
        path_a = _StubPathwayResult(source="ner_rules", details=details)
        path_b = _StubPathwayResult(source="ml_classification")
        return _StubParallelResult(path_a_result=path_a, path_b_result=path_b)

    def _build_ner_evidence(self, entities: list[Any] | None) -> dict[str, list[Any]]:  # noqa: ARG002
        return {}


def _march_2026_notes_dir() -> Path:
    return Path(__file__).resolve().parents[2].parent / "proc_suite_notes" / "new_synthetic_notes_3_5_26"


def _load_march_2026_note(*, batch: str, note_name: str) -> str:
    note_path = _march_2026_notes_dir() / batch / f"{note_name}.txt"
    if not note_path.is_file():
        raise FileNotFoundError(note_path)
    return note_path.read_text(encoding="utf-8")


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=MagicMock(),
        parallel_orchestrator=_StubParallelOrchestrator(),
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)
    return service.extract_fields(note_text)


def test_real_note_032_confirmation_only_trach_exchange_does_not_code_bronchoscopy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_3", note_name="note_032")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.procedures_performed is not None
    airway_device_action = getattr(record.procedures_performed, "airway_device_action", None)
    assert airway_device_action is not None
    assert airway_device_action.performed is True
    assert airway_device_action.device_type == "Tracheostomy tube"
    assert airway_device_action.action == "Exchange"

    assert record.established_tracheostomy_route is not True
    procedures = record.procedures_performed
    diagnostic = procedures.diagnostic_bronchoscopy if procedures is not None else None
    assert diagnostic is None or diagnostic.performed is not True

    assert "31615" not in result.cpt_codes
    assert "31622" not in result.cpt_codes


def test_real_note_039_t_tube_exchange_keeps_revision_without_standby_laser_ablation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_3", note_name="note_039")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.procedures_performed is not None

    airway_device_action = getattr(record.procedures_performed, "airway_device_action", None)
    assert airway_device_action is not None
    assert airway_device_action.performed is True
    assert airway_device_action.device_type == "Montgomery T-tube"
    assert airway_device_action.action == "Exchange"

    stent = record.procedures_performed.airway_stent
    assert stent is None or stent.performed is not True
    thermal = record.procedures_performed.thermal_ablation
    assert thermal is None or thermal.performed is not True

    assert "31638" not in result.cpt_codes
    assert "31641" not in result.cpt_codes


def test_real_note_046_t_tube_sidearm_clearance_is_not_brushings_and_keeps_31622(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_3", note_name="note_046")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.procedures_performed is not None

    diagnostic = record.procedures_performed.diagnostic_bronchoscopy
    assert diagnostic is not None
    assert diagnostic.performed is True
    abnormalities = diagnostic.airway_abnormalities or []
    assert "Stenosis" not in abnormalities

    brushings = record.procedures_performed.brushings
    assert brushings is None or brushings.performed is not True

    assert "31622" in result.cpt_codes
    assert "31623" not in result.cpt_codes


def test_real_note_012_trach_exchange_with_suction_keeps_established_route_and_31622(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_6", note_name="note_012")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.established_tracheostomy_route is True
    assert record.procedures_performed is not None
    airway_device_action = getattr(record.procedures_performed, "airway_device_action", None)
    assert airway_device_action is not None
    assert airway_device_action.performed is True
    assert airway_device_action.device_type == "Tracheostomy tube"
    assert airway_device_action.action == "Exchange"
    diagnostic = record.procedures_performed.diagnostic_bronchoscopy
    assert diagnostic is not None
    assert diagnostic.performed is True

    findings = (diagnostic.inspection_findings or "").lower()
    abnormalities = diagnostic.airway_abnormalities or []
    assert "secret" in findings or "Secretions" in abnormalities

    assert "31615" in result.cpt_codes
    assert "31622" in result.cpt_codes
