#!/usr/bin/env python3
"""Verify and cleanup registry human training data files.

This script:
1. Confirms all records from subset files exist in registry_human.csv (master)
2. Checks for label conflicts (same encounter_id with different procedure labels)
3. Reports schema differences (column mismatches)
4. Identifies any records missing from master
5. Optionally archives subset files to _archive/registry_human/

Usage:
    python ml/scripts/verify_registry_human_data.py           # Dry-run (report only)
    python ml/scripts/verify_registry_human_data.py --execute # Add missing + archive
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id

# File configuration
DATA_DIR = ROOT / "data" / "ml_training"
MASTER_FILE = "registry_human.csv"
SUBSET_FILES = [
    "registry_human_updates.csv",
    "registry_human_v2.csv",
    "registry_human_rigid_review.csv",
    "registry_human_v1_backup.csv",
]
ARCHIVE_DIR = DATA_DIR / "_archive" / "registry_human"


@dataclass
class VerificationResult:
    """Results from verifying a subset file against master."""

    subset_name: str
    total_records: int
    unique_encounter_ids: int
    columns: int
    column_list: list[str] = field(default_factory=list)
    contained_in_master: int = 0
    missing_from_master: list[str] = field(default_factory=list)
    label_conflicts: list[dict[str, Any]] = field(default_factory=list)
    schema_warnings: list[str] = field(default_factory=list)
    load_error: str | None = None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names (strip whitespace, BOM)."""
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
    return df


def _ensure_encounter_id(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Ensure encounter_id column exists and is populated."""
    if "encounter_id" not in df.columns:
        if "note_text" not in df.columns:
            raise ValueError(f"{name} missing both encounter_id and note_text columns")
        df["encounter_id"] = df["note_text"].fillna("").astype(str).map(
            lambda t: compute_encounter_id(t.strip())
        )
        return df

    df["encounter_id"] = df["encounter_id"].fillna("").astype(str).str.strip()

    if "note_text" in df.columns:
        mask = df["encounter_id"] == ""
        if mask.any():
            df.loc[mask, "encounter_id"] = df.loc[mask, "note_text"].fillna("").astype(str).map(
                lambda t: compute_encounter_id(t.strip())
            )
    return df


def load_csv_safe(path: Path) -> pd.DataFrame | None:
    """Load CSV with error handling for malformed files."""
    try:
        df = pd.read_csv(path)
        df = _normalize_columns(df)
        df = _ensure_encounter_id(df, path.name)
        return df
    except Exception as e:
        return None


def verify_subset(
    master_df: pd.DataFrame, subset_path: Path, labels: list[str]
) -> VerificationResult:
    """Verify a subset file against the master."""
    result = VerificationResult(
        subset_name=subset_path.name,
        total_records=0,
        unique_encounter_ids=0,
        columns=0,
    )

    if not subset_path.exists():
        result.load_error = "File not found"
        return result

    subset_df = load_csv_safe(subset_path)
    if subset_df is None:
        result.load_error = "Failed to load (malformed CSV)"
        return result

    result.total_records = len(subset_df)
    result.unique_encounter_ids = subset_df["encounter_id"].nunique()
    result.columns = len(subset_df.columns)
    result.column_list = list(subset_df.columns)

    # Check schema differences
    master_label_cols = set(labels) & set(master_df.columns)
    subset_label_cols = set(labels) & set(subset_df.columns)

    missing_in_subset = master_label_cols - subset_label_cols
    extra_in_subset = subset_label_cols - master_label_cols

    if missing_in_subset:
        result.schema_warnings.append(f"Missing columns vs master: {sorted(missing_in_subset)}")
    if extra_in_subset:
        result.schema_warnings.append(f"Extra columns vs master: {sorted(extra_in_subset)}")

    # Check containment
    master_ids = set(master_df["encounter_id"].unique())
    subset_ids = set(subset_df["encounter_id"].unique())

    contained = subset_ids & master_ids
    missing = subset_ids - master_ids

    result.contained_in_master = len(contained)
    result.missing_from_master = sorted(missing)

    # Check label conflicts for contained records
    common_labels = list(master_label_cols & subset_label_cols)
    if common_labels and contained:
        master_idx = master_df.set_index("encounter_id")
        subset_idx = subset_df.drop_duplicates("encounter_id").set_index("encounter_id")

        for eid in contained:
            if eid not in master_idx.index or eid not in subset_idx.index:
                continue

            master_row = master_idx.loc[eid]
            subset_row = subset_idx.loc[eid]

            conflicts = []
            for label in common_labels:
                if label in master_row and label in subset_row:
                    m_val = int(master_row[label]) if pd.notna(master_row[label]) else 0
                    s_val = int(subset_row[label]) if pd.notna(subset_row[label]) else 0
                    if m_val != s_val:
                        conflicts.append({"label": label, "master": m_val, "subset": s_val})

            if conflicts:
                result.label_conflicts.append({"encounter_id": eid, "conflicts": conflicts})

    return result


def generate_report(
    results: list[VerificationResult], master_stats: dict[str, Any]
) -> str:
    """Generate human-readable verification report."""
    lines = []
    ts = datetime.now().isoformat(timespec="seconds")

    lines.append("=" * 80)
    lines.append("              REGISTRY HUMAN DATA VERIFICATION REPORT")
    lines.append(f"              Generated: {ts}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"MASTER FILE: {MASTER_FILE}")
    lines.append(f"  - Total records: {master_stats['total_records']}")
    lines.append(f"  - Unique encounter_ids: {master_stats['unique_ids']}")
    lines.append(f"  - Columns: {master_stats['columns']}")
    lines.append("")

    total_missing = []
    total_conflicts = 0

    for r in results:
        lines.append("-" * 80)
        lines.append(f"SUBSET FILE: {r.subset_name}")
        lines.append("-" * 80)

        if r.load_error:
            lines.append(f"  ERROR: {r.load_error}")
            lines.append("")
            continue

        lines.append(f"  Records: {r.total_records} ({r.unique_encounter_ids} unique encounter_ids)")
        lines.append(f"  Columns: {r.columns}")
        lines.append("")

        pct = (r.contained_in_master / r.unique_encounter_ids * 100) if r.unique_encounter_ids > 0 else 0
        status = "[OK]" if r.contained_in_master == r.unique_encounter_ids else "[MISSING]"
        lines.append(f"  Containment: {r.contained_in_master}/{r.unique_encounter_ids} ({pct:.1f}%) in master {status}")

        if r.missing_from_master:
            lines.append(f"  Missing from master: {len(r.missing_from_master)}")
            for eid in r.missing_from_master[:5]:
                lines.append(f"    - {eid}")
            if len(r.missing_from_master) > 5:
                lines.append(f"    ... and {len(r.missing_from_master) - 5} more")
            total_missing.extend(r.missing_from_master)
        lines.append("")

        conflict_status = "[OK]" if not r.label_conflicts else "[CONFLICTS]"
        lines.append(f"  Label Conflicts: {len(r.label_conflicts)} {conflict_status}")
        if r.label_conflicts:
            # Summarize by label
            label_counts: dict[str, int] = {}
            for c in r.label_conflicts:
                for conflict in c["conflicts"]:
                    label_counts[conflict["label"]] = label_counts.get(conflict["label"], 0) + 1
            lines.append("    Affected labels:")
            for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
                lines.append(f"      - {label}: {count} conflicts")
            total_conflicts += len(r.label_conflicts)
        lines.append("")

        if r.schema_warnings:
            lines.append("  Schema Warnings:")
            for w in r.schema_warnings:
                lines.append(f"    - {w}")
            lines.append("")

    # Summary
    lines.append("=" * 80)
    lines.append("                              SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Files verified: {len(results)}")
    lines.append(f"Total unique missing records: {len(set(total_missing))}")
    if total_missing:
        lines.append(f"  Missing encounter_ids: {sorted(set(total_missing))}")
    lines.append(f"Total records with label conflicts: {total_conflicts}")
    lines.append("")

    if total_missing:
        lines.append("RECOMMENDATIONS:")
        lines.append("1. Add missing records to registry_human.csv")
        lines.append("2. Then run with --execute to archive subset files")
    else:
        lines.append("RECOMMENDATIONS:")
        lines.append("1. All records accounted for - safe to archive")
        lines.append("2. Run with --execute to archive subset files")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def add_missing_records(
    master_df: pd.DataFrame,
    subset_files: list[Path],
    missing_ids: set[str],
    labels: list[str],
) -> pd.DataFrame:
    """Add missing records from subset files to master."""
    if not missing_ids:
        return master_df

    records_to_add = []

    for subset_path in subset_files:
        subset_df = load_csv_safe(subset_path)
        if subset_df is None:
            continue

        for eid in missing_ids:
            matches = subset_df[subset_df["encounter_id"] == eid]
            if not matches.empty:
                records_to_add.append(matches.iloc[0].to_dict())

    if not records_to_add:
        return master_df

    # Ensure all label columns exist
    new_rows = pd.DataFrame(records_to_add)
    for col in labels:
        if col not in new_rows.columns:
            new_rows[col] = 0

    # Align columns with master
    for col in master_df.columns:
        if col not in new_rows.columns:
            new_rows[col] = "" if master_df[col].dtype == object else 0

    # Append and deduplicate
    result = pd.concat([master_df, new_rows], ignore_index=True)
    result = result.drop_duplicates(subset=["encounter_id"], keep="last")

    return result


def archive_files(files: list[Path], dry_run: bool = True) -> list[dict[str, str]]:
    """Archive files to _archive/registry_human/ folder."""
    archived = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for f in files:
        if not f.exists():
            continue

        archive_name = f"{f.name}.{ts}"
        archive_path = ARCHIVE_DIR / archive_name

        if dry_run:
            print(f"  [DRY-RUN] Would archive: {f.name} -> {archive_path}")
        else:
            shutil.move(str(f), str(archive_path))
            print(f"  Archived: {f.name} -> {archive_path}")

        archived.append({"original": f.name, "archived_as": archive_name})

    return archived


def create_manifest(
    archived: list[dict[str, str]],
    master_records: int,
    missing_added: int,
) -> None:
    """Create archive manifest JSON."""
    manifest = {
        "archived_at": datetime.now().isoformat(timespec="seconds"),
        "reason": "Consolidated into registry_human.csv (single source of truth)",
        "master_file": MASTER_FILE,
        "master_records_after": master_records,
        "missing_records_added": missing_added,
        "archived_files": archived,
    }

    manifest_path = ARCHIVE_DIR / "ARCHIVE_MANIFEST.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Created manifest: {manifest_path}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--execute",
        action="store_true",
        help="Execute cleanup (add missing records and archive files). Default is dry-run.",
    )
    p.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"Data directory (default: {DATA_DIR})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = args.data_dir

    master_path = data_dir / MASTER_FILE
    if not master_path.exists():
        print(f"ERROR: Master file not found: {master_path}")
        return 1

    # Load master
    master_df = load_csv_safe(master_path)
    if master_df is None:
        print(f"ERROR: Failed to load master file: {master_path}")
        return 1

    master_stats = {
        "total_records": len(master_df),
        "unique_ids": master_df["encounter_id"].nunique(),
        "columns": len(master_df.columns),
    }

    # Verify each subset
    results = []
    labels = list(REGISTRY_LABELS)

    for subset_name in SUBSET_FILES:
        subset_path = data_dir / subset_name
        result = verify_subset(master_df, subset_path, labels)
        results.append(result)

    # Generate and print report
    report = generate_report(results, master_stats)
    print(report)

    # Collect all missing IDs
    all_missing = set()
    for r in results:
        all_missing.update(r.missing_from_master)

    if args.execute:
        print("\n" + "=" * 80)
        print("                         EXECUTING CLEANUP")
        print("=" * 80 + "\n")

        # Step 1: Add missing records
        if all_missing:
            print(f"Adding {len(all_missing)} missing records to master...")
            subset_paths = [data_dir / name for name in SUBSET_FILES]
            master_df = add_missing_records(master_df, subset_paths, all_missing, labels)
            master_df.to_csv(master_path, index=False)
            print(f"  Updated: {master_path} (now {len(master_df)} records)")
        else:
            print("No missing records to add.")

        # Step 2: Archive subset files
        print("\nArchiving subset files...")
        subset_paths = [data_dir / name for name in SUBSET_FILES]
        archived = archive_files(subset_paths, dry_run=False)

        # Step 3: Create manifest
        if archived:
            create_manifest(archived, len(master_df), len(all_missing))

        print("\nCleanup complete!")
        print(f"  Master file: {master_path} ({len(master_df)} records)")
        print(f"  Archived files: {len(archived)}")

    else:
        print("\n[DRY-RUN MODE] No changes made. Use --execute to apply changes.")
        if all_missing:
            print(f"  Would add {len(all_missing)} missing records to master")
        print(f"  Would archive {len([f for f in SUBSET_FILES if (data_dir / f).exists()])} files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
