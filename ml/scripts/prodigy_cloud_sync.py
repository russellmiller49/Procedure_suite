#!/usr/bin/env python3
"""
Prodigy dataset cloud sync helper (safe for Google Drive / Dropbox / OneDrive).

Why this exists:
- Prodigy stores datasets in a local DB (often SQLite under ~/.prodigy).
- Cloud-syncing the SQLite DB file directly is risky and can corrupt the DB.
- The safe workflow is export → sync file → import.

This script wraps `prodigy db-out` and `prodigy db-in` with a convenient CLI and an
optional "reset dataset before import" mode to avoid drift/duplicates.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def export_dataset(*, dataset: str, out_file: Path, answer: str | None) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "prodigy", "db-out", dataset]
    if answer:
        cmd += ["--answer", answer]
    # Stream stdout directly to file (avoid loading into memory).
    with out_file.open("w", encoding="utf-8") as f:
        subprocess.run(cmd, check=True, stdout=f)


def reset_dataset(*, dataset: str) -> None:
    # Use the Prodigy DB API to avoid interactive CLI prompts.
    from prodigy.components.db import connect  # type: ignore

    db = connect()
    if dataset in db.datasets:
        db.drop_dataset(dataset)


def import_dataset(
    *,
    dataset: str,
    in_file: Path,
    reset_first: bool,
    overwrite: bool,
    rehash: bool,
) -> None:
    if not in_file.exists():
        raise FileNotFoundError(str(in_file))

    if reset_first:
        reset_dataset(dataset=dataset)

    cmd = [sys.executable, "-m", "prodigy", "db-in", dataset, str(in_file)]
    if overwrite:
        cmd += ["--overwrite"]
    if rehash:
        cmd += ["--rehash"]
    _run(cmd)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="Export a dataset to a JSONL file (cloud-safe)")
    p_exp.add_argument("--dataset", required=True, help="Prodigy dataset name (e.g. registry_v1)")
    p_exp.add_argument("--out", required=True, type=Path, help="Output JSONL file path")
    p_exp.add_argument(
        "--answer",
        choices=["accept", "reject", "ignore"],
        default=None,
        help="Optional: export only one answer type",
    )

    p_imp = sub.add_parser("import", help="Import a dataset JSONL file into the local Prodigy DB")
    p_imp.add_argument("--dataset", required=True, help="Prodigy dataset name (e.g. registry_v1)")
    p_imp.add_argument("--in", dest="in_file", required=True, type=Path, help="Input JSONL file path")
    p_imp.add_argument(
        "--reset",
        action="store_true",
        help="Drop the local dataset before importing (recommended when switching machines)",
    )
    p_imp.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing answers when importing (use with care; default: off)",
    )
    p_imp.add_argument(
        "--rehash",
        action="store_true",
        help="Recompute and overwrite hashes when importing (rarely needed; default: off)",
    )

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.cmd == "export":
        export_dataset(dataset=args.dataset, out_file=args.out, answer=args.answer)
        return 0
    if args.cmd == "import":
        import_dataset(
            dataset=args.dataset,
            in_file=args.in_file,
            reset_first=bool(args.reset),
            overwrite=bool(args.overwrite),
            rehash=bool(args.rehash),
        )
        return 0
    raise SystemExit(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())


