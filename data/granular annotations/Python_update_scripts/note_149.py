import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_149"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# We assume this script runs from the script location.
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Definitions
# ==========================================
# Cleaned text derived from note_149.txt (Source 1-11)
RAW_TEXT = """Procedure: Fiberoptic bronchoscopy
Anesthesia Type: Previously intubated and sedated
Indication: Hypoxia and hemoptysis
Consent: Emergent
Time-Out: Performed
Pre-Procedure Diagnosis: Hemoptysis
Post-Procedure Diagnosis: Hemoptysis versus oral blood aspiration
Medications: Patient previously sedated; topical anesthesia with 10 mL of 2% lidocaine

Procedure Description

The Olympus Q190 video bronchoscope was introduced through the previously placed endotracheal tube and advanced into the tracheobronchial tree. Blood was noted within the endotracheal tube and throughout the airway, beginning near the laryngeal inlet. The tip of the endotracheal tube was visualized approximately 3 cm proximal to the main carina. Diffuse blood was present throughout the airways, with multiple early clots partially obstructing the bronchi. These were suctioned via the bronchoscope. All left- and right-sided airways were inspected to at least the first subsegmental level and were patent following suctioning, with the exception of a small foreign body identified in the posterior segment of the right lower lobe. This material was suctioned from the airway and appeared consistent with tissue of unclear origin. No active bleeding was visualized within the distal airways following clot removal; however, continued blood dripping was observed originating proximal to the tip of the endotracheal tube. No obvious airway injury was identified. Once adequate clearance was achieved and no distal bleeding source was identified, the bronchoscope was withdrawn, and the procedure was completed. Estimated Blood Loss: No procedurally related blood loss
Complications: None
Specimens Sent: None
Implants: None

Recommendations

Plan for repeat bronchoscopy in the morning for additional clearance of blood and clots

Notify the pulmonary service immediately for increasing airway pressures or worsening hypoxia, as these findings may necessitate urgent repeat bronchoscopy

Follow-Up: Continue ICU-level care"""

# Entities mapped to Label_guide_UPDATED.csv
# We list specific substrings to find. The script will locate them.
# Note: For repeated terms (e.g. "endotracheal tube"), we can specify indices or find all.
# Here we list unique targets for robust searching.
TARGETS = [
    {"text": "10 mL", "label": "MEAS_VOL"},
    {"text": "lidocaine", "label": "MEDICATION"},
    {"text": "Olympus Q190 video bronchoscope", "label": "DEV_INSTRUMENT"},
    {"text": "endotracheal tube", "label": "DEV_INSTRUMENT"}, # Will capture first instance or all? Logic below handles all.
    {"text": "tracheobronchial tree", "label": "ANAT_AIRWAY"},
    {"text": "laryngeal inlet", "label": "ANAT_AIRWAY"},
    {"text": "3 cm", "label": "MEAS_SIZE"},
    {"text": "main carina", "label": "ANAT_AIRWAY"},
    {"text": "bronchi", "label": "ANAT_AIRWAY"},
    {"text": "suctioned", "label": "PROC_ACTION"}, # Multiple instances
    {"text": "bronchoscope", "label": "DEV_INSTRUMENT"}, # Multiple instances (generic)
    {"text": "foreign body", "label": "OBS_LESION"},
    {"text": "posterior segment of the right lower lobe", "label": "ANAT_LUNG_LOC"},
    {"text": "tissue", "label": "OBS_LESION"},
    {"text": "blood", "label": "OBS_FINDING"}, # Lowercase 'blood' matches generic findings
    {"text": "clots", "label": "OBS_FINDING"},
    {"text": "active bleeding", "label": "OBS_FINDING"}
]

# ==========================================
# 3. Processing Logic
# ==========================================

def find_entities(text, targets):
    """
    Locates all occurrences of target strings in the text.
    Returns a list of dicts with 'start', 'end', 'label'.
    """
    found_spans = []
    
    # Simple strategy: Find all occurrences of each target
    for target in targets:
        search_term = target["text"]
        label = target["label"]
        start_index = 0
        
        while True:
            idx = text.find(search_term, start_index)
            if idx == -1:
                break
                
            # Basic deduplication: Check if this span is already covered by a longer span?
            # For this script, we assume non-overlapping targets or handle overlaps simply.
            # We add it to the list.
            
            span = {
                "start": idx,
                "end": idx + len(search_term),
                "label": label,
                "text": search_term
            }
            
            # Avoid adding duplicate spans for the same location (if TARGETS has duplicates)
            if span not in found_spans:
                found_spans.append(span)
                
            start_index = idx + 1
            
    # Sort by start position
    found_spans.sort(key=lambda x: x["start"])
    return found_spans

def update_files():
    # 1. Extract Spans
    entities = find_entities(RAW_TEXT, TARGETS)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # 4. Update spans.jsonl
    new_spans_lines = []
    for ent in entities:
        span_entry = {
            "span_id": f"{ent['label']}_{ent['start']}",
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        new_spans_lines.append(json.dumps(span_entry))
        
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for line in new_spans_lines:
            f.write(line + "\n")
            
    # 5. Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Fallback if file doesn't exist (though it should)
        stats = {
            "total_files": 0, "total_notes": 0, 
            "total_spans_raw": 0, "total_spans_valid": 0, 
            "label_counts": {}
        }

    # Increment totals
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities) # Assuming all valid for this script

    # Update label counts
    for ent in entities:
        lbl = ent["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1
            
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        for ent in entities:
            # Slicing the text to verify
            extracted = RAW_TEXT[ent['start']:ent['end']]
            if extracted != ent['text']:
                log_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{ent['text']}', found '{extracted}' at {ent['start']}:{ent['end']}\n"
                log_file.write(log_msg)

if __name__ == "__main__":
    try:
        update_files()
        print(f"Successfully processed {NOTE_ID} and updated datasets.")
    except Exception as e:
        print(f"Error processing {NOTE_ID}: {e}")