import json
import os
import re
from pathlib import Path
from datetime import datetime

# ----------------------------------------------------------------------------------
# 1. Configuration & Path Setup
# ----------------------------------------------------------------------------------
NOTE_ID = "note_168"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# Using pathlib to resolve 2 levels up from current script location if run locally,
# but for this standalone generation, we assume the structure relative to repo root.
# In a real run, this would be: Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner"
# We will use the standard structure requested.

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = OUTPUT_DIR / "stats.json"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# 2. Raw Text & Entity Definition
# ----------------------------------------------------------------------------------

# Clean text derived from the provided note content (source tags removed)
RAW_TEXT = """Indications: Mediastinal Adenopathy with concern for brain mets
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. There was partial dynamic obstruction of the trachea of unclear etiology.
The carina was sharp. The tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa and anatomy were normal; there are no endobronchial lesions, and no secretions.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Enlarged mediastinal and hilar lymph nodes were seen in multiple stations in relatively symmetric pattern.
Mediastinal lymph node sampling was performed by transbronchial needle aspiration with the Olympus EBUSTBNA 22 gauge needle beginning with the 11L Lymph node, followed by the 7 lymph node followed by the 4L lymph node and finally the 2R lymph node.
A total of 5 biopsies were performed in each station (station 2R 7 samples were collected).
ROSE evaluation yielded multiple granulomas from the 11L, 4L and 2R stations and adequate lymphocytes from station 7. All samples were sent for routine cytology and two additional samples were taken for AFB and fungal culture from the station 2R.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood there and secretions there was some slow oozing seen in the bilateral lower lobes.
2ml of 1% lidocaine with epinephrine were instilled into each lower lobe and the bleeding stopped.
Once we were confident that there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 10ml

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# Define entities: (Label, Text_Segment, Occurrence_Index)
# Occurrence_Index 0 = first time appearing, 1 = second, etc.
# This approach helps handle identical words in different contexts.
TARGET_ENTITIES = [
    ("OBS_LESION", "Mediastinal Adenopathy", 0),
    ("OBS_LESION", "brain mets", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("ANAT_AIRWAY", "carina", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 0), # First occurrence
    ("ANAT_AIRWAY", "tracheobronchial tree", 1), # Second occurrence
    ("ANAT_AIRWAY", "tracheobronchial tree", 2), # Third occurrence
    ("OBS_FINDING", "partial dynamic obstruction", 0),
    ("OBS_FINDING", "secretions", 0), # "no secretions"
    ("OBS_FINDING", "secretions", 1), # "secretions there was"
    ("ANAT_LN_STATION", "hilar", 0),
    ("PROC_ACTION", "transbronchial needle aspiration", 0),
    ("DEV_NEEDLE", "22 gauge", 0),
    ("ANAT_LN_STATION", "11L", 0),
    ("ANAT_LN_STATION", "7", 0), # "followed by the 7 lymph node"
    ("ANAT_LN_STATION", "4L", 0),
    ("ANAT_LN_STATION", "2R", 0),
    ("MEAS_COUNT", "5", 0), # "5 biopsies"
    ("ANAT_LN_STATION", "2R", 1), # "station 2R 7 samples"
    ("MEAS_COUNT", "7", 1), # "7 samples" - skip first 7 (station)
    ("OBS_ROSE", "granulomas", 0),
    ("ANAT_LN_STATION", "11L", 1),
    ("ANAT_LN_STATION", "4L", 1),
    ("ANAT_LN_STATION", "2R", 2),
    ("OBS_ROSE", "lymphocytes", 0),
    ("ANAT_LN_STATION", "7", 1), # "from station 7"
    ("ANAT_LN_STATION", "2R", 3), # "from the station 2R"
    ("OBS_FINDING", "oozing", 0),
    ("MEAS_VOL", "2ml", 0),
    ("MEDICATION", "lidocaine", 0),
    ("MEDICATION", "epinephrine", 0),
    ("OUTCOME_COMPLICATION", "bleeding stopped", 0),
    ("OUTCOME_COMPLICATION", "No immediate complications", 0)
]

# ----------------------------------------------------------------------------------
# 3. Processing Logic
# ----------------------------------------------------------------------------------

def find_entity_spans(text, entities):
    """
    Finds strict start/end indices for entities based on text and occurrence count.
    """
    spans = []
    # Keep track of search cursor for each unique text string to handle multiple occurrences
    cursor_map = {} 
    
    # Sort entities by their occurrence index to ensure we process them in order for the same string
    # However, since the input list is mixed, we scan linearly and use find() with start index.
    
    # Pre-process: Group by string to manage offsets
    # Actually, a simpler way is to find all occurrences of a string, store them, and pick by index.
    
    # Map: "string" -> [list of (start, end) tuples]
    occurrence_cache = {}
    
    unique_strings = set(e[1] for e in entities)
    
    for s in unique_strings:
        matches = []
        start_search = 0
        while True:
            idx = text.find(s, start_search)
            if idx == -1:
                break
            matches.append((idx, idx + len(s)))
            start_search = idx + 1
        occurrence_cache[s] = matches

    for label, substr, occ_idx in entities:
        if substr not in occurrence_cache or occ_idx >= len(occurrence_cache[substr]):
            print(f"Warning: Could not find occurrence {occ_idx} of '{substr}' in text.")
            continue
        
        start, end = occurrence_cache[substr][occ_idx]
        spans.append({
            "start": start,
            "end": end,
            "label": label,
            "text": substr
        })
    
    # Sort spans by start position
    spans.sort(key=lambda x: x["start"])
    return spans

def update_stats(new_spans):
    """Updates the stats.json file."""
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
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
    # stats["total_files"] might track unique filenames; assuming 1 note = 1 file update for this script
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans) # Assuming all strict matches are valid
    
    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Calculate Spans
    extracted_spans = find_entity_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Prepare JSON Objects
    
    # ner_dataset_all entry
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }
    
    # notes.jsonl entry
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # spans.jsonl entries
    span_entries = []
    for s in extracted_spans:
        span_id = f"{s['label']}_{s['start']}"
        span_entries.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": s["label"],
            "text": s["text"],
            "start": s["start"],
            "end": s["end"]
        })
    
    # 3. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_FILE, "a") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Append to notes.jsonl
    with open(NOTES_FILE, "a") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Append to spans.jsonl
    with open(SPANS_FILE, "a") as f:
        for entry in span_entries:
            f.write(json.dumps(entry) + "\n")
            
    # 4. Update Stats
    update_stats(extracted_spans)
    
    # 5. Validation & Logging
    with open(LOG_FILE, "a") as log:
        for s in extracted_spans:
            extracted_text = RAW_TEXT[s["start"]:s["end"]]
            if extracted_text != s["text"]:
                log.write(f"[{datetime.now()}] MISMATCH {NOTE_ID}: Exp '{s['text']}' Got '{extracted_text}'\n")

    print(f"Successfully processed {NOTE_ID} with {len(extracted_spans)} entities.")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()