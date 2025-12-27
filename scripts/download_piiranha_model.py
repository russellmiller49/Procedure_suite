#!/usr/bin/env python3
"""
Download the Piiranha ONNX PHI detection model from Hugging Face.

Two modes:
- default: download a UI-usable snapshot into `modules/api/static/phi_redactor/vendor/...`
  so `/ui/phi_redactor/` can load it from same-origin static files.
- --full: download the full snapshot into `data/models/hf/...` for other local workflows.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    try:
        from huggingface_hub import snapshot_download
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "huggingface_hub is required. Install it (e.g. `pip install huggingface_hub`)."
        ) from e

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Download full snapshot (into data/models/hf/...) for other workflows.",
    )
    parser.add_argument(
        "--repo-id",
        default="onnx-community/piiranha-v1-detect-personal-information-ONNX",
        help=(
            "Hugging Face repo id to download. Default is the ONNX-converted repo used by the PHI UI. "
            "For the original model, use: iiiorg/piiranha-v1-detect-personal-information"
        ),
    )
    args = parser.parse_args()

    repo_id = args.repo_id
    repo_root = Path(__file__).resolve().parents[1]

    # For non-full mode, we only support the ONNX-converted repo because the UI worker expects the
    # `onnx/` subfolder artifacts to exist.
    if not args.full and repo_id != "onnx-community/piiranha-v1-detect-personal-information-ONNX":
        raise SystemExit(
            "--repo-id is only supported with --full (the UI vendor snapshot requires the ONNX repo)."
        )

    repo_slug = repo_id.split("/", 1)[1] if "/" in repo_id else repo_id
    local_dir = (
        repo_root / "data" / "models" / "hf" / repo_slug
        if args.full
        else repo_root
        / "modules"
        / "api"
        / "static"
        / "phi_redactor"
        / "vendor"
        / "piiranha-v1-detect-personal-information-ONNX"
    )
    local_dir.mkdir(parents=True, exist_ok=True)

    # Default keeps download tight: config/tokenizer + onnx artifacts.
    allow_patterns = None
    if not args.full:
        allow_patterns = [
            "*.json",
            "*.txt",
            "*.model",
            "tokenizer/**",
            "onnx/**",
        ]

    print(f"[piiranha] Downloading snapshot: {repo_id}")
    print(f"[piiranha] Destination: {local_dir}")
    out = snapshot_download(
        repo_id=repo_id,
        local_dir=str(local_dir),
        allow_patterns=allow_patterns,
    )
    print(f"[piiranha] Done: {out}")


if __name__ == "__main__":
    main()


