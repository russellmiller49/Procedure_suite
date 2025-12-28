#!/usr/bin/env python3
"""
Export pure Prodigy annotations to Gold Standard training format.

Unlike prodigy_export_corrections.py, this script does NOT merge with
any existing data. It exports only human-verified Prodigy annotations,
creating a pure "Gold Standard" dataset.

Usage:
    python scripts/export_phi_gold_standard.py \
        --dataset phi_corrections \
        --output data/ml_training/phi_gold_standard_v1.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from transformers import AutoTokenizer

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_MODEL_DIR = Path("artifacts/phi_distilbert_ner")
DEFAULT_OUTPUT = Path("data/ml_training/phi_gold_standard_v1.jsonl")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Prodigy dataset name to export")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSONL file")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Tokenizer directory")
    return parser.parse_args(argv)


def load_prodigy_annotations(dataset_name: str) -> List[Dict[str, Any]]:
    """Load annotations from Prodigy database."""
    try:
        from prodigy.components.db import connect

        db = connect()
        if dataset_name not in db:
            logger.error(f"Dataset '{dataset_name}' not found in Prodigy database")
            logger.info(f"Available datasets: {db.datasets}")
            return []

        examples = db.get_dataset_examples(dataset_name)
        logger.info(f"Loaded {len(examples)} annotations from Prodigy dataset '{dataset_name}'")
        return examples

    except ImportError:
        logger.error("Prodigy not installed. Install with: pip install prodigy")
        return []
    except Exception as e:
        logger.error(f"Failed to load Prodigy annotations: {e}")
        return []


def spans_to_bio(
    text: str,
    spans: List[Dict[str, Any]],
    tokenizer: Any,
) -> Tuple[List[str], List[str]]:
    """
    Convert character spans to BIO tags aligned to tokenizer output.

    Args:
        text: The original text
        spans: List of spans with start, end, label
        tokenizer: The tokenizer to use for alignment

    Returns:
        (tokens, ner_tags) tuple
    """
    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
    )

    offset_mapping = encoding.get("offset_mapping", [])
    input_ids = encoding.get("input_ids", [])

    # Convert input_ids back to tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Initialize all tags as O
    ner_tags = ["O"] * len(tokens)

    # Skip special tokens (CLS, SEP)
    # Special tokens have offset (0, 0)
    valid_indices = []
    for idx, offset in enumerate(offset_mapping):
        if offset[0] != 0 or offset[1] != 0:
            valid_indices.append(idx)

    # Sort spans by start position
    sorted_spans = sorted(spans, key=lambda s: s.get("start", 0))

    # Assign BIO tags based on spans
    for span in sorted_spans:
        span_start = span.get("start", 0)
        span_end = span.get("end", 0)
        label = span.get("label", "UNKNOWN")

        # Find tokens that overlap with this span
        is_first = True
        for idx in valid_indices:
            tok_start, tok_end = offset_mapping[idx]

            # Check if token overlaps with span
            if tok_start < span_end and tok_end > span_start:
                if is_first:
                    ner_tags[idx] = f"B-{label}"
                    is_first = False
                else:
                    ner_tags[idx] = f"I-{label}"

    # Filter out special tokens for output
    filtered_tokens = []
    filtered_tags = []
    for idx, (token, tag) in enumerate(zip(tokens, ner_tags)):
        offset = offset_mapping[idx] if idx < len(offset_mapping) else (0, 0)
        if offset[0] != 0 or offset[1] != 0:
            filtered_tokens.append(token)
            filtered_tags.append(tag)

    return filtered_tokens, filtered_tags


def convert_annotation(
    example: Dict[str, Any],
    tokenizer: Any,
    dataset_name: str,
) -> Optional[Dict[str, Any]]:
    """Convert a single Prodigy annotation to training format."""
    text = example.get("text", "")
    if not text:
        return None

    # Get all spans (in ner.correct, all spans in the output are the final result)
    spans = example.get("spans", [])

    # Convert to BIO
    tokens, ner_tags = spans_to_bio(text, spans, tokenizer)

    if not tokens:
        return None

    # Extract metadata
    meta = example.get("meta", {})
    source = meta.get("source", "unknown")
    record_index = meta.get("record_index", 0)
    window_index = meta.get("window_index", 0)
    window_start = meta.get("window_start", 0)
    window_end = meta.get("window_end", len(text))

    # Build ID matching distilled format
    id_str = f"{source}:{record_index}:{window_index}"
    id_base = f"{source}:{record_index}"

    return {
        "id": id_str,
        "id_base": id_base,
        "source_path": f"prodigy:{dataset_name}",
        "record_index": record_index,
        "window_start": window_start,
        "window_end": window_end,
        "text": text,
        "tokens": tokens,
        "ner_tags": ner_tags,
        "origin": "gold-standard",
        "prodigy_dataset": dataset_name,
        "annotated_at": datetime.now().isoformat(),
    }


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load tokenizer
    if not args.model_dir.exists():
        logger.error(f"Model directory not found: {args.model_dir}")
        return 1

    logger.info(f"Loading tokenizer from {args.model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(str(args.model_dir))

    # Load Prodigy annotations
    annotations = load_prodigy_annotations(args.dataset)
    if not annotations:
        logger.error("No annotations to export")
        return 1

    # Convert annotations to training format (only accepted examples)
    converted = []
    rejected_count = 0
    for example in annotations:
        # Only export accepted examples (answer == "accept")
        if example.get("answer") != "accept":
            rejected_count += 1
            continue

        record = convert_annotation(example, tokenizer, args.dataset)
        if record:
            converted.append(record)

    logger.info(f"Converted {len(converted)} accepted annotations")
    logger.info(f"Skipped {rejected_count} rejected/ignored annotations")

    if not converted:
        logger.warning("No valid annotations to export")
        return 0

    # Count label distribution
    label_counts: Dict[str, int] = {}
    for rec in converted:
        for tag in rec.get("ner_tags", []):
            if tag != "O":
                label_counts[tag] = label_counts.get(tag, 0) + 1
    logger.info(f"Label distribution: {label_counts}")

    # Count unique notes (id_base)
    unique_notes = set(rec["id_base"] for rec in converted)
    logger.info(f"Unique notes (id_base): {len(unique_notes)}")
    logger.info(f"Total windows: {len(converted)}")

    # Write output (pure gold, no merging)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for record in converted:
            f.write(json.dumps(record) + "\n")

    logger.info(f"Wrote {len(converted)} gold standard records to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
