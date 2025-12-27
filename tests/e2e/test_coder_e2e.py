"""End-to-end tests for the coder pipeline using golden fixtures."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from modules.coder.engine import CoderEngine

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _code_map(result):
    return {code.cpt: code for code in result.codes}


def test_ppl_nav_radial_tblb() -> None:
    engine = CoderEngine()
    result = engine.run(_read_fixture("ppl_nav_radial_tblb.txt"))
    codes = _code_map(result)
    expected = {"31627", "+31654", "31629", "31628", "31624"}
    assert expected.issubset(codes.keys())

    sedation_codes = [code.cpt for code in result.codes if code.cpt in {"99152", "+99153"}]
    assert "99152" in sedation_codes and "+99153" in sedation_codes

    mer_summary = result.mer_summary or {}
    adjustments = mer_summary.get("adjustments", [])
    assert adjustments, "MER summary should include adjustments"
    for adj in adjustments:
        if adj["role"] == "add_on":
            assert adj["allowed"] == adj["rvu"]

    nav_trace = _code_map(result)["31627"].rule_trace
    assert "navigation_initiated" in nav_trace
    radial_trace = _code_map(result)["+31654"].rule_trace
    assert "radial_peripheral_localization" in radial_trace
    assert "31622" not in codes


def test_ebus_staging_three_stations() -> None:
    engine = CoderEngine()
    result = engine.run(_read_fixture("ebus_staging_4R_7_11R.txt"))
    codes = _code_map(result)
    assert "31653" in codes and "31652" not in codes
    assert "+31654" not in codes and "31627" not in codes
    assert all(code.cpt not in {"99152", "+99153"} for code in result.codes)


def test_stent_and_distinct_site_dilation() -> None:
    engine = CoderEngine()
    result = engine.run(_read_fixture("stent_rmb_and_dilation_lul.txt"))
    codes = _code_map(result)
    assert {"31636", "31630"}.issubset(codes)
    dilation = codes["31630"]
    assert {"59", "XS"}.issubset(set(dilation.modifiers))
    assert any(action.rule == "distinct_site_modifier" for action in result.ncci_actions)
    assert all(code.cpt not in {"99152", "+99153"} for code in result.codes)


def test_blvr_two_lobes_with_chartis_policy() -> None:
    engine = CoderEngine()
    result = engine.run(_read_fixture("blvr_two_lobes.txt"))
    codes = _code_map(result)
    assert {"31647", "+31651"}.issubset(codes)
    chartis_present = "31634" in codes
    if not chartis_present:
        assert any("Chartis" in warning for warning in result.warnings)
    assert all(code.cpt not in {"99152", "+99153"} for code in result.codes)


def test_thoracentesis_bilateral() -> None:
    engine = CoderEngine()
    result = engine.run(_read_fixture("thora_bilateral.txt"))
    codes = _code_map(result)
    assert "32555" in codes
    assert "50" in codes["32555"].modifiers


def test_therapeutic_aspiration_repeat_stay() -> None:
    engine = CoderEngine()
    result = engine.run(_read_fixture("therapeutic_aspiration_repeat_stay.txt"))
    counts = Counter(code.cpt for code in result.codes)
    assert counts["31645"] >= 1
    assert counts["31646"] >= 1
    sedation_sessions = [code for code in result.codes if code.cpt in {"99152", "+99153"}]
    assert len([code for code in sedation_sessions if code.cpt == "99152"]) >= 2
    assert len([code for code in sedation_sessions if code.cpt == "+99153"]) >= 2
