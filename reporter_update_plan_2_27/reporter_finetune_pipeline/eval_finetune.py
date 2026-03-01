#!/usr/bin/env python3
"""Evaluate a fine-tuned reporter model against gold-standard completions.

Runs the fine-tuned model on validation examples and scores output quality
using section coverage, text similarity, and clinical content metrics.

Usage:
    python eval_finetune.py --model ft:gpt-4o-mini-2024-07-18:org::jobid
    python eval_finetune.py --model ft:gpt-4o-mini-2024-07-18:org::jobid --max-cases 50
    python eval_finetune.py --model ft:gpt-4o-mini-2024-07-18:org::jobid --style sloppy
    python eval_finetune.py --compare-baseline   # also run base model for comparison

Requires: OPENAI_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. pip install openai")
    sys.exit(1)

DEFAULT_EVAL_FILE = Path("fine_tuning/reporter_ft_valid.jsonl")
DEFAULT_OUTPUT_DIR = Path("fine_tuning/eval_results")

# ─── Required report sections ───
REQUIRED_SECTIONS = [
    "INDICATION",
    "CONSENT",
    "PREOPERATIVE DIAGNOSIS",
    "POSTOPERATIVE DIAGNOSIS",
    "PROCEDURE",
    "ANESTHESIA",
    "COMPLICATION",
    "PROCEDURE IN DETAIL",
    "IMPRESSION",
]

# ─── Input style detection patterns ───
STYLE_PATTERNS = {
    "structured": re.compile(
        r"^(PATIENT|DEMOGRAPHICS|PT):\s", re.MULTILINE
    ),
    "narrative": re.compile(
        r"(please generate|patient is a|we found|we placed)", re.IGNORECASE
    ),
    "sloppy": re.compile(
        r"^[a-z].*\.\s[a-z]", re.MULTILINE  # lowercase starts, terse
    ),
    "billing": re.compile(
        r"(Procedures:|Diagnosis:|Indication:|CPT)", re.IGNORECASE
    ),
    "formatted": re.compile(
        r"^Patient:\s.*\|", re.MULTILINE
    ),
}


def detect_style(prompt: str) -> str:
    """Detect the input style of a prompt."""
    # Check in order of specificity
    if STYLE_PATTERNS["formatted"].search(prompt):
        return "formatted"
    if STYLE_PATTERNS["billing"].search(prompt):
        return "billing"
    if STYLE_PATTERNS["structured"].search(prompt):
        return "structured"
    if STYLE_PATTERNS["narrative"].search(prompt):
        return "narrative"
    if STYLE_PATTERNS["sloppy"].search(prompt):
        return "sloppy"
    return "unknown"


def detect_procedure_types(text: str) -> list[str]:
    """Detect procedure types from text content."""
    text_lower = text.lower()
    types = []
    checks = [
        ("stent", "stent"),
        ("ebus", "ebus"),
        ("thoracentesis", "thoracentesis"),
        ("cryo", "cryotherapy"),
        ("balloon", "balloon_dilation"),
        ("robotic", "robotic_bronch"),
        ("ion ", "robotic_bronch"),
        ("valve", "blvr"),
        ("blvr", "blvr"),
        ("hemoptysis", "hemoptysis"),
        ("trach", "tracheostomy"),
        ("chest tube", "chest_tube"),
        ("pigtail", "chest_tube"),
        ("fiducial", "fiducial"),
        ("bal ", "bal"),
        ("bronchoalveolar", "bal"),
        ("rigid", "rigid_bronch"),
        ("transplant", "transplant"),
        ("pleuroscopy", "pleuroscopy"),
        ("pleurodesis", "pleuroscopy"),
    ]
    for pattern, label in checks:
        if pattern in text_lower and label not in types:
            types.append(label)
    return types or ["general"]


def score_section_coverage(generated: str) -> tuple[float, list[str]]:
    """Check what fraction of required sections are present."""
    generated_upper = generated.upper()
    missing = []
    found = 0
    for section in REQUIRED_SECTIONS:
        if section in generated_upper:
            found += 1
        else:
            missing.append(section)
    return found / len(REQUIRED_SECTIONS), missing


def score_text_similarity(generated: str, gold: str) -> float:
    """SequenceMatcher ratio between generated and gold."""
    return SequenceMatcher(None, generated, gold).ratio()


def extract_numbers_and_sizes(text: str) -> set[str]:
    """Extract device sizes, measurements, station numbers from text."""
    patterns = [
        r"\d+x\d+\s*mm",          # stent sizes like 14x30 mm
        r"\d+\.\d+\s*(?:cm|mm)",   # measurements like 1.5 cm
        r"station\s*\d+[a-zA-Z]?", # EBUS stations
        r"\d+\s*(?:Fr|French)",     # catheter sizes
        r"\d+/\d+/\d+",            # balloon sizes like 8/9/10
        r"\d+\s*ml\b",             # fluid volumes
    ]
    found = set()
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            found.add(match.group(0).lower().strip())
    return found


def score_clinical_details(generated: str, gold: str) -> float:
    """Measure how many clinical details from gold appear in generated."""
    gold_details = extract_numbers_and_sizes(gold)
    if not gold_details:
        return 1.0  # no details to check
    gen_details = extract_numbers_and_sizes(generated)
    if not gold_details:
        return 1.0
    overlap = gold_details & gen_details
    return len(overlap) / len(gold_details)


def score_length_ratio(generated: str, gold: str) -> float:
    """Ratio of generated length to gold length (ideal ≈ 1.0)."""
    if not gold:
        return 0.0
    return len(generated) / len(gold)


def call_model(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> str:
    """Call the model and return the response text."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"[ERROR: {e}]"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True,
                   help="Fine-tuned model ID (e.g., ft:gpt-4o-mini-2024-07-18:org::jobid)")
    p.add_argument("--eval-file", type=Path, default=DEFAULT_EVAL_FILE,
                   help=f"Validation JSONL file (default: {DEFAULT_EVAL_FILE})")
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--max-cases", type=int, default=None,
                   help="Max cases to evaluate (default: all)")
    p.add_argument("--style", default=None,
                   choices=["structured", "narrative", "sloppy", "billing", "formatted"],
                   help="Only evaluate cases of this input style.")
    p.add_argument("--procedure", default=None,
                   help="Only evaluate cases involving this procedure type.")
    p.add_argument("--compare-baseline", action="store_true",
                   help="Also run the base model for comparison.")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--save-outputs", action="store_true",
                   help="Save individual model outputs alongside scores.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not (os.environ.get("OPENAI_API_KEY") or "").strip():
        print("ERROR: OPENAI_API_KEY not set.")
        return 1

    if not args.eval_file.exists():
        print(f"ERROR: Eval file not found: {args.eval_file}")
        print("Run prepare_finetune.py first.")
        return 1

    client = OpenAI()

    # Load eval data
    print(f"Loading eval data from: {args.eval_file}")
    cases: list[dict] = []
    with args.eval_file.open() as f:
        for line in f:
            row = json.loads(line.strip())
            msgs = row["messages"]
            system = next((m["content"] for m in msgs if m["role"] == "system"), "")
            user = next((m["content"] for m in msgs if m["role"] == "user"), "")
            gold = next((m["content"] for m in msgs if m["role"] == "assistant"), "")
            style = detect_style(user)
            procs = detect_procedure_types(user + " " + gold)

            # Apply filters
            if args.style and style != args.style:
                continue
            if args.procedure and args.procedure not in procs:
                continue

            cases.append({
                "system": system,
                "user": user,
                "gold": gold,
                "style": style,
                "procedures": procs,
            })

    if args.max_cases:
        cases = cases[:args.max_cases]

    print(f"  Evaluating {len(cases)} cases")
    print(f"  Model: {args.model}")
    if args.style:
        print(f"  Style filter: {args.style}")
    if args.procedure:
        print(f"  Procedure filter: {args.procedure}")
    print()

    # Run evaluation
    results: list[dict] = []
    style_scores: dict[str, list[dict]] = defaultdict(list)
    proc_scores: dict[str, list[dict]] = defaultdict(list)

    start_time = time.time()
    for i, case in enumerate(cases):
        # Progress
        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(cases) - i - 1) / rate if rate > 0 else 0
        print(f"\r  [{i+1}/{len(cases)}] "
              f"({rate:.1f} cases/s, ETA {eta:.0f}s) "
              f"style={case['style']:<12} procs={','.join(case['procedures'][:2]):<20}",
              end="", flush=True)

        # Generate
        generated = call_model(
            client, args.model, case["system"], case["user"],
            max_tokens=args.max_tokens, temperature=args.temperature,
        )

        # Score
        section_cov, missing_sections = score_section_coverage(generated)
        text_sim = score_text_similarity(generated, case["gold"])
        clinical_det = score_clinical_details(generated, case["gold"])
        length_ratio = score_length_ratio(generated, case["gold"])

        scores = {
            "section_coverage": round(section_cov, 4),
            "text_similarity": round(text_sim, 4),
            "clinical_detail_recall": round(clinical_det, 4),
            "length_ratio": round(length_ratio, 4),
            "missing_sections": missing_sections,
            "style": case["style"],
            "procedures": case["procedures"],
        }

        if args.save_outputs:
            scores["prompt"] = case["user"][:500]
            scores["generated"] = generated
            scores["gold"] = case["gold"]

        results.append(scores)
        style_scores[case["style"]].append(scores)
        for proc in case["procedures"]:
            proc_scores[proc].append(scores)

    print(f"\n\nCompleted in {time.time() - start_time:.1f}s")

    # ─── Aggregate results ───
    def avg(lst: list[dict], key: str) -> float:
        vals = [d[key] for d in lst if isinstance(d.get(key), (int, float))]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    print(f"\n{'=' * 70}")
    print(f"  OVERALL RESULTS ({len(results)} cases)")
    print(f"{'=' * 70}")
    print(f"  Section Coverage:       {avg(results, 'section_coverage'):.4f}  (gate: >= 0.99)")
    print(f"  Text Similarity:        {avg(results, 'text_similarity'):.4f}")
    print(f"  Clinical Detail Recall: {avg(results, 'clinical_detail_recall'):.4f}")
    print(f"  Length Ratio (avg):     {avg(results, 'length_ratio'):.4f}  (ideal: ~1.0)")

    # Gate check
    sec_cov = avg(results, "section_coverage")
    gates_passed = sec_cov >= 0.99
    print(f"\n  Section Coverage Gate:  {'PASS' if gates_passed else 'FAIL'}")

    # ─── Per-style breakdown ───
    print(f"\n{'=' * 70}")
    print(f"  PER-STYLE BREAKDOWN")
    print(f"{'=' * 70}")
    print(f"  {'Style':<15} {'N':>5} {'SectCov':>9} {'TextSim':>9} {'ClinDet':>9} {'LenRatio':>10}")
    print(f"  {'-'*15} {'-'*5} {'-'*9} {'-'*9} {'-'*9} {'-'*10}")
    for style in ["structured", "narrative", "sloppy", "billing", "formatted", "unknown"]:
        if style not in style_scores:
            continue
        ss = style_scores[style]
        print(f"  {style:<15} {len(ss):>5} "
              f"{avg(ss, 'section_coverage'):>9.4f} "
              f"{avg(ss, 'text_similarity'):>9.4f} "
              f"{avg(ss, 'clinical_detail_recall'):>9.4f} "
              f"{avg(ss, 'length_ratio'):>10.4f}")

    # ─── Per-procedure breakdown ───
    print(f"\n{'=' * 70}")
    print(f"  PER-PROCEDURE BREAKDOWN (top 15)")
    print(f"{'=' * 70}")
    print(f"  {'Procedure':<20} {'N':>5} {'SectCov':>9} {'TextSim':>9} {'ClinDet':>9}")
    print(f"  {'-'*20} {'-'*5} {'-'*9} {'-'*9} {'-'*9}")
    sorted_procs = sorted(proc_scores.items(), key=lambda x: -len(x[1]))
    for proc, ps in sorted_procs[:15]:
        print(f"  {proc:<20} {len(ps):>5} "
              f"{avg(ps, 'section_coverage'):>9.4f} "
              f"{avg(ps, 'text_similarity'):>9.4f} "
              f"{avg(ps, 'clinical_detail_recall'):>9.4f}")

    # ─── Most common missing sections ───
    all_missing = defaultdict(int)
    for r in results:
        for sec in r.get("missing_sections", []):
            all_missing[sec] += 1
    if all_missing:
        print(f"\n{'=' * 70}")
        print(f"  MOST COMMONLY MISSING SECTIONS")
        print(f"{'=' * 70}")
        for sec, count in sorted(all_missing.items(), key=lambda x: -x[1]):
            pct = count / len(results) * 100
            print(f"  {sec:<30} {count:>5} ({pct:.1f}%)")

    # ─── Save results ───
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace(":", "_").replace("/", "_")
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Summary
    summary = {
        "model": args.model,
        "eval_file": str(args.eval_file),
        "timestamp": timestamp,
        "total_cases": len(results),
        "style_filter": args.style,
        "procedure_filter": args.procedure,
        "overall": {
            "section_coverage": avg(results, "section_coverage"),
            "text_similarity": avg(results, "text_similarity"),
            "clinical_detail_recall": avg(results, "clinical_detail_recall"),
            "length_ratio": avg(results, "length_ratio"),
            "section_coverage_gate_passed": sec_cov >= 0.99,
        },
        "per_style": {
            style: {
                "n": len(ss),
                "section_coverage": avg(ss, "section_coverage"),
                "text_similarity": avg(ss, "text_similarity"),
                "clinical_detail_recall": avg(ss, "clinical_detail_recall"),
                "length_ratio": avg(ss, "length_ratio"),
            }
            for style, ss in style_scores.items()
        },
        "per_procedure": {
            proc: {
                "n": len(ps),
                "section_coverage": avg(ps, "section_coverage"),
                "text_similarity": avg(ps, "text_similarity"),
                "clinical_detail_recall": avg(ps, "clinical_detail_recall"),
            }
            for proc, ps in sorted_procs[:15]
        },
        "missing_sections": dict(all_missing),
    }

    summary_path = args.output_dir / f"eval_{model_slug}_{timestamp}.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\n  Summary saved: {summary_path}")

    # Per-case results
    if args.save_outputs:
        details_path = args.output_dir / f"eval_{model_slug}_{timestamp}_details.jsonl"
        with details_path.open("w") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  Details saved: {details_path}")

    # ─── Recommendations ───
    print(f"\n{'=' * 70}")
    print(f"  RECOMMENDATIONS")
    print(f"{'=' * 70}")

    if sec_cov >= 0.99:
        print("  ✓ Section coverage gate PASSED. Report structure looks solid.")
    else:
        worst_missing = sorted(all_missing.items(), key=lambda x: -x[1])[:3]
        sections_str = ", ".join(f"{s} ({c}x)" for s, c in worst_missing)
        print(f"  ✗ Section coverage below 0.99. Most missing: {sections_str}")
        print(f"    → Check if training data consistently includes these sections.")
        print(f"    → Consider adding explicit section markers to the system prompt.")

    # Check style gap
    style_covs = {s: avg(ss, "section_coverage") for s, ss in style_scores.items()}
    if style_covs:
        best_style = max(style_covs, key=style_covs.get)
        worst_style = min(style_covs, key=style_covs.get)
        gap = style_covs[best_style] - style_covs[worst_style]
        if gap > 0.10:
            print(f"\n  ⚠ Style gap: {best_style} ({style_covs[best_style]:.3f}) vs "
                  f"{worst_style} ({style_covs[worst_style]:.3f}) = {gap:.3f}")
            print(f"    → Consider upsampling {worst_style}-style examples in training data.")

    text_sim = avg(results, "text_similarity")
    if text_sim < 0.30:
        print(f"\n  ⚠ Low text similarity ({text_sim:.3f}). Model may be generating")
        print(f"    plausible reports that don't match your specific documentation style.")
        print(f"    → This is common in early fine-tunes. Try more epochs or more data.")
    elif text_sim > 0.60:
        print(f"\n  ✓ Good text similarity ({text_sim:.3f}). Model is learning your style.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
