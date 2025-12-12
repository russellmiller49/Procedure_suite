from __future__ import annotations

import os
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from modules.common.logger import get_logger
from modules.registry.model_runtime import get_registry_runtime_dir, read_registry_manifest, resolve_model_backend

logger = get_logger("registry.model_bootstrap")


@dataclass(frozen=True)
class BundleBootstrapResult:
    runtime_dir: Path
    downloaded: bool
    manifest: dict[str, Any]


def _parse_s3_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an s3:// URI: {uri}")
    no_scheme = uri[len("s3://") :]
    bucket, _, key = no_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid s3:// URI: {uri}")
    return bucket, key


def _download_s3_to_path(uri: str, dest: Path) -> None:
    bucket, key = _parse_s3_uri(uri)

    # Lazy import so local dev can run without boto3 unless bootstrap is enabled.
    import boto3  # type: ignore

    client = boto3.client("s3")
    dest.parent.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, key, str(dest))


def _extract_tarball_to_dir(tar_gz_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_gz_path, "r:gz") as tf:
        tf.extractall(path=dest_dir)


def _flatten_single_root(extracted_dir: Path) -> Path:
    children = [p for p in extracted_dir.iterdir() if p.name not in (".DS_Store",)]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extracted_dir


def _replace_tree(src_dir: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_dir, dest_dir)


def _s3_uri_for_backend(backend: str) -> str | None:
    if backend == "pytorch":
        return os.getenv("MODEL_BUNDLE_S3_URI_PYTORCH") or os.getenv("MODEL_BUNDLE_S3_URI")
    if backend == "onnx":
        return os.getenv("MODEL_BUNDLE_S3_URI_ONNX") or os.getenv("MODEL_BUNDLE_S3_URI")
    return None


def apply_resolved_registry_paths(backend: str, runtime_dir: Path | None = None) -> None:
    runtime_dir = runtime_dir or get_registry_runtime_dir()
    os.environ["REGISTRY_RUNTIME_DIR"] = str(runtime_dir)

    tokenizer_path = runtime_dir / "tokenizer"
    os.environ["REGISTRY_TOKENIZER_PATH"] = str(tokenizer_path)
    os.environ["REGISTRY_THRESHOLDS_PATH"] = str(runtime_dir / "thresholds.json")
    os.environ["REGISTRY_LABEL_FIELDS_PATH"] = str(runtime_dir / "registry_label_fields.json")

    if backend == "pytorch":
        os.environ["REGISTRY_MODEL_DIR"] = str(runtime_dir)
    elif backend == "onnx":
        os.environ["REGISTRY_ONNX_MODEL_PATH"] = str(runtime_dir / "registry_model_int8.onnx")


def ensure_registry_model_bundle(backend: str | None = None) -> BundleBootstrapResult:
    """Download + extract the configured registry model bundle into the runtime dir.

    No-op if:
    - no S3 URI is configured for the resolved backend, or
    - a manifest.json already exists in the runtime directory.
    """
    backend = (backend or resolve_model_backend()).strip().lower()
    if backend not in ("pytorch", "onnx"):
        backend = "auto"

    runtime_dir = get_registry_runtime_dir()
    existing_manifest = read_registry_manifest()
    if existing_manifest:
        apply_resolved_registry_paths(backend=backend, runtime_dir=runtime_dir)
        return BundleBootstrapResult(runtime_dir=runtime_dir, downloaded=False, manifest=existing_manifest)

    # Default "auto" behavior: don't bootstrap unless explicitly configured.
    if backend == "auto":
        configured = os.getenv("MODEL_BUNDLE_S3_URI_PYTORCH") or os.getenv("MODEL_BUNDLE_S3_URI_ONNX") or os.getenv("MODEL_BUNDLE_S3_URI")
        if not configured:
            return BundleBootstrapResult(runtime_dir=runtime_dir, downloaded=False, manifest={})
        # If only one URI is configured, prefer pytorch for local/dev ergonomics.
        backend = "pytorch" if os.getenv("MODEL_BUNDLE_S3_URI_PYTORCH") or os.getenv("MODEL_BUNDLE_S3_URI") else "onnx"

    uri = _s3_uri_for_backend(backend)
    if not uri:
        return BundleBootstrapResult(runtime_dir=runtime_dir, downloaded=False, manifest={})

    logger.info("Downloading registry model bundle", extra={"backend": backend, "s3_uri": uri})

    with tempfile.TemporaryDirectory(prefix="registry_bundle_") as td:
        td_path = Path(td)
        tar_path = td_path / "bundle.tar.gz"
        _download_s3_to_path(uri, tar_path)

        extracted = td_path / "extracted"
        _extract_tarball_to_dir(tar_path, extracted)
        root = _flatten_single_root(extracted)

        # Swap into place
        _replace_tree(root, runtime_dir)

    manifest = read_registry_manifest()
    apply_resolved_registry_paths(backend=backend, runtime_dir=runtime_dir)
    return BundleBootstrapResult(runtime_dir=runtime_dir, downloaded=True, manifest=manifest)

