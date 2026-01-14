import json
import os
import datetime
import re
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================
NOTE_ID = "note_177"
SOURCE_FILE = "note_177.txt"

# Define the raw text content exactly as provided
RAW_TEXT = """Indications: diagnosis and staging of suspected lung cancer
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 11L, 4L, 4R, 7, 11Rs and 11Ri lymph nodes.
Sampling by transbronchial needle aspiration was performed with the Olympus EBUSTBNA 22 gauge needle beginning with the 11L Lymph node4L74R11Rs11Ri.
ROSE did not identify malignancy in any of the obtained samples. All samples were sent for routine cytology.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5 cc.

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# Define target entities to extract based on Label_guide_UPDATED.csv
# List of tuples: (Label, Search Phrase, Instance Index)
# Instance Index 0 = first match, 1 = second match, -1 = all matches (handled differently in logic below)
# We will map these manually to ensure precision.
TARGET_ENTITIES = [
    ("ANAT_AIRWAY", "tracheobronchial tree", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 1),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope", 0),
    ("ANAT_AIRWAY", "mouth", 0),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 0),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 1),
    ("ANAT_AIRWAY", "vocal cords", 0),
    ("ANAT_AIRWAY", "subglottic space", 0),
    ("ANAT_AIRWAY", "trachea", 0), # lowercase search in text
    ("ANAT_AIRWAY", "carina", 0), # lowercase search in text
    ("ANAT_AIRWAY", "tracheobronchial tree", 2),
    ("ANAT_AIRWAY", "Bronchial mucosa", 0),
    ("OBS_LESION", "endobronchial lesions", 0),
    ("OBS_FINDING", "secretions", 0),
    ("DEV_INSTRUMENT", "video bronchoscope", 1), # The one after "The"
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope", 0),
    ("ANAT_AIRWAY", "mouth", 1),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 2),
    ("ANAT_AIRWAY", "tracheobronchial tree", 3),
    ("ANAT_LN_STATION", "hilar", 0),
    ("ANAT_LN_STATION", "mediastinal", 0),
    ("ANAT_LN_STATION", "11L", 0),
    ("ANAT_LN_STATION", "4L", 0),
    ("ANAT_LN_STATION", "4R", 0),
    ("ANAT_LN_STATION", "7", 0),
    ("ANAT_LN_STATION", "11Rs", 0),
    ("ANAT_LN_STATION", "11Ri", 0),
    ("PROC_ACTION", "Sampling", 0),
    ("PROC_ACTION", "transbronchial needle aspiration", 0),
    ("DEV_NEEDLE", "22 gauge needle", 0),
    ("ANAT_LN_STATION", "11L", 1),
    ("ANAT_LN_STATION", "4L", 1),
    ("ANAT_LN_STATION", "7", 1),
    ("ANAT_LN_STATION", "4R", 1),
    ("ANAT_LN_STATION", "11Rs", 1),
    ("ANAT_LN_STATION", "11Ri", 1),
    ("OBS_ROSE", "malignancy", 0),
    ("PROC_METHOD", "EBUS", 1), # In "EBUS bronchoscopy"
    ("PROC_ACTION", "bronchoscopy", 0), # In "EBUS bronchoscopy"
    ("DEV_INSTRUMENT", "Q190 video bronchoscope", 1),
    ("OBS_FINDING", "secretions", 1),
    ("OBS_FINDING", "active bleeding", 0),
    ("OUTCOME_COMPLICATION", "No immediate complications", 0),
    ("PROC_ACTION", "flexible bronchoscopy", 0),
    ("PROC_METHOD", "endobronchial ultrasound", 0),
    ("PROC_ACTION", "biopsies", 0),
    ("MEAS_VOL", "5 cc", 0)
]

# Paths
# Adjusting to script location: data/granular annotations/Python_update_scripts/
# Target: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = OUTPUT_DIR / "stats.json" # Assuming stats.json lives in root or specific dir, adjusting to output dir for this task

# ==========================================
# 2. PROCESSING FUNCTIONS
# ==========================================

def get_spans(text, entities_to_find):
    found_spans = []
    
    # Sort by length descending to avoid sub-match issues (though specific indexing solves this)
    # But here we rely on the order in TARGET_ENTITIES and find occurrences
    
    # We need to track current position for multiple occurrences if we were scanning sequentially,
    # but here we specify instance index.
    
    for label, phrase, index in entities_to_find:
        matches = [m for m in re.finditer(re.escape(phrase), text, re.IGNORECASE)]
        
        if matches and len(matches) > index:
            m = matches[index]
            span = {
                "span_id": f"{label}_{m.start()}",
                "note_id": NOTE_ID,
                "label": label,
                "text": m.group(), # Capture actual text (case sensitive from source)
                "start": m.start(),
                "end": m.end()
            }
            found_spans.append(span)
        else:
            print(f"WARNING: Could not find '{phrase}' index {index} for label {label}")
            
    # Sort spans by start offset
    found_spans.sort(key=lambda x: x['start'])
    return found_spans

def update_stats(new_spans_count, new_labels):
    # Load existing stats or create new structure if missing
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    else:
        # Fallback if file doesn't exist (though it should based on prompt)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    # Update counts
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += new_spans_count
    stats["total_spans_valid"] += new_spans_count
    
    for label in new_labels:
        if label in stats["label_counts"]:
            stats["label_counts"][label] += 1
        else:
            stats["label_counts"][label] = 1
            
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Extract Spans
    spans = get_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Validate Alignment
    alignment_log = []
    valid_spans = []
    labels_found = []
    
    for span in spans:
        extracted = RAW_TEXT[span['start']:span['end']]
        if extracted != span['text']:
            error_msg = f"Mismatch in {NOTE_ID}: Expected '{span['text']}' but got '{extracted}' at {span['start']}:{span['end']}"
            alignment_log.append(error_msg)
            print(error_msg)
        else:
            valid_spans.append(span)
            labels_found.append(span['label'])

    if alignment_log:
        with open(OUTPUT_DIR / "alignment_warnings.log", "a") as log:
            for err in alignment_log:
                log.write(err + "\n")

    # 3. Prepare Data Objects
    
    # ner_dataset_all.jsonl entry
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": s["span_id"],
                "label": s["label"],
                "start_offset": s["start"],
                "end_offset": s["end"]
            }
            for s in valid_spans
        ]
    }

    # notes.jsonl entry
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # 4. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # Append to notes.jsonl
    with open(OUTPUT_DIR / "notes.jsonl", "a") as f:
        f.write(json.dumps(note_entry) + "\n")

    # Append to spans.jsonl
    with open(OUTPUT_DIR / "spans.jsonl", "a") as f:
        for span in valid_spans:
            f.write(json.dumps(span) + "\n")

    # 5. Update Stats
    # Note: Using valid_spans count
    # Update stats.json in the current directory (or defined path)
    # We will look for stats.json provided in the prompt context, 
    # but for this script we assume it resides in the same output dir or we create it.
    # To match the prompt's stats.json content, we assume it's available.
    
    # For this script to be runnable, we need to locate the stats file.
    # If it's not at OUTPUT_DIR, we might need to adjust. 
    # Assuming the user puts the stats.json in the OUTPUT_DIR for this operation.
    if not os.path.exists(STATS_FILE):
        # Create a dummy one if strictly needed for the script to run standalone
        # based on provided content
        with open(STATS_FILE, 'w') as f:
             json.dump({
                "total_files": 191,
                "successful_files": 188,
                "total_notes": 188,
                "total_spans_raw": 3413,
                "total_spans_valid": 3404,
                "alignment_warnings": 0,
                "alignment_errors": 9,
                "label_counts": {} # truncated for brevity
             }, f)
             
    update_stats(len(valid_spans), labels_found)
    
    print(f"Successfully processed {NOTE_ID}.")
    print(f"Extracted {len(valid_spans)} entities.")
    print(f"Data written to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()