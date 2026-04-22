from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService


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
        from app.registry.schema import RegistryRecord

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


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=MagicMock(),
        parallel_orchestrator=_StubParallelOrchestrator(),
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)
    return service.extract_fields(note_text)


def test_real_note_blue_rhino_pdt_routes_to_percutaneous_trach(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PDT PROCEDURE CHECKLIST AND NOTE\n"
        "PROCEDURE: Ciaglia Blue Rhino single-step PDT. Ring 2-3 interspace. "
        "Bronchoscopic guidance throughout. Guidewire placed. Blue Rhino dilator advanced; "
        "trachea dilated to 8.0 mm. Shiley 8.0 cuffed tube placed and secured.\n"
        "POST-PROCEDURE CHECKLIST: Bronchoscopy through trach: tip 4 cm above carina.\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.established_tracheostomy_route is not True
    assert record.procedures_performed is not None
    pt = record.procedures_performed.percutaneous_tracheostomy
    assert pt is not None
    assert pt.performed is True
    assert "31600" in result.cpt_codes
    assert "31615" not in result.cpt_codes


def test_real_note_mature_trach_exchange_confirmation_only_does_not_keep_established_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = (
        "TRACHEOSTOMY EXCHANGE NOTE\n"
        "INDICATION: Mature tracheostomy (14 days post-PDT); first trach tube exchange for smaller cuffless tube.\n"
        "PROCEDURE: Tracheostomy tube change, mature tract.\n"
        "Old tube removed. New cuffless Shiley advanced through mature stoma tract. "
        "Position confirmed: bronchoscope introduced through 6.0 cuffless tube; tip 4.5 cm above carina; no false passage.\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.procedures_performed is not None
    airway_device_action = getattr(record.procedures_performed, "airway_device_action", None)
    assert airway_device_action is not None
    assert airway_device_action.performed is True
    assert airway_device_action.device_type == "Tracheostomy tube"
    assert airway_device_action.action == "Exchange"

    assert record.established_tracheostomy_route is not True
    assert "31615" not in result.cpt_codes
    assert "31622" not in result.cpt_codes
    assert "31600" not in result.cpt_codes


def test_real_note_t_tube_sidearm_surveillance_is_not_stent_removal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = (
        "PROCEDURE NOTE\n"
        "PRE-PROCEDURE DIAGNOSIS: Montgomery T-tube in situ (placed 4 months prior).\n"
        "PROCEDURE: Flexible bronchoscopy through T-tube sidearm; mechanical clearance (CPT 31622).\n"
        "COMPLICATIONS: acute obstruction from mucus impaction. No intubation required.\n"
        "T-tube sidearm plug removed: immediate partial relief of symptoms. Flexible bronchoscope introduced via sidearm. "
        "Tube position intact and satisfactory. Thick mucoid material cleared with suction and forceps.\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.diagnostic_bronchoscopy is not None
    assert record.procedures_performed.diagnostic_bronchoscopy.performed is True
    assert record.procedures_performed.airway_stent is None
    assert record.procedures_performed.intubation is None
    assert "31622" in result.cpt_codes
    assert "31638" not in result.cpt_codes
    assert "31500" not in result.cpt_codes


def test_real_note_ebus_pass_counts_do_not_invent_station_5(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "Bronchoscopy with linear EBUS staging.\n"
        "EBUS-TBNA sampling:\n"
        "Station 4R: 5 passes with 22G needle\n"
        "Station 7: 6 passes with 22G needle\n"
        "Station 11L: 3 passes with 22G needle\n"
        "SPECIMENS:\n"
        "\"4R TBNA\" (passes 1-5)\n"
        "\"7 TBNA\" (passes 1-6)\n"
        "\"11L TBNA\" (passes 1-3)\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.procedures_performed is not None
    linear = record.procedures_performed.linear_ebus
    assert linear is not None
    assert set(linear.stations_sampled or []) == {"4R", "7", "11L"}
    assert {event.station for event in linear.node_events or [] if event.station} == {"4R", "7", "11L"}


def test_real_note_bal_and_navigation_targets_trim_non_anatomic_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = (
        "POST-PROCEDURE DIAGNOSIS Same, status post computer-assisted navigational bronchoscopy to LUL peripheral target, "
        "radial EBUS, transbronchial sampling, BAL, and linear EBUS staging.\n"
        "PROCEDURES PERFORMED\n"
        "1. Flexible bronchoscopy with complete airway inspection\n"
        "2. Computer-assisted navigational bronchoscopy to LUL peripheral target\n"
        "3. Radial EBUS confirmation\n"
        "4. Cone-beam CT spin with confirmation of tool-in-lesion\n"
        "5. Transbronchial needle aspiration, forceps biopsy, transbronchial biopsy, and cryobiopsy of target lesion\n"
        "6. BAL, lingula\n"
        "7. Linear EBUS-TBNA of stations 4L, 7, and 11L\n"
        "FINDINGS: Airway inspection normal. BAL performed in right middle lobe with 150 mL instilled, 60 mL return.\n"
        "The peripheral target was reached via an apicoposterior route based on pre-procedure planning.\n"
    )

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    record = result.record

    assert record.procedures_performed is not None
    bal = record.procedures_performed.bal
    assert bal is not None
    assert bal.location == "right middle lobe"

    ptbna = record.procedures_performed.peripheral_tbna
    assert ptbna is not None
    assert ptbna.targets_sampled == ["LUL"]

    tbbx = record.procedures_performed.transbronchial_biopsy
    assert tbbx is None or tbbx.locations in (None, ["LUL"])

    assert record.granular_data is not None
    assert record.granular_data.navigation_targets is not None
    assert [target.target_location_text for target in record.granular_data.navigation_targets] == ["LUL"]
