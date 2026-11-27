#!/usr/bin/env python3
# ruff: noqa: E402 -- Put the repository root on sys.path before importing it.
"""One-use qualification of an extractor on a truth-first corpus's sealed test split.

    python ops/tools/robotic_ebus_truth/qualify_truth.py \\
        --corpus data/ml_training/robotic_ebus_v1/corpus_truth_20261109 \\
        --provider claude:opus:medium --output reports/robotic_ebus_truth_qualification.json

The corpus artifacts and the sealed gold are verified against the manifest, then
independent_qualification_use.json is reserved atomically before any test
document is extracted. The reservation stays even if the run fails; a corpus is
qualified at most once. Passing is synthetic qualification only: clinical
validation and promotion stay closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]

from ip_registry_engine.engine import LocalDeterministicProvider

from app.common.anthropic_client import ClaudeClient, ClaudeSettings, load_api_key_from_dotenv
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.extraction.contract_spec import dictionary_fields
from app.registry_workbench.extraction.prompt import prompt_digest
from ops.tools.eval_registry_llm import contract_scores, mechanics, parse_arm, run_batch, run_online

PRECISION_TARGET, RECALL_TARGET = 0.98, 0.95
LEDGER = "independent_qualification_use.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_corpus(corpus: Path) -> dict:
    manifest = json.loads((corpus / "manifest.json").read_text())
    if manifest.get("corpus_kind") != "truth_first":
        raise ValueError("Not a truth-first corpus")
    for name, digest in {**manifest["artifacts"], **manifest["sealed"]}.items():
        if _sha(corpus / name) != digest:
            raise ValueError(f"Corpus artifact changed since generation: {name}")
    return manifest


def core_fields() -> set[str]:
    return {
        path
        for path, entry in dictionary_fields().items()
        if entry.get("collection_tier") == "Core"
    }


def gate(contract: dict, mechanics_report: dict, errors: int) -> dict:
    core = core_fields()
    failing = {
        path: {k: rates[k] for k in ("precision", "recall", "support")}
        for path, rates in contract["fields"].items()
        if path in core
        and rates["sufficient_support"]
        and ((rates["precision"] or 0) < PRECISION_TARGET or (rates["recall"] or 0) < RECALL_TARGET)
    }
    checks = {
        "core_field_thresholds": not failing,
        "foreign_key_accuracy": (contract["foreign_key_accuracy"]["rate"] or 0) >= PRECISION_TARGET,
        "contract_valid_rate": mechanics_report["contract_valid_rate"] >= 0.99,
        "runtime_success": errors == 0,
    }
    return {"checks": checks, "failing_core_fields": failing, "passed": all(checks.values())}


def qualify(
    corpus: Path,
    provider_label: str,
    output: Path,
    *,
    mode: str = "online",
    poll_seconds: float = 60.0,
) -> dict:
    if output.exists():
        raise ValueError("Qualification output exists; results are immutable")
    manifest = verify_corpus(corpus)
    if (corpus / LEDGER).exists():
        raise ValueError("This corpus's test split was already used; engineering regression only")
    arm = parse_arm(provider_label)
    if arm["kind"] == "deterministic":
        provider, identity = (
            LocalDeterministicProvider(),
            {"provider": "deterministic", "engine_version": "0.2.0"},
        )
    else:
        settings = ClaudeSettings.from_env(model=arm["model"], effort=arm["effort"])
        provider = ClaudeRegistryProvider(ClaudeClient(settings))
        identity = {
            "provider": "claude",
            "model": settings.model,
            "effort": settings.effort,
            "prompt_digest": prompt_digest(),
        }
    rows = [json.loads(line) for line in (corpus / "test.jsonl").read_text().splitlines()]
    reservation = {
        "corpus_manifest_sha256": _sha(corpus / "manifest.json"),
        "sealed_gold_sha256": manifest["sealed"],
        "extractor": identity,
        "reserved_at": datetime.now(UTC).isoformat(),
        "document_ids": sorted(r["document_id"] for r in rows),
        "policy": "Test split now exposed; never reuse this corpus for independent qualification",
    }
    with (corpus / LEDGER).open("x", encoding="utf-8") as handle:  # reserve before any inference
        handle.write(json.dumps(reservation, indent=2) + "\n")
    gold, traps = {}, {}
    for line in (corpus / "sealed" / "test.gold.jsonl").read_text().splitlines():
        entry = json.loads(line)
        gold[entry["document_id"]], traps[entry["document_id"]] = (
            entry["revision"],
            entry.get("traps", []),
        )
    results = (
        run_batch(arm, rows, provider, poll_seconds, corpus.name)
        if mode == "batch" and arm["kind"] == "claude"
        else run_online(arm, rows, provider, corpus.name)
    )
    errors = sum(1 for r in results.values() if r["status"] == "error")
    contract = contract_scores(results, gold, traps)
    mech = mechanics(results)
    verdict = gate(contract, mech, errors)
    report = {
        "schema_version": "robotic_ebus.truth_first_qualification.v1",
        "synthetic_only": True,
        "clinical_validation": False,
        "promotion_allowed": False,
        "independent_synthetic_qualification_passed": verdict["passed"],
        "precision_target": PRECISION_TARGET,
        "recall_target": RECALL_TARGET,
        "binding": reservation,
        "corpus": {
            "name": corpus.name,
            "writer": manifest["writer"],
            "generator_version": manifest["generator_version"],
        },
        "documents": len(rows),
        **verdict,
        "mechanics": {k: v for k, v in mech.items() if k != "assembly_stats"},
        "contract": contract,
        "blocked_reasons": [k for k, ok in verdict["checks"].items() if not ok]
        + ["synthetic_is_not_clinical_validation", "physician_anchor_set_pending"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument(
        "--provider", required=True, help="deterministic or claude:<opus|sonnet|haiku>:<effort>"
    )
    parser.add_argument("--mode", choices=["online", "batch"], default="online")
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_api_key_from_dotenv(ROOT / ".env")
    report = qualify(
        args.corpus, args.provider, args.output, mode=args.mode, poll_seconds=args.poll_seconds
    )
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("independent_synthetic_qualification_passed", "checks", "blocked_reasons")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
