#!/usr/bin/env python3
"""
Prepare a batch of golden notes for Prodigy annotation.

Samples golden notes, runs DistilBERT inference to pre-annotate PHI spans,
and outputs Prodigy-compatible JSONL format.

Usage:
    python scripts/prodigy_prepare_phi_batch.py --count 100 --output data/ml_training/prodigy_batch.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

# Add repo root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_GOLDEN_DIR = Path("data/knowledge/golden_extractions")
DEFAULT_MODEL_DIR = Path("artifacts/phi_distilbert_ner")
DEFAULT_OUTPUT = Path("data/ml_training/prodigy_batch.jsonl")
DEFAULT_MANIFEST = Path("data/ml_training/prodigy_manifest.json")

# Windowing config
WINDOW_CHARS = 2000
OVERLAP_CHARS = 200


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100, help="Number of notes to sample")
    parser.add_argument("--golden-dir", type=Path, default=DEFAULT_GOLDEN_DIR, help="Golden notes directory")
    parser.add_argument("--input-file", type=Path, default=None, help="Single JSONL file to use instead of golden-dir")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Trained model directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSONL file")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Manifest file for tracking")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--window-chars", type=int, default=WINDOW_CHARS, help="Window size in characters")
    parser.add_argument("--overlap-chars", type=int, default=OVERLAP_CHARS, help="Overlap between windows")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda/mps/cpu)")
    return parser.parse_args(argv)


def iter_golden_files(golden_dir: Path) -> List[Path]:
    """Iterate over golden extraction JSON files."""
    patterns = [
        "golden_*.json",
        "consolidated_verified_notes_v2_8_part_*.json",
        "synthetic_*.json",
    ]
    files: List[Path] = []
    for pattern in patterns:
        files.extend(golden_dir.glob(pattern))
    # Also include JSONL files
    files.extend(golden_dir.glob("*.jsonl"))

    # Dedupe
    seen: set[Path] = set()
    unique: List[Path] = []
    for p in sorted(files):
        if p in seen:
            continue
        seen.add(p)
        unique.append(p)
    return unique


def flatten_entries(data: Any) -> List[Dict[str, Any]]:
    """Flatten entries from various JSON structures."""
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    elif isinstance(data, dict):
        entries = []
        for key, value in data.items():
            if key == "metadata":
                continue
            if isinstance(value, list):
                entries.extend([e for e in value if isinstance(e, dict)])
        return entries
    return []


def get_note_text(entry: Dict[str, Any]) -> str | None:
    """Get note text from entry, checking both 'note_text' and 'text' fields."""
    return entry.get("note_text") or entry.get("text")


def load_golden_notes(golden_dir: Path) -> List[Dict[str, Any]]:
    """Load all golden notes with their source file info."""
    notes = []
    for file_path in iter_golden_files(golden_dir):
        try:
            if file_path.suffix == ".jsonl":
                with open(file_path, "r") as f:
                    for line_num, line in enumerate(f):
                        line = line.strip()
                        if not line:
                            continue
                        entry = json.loads(line)
                        if isinstance(entry, dict) and get_note_text(entry):
                            entry["_source_file"] = file_path.name
                            entry["_record_index"] = line_num
                            notes.append(entry)
            else:
                with open(file_path, "r") as f:
                    data = json.load(f)
                entries = flatten_entries(data)
                for idx, entry in enumerate(entries):
                    if get_note_text(entry):
                        entry["_source_file"] = file_path.name
                        entry["_record_index"] = idx
                        notes.append(entry)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
    return notes


def load_notes_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load notes from a single JSONL file."""
    notes = []
    try:
        with open(file_path, "r") as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if isinstance(entry, dict) and get_note_text(entry):
                    entry["_source_file"] = file_path.name
                    entry["_record_index"] = line_num
                    notes.append(entry)
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
    return notes


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load the annotation manifest to track already-annotated notes."""
    if not manifest_path.exists():
        return {"batches": [], "annotated_windows": []}
    try:
        with open(manifest_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load manifest: {e}")
        return {"batches": [], "annotated_windows": []}


def save_manifest(manifest_path: Path, manifest: Dict[str, Any]) -> None:
    """Save the annotation manifest."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def window_text(text: str, window_chars: int, overlap_chars: int) -> List[Tuple[int, int, str]]:
    """Split text into overlapping windows."""
    if not text or window_chars <= 0:
        return []
    overlap_chars = max(0, overlap_chars)
    step = max(window_chars - overlap_chars, 1)
    windows: List[Tuple[int, int, str]] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + window_chars, text_len)
        windows.append((start, end, text[start:end]))
        if end >= text_len:
            break
        start += step
    return windows


def load_model(model_dir: Path, device: torch.device) -> Tuple[Any, Any, Dict[int, str]]:
    """Load the trained DistilBERT model and tokenizer."""
    logger.info(f"Loading model from {model_dir}")

    model = AutoModelForTokenClassification.from_pretrained(str(model_dir))
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model.to(device)
    model.eval()

    # Load label mapping
    label_map_path = model_dir / "label_map.json"
    if label_map_path.exists():
        with open(label_map_path, "r") as f:
            label_data = json.load(f)
        id2label = {int(k): v for k, v in label_data.get("id2label", {}).items()}
    else:
        # Fallback to model config
        id2label = {int(k): v for k, v in model.config.id2label.items()}

    return model, tokenizer, id2label


def run_inference(
    text: str,
    tokenizer: Any,
    model: Any,
    id2label: Dict[int, str],
    device: torch.device,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Run inference on text and return both tokens and predicted spans.

    Returns:
        (tokens, spans) where:
        - tokens: List of {"text": str, "start": int, "end": int, "id": int}
        - spans: List of {"start": int, "end": int, "label": str, "token_start": int, "token_end": int}
    """
    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
        return_attention_mask=True,
    )

    offset_mapping = encoding.pop("offset_mapping")[0].tolist()  # List of (start, end) tuples

    # Move to device
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    # Run inference
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    logits = outputs.logits
    pred_ids = logits.argmax(-1).squeeze(0).tolist()

    # Skip CLS and SEP tokens
    # offset_mapping[0] is CLS, offset_mapping[-1] is SEP
    tokens_list = []
    pred_labels = []

    for idx, (offset, pred_id) in enumerate(zip(offset_mapping, pred_ids)):
        start, end = offset
        if start == 0 and end == 0:
            # Special token (CLS or SEP) - skip
            continue

        token_text = text[start:end]
        tokens_list.append({
            "text": token_text,
            "start": start,
            "end": end,
            "id": len(tokens_list),
        })
        pred_labels.append(id2label.get(pred_id, "O"))

    # Convert BIO labels to spans
    spans = bio_to_spans(tokens_list, pred_labels)

    return tokens_list, spans


def bio_to_spans(
    tokens: List[Dict[str, Any]],
    labels: List[str],
) -> List[Dict[str, Any]]:
    """Convert BIO labels to character spans."""
    spans = []
    current_span = None

    for idx, (token, label) in enumerate(zip(tokens, labels)):
        if label.startswith("B-"):
            # Start new span
            if current_span is not None:
                spans.append(current_span)
            entity_type = label[2:]
            current_span = {
                "start": token["start"],
                "end": token["end"],
                "label": entity_type,
                "token_start": idx,
                "token_end": idx,
            }
        elif label.startswith("I-") and current_span is not None:
            # Continue current span if same type
            entity_type = label[2:]
            if entity_type == current_span["label"]:
                current_span["end"] = token["end"]
                current_span["token_end"] = idx
            else:
                # Type mismatch - end current span, start new
                spans.append(current_span)
                current_span = {
                    "start": token["start"],
                    "end": token["end"],
                    "label": entity_type,
                    "token_start": idx,
                    "token_end": idx,
                }
        elif label == "O":
            # End current span if any
            if current_span is not None:
                spans.append(current_span)
                current_span = None
        else:
            # I- tag without B- - treat as B-
            if current_span is not None:
                spans.append(current_span)
            if label.startswith("I-"):
                entity_type = label[2:]
                current_span = {
                    "start": token["start"],
                    "end": token["end"],
                    "label": entity_type,
                    "token_start": idx,
                    "token_end": idx,
                }
            else:
                current_span = None

    # Don't forget the last span
    if current_span is not None:
        spans.append(current_span)

    return spans


def process_note(
    note: Dict[str, Any],
    tokenizer: Any,
    model: Any,
    id2label: Dict[int, str],
    device: torch.device,
    window_chars: int,
    overlap_chars: int,
    batch_id: str,
) -> List[Dict[str, Any]]:
    """Process a single note into Prodigy examples."""
    text = get_note_text(note)
    if not text:
        return []

    source_file = note.get("_source_file", "unknown")
    record_index = note.get("_record_index", 0)

    examples = []
    windows = window_text(text, window_chars, overlap_chars)

    for window_idx, (start, end, window_text_content) in enumerate(windows):
        # Run inference on window
        tokens, spans = run_inference(window_text_content, tokenizer, model, id2label, device)

        # Create Prodigy example
        example = {
            "text": window_text_content,
            "spans": spans,
            "tokens": tokens,
            "meta": {
                "source": source_file,
                "record_index": record_index,
                "window_index": window_idx,
                "window_start": start,
                "window_end": end,
                "batch_id": batch_id,
            },
        }
        examples.append(example)

    return examples


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Set random seed
    if args.seed is not None:
        random.seed(args.seed)

    # Determine device
    if args.device:
        device = torch.device(args.device)
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    logger.info(f"Using device: {device}")

    # Load model
    if not args.model_dir.exists():
        logger.error(f"Model directory not found: {args.model_dir}")
        return 1
    model, tokenizer, id2label = load_model(args.model_dir, device)
    logger.info(f"Loaded model with labels: {list(id2label.values())}")

    # Load notes from input file or golden directory
    if args.input_file:
        if not args.input_file.exists():
            logger.error(f"Input file not found: {args.input_file}")
            return 1
        logger.info(f"Loading notes from {args.input_file}")
        all_notes = load_notes_from_file(args.input_file)
    else:
        logger.info(f"Loading golden notes from {args.golden_dir}")
        all_notes = load_golden_notes(args.golden_dir)
    logger.info(f"Found {len(all_notes)} total notes")

    # Load manifest to get already-annotated notes
    manifest = load_manifest(args.manifest)
    annotated_ids = set(manifest.get("annotated_windows", []))

    # Filter out already-annotated notes
    def note_id(note: Dict[str, Any]) -> str:
        return f"{note.get('_source_file', 'unknown')}:{note.get('_record_index', 0)}"

    available_notes = [n for n in all_notes if not any(
        wid.startswith(note_id(n)) for wid in annotated_ids
    )]
    logger.info(f"Available notes after filtering: {len(available_notes)}")

    if len(available_notes) == 0:
        logger.warning("No available notes to sample. All notes may have been annotated.")
        return 0

    # Sample notes
    sample_count = min(args.count, len(available_notes))
    sampled_notes = random.sample(available_notes, sample_count)
    logger.info(f"Sampled {sample_count} notes")

    # Generate batch ID
    batch_id = datetime.now().strftime("%Y-%m-%d_batch_%H%M%S")

    # Process notes and generate examples
    all_examples = []
    new_window_ids = []

    for note in sampled_notes:
        examples = process_note(
            note, tokenizer, model, id2label, device,
            args.window_chars, args.overlap_chars, batch_id
        )
        for ex in examples:
            window_id = f"{ex['meta']['source']}:{ex['meta']['record_index']}:{ex['meta']['window_index']}"
            new_window_ids.append(window_id)
        all_examples.extend(examples)

    logger.info(f"Generated {len(all_examples)} examples from {sample_count} notes")

    # Count spans by label
    span_counts: Dict[str, int] = {}
    for ex in all_examples:
        for span in ex.get("spans", []):
            label = span.get("label", "UNKNOWN")
            span_counts[label] = span_counts.get(label, 0) + 1
    logger.info(f"Span counts by label: {span_counts}")

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex) + "\n")
    logger.info(f"Wrote {len(all_examples)} examples to {args.output}")

    # Update manifest
    manifest["batches"].append({
        "batch_id": batch_id,
        "created_at": datetime.now().isoformat(),
        "notes_count": sample_count,
        "windows_count": len(all_examples),
        "source_file": str(args.output),
        "status": "pending",
    })
    manifest["annotated_windows"].extend(new_window_ids)
    save_manifest(args.manifest, manifest)
    logger.info(f"Updated manifest at {args.manifest}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
