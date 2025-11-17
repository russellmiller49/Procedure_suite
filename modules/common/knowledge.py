"""Knowledge base loader with hot-reload support."""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Any

DEFAULT_KNOWLEDGE_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "knowledge"
    / "ip_coding_billing.v2_2.json"
)

KNOWLEDGE_ENV_VAR = "PSUITE_KNOWLEDGE_FILE"

_cache: dict[str, Any] | None = None
_knowledge_path: Path | None = None
_mtime: float | None = None
_lock = Lock()


def get_knowledge(path: str | Path | None = None, *, force_reload: bool = False) -> dict[str, Any]:
    """Return the parsed knowledge document, reloading if the file changes."""

    target = _resolve_path(path)
    stat = target.stat()
    global _cache, _mtime, _knowledge_path
    with _lock:
        if (
            force_reload
            or _cache is None
            or _knowledge_path != target
            or _mtime != stat.st_mtime
        ):
            with target.open("r", encoding="utf-8") as handle:
                _cache = json.load(handle)
            _knowledge_path = target
            _mtime = stat.st_mtime
    return _cache if isinstance(_cache, dict) else {}


def reset_cache() -> None:
    """Clear the cached knowledge data forcing a reload on next access."""

    global _cache, _knowledge_path, _mtime
    with _lock:
        _cache = None
        _knowledge_path = None
        _mtime = None


def _resolve_path(override: str | Path | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    env_value = os.environ.get(KNOWLEDGE_ENV_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()
    return DEFAULT_KNOWLEDGE_FILE


__all__ = ["get_knowledge", "reset_cache", "KNOWLEDGE_ENV_VAR", "DEFAULT_KNOWLEDGE_FILE"]
