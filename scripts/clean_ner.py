import json
import os
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).resolve().parents[1] / "data" / "ml_training" / "granular_ner"
input_file = BASE_DIR / "ner_dataset_all.jsonl"
output_clean = BASE_DIR / "clean_training_data.jsonl"
output_empty = BASE_DIR / "empty_notes_to_fix.jsonl"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Counters
total_notes = 0
valid_notes = 0
empty_notes = 0

print(f"Scanning {input_file}...")

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_clean, "w", encoding="utf-8") as f_clean, \
     open(output_empty, "w", encoding="utf-8") as f_empty:

    for line in f_in:
        line = line.strip()
        if not line:
            continue

        total_notes += 1
        try:
            data = json.loads(line)
            note_id = data.get('id', 'unknown_id')
            entities = data.get('entities', [])

            # CHECK: Is the entity list empty?
            if len(entities) == 0:
                # Write to the "To Fix" file
                json.dump(data, f_empty)
                f_empty.write('\n')
                empty_notes += 1
                # Optional: Print the IDs of empty notes to console for quick verification
                # print(f"  [!] Flagged empty note: {note_id}")
            else:
                # Write to the "Ready for Training" file
                json.dump(data, f_clean)
                f_clean.write('\n')
                valid_notes += 1

        except json.JSONDecodeError:
            print(f"  [Error] Could not decode JSON on line {total_notes}")

# Summary Report
print("-" * 30)
print(f"Processing Complete.")
print(f"Total Notes Scanned: {total_notes}")
print(f"Valid Notes (Saved to {output_clean}): {valid_notes}")
print(f"Empty Notes (Saved to {output_empty}): {empty_notes}")
print("-" * 30)

if empty_notes > 0:
    print(f"ACTION REQUIRED: Please open '{output_empty}' and annotate the {empty_notes} missing notes.")
    print("Based on your uploaded file, expect to see IDs like: note_021, note_029, note_041, note_042, etc.")