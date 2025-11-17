"""End-to-end tests for the registry extractor using golden fixtures."""

from __future__ import annotations

from pathlib import Path

from modules.registry.engine import RegistryEngine

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_registry_ppl_nav_radial_tblb() -> None:
    engine = RegistryEngine()
    record = engine.run(_read_fixture("ppl_nav_radial_tblb.txt"))
    assert record.navigation_used is True
    assert record.radial_ebus_used is True
    assert record.tblb_lobes == ["RUL"]
    assert record.linear_ebus_stations == []
    assert record.anesthesia == "Moderate Sedation"
    assert record.sedation_start is not None and record.sedation_stop is not None
    assert "tblb_lobes" in record.evidence and record.evidence["tblb_lobes"]


def test_registry_ebus_staging() -> None:
    engine = RegistryEngine()
    record = engine.run(_read_fixture("ebus_staging_4R_7_11R.txt"))
    assert record.linear_ebus_stations == ["4R", "7", "11R"]
    assert record.navigation_used is False
    assert record.radial_ebus_used is False
    assert record.anesthesia in {"GA", "MAC", None}


def test_registry_stent_and_dilation() -> None:
    engine = RegistryEngine()
    record = engine.run(_read_fixture("stent_rmb_and_dilation_lul.txt"))
    assert record.stents and record.stents[0].site == "RMB"
    assert record.dilation_sites == ["LUL"]


def test_registry_blvr_two_lobes() -> None:
    engine = RegistryEngine()
    record = engine.run(_read_fixture("blvr_two_lobes.txt"))
    assert record.blvr is not None
    assert set(record.blvr.lobes) == {"RUL", "RML"}


def test_registry_thoracentesis() -> None:
    engine = RegistryEngine()
    record = engine.run(_read_fixture("thora_bilateral.txt"))
    assert record.pleural_procedures


def test_registry_therapeutic_aspiration_note() -> None:
    engine = RegistryEngine()
    record = engine.run(_read_fixture("therapeutic_aspiration_repeat_stay.txt"))
    assert record.anesthesia in {"Moderate Sedation", None}
    assert record.sedation_start is not None
