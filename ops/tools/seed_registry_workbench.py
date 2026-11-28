#!/usr/bin/env python3
# ruff: noqa: E402 -- Import the app after putting the repo root on sys.path.
"""Seed the synthetic registry workbench from the frozen robotic/EBUS corpus.

One case per case family; each rendition (clean, messy, PDF text) becomes a
document. Train, validation and regression load by default. Test documents are
already exposed and load only with --include-test --exposure-ack; viewing them
in the workbench is recorded. Re-running is idempotent.

    python ops/tools/seed_registry_workbench.py --splits validation --limit 20
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]

from sqlalchemy import func, select

from app.registry_workbench import service
from app.registry_workbench.db import Case, Document, database_url, session_factory

CORPUS = ROOT / "data/ml_training/robotic_ebus_v1/corpus_20260914_v2"


def _variant(row: dict) -> str:
    source = " ".join(str(s) for s in row.get("sources") or []).lower()
    for name in ("messy", "clean", "pdf", "zip"):
        if name in source:
            return name
    return "text"


def seed(splits: list[str], *, limit: int | None = None) -> dict[str, int]:
    families: dict[str, list[dict]] = defaultdict(list)
    for split in splits:
        for line in (CORPUS / f"{split}.jsonl").read_text().splitlines():
            row = json.loads(line)
            families[row["family_id"]].append(row)
    selected = sorted(families)[:limit] if limit else sorted(families)
    counts = {"families": len(selected), "cases_created": 0}
    with session_factory()() as db:
        documents_before = db.scalar(select(func.count()).select_from(Document))
        for family_id in selected:
            rows = families[family_id]
            first = rows[0]
            anchor = (first.get("family_anchor") or family_id[:12]).removeprefix("case:")
            label = f"{first['split']}/{anchor}"
            case = db.scalar(select(Case).where(Case.family_id == family_id))
            if case is None:
                case = service.create_case(
                    db,
                    label=label,
                    source=f"corpus:{CORPUS.name}",
                    family_id=family_id,
                    platform=first.get("platform"),
                    split=first["split"],
                )
                counts["cases_created"] += 1
            for row in rows:
                service.add_document(
                    db,
                    case,
                    kind="procedure",
                    text=row["text"],
                    corpus_document_id=row["document_id"],
                    variant=_variant(row),
                    exposure="exposed_test" if row["split"] == "test" else "development",
                )
            db.commit()
        counts["documents_added"] = (
            db.scalar(select(func.count()).select_from(Document)) - documents_before
        )
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train", "validation", "regression"],
        choices=["train", "validation", "regression", "test"],
    )
    parser.add_argument("--limit", type=int, help="Maximum number of case families")
    parser.add_argument("--include-test", action="store_true")
    parser.add_argument("--exposure-ack", action="store_true")
    args = parser.parse_args()
    if "test" in args.splits and not (args.include_test and args.exposure_ack):
        raise SystemExit("test split requires --include-test --exposure-ack")
    counts = seed(args.splits, limit=args.limit)
    print(json.dumps({"database": database_url(), **counts}, indent=2))


if __name__ == "__main__":
    main()
