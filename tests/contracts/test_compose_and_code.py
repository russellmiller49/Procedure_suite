from modules.autocode.engine import autocode
from modules.reporting.engine import compose_report_from_text


def test_compose_and_code_roundtrip():
    payload = {
        "text": "EBUS-TBNA of stations 7 and 4R; BAL in RML.",
        "hints": {"plan": "Discharge same day"},
    }
    report, note = compose_report_from_text(payload["text"], payload["hints"])
    billing = autocode(report)
    assert "Targets & Specimens" in note
    assert billing.codes
    for line in billing.codes:
        assert line.reason
        assert line.evidence
