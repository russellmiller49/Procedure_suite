from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.application.registry_service import RegistryService
from app.registry.deterministic_extractors import extract_linear_ebus
from app.registry.postprocess import (
    reconcile_ebus_inspected_only_stations,
    reconcile_ebus_sampling_from_narrative,
)
from app.registry.schema import RegistryRecord
from app.registry.schema import NodeInteraction


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
    path_b_result: _StubPathwayResult = field(
        default_factory=lambda: _StubPathwayResult(source="ml_classification")
    )
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


def _extract_record_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str) -> RegistryRecord:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=MagicMock(),
        parallel_orchestrator=_StubParallelOrchestrator(),
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)
    record, _warnings, _meta = service.extract_record(note_text)
    return record


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=MagicMock(),
        parallel_orchestrator=_StubParallelOrchestrator(),
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)
    return service.extract_fields(note_text)


def _march_2026_notes_dir() -> Path:
    return Path(__file__).resolve().parents[2].parent / "proc_suite_notes" / "new_synthetic_notes_3_5_26"


def _load_march_2026_note(*, batch: str, note_name: str) -> str:
    note_path = _march_2026_notes_dir() / batch / f"{note_name}.txt"
    if not note_path.is_file():
        raise FileNotFoundError(note_path)
    return note_path.read_text(encoding="utf-8")


def test_routine_trach_exchange_does_not_promote_established_route(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "TRACH CHANGE NOTE\n"
        "Reason: Routine quarterly tracheostomy tube exchange; non-healing granulation tissue at stoma.\n"
        "Current tube: Bivona 7.0 TTS cuffed, in place 3 months.\n"
        "Procedure: Cuff deflated; tube removed. New Bivona 7.0 TTS tube advanced over guide. "
        "Position confirmed clinically.\n"
        "Hemostasis achieved.\n"
    )

    record = _extract_record_parallel_ner(monkeypatch, note_text)
    assert record.established_tracheostomy_route is not True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31615" not in codes


def test_guardrails_clear_false_blvr_on_routine_trach_exchange() -> None:
    note_text = (
        "Reason: Routine quarterly tracheostomy tube exchange; non-healing granulation tissue at stoma.\n"
        "Current tube: Bivona 7.0 TTS cuffed, in place 3 months.\n"
        "Procedure: Cuff deflated; tube removed. New Bivona 7.0 TTS tube advanced over guide.\n"
    )
    record = RegistryRecord(
        procedures_performed={
            "blvr": {
                "performed": True,
                "procedure_type": "Valve placement",
                "number_of_valves": 2,
            }
        }
    )

    updated = ClinicalGuardrails().apply_record_guardrails(note_text, record).record
    assert updated is not None
    assert updated.procedures_performed is not None
    blvr = updated.procedures_performed.blvr
    assert blvr is None or blvr.performed is not True


def test_montgomery_t_tube_insertion_routes_to_airway_stent(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "MONTGOMERY T-TUBE INSERTION\n"
        "PROCEDURE: Rigid bronchoscopy + Nd:YAG laser + balloon dilation + Montgomery T-tube insertion\n"
        "Rigid bronchoscopy confirmed upper tracheal stenosis. Nd:YAG laser web radial incisions. "
        "Serial balloon dilation to 13 mm. Stoma created at ring 3-4. "
        "T-tube (13 x 70 x 30 mm) folded and introduced via rigid barrel; sidearm exteriorized through stoma. "
        "Position confirmed on flexible bronchoscopy.\n"
    )

    record = _extract_record_parallel_ner(monkeypatch, note_text)
    assert record.procedures_performed is not None
    stent = record.procedures_performed.airway_stent
    assert stent is not None
    assert stent.performed is True
    assert stent.action == "Placement"
    assert stent.stent_brand == "Montgomery"
    assert stent.stent_type == "Other"
    assert stent.location == "Trachea"

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31631" in codes


def test_montgomery_t_tube_exchange_routes_to_airway_device_action(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "MONTGOMERY T-TUBE MANAGEMENT - TUBE EXCHANGE\n"
        "New T-tube confirmed at bedside. Rigid bronchoscope and laser on standby.\n"
        "Rigid bronchoscope introduced through existing stoma. T-tube identified.\n"
        "Old T-tube removed via rigid barrel after folding with T-tube forceps.\n"
        "New T-tube folded and inserted via rigid barrel; repositioned identically; sidearm exteriorized. "
        "Position confirmed.\n"
    )

    record = _extract_record_parallel_ner(monkeypatch, note_text)
    assert record.procedures_performed is not None
    airway_device_action = getattr(record.procedures_performed, "airway_device_action", None)
    assert airway_device_action is not None
    assert airway_device_action.performed is True
    assert airway_device_action.device_type == "Montgomery T-tube"
    assert airway_device_action.action == "Exchange"
    assert airway_device_action.location == "Trachea"

    stent = record.procedures_performed.airway_stent
    assert stent is None or stent.performed is not True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31638" not in codes
    assert "31641" not in codes


def test_deferred_covered_stent_discussion_does_not_promote_stent(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "Flexible bronchoscopy with BAL and endobronchial biopsies.\n"
        "Left anastomotic dehiscence discussed emergently with transplant surgery.\n"
        "Decision: conservative management initially. Covered stent evaluated - deferred.\n"
        "Plan: surgical revision discussed.\n"
    )

    record = _extract_record_parallel_ner(monkeypatch, note_text)
    procedures = record.procedures_performed
    assert procedures is not None
    assert procedures.airway_stent is None or procedures.airway_stent.performed is not True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31631" not in codes
    assert "31636" not in codes
    assert "31638" not in codes


def test_real_note_measurement_lines_do_not_cancel_sampled_ebus_stations() -> None:
    note_text = (
        "The linear EBUS scope was then introduced. We surveyed stations 4R, 7, and 10R.\n"
        "Station 7 measured 1.8 cm. Station 4R measured 1.4 cm.\n"
        "TBNA was performed at Station 7 x3 passes, and Station 4R x3 passes using a 22G needle.\n"
    )
    record = RegistryRecord(
        procedures_performed={
            "linear_ebus": {
                "performed": True,
                    "stations_sampled": ["4R", "7"],
                    "node_events": [
                        {"station": "10R", "action": "inspected_only", "evidence_quote": "Surveyed 10R."},
                        {"station": "7", "action": "inspected_only", "evidence_quote": "Station 7 measured 1.8 cm."},
                        {"station": "4R", "action": "inspected_only", "evidence_quote": "Station 4R measured 1.4 cm."},
                    ],
                }
            }
        )

    reconcile_ebus_sampling_from_narrative(record, note_text)
    reconcile_ebus_inspected_only_stations(record, note_text)

    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"4R", "7"}

    actions = {event.station: event.action for event in linear.node_events or [] if event.station}
    assert actions.get("4R") == "needle_aspiration"
    assert actions.get("7") == "needle_aspiration"
    assert actions.get("10R") == "inspected_only"


def test_real_note_compact_ebus_pass_list_derives_three_sampled_stations(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "Procedure:\n"
        "Electromagnetic navigational bronchoscopy, radial EBUS, fluoroscopy, TBNA and forceps biopsy of RML target, "
        "followed by EBUS-TBNA 4R/7/11R.\n"
        "Sampling:\n"
        "RML TBNA x3\n"
        "RML forceps x6\n"
        "4R x5 passes\n"
        "7 x3 passes\n"
        "11R x4 passes\n"
    )

    extracted = extract_linear_ebus(note_text)
    assert set(extracted.get("linear_ebus", {}).get("stations_sampled") or []) == {"4R", "7", "11R"}

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"4R", "7", "11R"}
    assert all(event.action != "forceps_biopsy" for event in linear.node_events or [])

    assert "31653" in result.cpt_codes


def test_real_note_minimal_heading_ebus_pass_list_keeps_three_sampled_stations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_1", note_name="note_009")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    extracted = extract_linear_ebus(note_text)
    assert set(extracted.get("linear_ebus", {}).get("stations_sampled") or []) == {"4R", "7", "10R"}

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"4R", "7", "10R"}

    node_map = {event.station: event for event in linear.node_events or [] if event.station}
    assert set(node_map) == {"4R", "7", "10R"}
    assert node_map["4R"].action == "needle_aspiration"
    assert node_map["7"].action == "needle_aspiration"
    assert node_map["10R"].action == "needle_aspiration"
    assert node_map["4R"].passes == 5
    assert node_map["7"].passes == 5
    assert node_map["10R"].passes == 3

    assert "31653" in result.cpt_codes
    assert "31652" not in result.cpt_codes


def test_real_note_all_three_station_ebus_tbna_keeps_station_7_and_31653(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_2", note_name="note_033")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    extracted = extract_linear_ebus(note_text)
    assert set(extracted.get("linear_ebus", {}).get("stations_sampled") or []) == {"4R", "4L", "7"}

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"4R", "4L", "7"}

    node_map = {event.station: event for event in linear.node_events or [] if event.station}
    assert set(node_map) == {"4R", "4L", "7"}
    assert all(event.station is not None for event in linear.node_events or [])
    assert all(event.action == "needle_aspiration" for event in node_map.values())
    assert all(event.passes == 3 for event in node_map.values())

    assert "31653" in result.cpt_codes
    assert "31652" not in result.cpt_codes


def test_real_note_keeps_eus_b_separate_from_bronchoscopic_ebus(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "Procedure note:\n"
        "Linear EBUS with EUS-B added for inaccessible station.\n"
        "Findings:\n"
        "Stations 11L, 7, and 4L were sampled bronchoscopically. "
        "EUS-B was then used to sample station 8 because of favorable esophageal window.\n"
        "Sampling order:\n"
        "11L x4 passes\n"
        "7 x4 passes\n"
        "4L x5 passes\n"
        "8 via EUS-B x3 passes\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record
    assert record.procedures_performed is not None

    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"11L", "7", "4L"}
    assert {event.station for event in linear.node_events or [] if event.station} == {"11L", "7", "4L"}

    eus_b = record.procedures_performed.eus_b
    assert eus_b is not None
    assert eus_b.performed is True
    assert eus_b.passes == 3

    assert "31653" in result.cpt_codes
    assert "43238" in result.cpt_codes
