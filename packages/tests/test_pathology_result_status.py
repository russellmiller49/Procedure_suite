"""Regressions exposed by the Epic sandbox workflow; all notes are synthetic."""

import hashlib
import sys
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]
from ip_registry_contracts.models import ExtractionRequest  # noqa: E402
from ip_registry_engine.updates import pathology_update  # noqa: E402


def results(text):
    request = ExtractionRequest(
        job_id=uuid4(),
        source_document_id=uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        text=text,
        kind="pathology",
    )
    return pathology_update(request)["unlinked_pathology"]


@pytest.mark.parametrize(
    "text",
    [
        "ROSE was adequate; final pathology is pending.",
        "ROSE suspicious for malignancy. Final cytology: pending.",
        "Awaiting final pathology. ROSE showed lymphocytes.",
        "Final pathology is not yet available.",
        "Amended pathology report pending.",
    ],
)
def test_pending_diagnosis_cannot_become_final_or_amended(text):
    value = results(text)[0]
    assert value["result_status"] == "pending"
    assert value["index_result_class"] == "pending"
    assert value["diagnosis_text"] is None
    assert value["evidence"]["text"] == text


def test_pending_molecular_testing_preserves_final_diagnosis():
    value = results("Final diagnosis: adenocarcinoma. Molecular testing is pending.")[0]
    assert value["result_status"] == "final"
    assert value["index_result_class"] == "specific_malignant"


def test_status_stays_with_its_specimen():
    values = results(
        "A. Final diagnosis: adenocarcinoma.\n"
        "B. ROSE showed lymphocytes.\nC. Final pathology pending."
    )
    assert [(v["specimen_label"], v["result_status"]) for v in values] == [
        ("A", "final"),
        ("B", "preliminary"),
        ("C", "pending"),
    ]


def test_document_header_is_inherited_but_explicit_pending_wins():
    values = results(
        "FINAL DIAGNOSIS:\nA. Adenocarcinoma.\nB. Final cytology pending.\nC. Pending."
    )
    assert [v["result_status"] for v in values] == ["final", "pending", "pending"]


def test_actual_amendment_retains_required_supersession_review():
    value = results("A. Amended diagnosis: squamous cell carcinoma.")[0]
    assert value["result_status"] == "amended"
    assert value["supersedes_pathology_result_id"] is None
    assert value["attribution_status"] == "requires_review"


@pytest.mark.parametrize("suffix", [
    "No amended or superseded result is documented.",
    "The report was not amended.",
    "No corrected diagnosis has been issued.",
    "This specimen was finalized without an amended report.",
])
def test_negated_amendment_does_not_change_final_status(suffix):
    value = results("Final diagnosis: adenocarcinoma. " + suffix)[0]
    assert value["result_status"] == "final"
    assert value["index_result_class"] == "specific_malignant"


@pytest.mark.parametrize("text", [
    "No amended report was available previously. Corrected diagnosis: adenocarcinoma.",
    "The report was amended. Final diagnosis: adenocarcinoma.",
    "No prior amendment, but amended diagnosis: adenocarcinoma.",
])
def test_explicit_amendment_in_separate_clause_is_retained(text):
    assert results(text)[0]["result_status"] == "amended"


@pytest.mark.parametrize("ancillary", [
    "Material is insufficient for molecular testing.",
    "NGS: insufficient tissue.",
    "PD-L1 testing: insufficient material.",
    "Biomarker testing: nondiagnostic.",
])
def test_ancillary_insufficiency_does_not_make_diagnostic_biopsy_nondiagnostic(ancillary):
    value = results("Final diagnosis: adenocarcinoma. " + ancillary)[0]
    assert value["result_status"] == "final"
    assert value["index_result_class"] == "specific_malignant"
    assert ancillary in value["evidence"]["text"]


def test_explicit_diagnostic_insufficiency_is_preserved():
    value = results("Final diagnosis: insufficient tissue for diagnosis and molecular testing.")[0]
    assert value["index_result_class"] == "nondiagnostic"


def test_epic_prior_encounter_pathology_keeps_specimens_and_final_results_separate():
    values = results(
        "Final pathology addendum.\nSpecimen A: right upper lobe target T1 needle aspirate. "
        "Final diagnosis: pulmonary adenocarcinoma. Diagnostic adequacy: adequate. "
        "Material is insufficient for molecular testing. No amended or superseded result is documented.\n"
        "Specimen B: station 7 EBUS needle aspirate. Final diagnosis: lymphoid tissue, negative for malignant cells."
    )
    assert [(v["specimen_label"], v["result_status"], v["index_result_class"]) for v in values] == [
        ("A", "final", "specific_malignant"), ("B", "final", "nonspecific_benign")]
    assert all(v["attribution_status"] == "requires_review" for v in values)
