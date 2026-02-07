#!/usr/bin/env python3
"""
Convert character-span NER annotations to BIO-tagged format for training.

Input format (ner_dataset_all.jsonl):
{
  "id": "note_001",
  "text": "Full procedure note text...",
  "entities": [
    {"start": 100, "end": 102, "label": "ANAT_LN_STATION", "text": "4R"},
    ...
  ]
}

Output format (for train_registry_ner.py):
{
  "id": "note_001",
  "tokens": ["station", "4", "##r", "was", "sampled", ...],
  "ner_tags": ["O", "B-ANAT_LN_STATION", "I-ANAT_LN_STATION", "O", "O", ...]
}

Usage:
    python ml/scripts/convert_spans_to_bio.py \
        --input data/ml_training/granular_ner/ner_dataset_all.jsonl \
        --output data/ml_training/granular_ner/ner_bio_format.jsonl \
        --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from transformers import AutoTokenizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input JSONL file with character-span annotations"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output JSONL file with BIO-tagged tokens"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext",
        help="Tokenizer model name (default: microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help="Maximum sequence length (default: 512)"
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=None,
        help="If set, split long texts into overlapping windows of this many chars"
    )
    parser.add_argument(
        "--window-overlap",
        type=int,
        default=200,
        help="Overlap between windows in characters (default: 200)"
    )
    return parser.parse_args(argv)


def normalize_entity(entity: Any) -> Dict[str, Any]:
    """
    Normalize entity to dict format.

    Handles both formats:
    - Dict: {"start": 100, "end": 102, "label": "ANAT_LN_STATION", "text": "4R"}
    - List: [100, 102, "ANAT_LN_STATION"] or [100, 102, "ANAT_LN_STATION", "4R"]
    """
    if isinstance(entity, dict):
        start = entity.get("start")
        end = entity.get("end")
        if start is None:
            start = entity.get("start_char", entity.get("start_offset", 0))
        if end is None:
            end = entity.get("end_char", entity.get("end_offset", 0))
        text = entity.get("text")
        if text is None:
            text = entity.get("span_text", "")
        return {
            "start": start,
            "end": end,
            "label": entity.get("label", "UNKNOWN"),
            "text": text or "",
        }
    elif isinstance(entity, (list, tuple)):
        if len(entity) >= 3:
            return {
                "start": entity[0],
                "end": entity[1],
                "label": entity[2],
                "text": entity[3] if len(entity) > 3 else "",
            }
    return {"start": 0, "end": 0, "label": "UNKNOWN", "text": ""}


def spans_to_bio(
    text: str,
    entities: List[Any],
    tokenizer: Any,
    max_length: int = 512,
) -> Tuple[List[str], List[str]]:
    """
    Convert character spans to BIO tags aligned to tokenizer output.

    Args:
        text: The original text
        entities: List of entities (dict or list format)
        tokenizer: The tokenizer to use for alignment
        max_length: Maximum sequence length

    Returns:
        (tokens, ner_tags) tuple with special tokens filtered out
    """
    # Normalize all entities to dict format
    normalized_entities = [normalize_entity(e) for e in entities]

    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=max_length,
        return_offsets_mapping=True,
        add_special_tokens=True,
    )

    offset_mapping = encoding.get("offset_mapping", [])
    input_ids = encoding.get("input_ids", [])

    # Convert input_ids back to tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Initialize all tags as O
    ner_tags = ["O"] * len(tokens)

    # Find valid token indices (non-special tokens)
    # Special tokens like [CLS], [SEP] have offset (0, 0)
    valid_indices = []
    for idx, offset in enumerate(offset_mapping):
        if offset[0] != offset[1]:  # Has non-zero span
            valid_indices.append(idx)

    # Sort entities by start position
    sorted_entities = sorted(normalized_entities, key=lambda e: e.get("start", 0))

    # Assign BIO tags based on entity spans
    for entity in sorted_entities:
        span_start = entity.get("start", 0)
        span_end = entity.get("end", 0)
        label = entity.get("label", "UNKNOWN")

        # Find tokens that overlap with this entity span
        is_first = True
        for idx in valid_indices:
            tok_start, tok_end = offset_mapping[idx]

            # Check if token overlaps with entity span
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
        # Include tokens with actual character spans
        if offset[0] != offset[1]:
            filtered_tokens.append(token)
            filtered_tags.append(tag)

    return filtered_tokens, filtered_tags


def split_into_windows(
    text: str,
    entities: List[Any],
    window_size: int,
    window_overlap: int,
) -> List[Tuple[str, List[Dict[str, Any]], int]]:
    """
    Split long text into overlapping windows with adjusted entity spans.

    Returns list of (window_text, adjusted_entities, window_start) tuples.
    """
    # Normalize all entities to dict format
    normalized_entities = [normalize_entity(e) for e in entities]

    windows = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + window_size, text_len)

        # Try to break at a sentence boundary if possible
        if end < text_len:
            # Look for sentence end markers in last 100 chars
            search_region = text[max(end - 100, start):end]
            for marker in [". ", ".\n", "! ", "? "]:
                last_marker = search_region.rfind(marker)
                if last_marker != -1:
                    end = max(end - 100, start) + last_marker + len(marker)
                    break

        window_text = text[start:end]

        # Adjust entity spans to window coordinates
        window_entities = []
        for entity in normalized_entities:
            ent_start = entity.get("start", 0)
            ent_end = entity.get("end", 0)

            # Check if entity overlaps with window
            if ent_start < end and ent_end > start:
                # Clip entity to window boundaries
                adj_start = max(0, ent_start - start)
                adj_end = min(end - start, ent_end - start)

                # Only include if entity has meaningful overlap
                if adj_end > adj_start:
                    window_entities.append({
                        "start": adj_start,
                        "end": adj_end,
                        "label": entity["label"],
                        "text": window_text[adj_start:adj_end],
                    })

        windows.append((window_text, window_entities, start))

        # Move to next window
        if end >= text_len:
            break
        start = end - window_overlap

    return windows


def convert_record(
    record: Dict[str, Any],
    tokenizer: Any,
    max_length: int,
    window_size: int | None,
    window_overlap: int,
) -> List[Dict[str, Any]]:
    """
    Convert a single record from span format to BIO format.

    May return multiple records if windowing is enabled.
    """
    record_id = record.get("id", "unknown")
    text = record.get("text", "")
    entities = record.get("entities", [])

    if not text:
        return []

    results = []

    if window_size and len(text) > window_size:
        # Split into windows
        windows = split_into_windows(text, entities, window_size, window_overlap)
        for idx, (window_text, window_entities, window_start) in enumerate(windows):
            tokens, ner_tags = spans_to_bio(
                window_text, window_entities, tokenizer, max_length
            )
            if tokens:
                results.append({
                    "id": f"{record_id}:w{idx}",
                    "id_base": record_id,
                    "window_index": idx,
                    "window_start": window_start,
                    "window_end": window_start + len(window_text),
                    "tokens": tokens,
                    "ner_tags": ner_tags,
                })
    else:
        # Process entire text
        tokens, ner_tags = spans_to_bio(text, entities, tokenizer, max_length)
        if tokens:
            results.append({
                "id": record_id,
                "tokens": tokens,
                "ner_tags": ner_tags,
            })

    return results


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load tokenizer
    logger.info(f"Loading tokenizer: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    # Read input
    logger.info(f"Reading input: {args.input}")
    records = []
    with open(args.input, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    logger.info(f"Loaded {len(records)} records")

    # Convert records
    output_records = []
    label_counts = {}
    total_tokens = 0

    for record in records:
        converted = convert_record(
            record,
            tokenizer,
            args.max_length,
            args.window_size,
            args.window_overlap,
        )
        for rec in converted:
            output_records.append(rec)
            total_tokens += len(rec["tokens"])

            # Count labels
            for tag in rec["ner_tags"]:
                if tag != "O":
                    # Extract base label (remove B-/I- prefix)
                    base_label = tag.split("-", 1)[-1] if "-" in tag else tag
                    label_counts[base_label] = label_counts.get(base_label, 0) + 1

    logger.info(f"Generated {len(output_records)} output records")
    logger.info(f"Total tokens: {total_tokens}")
    logger.info(f"Label distribution: {json.dumps(label_counts, indent=2)}")

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for rec in output_records:
            f.write(json.dumps(rec) + "\n")

    logger.info(f"Wrote output to: {args.output}")

    # Write stats
    stats_path = args.output.with_suffix(".stats.json")
    stats = {
        "input_records": len(records),
        "output_records": len(output_records),
        "total_tokens": total_tokens,
        "label_counts": label_counts,
        "model": args.model,
        "max_length": args.max_length,
        "window_size": args.window_size,
        "window_overlap": args.window_overlap,
    }
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    logger.info(f"Wrote stats to: {stats_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
