"""Demo gates and limits. Off unless explicitly enabled."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "data/knowledge/robotic_ebus_v1/demo"
PLACEHOLDER = "[REDACTED]"
MAX_TEXT_CHARS = 20_000
EGRESS_PROVIDER = "anthropic"


def _truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def _number(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


def demo_enabled() -> bool:
    return _truthy("PROCSUITE_ROBOTIC_EBUS_DEMO")


def data_dir() -> Path:
    override = os.getenv("PROCSUITE_DEMO_DATA_DIR", "").strip()
    return Path(override) if override else DEFAULT_DATA_DIR


def access_codes() -> tuple[str, ...]:
    """Tester passwords, comma separated, so one tester's can be withdrawn on its own."""
    raw = os.getenv("PROCSUITE_DEMO_ACCESS_CODE", "")
    return tuple(code.strip() for code in raw.split(",") if code.strip())


def live_extraction_enabled() -> bool:
    """Testers' own notes are read only when at least one tester password is set."""
    return bool(access_codes())


def model_configured() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())


def real_notes_to_model() -> bool:
    """The three switches the egress gate needs before browser-redacted text may leave."""
    providers = {
        p.strip().lower() for p in os.getenv("PROCSUITE_LLM_EGRESS_PROVIDERS", "").split(",")
    }
    return (
        _truthy("PROCSUITE_LLM_EGRESS_APPROVED")
        and EGRESS_PROVIDER in providers
        and _truthy("PROCSUITE_TRUST_CLIENT_SCRUB")
    )


def daily_usd_cap() -> float:
    return max(0.0, _number("PROCSUITE_DEMO_DAILY_USD_CAP", 10.0))


def reserve_usd() -> float:
    """Held before a paid call: the worst case of one extraction plus one repair call."""
    return max(0.01, _number("PROCSUITE_DEMO_RESERVE_USD", 0.75))


def timeout_s() -> float:
    return max(10.0, _number("PROCSUITE_DEMO_TIMEOUT_S", 240.0))


def state_dir() -> Path:
    override = os.getenv("PROCSUITE_DEMO_STATE_DIR", "").strip()
    return Path(override) if override else Path(tempfile.gettempdir()) / "procsuite_demo"


__all__ = [
    "DEFAULT_DATA_DIR",
    "EGRESS_PROVIDER",
    "MAX_TEXT_CHARS",
    "PLACEHOLDER",
    "access_codes",
    "daily_usd_cap",
    "data_dir",
    "demo_enabled",
    "live_extraction_enabled",
    "model_configured",
    "real_notes_to_model",
    "reserve_usd",
    "state_dir",
    "timeout_s",
]
