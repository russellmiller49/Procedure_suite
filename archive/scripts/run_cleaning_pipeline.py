#!/usr/bin/env python3
"""
Run the registry cleaning pipeline over a JSONL notes file.

Usage:
    python scripts/run_cleaning_pipeline.py \
        --notes data/synthetic/synthetic_notes_with_registry.jsonl \
        --kb data/knowledge/ip_coding_billing_v2_8.json \
        --schema data/knowledge/IP_Registry_Enhanced_v2.json \
        --out-json autopatches/patches.json \
        --out-csv reports/errors.csv \
        --apply-minimal-fixes
"""

import argparse
from pathlib import Path

from modules.registry_cleaning.pipeline import run_pipeline


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", required=True, help="Path to JSONL notes file.")
    ap.add_argument("--kb", required=True, help="Path to coding KB JSON.")
    ap.add_argument("--schema", required=True, help="Path to registry JSON schema.")
    ap.add_argument("--out-json", required=True, help="Where to write patch JSON.")
    ap.add_argument("--out-csv", required=True, help="Where to write error CSV.")
    ap.add_argument(
        "--apply-minimal-fixes",
        action="store_true",
        help="If set, apply safe/minimal patches automatically.",
    )
    args = ap.parse_args()

    run_pipeline(
        notes_path=Path(args.notes),
        kb_path=Path(args.kb),
        schema_path=Path(args.schema),
        out_json=Path(args.out_json),
        out_csv=Path(args.out_csv),
        apply_minimal_fixes=bool(args.apply_minimal_fixes),
    )

    print("Cleaning pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
