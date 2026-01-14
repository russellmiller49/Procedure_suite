from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all python scripts in data/granular annotations/Python_update_scripts/"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failing script (default: continue).",
    )
    parser.add_argument(
        "--pattern",
        default="note_*.py",
        help="Glob pattern to select scripts (default: note_*.py).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "data" / "granular annotations" / "Python_update_scripts"

    if not scripts_dir.exists():
        raise SystemExit(f"Scripts directory not found: {scripts_dir}")

    scripts = sorted(scripts_dir.glob(args.pattern))
    if not scripts:
        print(f"No scripts matched {args.pattern!r} in {scripts_dir}")
        return 0

    print(f"Found {len(scripts)} scripts in: {scripts_dir}")
    print(f"Python: {sys.executable}")
    print("-" * 60)

    failures: list[Path] = []
    start_all = time.time()

    for idx, script_path in enumerate(scripts, start=1):
        rel = script_path.relative_to(repo_root)
        print(f"[{idx}/{len(scripts)}] Running {rel} ...", flush=True)

        # Run each script in repo root so relative-path scripts behave consistently.
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(repo_root),
        )

        if result.returncode != 0:
            failures.append(script_path)
            print(f"  -> FAILED (exit {result.returncode})")
            if args.fail_fast:
                break

    elapsed = time.time() - start_all
    print("-" * 60)
    print(f"Done in {elapsed:.2f}s")
    print(f"Failed: {len(failures)}")
    if failures:
        for p in failures:
            print(f" - {p.relative_to(repo_root)}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

