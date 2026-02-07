from __future__ import annotations

import os
from pathlib import Path


def notes_dir_from_env_or_workspace(*, anchor_file: str) -> Path:
    """Resolve notes fixture directory with optional environment override.

    Environment override:
    - PROCSUITE_NOTES_DIR: absolute/relative path to notes_text directory
    """
    override = os.getenv("PROCSUITE_NOTES_DIR")
    if override:
        return Path(override).expanduser()

    repo_root = Path(anchor_file).resolve().parents[2]
    return (
        repo_root.parent
        / "proc_suite_notes"
        / "data"
        / "granular annotations"
        / "notes_text"
    )

