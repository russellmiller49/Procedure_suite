"""Knowledge base loader with hot-reload support."""

from __future__ import annotations

import hashlib
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
_checksum: str | None = None
_version: str | None = None
_lock = Lock()


def get_knowledge(path: str | Path | None = None, *, force_reload: bool = False) -> dict[str, Any]:
    """Return the parsed knowledge document, reloading if the file changes."""

    target = _resolve_path(path)
    stat = target.stat()
    global _cache, _mtime, _knowledge_path, _checksum, _version
    with _lock:
        if (
            force_reload
            or _cache is None
            or _knowledge_path != target
            or _mtime != stat.st_mtime
        ):
            raw = target.read_bytes()
            data = json.loads(raw.decode("utf-8"))
            _cache = data
            _knowledge_path = target
            _mtime = stat.st_mtime
            _checksum = hashlib.sha256(raw).hexdigest()
            _version = data.get("version")
    return _cache if isinstance(_cache, dict) else {}


def reset_cache() -> None:
    """Clear the cached knowledge data forcing a reload on next access."""

    global _cache, _knowledge_path, _mtime, _checksum, _version
    with _lock:
        _cache = None
        _knowledge_path = None
        _mtime = None
        _checksum = None
        _version = None


def knowledge_version() -> str | None:
    """Return the semantic version of the loaded knowledge file."""

    get_knowledge()
    return _version


def knowledge_hash() -> str | None:
    """Return the SHA256 hash of the current knowledge file contents."""

    get_knowledge()
    return _checksum


def get_rvu(cpt: str) -> dict[str, float] | None:
    data = get_knowledge()
    rvus = data.get("rvus", {})
    entry = rvus.get(cpt)
    if not entry:
        return None
    return {"work": float(entry.get("work", 0.0)), "pe": float(entry.get("pe", 0.0)), "mp": float(entry.get("mp", 0.0))}


def total_rvu(cpt: str) -> float:
    entry = get_rvu(cpt)
    if not entry:
        return 0.0
    return entry["work"] + entry["pe"] + entry["mp"]


def is_add_on_code(cpt: str) -> bool:
    data = get_knowledge()
    return cpt.startswith("+") or cpt in set(data.get("add_on_codes", []))


def bundling_rules() -> dict[str, Any]:
    return get_knowledge().get("bundling_rules", {})


def ncci_pairs() -> list[dict[str, Any]]:
    return list(get_knowledge().get("ncci_pairs", []))


def synonym_list(key: str) -> list[str]:
    return list(get_knowledge().get("synonyms", {}).get(key, []))


def lobe_aliases() -> dict[str, list[str]]:
    return get_knowledge().get("lobes", {})


def station_aliases() -> dict[str, list[str]]:
    return get_knowledge().get("stations", {})


def airway_map() -> dict[str, dict[str, Any]]:
    return get_knowledge().get("airways", {})


def blvr_config() -> dict[str, Any]:
    return get_knowledge().get("blvr", {})


def _resolve_path(override: str | Path | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    env_value = os.environ.get(KNOWLEDGE_ENV_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()
    return DEFAULT_KNOWLEDGE_FILE


__all__ = [
    "get_knowledge",
    "reset_cache",
    "knowledge_version",
    "knowledge_hash",
    "get_rvu",
    "total_rvu",
    "is_add_on_code",
    "bundling_rules",
    "ncci_pairs",
    "synonym_list",
    "lobe_aliases",
    "station_aliases",
    "airway_map",
    "blvr_config",
    "KNOWLEDGE_ENV_VAR",
    "DEFAULT_KNOWLEDGE_FILE",
]
