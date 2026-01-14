import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION & PATH SETUP
# ==========================================
NOTE_ID = "note_152"

# Raw text content exactly as provided in the source file
RAW_TEXT = """Procedure: Fiberoptic bronchoscopy
Indication: Pneumonia
Anesthesia: Patient previously intubated and sedated
Consent: Obtained from daughter
Time-Out: Performed

Pre-Procedure Diagnosis: Pneumonia
Post-Procedure Diagnosis: Pneumonia

Medications: Patient previously sedated per ICU record

Procedure Description

The Olympus Q190 video bronchoscope was introduced through the previously placed endotracheal tube and advanced into the tracheobronchial tree.
The tip of the endotracheal tube was noted to be at the level of the cricoid cartilage and was advanced 5 cm to an appropriate position approximately 2 cm above the carina.
The bronchoscope was then advanced with suction off into the anterior segment of the right lower lobe and wedged into position.
Purulent secretions were visualized within this segment. Bronchoalveolar lavage was performed with instillation of 120 mL of sterile saline and return of 40 mL using hand suction technique, yielding purulent material.
Following completion of lavage, a complete airway inspection was performed.
The remainder of the tracheobronchial tree was normal in appearance, without additional secretions or evidence of endobronchial disease.
Specimens

Bronchoalveolar lavage from the right lower lobe sent for microbiologic analysis

Estimated Blood Loss

None.

Complications

None.

Implants

None.

Post-Procedure Plan

Continue ICU-level care."""

# Defined Entities based on Label_guide_UPDATED.csv
# Format: (Label, Text Span)
# Note: Indication "Pneumonia" is a Diagnosis, not strictly OBS_LESION (mass/nodule) per guide.
# [cite_start]"Purulent secretions" -> OBS_FINDING [cite: 27]
ENTITIES_TO_EXTRACT = [
    ("DEV_INSTRUMENT", "Olympus Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # Instance 1
    ("ANAT_AIRWAY", "cricoid cartilage"),
    ("MEAS_SIZE", "5 cm"),
    ("MEAS_SIZE", "2 cm"),
    ("ANAT_AIRWAY", "carina"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_LUNG_LOC", "anterior segment of the right lower lobe"),
    ("OBS_FINDING", "Purulent secretions"),
    ("PROC_ACTION", "Bronchoalveolar lavage"), # Action context
    ("MEAS_VOL", "120 mL"),
    ("MEAS_VOL", "40 mL"),
    ("OBS_FINDING", "purulent material"),
    ("PROC_ACTION", "lavage"), # Reference to previous action
    ("ANAT_AIRWAY", "tracheobronchial tree"), # Instance 2
    ("SPECIMEN", "Bronchoalveolar lavage"), # Specimen context
    ("ANAT_LUNG_LOC", "right lower lobe")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING LOGIC
# ==========================================

def find_offsets(text, entities):
    """
    Locates start/end indices for entities. 
    Handles multiple occurrences by tracking search position.
    """
    spans = []
    search_start_indices = {} # Track last found index for each distinct text

    sorted_entities = []
    
    # We must scan the text sequentially to handle duplicates correctly
    # Simple strategy: Find first match, store, then mask it or search after it.
    # To keep it robust without masking, we track the 'cursor' for specific phrases.
    
    current_cursor = 0
    # Because the list `ENTITIES_TO_EXTRACT` is ordered by appearance in the text:
    for label, entity_text in entities:
        start = text.find(entity_text, current_cursor)
        
        if start == -1:
            # If not found after current cursor, reset cursor to 0 to check if it appeared earlier 
            # (though the list *should* be ordered, this is a fallback) or log error.
            # However, for this specific note, we assume the list is ordered by occurrence.
            print(f"WARNING: Could not find '{entity_text}' after index {current_cursor}")
            continue

        end = start + len(entity_text)
        spans.append({
            "label": label,
            "text": entity_text,
            "start": start,
            "end": end
        })
        current_cursor = start + 1 # Advance cursor just past the start of this hit to find next overlapping or subsequent
    
    return spans

def update_jsonl(file_path, new_record):
    """Appends a JSON record to a JSONL file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def update_stats(file_path, new_spans):
    """Updates the statistics JSON file."""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }

    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file for this batch
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Calculate Offsets
    extracted_spans = find_offsets(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Data Structures
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }

    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    span_records = []
    for s in extracted_spans:
        span_records.append({
            "span_id": f"{s['label']}_{s['start']}",
            "note_id": NOTE_ID,
            "label": s["label"],
            "text": s["text"],
            "start": s["start"],
            "end": s["end"]
        })

    # 3. Write to Files
    print(f"Updating data in {OUTPUT_DIR}...")
    
    # Update ner_dataset_all.jsonl
    update_jsonl(OUTPUT_DIR / "ner_dataset_all.jsonl", ner_record)
    
    # Update notes.jsonl
    update_jsonl(OUTPUT_DIR / "notes.jsonl", note_record)
    
    # Update spans.jsonl
    for sr in span_records:
        update_jsonl(OUTPUT_DIR / "spans.jsonl", sr)

    # 4. Update Stats
    update_stats(OUTPUT_DIR / "stats.json", extracted_spans)

    # 5. Validate & Log
    with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as log_file:
        for s in extracted_spans:
            sliced_text = RAW_TEXT[s["start"]:s["end"]]
            if sliced_text != s["text"]:
                warning_msg = (f"[{datetime.datetime.now()}] MISMATCH: "
                               f"Label {s['label']} indices {s['start']}:{s['end']} "
                               f"extracts '{sliced_text}', expected '{s['text']}'\n")
                log_file.write(warning_msg)
                print(warning_msg.strip())

    print(f"Successfully processed {NOTE_ID} with {len(extracted_spans)} entities.")

if __name__ == "__main__":
    main()