from __future__ import annotations

from modules.coder.ncci import NCCIEngine


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

