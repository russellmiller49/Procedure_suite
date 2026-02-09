#!/usr/bin/env python3
"""Build canonical reporter prompt/completion training dataset."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_INPUT_DIR = Path(
    "/home/rjm/projects/proc_suite_notes/reporter_training/reporter_training"
)
DEFAULT_OUTPUT_DIR = Path("data/ml_training/reporter_prompt/v1")
DEFAULT_OUTPUT_JSONL = "reporter_prompt_pairs.jsonl"
DEFAULT_MANIFEST_JSON = "reporter_prompt_manifest.json"

REQUIRED_SECTION_HEADERS = [
    "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
    "INDICATION FOR OPERATION",
    "CONSENT",
    "PREOPERATIVE DIAGNOSIS",
    "POSTOPERATIVE DIAGNOSIS",
    "PROCEDURE",
    "ANESTHESIA",
    "MONITORING",
    "COMPLICATIONS",
    "PROCEDURE IN DETAIL",
    "IMPRESSION / PLAN",
]

ALLOWED_PLACEHOLDERS = {
    "Date",
    "Name",
    "Patient Name",
    "Age",
    "Sex",
    "Name / Self, Referred",
    "Referred Physician Name",
    "General anesthesia / airway type",
    "General anesthesia / Deep sedation",
    "General anesthesia / Moderate Sedation",
    "Fellow name",
    "Supine",
    "analysis type",
    "Additional ICD-10 if applicable",
    "Additional ICD-10 if applicable, e.g., COPD/Emphysema",
    "pleural effusion/nodules",
}

SOURCE_FILE_RE = re.compile(r"^(?P<family>note_\d{3})_(?P<split>train|valid)\.jsonl$", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\[([^\]\n]{1,80})\]")
DATE_LINE_RE = re.compile(r"(?im)^(\s*DATE OF PROCEDURE\s*:\s*)(.+)$")
NOTE_ID_LINE_RE = re.compile(r"(?i)^\s*NOTE_ID\s*:")
SOURCE_LINE_RE = re.compile(r"(?i)^\s*SOURCE_FILE\s*:")
LITERAL_NONE_RE = re.compile(r"\bNone\b")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-jsonl", default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--manifest-json", default=DEFAULT_MANIFEST_JSON)
    return parser.parse_args(argv)


def infer_source_metadata(source_file: str) -> tuple[str, str]:
    m = SOURCE_FILE_RE.match(source_file)
    if not m:
        return "unknown", "unknown"
    return m.group("family"), m.group("split").lower()


def find_missing_sections(text: str) -> list[str]:
    upper = (text or "").upper()
    return [header for header in REQUIRED_SECTION_HEADERS if header.upper() not in upper]


def find_disallowed_placeholders(text: str) -> list[str]:
    found = [m.group(1).strip() for m in PLACEHOLDER_RE.finditer(text or "")]
    disallowed = sorted({item for item in found if item not in ALLOWED_PLACEHOLDERS})
    return disallowed


def canonicalize_completion(completion_raw: str) -> tuple[str, bool]:
    """Return canonical completion text and preamble flag.

    - removes NOTE_ID/SOURCE_FILE preamble lines
    - normalizes DATE OF PROCEDURE value
    - preserves section bodies and overall order
    """
    lines = str(completion_raw or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out_lines: list[str] = []
    had_preamble = False

    for line in lines:
        normalized = line.rstrip()
        upper = normalized.upper()
        # Some rows have NOTE_ID and SOURCE_FILE on a single line.
        if "NOTE_ID:" in upper or "SOURCE_FILE:" in upper:
            had_preamble = True
            continue
        if NOTE_ID_LINE_RE.match(normalized) or SOURCE_LINE_RE.match(normalized):
            had_preamble = True
            continue
        out_lines.append(normalized)

    canonical = "\n".join(out_lines).strip()
    canonical = DATE_LINE_RE.sub(r"\1[Date]", canonical)
    return canonical, had_preamble


def build_quality_flags(completion_canonical: str, contains_note_id_preamble: bool) -> dict[str, Any]:
    return {
        "missing_required_sections": find_missing_sections(completion_canonical),
        "disallowed_placeholders": find_disallowed_placeholders(completion_canonical),
        "literal_none_present": bool(LITERAL_NONE_RE.search(completion_canonical)),
        "contains_note_id_preamble": contains_note_id_preamble,
    }


def iter_input_rows(input_dir: Path):
    for path in sorted(input_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line_num, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                yield path, line_num, line


def build_dataset_rows(input_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rejected_rows = 0
    flag_counter: Counter[str] = Counter()
    note_families: Counter[str] = Counter()

    index_per_file: Counter[str] = Counter()

    for path, line_num, raw in iter_input_rows(input_dir):
        try:
            payload = json.loads(raw)
        except Exception:
            rejected_rows += 1
            continue

        prompt = str(payload.get("prompt") or "").strip()
        completion_raw = str(payload.get("completion") or "").strip()
        if not prompt or not completion_raw:
            rejected_rows += 1
            continue

        source_file = path.name
        note_family, split_hint = infer_source_metadata(source_file)
        note_families[note_family] += 1

        index_per_file[source_file] += 1
        row_idx = index_per_file[source_file]
        row_id = f"reporter_prompt_v1_{note_family}_{split_hint}_{row_idx:04d}"

        completion_canonical, had_preamble = canonicalize_completion(completion_raw)
        quality_flags = build_quality_flags(completion_canonical, had_preamble)

        if quality_flags["missing_required_sections"]:
            flag_counter["rows_missing_required_sections"] += 1
        if quality_flags["disallowed_placeholders"]:
            flag_counter["rows_with_disallowed_placeholders"] += 1
        if quality_flags["literal_none_present"]:
            flag_counter["rows_with_literal_none"] += 1
        if quality_flags["contains_note_id_preamble"]:
            flag_counter["rows_with_note_id_preamble"] += 1

        rows.append(
            {
                "id": row_id,
                "note_family": note_family,
                "source_file": source_file,
                "source_split_hint": split_hint,
                "prompt_text": prompt,
                "completion_raw": completion_raw,
                "completion_canonical": completion_canonical,
                "quality_flags": quality_flags,
            }
        )

    manifest = {
        "dataset_contract": "reporter_prompt_pairs.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "summary": {
            "rows_written": len(rows),
            "rows_rejected": rejected_rows,
            "note_family_count": len(note_families),
        },
        "quality": dict(flag_counter),
        "note_family_counts": dict(sorted(note_families.items())),
        "required_headers": REQUIRED_SECTION_HEADERS,
    }
    return rows, manifest


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {args.input_dir}")

    rows, manifest = build_dataset_rows(args.input_dir)
    if not rows:
        raise RuntimeError("No valid rows were produced from input directory")

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    output_jsonl_path = output_dir / args.output_jsonl
    manifest_path = output_dir / args.manifest_json

    write_jsonl(output_jsonl_path, rows)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote dataset: {output_jsonl_path}")
    print(f"Wrote manifest: {manifest_path}")
    print(f"Rows: {manifest['summary']['rows_written']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
