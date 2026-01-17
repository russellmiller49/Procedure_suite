import json
import shutil
from collections import Counter
from pathlib import Path

# --- CONFIGURATION ---

# 1. MERGE MAP: { "OLD_LABEL": "NEW_TARGET_LABEL" }
MERGE_MAP = {
    # Fix Schema Inconsistencies (Rare -> Common)
    "PROC_MEDICATION": "MEDICATION",        # 3 -> 954
    "MEAS_VOLUME": "MEAS_VOL",              # 4 -> 1055
    "DEV_DEVICE": "DEV_INSTRUMENT",         # 4 -> 6298
    
    # Semantic Merges (Specific -> General)
    "PROC_NAME": "PROC_ACTION",             # 3 -> 7411
    "LMB": "ANAT_AIRWAY",                   # 39 -> 6524
    "ANAT_INTERCOSTAL_SPACE": "ANAT_PLEURA",# 4 -> 1429
    "OBS_FLUID_COLOR": "OBS_FINDING",       # 4 -> 3045
    "OBS_NO_COMPLICATION": "OBS_FINDING",   # 1 -> 3045
    
    # NEW SUGGESTION based on updated stats (Optional but recommended)
    # "MEAS_AIRWAY_DIAM": "MEAS_SIZE",      # 36 -> 2364 (Borderline count)
    # "MEAS_TEMP": "OBS_FINDING",           # 48 -> 3045 (Borderline count)
}

# 2. PRUNE LIST: [ "LABEL_TO_REMOVE" ]
#    These labels will be converted to 'O' (Outside).
PRUNE_LIST = [
    "CTX_INDICATION",   # Count: 2 (Too low to learn)
    "DISPOSITION",      # Count: 2 (Too low to learn)
    
    # Note: CTX_HISTORICAL (192) and CTX_TIME (165) are now robust enough 
    # to keep! They are commented out below so they WON'T be pruned.
    # "CTX_HISTORICAL", 
    # "CTX_TIME",       
]

# --- SCRIPT LOGIC ---

def process_label(bio_tag):
    """Refines a single BIO tag (e.g., 'B-PROC_NAME') based on rules."""
    if bio_tag == "O":
        return "O"
        
    # Handle potentially malformed tags (just in case)
    if "-" not in bio_tag:
        return "O"

    prefix, label = bio_tag.split("-", 1)
    
    # Check Prune List
    if label in PRUNE_LIST:
        return "O"
        
    # Check Merge Map
    if label in MERGE_MAP:
        new_label = MERGE_MAP[label]
        return f"{prefix}-{new_label}"
        
    return bio_tag

def refine_dataset(input_path, output_path):
    print(f"Reading from: {input_path}")
    print(f"Writing to:   {output_path}")
    
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    counts = Counter()
    modified_counts = Counter()
    
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        
        for line_num, line in enumerate(fin):
            try:
                data = json.loads(line)
                original_tags = data.get("ner_tags", [])
                
                new_tags = []
                for tag in original_tags:
                    new_tag = process_label(tag)
                    new_tags.append(new_tag)
                    
                    # Track stats
                    if tag != "O":
                        # Handle cases where tag might be malformed
                        parts = tag.split("-", 1)
                        base_label = parts[1] if len(parts) > 1 else tag
                        counts[base_label] += 1
                        
                        if new_tag != "O":
                            new_parts = new_tag.split("-", 1)
                            new_base_label = new_parts[1] if len(new_parts) > 1 else new_tag
                            
                            if base_label != new_base_label:
                                modified_counts[f"Merged {base_label} -> {new_base_label}"] += 1
                        else:
                            modified_counts[f"Pruned {base_label}"] += 1

                data["ner_tags"] = new_tags
                fout.write(json.dumps(data) + "\n")
                
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line {line_num}")

    print("\n--- Modification Stats ---")
    if not modified_counts:
        print("No labels were modified.")
    for action, count in modified_counts.most_common():
        print(f"{action}: {count} occurrences")
        
    print(f"\nSuccess! New dataset saved to {output_path}")

if __name__ == "__main__":
    # Point this to your uploaded file
    INPUT_FILE = "ner_bio_format.jsonl" 
    OUTPUT_FILE = "ner_bio_format_refined.jsonl"
    
    if Path(INPUT_FILE).exists():
        refine_dataset(INPUT_FILE, OUTPUT_FILE)
    else:
        # Fallback for folder structures
        INPUT_FILE = "data/ml_training/granular_ner/ner_bio_format.jsonl"
        OUTPUT_FILE = "data/ml_training/granular_ner/ner_bio_format_refined.jsonl"
        
        if Path(INPUT_FILE).exists():
            refine_dataset(INPUT_FILE, OUTPUT_FILE)
        else:
            print(f"Error: Could not find input file at {INPUT_FILE}")