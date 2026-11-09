#!/usr/bin/env python3
# ruff: noqa: E402 -- Put the repository root on sys.path before importing it.
"""Build a truth-first corpus: documents, gold revisions, and a sealed test split.

    python ops/tools/robotic_ebus_truth/build_split.py --families 200 --seed 20261109 \\
        --writer template --out data/ml_training/robotic_ebus_v1/corpus_truth_20261109

Each family is one sampled case written twice: a clean style and a messy
dictation. Families, not documents, are split (60/20/20), so renditions of a case
never straddle splits. Test gold is written to sealed/test.gold.jsonl and its hash
recorded in the manifest; only the one-use qualification command opens it.
The Claude writer needs ANTHROPIC_API_KEY and runs online.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]

from ip_registry_engine.focused import stable_id

from app.common.anthropic_client import load_api_key_from_dotenv
from ops.tools.robotic_ebus_truth.gold import build_gold, plan_statements
from ops.tools.robotic_ebus_truth.scenarios import sample_scenario
from ops.tools.robotic_ebus_truth.template_writer import render
from ops.tools.robotic_ebus_truth.verify import unsupported_values

GENERATOR_VERSION = "truth-first-1"
CLEAN_TEMPLATE_STYLES = ("sectioned", "markdown", "fielded", "dictation")
CLEAN_CLAUDE_STYLES = ("narrative", "dictation")


def _sha(data: bytes | str) -> str:
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def compact(revision: dict) -> tuple[dict, dict]:
    """Gold values plus {field_path: [start, end, assertion]}; provenance is rebuilt from the text."""
    evidence = {
        p["field_path"]: [p["source_start"], p["source_end"], p.get("assertion_context")]
        for p in revision["field_provenance"]
        if p.get("source_start") is not None
    }
    return {k: v for k, v in revision.items() if k != "field_provenance"}, evidence


def split_for(family_id: str) -> str:
    bucket = int(_sha(family_id)[:8], 16) % 10
    return "train" if bucket < 6 else ("validation" if bucket < 8 else "test")


def _documents(seed: int, writer: str, client=None):
    """Yield (style, text, spans, scenario, stated, problems) for one family."""
    scenario = sample_scenario(seed)
    stated = plan_statements(scenario, seed)
    rng = random.Random(seed)
    if writer == "template":
        for style in (rng.choice(CLEAN_TEMPLATE_STYLES), "messy"):
            text, spans = render(scenario, stated, style, seed)
            problems = [
                f"unsupported:{u}:{f}"
                for u, f, _ in unsupported_values(scenario, stated, spans, text)
            ]
            yield style, text, spans, scenario, stated, problems
        return
    from app.common.llm_egress import egress_context
    from ops.tools.robotic_ebus_truth.claude_writer import write_online

    for style in (rng.choice(CLEAN_CLAUDE_STYLES), "messy"):
        with egress_context("synthetic", source="truth_first_generator"):
            result = write_online(client, scenario, stated, style=style, seed=seed)
        yield style, result["text"], result["spans"], scenario, stated, result["problems"]


def build(
    out: Path,
    *,
    families: int,
    seed: int,
    writer: str,
    model: str | None = None,
    effort: str | None = None,
) -> dict:
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} exists; corpora are immutable, choose a new directory")
    client = None
    if writer == "claude":
        from app.common.anthropic_client import ClaudeClient, ClaudeSettings

        client = ClaudeClient(ClaudeSettings.from_env(model=model, effort=effort))
    (out / "gold").mkdir(parents=True, exist_ok=True)
    (out / "sealed").mkdir(exist_ok=True)
    documents: dict[str, list[dict]] = {"train": [], "validation": [], "test": []}
    gold: dict[str, list[dict]] = {"train": [], "validation": [], "test": []}
    rejected, traps, styles = [], Counter(), Counter()
    for offset in range(families):
        family_seed = seed + offset
        for style, text, spans, scenario, stated, problems in _documents(
            family_seed, writer, client
        ):
            split = split_for(scenario.family_id)
            if problems or not text:
                rejected.append(
                    {"family_id": scenario.family_id, "style": style, "problems": problems[:20]}
                )
                continue
            document_id = stable_id(scenario.family_id, f"truth:doc:{style}")
            digest = _sha(text)
            revision = build_gold(
                scenario, stated, spans, text, document_id=document_id, digest=digest
            )
            documents[split].append(
                {
                    "document_id": document_id,
                    "text": text,
                    "text_sha256": digest,
                    "family_id": scenario.family_id,
                    "split": split,
                    "platform": scenario.platform,
                    "style": style,
                    "writer": writer,
                    "traps": scenario.traps,
                    "components": list(scenario.components),
                    "generator": {"version": GENERATOR_VERSION, "seed": family_seed},
                }
            )
            values, evidence = compact(revision)
            gold[split].append(
                {
                    "document_id": document_id,
                    "family_id": scenario.family_id,
                    "traps": scenario.traps,
                    "revision": values,
                    "evidence": evidence,
                }
            )
            traps.update(scenario.traps)
            styles[style] += 1
    artifacts, sealed = {}, {}
    for split in documents:
        path = out / f"{split}.jsonl"
        path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in documents[split]))
        artifacts[path.name] = _sha(path.read_bytes())
        target = out / ("sealed" if split == "test" else "gold") / f"{split}.gold.jsonl"
        target.write_text("".join(json.dumps(g, sort_keys=True) + "\n" for g in gold[split]))
        (sealed if split == "test" else artifacts)[target.relative_to(out).as_posix()] = _sha(
            target.read_bytes()
        )
    if rejected:
        (out / "rejected.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rejected))
    manifest = {
        "profile": "robotic_ebus_v1",
        "schema_version": "0.2.0",
        "corpus_kind": "truth_first",
        "generator_version": GENERATOR_VERSION,
        "writer": writer,
        "model": model if writer == "claude" else None,
        "seed": seed,
        "families": families,
        "documents": {split: len(rows) for split, rows in documents.items()},
        "rejected_documents": len(rejected),
        "styles": dict(styles),
        "traps": dict(traps),
        "artifacts": artifacts,
        "sealed": sealed,
        "created_at": datetime.now(UTC).isoformat(),
        "policy": (
            "Synthetic only. Gold is known by construction (stated units with exact spans). "
            "sealed/ is opened only by the one-use qualification command, which reserves "
            "independent_qualification_use.json first; any other look at test gold ends its "
            "use for qualification."
        ),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--families", type=int, default=200)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--writer", choices=["template", "claude"], default="template")
    parser.add_argument("--model", default=None)
    parser.add_argument("--effort", default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    load_api_key_from_dotenv(ROOT / ".env")
    manifest = build(
        args.out,
        families=args.families,
        seed=args.seed,
        writer=args.writer,
        model=args.model,
        effort=args.effort,
    )
    print(
        json.dumps(
            {k: manifest[k] for k in ("documents", "rejected_documents", "styles", "traps")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
