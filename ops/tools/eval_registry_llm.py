#!/usr/bin/env python3
# ruff: noqa: E402 -- Import the bounded packages from packages/*/src.
"""Compare registry extractors on the synthetic robotic/EBUS corpus.

Arms: ``deterministic`` (the vendored focused engine) and
``claude:<opus|sonnet|haiku>:<effort>``. Claude arms run online (one request at a
time, refusal fallbacks on) or through the Message Batches API (half price,
second batch for repairs).

Scores:
  - gold: the 10 continuity fact types on the reviewed selection
    (reviewed_eval_selection.json). Those documents are already exposed, so this
    is engineering regression only, never qualification.
  - silver: agreement with generator metadata (lobe, size, bronchus sign,
    sampled / observed-only stations, immediate safety). Metadata may describe
    details the note never states, so silver recall is a lower bound.
  - mechanics: proposal status, validator pass, repairs, anchoring, cost, latency.

Every document is synthetic; requests run under a declared synthetic egress context.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]
from ip_registry_contracts.models import ClinicalRevision, ExtractionRequest, approval_errors
from ip_registry_engine.engine import LocalDeterministicProvider

from app.common.anthropic_client import (
    ClaudeClient,
    ClaudeSettings,
    load_api_key_from_dotenv,
    result_from_message,
)
from app.common.llm_egress import egress_context
from app.llm_extraction import batch as batches
from app.registry_workbench.extraction.assembler import VALIDATION_EVENT_DATE
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.extraction.prompt import prompt_digest
from app.registry_workbench.scoring import aggregate, score_document
from ops.tools.eval_robotic_ebus import focused_facts, metrics

CORPUS = ROOT / "data/ml_training/robotic_ebus_v1/corpus_20260914_v2"
GOLD = ROOT / "data/knowledge/robotic_ebus_v1/reviewed_eval_selection.json"
MODELS = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}
SILVER_FIELDS = (
    "target.lobe",
    "target.max_diameter_mm",
    "target.bronchus_sign",
    "ebus.sampled_station",
    "ebus.observed_not_sampled",
    "safety.immediate",
)


def load_documents(splits, limit=None, platform=None, corpus=CORPUS):
    rows = []
    for split in splits:
        for line in (corpus / f"{split}.jsonl").read_text().splitlines():
            row = json.loads(line)
            if platform and row.get("platform") != platform:
                continue
            rows.append(row)
    return rows[:limit] if limit else rows


def silver_facts(meta):
    """Expected facts, only for fields the generator metadata actually describes."""
    out = {}
    lobe = meta.get("lobe")
    if lobe:
        out["target.lobe"] = {lobe}
        if isinstance(meta.get("lesion_size_mm"), (int, float)):
            out["target.max_diameter_mm"] = {f"{lobe}:{meta['lesion_size_mm']:g}"}
        if meta.get("bronchus_sign") in {"positive", "negative"}:
            out["target.bronchus_sign"] = {
                f"{lobe}:{str(meta['bronchus_sign'] == 'positive').lower()}"
            }
    if "sampled_stations" in meta:
        out["ebus.sampled_station"] = {str(s) for s in meta["sampled_stations"] or []}
    if "visualized_not_sampled" in meta:
        out["ebus.observed_not_sampled"] = {str(s) for s in meta["visualized_not_sampled"] or []}
    complication = (meta.get("complication") or "").strip().lower()
    if complication:
        out["safety.immediate"] = {"absent" if complication in {"none", "no"} else "present"}
    return out


def parse_arm(label):
    if label == "deterministic":
        return {"label": label, "kind": "deterministic"}
    kind, model, effort = label.split(":")
    if kind != "claude" or model not in MODELS:
        raise SystemExit(f"unknown arm {label!r}")
    return {"label": label, "kind": "claude", "model": MODELS[model], "effort": effort}


def request_for(row):
    return ExtractionRequest(
        job_id=uuid4(),
        source_document_id=uuid4(),
        source_digest=row["text_sha256"],
        text=row["text"],
        kind="procedure",
    )


def contract_check(proposal):
    """Validate any arm's proposal the same way: (valid, approval errors)."""
    if not proposal:
        return False, []
    try:
        revision = ClinicalRevision.model_validate(
            {**proposal, "event_date": VALIDATION_EVENT_DATE}
        )
    except ValueError:
        return False, []
    return True, approval_errors(revision)


def summarize(response):
    if isinstance(response, Exception):
        return {
            "status": "error",
            "error": f"{type(response).__name__}: {response}"[:300],
            "facts": {},
        }
    obs = response.observations
    inference = obs.get("inference") or {}
    valid, approval = contract_check(obs.get("proposal"))
    return {
        "status": response.status,
        "warnings": response.warnings,
        "proposal": obs.get("proposal"),
        "facts": {
            k: sorted(v) for k, v in focused_facts(obs if obs.get("proposal") else {}).items()
        },
        "contract_valid": valid,
        "approval_errors": approval,
        "unresolved": len(obs.get("unresolved_mentions") or []),
        "assembly_stats": obs.get("assembly_stats") or {},
        "repair_used": inference.get("repair_used", False),
        "fallback_used": inference.get("fallback_used", False),
        "cost_usd": inference.get("cost_usd"),
        "latency_s": inference.get("latency_s"),
    }


def run_online(arm, rows, provider, source=CORPUS.name):
    results = {}
    for index, row in enumerate(rows, 1):
        try:
            response = (
                provider.extract(request_for(row))
                if arm["kind"] == "deterministic"
                else _extract_synthetic(provider, row, source)
            )
        except Exception as exc:  # recorded per document; the run continues
            response = exc
        results[row["document_id"]] = summarize(response)
        print(
            f"[{arm['label']}] {index}/{len(rows)} {row['document_id']} {results[row['document_id']]['status']}",
            file=sys.stderr,
        )
    return results


def _extract_synthetic(provider, row, source):
    with egress_context("synthetic", source=f"corpus:{source}"):
        return provider.extract(request_for(row))


def run_batch(arm, rows, provider, poll_seconds, source=CORPUS.name):
    requests = {f"d{i}": (row, request_for(row)) for i, row in enumerate(rows)}
    with egress_context("synthetic", source=f"corpus:{source}"):
        sdk = provider.client.sdk
        batch_id = batches.submit(
            sdk, ((cid, provider.build_params(req)) for cid, (_, req) in requests.items())
        )
        print(
            f"[{arm['label']}] batch {batch_id} submitted ({len(requests)} requests)",
            file=sys.stderr,
        )
        batches.wait(
            sdk,
            batch_id,
            poll_seconds=poll_seconds,
            on_poll=lambda b: print(f"  {b.processing_status} {b.request_counts}", file=sys.stderr),
        )
        messages, errors = batches.collect(sdk, batch_id)
        model = provider.client.settings.model
        repairs = {}
        for cid, message in messages.items():
            _, req = requests[cid]
            first = result_from_message(message, requested_model=model, batch=True)
            _, repair_errors = provider.needs_repair(req, first)
            if repair_errors:
                repairs[cid] = provider.build_params(
                    req, previous=first.parsed, errors=repair_errors
                )
        repair_messages = {}
        if repairs:
            repair_id = batches.submit(sdk, repairs.items())
            print(
                f"[{arm['label']}] repair batch {repair_id} submitted ({len(repairs)})",
                file=sys.stderr,
            )
            batches.wait(sdk, repair_id, poll_seconds=poll_seconds)
            repair_messages, _ = batches.collect(sdk, repair_id)
    results = {}
    for cid, (row, req) in requests.items():
        if cid in messages:
            response = provider.response_from_batch(
                req, messages[cid], repair_message_obj=repair_messages.get(cid)
            )
        else:
            response = RuntimeError(f"batch item {errors.get(cid, 'missing')}")
        results[row["document_id"]] = summarize(response)
    return results


def score(results, references, fields, *, known_only=False):
    aggregate = defaultdict(lambda: [0, 0, 0])
    for doc_id, expected in references.items():
        actual = results.get(doc_id, {}).get("facts", {})
        for field in fields:
            if known_only and field not in expected:
                continue
            want, got = set(expected.get(field, [])), set(actual.get(field, []))
            counts = (len(want & got), len(got - want), len(want - got))
            for key in ("overall", "field:" + field):
                aggregate[key] = [a + b for a, b in zip(aggregate[key], counts, strict=True)]
    return {key: metrics(*value) for key, value in sorted(aggregate.items())}


def mechanics(results):
    values = list(results.values())
    n = len(values) or 1
    costs = [v["cost_usd"] for v in values if v.get("cost_usd") is not None]
    statuses = defaultdict(int)
    for v in values:
        statuses[v["status"]] += 1
    stats = defaultdict(int)
    for v in values:
        for key, count in (v.get("assembly_stats") or {}).items():
            stats[key] += count
    return {
        "documents": len(values),
        "status": dict(statuses),
        "contract_valid_rate": sum(v.get("contract_valid", False) for v in values) / n,
        "approvable_rate": sum(
            v.get("contract_valid", False) and not v.get("approval_errors") for v in values
        )
        / n,
        "repair_rate": sum(v.get("repair_used", False) for v in values) / n,
        "fallback_rate": sum(v.get("fallback_used", False) for v in values) / n,
        "fact_anchor_rate": (
            1 - stats["facts_unanchored"] / stats["facts"] if stats.get("facts") else None
        ),
        "assembly_stats": dict(stats),
        "cost_usd_total": round(sum(costs), 4) if costs else None,
        "cost_usd_per_document": round(sum(costs) / len(costs), 5) if costs else None,
    }


def contract_scores(results, gold_revisions, traps):
    """Full-contract scores against truth-first gold, overall and per trap."""
    scored = {d: score_document(gold_revisions[d], results.get(d, {}).get("proposal")) for d in gold_revisions}
    by_trap = {}
    for trap in sorted({t for ts in traps.values() for t in ts}):
        members = [scored[d] for d in scored if trap in traps.get(d, [])]
        report = aggregate(members)
        by_trap[trap] = {"documents": len(members), "overall": report["overall"], "rows": report["rows"]}
    return {**aggregate(list(scored.values())), "traps": by_trap}


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--arms", nargs="+", default=["deterministic", "claude:opus:medium"])
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["validation"],
        choices=["train", "validation", "regression", "test"],
    )
    parser.add_argument(
        "--gold",
        action="store_true",
        help="Run only the reviewed selection (exposed test docs; engineering regression only)",
    )
    parser.add_argument("--include-test", action="store_true")
    parser.add_argument("--exposure-ack", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--platform")
    parser.add_argument("--mode", choices=["online", "batch"], default="online")
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    parser.add_argument("--no-repair", action="store_true")
    parser.add_argument(
        "--dry-run", action="store_true", help="Build requests and report sizes; no network"
    )
    parser.add_argument(
        "--truth-corpus",
        type=Path,
        help="Score the full contract against a truth-first corpus (train/validation only)",
    )
    parser.add_argument("--keep-proposals", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_api_key_from_dotenv(ROOT / ".env")

    gold = json.loads(GOLD.read_text())
    gold_expected = {case["document_id"]: case["expected"] for case in gold["cases"]}
    corpus, gold_revisions, traps = CORPUS, {}, {}
    if args.truth_corpus:
        if "test" in args.splits:
            raise SystemExit("Truth-corpus test gold is sealed; use robotic_ebus_truth/qualify_truth.py")
        corpus = args.truth_corpus
        rows = load_documents(args.splits, args.limit, args.platform, corpus=corpus)
        wanted = {r["document_id"] for r in rows}
        for split in args.splits:
            for line in (corpus / "gold" / f"{split}.gold.jsonl").read_text().splitlines():
                entry = json.loads(line)
                if entry["document_id"] in wanted:
                    gold_revisions[entry["document_id"]] = entry["revision"]
                    traps[entry["document_id"]] = entry.get("traps", [])
    elif args.gold:
        rows = [r for r in load_documents(["test"]) if r["document_id"] in gold_expected]
    else:
        if "test" in args.splits and not (args.include_test and args.exposure_ack):
            raise SystemExit("test split requires --include-test --exposure-ack")
        rows = load_documents(args.splits, args.limit, args.platform)
    arms = [parse_arm(label) for label in args.arms]

    if args.dry_run:
        provider = ClaudeRegistryProvider(ClaudeClient(ClaudeSettings.from_env(), sdk=object()))
        params = [provider.build_params(request_for(r)) for r in rows]
        chars = [len(p["messages"][0]["content"]) for p in params]
        report = {
            "documents": len(rows),
            "system_prompt_chars": len(params[0]["system"][0]["text"]) if params else 0,
            "user_chars_mean": sum(chars) / len(chars) if chars else 0,
            "prompt_digest": prompt_digest(),
            "arms": [a["label"] for a in arms],
        }
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return

    report = {
        "corpus": corpus.name,
        "splits": ["test(gold)"] if args.gold else args.splits,
        "prompt_digest": prompt_digest(),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "qualification_use": "none (engineering evaluation on exposed or development documents)",
        "arms": {},
        "documents": {
            r["document_id"]: {
                "split": r["split"],
                "platform": r.get("platform"),
                "style": r.get("style"),
                "traps": r.get("traps"),
            }
            for r in rows
        },
    }
    silver = {
        r["document_id"]: silver_facts(r["generator_metadata"])
        for r in rows
        if r.get("generator_metadata")
    }
    for arm in arms:
        if arm["kind"] == "deterministic":
            results = run_online(arm, rows, LocalDeterministicProvider(), corpus.name)
        else:
            settings = ClaudeSettings.from_env(model=arm["model"], effort=arm["effort"])
            provider = ClaudeRegistryProvider(ClaudeClient(settings), repair=not args.no_repair)
            results = (
                run_batch(arm, rows, provider, args.poll_seconds, corpus.name)
                if args.mode == "batch"
                else run_online(arm, rows, provider, corpus.name)
            )
        report["arms"][arm["label"]] = {
            "mechanics": mechanics(results),
            "gold": score(
                results,
                {d: e for d, e in gold_expected.items() if d in results},
                gold["critical_fields"],
            ),
            "silver": score(results, silver, SILVER_FIELDS, known_only=True),
            "contract": contract_scores(results, gold_revisions, traps) if gold_revisions else None,
            "results": {
                d: r if args.keep_proposals else {k: v for k, v in r.items() if k != "proposal"}
                for d, r in results.items()
            },
        }
        args.output.write_text(json.dumps(report, indent=2, default=list) + "\n")
    summary = {
        label: {
            "mechanics": {k: v for k, v in arm["mechanics"].items() if k != "assembly_stats"},
            "gold_overall": arm["gold"].get("overall"),
            "silver_overall": arm["silver"].get("overall"),
            "contract_overall": (arm["contract"] or {}).get("overall"),
            "contract_rows": {
                k: {m: v[m] for m in ("precision", "recall", "support")}
                for k, v in ((arm["contract"] or {}).get("rows") or {}).items()
            },
        }
        for label, arm in report["arms"].items()
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
