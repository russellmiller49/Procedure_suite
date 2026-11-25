#!/usr/bin/env python3
# ruff: noqa: E402 -- Put the repository root on sys.path before importing it.
"""Precompute the stored results the robotic/EBUS demo page serves.

    python ops/tools/warm_robotic_ebus_demo_cache.py --llm claude        # paid, online
    python ops/tools/warm_robotic_ebus_demo_cache.py --llm none          # rules engine only
    python ops/tools/warm_robotic_ebus_demo_cache.py --llm gold --raw \\
        --output /tmp/results.dev.json                                    # offline stand-in

For every reviewed redacted text in redactions.json (the text the real browser
redactor produces for a sample) this runs the rules engine and the chosen LLM
and writes results.json keyed by the sha256 of that text. The demo then serves
these stored results and makes no provider call.

It also prints a review report per sample: agreement with the generator gold
where a sample has gold, the suggested codes, and four checks that must hold for
a public sample (no surveyed station shown as sampled, no specimen on the wrong
lesion, nothing planned shown as performed, no tool-in-lesion from a radial view).

``--llm gold`` builds a stand-in from the generator gold for development only.
It never writes the default results.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]

from ip_registry_contracts.models import ExtractionRequest
from ip_registry_engine.engine import LocalDeterministicProvider

from app.common.anthropic_client import ClaudeClient, ClaudeSettings, load_api_key_from_dotenv
from app.common.llm_egress import egress_context
from app.registry_demo.store import normalise, text_key
from app.registry_workbench.contract_coding import provenance_from_evidence_map, suggest_codes
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.scoring import score_document

DEMO_DIR = ROOT / "data/knowledge/robotic_ebus_v1/demo"
MODELS = {
    "opus": "claude-opus-5-5",
    "sonnet": "claude-sonnet-5-5",
    "haiku": "claude-haiku-5-5",
}
STARTED = {"performed", "attempted"}


def _request(text: str) -> ExtractionRequest:
    return ExtractionRequest(
        job_id=uuid4(),
        source_document_id=uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        text=text,
        kind="procedure",
    )


def _gold_response(sample: dict, text: str) -> dict | None:
    """Development stand-in: the generator gold shaped like an extraction response."""
    gold = sample.get("gold")
    if not gold or normalise(text) != normalise(sample["text"]):
        return None
    proposal = dict(gold["revision"])
    proposal.pop("event_date", None)
    proposal["field_provenance"] = provenance_from_evidence_map(gold["evidence"], text)
    return {
        "status": "proposed",
        "warnings": ["requires_clinical_review"],
        "observations": {
            "proposal": proposal,
            "unresolved_mentions": [],
            "quality_signals": [],
            "inference": {"provider": "gold_reference", "model": "generator gold (not a model)"},
        },
    }


def _sampled_stations(proposal: dict | None) -> set[str]:
    return {
        s["iaslc_station"]
        for s in (proposal or {}).get("station_surveys") or []
        if s.get("station_sampled") is True
    }


def _started(proposal: dict | None) -> set[str]:
    return {
        p["category"]
        for p in (proposal or {}).get("procedures") or []
        if p.get("performance") in STARTED
    }


def _til(proposal: dict | None) -> int:
    return sum(
        1
        for e in (proposal or {}).get("localization_events") or []
        if e.get("tool_lesion_relationship") == "TIL"
    )


def review(sample: dict, entry: dict) -> dict:
    """Checks a reviewer reads before a sample goes public. Uses gold or ``expected``."""
    llm = ((entry.get("llm") or {}).get("observations") or {}).get("proposal")
    report: dict = {"llm_status": (entry.get("llm") or {}).get("status")}
    if not llm:
        return report
    codes = suggest_codes(llm, source_text=entry["text"])
    report["codes"] = [
        f"{c['code']}"
        + (f" x{c['units']}" if (c["units"] or 1) > 1 else "")
        + ("-" + ",".join(c["modifiers"]) if c["modifiers"] else "")
        for c in codes["codes"]
    ]
    report["code_review_flags"] = [f["flag"] for f in codes["review_flags"]]
    gold = (sample.get("gold") or {}).get("revision")
    expected = sample.get("expected") or {}
    checks: dict[str, bool | None] = {}
    if gold:
        score = score_document(gold, llm)
        tp = sum(v[0] for v in score.fields.values())
        fp = sum(v[1] for v in score.fields.values())
        fn = sum(v[2] for v in score.fields.values())
        report["vs_gold"] = {
            "correct": tp,
            "false_fills": fp,
            "missed": fn,
            "links_correct": score.foreign_keys[0],
            "links_total": score.foreign_keys[1],
            "false_fill_fields": sorted(k for k, v in score.fields.items() if v[1]),
        }
        checks["no_surveyed_station_shown_as_sampled"] = _sampled_stations(
            llm
        ) <= _sampled_stations(gold)
        checks["no_specimen_on_wrong_lesion"] = score.foreign_keys[0] == score.foreign_keys[1]
        checks["nothing_planned_shown_as_performed"] = _started(llm) <= _started(gold)
        checks["no_til_beyond_gold"] = _til(llm) <= _til(gold)
    elif expected:
        checks["no_surveyed_station_shown_as_sampled"] = _sampled_stations(llm) <= set(
            expected.get("stations_sampled") or []
        )
        checks["stations_sampled_as_expected"] = _sampled_stations(llm) == set(
            expected.get("stations_sampled") or []
        )
        checks["codes_as_expected"] = sorted(c["code"] for c in codes["codes"]) == sorted(
            expected.get("codes") or []
        )
        checks["no_specimen_on_wrong_lesion"] = None  # read by the reviewer
    report["checks"] = checks
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--llm", choices=["claude", "gold", "none"], required=True)
    parser.add_argument("--model", default="opus", choices=sorted(MODELS))
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--raw", action="store_true", help="also warm the unredacted sample text")
    parser.add_argument("--only", nargs="*", help="sample ids to (re)compute; others are kept")
    parser.add_argument("--output", type=Path, default=DEMO_DIR / "results.json")
    args = parser.parse_args()

    if args.llm == "gold" and args.output.resolve() == (DEMO_DIR / "results.json").resolve():
        raise SystemExit("--llm gold is a development stand-in; pass a separate --output")
    samples = json.loads((DEMO_DIR / "samples.json").read_text())["samples"]
    redactions_path = DEMO_DIR / "redactions.json"
    redactions = (
        json.loads(redactions_path.read_text()).get("redactions")
        if redactions_path.exists()
        else {}
    ) or {}
    existing = (
        json.loads(args.output.read_text()).get("entries") if args.output.exists() else {}
    ) or {}

    provider = None
    if args.llm == "claude":
        if not load_api_key_from_dotenv(ROOT / ".env"):
            raise SystemExit("ANTHROPIC_API_KEY is not set (shell or .env)")
        settings = ClaudeSettings.from_env(model=MODELS[args.model], effort=args.effort)
        provider = ClaudeRegistryProvider(ClaudeClient(settings))
    rules = LocalDeterministicProvider()

    entries = dict(existing)
    reports, total_cost = [], 0.0
    for sample in samples:
        if args.only and sample["id"] not in args.only:
            continue
        texts = [
            (r.get("worker") or "reviewed", r["text"]) for r in redactions.get(sample["id"], [])
        ]
        if args.raw:
            texts.append(("raw", sample["text"]))
        if not texts:
            print(
                f"{sample['id']}: no reviewed redaction yet (capture it in the browser, or --raw)"
            )
            continue
        for variant, text in texts:
            text = normalise(text)
            key = text_key(text)
            with egress_context("synthetic", source=f"demo:sample:{sample['id']}"):
                rules_response = rules.extract(_request(text)).model_dump(mode="json")
                if provider is not None:
                    llm_response = provider.extract(_request(text)).model_dump(mode="json")
                elif args.llm == "gold":
                    llm_response = _gold_response(sample, text)
                else:
                    llm_response = (existing.get(key) or {}).get("llm")
            entry = {
                "sample_id": sample["id"],
                "variant": variant,
                "text": text,
                "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "llm": llm_response,
                "rules": rules_response,
            }
            report = review(sample, entry)
            entries[key] = {k: v for k, v in entry.items() if k != "text"}
            inference = ((llm_response or {}).get("observations") or {}).get("inference") or {}
            total_cost += inference.get("cost_usd") or 0.0
            reports.append({"sample_id": sample["id"], "variant": variant, "sha256": key, **report})
            print(json.dumps(reports[-1], indent=1))

    args.output.write_text(
        json.dumps({"version": 1, "entries": entries}, indent=1, sort_keys=True) + "\n"
    )
    failed = [
        f"{r['sample_id']}:{name}"
        for r in reports
        for name, ok in (r.get("checks") or {}).items()
        if ok is False
    ]
    print(f"wrote {args.output} ({len(entries)} entries); LLM cost ${total_cost:.2f}")
    print("review checks failing: " + (", ".join(failed) if failed else "none"))


if __name__ == "__main__":
    main()
