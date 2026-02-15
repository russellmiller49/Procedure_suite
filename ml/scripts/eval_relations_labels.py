#!/usr/bin/env python3
"""Evaluate labeled relation edges exported from Prodigy (Phase 8).

This script summarizes accept/reject outcomes by:
- edge_source (merged / heuristic / ml)
- relation type
- disagreement keys (where merged and heuristic propose different targets)

Important:
- This is NOT a recall calculation. It measures accuracy on the reviewed candidate edges.
- Input should come from `ml/scripts/prodigy_export_relations.py`.
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid JSON at %s:%d", path, line_num)
                continue
            if isinstance(obj, dict):
                yield obj


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _edge_fields(row: dict[str, Any]) -> tuple[str, str, str, str]:
    edge = _as_dict(row.get("edge"))
    case_id = str(row.get("case_id") or "").strip()
    entity_id = str(edge.get("entity_id") or "").strip()
    relation = str(edge.get("relation") or row.get("relation") or "").strip()
    linked_to_id = str(edge.get("linked_to_id") or "").strip()
    return case_id, entity_id, relation, linked_to_id


def _safe_rate(num: int, denom: int) -> float:
    return float(num) / float(denom) if denom else 0.0


def evaluate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [r for r in rows if r.get("label") in (0, 1)]

    counts_by_source: dict[str, dict[str, int]] = defaultdict(lambda: {"accepted": 0, "rejected": 0})
    counts_by_relation: dict[str, dict[str, int]] = defaultdict(lambda: {"accepted": 0, "rejected": 0})
    counts_by_source_relation: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"accepted": 0, "rejected": 0}
    )

    # Group by (case_id, entity_id, relation) to analyze disagreements.
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for r in labeled:
        edge_source = str(r.get("edge_source") or "").strip() or "unknown"
        relation = str(r.get("relation") or _as_dict(r.get("edge")).get("relation") or "").strip() or "unknown"
        label = int(r.get("label"))

        if label == 1:
            counts_by_source[edge_source]["accepted"] += 1
            counts_by_relation[relation]["accepted"] += 1
            counts_by_source_relation[(edge_source, relation)]["accepted"] += 1
        else:
            counts_by_source[edge_source]["rejected"] += 1
            counts_by_relation[relation]["rejected"] += 1
            counts_by_source_relation[(edge_source, relation)]["rejected"] += 1

        case_id, entity_id, rel, _linked_to_id = _edge_fields(r)
        if case_id and entity_id and rel:
            groups[(case_id, entity_id, rel)].append(r)

    disagreements_total = 0
    merged_wins = 0
    heuristic_wins = 0
    both_accepted = 0
    neither_accepted = 0

    for _k, rows_k in groups.items():
        merged = [r for r in rows_k if str(r.get("edge_source") or "").strip() == "merged"]
        heur = [r for r in rows_k if str(r.get("edge_source") or "").strip() == "heuristic"]
        if not merged or not heur:
            continue

        merged_targets = { _edge_fields(r)[3] for r in merged if _edge_fields(r)[3] }
        heur_targets = { _edge_fields(r)[3] for r in heur if _edge_fields(r)[3] }
        if not merged_targets or not heur_targets:
            continue
        if merged_targets == heur_targets:
            continue

        disagreements_total += 1
        merged_accept = any(int(r.get("label")) == 1 for r in merged)
        heur_accept = any(int(r.get("label")) == 1 for r in heur)
        if merged_accept and not heur_accept:
            merged_wins += 1
        elif heur_accept and not merged_accept:
            heuristic_wins += 1
        elif merged_accept and heur_accept:
            both_accepted += 1
        else:
            neither_accepted += 1

    def _with_rates(counter: dict[str, dict[str, int]]) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for key, v in sorted(counter.items(), key=lambda kv: kv[0]):
            acc = int(v.get("accepted", 0))
            rej = int(v.get("rejected", 0))
            total = acc + rej
            out[key] = {
                "accepted": acc,
                "rejected": rej,
                "total": total,
                "accept_rate": _safe_rate(acc, total),
            }
        return out

    by_source = _with_rates(counts_by_source)
    by_relation = _with_rates(counts_by_relation)

    by_source_relation: dict[str, dict[str, Any]] = {}
    for (src, rel), v in sorted(counts_by_source_relation.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        acc = int(v.get("accepted", 0))
        rej = int(v.get("rejected", 0))
        total = acc + rej
        by_source_relation[f"{src}::{rel}"] = {
            "edge_source": src,
            "relation": rel,
            "accepted": acc,
            "rejected": rej,
            "total": total,
            "accept_rate": _safe_rate(acc, total),
        }

    return {
        "edges_total": len(rows),
        "edges_labeled": len(labeled),
        "by_source": by_source,
        "by_relation": by_relation,
        "by_source_relation": by_source_relation,
        "disagreements": {
            "keys_total": disagreements_total,
            "merged_wins": merged_wins,
            "heuristic_wins": heuristic_wins,
            "both_accepted": both_accepted,
            "neither_accepted": neither_accepted,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-jsonl", type=Path, required=True, help="Labeled edges JSONL from Prodigy export")
    p.add_argument("--output-json", type=Path, default=None, help="Optional output JSON report path")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    rows = list(iter_jsonl(args.input_jsonl))
    report = evaluate(rows)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

