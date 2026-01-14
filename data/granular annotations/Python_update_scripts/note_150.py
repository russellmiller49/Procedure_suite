import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_150"
TIMESTAMP = datetime.datetime.now().isoformat()

# Define the raw text exactly as it appears in the note
# (reconstructed from the source file content provided)
RAW_TEXT = """Procedure Name: Bronchoscopy

Indication: Pneumonia with hypoxia

Anesthesia: Patient previously intubated and sedated

Consent: Obtained by telephone from family

Time-Out: Performed

Pre-Procedure Diagnosis: Pneumonia

Post-Procedure Diagnosis: Hypoxia

Medications: Patient previously sedated

Procedure Description

An Olympus Q190 video bronchoscope was introduced through the previously placed endotracheal tube and advanced into the tracheobronchial tree.
The tip of the endotracheal tube was confirmed to be in appropriate position, approximately 2 cm above the carina.
Thick, clear, non-purulent secretions were present predominantly within the right-sided airways and were suctioned to clearance.
A complete airway inspection was performed and was notable only for a small white raised endobronchial nodule in the distal bronchus intermedius.
Targeted biopsy of the endobronchial nodule was performed using cupped forceps.
Minimal oozing was observed following biopsy, which resolved spontaneously after a brief period.
The bronchoscope was then advanced into the right middle lobe medial segment, where bronchoalveolar lavage was performed with instillation of 120 mL of saline and return of approximately 80 mL using hand suction.
The bronchoscope was subsequently withdrawn, and the procedure was completed without complication.

Estimated Blood Loss

None

Complications

None

Specimens Sent

Bronchoalveolar lavage from the right middle lobe for standard infectious evaluation

Biopsy specimen from the bronchus intermedius nodule for culture only

Implants

None

Post-Procedure Plan

Continue ICU-level care"""

# Define target entities to extract (Label, String literal to find)
# Order matters for simple find() matching; unique phrases preferred.
TARGET_ENTITIES = [
    ("DEV_INSTRUMENT", "Olympus Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "carina"),
    ("OBS_FINDING", "secretions"),
    ("ANAT_AIRWAY", "right-sided airways"),
    ("OBS_LESION", "endobronchial nodule"),
    ("ANAT_AIRWAY", "distal bronchus intermedius"),
    ("PROC_ACTION", "biopsy"),
    ("DEV_INSTRUMENT", "cupped forceps"),
    ("OBS_FINDING", "oozing"),
    ("ANAT_LUNG_LOC", "right middle lobe medial segment"),
    ("PROC_ACTION", "bronchoalveolar lavage"),
    ("MEAS_VOL", "120 mL"),
    ("MEAS_VOL", "80 mL"),
    # Occurrences in Specimens Sent section
    ("PROC_ACTION", "Bronchoalveolar lavage"),
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("SPECIMEN", "Biopsy specimen"),
    ("ANAT_AIRWAY", "bronchus intermedius"),
    ("OBS_LESION", "nodule"),
]

# ==========================================
# PATH SETUP
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG = OUTPUT_DIR / "alignment_warnings.log"
DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"

# ==========================================
# PROCESSING
# ==========================================

def get_entities(text, targets):
    """
    Finds start/end offsets for target strings.
    Handles multiple occurrences by searching from the last found index.
    """
    entities = []
    search_start = 0
    
    # We sort targets by their appearance in text to handle order correctly
    # However, since the list is manual, we process sequentially and track index.
    # To handle duplicates (e.g. 'endobronchial nodule'), we scan linearly.
    
    current_idx = 0
    sorted_targets = []
    
    # Simple strategy: find the first occurrence of each target *after* the previous match
    # This requires the TARGET_ENTITIES list to be roughly in order of appearance 
    # OR we scan the whole text for unique matches. 
    # Given the input list is ordered by appearance in the note:
    
    last_end = 0
    
    for label, substr in targets:
        start = text.find(substr, last_end)
        if start == -1:
            # If not found after last_end, try from beginning (in case list order was wrong)
            # but usually we want to respect flow. Let's try whole text but ensure no overlap?
            # For this script, we assume strict linear order in TARGET_ENTITIES for safety.
            start = text.find(substr)
            if start == -1:
                print(f"WARNING: substring '{substr}' not found.")
                continue
        
        end = start + len(substr)
        entities.append({
            "label": label,
            "start": start,
            "end": end,
            "text": substr
        })
        # Update search head. Note: If we have nested or close entities, 
        # we might need to be careful. Here we set last_end to start to allow overlap
        # if needed, or end to enforce disjoint. 
        # "biopsy" comes before "biopsy specimen" - disjoint is safer.
        last_end = start + 1 
        
    return entities

def update_jsonl(filepath, new_entry):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_entry) + "\n")

def update_stats(filepath, note_id, entities):
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)

    for ent in entities:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def main():
    print(f"Processing Note ID: {NOTE_ID}...")
    
    # 1. Extract Entities
    entities = get_entities(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Format for ner_dataset_all.jsonl
    # Schema: {"id": str, "text": str, "entities": [[start, end, label], ...]}
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    update_jsonl(DATASET_FILE, ner_entry)
    
    # 3. Format for notes.jsonl
    # Schema: {"id": str, "text": str}
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    update_jsonl(NOTES_FILE, note_entry)
    
    # 4. Format for spans.jsonl
    # Schema: {"span_id": str, "note_id": str, "label": str, "text": str, "start": int, "end": int}
    for e in entities:
        span_entry = {
            "span_id": f"{e['label']}_{e['start']}",
            "note_id": NOTE_ID,
            "label": e['label'],
            "text": e['text'],
            "start": e['start'],
            "end": e['end']
        }
        update_jsonl(SPANS_FILE, span_entry)
    
    # 5. Update Statistics
    update_stats(STATS_FILE, NOTE_ID, entities)
    
    # 6. Validation
    with open(ALIGNMENT_LOG, 'a', encoding='utf-8') as log:
        for e in entities:
            extracted = RAW_TEXT[e['start']:e['end']]
            if extracted != e['text']:
                msg = f"{datetime.datetime.now()} - MISMATCH: Expected '{e['text']}', found '{extracted}' at {e['start']}-{e['end']} in {NOTE_ID}\n"
                log.write(msg)
                print(msg)

    print("Success. Pipeline files updated.")

if __name__ == "__main__":
    main()