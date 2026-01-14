from pathlib import Path
import json
import os
import datetime
import re

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
NOTE_ID = "note_242"

# Raw text extracted from the provided source content. 
# Note: Special characters like '×' are preserved.
RAW_TEXT = """NOTE_ID:  note_242 SOURCE_FILE: note_242.txt ANESTHESIA:  General
INDICATIONS FOR PROCEDURE: Right lower lobe mass
DESCRIPTION OF PROCEDURE: Explanation of the procedure and all risks, benefits, and options were discussed.
The risks include but were not limited to bleeding, infection, and pneumothorax. All questions were answered.
The patient was anesthetized with topical anesthesia and the bronchoscope was introduced through the mouth where topical lidocaine was instilled on the vocal cords and into the trachea.
When adequate anesthesia was achieved, the bronchoscope was passed through the vocal cords and topical lidocaine administered on a local-regional fashion.
The endobronchial tree was inspected and patient was found to have endobronchial lesion noted in the right lower lobe superior segment.
Multiple forceps biopsies were obtained at this time.  Lidocaine with epinephrine was instilled in addition to cold saline to achieve adequate hemostasis.
ROSE at bedside confirmed adequate sample and possible evidence of malignancy.  The bronchoscope was then slowly withdrawn and removed.
The endobronchial ultrasound bronchoscope was inserted through the vocal cords.  Staging ultrasound performed.
Measured on ultrasound the 11 L, 10 L, for now, 7, 4R, 10 R, 11RS and 11Ri.
Station 7 was greater than 5 mm and therefore was sampled by needle aspiration ×4.
ROSE at bedside confirmed adequate sample.  Bronchoscope was slowly withdrawn and removed.
Diagnostic bronchoscope passed through the vocal cords.
Tracheobronchial tree was examined adequate hemostasis was achieved.  Right lower lobe superior segment endobronchial lesion no longer bleeding.
Bronchoscope was slowly withdrawn and removed.
Complication: None
Impression:
1.  Right lower lobe superior segment endobronchial lesion
2.  Biopsies of 7 lymph node station
Recommendations: 
1.  Follow up final pathology of endobronchial lesion
2.  Will notify patient in regards to follow-up with primary pulmonologist"""

# Entities identified based on Label_guide_UPDATED.csv
# Format: (Text_Snippet, Label, Occurrence_Index)
# Occurrence_Index: 0 for first match, 1 for second, etc.
ENTITIES_TO_EXTRACT = [
    ("Right lower lobe", "ANAT_LUNG_LOC", 0),
    ("mass", "OBS_LESION", 0),
    ("lidocaine", "MEDICATION", 0),
    ("trachea", "ANAT_AIRWAY", 0),
    ("lidocaine", "MEDICATION", 1),
    ("endobronchial lesion", "OBS_LESION", 0),
    ("right lower lobe superior segment", "ANAT_LUNG_LOC", 0),
    ("forceps", "DEV_INSTRUMENT", 0),
    ("biopsies", "PROC_ACTION", 0),
    ("Lidocaine", "MEDICATION", 0),
    ("epinephrine", "MEDICATION", 0),
    ("malignancy", "OBS_ROSE", 0),
    ("endobronchial ultrasound", "PROC_METHOD", 0),
    ("11 L", "ANAT_LN_STATION", 0),
    ("10 L", "ANAT_LN_STATION", 0),
    ("7", "ANAT_LN_STATION", 0),
    ("4R", "ANAT_LN_STATION", 0),
    ("10 R", "ANAT_LN_STATION", 0),
    ("11RS", "ANAT_LN_STATION", 0),
    ("11Ri", "ANAT_LN_STATION", 0),
    ("Station 7", "ANAT_LN_STATION", 0),
    ("5 mm", "MEAS_SIZE", 0),
    ("needle aspiration", "PROC_ACTION", 0),
    ("×4", "MEAS_COUNT", 0),
    ("Right lower lobe superior segment", "ANAT_LUNG_LOC", 0),
    ("endobronchial lesion", "OBS_LESION", 1),
    ("no longer bleeding", "OUTCOME_COMPLICATION", 0),
    ("Right lower lobe superior segment", "ANAT_LUNG_LOC", 1),
    ("endobronchial lesion", "OBS_LESION", 2),
    ("Biopsies", "PROC_ACTION", 0),
    ("7", "ANAT_LN_STATION", 1),
    ("endobronchial lesion", "OBS_LESION", 3),
]

# ----------------------------------------------------------------------------------
# PATH SETUP
# ----------------------------------------------------------------------------------
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------------
def find_entity_indices(text, snippet, occurrence=0):
    """Finds the start/end indices of the nth occurrence of a snippet."""
    matches = [m for m in re.finditer(re.escape(snippet), text)]
    if len(matches) > occurrence:
        m = matches[occurrence]
        return m.start(), m.end()
    return None, None

def update_stats(labels_found):
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
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(labels_found)
    stats["total_spans_valid"] += len(labels_found)

    for label in labels_found:
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def log_warning(message):
    """Logs warnings to the log file."""
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# ----------------------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------------------
def process_note():
    entities_data = []
    labels_found = []

    # 1. Extract Entities
    for snippet, label, occ in ENTITIES_TO_EXTRACT:
        start, end = find_entity_indices(RAW_TEXT, snippet, occ)
        
        if start is not None:
            # Validation
            extracted_text = RAW_TEXT[start:end]
            if extracted_text != snippet:
                log_warning(f"Mismatch for {NOTE_ID}: Expected '{snippet}', found '{extracted_text}' at {start}:{end}")
            
            entities_data.append({
                "start": start,
                "end": end,
                "label": label,
                "text": snippet
            })
            labels_found.append(label)
        else:
            log_warning(f"Entity not found in {NOTE_ID}: '{snippet}' (occurrence {occ})")

    # 2. Update ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities_data
    }
    with open(NER_DATASET_FILE, "a") as f:
        f.write(json.dumps(ner_record) + "\n")

    # 3. Update notes.jsonl
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(NOTES_FILE, "a") as f:
        f.write(json.dumps(note_record) + "\n")

    # 4. Update spans.jsonl
    with open(SPANS_FILE, "a") as f:
        for ent in entities_data:
            span_record = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_record) + "\n")

    # 5. Update stats.json
    update_stats(labels_found)

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities_data)} entities.")

if __name__ == "__main__":
    process_note()