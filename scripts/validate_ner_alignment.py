import json
from pathlib import Path
import sys

def _resolve_target_path(arg: str | None) -> Path:
    """
    If arg is None, default to our NER training data location:
      data/ml_training/granular_ner/ner_dataset_all.jsonl

    If arg is provided:
    - absolute paths are used as-is
    - relative paths are first interpreted relative to repo root
    - if not found, we try relative to the granular_ner folder
    """
    repo_root = Path(__file__).resolve().parents[1]
    granular_ner_dir = repo_root / "data" / "ml_training" / "granular_ner"

    if arg is None:
        return granular_ner_dir / "ner_dataset_all.jsonl"

    p = Path(arg)
    if p.is_absolute():
        return p

    p_repo = repo_root / p
    if p_repo.exists():
        return p_repo

    p_granular = granular_ner_dir / p
    return p_granular


def validate_ner_alignment(file_path: Path) -> None:
    print(f"Validating NER alignment for: {file_path}")
    
    issues_found = 0
    total_spans = 0

    def _normalize_span(span):
        """
        Supports common formats:
        - dict spans: {"start": int, "end": int, "label": str, "text": str}
        - dict spans (alt keys): start_char/end_char/span_text or start_offset/end_offset
        - list spans: [start, end, label] or [start, end, label, text]
        """
        if isinstance(span, dict):
            start = span.get("start")
            end = span.get("end")
            if start is None and "start_char" in span:
                start = span.get("start_char")
            if end is None and "end_char" in span:
                end = span.get("end_char")
            if start is None and "start_offset" in span:
                start = span.get("start_offset")
            if end is None and "end_offset" in span:
                end = span.get("end_offset")

            label = span.get("label")
            expected_text = span.get("text")
            if expected_text is None and "span_text" in span:
                expected_text = span.get("span_text")
            return start, end, label, expected_text

        if isinstance(span, (list, tuple)):
            if len(span) == 3:
                start, end, label = span
                return start, end, label, None
            if len(span) >= 4:
                start, end, label, expected_text = span[0], span[1], span[2], span[3]
                return start, end, label, expected_text

        return None, None, None, None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Line {line_num}: Invalid JSON")
                    continue

                text = data.get('text', '')
                # Adjust key 'entities' or 'spans' based on your specific JSONL format
                spans = data.get('entities', []) or data.get('spans', [])
                record_id = data.get('id') or data.get('note_id') or "unknown_id"
                
                if not spans:
                    continue

                for span in spans:
                    total_spans += 1
                    start, end, label, expected_text = _normalize_span(span)

                    # 1. Check if indices exist
                    if start is None or end is None:
                        print(f"Line {line_num} ({record_id}): Span missing start/end indices")
                        issues_found += 1
                        continue

                    # 2. Check bounds
                    if end > len(text):
                        print(f"Line {line_num} ({record_id}): Span out of bounds! End {end} > Text Length {len(text)}")
                        issues_found += 1
                        continue

                    # 3. Check text alignment
                    actual_text = text[start:end]
                    
                    # Normalization for loose checking (optional)
                    # We usually want exact match, but sometimes whitespace differs
                    if expected_text is None:
                        continue
                    if actual_text != expected_text:
                        # Allow for minor whitespace differences if strictly necessary
                        if (expected_text is not None) and (actual_text.strip() == expected_text.strip()):
                            continue
                            
                        print(f"Line {line_num} ({record_id}): Mismatch for '{label}'")
                        print(f"   Expected: '{expected_text}'")
                        print(f"   Actual:   '{actual_text}'")
                        print(f"   Indices:  {start}:{end}")
                        issues_found += 1

    except FileNotFoundError:
        print(f"File not found: {file_path} (try data/ml_training/granular_ner/ner_dataset_all.jsonl)")
        return

    print("-" * 30)
    if issues_found == 0:
        print(f"Success! Verified {total_spans} spans. No alignment errors found.")
    else:
        print(f"Validation Failed. Found {issues_found} alignment errors.")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    target_file = _resolve_target_path(arg)
    validate_ner_alignment(target_file)