"""Read-only store of demo samples, their reviewed redactions and stored results.

Three files in the demo data directory:

- ``samples.json``   sample notes (``ops/tools/build_robotic_ebus_demo_samples.py``)
- ``redactions.json`` the redacted text the real browser redactor produces for each
  sample; only these exact texts are served publicly
- ``results.json``   stored extraction results keyed by the sha256 of that text
  (``ops/tools/warm_robotic_ebus_demo_cache.py``)
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.registry_demo.settings import data_dir


def normalise(text: str) -> str:
    """Line endings and trailing whitespace never change which sample a text is."""
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip()


def text_key(text: str) -> str:
    return hashlib.sha256(normalise(text).encode()).hexdigest()


@lru_cache(maxsize=8)
def _load(path: str, mtime_ns: int) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def _read(name: str) -> dict[str, Any]:
    path = data_dir() / name
    if not path.exists():
        return {}
    return _load(str(path), path.stat().st_mtime_ns)


def samples() -> list[dict[str, Any]]:
    return list(_read("samples.json").get("samples") or [])


def sample(sample_id: str) -> dict[str, Any] | None:
    return next((s for s in samples() if s["id"] == sample_id), None)


def redactions(sample_id: str) -> list[dict[str, Any]]:
    """Reviewed redacted variants of a sample, canonical first."""
    return list((_read("redactions.json").get("redactions") or {}).get(sample_id) or [])


def result_for(text: str) -> dict[str, Any] | None:
    return (_read("results.json").get("entries") or {}).get(text_key(text))


def has_result(sample_id: str) -> bool:
    entries = _read("results.json").get("entries") or {}
    return any(r.get("sha256") in entries for r in redactions(sample_id))


__all__ = ["has_result", "normalise", "redactions", "result_for", "sample", "samples", "text_key"]
