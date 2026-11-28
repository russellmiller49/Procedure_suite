#!/usr/bin/env python3
# ruff: noqa: E402 -- Import the bounded packages from packages/*/src.
"""Compare registry extractors on the synthetic robotic/EBUS corpus.

Arms: ``deterministic`` (the vendored focused engine),
``claude:<opus|sonnet|haiku>:<effort>`` and ``openai:<model>:<effort>`` (model one
of gpt-6.2-astra, gpt-6.2-sol, gpt-6.1-terra, gpt-6-luna). LLM arms run online
(``--concurrency`` requests at a time after a sequential first document that warms
the prompt cache; Claude refusal fallbacks on). Claude arms can instead run
through the Message Batches API (half price, second batch for repairs); OpenAI
arms are online only.

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
import math
import statistics
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
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

from app.common.anthropic_client import ClaudeClient, ClaudeSettings, result_from_message
from app.common.dotenv_keys import load_api_key_from_dotenv
from app.common.llm_egress import egress_context
from app.common.openai_structured_client import MODEL_EFFORTS as OPENAI_MODEL_EFFORTS
from app.common.openai_structured_client import OpenAISettings, OpenAIStructuredClient
from app.llm_extraction import batch as batches
from app.registry_workbench.extraction.assembler import VALIDATION_EVENT_DATE
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.extraction.openai_provider import OpenAIRegistryProvider
from app.registry_workbench.extraction.prompt import prompt_digest
from app.registry_workbench.scoring import aggregate, score_document
from ops.tools.eval_robotic_ebus import focused_facts, metrics

CORPUS = ROOT / "data/ml_training/robotic_ebus_v1/corpus_20260914_v2"
GOLD = ROOT / "data/knowledge/robotic_ebus_v1/reviewed_eval_selection.json"
MODELS = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}
API_KEYS = {"claude": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
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
    parts = label.split(":")
    if len(parts) != 3:
        raise SystemExit(f"unknown arm {label!r}")
    kind, model, effort = parts
    if kind == "claude" and model in MODELS:
        return {"label": label, "kind": "claude", "model": MODELS[model], "effort": effort}
    if kind == "openai" and model in OPENAI_MODEL_EFFORTS:
        if effort not in OPENAI_MODEL_EFFORTS[model]:
            allowed = ", ".join(OPENAI_MODEL_EFFORTS[model])
            raise SystemExit(f"arm {label!r}: effort must be one of {allowed}")
        return {"label": label, "kind": "openai", "model": model, "effort": effort}
    raise SystemExit(f"unknown arm {label!r}")


def check_mode(arms, mode):
    """Only Claude arms have a batch path."""
    if mode == "batch":
        online_only = [a["label"] for a in arms if a["kind"] == "openai"]
        if online_only:
            raise SystemExit(f"--mode batch is not supported for {', '.join(online_only)}")


def load_keys(arms, dotenv_path):
    """Load from .env only the API keys the chosen arms need."""
    missing = []
    for name in sorted({API_KEYS[a["kind"]] for a in arms if a["kind"] in API_KEYS}):
        if not load_api_key_from_dotenv(dotenv_path, name):
            missing.append(name)
    if missing:
        raise SystemExit(f"missing API key(s): {', '.join(missing)}")


def llm_provider(arm, *, repair=True, offline=False):
    if arm["kind"] == "claude":
        settings = ClaudeSettings.from_env(model=arm["model"], effort=arm["effort"])
        return ClaudeRegistryProvider(
            ClaudeClient(settings, sdk=object() if offline else None), repair=repair
        )
    settings = OpenAISettings.from_env(model=arm["model"], effort=arm["effort"])
    return OpenAIRegistryProvider(OpenAIStructuredClient(settings), repair=repair)


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


def error_kind(exc):
    text = f"{type(exc).__name__} {exc}".lower()
    return "timeout" if "timeout" in text or "timed out" in text else "error"


def summarize(response, wall_s=None):
    if isinstance(response, Exception):
        return {
            "status": "error",
            "error": f"{type(response).__name__}: {response}"[:300],
            "error_kind": error_kind(response),
            "facts": {},
            "wall_s": wall_s,
        }
    obs = response.observations
    inference = obs.get("inference") or {}
    valid, approval = contract_check(obs.get("proposal"))
    signals = obs.get("quality_signals") or []
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
        "stop_reason": signals[0].get("stop_reason") if signals else None,
        "usage": inference.get("usage") or [],
        "cost_usd": inference.get("cost_usd"),
        "latency_s": inference.get("latency_s"),
        "wall_s": wall_s,
    }


def run_online(arm, rows, provider, source=CORPUS.name, concurrency=1):
    """First document alone (warms the prompt cache), then up to ``concurrency`` at once.

    The deterministic engine always runs sequentially. Results keep corpus order.
    """
    done, lock = [0], threading.Lock()

    def one(row):
        started = time.monotonic()
        try:
            response = (
                provider.extract(request_for(row))
                if arm["kind"] == "deterministic"
                else _extract_synthetic(provider, row, source)
            )
        except Exception as exc:  # recorded per document; the run continues
            response = exc
        summary = summarize(response, wall_s=round(time.monotonic() - started, 3))
        with lock:
            done[0] += 1
            print(
                f"[{arm['label']}] {done[0]}/{len(rows)} {row['document_id']} {summary['status']}",
                file=sys.stderr,
            )
        return summary

    workers = 1 if arm["kind"] == "deterministic" else max(1, concurrency)
    summaries = [one(row) for row in rows[:1]]
    if workers == 1:
        summaries += [one(row) for row in rows[1:]]
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            summaries += list(pool.map(one, rows[1:]))
    return {row["document_id"]: summary for row, summary in zip(rows, summaries, strict=True)}


def _extract_synthetic(provider, row, source):
    # Entered per call: context variables do not carry into worker threads.
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


def latency_stats(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    p95 = values[math.ceil(0.95 * len(values)) - 1]  # nearest rank
    return {
        "n": len(values),
        "mean": round(statistics.fmean(values), 3),
        "p50": round(statistics.median(values), 3),
        "p95": round(p95, 3),
    }


def outcome_counts(values):
    """Per-document outcomes. First-pass success: usable without a repair call."""
    return {
        "first_pass_success": sum(
            v["status"] in {"proposed", "unsupported"} and not v.get("repair_used", False)
            for v in values
        ),
        "repairs": sum(v.get("repair_used", False) for v in values),
        "refusals": sum(v.get("stop_reason") == "refusal" for v in values),
        "timeouts": sum(v.get("error_kind") == "timeout" for v in values),
        "errors": sum(v["status"] == "error" for v in values),
        "degraded": sum(v["status"] == "degraded" for v in values),
    }


def usage_totals(values):
    totals = defaultdict(int)
    for v in values:
        for call in v.get("usage") or []:
            for key, count in call.items():
                totals[key] += int(count or 0)
    return dict(sorted(totals.items()))


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
        "outcomes": outcome_counts(values),
        "usage_totals": usage_totals(values),
        "latency_s": latency_stats(v.get("latency_s") for v in values),
        "wall_s": latency_stats(v.get("wall_s") for v in values),
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


def dry_run_requests(arm, rows):
    """Request bodies an LLM arm would send, built offline (no client, no key)."""
    provider = llm_provider(arm, offline=True)
    bodies = [json.dumps(provider.build_params(request_for(r))) for r in rows]
    return {
        "provider": provider.provider_name,
        "model": arm["model"],
        "effort": arm["effort"],
        "request_bytes_mean": round(sum(map(len, bodies)) / len(bodies)) if bodies else 0,
    }


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
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Online LLM requests in flight after the first (sequential) document",
    )
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
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be at least 1")
    arms = [parse_arm(label) for label in args.arms]
    check_mode(arms, args.mode)
    if not args.dry_run:
        load_keys(arms, ROOT / ".env")

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
            "requests": {
                a["label"]: dry_run_requests(a, rows) for a in arms if a["kind"] != "deterministic"
            },
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
            provider = llm_provider(arm, repair=not args.no_repair)
            results = (
                run_batch(arm, rows, provider, args.poll_seconds, corpus.name)
                if args.mode == "batch"
                else run_online(arm, rows, provider, corpus.name, args.concurrency)
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
