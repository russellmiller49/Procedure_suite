from __future__ import annotations

from app.coder.ncci import NCCIEngine
from app.coder.ncci import merge_ncci_sources


def test_ncci_ptp_modifier_indicator_zero_bundles_secondary() -> None:
    cfg = {
        "pairs": [
            {"column1": "31653", "column2": "31645", "modifier_indicator": "0"},
        ]
    }
    engine = NCCIEngine(ptp_cfg=cfg)
    result = engine.apply({"31653", "31645"})

    assert "31645" not in result.allowed
    assert result.bundled.get("31645") == "31653"


def test_ncci_ptp_modifier_indicator_one_does_not_bundle() -> None:
    cfg = {
        "pairs": [
            {"column1": "31653", "column2": "31629", "modifier_indicator": "1"},
        ]
    }
    engine = NCCIEngine(ptp_cfg=cfg)
    result = engine.apply({"31653", "31629"})

    assert "31629" in result.allowed
    assert "31653" in result.allowed
    assert result.bundled == {}


def test_ncci_ptp_backwards_compatible_modifier_allowed_bool() -> None:
    cfg = {
        "pairs": [
            {"column1": "31653", "column2": "31645", "modifier_allowed": False},
        ]
    }
    engine = NCCIEngine(ptp_cfg=cfg)
    result = engine.apply({"31653", "31645"})

    assert "31645" not in result.allowed
    assert result.bundled.get("31645") == "31653"


def test_merge_ncci_sources_external_overrides_kb() -> None:
    kb = {
        "ncci_pairs": [
            {"primary": "31628", "secondary": "31629", "modifier_allowed": True},
        ]
    }
    external = {
        "source_year": 2026,
        "pairs": [
            {"column1": "31628", "column2": "31629", "modifier_indicator": "0"},
        ],
    }
    merged = merge_ncci_sources(kb_document=kb, external_cfg=external)

    pairs = merged.get("pairs") or []
    match = next((p for p in pairs if p.get("column1") == "31628" and p.get("column2") == "31629"), None)
    assert match is not None
    assert match.get("modifier_indicator") == "0"
