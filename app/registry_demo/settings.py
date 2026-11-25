"""Demo gates and limits. Off unless explicitly enabled."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "data/knowledge/robotic_ebus_v1/demo"
PLACEHOLDER = "[REDACTED]"
MAX_TEXT_CHARS = 20_000


def _truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def demo_enabled() -> bool:
    return _truthy("PROCSUITE_ROBOTIC_EBUS_DEMO")


def data_dir() -> Path:
    override = os.getenv("PROCSUITE_DEMO_DATA_DIR", "").strip()
    return Path(override) if override else DEFAULT_DATA_DIR


def live_extraction_enabled() -> bool:
    """Live extraction of pasted text is not part of the public sample release."""
    return False


__all__ = [
    "DEFAULT_DATA_DIR",
    "MAX_TEXT_CHARS",
    "PLACEHOLDER",
    "data_dir",
    "demo_enabled",
    "live_extraction_enabled",
]
