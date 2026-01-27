#!/usr/bin/env python3
"""Immediate hotfix utilities for critical extraction issues.

Primary use: apply checkbox-negative corrections where some EMR templates encode
unchecked options as "0- Item" or "[ ] Item", which can be hallucinated as True.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_repo_on_path() -> None:
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _set_field_path(record: dict[str, Any], field_path: str, value: Any) -> bool:
    """Set a dotted field path on a JSON-like dict. Returns True if changed."""
    parts = [p for p in (field_path or "").split(".") if p]
    if not parts:
        return False

    current: Any = record
    for part in parts[:-1]:
        if not isinstance(current, dict):
            return False
        if part not in current or not isinstance(current.get(part), dict):
            current[part] = {}
        current = current[part]

    if not isinstance(current, dict):
        return False
    leaf = parts[-1]
    prior = current.get(leaf)
    current[leaf] = value
    return prior != value


def apply_checkbox_correction(text: str, record: Any) -> Any:
    """Fix hallucination of '0- Item' as True.

    Supports either a raw dict (JSON) or a RegistryRecord-like object that has
    `model_dump()` / `model_validate()`.
    """
    import re as _re

    record_dict: dict[str, Any]
    if isinstance(record, dict):
        record_dict = dict(record)
    elif hasattr(record, "model_dump"):
        record_dict = dict(record.model_dump())  # type: ignore[no-any-return]
    else:
        raise TypeError("record must be a dict or a RegistryRecord-like object")

    # Pattern for "0- Item" (indicating unselected in some EMRs)
    negation_patterns: list[tuple[str, str]] = [
        (r"(?im)^\s*0\s*[—\-]\s*Tunneled Pleural Catheter\b", "pleural_procedures.ipc.performed"),
        (r"(?im)^\s*0\s*[—\-]\s*Chest\s+tube\b", "pleural_procedures.chest_tube.performed"),
        (r"(?im)^\s*0\s*[—\-]\s*Pneumothorax\b", "complications.pneumothorax.occurred"),
    ]

    changed = False
    for pattern, field_path in negation_patterns:
        if _re.search(pattern, text or "", _re.IGNORECASE):
            changed |= _set_field_path(record_dict, field_path, False)

    if not changed:
        return record

    # Best-effort: return same type when possible.
    if isinstance(record, dict):
        return record_dict

    _ensure_repo_on_path()
    try:
        from modules.registry.schema import RegistryRecord

        return RegistryRecord.model_validate(record_dict)
    except Exception:
        return record_dict


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply immediate extraction logic fixes to a record JSON.")
    parser.add_argument("--note", type=Path, required=True, help="Path to raw/masked note text file")
    parser.add_argument("--record", type=Path, required=True, help="Path to RegistryRecord JSON file")
    args = parser.parse_args()

    note_text = _load_text(args.note)
    record_json = _load_json(args.record)
    updated = apply_checkbox_correction(note_text, record_json)

    out = updated if isinstance(updated, dict) else getattr(updated, "model_dump", lambda: updated)()
    print(json.dumps(out, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
