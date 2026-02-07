#!/usr/bin/env python3
"""Generate a registry label overlap/contradiction report for targeted annotation.

Input: one or more registry CSVs (train/val/test)
Output: JSON report with:
- per-label positive counts
- top pairwise co-occurrences (counts + rates)
- constraint-driven contradictions / normalization events

This is intended to drive targeted Prodigy batches for semantic overlap areas
(e.g., BAL vs bronchial wash, rigid vs debulking).
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml.lib.ml_coder.registry_label_constraints import apply_label_constraints, registry_consistency_flags
from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id

_RE_BAL = re.compile(r"\b(bal|bronchoalveolar\s+lavage)\b", flags=re.IGNORECASE)
_RE_WASH = re.compile(r"\bbronchial\s+wash(?:ing)?s?\b", flags=re.IGNORECASE)


def _first_span(regex: re.Pattern[str], text: str) -> tuple[int, int] | None:
    m = regex.search(text or "")
    if not m:
        return None
    return (int(m.start()), int(m.end()))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--csv",
        type=Path,
        action="append",
        default=[],
        help="Registry CSV to analyze (repeatable). Default: registry_train.csv only.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("reports/registry_label_overlap.json"),
        help="Output JSON report path",
    )
    p.add_argument("--top-k", type=int, default=200, help="Top co-occurring label pairs to include")
    p.add_argument("--max-examples", type=int, default=50, help="Max example rows per issue type")
    return p.parse_args(argv)


def _load_csv(path: Path, labels: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        return df
    if "note_text" not in df.columns:
        raise ValueError(f"Missing note_text in {path}")

    for label in labels:
        if label not in df.columns:
            df[label] = 0
        df[label] = pd.to_numeric(df[label], errors="coerce").fillna(0).clip(0, 1).astype(int)
    return df


def _pairwise_stats(y: np.ndarray, labels: list[str], top_k: int) -> list[dict[str, Any]]:
    if y.size == 0:
        return []
    counts = y.sum(axis=0).astype(int)
    co = (y.T @ y).astype(int)

    pairs: list[dict[str, Any]] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            c = int(co[i, j])
            if c == 0:
                continue
            denom = int(counts[i] + counts[j] - c)
            jaccard = float(c / denom) if denom else 0.0
            p_j_given_i = float(c / counts[i]) if counts[i] else 0.0
            p_i_given_j = float(c / counts[j]) if counts[j] else 0.0
            pairs.append(
                {
                    "a": labels[i],
                    "b": labels[j],
                    "co_count": c,
                    "count_a": int(counts[i]),
                    "count_b": int(counts[j]),
                    "jaccard": jaccard,
                    "p_b_given_a": p_j_given_i,
                    "p_a_given_b": p_i_given_j,
                }
            )

    pairs.sort(key=lambda d: d["co_count"], reverse=True)
    return pairs[: max(0, int(top_k))]


@dataclass
class IssueCollector:
    max_examples: int
    counts: dict[str, int]
    examples: dict[str, list[dict[str, Any]]]

    def __init__(self, max_examples: int):
        self.max_examples = max_examples
        self.counts = {}
        self.examples = {}

    def add(self, issue_type: str, example: dict[str, Any]) -> None:
        self.counts[issue_type] = int(self.counts.get(issue_type, 0)) + 1
        if issue_type not in self.examples:
            self.examples[issue_type] = []
        if len(self.examples[issue_type]) < self.max_examples:
            self.examples[issue_type].append(example)


def _analyze_constraints(df: pd.DataFrame, *, source: str, max_examples: int) -> dict[str, Any]:
    issues = IssueCollector(max_examples=max_examples)
    if df.empty:
        return {"counts": {}, "examples": {}}

    for idx, row in df.iterrows():
        text = str(row.get("note_text") or "")
        raw = {
            "note_text": text,
            "bal": int(row.get("bal", 0)),
            "bronchial_wash": int(row.get("bronchial_wash", 0)),
            "transbronchial_cryobiopsy": int(row.get("transbronchial_cryobiopsy", 0)),
            "transbronchial_biopsy": int(row.get("transbronchial_biopsy", 0)),
            "rigid_bronchoscopy": int(row.get("rigid_bronchoscopy", 0)),
            "tumor_debulking_non_thermal": int(row.get("tumor_debulking_non_thermal", 0)),
        }
        normalized = dict(raw)
        apply_label_constraints(normalized, note_text=text, inplace=True)

        eid = compute_encounter_id(text)

        # Record normalization events (where constraints changed labels).
        if raw["bal"] != normalized["bal"] or raw["bronchial_wash"] != normalized["bronchial_wash"]:
            issues.add(
                "bal_vs_bronchial_wash_normalized",
                {
                    "encounter_id": eid,
                    "source": source,
                    "row_index": int(idx),
                    "bal_raw": raw["bal"],
                    "wash_raw": raw["bronchial_wash"],
                    "bal_norm": normalized["bal"],
                    "wash_norm": normalized["bronchial_wash"],
                    "bal_span": _first_span(_RE_BAL, text),
                    "wash_span": _first_span(_RE_WASH, text),
                    "note_len": len(text),
                },
            )
        elif raw["bal"] == 1 and raw["bronchial_wash"] == 1:
            issues.add(
                "bal_and_bronchial_wash_overlap",
                {
                    "encounter_id": eid,
                    "source": source,
                    "row_index": int(idx),
                    "bal_span": _first_span(_RE_BAL, text),
                    "wash_span": _first_span(_RE_WASH, text),
                    "note_len": len(text),
                },
            )

        if raw["transbronchial_cryobiopsy"] == 1 and raw["transbronchial_biopsy"] == 0:
            issues.add(
                "cryo_without_tbb",
                {
                    "encounter_id": eid,
                    "source": source,
                    "row_index": int(idx),
                    "note_len": len(text),
                },
            )

        flags = registry_consistency_flags(raw)
        if flags.get("rigid_without_debulking"):
            issues.add("rigid_without_debulking", {"encounter_id": eid, "source": source, "row_index": int(idx)})
        if flags.get("debulking_without_rigid"):
            issues.add("debulking_without_rigid", {"encounter_id": eid, "source": source, "row_index": int(idx)})

    return {"counts": issues.counts, "examples": issues.examples}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    csvs = args.csv if args.csv else [Path("data/ml_training/registry_train.csv")]
    labels = list(REGISTRY_LABELS)

    all_rows = 0
    label_counts: dict[str, int] = {label: 0 for label in labels}
    pairwise: list[dict[str, Any]] = []
    constraint_counts: dict[str, int] = {}
    constraint_examples: dict[str, list[dict[str, Any]]] = {}

    for csv_path in csvs:
        df = _load_csv(csv_path, labels)
        if df.empty:
            continue
        all_rows += int(len(df))

        y = df[labels].to_numpy(dtype=int)
        for label, c in zip(labels, y.sum(axis=0).tolist()):
            label_counts[label] += int(c)

        pairwise.extend(_pairwise_stats(y, labels, top_k=args.top_k))

        constraint_report = _analyze_constraints(df, source=str(csv_path), max_examples=args.max_examples)
        for k, v in constraint_report["counts"].items():
            constraint_counts[k] = int(constraint_counts.get(k, 0)) + int(v)
        for k, examples in constraint_report["examples"].items():
            constraint_examples.setdefault(k, [])
            remaining = args.max_examples - len(constraint_examples[k])
            if remaining > 0:
                constraint_examples[k].extend(list(examples)[:remaining])

    # De-duplicate pairwise list across multiple CSVs by (a,b) while summing counts.
    merged_pairs: dict[tuple[str, str], dict[str, Any]] = {}
    for item in pairwise:
        key = (item["a"], item["b"])
        if key not in merged_pairs:
            merged_pairs[key] = dict(item)
            continue
        merged_pairs[key]["co_count"] += int(item["co_count"])
        merged_pairs[key]["count_a"] += int(item["count_a"])
        merged_pairs[key]["count_b"] += int(item["count_b"])

    top_pairs = sorted(merged_pairs.values(), key=lambda d: d["co_count"], reverse=True)[: args.top_k]

    out = {
        "inputs": [str(p) for p in csvs],
        "n_rows": int(all_rows),
        "labels": labels,
        "label_counts": label_counts,
        "top_pairs": top_pairs,
        "constraint_counts": constraint_counts,
        "constraint_examples": constraint_examples,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"Wrote report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

