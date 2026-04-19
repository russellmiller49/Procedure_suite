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


def test_real_note_blank_separated_ebus_specimens_keep_all_three_stations_and_tbna_specimens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = (
        "PRE-PROCEDURE DIAGNOSIS: Mediastinal adenopathy; pulmonary nodule (R91.1, R59.0)\n"
        "POST-PROCEDURE DIAGNOSIS: Same\n"
        "PROCEDURES: Bronchoscopy with BAL; Linear EBUS-TBNA of mediastinal/hilar lymph nodes "
        "(include codes: CPT 31624, 31652)\n"
        "ANESTHESIA: General anesthesia with LMA\n"
        "ESTIMATED BLOOD LOSS: Minimal\n"
        "COMPLICATIONS: None\n"
        "\n"
        "INDICATION: [PATIENT] is a 64-year-old male with right upper lobe pulmonary nodule and "
        "PET-avid mediastinal nodes for diagnosis and staging.\n"
        "\n"
        "FINDINGS:\n"
        "\n"
        "Trachea and main carina normal.\n"
        "\n"
        "Mild bronchitic secretions in right lower lobe; no endobronchial mass.\n"
        "\n"
        "EBUS: Enlarged station 4R and station 7 with heterogeneous echotexture; "
        "station 11L small but visualized.\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "After informed consent and time-out, flexible bronchoscopy was performed through the LMA. "
        "Airway inspection was completed to segmental level bilaterally. BAL was performed in the "
        "right upper lobe posterior segment with 120 mL instilled, 48 mL returned, mildly turbid. "
        "The EBUS bronchoscope was then introduced. Doppler was used prior to each pass.\n"
        "\n"
        "EBUS-TBNA sampling:\n"
        "\n"
        "Station 4R: 5 passes with 22G needle\n"
        "\n"
        "Station 7: 6 passes with 22G needle\n"
        "\n"
        "Station 11L: 3 passes with 22G needle\n"
        "\n"
        "SPECIMENS:\n"
        "\n"
        "“4R TBNA” (passes 1-5)\n"
        "\n"
        "“7 TBNA” (passes 1-6)\n"
        "\n"
        "“11L TBNA” (passes 1-3)\n"
        "\n"
        "“RUL BAL”\n"
        "\n"
        "IMPRESSION/PLAN:\n"
        "\n"
        "No endobronchial lesion.\n"
        "\n"
        "Await cytology/pathology and flow as ordered.\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)

    record = result.record
    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert linear.stations_sampled == ["4R", "7", "11L"]

    node_map = {event.station: event for event in linear.node_events or [] if event.station}
    assert set(node_map) == {"4R", "7", "11L"}
    assert all(event.action == "needle_aspiration" for event in node_map.values())
    assert node_map["4R"].passes == 5
    assert node_map["7"].passes == 6
    assert node_map["11L"].passes == 3

    assert record.specimens is not None
    specimens = record.specimens.specimens_collected
    assert specimens is not None
    assert [(spec.type, spec.location) for spec in specimens] == [
        ("TBNA", "4R"),
        ("TBNA", "7"),
        ("TBNA", "11L"),
        ("BAL", "RUL"),
    ]

    assert "31653" in result.cpt_codes
    assert "31652" not in result.cpt_codes
    assert "31624" in result.cpt_codes


def test_real_note_brushings_and_bal_locations_survive_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "Indication: Hemoptysis and left upper lobe mass on CT in a 58-year-old female.\n"
        "\n"
        "Procedure: Bronchoscopy, endobronchial biopsy, brushings, BAL, linear EBUS-TBNA.\n"
        "\n"
        "Sedation: Moderate sedation (midazolam and fentanyl) with topical lidocaine.\n"
        "\n"
        "Narrative:\n"
        "\n"
        "Consent obtained and time-out performed. Flexible bronchoscopy was advanced via oral bite block. "
        "Vocal cords normal. There was an exophytic lesion at the left upper lobe apicoposterior segment "
        "entrance with contact bleeding. Suction and cold saline were used for hemostasis.\n"
        "\n"
        "Interventions:\n"
        "\n"
        "Endobronchial biopsies x6 from LUL lesion.\n"
        "\n"
        "Cytology brush x2 from LUL lesion.\n"
        "\n"
        "BAL in lingula with 100 mL instilled, 35 mL return, blood-tinged initially then clearing.\n"
        "\n"
        "EBUS portion:\n"
        "EBUS scope introduced. Doppler confirmed no intervening vessels. Sampling performed in the following order:\n"
        "\n"
        "Station 11L: 4 passes (22G)\n"
        "\n"
        "Station 7: 4 passes (22G)\n"
        "\n"
        "Station 4L: 3 passes (22G)\n"
        "\n"
        "Specimens labeled:\n"
        "\n"
        "“LUL endobronchial bx”\n"
        "\n"
        "“LUL brush”\n"
        "\n"
        "“Lingula BAL”\n"
        "\n"
        "“11L TBNA”\n"
        "\n"
        "“7 TBNA”\n"
        "\n"
        "“4L TBNA”\n"
        "\n"
        "Complications: None. EBL minimal.\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)

    record = result.record
    assert record.procedures_performed is not None

    brushings = record.procedures_performed.brushings
    assert brushings is not None
    assert brushings.performed is True
    assert brushings.locations == ["LUL"]

    bal = record.procedures_performed.bal
    assert bal is not None
    assert bal.performed is True
    assert bal.location == "lingula"
    assert bal.volume_instilled_ml == 100
    assert bal.volume_recovered_ml == 35

    assert {"31623", "31624", "31625", "31653"}.issubset(set(result.cpt_codes or []))


def test_reconciled_three_station_ebus_note_keeps_station_7_sampled_in_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = """
    The convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
    A systematic hilar and mediastinal lymph node survey was carried out.
    Sampling criteria (5mm short axis diameter PET avid) were met in station 11 L, 7, 3P lymph nodes.
    Sampling by transbronchial needle aspiration was performed with the EBUS TBNA 21 gauge needle beginning with the 11 L lymph node, followed by the 7 lymph node, followed by the 3P lymph node.
    A total of at least 5 biopsies were performed in each station.
    ROSE evaluation yielded malignancy at station 7 and 3P.

    Lymph nodes
    3p: 4.0 mm; 4 passes
    4R: <3mm;
    4L: 3mm;
    7: 7.6; 7passes
    11Rs: 4.9 mm;
    11Ri: 3.5 mm;
    11L: 5.4mm; 6of passes
    """.strip()

    result = _extract_fields_parallel_ner(monkeypatch, note_text)

    record = result.record
    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"3P", "7", "11L"}

    node_map = {event.station: event for event in linear.node_events or [] if event.station}
    assert node_map["3P"].action == "needle_aspiration"
    assert node_map["7"].action == "needle_aspiration"
    assert node_map["11L"].action == "needle_aspiration"

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
