#!/usr/bin/env python3
"""Scrub PHI from golden JSON files for ML training.

This script processes all golden_*.json files in data/knowledge/golden_extractions/
and scrubs PHI from the `note_text` field using PresidioScrubber.

The scrubbing uses the same Presidio-based scrubber as the PHI Demo workflow,
with clinical allowlists to preserve anatomical terms and procedure vocabulary.

Usage:
    python scripts/scrub_golden_jsons.py                    # Scrub in-place (creates backups)
    python scripts/scrub_golden_jsons.py --dry-run          # Preview without modifying
    python scripts/scrub_golden_jsons.py --no-backup        # Scrub in-place without backups
    python scripts/scrub_golden_jsons.py --output-dir out/  # Write to separate directory
    python scripts/scrub_golden_jsons.py --report-path artifacts/redactions.jsonl  # Write redaction report (JSONL)
"""

from __future__ import annotations

import argparse
import json
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add project root to path for module imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tqdm import tqdm


def get_scrubber():
    """Initialize PresidioScrubber with fallback."""
    from app.phi.adapters.presidio_scrubber import PresidioScrubber
    return PresidioScrubber()


def _open_report_writer(report_path: Path | None, report_format: str):
    """Open a report writer for redactions.

    Returns:
        (handle, write_row_fn) or (None, None) if report_path is None.
    """
    if report_path is None:
        return None, None

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_format = report_format.lower().strip()
    if report_format not in {"jsonl", "csv"}:
        raise ValueError("report_format must be one of: jsonl, csv")

    if report_format == "jsonl":
        f = report_path.open("w", encoding="utf-8")

        def _write(row: dict[str, Any]) -> None:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        return f, _write

    # CSV
    f = report_path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "timestamp_utc",
            "input_file",
            "record_index",
            "entity_type",
            "placeholder",
            "original_start",
            "original_end",
            "original_text",
        ],
    )
    writer.writeheader()

    def _write(row: dict[str, Any]) -> None:
        writer.writerow(row)

    return f, _write


def scrub_golden_json(
    input_path: Path,
    scrubber,
    dry_run: bool = False,
    output_path: Path | None = None,
    create_backup: bool = True,
    report_write=None,
    report_timestamp_utc: str | None = None,
) -> dict:
    """Scrub PHI from a single golden JSON file.

    Args:
        input_path: Path to golden JSON file
        scrubber: PresidioScrubber instance
        dry_run: If True, don't write changes
        output_path: Optional separate output path
        create_backup: If True and output_path is None, create .bak backup
        report_write: Optional function which accepts a dict and writes a report row
        report_timestamp_utc: Optional timestamp string to include in report rows

    Returns:
        Dict with stats: {total_records, scrubbed_count, entity_count}
    """
    with open(input_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    stats = {
        "total_records": len(records),
        "scrubbed_count": 0,
        "entity_count": 0,
        "entities_by_type": {},
    }

    for idx, record in enumerate(records):
        if "note_text" not in record or not record["note_text"]:
            continue

        original_text = record["note_text"]
        result = scrubber.scrub(original_text, document_type="procedure_note")

        if result.scrubbed_text != original_text:
            stats["scrubbed_count"] += 1
            stats["entity_count"] += len(result.entities)

            # Track entity types
            for ent in result.entities:
                etype = ent.get("entity_type", "UNKNOWN")
                stats["entities_by_type"][etype] = stats["entities_by_type"].get(etype, 0) + 1

                # Optional per-entity report rows
                if report_write is not None:
                    try:
                        start = int(ent.get("original_start", -1))
                        end = int(ent.get("original_end", -1))
                    except Exception:
                        start, end = -1, -1
                    redacted = ""
                    if 0 <= start < end <= len(original_text):
                        redacted = original_text[start:end]
                    report_write(
                        {
                            "timestamp_utc": report_timestamp_utc,
                            "input_file": str(input_path),
                            "record_index": idx,
                            "entity_type": etype,
                            "placeholder": ent.get("placeholder", ""),
                            "original_start": start,
                            "original_end": end,
                            "original_text": redacted,
                        }
                    )

            # Update the record
            record["note_text"] = result.scrubbed_text

            # Store original for reference (optional metadata)
            if "scrub_metadata" not in record:
                record["scrub_metadata"] = {}
            record["scrub_metadata"]["entities_redacted"] = len(result.entities)
            record["scrub_metadata"]["entity_types"] = [e.get("entity_type") for e in result.entities]

    if not dry_run:
        # Determine output path
        final_output = output_path if output_path else input_path

        # Create backup if writing in-place
        if output_path is None and create_backup:
            backup_path = input_path.with_suffix(".json.bak")
            shutil.copy2(input_path, backup_path)

        # Ensure output directory exists
        final_output.parent.mkdir(parents=True, exist_ok=True)

        # Write scrubbed data
        with open(final_output, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Scrub PHI from golden JSON files for ML training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions"),
        help="Directory containing golden_*.json files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write scrubbed files to separate directory (default: in-place)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create .bak backups when modifying in-place",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="golden_*.json",
        help="Glob pattern for input files (default: golden_*.json)",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Optional path to write a redaction report (JSONL/CSV).",
    )
    parser.add_argument(
        "--report-format",
        type=str,
        default="jsonl",
        choices=["jsonl", "csv"],
        help="Redaction report format (default: jsonl).",
    )

    args = parser.parse_args()

    # Find golden JSON files
    input_files = sorted(args.input_dir.glob(args.pattern))
    if not input_files:
        print(f"No files matching '{args.pattern}' found in {args.input_dir}")
        return

    print(f"\n{'=' * 60}")
    print("Golden JSON PHI Scrubbing")
    print(f"{'=' * 60}")
    print(f"Input directory: {args.input_dir}")
    print(f"Files found: {len(input_files)}")
    print(f"Output: {'DRY RUN (no changes)' if args.dry_run else (args.output_dir or 'in-place')}")
    print(f"Backups: {'No' if args.no_backup else 'Yes'}")
    if args.report_path:
        print(f"Redaction report: {args.report_path} ({args.report_format})")
    print(f"{'=' * 60}\n")

    # Initialize scrubber
    print("Initializing Presidio scrubber...")
    scrubber = get_scrubber()
    print(f"Using spaCy model: {scrubber.model_name}\n")

    # Optional report writer
    report_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")
    report_handle, report_write = _open_report_writer(args.report_path, args.report_format)

    # Process files
    total_stats = {
        "files_processed": 0,
        "total_records": 0,
        "scrubbed_count": 0,
        "entity_count": 0,
        "entities_by_type": {},
    }

    for input_path in tqdm(input_files, desc="Processing files"):
        # Determine output path
        if args.output_dir:
            output_path = args.output_dir / input_path.name
        else:
            output_path = None

        try:
            stats = scrub_golden_json(
                input_path=input_path,
                scrubber=scrubber,
                dry_run=args.dry_run,
                output_path=output_path,
                create_backup=not args.no_backup,
                report_write=report_write,
                report_timestamp_utc=report_ts,
            )

            total_stats["files_processed"] += 1
            total_stats["total_records"] += stats["total_records"]
            total_stats["scrubbed_count"] += stats["scrubbed_count"]
            total_stats["entity_count"] += stats["entity_count"]

            for etype, count in stats["entities_by_type"].items():
                total_stats["entities_by_type"][etype] = (
                    total_stats["entities_by_type"].get(etype, 0) + count
                )

        except Exception as e:
            print(f"\nError processing {input_path}: {e}")
            continue

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Total records: {total_stats['total_records']}")
    print(f"Records with PHI scrubbed: {total_stats['scrubbed_count']}")
    print(f"Total entities redacted: {total_stats['entity_count']}")

    if total_stats["entities_by_type"]:
        print("\nEntities by type:")
        for etype, count in sorted(
            total_stats["entities_by_type"].items(), key=lambda x: -x[1]
        ):
            print(f"  {etype}: {count}")

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
    elif args.output_dir:
        print(f"\nScrubbed files written to: {args.output_dir}")
    else:
        print(f"\nFiles modified in-place. Backups: {'disabled' if args.no_backup else 'created (.bak)'}")

    if report_handle is not None:
        report_handle.close()
        print(f"\nRedaction report written: {args.report_path}")


if __name__ == "__main__":
    main()
