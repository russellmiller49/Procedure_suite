"""
Shim to make ``from scripts.add_training_case import add_case`` work when running
generated scripts from ``data/granular annotations/Python_update_scripts``.

The update scripts are often executed via absolute paths, so the repository root
is not on ``sys.path`` and importing the real ``<repo>/scripts/add_training_case.py``
fails. This shim is discovered first (because the script directory is on
``sys.path``), then loads the real implementation by file path and re-exports
``add_case``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (
            candidate / "scripts" / "add_training_case.py"
        ).exists():
            return candidate
    raise RuntimeError(
        f"Could not locate repo root from {start}. Expected pyproject.toml and scripts/add_training_case.py"
    )


_here = Path(__file__).resolve()
_repo_root = _find_repo_root(_here.parent)
_target = _repo_root / "scripts" / "add_training_case.py"

_spec = importlib.util.spec_from_file_location("_proc_suite_add_training_case", _target)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load spec for {_target}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

add_case = _module.add_case

__all__ = ["add_case"]

