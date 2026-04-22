from __future__ import annotations

import pytest

from app.registry.application.registry_service import RegistryService
from app.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes_with_meta,
    derive_units_for_codes,
)
from app.registry.postprocess import enrich_ebus_node_event_sampling_details
from app.registry.deterministic_extractors import run_deterministic_extractors
from app.registry.schema import RegistryRecord
from app.registry.self_correction.keyword_guard import apply_required_overrides


def test_note_281_elastography_does_not_force_tblb_and_derives_elastography_codes() -> None:
    note_text = """
    PROCEDURE:
    Linear EBUS was performed with sampling at stations 11L, 4L, and 4R.
    76981 Ultrasound Elastography, Parenchyma of Organ
    76982 Ultrasound Elastography, First target lesion
    76983 Ultrasound Elastography, Each additional target lesion

    PROCEDURE IN DETAIL:
    Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness.
    Site 1: The 11L lymph node was sampled. 4 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
    Site 2: The 4L lymph node was sampled. 5 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 1 elastographic pattern.
    Site 3: The 4R lymph node was sampled. 6 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 1 elastographic pattern.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    record, _override_warnings = apply_required_overrides(note_text, record)
    assert record.procedures_performed
    assert record.procedures_performed.linear_ebus
    assert record.procedures_performed.linear_ebus.elastography_used is True

    # "EBUS guided transbronchial biopsies" refers to nodal TBNA and must not force
    # a parenchymal transbronchial lung biopsy flag/code (31628).
    tblb = getattr(record.procedures_performed, "transbronchial_biopsy", None)
    assert tblb is None or tblb.performed is not True

    record_data = record.model_dump()
    record_data.setdefault("evidence", {})["header_code_hints"] = [{"text": "76981", "start": 0, "end": 5}]
    record = RegistryRecord(**record_data)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31628" not in codes
    assert "31653" in codes
    assert "76982" in codes
    assert "76983" in codes
    assert "76981" not in codes

    units = derive_units_for_codes(record, codes)
    assert units.get("76983") == 2


def test_enrich_ebus_sampling_details_backfills_node_events_for_site_blocks() -> None:
    note_text = """
    PROCEDURE IN DETAIL:
    Endobronchial ultrasound (EBUS) elastography was performed.
    Site 1: The 11Rs lymph node was sampled.
    4 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 2 elastographic pattern.
    """

    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [],
                    "stations_sampled": [],
                }
            }
        }
    )

    warnings = enrich_ebus_node_event_sampling_details(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.node_events is not None
    assert len(linear.node_events) == 1
    assert linear.node_events[0].station == "11RS"
    assert linear.node_events[0].action == "needle_aspiration"
    assert linear.elastography_used is True
    assert linear.stations_sampled == ["11RS"]
    assert any("AUTO_EBUS_GRANULARITY: added node_events" in w for w in warnings)

    codes, _rationales, derivation_warnings = derive_all_codes_with_meta(record)
    assert "76982" in codes
    assert not any("Suppressed 76982/76983" in w for w in derivation_warnings)


def test_extract_record_inspection_only_ebus_elastography_does_not_warn_missing_stations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    monkeypatch.setenv("OPENAI_OFFLINE", "1")
    monkeypatch.setenv("GEMINI_OFFLINE", "1")

    note_text = """
    INSTRUMENT:
    Linear EBUS

    EBUS-Findings
    Indications: Diagnostic
    Technique:
    All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
    Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
    4L (lower paratracheal) node
    7 (subcarinal) node
    No biopsies taken based upon ultrasound appearance
    Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
    Lymph Nodes Evaluated:
    Site 1: The 7 (subcarinal) node was < 10 mm on CT. The site was not sampled: Sampling this lymph node was not clinically indicated.
    Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
    The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
    """

    record, warnings, _meta = RegistryService().extract_record(note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear is not None
    assert linear.performed is True
    assert linear.elastography_used is True
    assert not (linear.stations_sampled or [])
    assert linear.node_events is not None
    assert all(event.action == "inspected_only" for event in linear.node_events)
    assert not any("procedures_performed.linear_ebus.performed=true but stations_sampled is empty/missing" in w for w in warnings)
