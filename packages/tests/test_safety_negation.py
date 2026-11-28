"""Explicit coordinated negatives from synthetic Epic notes retain their scope."""
import hashlib
import sys
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "packages/ip_registry_contracts/src"), str(ROOT / "packages/ip_registry_engine/src")]
from ip_registry_contracts.models import ExtractionRequest  # noqa: E402
from ip_registry_engine.updates import clinical_update  # noqa: E402


def extract(text):
    request = ExtractionRequest(job_id=uuid4(), source_document_id=uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(), text=text, kind="clinical_update")
    return clinical_update(request)


@pytest.mark.parametrize("prefix", ["No", "Denies", "Without"])
def test_coordinated_negative_list_does_not_fabricate_icu_admission(prefix):
    text = prefix + " procedure-related complications, emergency department visits, hospital admissions, ICU admission or mechanical ventilation."
    result = extract(text)
    assert {k: result["clinical_update"][k] for k in ("icu_admission", "ed_visit", "hospital_admission")} == {
        "icu_admission": False, "ed_visit": False, "hospital_admission": False}
    assert result["clinical_update"]["deceased"] is None
    assert result["clinical_update"]["complete"] is None
    assert result["source_evidence"][0]["text"] == text


def test_unrelated_negative_does_not_suppress_documented_icu_admission():
    result = extract("No pneumothorax. The patient was admitted to the ICU for respiratory failure on day 2.")
    assert result["clinical_update"]["icu_admission"] is True


def test_different_interval_findings_require_review_instead_of_becoming_a_single_negative():
    result = extract("Days 0-7: No ICU admission. On day 12, the patient was admitted to the ICU.")
    assert result["clinical_update"]["icu_admission"] is None
    assert result["conflicting_safety_findings"] == ["icu_admission"]
    assert "conflicting_safety_findings" in result["review_requirements"]


def test_undocumented_followup_remains_unassessed():
    result = extract("Follow-up has not yet been assessed.")["clinical_update"]
    assert all(result[k] is None for k in ("icu_admission", "ed_visit", "hospital_admission", "complete", "deceased"))
