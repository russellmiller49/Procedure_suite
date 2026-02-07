#!/usr/bin/env python3
"""
Parse reporter examples into a structured JSON dataset for testing.

Usage:
    python scripts/parse_golden_reporter_examples.py \
        --input "ml/data/reporter_examples.txt" \
        --output "tests/fixtures/reporter_golden_dataset.json"
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean artifacts from text chunks."""
    text = text.strip()

    # Remove surrounding quotes often found in the examples (only if paired).
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        text = text[1:-1].strip()

    # Normalize common escaped sequences found in the raw examples.
    # Important: do NOT delete all backslashes, because many inputs encode newlines as "\n".
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
    text = text.replace('\\"', '"').replace("\\'", "'")

    # Normalize line endings.
    text = text.replace("\r\n", "\n")
    return text.strip()

def parse_examples(file_path: Path) -> List[Dict[str, str]]:
    """Parse the raw text file into Input/Output pairs."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    raw_content = file_path.read_text(encoding="utf-8")

    output_marker_re = re.compile(r"(?im)^\s*Output:\s*")
    # Some examples omit the explicit "Output:" separator and jump straight into the report text.
    # Use the common report header as a robust fallback split point.
    report_header_re = re.compile(
        r"(?im)^\s*INTERVENTIONAL\s+PULMONOLOGY\s+OPERATIVE\s+REPORT\b"
    )

    # Split by "Input:" markers at the start of a line (handles file starting with Input:).
    chunks = re.split(r"(?im)^\s*Input:\s*", raw_content)

    examples = []
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        # The first chunk might start with "Input:" if the file starts immediately with it
        # re.split removes the delimiter, so 'chunk' is the content AFTER "Input:"
        
        # Find the "Output:" marker within this chunk (anchored to line start).
        output_match = output_marker_re.search(chunk)
        
        if output_match:
            input_text = clean_text(chunk[:output_match.start()])
            output_text = clean_text(chunk[output_match.end():])
        else:
            header_match = report_header_re.search(chunk)
            if not header_match:
                # Special case for the very first chunk if it contained the first Input header
                # or if formatting is messy. But generally, if no Output, skip or warn.
                print(f"Warning: Chunk {i} missing 'Output:' separator. Skipping.")
                continue

            input_text = clean_text(chunk[:header_match.start()])
            output_text = clean_text(chunk[header_match.start():])
        
        # Heuristic: The output text usually runs until the end of the chunk (next Input)
        # But sometimes there are trailing artifacts. 
        
        examples.append({
            "id": f"example_{len(examples) + 1}",
            "input_text": input_text,
            "ideal_output": output_text
        })

    return examples

def main():
    parser = argparse.ArgumentParser(description="Parse reporter examples into test fixtures.")
    # Backwards-compatible: you can either pass `--input ...` or just run the script
    # with no args (it will default to `ml/data/reporter_examples.txt`).
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path("ml/data/reporter_examples.txt"),
        help='Path to raw txt file (default: "ml/data/reporter_examples.txt")',
    )
    parser.add_argument("--input", dest="input_flag", type=Path, help="Path to raw txt file (overrides positional)")
    parser.add_argument("--output", type=Path, default=Path("tests/fixtures/reporter_golden_dataset.json"), help="Output JSON path")
    
    args = parser.parse_args()
    input_path: Path = args.input_flag if args.input_flag is not None else args.input
    
    print(f"Parsing {input_path}...")
    examples = parse_examples(input_path)
    
    print(f"Found {len(examples)} examples.")
    
    # Ensure output dir exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
        
    print(f"Saved dataset to {args.output}")

if __name__ == "__main__":
    main()
