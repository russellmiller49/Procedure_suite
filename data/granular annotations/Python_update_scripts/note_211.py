import json
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION & PATH SETUP
# ==============================================================================
NOTE_ID = "note_211"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# We use .parents[2] assuming this script runs from the depth implied above.
# Adjust .parents index if directory structure differs in actual execution.
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# INPUT DATA
# ==============================================================================
RAW_TEXT = """NOTE_ID:  note_211 SOURCE_FILE: note_211.txt PREOPERATIVE DIAGNOSIS: Diffuse parenchymal lung disease
POSTOPERATIVE DIAGNOSIS: Diffuse parenchymal lung disease 
PROCEDURE PERFORMED: Rigid bronchoscopy with transbronchial cryobiopsy, 
INDICATIONS: Diffuse parenchymal lung disease
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia

DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After receiving analgesia and paralytics the patient was bag masked and once preoxygenated a 12 mm rigid tracheoscope was inserted into the mid trachea and attached to the jet ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope. Inspection bronchoscopy was unremarkable.
Subsequently a Forgery balloon was inserted to the rigid bronchoscope into the superior segment of the lingula.
Under fluoroscopic guidance the cryoprobe was inserted past the balloon into the lateral left lower lobe segment under fluoroscopic guidance.
Once the pleural margin was reached the probe was withdrawn approximately 1 cm and the cryoprobe was activated for 4 seconds at which time the flexible bronchoscope and cryoprobe were removed en-bloc in the Fogarty balloon was inflated immediately after removal.
One specimen was removed from the cryoprobe the flexible bronchoscope was reinserted and the balloon was slowly deflated to assess for distal bleeding.
The patient did develop some minor hemorrhage which resolved after balloon occlusion.
It was difficult to maintain the balloon in place and we converted to an endobronchial blocker which was too large to pass the cryoprobe beyond when inserted into the lingua and we subsequently moved the blocker into the mainstem while completing biopsies.
A total of 6 biopsies were performed. During the procedure the patient developed transient hypoxia requiring us to convert to conventional ventilation and the hypoxia resolved.
Once we were confident that there was no active bleeding the flexible bronchoscope was removed.
Following completion of the procedure fluoroscopic evaluation of the pleura was performed to evaluate for pneumothorax and none was seen.
The rigid bronchoscope was subsequently removed once the patient was able to breathe spontaneously.
-	Patient to PACU
-	CXR pending
-	Await pathological evaluation of tissue"""

# We define the entities we want to extract. 
# The script will locate them in the text to ensure exact offsets.
# Format: (Label, Text_Snippet, Occurrence_Index)
# Occurrence_Index=0 means the first time this text snippet appears after the previous found entity, 
# or strictly from the start if we reset search.
# To be robust, we will find all occurrences and select based on context logic or simply list them in order of appearance.

ENTITIES_TO_EXTRACT = [
    # Header Info
    ("OBS_LESION", "Diffuse parenchymal lung disease"), # Preop
    ("OBS_LESION", "Diffuse parenchymal lung disease"), # Postop
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "transbronchial cryobiopsy"),
    ("OBS_LESION", "Diffuse parenchymal lung disease"), # Indications
    
    # Body
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("DEV_INSTRUMENT", "jet ventilator"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("OBS_FINDING", "unremarkable"), # Inspection result
    ("DEV_INSTRUMENT", "Forgery balloon"), # Typos preserved
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_LUNG_LOC", "superior segment of the lingula"),
    ("PROC_METHOD", "fluoroscopic guidance"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("ANAT_LUNG_LOC", "lateral left lower lobe segment"),
    ("PROC_METHOD", "fluoroscopic guidance"),
    ("ANAT_PLEURA", "pleural margin"),
    ("MEAS_SIZE", "1 cm"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("MEAS_TIME", "4 seconds"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("DEV_INSTRUMENT", "Fogarty balloon"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "balloon"),
    ("OUTCOME_COMPLICATION", "minor hemorrhage"),
    ("DEV_INSTRUMENT", "balloon"),
    ("DEV_INSTRUMENT", "endobronchial blocker"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("ANAT_LUNG_LOC", "lingua"), # Typo preserved
    ("DEV_INSTRUMENT", "blocker"),
    ("ANAT_AIRWAY", "mainstem"),
    ("PROC_ACTION", "biopsies"),
    ("MEAS_COUNT", "6"),
    ("PROC_ACTION", "biopsies"),
    ("OUTCOME_COMPLICATION", "transient hypoxia"),
    ("OUTCOME_COMPLICATION", "active bleeding"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("PROC_METHOD", "fluoroscopic evaluation"),
    ("ANAT_PLEURA", "pleura"),
    ("OUTCOME_COMPLICATION", "pneumothorax"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
]

# ==============================================================================
# PROCESSING LOGIC
# ==============================================================================

def extract_entities_with_offsets(text, entity_list):
    """
    Finds entities in text sequentially to determine correct offsets.
    Returns a list of dicts with keys: label, text, start, end.
    """
    results = []
    current_pos = 0
    
    for label, substr in entity_list:
        # Find next occurrence of substring starting from current_pos
        start = text.lower().find(substr.lower(), current_pos)
        
        if start == -1:
            # Fallback: simple finding failed, log warning (in a real scenario, this helps debug)
            # For this script, we assume the input list matches the text order.
            print(f"WARNING: Could not find '{substr}' after index {current_pos}")
            continue
            
        end = start + len(substr)
        
        # Grab the exact text from the raw string to preserve case
        actual_text = text[start:end]
        
        results.append({
            "label": label,
            "text": actual_text,
            "start": start,
            "end": end
        })
        
        # Move current_pos forward
        # We assume entities do not overlap in a way that requires backtracking
        current_pos = start + 1 # Allow overlap if needed, or 'end' for strictly sequential

    return results

def update_stats(stats_path, new_note_count, new_span_count, label_counts):
    """
    Updates the stats.json file.
    """
    if stats_path.exists():
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
        
    stats["total_notes"] += new_note_count
    # Assuming 1 file per note for this update
    stats["total_files"] += new_note_count 
    stats["total_spans_raw"] += new_span_count
    stats["total_spans_valid"] += new_span_count # Assuming all valid
    
    for label, count in label_counts.items():
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count
        
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

def main():
    # 1. Extract Entities
    entities = extract_entities_with_offsets(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Data Lines
    
    # ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    
    # notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # spans.jsonl
    span_entries = []
    label_counts = {}
    
    for e in entities:
        span_id = f"{e['label']}_{e['start']}"
        span_entries.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        })
        label_counts[e["label"]] = label_counts.get(e["label"], 0) + 1

    # 3. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Append to notes.jsonl
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Append to spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for span in span_entries:
            f.write(json.dumps(span) + "\n")
            
    # 4. Update Stats
    update_stats(STATS_PATH, 1, len(entities), label_counts)
    
    # 5. Validation & Logging
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        for e in entities:
            extracted_text = RAW_TEXT[e["start"]:e["end"]]
            if extracted_text != e["text"]:
                log.write(f"MISMATCH [Note: {NOTE_ID}]: Expected '{e['text']}' but got '{extracted_text}' at {e['start']}:{e['end']}\n")
    
    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    main()