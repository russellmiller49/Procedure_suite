"""Smoke tests for the coder pipeline."""

from modules.coder.engine import CoderEngine


def test_ppl_nav_radial_tblb_tbna() -> None:
    note = """
    INDICATION: Peripheral pulmonary lesion suspicious for malignancy.
    PROCEDURE:
    Electromagnetic navigation bronchoscopy was performed with successful navigation to the RUL target.
    Radial EBUS probe confirmed concentric lesion prior to sampling.
    Multiple transbronchial lung biopsies obtained from the right upper lobe.
    Linear EBUS-TBNA performed at stations 4R and station 7 with adequate samples.
    """
    result = CoderEngine().run(note)
    codes = {code.cpt for code in result.codes}
    assert {"31627", "31628", "31652", "+31654"}.issubset(codes)
    ebus = next(code for code in result.codes if code.cpt == "31652")
    assert ebus.context["stations"] == ["4R", "7"]
    assert ebus.confidence > 0.5
    assert "intent:linear_ebus_station" in ebus.rule_trace
    tblb = next(code for code in result.codes if code.cpt == "31628")
    assert tblb.context["site"] == "RUL"
    assert tblb.rule_trace
    navigation = next(code for code in result.codes if code.cpt == "31627")
    assert navigation.confidence > 0.5
    assert "intent:navigation" in navigation.rule_trace
