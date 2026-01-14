import json
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_263"

# Raw text from the input file
RAW_TEXT = """NOTE_ID:  note_263 SOURCE_FILE: note_263.txt PREOPERATIVE DIAGNOSIS: Tracheal stenosis
POSTOPERATIVE DIAGNOSIS: Complex Tracheal stenosis s/p stent placement 
PROCEDURE PERFORMED: Tracheal self-expandable airway stent placement
INDICATIONS: Symptomatic tracheal stenosis
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite.
After administration of sedatives an LMA was inserted and the flexible bronchoscope was passed through the vocal cords and into the trachea.
Approximately 2.5 cm distal to the vocal cords was a long segment of circumferential complex stenosis measuring 3.5 cm with maximal airway obstruction of 90%.
Distal to the stenosis the mid and distal trachea appeared normal.
All right and left sided airways to at least the first sub-segments were examined and normal without endobronchial disease or airway distortion.
External markers were placed on the patient’s chest with fluoroscopic observation at the proximal and distal edges of the stenosis.
At this point we inserted a JAG guidewire into the trachea through the flexible bronchoscope.
The bronchoscope was then removed with the jagwire left in place.
A 16x40 mm Ultraflex uncovered self-expandable metallic stent was then inserted over the guidewire and using the external markers positioned in proper place and then deployed.
The flexible bronchoscope was re-inserted. The stent was well positioned and partially compressed externally.
A 14/16.5/18 mm Elation dilatational balloon was used to dilate the stent after which the airway was approximately 90% of normal caliber.
At this point inspection was performed to evaluate for any bleeding or other complications and none was seen.
The bronchoscope was removed and the procedure was completed. 

Recommendations:
- Transfer to PACU
- Discharge once criteria met.
- Plan for repeat evaluation and possible stent replacement in approximately 2 weeks."""

# Define target entities based on the Label_guide_UPDATED.csv
# Format: (Text_Substring, Label)
# We use a list to preserve order and allow duplicates if distinct in text
TARGET_ENTITIES = [
    ("Tracheal stenosis", "OBS_LESION"),
    ("Tracheal stenosis", "OBS_LESION"),
    ("stent placement", "PROC_ACTION"),
    ("Tracheal", "ANAT_AIRWAY"),
    ("stent placement", "PROC_ACTION"),
    ("tracheal stenosis", "OBS_LESION"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("2.5 cm", "MEAS_SIZE"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("circumferential complex stenosis", "OBS_LESION"),
    ("3.5 cm", "MEAS_SIZE"),
    ("maximal airway obstruction of 90%", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("stenosis", "OBS_LESION"),
    ("mid and distal trachea", "ANAT_AIRWAY"),
    ("right and left sided airways", "ANAT_AIRWAY"),
    ("JAG guidewire", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("jagwire", "DEV_INSTRUMENT"),
    ("16x40 mm", "DEV_STENT_SIZE"),
    ("Ultraflex", "DEV_STENT_MATERIAL"),
    ("uncovered self-expandable metallic stent", "DEV_STENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("14/16.5/18 mm", "MEAS_SIZE"),
    ("Elation dilatational balloon", "DEV_INSTRUMENT"),
    ("dilate", "PROC_ACTION"),
    ("stent", "DEV_STENT"),
    ("approximately 90% of normal caliber", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("bleeding", "OBS_FINDING"),
    ("none was seen", "OUTCOME_COMPLICATION"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("stent replacement", "PROC_ACTION")
]

# ==============================================================================
# PATH SETUP
# ==============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# PROCESSING FUNCTIONS
# ==============================================================================

def find_entity_spans(text, targets):
    """
    Locates start/end indices for target substrings.
    Handles multiple occurrences by tracking the search cursor.
    """
    spans = []
    cursor_map = {} # Tracks the search start index for each unique substring

    for sub, label in targets:
        start_search = cursor_map.get(sub, 0)
        start_idx = text.find(sub, start_search)
        
        if start_idx != -1:
            end_idx = start_idx + len(sub)
            
            # Verify exact text match
            extracted = text[start_idx:end_idx]
            if extracted != sub:
                print(f"CRITICAL ERROR: Mismatch for '{sub}'")
                continue

            spans.append({
                "start": start_idx,
                "end": end_idx,
                "label": label,
                "text": sub
            })
            
            # Update cursor to avoid re-finding the same instance if we intend to find the next one
            # Note: This logic assumes the TARGET_ENTITIES list is ordered by appearance 
            # or that we want unique instances.
            cursor_map[sub] = end_idx
        else:
            print(f"WARNING: Could not find substring '{sub}' in text.")
    
    return spans

def update_jsonl(file_path, data):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(new_spans):
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
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
    # Assuming 1 note = 1 file in this context, though architecture might differ
    stats["total_files"] += 1
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def log_warnings(spans):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        for span in spans:
            extracted = RAW_TEXT[span['start']:span['end']]
            if extracted != span['text']:
                log_entry = f"[{datetime.datetime.now()}] ALIGNMENT ERROR: {NOTE_ID} - Expected '{span['text']}', found '{extracted}' at {span['start']}:{span['end']}\n"
                f.write(log_entry)

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    # 1. Extract Spans
    extracted_spans = find_entity_spans(RAW_TEXT, TARGET_ENTITIES)

    # 2. Update ner_dataset_all.jsonl
    # Schema: {"id": NOTE_ID, "text": RAW_TEXT, "entities": [[start, end, label], ...]}
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }
    update_jsonl(NER_DATASET_FILE, ner_entry)

    # 3. Update notes.jsonl
    # Schema: {"id": NOTE_ID, "text": RAW_TEXT}
    notes_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    update_jsonl(NOTES_FILE, notes_entry)

    # 4. Update spans.jsonl
    # Schema: {"span_id": "Label_Offset", "note_id": NOTE_ID, "label": "...", "text": "...", "start": ..., "end": ...}
    for s in extracted_spans:
        span_entry = {
            "span_id": f"{s['label']}_{s['start']}",
            "note_id": NOTE_ID,
            "label": s["label"],
            "text": s["text"],
            "start": s["start"],
            "end": s["end"]
        }
        update_jsonl(SPANS_FILE, span_entry)

    # 5. Update stats.json
    update_stats(extracted_spans)

    # 6. Validate & Log
    log_warnings(extracted_spans)

    print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()