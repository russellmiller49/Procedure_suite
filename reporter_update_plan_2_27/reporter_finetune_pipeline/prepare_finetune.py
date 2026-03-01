#!/usr/bin/env python3
"""Prepare reporter_training dataset for OpenAI fine-tuning.

Converts proc_suite_notes/reporter_training JSONL files into
OpenAI chat-format fine-tuning files (train + validation).

Usage:
    python prepare_finetune.py
    python prepare_finetune.py --input /path/to/reporter_training/reporter_training
    python prepare_finetune.py --system-prompt custom_system.txt
    python prepare_finetune.py --validate-only  # just check an existing output file

Output:
    reporter_ft_train.jsonl   (8,480 examples)
    reporter_ft_valid.jsonl   (2,120 examples)
    reporter_ft_manifest.json (metadata + token stats)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# System prompt — this is baked into every fine-tuning example.
# Keep it short: every token here is repeated 8,480x and costs money.
# ---------------------------------------------------------------------------
DEFAULT_SYSTEM_PROMPT = """You are an Interventional Pulmonology operative report generator at a Navy medical center.

Given a procedure dictation (which may be structured, narrative, shorthand, or billing-focused), produce a complete synoptic operative report.

Required sections (in order):
1. INDICATION FOR OPERATION
2. CONSENT
3. PREOPERATIVE DIAGNOSIS
4. POSTOPERATIVE DIAGNOSIS
5. PROCEDURE (list of procedures performed)
6. ATTENDING / ANESTHESIA / MONITORING
7. COMPLICATIONS
8. PROCEDURE IN DETAIL (detailed narrative)
9. IMPRESSION / PLAN

Rules:
- Include ALL procedures actually performed. Do not infer procedures not described.
- Use exact device names, sizes, and settings when provided.
- Use standard anatomical terminology (e.g., "Right Upper Lobe", "station 7", "LB6").
- If information is missing from the dictation, use "[Not Documented]" rather than inventing details.
- Write in formal operative report style."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", type=Path,
                   default=Path("proc_suite_notes/reporter_training/reporter_training"),
                   help="Directory containing *_train.jsonl and *_valid.jsonl files.")
    p.add_argument("--output-dir", type=Path, default=Path("fine_tuning"),
                   help="Output directory for converted files.")
    p.add_argument("--system-prompt", type=Path, default=None,
                   help="Path to a .txt file containing a custom system prompt. "
                        "If not provided, uses the built-in default.")
    p.add_argument("--max-total-tokens", type=int, default=16384,
                   help="Drop examples exceeding this total token count (default: 16384).")
    p.add_argument("--validate-only", action="store_true",
                   help="Only validate an existing output file (checks format + token counts).")
    p.add_argument("--validate-file", type=Path, default=None,
                   help="File to validate (used with --validate-only).")
    p.add_argument("--no-tiktoken", action="store_true",
                   help="Skip token counting (if tiktoken is not installed).")
    return p.parse_args(argv)


def load_jsonl_dir(directory: Path, suffix: str) -> list[dict[str, Any]]:
    """Load all *_{suffix}.jsonl files from a directory."""
    rows: list[dict[str, Any]] = []
    for jf in sorted(directory.glob(f"*_{suffix}.jsonl")):
        note_id = jf.stem.replace(f"_{suffix}", "")
        for i, line in enumerate(jf.open("r", encoding="utf-8")):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            row["_note_id"] = note_id
            row["_example_idx"] = i
            rows.append(row)
    return rows


def to_openai_chat(row: dict[str, Any], system_prompt: str) -> dict[str, Any]:
    """Convert a prompt/completion pair to OpenAI chat fine-tuning format."""
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": row["prompt"]},
            {"role": "assistant", "content": row["completion"]},
        ]
    }


def count_tokens(text: str, enc: Any) -> int:
    """Count tokens using tiktoken encoder."""
    return len(enc.encode(text))


def estimate_message_tokens(messages: list[dict], enc: Any) -> int:
    """Estimate token count for a chat message list (OpenAI overhead included)."""
    # Per OpenAI docs: every message adds ~4 tokens overhead
    total = 3  # <|start|>assistant<|message|> priming
    for msg in messages:
        total += 4  # message overhead
        total += count_tokens(msg["content"], enc)
    return total


def write_jsonl(rows: list[dict], path: Path) -> None:
    """Write rows to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def validate_file(path: Path, enc: Any | None = None) -> dict[str, Any]:
    """Validate an OpenAI fine-tuning JSONL file."""
    errors: list[str] = []
    warnings: list[str] = []
    token_counts: list[int] = []
    n = 0

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON: {e}")
                continue

            # Check structure
            if "messages" not in row:
                errors.append(f"Line {line_num}: Missing 'messages' key")
                continue

            msgs = row["messages"]
            if not isinstance(msgs, list) or len(msgs) < 2:
                errors.append(f"Line {line_num}: 'messages' must be a list with >= 2 entries")
                continue

            roles = [m.get("role") for m in msgs]
            if roles[-1] != "assistant":
                errors.append(f"Line {line_num}: Last message must be 'assistant', got '{roles[-1]}'")

            if roles[0] not in ("system", "user"):
                errors.append(f"Line {line_num}: First message must be 'system' or 'user'")

            for i, msg in enumerate(msgs):
                if "content" not in msg:
                    errors.append(f"Line {line_num}: Message {i} missing 'content'")
                elif not msg["content"].strip():
                    warnings.append(f"Line {line_num}: Message {i} has empty content")

            # Token count
            if enc:
                toks = estimate_message_tokens(msgs, enc)
                token_counts.append(toks)

    result: dict[str, Any] = {
        "file": str(path),
        "examples": n,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    if errors:
        result["error_details"] = errors[:20]
    if warnings:
        result["warning_details"] = warnings[:10]
    if token_counts:
        result["token_stats"] = {
            "min": min(token_counts),
            "max": max(token_counts),
            "avg": round(sum(token_counts) / len(token_counts)),
            "median": sorted(token_counts)[len(token_counts) // 2],
            "total": sum(token_counts),
            "over_4k": sum(1 for t in token_counts if t > 4096),
            "over_8k": sum(1 for t in token_counts if t > 8192),
            "over_16k": sum(1 for t in token_counts if t > 16384),
        }

    return result


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # Optional tiktoken
    enc = None
    if not args.no_tiktoken:
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model("gpt-4o-mini")
        except ImportError:
            print("Warning: tiktoken not installed. Skipping token counts.")
            print("  Install with: pip install tiktoken")

    # ── Validate-only mode ──
    if args.validate_only:
        target = args.validate_file or args.output_dir / "reporter_ft_train.jsonl"
        if not target.exists():
            print(f"File not found: {target}")
            return 1
        result = validate_file(target, enc)
        print(json.dumps(result, indent=2))
        return 0 if result["errors"] == 0 else 1

    # ── Load data ──
    if not args.input.is_dir():
        print(f"Input directory not found: {args.input}")
        print("Expected: directory containing note_XXX_train.jsonl / note_XXX_valid.jsonl files")
        print()
        print("If you haven't generated the JSONL files yet, run:")
        print(f"  cd {args.input.parent} && ./run_all_python.sh")
        return 1

    print(f"Loading training data from: {args.input}")
    train_rows = load_jsonl_dir(args.input, "train")
    valid_rows = load_jsonl_dir(args.input, "valid")

    if not train_rows:
        print("ERROR: No training examples found. Check the input directory.")
        return 1

    print(f"  Train examples: {len(train_rows)}")
    print(f"  Valid examples: {len(valid_rows)}")

    # ── Load system prompt ──
    if args.system_prompt and args.system_prompt.exists():
        system_prompt = args.system_prompt.read_text("utf-8").strip()
        print(f"  System prompt: {args.system_prompt} ({len(system_prompt)} chars)")
    else:
        system_prompt = DEFAULT_SYSTEM_PROMPT
        print(f"  System prompt: built-in default ({len(system_prompt)} chars)")

    # ── Convert ──
    print("\nConverting to OpenAI chat format...")
    train_converted: list[dict] = []
    valid_converted: list[dict] = []
    dropped = 0
    note_ids_seen: set[str] = set()
    proc_type_counts: Counter = Counter()

    for row in train_rows:
        chat = to_openai_chat(row, system_prompt)
        if enc:
            toks = estimate_message_tokens(chat["messages"], enc)
            if toks > args.max_total_tokens:
                dropped += 1
                continue
        train_converted.append(chat)
        note_ids_seen.add(row["_note_id"])

    for row in valid_rows:
        chat = to_openai_chat(row, system_prompt)
        if enc:
            toks = estimate_message_tokens(chat["messages"], enc)
            if toks > args.max_total_tokens:
                dropped += 1
                continue
        valid_converted.append(chat)

    print(f"  Converted: {len(train_converted)} train, {len(valid_converted)} valid")
    if dropped:
        print(f"  Dropped (>{args.max_total_tokens} tokens): {dropped}")

    # ── Write output ──
    train_path = args.output_dir / "reporter_ft_train.jsonl"
    valid_path = args.output_dir / "reporter_ft_valid.jsonl"

    write_jsonl(train_converted, train_path)
    write_jsonl(valid_converted, valid_path)
    print(f"\nWrote: {train_path}")
    print(f"Wrote: {valid_path}")

    # ── Token stats + manifest ──
    manifest: dict[str, Any] = {
        "created_by": "prepare_finetune.py",
        "train_file": str(train_path),
        "valid_file": str(valid_path),
        "train_examples": len(train_converted),
        "valid_examples": len(valid_converted),
        "dropped_examples": dropped,
        "unique_note_ids": len(note_ids_seen),
        "system_prompt_length_chars": len(system_prompt),
    }

    if enc:
        print("\nComputing token statistics...")
        train_toks = [estimate_message_tokens(r["messages"], enc) for r in train_converted]
        valid_toks = [estimate_message_tokens(r["messages"], enc) for r in valid_converted]
        total_train = sum(train_toks)
        total_valid = sum(valid_toks)

        manifest["token_stats"] = {
            "train": {
                "min": min(train_toks), "max": max(train_toks),
                "avg": round(sum(train_toks) / len(train_toks)),
                "median": sorted(train_toks)[len(train_toks) // 2],
                "total": total_train,
            },
            "valid": {
                "min": min(valid_toks), "max": max(valid_toks),
                "avg": round(sum(valid_toks) / len(valid_toks)),
                "median": sorted(valid_toks)[len(valid_toks) // 2],
                "total": total_valid,
            },
        }

        # Cost estimates
        cost_per_1m = {"gpt-4o-mini-2024-07-18": 0.30, "gpt-4o-2024-08-06": 3.00}
        manifest["cost_estimates"] = {}
        for model, price in cost_per_1m.items():
            for epochs in [2, 3, 4]:
                key = f"{model}_{epochs}ep"
                manifest["cost_estimates"][key] = f"${total_train * epochs * price / 1_000_000:.2f}"

        print(f"  Train tokens: {total_train:,} (avg {sum(train_toks)//len(train_toks)} per example)")
        print(f"  Valid tokens: {total_valid:,}")
        print(f"\n  Estimated fine-tuning costs:")
        for k, v in manifest["cost_estimates"].items():
            print(f"    {k}: {v}")

    manifest_path = args.output_dir / "reporter_ft_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"\nWrote manifest: {manifest_path}")

    # ── Validate ──
    print("\nValidating output files...")
    for p in [train_path, valid_path]:
        result = validate_file(p, enc)
        status = "PASS" if result["errors"] == 0 else "FAIL"
        print(f"  {p.name}: {status} ({result['examples']} examples, {result['errors']} errors)")
        if result["errors"] > 0:
            for e in result.get("error_details", [])[:5]:
                print(f"    {e}")

    # ── Next steps ──
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"""
1. Upload and start fine-tuning:

   python launch_finetune.py

   Or manually via the OpenAI API:

   openai api fine_tuning.jobs.create \\
     -m gpt-4o-mini-2024-07-18 \\
     -t {train_path} \\
     -v {valid_path} \\
     --suffix reporter-v1

2. Monitor the job:

   python launch_finetune.py --status

3. After training completes, evaluate:

   python eval_finetune.py --model ft:gpt-4o-mini-2024-07-18:your-org::jobid
""")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
