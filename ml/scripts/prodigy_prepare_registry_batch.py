#!/usr/bin/env python3
"""Compatibility wrapper for the Registry Prodigy batch prep ("Diamond Loop").

The repo historically used `ml/scripts/prodigy_prepare_registry.py`. The Diamond Loop
brief references `ml/scripts/prodigy_prepare_registry_batch.py`, so this wrapper
provides the documented CLI while delegating to the existing implementation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure repo root is importable when running as a file.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.scripts import prodigy_prepare_registry  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--output-file", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None, help="Alias for --count")
    parser.add_argument("--count", type=int, default=200, help="Number of tasks to emit")
    parser.add_argument(
        "--strategy",
        choices=["disagreement", "uncertainty", "random", "rare_boost", "hybrid"],
        default="disagreement",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/ml_training/registry_prodigy_manifest.json"),
        help="Manifest JSON (dedup)",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model-dir", type=Path, default=Path("data/models/registry_runtime"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    count = args.limit if args.limit is not None else args.count

    forwarded = [
        "--input-file",
        str(args.input_file),
        "--output-file",
        str(args.output_file),
        "--count",
        str(count),
        "--strategy",
        str(args.strategy),
        "--manifest",
        str(args.manifest),
        "--seed",
        str(args.seed),
        "--model-dir",
        str(args.model_dir),
    ]
    return int(prodigy_prepare_registry.main(forwarded))


if __name__ == "__main__":
    raise SystemExit(main())
