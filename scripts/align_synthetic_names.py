#!/usr/bin/env python3
"""Align patient name mentions to `synthetic_metadata.generated_name`.

Some golden extraction records contain inconsistent or placeholder patient names in
`note_text` and `registry_entry.evidence` (e.g., "Pt: [Name]" vs generated_name).
This script enforces the synthetic name for common patient header patterns and
prints a summary report.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any, Iterable, Tuple

logger = logging.getLogger(__name__)

STANDARD_REDACTION_TOKEN = "[REDACTED]"

# Match common patient header keys and capture the patient name value (not age/MRN suffixes).
PATIENT_HEADER_NAME_RE = re.compile(
    r"(?im)"
    r"(?P<prefix>\b(?:patient(?:\s+name)?|pt|subject|name)\b\s*[:\-]\s*)"
    r"(?P<name>"
    r"\[(?:patient\s+)?name\]"  # [Name] / [Patient Name]
    r"|<PERSON>"  # <PERSON>
    r"|[A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?"  # Last, First M.
    r"|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}"  # First Last (2-4 parts)
    r"|[A-Z][a-z]+"  # Single token fallback
    r")"
)

# Replace honorific placeholders like "Ms. [Name]" or "Mr. <PERSON>"
HONORIFIC_PLACEHOLDER_RE = re.compile(r"(?i)\b(?P<title>mr|ms|mrs)\.\s*(?P<name>\[(?:patient\s+)?name\]|<PERSON>)")


def iter_input_files(input_dir: Path) -> Iterable[Path]:
    yield from sorted(input_dir.glob("*.json"))


def _normalize_name(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if STANDARD_REDACTION_TOKEN in s:
        return ""
    # Placeholders are treated as non-matching.
    if s.startswith("[") and s.endswith("]"):
        return ""
    if s.startswith("<") and s.endswith(">"):
        return ""
    s = re.sub(r"(?i)^(mr|ms|mrs|dr)\.\s+", "", s).strip()

    # Trim common trailing demographics (", 64M", ", 67-year-old Male", etc.)
    s = re.sub(r"(?i),\s*\d{1,3}\s*[mf]\b.*$", "", s).strip()
    s = re.sub(r"(?i),\s*\d{1,3}[-\s]*(?:y/?o|yo|yrs?|years?|year[-\s]old)\b.*$", "", s).strip()

    # Normalize "Last, First" to "First Last"
    if "," in s:
        last, rest = s.split(",", 1)
        rest = rest.strip()
        if rest:
            s = f"{rest} {last.strip()}"

    s = " ".join(s.split()).strip(" ,")
    return s.casefold()


def _swap_last_first(name: str) -> str | None:
    if "," not in name:
        return None
    last, rest = name.split(",", 1)
    rest = " ".join(rest.split()).strip()
    if not last.strip() or not rest:
        return None
    return f"{rest} {last.strip()}"


def enforce_synthetic_name(text: str, generated_name: str) -> Tuple[str, bool, int]:
    """Return (new_text, changed, replacements_count)."""
    if not text or not generated_name:
        return text, False, 0

    desired_norm = _normalize_name(generated_name)
    if not desired_norm:
        return text, False, 0

    replacements = 0
    changed = False
    original_names: set[str] = set()

    def _replace_header(match: re.Match[str]) -> str:
        nonlocal replacements, changed
        prefix = match.group("prefix")
        name = match.group("name")
        if STANDARD_REDACTION_TOKEN in name:
            return match.group(0)
        current_norm = _normalize_name(name)
        if current_norm == desired_norm and current_norm:
            return match.group(0)
        # Record the original (non-placeholder) for global replacement pass
        if current_norm and not (name.startswith("[") or name.startswith("<")):
            original_names.add(name)
        replacements += 1
        changed = True
        return f"{prefix}{generated_name}"

    new_text = PATIENT_HEADER_NAME_RE.sub(_replace_header, text)

    def _replace_honorific(match: re.Match[str]) -> str:
        nonlocal replacements, changed
        title = match.group("title")
        name = match.group("name")
        if STANDARD_REDACTION_TOKEN in name:
            return match.group(0)
        replacements += 1
        changed = True
        return f"{title}. {generated_name}"

    new_text = HONORIFIC_PLACEHOLDER_RE.sub(_replace_honorific, new_text)

    # Replace remaining mentions of the original patient name (if we saw a concrete name).
    for original in sorted(original_names, key=len, reverse=True):
        if original and original in new_text:
            new_text = new_text.replace(original, generated_name)
        swapped = _swap_last_first(original)
        if swapped and swapped in new_text:
            new_text = new_text.replace(swapped, generated_name)

    if new_text != text and not changed:
        # e.g., global replacements only
        changed = True

    return new_text, changed, replacements


def enforce_in_structure(value: Any, generated_name: str) -> Tuple[Any, int, bool]:
    """Return (new_value, replacements, changed)."""
    if isinstance(value, str):
        new_text, changed, replacements = enforce_synthetic_name(value, generated_name)
        return new_text, replacements, changed
    if isinstance(value, list):
        total_rep = 0
        any_changed = False
        new_list = []
        for item in value:
            new_item, rep, ch = enforce_in_structure(item, generated_name)
            total_rep += rep
            any_changed = any_changed or ch
            new_list.append(new_item)
        return new_list, total_rep, any_changed
    if isinstance(value, dict):
        total_rep = 0
        any_changed = False
        new_dict = {}
        for k, v in value.items():
            new_v, rep, ch = enforce_in_structure(v, generated_name)
            total_rep += rep
            any_changed = any_changed or ch
            new_dict[k] = new_v
        return new_dict, total_rep, any_changed
    return value, 0, False


def main() -> int:
    parser = argparse.ArgumentParser(description="Align patient names to synthetic_metadata.generated_name")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions"),
        help="Directory containing golden JSON files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_aligned"),
        help="Directory to write aligned output files",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite input files instead of writing to --output-dir",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="When --in-place, create .bak backups next to the originals",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.input_dir.exists():
        logger.error("Input directory not found: %s", args.input_dir)
        return 1

    files = list(iter_input_files(args.input_dir))
    if not files:
        logger.warning("No golden_*.json files found in %s", args.input_dir)
        return 0

    if not args.in_place:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    records_total = 0
    records_changed = 0
    replacements_total = 0

    for path in files:
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            continue

        file_changed = False
        for rec in records:
            if not isinstance(rec, dict):
                continue
            records_total += 1

            synthetic = rec.get("synthetic_metadata")
            generated_name = synthetic.get("generated_name") if isinstance(synthetic, dict) else None
            if not isinstance(generated_name, str) or not generated_name.strip():
                continue

            rep_this = 0
            changed_this = False

            note_text = rec.get("note_text")
            if isinstance(note_text, str) and note_text:
                new_note, ch, rep = enforce_synthetic_name(note_text, generated_name)
                if ch and new_note != note_text:
                    rec["note_text"] = new_note
                    changed_this = True
                rep_this += rep

            registry_entry = rec.get("registry_entry")
            if isinstance(registry_entry, dict) and "evidence" in registry_entry:
                new_evidence, rep, ch = enforce_in_structure(registry_entry.get("evidence"), generated_name)
                if ch and new_evidence != registry_entry.get("evidence"):
                    registry_entry["evidence"] = new_evidence
                    changed_this = True
                rep_this += rep

            if changed_this:
                records_changed += 1
                replacements_total += rep_this
                file_changed = True

        out_path = path if args.in_place else (args.output_dir / path.name)
        if args.in_place and args.backup and file_changed:
            backup_path = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup_path)
        if file_changed or not args.in_place:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info("Records processed: %s", records_total)
    logger.info("Records changed: %s", records_changed)
    logger.info("Name replacements applied: %s", replacements_total)
    if args.in_place:
        logger.info("Output: in-place (%s)", args.input_dir)
    else:
        logger.info("Output directory: %s", args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

