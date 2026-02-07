from __future__ import annotations

from pathlib import Path

from app.registry_cleaning import (
    CPTProcessor,
    ClinicalQCChecker,
    ConsistencyChecker,
    IssueLogger,
    SchemaNormalizer,
    derive_entry_id,
)


def _schema_path() -> str:
    candidates = [
        Path("schemas/IP_Registry.json"),
        Path("data/knowledge/IP_Registry.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError("Cannot locate IP Registry schema for tests")


def _kb_path() -> str:
    candidates = [
        Path("data/knowledge/ip_coding_billing_v3_0.json"),
        Path("data/knowledge/ip_coding_billing_v2_9.json"),
        Path("data/ip_coding_billing.v2_3.json"),
        Path("data/ip_coding_billing.v2_2.json"),
        Path("data/knowledge/ip_coding_billing.v2_2.json"),
        Path("proc_autocode/ip_kb/ip_coding_billing.v2_2.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError("Cannot locate IP coding knowledge base for tests")


def _base_entry() -> dict[str, object]:
    return {
        "patient_mrn": "MRN-001",
        "procedure_date": "2025-01-01",
        "provider_role": "Attending",
        "attending_name": "Dr. Test",
        "patient_age": 65,
        "gender": "M",
        "asa_class": 3,
        "primary_indication": "Test indication",
        "sedation_type": "Moderate",
        "airway_type": "Native",
        "final_diagnosis_prelim": "Malignancy",
        "data_entry_status": "Complete",
        "cpt_codes": ["31628"],
        "evidence": {},
    }


def _run_pipeline(entry: dict[str, object]):
    logger = IssueLogger()
    schema = SchemaNormalizer(_schema_path())
    cpt = CPTProcessor(_kb_path())
    consistency = ConsistencyChecker()
    clinical = ClinicalQCChecker()

    entry_id = derive_entry_id(entry, 0)
    cleaned = schema.normalize_entry(entry, entry_id, logger)
    cpt_context = cpt.process_entry(cleaned, entry_id, logger)
    consistency.apply(cleaned, entry_id, logger)
    clinical.check(cleaned, cpt_context, entry_id, logger)
    schema.validate_entry(cleaned, entry_id, logger)
    return cleaned, logger


def test_tblb_bundles_diagnostic_drop():
    entry = _base_entry()
    entry["cpt_codes"] = ["31628", "31622"]
    cleaned, logger = _run_pipeline(entry)
    assert cleaned["cpt_codes"] == ["31628"]
    assert any(
        issue.issue_type == "bundling_auto_drop" and issue.details.get("old") == "31622"
        for issue in logger.entries
    )


def test_gender_normalization():
    entry = _base_entry()
    entry["gender"] = "Male"
    cleaned, logger = _run_pipeline(entry)
    assert cleaned["gender"] == "M"
    assert any(issue.issue_type == "enum_normalized" and issue.field == "gender" for issue in logger.entries)
