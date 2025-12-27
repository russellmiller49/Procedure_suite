from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY_RUNTIME_DIR = Path("data/models/registry_runtime")


@dataclass(frozen=True)
class RegistryModelProvenance:
    backend: str | None
    version: str | None


def get_registry_runtime_dir() -> Path:
    override = os.getenv("REGISTRY_RUNTIME_DIR")
    return Path(override) if override else DEFAULT_REGISTRY_RUNTIME_DIR


def get_registry_manifest_path() -> Path:
    return get_registry_runtime_dir() / "manifest.json"


def read_registry_manifest() -> dict[str, Any]:
    path = get_registry_manifest_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def resolve_model_backend() -> str:
    value = os.getenv("MODEL_BACKEND", "").strip().lower()
    if value in ("pytorch", "onnx", "auto"):
        return value
    # Default to PyTorch for local/dev; production can set MODEL_BACKEND=onnx explicitly.
    return "pytorch"


def get_registry_model_provenance() -> RegistryModelProvenance:
    manifest = read_registry_manifest()
    backend = os.getenv("MODEL_BACKEND")
    backend = backend.strip().lower() if backend else None
    if backend == "":
        backend = None

    version = None
    if isinstance(manifest, dict):
        version_val = manifest.get("model_version") or manifest.get("version")
        if isinstance(version_val, str) and version_val.strip():
            version = version_val.strip()

        manifest_backend = manifest.get("model_backend") or manifest.get("backend")
        if backend is None and isinstance(manifest_backend, str) and manifest_backend.strip():
            backend = manifest_backend.strip().lower()

    # If MODEL_BACKEND isn't set, still expose the resolved mode ("auto") for logging.
    if backend is None:
        backend = resolve_model_backend()

    return RegistryModelProvenance(backend=backend, version=version)
