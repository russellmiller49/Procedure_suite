#!/usr/bin/env python3
"""Clean hallucinated or malformed institution fields in scrubbed golden JSONs.

Reads `.json` and `.jsonl` files from the scrubbed directory, fixes bad
`registry_entry.institution_name` values, and writes cleaned output to
`data/knowledge/golden_extractions_final/`.

Rules:
- If `institution_name` contains anatomical terms (e.g., bronchus/lobe/carina/distal),
  replace with "Unknown Institution".
- Remove date fragments mistakenly embedded in institution fields (e.g., "Date: 11/10/2025").
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

ANATOMICAL_TERMS = ("bronchus", "lobe", "carina", "distal")

DATE_FRAGMENT_RE = re.compile(
    r"(?i)\bdate(?:\s+of\s+procedure)?\s*[:\-]\s*"
    r"(?:\[[^\]]+\]|<[^>]+>|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})"
)
SEPARATOR_RE = re.compile(r"\s*\|\|\s*|\s*\|\s*")
PREFIX_RE = re.compile(r"(?i)\b(?:location|facility|hospital|institution|site|center)\s*[:\-]\s*")


def iter_input_files(input_dir: Path) -> Iterable[Path]:
    yield from sorted([*input_dir.glob("*.json"), *input_dir.glob("*.jsonl")])


def clean_institution_name(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return "Unknown Institution"

    # Remove embedded date fragments
    s = DATE_FRAGMENT_RE.sub("", s)

    # Remove common separators used in evidence-like strings
    s = SEPARATOR_RE.sub(" ", s)

    # Strip common prefixes
    s = PREFIX_RE.sub("", s)

    s = " ".join(s.split()).strip(" -|")
    if not s:
        return "Unknown Institution"

    lowered = s.lower()
    if any(term in lowered for term in ANATOMICAL_TERMS):
        return "Unknown Institution"

    return s


def process_record(record: dict[str, Any]) -> bool:
    registry_entry = record.get("registry_entry")
    if not isinstance(registry_entry, dict):
        return False
    inst = registry_entry.get("institution_name")
    if not isinstance(inst, str):
        return False

    cleaned = clean_institution_name(inst)
    if cleaned == inst:
        return False
    registry_entry["institution_name"] = cleaned
    return True


def process_json_file(input_path: Path, output_path: Path) -> dict[str, int]:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        return {"records": 0, "changed": 0}

    changed = 0
    for rec in records:
        if isinstance(rec, dict) and process_record(rec):
            changed += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"records": len(records), "changed": changed}


def process_jsonl_file(input_path: Path, output_path: Path) -> dict[str, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    changed = 0
    records = 0
    with input_path.open("r", encoding="utf-8") as in_f, output_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            records += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if isinstance(rec, dict) and process_record(rec):
                changed += 1
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"records": records, "changed": changed}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix hallucinated institution_name values in scrubbed golden JSONs")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_scrubbed"),
        help="Directory containing scrubbed golden JSON/JSONL files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory to write cleaned output files",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.input_dir.exists():
        logger.error("Input directory not found: %s", args.input_dir)
        return 1

    files = list(iter_input_files(args.input_dir))
    if not files:
        logger.warning("No .json/.jsonl files found in %s", args.input_dir)
        return 0

    total_records = 0
    total_changed = 0
    for path in files:
        out_path = args.output_dir / path.name
        if path.suffix == ".jsonl":
            stats = process_jsonl_file(path, out_path)
        else:
            stats = process_json_file(path, out_path)
        total_records += stats["records"]
        total_changed += stats["changed"]

    logger.info("Files processed: %s", len(files))
    logger.info("Records processed: %s", total_records)
    logger.info("Records changed: %s", total_changed)
    logger.info("Output directory: %s", args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

