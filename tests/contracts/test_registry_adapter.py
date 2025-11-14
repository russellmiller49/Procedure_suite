from proc_registry.adapter import report_to_registry
from proc_autocode.engine import autocode
from proc_report.engine import compose_report_from_text


def test_registry_bundle_contains_lineage():
    text = "EBUS-TBNA of station 7 with 3 FNA passes."
    report, _ = compose_report_from_text(text, {"plan": "Recover in PACU"})
    billing = autocode(report)
    bundle = report_to_registry(report, billing)
    lineage = bundle["bronchoscopy_procedure"]["lineage"]
    assert lineage["paragraph_hashes"]
    assert "specimens" in bundle
    assert bundle["billing_lines"]
