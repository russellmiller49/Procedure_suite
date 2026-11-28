#!/usr/bin/env python3
# ruff: noqa: E402 -- Put the repository root on sys.path before importing it.
"""Select the physician anchor set and load it into the workbench for blinded review.

    python ops/tools/robotic_ebus_truth/anchor_set.py \\
        --truth-corpus data/ml_training/robotic_ebus_v1/corpus_truth_20261109 --count 50 --seed 7 \\
        --output data/knowledge/robotic_ebus_v1/anchor_set_20261109.json --seed-workbench

Half the notes come from the third-party corpus (validation and regression), half
from the truth-first corpus (validation), stratified by platform and, for truth
notes, by trap. Reviewed blind in the workbench (start a blinded draft; model
proposals stay hidden), the approved revisions are the anchor that checks whether
truth-first scores carry over to notes no generator wrote. Test splits are never
used. Each note becomes its own case under split "anchor".
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT)]

V2 = ROOT / "data/ml_training/robotic_ebus_v1/corpus_20260914_v2"


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def _stratified(rows: list[dict], count: int, key, rng: random.Random) -> list[dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[key(row)].append(row)
    for bucket in buckets.values():
        rng.shuffle(bucket)
    chosen, families = [], set()
    while len(chosen) < count and any(buckets.values()):
        for name in sorted(buckets):
            while buckets[name]:
                row = buckets[name].pop()
                if row["family_id"] not in families:  # one rendition per case
                    chosen.append(row)
                    families.add(row["family_id"])
                    break
            if len(chosen) == count:
                break
    return chosen


def select(truth_corpus: Path, count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    third_party = [
        {**r, "_source": V2.name}
        for r in _rows(V2 / "validation.jsonl") + _rows(V2 / "regression.jsonl")
    ]
    truth = [{**r, "_source": truth_corpus.name} for r in _rows(truth_corpus / "validation.jsonl")]
    picked = _stratified(third_party, count - count // 2, lambda r: r.get("platform") or "", rng)
    picked += _stratified(
        truth, count // 2, lambda r: (r.get("traps") or ["none"])[0] + r.get("platform", ""), rng
    )
    return [
        {
            "document_id": r["document_id"],
            "source": r["_source"],
            "split": r["split"],
            "platform": r.get("platform"),
            "traps": r.get("traps", []),
            "text_sha256": r["text_sha256"],
            "text": r["text"],
        }
        for r in picked
    ]


def seed_workbench(selection: list[dict]) -> int:
    from sqlalchemy import select

    from app.registry_workbench import service
    from app.registry_workbench.db import Case, session_factory

    created = 0
    with session_factory()() as db:
        for index, item in enumerate(selection, 1):
            label = f"anchor/{index:03d}-{item['document_id'][:8]}"
            if db.scalar(select(Case).where(Case.label == label)) is not None:
                continue
            case = service.create_case(
                db,
                label=label,
                source=f"anchor:{item['source']}",
                platform=item["platform"],
                split="anchor",
            )
            service.add_document(
                db,
                case,
                kind="procedure",
                text=item["text"],
                corpus_document_id=item["document_id"],
                variant="anchor",
            )
            created += 1
        db.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--truth-corpus", type=Path, required=True)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed-workbench", action="store_true")
    args = parser.parse_args()
    selection = select(args.truth_corpus, args.count, args.seed)
    args.output.write_text(
        json.dumps(
            {
                "seed": args.seed,
                "truth_corpus": args.truth_corpus.name,
                "review": "blinded",
                "documents": [{k: v for k, v in s.items() if k != "text"} for s in selection],
            },
            indent=2,
        )
        + "\n"
    )
    created = seed_workbench(selection) if args.seed_workbench else 0
    print(
        json.dumps(
            {
                "selected": len(selection),
                "workbench_cases_created": created,
                "by_source": {
                    s: sum(x["source"] == s for x in selection)
                    for s in {x["source"] for x in selection}
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
