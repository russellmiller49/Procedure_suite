#!/usr/bin/env python3
"""
Export Prodigy annotations to training format.

Converts Prodigy NER annotations back to BIO-tagged JSONL format
compatible with the DistilBERT training pipeline.

Usage:
    python ml/scripts/prodigy_export_corrections.py --dataset phi_corrections --output data/ml_training/prodigy_corrected.jsonl

    # With merge into existing training data:
    python ml/scripts/prodigy_export_corrections.py --dataset phi_corrections \
        --merge-with data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
        --output data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from transformers import AutoTokenizer

# Add repo root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_MODEL_DIR = Path("artifacts/phi_distilbert_ner")
DEFAULT_OUTPUT = Path("data/ml_training/prodigy_corrected.jsonl")
DEFAULT_MANIFEST = Path("data/ml_training/prodigy_manifest.json")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Prodigy dataset name to export")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSONL file")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Tokenizer directory")
    parser.add_argument("--merge-with", type=Path, default=None, help="Existing training data to merge with")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Manifest file to update")
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

    # Get accepted spans (Prodigy marks rejected spans)
    spans = []
    for span in example.get("spans", []):
        # In ner.correct, all spans in the final output are accepted
        spans.append(span)

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
        "origin": "prodigy-corrected",
        "prodigy_dataset": dataset_name,
        "annotated_at": datetime.now().isoformat(),
    }


def load_existing_data(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load existing training data into a dict keyed by id."""
    data = {}
    if not path.exists():
        return data

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                record_id = record.get("id", "")
                if record_id:
                    data[record_id] = record
            except json.JSONDecodeError:
                continue

    logger.info(f"Loaded {len(data)} existing records from {path}")
    return data


def merge_data(
    existing: Dict[str, Dict[str, Any]],
    corrections: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Merge corrections into existing data using replace strategy.

    Corrections completely replace existing records with matching IDs.
    """
    # Build a dict of corrections by ID
    corrections_by_id = {}
    for rec in corrections:
        record_id = rec.get("id", "")
        if record_id:
            corrections_by_id[record_id] = rec

    # Replace matching records
    replaced_count = 0
    for record_id in corrections_by_id:
        if record_id in existing:
            replaced_count += 1

    # Merge: start with existing, override with corrections
    merged = {**existing, **corrections_by_id}

    logger.info(f"Merged {len(corrections)} corrections into {len(existing)} existing records")
    logger.info(f"Replaced {replaced_count} existing records, added {len(corrections) - replaced_count} new records")

    # Return as list, preserving order from existing where possible
    result = []
    seen_ids: Set[str] = set()

    # First, add all existing in order (with corrections applied)
    for record_id in existing:
        if record_id in merged:
            result.append(merged[record_id])
            seen_ids.add(record_id)

    # Then add any new corrections not in existing
    for rec in corrections:
        record_id = rec.get("id", "")
        if record_id and record_id not in seen_ids:
            result.append(rec)

    return result


def update_manifest(manifest_path: Path, dataset_name: str, output_path: Path, count: int) -> None:
    """Update the manifest with export info."""
    manifest = {"batches": [], "annotated_windows": []}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        except Exception:
            pass

    # Find the batch for this dataset and update status
    for batch in manifest.get("batches", []):
        if batch.get("prodigy_dataset") == dataset_name:
            batch["status"] = "exported"
            batch["export_file"] = str(output_path)
            batch["exported_at"] = datetime.now().isoformat()
            batch["exported_count"] = count
            break

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


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

    # Convert annotations to training format
    converted = []
    for example in annotations:
        # Only export accepted examples (answer == "accept")
        if example.get("answer") != "accept":
            continue

        record = convert_annotation(example, tokenizer, args.dataset)
        if record:
            converted.append(record)

    logger.info(f"Converted {len(converted)} annotations to training format")

    if not converted:
        logger.warning("No valid annotations to export")
        return 0

    # Count label distribution
    label_counts: Dict[str, int] = {}
    for rec in converted:
        for tag in rec.get("ner_tags", []):
            if tag != "O":
                label_counts[tag] = label_counts.get(tag, 0) + 1
    logger.info(f"Label distribution in corrections: {label_counts}")

    # Merge with existing data if requested
    if args.merge_with:
        existing = load_existing_data(args.merge_with)
        merged = merge_data(existing, converted)
        output_data = merged
    else:
        output_data = converted

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for record in output_data:
            f.write(json.dumps(record) + "\n")

    logger.info(f"Wrote {len(output_data)} records to {args.output}")

    # Update manifest
    update_manifest(args.manifest, args.dataset, args.output, len(converted))

    return 0


if __name__ == "__main__":
    sys.exit(main())
