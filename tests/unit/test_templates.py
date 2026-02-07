from app.reporting.engine import compose_report_from_text


def test_ebus_template_contains_sections():
    text = "EBUS-TBNA of stations 7 and 4R; 3 FNA passes at each."
    report, note = compose_report_from_text(text, {"plan": "Observation"})
    assert report.procedure_core.type == "ebus_tbna"
    assert "Targets & Specimens" in note
    assert "Devices" in note
