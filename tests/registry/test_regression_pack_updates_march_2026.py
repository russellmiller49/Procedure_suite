from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.application.registry_service import RegistryService
from app.registry.deterministic_extractors import (
    classify_stent_action,
    extract_airway_dilation,
    extract_chest_tube,
    extract_demographics,
    extract_endobronchial_biopsy,
    extract_ipc,
    extract_therapeutic_aspiration,
    extract_airway_stent,
    is_negated,
    run_deterministic_extractors,
)
from app.registry.evidence.verifier import verify_evidence_integrity
from app.registry.postprocess import (
    enrich_ebus_node_event_outcomes,
    enrich_medical_thoracoscopy_biopsies_taken,
    extract_rose_sentence,
    parse_rose_outcomes,
    populate_ebus_node_events_fallback,
    sanitize_ebus_events,
)
from app.registry.schema import RegistryRecord


def _fixture(note_id: str) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    return (repo_root / "regression_pack" / "fixtures" / f"note_{note_id}.txt").read_text(encoding="utf-8")


def test_nonstation_ebus_target_captured_and_31652_derives() -> None:
    note_text = _fixture("138")
    record = RegistryRecord.model_validate({"procedures_performed": {"linear_ebus": {"performed": True}}})

    warnings = populate_ebus_node_events_fallback(record, note_text)
    warnings.extend(sanitize_ebus_events(record, note_text))

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear is not None
    assert linear.stations_sampled in (None, [])
    assert isinstance(linear.targets_sampled, list) and linear.targets_sampled
    assert any("pulmonary artery mass" in str(t).lower() for t in linear.targets_sampled)
    assert linear.node_events
    assert linear.node_events[0].station is None
    assert "pulmonary artery mass" in str(linear.node_events[0].target_text or "").lower()
    assert any("EBUS_NONSTATION_TARGET_CAPTURED" in w for w in warnings)

    codes, _rationales, _code_warnings = derive_all_codes_with_meta(record)
    assert "31652" in codes


def test_rose_sentence_capture_and_multi_station_mapping() -> None:
    sentence = (
        "ROSE showed non-diagnostic tissue in the 4L and 4R lymph nodes and "
        "benign lymphocytes in station 7 lymph node."
    )
    captured = extract_rose_sentence(f"Header. {sentence} Next.")
    assert captured == sentence

    parsed = parse_rose_outcomes(sentence)
    assert parsed.get("4L") == "nondiagnostic"
    assert parsed.get("4R") == "nondiagnostic"
    assert parsed.get("7") == "benign"


def test_rose_enrichment_replaces_helper_verb_result() -> None:
    note_text = (
        "Sampling by TBNA was performed at station 4L. "
        "ROSE did not show evidence of malignancy in station 4L."
    )
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "4L",
                            "action": "needle_aspiration",
                            "rose_result": "did",
                            "evidence_quote": "TBNA at 4L",
                        }
                    ],
                }
            }
        }
    )

    enrich_ebus_node_event_outcomes(record, note_text)
    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear is not None and linear.node_events
    event = linear.node_events[0]
    assert event.outcome == "benign"
    assert event.rose_result == "benign"


def test_stent_action_classifier_gates_preexisting_context_and_exchange() -> None:
    note_193 = _fixture("193")
    classified_193 = classify_stent_action(note_193)
    stent_193 = extract_airway_stent(note_193).get("airway_stent", {})
    assert classified_193.get("preexisting_stent") is False
    assert stent_193.get("action") == "Placement"
    assert stent_193.get("action_type") == "placement"
    assert "15x12x12" in str(stent_193.get("device_size", "")).replace(" ", "").lower()

    note_257 = _fixture("257")
    classified_257 = classify_stent_action(note_257)
    stent_257 = extract_airway_stent(note_257).get("airway_stent", {})
    assert classified_257.get("preexisting_stent") is True
    assert stent_257.get("action") == "Revision/Repositioning"
    assert stent_257.get("action_type") == "revision"
    assert stent_257.get("airway_stent_removal") is True
    assert "12x40" in str(stent_257.get("device_size", "")).replace(" ", "").lower()


def test_ipc_removal_fallback_from_header_and_code_32552() -> None:
    note_text = _fixture("036")
    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord.model_validate(seed)
    record, _warnings = verify_evidence_integrity(record, note_text)

    ipc = record.pleural_procedures.ipc if record.pleural_procedures else None
    assert ipc is not None
    assert ipc.performed is True
    assert ipc.action == "Removal"

    codes, _rationales, _code_warnings = derive_all_codes_with_meta(record)
    assert "32552" in codes


def test_therapeutic_aspiration_boilerplate_filter_blocks_note_125() -> None:
    note_text = _fixture("125")
    result = extract_therapeutic_aspiration(note_text)
    assert result == {}


def test_sentence_scoped_endobronchial_biopsy_location_note_104() -> None:
    note_text = _fixture("104")
    result = extract_endobronchial_biopsy(note_text)
    locations = result.get("endobronchial_biopsy", {}).get("locations")
    assert locations == ["RML Carina (RC2)"]


def test_age_guardrail_prefers_year_old_over_french_size_tokens() -> None:
    note_text = (
        "INDICATION: 65 year old-year-old female with pleural effusion. "
        "A 12F pigtail catheter was then inserted."
    )
    demo = extract_demographics(note_text)
    assert demo.get("patient_age") == 65


def test_thoracoscopy_biopsy_note_145_upgrades_to_32604_and_keeps_ipc_code() -> None:
    note_text = _fixture("145")
    ipc_data = extract_ipc(note_text)
    record_dict = {
        "pleural_procedures": {
            "medical_thoracoscopy": {"performed": True},
        }
    }
    if ipc_data.get("ipc"):
        record_dict["pleural_procedures"]["ipc"] = ipc_data["ipc"]  # type: ignore[index]

    record = RegistryRecord.model_validate(record_dict)
    enrich_medical_thoracoscopy_biopsies_taken(record, note_text)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32604" in codes
    assert "32550" in codes


def test_note_158_does_not_force_endobronchial_biopsy_from_header_wording() -> None:
    note_text = _fixture("158")
    ebbx = extract_endobronchial_biopsy(note_text)
    assert ebbx == {}


def test_note_205_captures_endobronchial_biopsy_and_fluoro_chest_tube_guidance() -> None:
    note_text = _fixture("205")
    ebbx = extract_endobronchial_biopsy(note_text)
    chest_tube = extract_chest_tube(note_text)

    assert ebbx.get("endobronchial_biopsy", {}).get("performed") is True
    assert chest_tube.get("chest_tube", {}).get("guidance") == "Fluoroscopy"

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord.model_validate(seed)
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31625" in codes


def test_note_231_station_7_not_dropped_from_station_list_syntax() -> None:
    note_text = _fixture("231")
    record = RegistryRecord.model_validate({"procedures_performed": {"linear_ebus": {"performed": True}}})
    warnings = populate_ebus_node_events_fallback(record, note_text)
    warnings.extend(sanitize_ebus_events(record, note_text))

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    stations = {str(ev.station).upper() for ev in (linear.node_events or []) if ev.station}
    assert "7" in stations
    assert not any("AUTO_DROPPED_EBUS_STATION_NOT_IN_TEXT: 7" in w for w in warnings)


def test_note_257_airway_dilation_uses_largest_documented_balloon_mm() -> None:
    note_text = _fixture("257")
    dilation = extract_airway_dilation(note_text).get("airway_dilation", {})
    assert dilation.get("performed") is True
    assert dilation.get("balloon_diameter_mm") == 15.0


def test_negation_scope_is_sentence_local_for_stricture_detection() -> None:
    text = (
        "Bronchial mucosa and anatomy were normal, with no endobronchial lesions and no secretions noted. "
        "A stricture was identified in the right bronchus intermedius."
    )
    sec_match = next(m for m in re.finditer(r"(?i)secretions", text))
    str_match = next(m for m in re.finditer(r"(?i)stricture", text))
    assert is_negated(sec_match.start(), sec_match.end(), text) is True
    assert is_negated(str_match.start(), str_match.end(), text) is False


def test_note_138_stricture_maps_to_airway_stenosis(monkeypatch) -> None:
    class _StubParallelPathwayOrchestrator:
        def __init__(self, seed_record: dict[str, object]) -> None:
            self._seed_record = seed_record

        def process(self, note_text: str, ml_predictor: object | None = None) -> SimpleNamespace:  # noqa: ARG002
            record = RegistryRecord.model_validate(self._seed_record)
            path_a = SimpleNamespace(
                source="ner_rules",
                codes=[],
                confidences={},
                rationales={},
                processing_time_ms=0.0,
                details={"record": record, "ner_entities": [], "ner_entity_count": 0, "stations_sampled_count": 0},
            )
            path_b = SimpleNamespace(
                source="ml_classification",
                codes=[],
                confidences={},
                rationales={},
                processing_time_ms=0.0,
                details={},
            )
            return SimpleNamespace(
                final_codes=[],
                final_confidences={},
                path_a_result=path_a,
                path_b_result=path_b,
                needs_review=False,
                review_reasons=[],
                explanations={},
                total_time_ms=0.0,
            )

        def _build_ner_evidence(self, ner_entities: object | None) -> dict[str, list[object]]:  # noqa: ARG002
            return {}

    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    orchestrator = _StubParallelPathwayOrchestrator(
        seed_record={"procedures_performed": {"diagnostic_bronchoscopy": {"performed": True}, "linear_ebus": {"performed": True}}}
    )
    service = RegistryService(parallel_orchestrator=orchestrator)
    service._get_registry_ml_predictor = lambda: None  # type: ignore[method-assign]

    result = service.extract_fields(_fixture("138"))
    proc = result.record.procedures_performed.diagnostic_bronchoscopy if result.record.procedures_performed else None
    assert proc is not None
    assert "Stenosis" in (proc.airway_abnormalities or [])
