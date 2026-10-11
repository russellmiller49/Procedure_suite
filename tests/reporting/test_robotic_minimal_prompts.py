"""Independent short-prompt fidelity: no parent-report or case-title enrichment."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.reporting import build_procedure_bundle_from_extraction, compose_structured_report
from app.reporting.normalization.robotic_prompt_fidelity import reconcile_robotic_prompt
from ops.tools.eval_reporter_robotic_minimal import check_slots
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
    assert not check_slots(bundle.model_dump(mode="json"), row["expected"])
    rendered = compose_structured_report(bundle, strict=True)
    for unsupported in [
        "informed consent was obtained",
        "3-4 passes",
        "ESTIMATED BLOOD LOSS: Minimal",
        "Post-procedure monitoring per protocol",
    ]:
        assert unsupported not in rendered


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
            "Ion RUL nodule biopsy. EBUS sampled 11L (left hilar) "
            "and station 7 (subcarinal)."
        ),
    )
    nodes = [
        s["station_name"]
        for p in bundle.procedures
        if p.proc_type == "ebus_tbna"
        for s in p.data["stations"]
    ]
    assert nodes == ["11L", "7"]
