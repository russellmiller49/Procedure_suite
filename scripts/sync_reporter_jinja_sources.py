#!/usr/bin/env python3
"""Sync macro Jinja sources into the knowledge mirror directory.

Canonical macro source:
  modules/reporting/templates/macros

Knowledge mirror:
  data/knowledge/Reporter_jinja2
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _tracked_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in root.glob("*.j2"):
        files[path.name] = path
    schema = root / "template_schema.json"
    if schema.exists():
        files[schema.name] = schema
    return files


def _diff(source_root: Path, target_root: Path) -> tuple[list[str], list[str], list[str]]:
    source = _tracked_files(source_root)
    target = _tracked_files(target_root)

    missing = sorted(name for name in source if name not in target)
    extra = sorted(name for name in target if name not in source)

    changed: list[str] = []
    for name in sorted(set(source).intersection(target)):
        if source[name].read_bytes() != target[name].read_bytes():
            changed.append(name)
    return missing, extra, changed


def _run_check(source_root: Path, target_root: Path) -> int:
    missing, extra, changed = _diff(source_root, target_root)
    if not (missing or extra or changed):
        print("Reporter Jinja mirror is in sync.")
        return 0

    print("Reporter Jinja mirror drift detected.")
    if missing:
        print("Missing in mirror:")
        for name in missing:
            print(f"  - {name}")
    if extra:
        print("Extra in mirror:")
        for name in extra:
            print(f"  - {name}")
    if changed:
        print("Content differs:")
        for name in changed:
            print(f"  - {name}")
    return 1


def _run_sync(source_root: Path, target_root: Path) -> int:
    target_root.mkdir(parents=True, exist_ok=True)
    source = _tracked_files(source_root)
    target = _tracked_files(target_root)

    copied = 0
    for name, src in source.items():
        dst = target_root / name
        shutil.copy2(src, dst)
        copied += 1

    removed = 0
    for name in sorted(name for name in target if name not in source):
        (target_root / name).unlink()
        removed += 1

    print(f"Synced {copied} file(s) from {source_root} -> {target_root}.")
    if removed:
        print(f"Removed {removed} stale mirrored file(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync reporter macro Jinja files into knowledge mirror.")
    parser.add_argument("--check", action="store_true", help="Fail if mirror differs from source.")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=_repo_root() / "modules" / "reporting" / "templates" / "macros",
        help="Canonical macro source directory.",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=_repo_root() / "data" / "knowledge" / "Reporter_jinja2",
        help="Knowledge mirror directory.",
    )
    args = parser.parse_args()

    source_root = args.source_dir.resolve()
    target_root = args.target_dir.resolve()
    if not source_root.exists():
        print(f"Source directory does not exist: {source_root}")
        return 1
    if args.check:
        return _run_check(source_root, target_root)
    return _run_sync(source_root, target_root)


if __name__ == "__main__":
    raise SystemExit(main())
