"""Logging utilities for pretty-printed explanations and export."""
import json
import csv
from typing import List, Dict, Any
from proc_schemas.envelope_models import CodeSuggestion


def explain_codes(codes: List[CodeSuggestion]) -> None:
    for code in codes:
        conf = getattr(code, 'llm_confidence', 0.0)
        rationale = getattr(code, 'reasoning', '')
        print(f"{code.code} ({conf:.2f}): {rationale}")


def export_jsonl(notes: List[Dict[str, Any]], path: str) -> None:
    with open(path, 'w') as f:
        for note in notes:
            f.write(json.dumps(note) + "\n")


def export_csv(notes: List[Dict[str, Any]], path: str) -> None:
    if not notes:
        return
    keys = list(notes[0].keys())
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(notes)
