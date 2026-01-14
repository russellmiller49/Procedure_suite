from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    target_dir = repo_root / "data" / "granular annotations" / "Python_update_scripts"
    target_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for note_num in range(129, 265):
        path = target_dir / f"note_{note_num:03d}.py"
        if path.exists():
            skipped += 1
            continue
        path.write_text("", encoding="utf-8")
        created += 1

    print(f"Target: {target_dir}")
    print(f"Created: {created}")
    print(f"Skipped (already existed): {skipped}")


if __name__ == "__main__":
    main()

