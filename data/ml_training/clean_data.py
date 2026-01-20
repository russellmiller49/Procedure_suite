import json
import argparse
from collections import Counter
from pathlib import Path

# --- CONFIGURATION ---
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_FILE = REPO_ROOT / "data" / "ml_training" / "granular_ner" / "ner_dataset_all.neg_stent.jsonl"
DEFAULT_OUTPUT_FILE = REPO_ROOT / "data" / "ml_training" / "granular_ner" / "ner_dataset_all.cleaned.jsonl"

# 1. Define Merge Rules (Old Label -> New Label)
MERGE_MAP = {
    "LMB": "ANAT_AIRWAY",
    "MEAS_VOLUME": "MEAS_VOL",
    "DEV_DEVICE": "DEV_INSTRUMENT",
}

# 2. Define Labels to Drop completely
# Updated list including the new stragglers
DROP_LABELS = {
    "PROC_MEDICATION",
    "CTX_INDICATION",
    "MEAS_OTHER",
    # New additions found in latest run:
    "OBS_NO_COMPLICATION",
    "DISPOSITION",
    "PROC_NAME",
    "ANAT_INTERCOSTAL_SPACE",
    "OBS_FLUID_COLOR"
}

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Clean granular NER dataset (merge/drop labels).")
    ap.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_FILE,
        help=f"Input JSONL (default: {DEFAULT_INPUT_FILE})",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output JSONL (default: {DEFAULT_OUTPUT_FILE})",
    )
    return ap.parse_args()


def clean_dataset(input_file: Path, output_file: Path) -> None:
    stats_merged = Counter()
    stats_dropped = Counter()
    total_spans = 0
    records_with_entities = 0
    records_without_entities = 0
    
    print(f"Processing {input_file}...")
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON on line {line_num}")
                continue
            
            # Support both shapes:
            # - ner_dataset_all.jsonl: {"id","text","entities":[...]}
            # - legacy files: {"spans":[...]}
            key = "entities" if "entities" in record else ("spans" if "spans" in record else None)
            if key is None:
                records_without_entities += 1
                outfile.write(json.dumps(record) + "\n")
                continue

            original_spans = record.get(key) or []
            if not isinstance(original_spans, list):
                records_without_entities += 1
                outfile.write(json.dumps(record) + "\n")
                continue

            records_with_entities += 1
            cleaned_spans: list[dict] = []
            
            for span in original_spans:
                if not isinstance(span, dict):
                    continue
                label = span.get("label")
                
                # Check for DROP
                if label in DROP_LABELS:
                    stats_dropped[label] += 1
                    continue # Skip adding this span
                
                # Check for MERGE
                if label in MERGE_MAP:
                    new_label = MERGE_MAP[label]
                    span["label"] = new_label # Update the label in place
                    stats_merged[f"{label} -> {new_label}"] += 1
                
                # Add to new list
                cleaned_spans.append(span)
            
            # Update the record with the cleaned list
            record[key] = cleaned_spans
            total_spans += len(cleaned_spans)
            
            # Write the cleaned record to the new file
            outfile.write(json.dumps(record) + "\n")

    # --- SUMMARY REPORT ---
    print("\n" + "="*40)
    print("CLEANING COMPLETE")
    print("="*40)
    print(f"Output saved to: {output_file}")
    print("-" * 40)
    print(f"Records with entities/spans cleaned: {records_with_entities}")
    print(f"Records without entities/spans:      {records_without_entities}")
    
    print("\nMERGED LABELS:")
    if stats_merged:
        for transformation, count in stats_merged.items():
            print(f"  {transformation}: {count} spans")
    else:
        print("  None")
        
    print("\nDROPPED LABELS:")
    if stats_dropped:
        for label, count in stats_dropped.items():
            print(f"  {label}: {count} spans removed")
    else:
        print("  None")
        
    print("-" * 40)
    print(f"Total valid spans remaining: {total_spans}")

if __name__ == "__main__":
    args = parse_args()
    clean_dataset(args.input, args.output)