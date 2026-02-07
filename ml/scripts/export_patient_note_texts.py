#!/usr/bin/env python3
"""
Export per-patient NOTE_ID → note_text JSON files from golden extractions.

Context:
  `data/knowledge/golden_extractions_final/golden_*.json` contains arrays of entries like:
    {
      "note_text": "...",
      "registry_entry": { "patient_mrn": "445892_syn_2", ... },
      ...
    }

Goal:
  Create one JSON file per patient that includes ONLY the NOTE_ID and note text for each
  associated synthetic note, e.g.:
    output/445892.json
      {
        "445892_syn_1": "...",
        "445892_syn_2": "...",
        ...
      }

Usage:
  python scripts/export_patient_note_texts.py \
    --input-dir data/knowledge/golden_extractions_final \
    --output-dir data/knowledge/patient_note_texts
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


_SYN_RE = re.compile(r"^(?P<base>.+?)_syn_(?P<num>\d+)$")
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class NoteRef:
    note_id: str
    note_text: str
    syn_num: int | None
    source_file: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Export per-patient NOTE_ID → note_text JSON files from golden_*.json."
    )
    p.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory containing golden_*.json files (arrays).",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/patient_note_texts"),
        help="Directory to write per-patient JSON files.",
    )
    p.add_argument(
        "--id-field",
        type=str,
        default="registry_entry.patient_mrn",
        help=(
            "Dot-path to the NOTE_ID. Examples: registry_entry.patient_mrn (default), "
            "note_id, registry_entry.note_id"
        ),
    )
    p.add_argument(
        "--text-field",
        type=str,
        default="note_text",
        help="Field name for note text (default: note_text).",
    )
    p.add_argument(
        "--only-synthetic",
        action="store_true",
        help="If set, only export notes whose NOTE_ID matches *_syn_<n>.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, do not write files; only log counts.",
    )
    return p.parse_args(argv)


def _get_by_dotpath(obj: dict[str, Any], dotpath: str) -> Any:
    cur: Any = obj
    for key in dotpath.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def extract_note_id(entry: dict[str, Any], id_field: str) -> str | None:
    """Extract a NOTE_ID from an entry, using the configured dot-path plus fallbacks."""
    raw = _get_by_dotpath(entry, id_field)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()

    # Common fallbacks we’ve seen in various datasets.
    for fallback in ("note_id", "noteId", "registry_entry.patient_mrn", "registry_entry.note_id"):
        raw2 = _get_by_dotpath(entry, fallback)
        if isinstance(raw2, str) and raw2.strip():
            return raw2.strip()

    return None


def split_patient_base(note_id: str) -> tuple[str, int | None]:
    """Return (patient_base_id, syn_num) where syn_num is parsed from *_syn_<n>."""
    m = _SYN_RE.match(note_id)
    if not m:
        return note_id, None
    return m.group("base"), int(m.group("num"))


def _safe_patient_filename(patient_id: str) -> str:
    cleaned = _SAFE_FILENAME_RE.sub("_", patient_id).strip("._-")
    return cleaned or "unknown"


def collect_notes(
    input_dir: Path,
    *,
    id_field: str,
    text_field: str,
    only_synthetic: bool,
) -> tuple[dict[str, list[NoteRef]], dict[str, int]]:
    """Scan golden_*.json and group NoteRef entries by patient base id."""
    by_patient: dict[str, list[NoteRef]] = defaultdict(list)
    stats = {
        "files": 0,
        "entries": 0,
        "kept": 0,
        "skipped_missing_id": 0,
        "skipped_missing_text": 0,
        "skipped_non_synthetic": 0,
        "skipped_parse_error": 0,
    }

    golden_files = sorted(input_dir.glob("golden_*.json"))
    if not golden_files:
        raise FileNotFoundError(f"No golden_*.json found in: {input_dir}")

    for path in golden_files:
        stats["files"] += 1
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001 - surface source file in log + stats
            logger.warning("Failed to parse %s: %s", path, e)
            stats["skipped_parse_error"] += 1
            continue

        if not isinstance(data, list):
            logger.warning("Skipping %s (expected top-level list, got %s)", path, type(data).__name__)
            stats["skipped_parse_error"] += 1
            continue

        for entry in data:
            stats["entries"] += 1
            if not isinstance(entry, dict):
                stats["skipped_parse_error"] += 1
                continue

            note_id = extract_note_id(entry, id_field)
            if not note_id:
                stats["skipped_missing_id"] += 1
                continue

            patient_id, syn_num = split_patient_base(note_id)
            if only_synthetic and syn_num is None:
                stats["skipped_non_synthetic"] += 1
                continue

            note_text = entry.get(text_field)
            if not isinstance(note_text, str) or not note_text.strip():
                stats["skipped_missing_text"] += 1
                continue

            by_patient[patient_id].append(
                NoteRef(
                    note_id=note_id,
                    note_text=note_text,
                    syn_num=syn_num,
                    source_file=path.name,
                )
            )
            stats["kept"] += 1

    return by_patient, stats


def write_patient_files(by_patient: dict[str, list[NoteRef]], output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for patient_id, notes in by_patient.items():
        # Sort: synthetic notes by syn_num, then non-synthetic by note_id (stable).
        notes_sorted = sorted(
            notes,
            key=lambda n: (
                0 if n.syn_num is not None else 1,
                n.syn_num if n.syn_num is not None else 10**9,
                n.note_id,
            ),
        )

        payload: dict[str, str] = {}
        for n in notes_sorted:
            payload[n.note_id] = n.note_text

        out_path = output_dir / f"{_safe_patient_filename(patient_id)}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written += 1

    return written


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    args = parse_args(argv)

    by_patient, stats = collect_notes(
        args.input_dir,
        id_field=args.id_field,
        text_field=args.text_field,
        only_synthetic=args.only_synthetic,
    )

    logger.info(
        "Scanned %d files, %d entries; kept=%d (patients=%d).",
        stats["files"],
        stats["entries"],
        stats["kept"],
        len(by_patient),
    )
    logger.info(
        "Skipped: missing_id=%d missing_text=%d non_synthetic=%d parse_error=%d",
        stats["skipped_missing_id"],
        stats["skipped_missing_text"],
        stats["skipped_non_synthetic"],
        stats["skipped_parse_error"],
    )

    if args.dry_run:
        logger.info("Dry run: no files written.")
        return

    written = write_patient_files(by_patient, args.output_dir)
    logger.info("Wrote %d patient JSON files to %s", written, args.output_dir)


if __name__ == "__main__":
    main(sys.argv[1:])

