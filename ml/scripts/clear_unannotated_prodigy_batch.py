#!/usr/bin/env python3
"""
Remove unannotated examples from Prodigy batch file.

This script checks which examples in the batch file have been annotated in Prodigy
and removes those that haven't been annotated yet, keeping only unannotated examples
or removing all unannotated ones (depending on mode).
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Add repo root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_BATCH_FILE = Path("data/ml_training/prodigy_batch.jsonl")
DEFAULT_DATASET = "phi_corrections"


def load_prodigy_annotations(dataset_name: str) -> List[Dict[str, Any]]:
    """Load annotations from Prodigy database."""
    try:
        from prodigy.components.db import connect

        db = connect()
        if dataset_name not in db:
            logger.warning(f"Dataset '{dataset_name}' not found in Prodigy database")
            logger.info(f"Available datasets: {db.datasets}")
            return []

        examples = db.get_dataset_examples(dataset_name)
        logger.info(f"Loaded {len(examples)} annotations from Prodigy dataset '{dataset_name}'")
        return examples
    except ImportError:
        logger.error("Prodigy not installed. Install with: pip install prodigy")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load Prodigy annotations: {e}")
        return []


def get_example_id(example: Dict[str, Any]) -> str:
    """Generate a unique ID for a Prodigy example based on its metadata."""
    meta = example.get("meta", {})
    source = meta.get("source", "unknown")
    record_index = meta.get("record_index", 0)
    window_index = meta.get("window_index", 0)
    return f"{source}:{record_index}:{window_index}"


def load_batch_file(batch_path: Path) -> List[Dict[str, Any]]:
    """Load examples from the batch file."""
    if not batch_path.exists():
        logger.error(f"Batch file not found: {batch_path}")
        sys.exit(1)

    examples = []
    with open(batch_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                example = json.loads(line)
                examples.append(example)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse line: {e}")
                continue

    logger.info(f"Loaded {len(examples)} examples from batch file")
    return examples


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-file",
        type=Path,
        default=DEFAULT_BATCH_FILE,
        help=f"Path to Prodigy batch file (default: {DEFAULT_BATCH_FILE})",
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help=f"Prodigy dataset name (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--mode",
        choices=["remove-unannotated", "keep-unannotated"],
        default="remove-unannotated",
        help="Mode: 'remove-unannotated' removes unannotated examples, 'keep-unannotated' keeps only unannotated (default: remove-unannotated)",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a backup of the original batch file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually modifying the file",
    )
    args = parser.parse_args()

    # Load batch file
    batch_examples = load_batch_file(args.batch_file)
    if not batch_examples:
        logger.warning("No examples in batch file")
        return 0

    # Load Prodigy annotations
    prodigy_examples = load_prodigy_annotations(args.dataset)
    if not prodigy_examples:
        logger.warning(f"No annotations found in dataset '{args.dataset}'")
        if args.mode == "remove-unannotated":
            logger.info("All examples in batch are unannotated. Nothing to remove.")
        else:
            logger.info("All examples in batch are unannotated. Keeping all.")
        return 0

    # Build set of annotated example IDs
    annotated_ids: Set[str] = set()
    for prodigy_ex in prodigy_examples:
        # Check if this example has been accepted (annotated)
        answer = prodigy_ex.get("answer")
        if answer == "accept":
            example_id = get_example_id(prodigy_ex)
            annotated_ids.add(example_id)
        # Also check by text matching as fallback
        prodigy_text = prodigy_ex.get("text", "")
        if prodigy_text:
            for batch_ex in batch_examples:
                batch_text = batch_ex.get("text", "")
                if batch_text == prodigy_text:
                    batch_id = get_example_id(batch_ex)
                    annotated_ids.add(batch_id)

    logger.info(f"Found {len(annotated_ids)} annotated examples in Prodigy")

    # Filter batch examples
    if args.mode == "remove-unannotated":
        # Remove examples that haven't been annotated
        filtered_examples = []
        for batch_ex in batch_examples:
            batch_id = get_example_id(batch_ex)
            if batch_id in annotated_ids:
                filtered_examples.append(batch_ex)
            else:
                logger.debug(f"Removing unannotated example: {batch_id}")
    else:
        # Keep only unannotated examples
        filtered_examples = []
        for batch_ex in batch_examples:
            batch_id = get_example_id(batch_ex)
            if batch_id not in annotated_ids:
                filtered_examples.append(batch_ex)
            else:
                logger.debug(f"Removing annotated example: {batch_id}")

    removed_count = len(batch_examples) - len(filtered_examples)
    logger.info(f"Would {'remove' if args.mode == 'remove-unannotated' else 'keep'} {removed_count} examples")
    logger.info(f"Would keep {len(filtered_examples)} examples")

    if args.dry_run:
        logger.info("DRY RUN: No changes made to batch file")
        return 0

    # Create backup if requested
    if args.backup:
        backup_path = args.batch_file.with_suffix(f".jsonl.backup")
        logger.info(f"Creating backup: {backup_path}")
        import shutil

        shutil.copy2(args.batch_file, backup_path)

    # Write filtered examples
    logger.info(f"Writing {len(filtered_examples)} examples to {args.batch_file}")
    with open(args.batch_file, "w") as f:
        for ex in filtered_examples:
            f.write(json.dumps(ex) + "\n")

    logger.info(f"✓ Updated batch file: removed {removed_count} examples, kept {len(filtered_examples)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
