"""Independent short-prompt fidelity: no parent-report or case-title enrichment."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.reporting import build_procedure_bundle_from_extraction, compose_structured_report
from app.reporting.normalization.robotic_prompt_fidelity import reconcile_robotic_prompt
from app.reporting.seed_inputs import ReporterSeedInputs, apply_seed_inputs
from ops.tools.eval_reporter_robotic_minimal import (
    check_order,
    check_rendered,
    check_slots,
    observed_order,
)
from proc_schemas.clinical import ProcedureBundle, ProcedureInput

CORPUS = json.loads(
    (Path(__file__).parents[1] / "fixtures/reporting/robotic_ebus_minimal_prompts.json").read_text()
)["cases"]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    for key, value in {
        "PROCSUITE_SKIP_DOTENV": "1",
        "REPORTER_DISABLE_LLM": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "ENABLE_UMLS_LINKER": "false",
    }.items():
        monkeypatch.setenv(key, value)


@pytest.mark.parametrize("row", CORPUS, ids=lambda row: row["id"])
def test_source_reviewed_short_prompt_slots(row):
    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    if row.get("structured_inputs"):
        # Builder dropdown selections travel beside the prompt, never inside it.
        bundle = apply_seed_inputs(
            bundle, ReporterSeedInputs.model_validate(row["structured_inputs"])
        ).bundle
    assert not check_slots(bundle.model_dump(mode="json"), row["expected"])
    rendered = compose_structured_report(bundle, strict=True)
    unsupported_phrases = ["informed consent was obtained", "3-4 passes"]
    if not row.get("structured_inputs"):
        # These appear only when a builder selection explicitly supplies them.
        unsupported_phrases += [
            "ESTIMATED BLOOD LOSS: Minimal",
            "Post-procedure monitoring per protocol",
            "under fluoroscopic guidance",
            "I personally performed and interpreted",
            "COMPLICATIONS: None",
            "registration was used",
            "ANESTHESIA: General",
        ]
    for unsupported in unsupported_phrases:
        assert unsupported not in rendered
    # The report follows the dictated workflow and renders what the bundle holds.
    assert not check_order(rendered, row.get("expected_order"))
    assert not check_rendered(bundle.model_dump(mode="json"), rendered)


def test_sparse_prompt_does_not_borrow_parent_case_counts_or_techniques():
    row = next(r for r in CORPUS if r["id"] == "RB-01-10")
    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    assert not any(
        p.proc_type
        in {
            "transbronchial_lung_biopsy",
            "transbronchial_cryobiopsy",
            "transbronchial_needle_aspiration",
            "ebus_tbna",
        }
        for p in bundle.procedures
    )
    assert "11Ri/7/11L" in bundle.findings_text
    assert "Nodal sampling versus inspection unspecified" in bundle.findings_text
    text = compose_structured_report(bundle, strict=True)
    assert "Peripheral lung biopsy" in text
    assert "ANESTHESIA: Not documented" in text
    assert "without complication" not in text


@pytest.mark.parametrize(
    "text",
    [
        "Planned Ion RUL nodule TBNA and cryobiopsy, not performed.",
        "Indication: ILD. RLL radial EBUS cryobiopsy with balloon prophylaxis.",
    ],
)
def test_other_workflows_not_reconciled(text):
    bundle = ProcedureBundle(patient={}, encounter={}, procedures=[])
    assert reconcile_robotic_prompt(bundle, text) is bundle


def test_explicit_stent_action_is_preserved_but_marker_deployment_is_not_a_stent():
    stent = ProcedureInput(
        proc_type="airway_stent_placement",
        schema_id="airway_stent_placement_v1",
        data={"airway_segment": "RMS"},
    )
    bundle = ProcedureBundle(patient={}, encounter={}, procedures=[stent])
    assert not any(
        p.proc_type == "airway_stent_placement"
        for p in reconcile_robotic_prompt(
            bundle, "Ion RUL nodule biopsy. Gold marker deployed."
        ).procedures
    )
    assert any(
        p.proc_type == "airway_stent_placement"
        for p in reconcile_robotic_prompt(
            bundle, "Ion RUL nodule biopsy. RMS stent placed for obstruction."
        ).procedures
    )


def test_negative_peripheral_sampling_does_not_suppress_positive_nodes():
    bundle = build_procedure_bundle_from_extraction(
        {},
        source_text=(
            "Ion RUL nodule localized. No TBNA or cryobiopsy performed at lung target. "
            "EBUS station 7 TBNA x4."
        ),
    )
    assert not any(
        p.proc_type in {"transbronchial_needle_aspiration", "transbronchial_cryobiopsy"}
        for p in bundle.procedures
    )
    assert any(p.proc_type == "ebus_tbna" for p in bundle.procedures)


def test_target_rose_and_radial_patterns_stay_distinct():
    source = next(r["prompt_text"] for r in CORPUS if r["id"] == "RB-02-01")
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    patterns = [
        p.data["rebus_features"] for p in bundle.procedures if p.proc_type == "radial_ebus_survey"
    ]
    assert patterns == ["Eccentric", "Concentric"]
    assert "RB2 ROSE: atypical nonmalignant" in bundle.findings_text
    assert "LB4 ROSE: malignant" in bundle.findings_text
    for p in bundle.procedures:
        if p.proc_type == "ebus_tbna":
            assert all(not station.get("rose_result") for station in p.data["stations"])


def test_missing_ebus_details_remain_a_review_warning():
    from app.reporting.quality_gate import _omitted_major_family_flags

    source = next(r["prompt_text"] for r in CORPUS if r["id"] == "RB-11-10")
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    flags = _omitted_major_family_flags(source, bundle)
    assert any(
        f["code"] == "EBUS_DETAILS_UNSPECIFIED" and f["severity"] == "warning" for f in flags
    )
    assert not any(f["code"] == "OMITTED_MAJOR_PROCEDURE_FAMILY" for f in flags)


def test_lesion_size_does_not_come_from_cryoprobe_size():
    for case, size in [("RB-09-01", "Target RB3: 3 cm."), ("RB-11-01", "Target LB1/2: 8 mm.")]:
        source = next(r["prompt_text"] for r in CORPUS if r["id"] == case)
        bundle = build_procedure_bundle_from_extraction({}, source_text=source)
        assert size in bundle.findings_text
    source = next(r["prompt_text"] for r in CORPUS if r["id"] == "RB-08-06")
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    assert "Target RB4: 1.1 mm" not in bundle.findings_text


@pytest.mark.parametrize(
    "row", [r for r in CORPUS if "ebus_warning_review" in r], ids=lambda r: r["id"]
)
def test_reviewed_ebus_warnings(row):
    from app.reporting.quality_gate import _omitted_major_family_flags

    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    flags = [
        f
        for f in _omitted_major_family_flags(row["prompt_text"], bundle)
        if f["code"] == "EBUS_DETAILS_UNSPECIFIED"
    ]
    review = row["ebus_warning_review"]
    assert bool(flags) == review["remaining_warning"]
    if flags:
        assert flags[0]["metadata"]["missing_details"] == review["missing_details"]
    assert not check_slots(bundle.model_dump(mode="json"), row["expected"])


def test_anatomical_node_names_preserve_uncertainty_and_source_labels():
    source = next(r["prompt_text"] for r in CORPUS if r["id"] == "RB-02-04")
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    nodes = [s for p in bundle.procedures if p.proc_type == "ebus_tbna" for s in p.data["stations"]]
    assert [s["station_name"] for s in nodes] == ["7"]
    assert "right paratracheal" in bundle.findings_text
    assert "upper/lower" in bundle.findings_text
    assert "sampling details unspecified" not in bundle.findings_text


@pytest.mark.parametrize(
    "nodal",
    [
        "EBUS station 4R looked benign.",
        "EBUS station 4R; lung ROSE showed benign lymphocytes.",
        "EBUS inspection of station 4R without sampling.",
        "EBUS survey of 4R, 7 and 11L without nodal sampling.",
        "EBUS survey of 4R and 7 without nodal biopsies.",
    ],
)
def test_nodal_inspection_and_lung_cytology_do_not_imply_tbna(nodal):
    bundle = build_procedure_bundle_from_extraction(
        {}, source_text="Ion LUL nodule cryobiopsy. " + nodal
    )
    assert not any(p.proc_type == "ebus_tbna" for p in bundle.procedures)


def test_explicit_station_label_takes_precedence_over_named_region():
    bundle = build_procedure_bundle_from_extraction(
        {},
        source_text=(
            "Ion RUL nodule biopsy. EBUS sampled 11L (left hilar) and station 7 (subcarinal)."
        ),
    )
    nodes = [
        s["station_name"]
        for p in bundle.procedures
        if p.proc_type == "ebus_tbna"
        for s in p.data["stations"]
    ]
    assert nodes == ["11L", "7"]


def test_detail_and_header_follow_dictation_order():
    row = next(r for r in CORPUS if r["id"] == "RB-01-01")
    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    rendered = compose_structured_report(bundle, strict=True)
    order = observed_order(rendered)
    assert order["detail_blocks"] == [
        "robotic_navigation",
        "radial_ebus_survey",
        "cbct_cact_fusion",
        "transbronchial_needle_aspiration",
        "transbronchial_lung_biopsy",
        "transbronchial_cryobiopsy",
        "bronchial_brushings",
        "bal",
        "fiducial_marker_placement",
        "ebus_tbna",
    ]
    assert order["header_lines"] == order["detail_blocks"]
    assert [p.sequence for p in bundle.procedures if p.sequence is None] == []


def test_source_sequence_can_be_disabled(monkeypatch):
    monkeypatch.setenv("REPORTER_SOURCE_SEQUENCE", "0")
    row = next(r for r in CORPUS if r["id"] == "RB-01-01")
    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    assert all(p.sequence is None for p in bundle.procedures)
    # Even the legacy ranking no longer places the marker ahead of navigation.
    blocks = observed_order(compose_structured_report(bundle, strict=True))["detail_blocks"]
    assert blocks.index("fiducial_marker_placement") > blocks.index("transbronchial_cryobiopsy")


def test_single_target_then_navigated_is_not_split_into_two_targets():
    row = next(r for r in CORPUS if r["id"] == "RB-01-04")
    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    nav = [p for p in bundle.procedures if p.proc_type == "robotic_navigation"]
    assert [p.data["lesion_location"] for p in nav] == ["LB1/2"]


@pytest.mark.parametrize(
    "nodal,used,by_station",
    [
        ("EBUS-TBNA 4 each at 11Ri, 7 and 11L; elastography mixed type 2.", True, {"11RI": "Type 2", "7": "Type 2", "11L": "Type 2"}),
        ("EBUS 11Rs x4, elastography T1.", True, {"11RS": "Type 1"}),
        ("EBUS 7 type 1 x4, 4R type 3 x5.", True, {"7": "Type 1", "4R": "Type 3"}),
        ("EBUS 7 x4.", False, {}),
    ],
)
def test_elastography_class_is_bound_to_stations_and_never_a_pass_count(nodal, used, by_station):
    bundle = build_procedure_bundle_from_extraction({}, source_text="Ion LUL nodule cryo x4. " + nodal)
    ebus = next(p.data for p in bundle.procedures if p.proc_type == "ebus_tbna")
    assert bool(ebus.get("elastography_used")) is used
    assert {
        s["station_name"]: s["elastography_pattern"]
        for s in ebus["stations"]
        if s.get("elastography_pattern")
    } == by_station
    assert all(s["passes"] in (4, 5) for s in ebus["stations"])
    rendered = compose_structured_report(bundle, strict=True)
    for pattern in set(by_station.values()):
        assert f"{pattern} elastographic pattern" in rendered
    assert ("elastography" in rendered) is used


def test_survey_only_ebus_is_a_block_without_sampling_or_codes():
    row = next(r for r in CORPUS if r["id"] == "RB-08-03")
    bundle = build_procedure_bundle_from_extraction({}, source_text=row["prompt_text"])
    assert not any(p.proc_type == "ebus_tbna" for p in bundle.procedures)
    survey = next(p for p in bundle.procedures if p.proc_type == "ebus_survey")
    assert all(s["sampled"] is False for s in survey.data["stations"])
    assert not survey.cpt_candidates
    rendered = compose_structured_report(bundle, strict=True)
    assert "No lymph nodes were sampled." in rendered
    assert "Type 1 elastographic pattern" in rendered
    assert "31652" not in rendered and "31653" not in rendered


@pytest.mark.parametrize(
    "sampling",
    ["Brushed the nodule. No biopsy.", "Brush biopsy only.", "Nodule not biopsied; brushed only."],
)
def test_brushing_alone_does_not_add_generic_biopsy(sampling):
    source = "Navigated to LLL nodule with radial EBUS. " + sampling
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    assert "Peripheral lung biopsy" not in (bundle.findings_text or "")


def test_sequential_cone_beam_and_biopsy_survive_brushing_and_render_patch():
    from app.reporting import apply_bundle_json_patch

    source = next(r["prompt_text"] for r in CORPUS if r["id"] == "RB-07-04")
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    index = next(i for i, p in enumerate(bundle.procedures) if p.proc_type == "ebus_tbna")
    patched = apply_bundle_json_patch(
        bundle, [{"op": "add", "path": f"/procedures/{index}/data/stations/0/passes", "value": 3}]
    )
    rendered = compose_structured_report(patched, strict=True)
    assert "Peripheral lung biopsy at LLL; sampling technique unspecified" in rendered
    assert "used sequential cone-beam spins until needle placement was confirmed" in rendered
    assert "Station 11L. 3 EBUS-guided transbronchial needle aspiration passes were performed." in rendered


@pytest.mark.parametrize(
    "imaging", ["Never used cone-beam spins.", "Planned to perform cone-beam spins, not performed."]
)
def test_unused_cone_beam_does_not_add_guidance(imaging):
    source = "Navigated to LLL nodule with radial EBUS and brushed. " + imaging
    bundle = build_procedure_bundle_from_extraction({}, source_text=source)
    assert "CBCT guidance:" not in (bundle.findings_text or "")
