from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from modules.registry.application.registry_service import RegistryService
from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.processing.cao_interventions_detail import extract_cao_interventions_detail
from modules.registry.schema import RegistryRecord


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
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")

    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=MagicMock(),
        parallel_orchestrator=_StubParallelOrchestrator(),
    )
    monkeypatch.setattr(service, "_get_registry_ml_predictor", lambda: None)
    record, _warnings, _meta = service.extract_record(note_text)
    return record


def test_note_008_tracheal_puncture_derives_31612_and_has_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PROCEDURE:\n"
        "31612 tracheal puncture\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "A 14 gauge angiocath was used to puncture the anterior tracheal wall more superiorly.\n"
    )
    record = _extract_record_parallel_ner(monkeypatch, note_text)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31612" in codes
    assert "31600" not in codes

    assert record.evidence.get("procedures_performed.percutaneous_tracheostomy.performed")


def test_note_011_subsequent_aspiration_31646_overrides_31645(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PROCEDURE:\n"
        "31646 Therapeutic aspiration subsequent episodes\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "Successful therapeutic aspiration was performed to clean out the Trachea from mucus.\n"
    )
    record = _extract_record_parallel_ner(monkeypatch, note_text)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31646" in codes
    assert "31645" not in codes

    assert record.evidence.get("procedures_performed.therapeutic_aspiration.is_subsequent")


def test_note_011_balloon_occlusion_derives_31634_without_chartis(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PROCEDURE IN DETAIL:\n"
        "New Uniblocker (5Fr) balloon occlusion was performed at the Left Carina (LC2).\n"
        "The endobronchial blocker balloon was left inflated in the LUL.\n"
    )
    record = _extract_record_parallel_ner(monkeypatch, note_text)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31634" in codes
    assert "31647" not in codes

    assert record.evidence.get("procedures_performed.blvr.performed")


def test_note_007_valve_removal_triggers_31635(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PROCEDURE IN DETAIL:\n"
        "Size 7 spiration valve was placed but noted to be too large for the airway (RB10). This was subsequently removed.\n"
        "Then size 6 spiration valve was placed in RB10, noted to be in poor position, this was removed again and replaced.\n"
    )
    record = _extract_record_parallel_ner(monkeypatch, note_text)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31635" in codes

    assert record.evidence.get("procedures_performed.foreign_body_removal.performed")


def test_note_010_established_tracheostomy_route_derives_31615(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = "Pharynx: Not assessed due to bronchoscopy introduction through tracheostomy tube.\n"
    record = _extract_record_parallel_ner(monkeypatch, note_text)

    assert record.established_tracheostomy_route is True
    assert record.evidence.get("established_tracheostomy_route")

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31615" in codes


def test_note_007_pleurodesis_referral_sentence_does_not_code_32560() -> None:
    note_text = "See Dr. Thistlethwaite's note for VATS and pleurodesis.\n"
    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record
    assert updated is not None

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "32560" not in codes
    assert any("Pleurodesis mentioned only in attributed" in w for w in outcome.warnings)


def test_note_018_distance_to_carina_line_does_not_create_cao_location_carina() -> None:
    note_text = (
        "Surgical Planning Measurements:\n"
        "Distance of bottom of stenosis to carina 90 mm\n"
        "Prior to treatment, affected airway was note to be 50% patent.\n"
        "\n"
        "Endobronchial obstruction at Subglottic was treated with the following modalities:\n"
        "Balloon dilation was performed at Trachea (Proximal 1/3).\n"
    )
    details = extract_cao_interventions_detail(note_text)
    assert details
    assert "Carina" not in {d.get("location") for d in details}


def test_note_010_header_cpt_stenosis_does_not_leak_into_airway_abnormalities(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PROCEDURE:\n"
        "31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)\n"
        "\n"
        "INSTRUMENT:\n"
        "Flexible bronchoscope\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "Initial Airway Inspection Findings:\n"
        "Left Lung Proximal Airways: No evidence of mass, lesions, bleeding or other endobronchial pathology.\n"
    )
    record = _extract_record_parallel_ner(monkeypatch, note_text)

    assert record.procedures_performed is not None
    proc = record.procedures_performed.diagnostic_bronchoscopy
    assert proc is not None and proc.performed is True
    abnormalities = proc.airway_abnormalities if proc else None
    assert not abnormalities or "Stenosis" not in set(abnormalities)
