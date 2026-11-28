#!/usr/bin/env python3
# ruff: noqa: E402 -- Put the repository root on sys.path before importing it.
"""Apply the pre-set model selection rule to registry extractor eval outputs.

    python ops/tools/select_registry_llm.py \\
        --corpus data/ml_training/robotic_ebus_v1/corpus_truth_20261125 --split validation \\
        --inputs outputs/robotic_ebus_llm_validation/*.json \\
        --output reports/robotic_ebus_llm_validation_selection.json

Inputs are ``eval_registry_llm.py --truth-corpus ... --keep-proposals`` outputs. The
rule was fixed before any validation result was opened (plan of 2026-11-25):

- usable results: at most one of the documents without a usable final result
  (a degraded, unsupported or failed answer is not usable);
- observed field precision at least 0.975;
- overall recall at least 0.25 above the rules engine on the same notes, and
  recall at least 0.70 for sampling acquisitions, specimens and their links;
- winner: highest recall among arms passing every gate; arms within 0.02 recall
  are a tie, broken by p95 latency and then cost per note.

Clinically consequential errors are listed per arm for reading, not gated:
a surveyed station recorded as sampled, a link to the wrong parent row, a
component recorded as started that the answer key says was not, and a
tool-in-lesion claim the key does not have. Intervals are note-level
bootstraps (fields within a note are correlated) and are reported, not gated.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]

from app.registry_workbench.scoring import aggregate, score_document

PRECISION_GATE = 0.975
RECALL_GAIN_GATE = 0.25
ENTITY_RECALL_GATE = 0.70
GATED_ENTITIES = ("sampling_acquisitions", "specimens", "sampling_specimen_links")
TIE_MARGIN = 0.02
STARTED = {"performed", "attempted"}
RULES_ARM = "deterministic"


def _sampled(revision: dict | None) -> set[str]:
    return {
        s["iaslc_station"]
        for s in (revision or {}).get("station_surveys") or []
        if s.get("station_sampled") is True
    }


def _started(revision: dict | None) -> set[str]:
    return {
        p["category"]
        for p in (revision or {}).get("procedures") or []
        if p.get("performance") in STARTED
    }


def _til(revision: dict | None) -> int:
    return sum(
        1
        for e in (revision or {}).get("localization_events") or []
        if e.get("tool_lesion_relationship") == "TIL"
    )


def _bootstrap(scores, statistic, rounds: int = 2000, seed: int = 20261125):
    rng = random.Random(seed)
    values = []
    for _ in range(rounds):
        sample = [scores[rng.randrange(len(scores))] for _ in scores]
        value = statistic(aggregate(sample, min_support=1)["overall"])
        if value is not None:
            values.append(value)
    values.sort()
    if not values:
        return None
    return [
        round(values[int(0.025 * len(values))], 4),
        round(values[int(0.975 * len(values)) - 1], 4),
    ]


def evaluate(name: str, arm: dict, gold: dict[str, dict]) -> dict:
    results = arm["results"]
    scores, consequential = (
        [],
        {
            "surveyed_station_recorded_as_sampled": [],
            "link_to_wrong_parent": [],
            "component_started_that_key_says_was_not": [],
            "tool_in_lesion_beyond_key": [],
        },
    )
    unusable = []
    for doc, result in results.items():
        proposal = result.get("proposal")
        score = score_document(gold[doc], proposal)
        scores.append(score)
        if name != RULES_ARM and result.get("status") != "proposed":
            unusable.append({"document_id": doc, "status": result.get("status")})
        extra = sorted(_sampled(proposal) - _sampled(gold[doc]))
        if extra:
            consequential["surveyed_station_recorded_as_sampled"].append(
                {"document_id": doc, "stations": extra}
            )
        wrong_links = score.foreign_keys[1] - score.foreign_keys[0]
        if proposal and wrong_links:
            consequential["link_to_wrong_parent"].append({"document_id": doc, "count": wrong_links})
        started = sorted(_started(proposal) - _started(gold[doc]))
        if started:
            consequential["component_started_that_key_says_was_not"].append(
                {"document_id": doc, "components": started}
            )
        if _til(proposal) > _til(gold[doc]):
            consequential["tool_in_lesion_beyond_key"].append({"document_id": doc})
    total = aggregate(scores, min_support=1)
    overall, entities = total["overall"], total["entities"]
    mechanics = arm.get("mechanics") or {}
    latency = mechanics.get("latency_s") or {}
    return {
        "documents": len(results),
        "usable": len(results) - len(unusable),
        "unusable": unusable,
        "outcomes": mechanics.get("outcomes"),
        "tp": overall["tp"],
        "fp": overall["fp"],
        "fn": overall["fn"],
        "precision": round(overall["precision"], 4) if overall["precision"] is not None else None,
        "recall": round(overall["recall"], 4) if overall["recall"] is not None else None,
        "precision_interval_95": _bootstrap(scores, lambda o: o["precision"]),
        "recall_interval_95": _bootstrap(scores, lambda o: o["recall"]),
        "links_correct": total["foreign_key_accuracy"]["correct"],
        "links_total": total["foreign_key_accuracy"]["total"],
        "entity_recall": {
            k: (
                round(entities[k]["recall"], 4)
                if entities.get(k, {}).get("recall") is not None
                else None
            )
            for k in GATED_ENTITIES
        },
        "entity_precision": {
            k: (
                round(entities[k]["precision"], 4)
                if entities.get(k, {}).get("precision") is not None
                else None
            )
            for k in GATED_ENTITIES
        },
        "top_wrong_fills": [
            [k, v["fp"]]
            for k, v in sorted(total["fields"].items(), key=lambda kv: -kv[1]["fp"])[:8]
            if v["fp"]
        ],
        "top_misses": [
            [k, v["fn"]]
            for k, v in sorted(total["fields"].items(), key=lambda kv: -kv[1]["fn"])[:8]
            if v["fn"]
        ],
        "traps": {
            k: {
                "documents": v.get("documents"),
                "precision": (v.get("overall") or {}).get("precision"),
                "recall": (v.get("overall") or {}).get("recall"),
            }
            for k, v in ((arm.get("contract") or {}).get("traps") or {}).items()
        },
        "consequential": {k: v for k, v in consequential.items()},
        "consequential_counts": {k: len(v) for k, v in consequential.items()},
        "cost_usd_total": mechanics.get("cost_usd_total"),
        "cost_usd_per_document": mechanics.get("cost_usd_per_document"),
        "latency_mean_s": latency.get("mean"),
        "latency_p50_s": latency.get("p50"),
        "latency_p95_s": latency.get("p95"),
        "repair_rate": mechanics.get("repair_rate"),
        "fallback_rate": mechanics.get("fallback_rate"),
    }


def select(arms: dict[str, dict]) -> dict:
    rules = arms.get(RULES_ARM)
    gates = {}
    for name, arm in arms.items():
        if name == RULES_ARM:
            continue
        checks = {
            "usable_results": arm["usable"] >= arm["documents"] - 1,
            "precision": arm["precision"] is not None and arm["precision"] >= PRECISION_GATE,
            "recall_gain_over_rules": rules is not None
            and arm["recall"] is not None
            and arm["recall"] - rules["recall"] >= RECALL_GAIN_GATE,
            "entity_recall": all(
                (arm["entity_recall"].get(k) or 0) >= ENTITY_RECALL_GATE for k in GATED_ENTITIES
            ),
        }
        gates[name] = {**checks, "passes": all(checks.values())}
    passing = [n for n, g in gates.items() if g["passes"]]
    winner, tied = None, []
    if passing:
        best = max(arms[n]["recall"] for n in passing)
        tied = sorted(n for n in passing if best - arms[n]["recall"] <= TIE_MARGIN)
        winner = min(
            tied,
            key=lambda n: (
                arms[n]["latency_p95_s"] if arms[n]["latency_p95_s"] is not None else float("inf"),
                arms[n]["cost_usd_per_document"] or 0.0,
            ),
        )
        if len(tied) == 1:
            winner = tied[0]
    return {"gates": gates, "passing": passing, "tied_on_recall": tied, "winner": winner}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--split", default="validation", choices=["train", "validation"])
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    gold = {
        row["document_id"]: row["revision"]
        for row in map(json.loads, (args.corpus / "gold" / f"{args.split}.gold.jsonl").open())
    }
    arms: dict[str, dict] = {}
    for path in args.inputs:
        data = json.loads(path.read_text())
        if args.split not in (data.get("splits") or [args.split]):
            raise SystemExit(f"{path}: not a {args.split} run")
        for name, arm in data["arms"].items():
            if name in arms:
                raise SystemExit(f"{name} appears in more than one input")
            missing = set(arm["results"]) - set(gold)
            if missing:
                raise SystemExit(f"{name}: documents outside {args.split} gold")
            arms[name] = evaluate(name, arm, gold)
    documents = {a["documents"] for a in arms.values()}
    if len(documents) != 1:
        raise SystemExit(f"arms ran on different numbers of documents: {documents}")
    report = {
        "corpus": args.corpus.name,
        "split": args.split,
        "rule": {
            "usable_results": "at most one unusable",
            "precision_min": PRECISION_GATE,
            "recall_gain_over_rules_min": RECALL_GAIN_GATE,
            "entity_recall_min": {k: ENTITY_RECALL_GATE for k in GATED_ENTITIES},
            "tie_margin": TIE_MARGIN,
            "tie_break": ["latency_p95_s", "cost_usd_per_document"],
        },
        "arms": arms,
        "selection": select(arms),
    }
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    for name, arm in sorted(arms.items(), key=lambda kv: -(kv[1]["recall"] or 0)):
        gate = report["selection"]["gates"].get(name, {})
        print(
            f"{name:27s} usable {arm['usable']}/{arm['documents']}  P {arm['precision']}  "
            f"R {arm['recall']}  links {arm['links_correct']}/{arm['links_total']}  "
            f"entity recall {arm['entity_recall']}  p95 {arm['latency_p95_s']}  "
            f"$/note {arm['cost_usd_per_document']}  "
            + (
                "PASS"
                if gate.get("passes")
                else (
                    "rules"
                    if name == RULES_ARM
                    else "fail " + ",".join(k for k, v in gate.items() if k != "passes" and not v)
                )
            )
        )
    print(
        "winner:", report["selection"]["winner"], "| tied:", report["selection"]["tied_on_recall"]
    )


if __name__ == "__main__":
    main()
