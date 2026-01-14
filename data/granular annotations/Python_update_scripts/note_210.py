from pathlib import Path
import json
import os
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_210"

# Raw text content of the note
NOTE_TEXT = """After pt was induced by Anesthesia and LMA was placed, the OR table was rotated 180 degrees.
The diagnostic bronchoscope was introduced and LMA placement was adjusted. Whitish nodules were noted on the right vocal cord.
The scope was then passed into the trachea and the central airways were inspected.
Moderate purulent secretions were noted at the RUL. The endobronchial mucosa of the RUL was edematous and friable and the apical subsegment bronchus appeared somewhat narrowed as though from extrinsic compression.
The diagnostic scope was removed and the EBUS scope was introduced.
The hilar and mediastinal lymph nodes were surveyed and all nodes were measured.
The nodes that met criteria for sampling (i.e. >5mm short axis diameter) were then sampled by real time EBUS TBNA in the following order: 4R, 7, 2R, 10R, 11R.
The EBUS scope was then removed and the diagnostic scope was introduced.
Radial probe EBUS was inserted into the RUL apical subsegment until abnormal tissue was identified at approx 4cm from the end of the scope.
This area was then biopsied with needle and brush. A BAL was then performed in the RUL.
The central airways were inspected to confirm hemostasis and the scope was removed."""

# Helper to locate entities (prevents manual offset errors)
def find_entity(text, substring, start_search=0):
    start = text.find(substring, start_search)
    if start == -1:
        raise ValueError(f"Entity '{substring}' not found starting from index {start_search}")
    return start, start + len(substring)

# Annotated Entities List
# Format: (Label, Text_Substring)
# Order must match appearance in text to allow sequential searching
entities_to_map = [
    ("DEV_INSTRUMENT", "LMA"),
    ("DEV_INSTRUMENT", "diagnostic bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("OBS_LESION", "Whitish nodules"),
    ("ANAT_AIRWAY", "right vocal cord"),
    ("DEV_INSTRUMENT", "scope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "central airways"),
    ("OBS_FINDING", "purulent secretions"),
    ("ANAT_LUNG_LOC", "RUL"),
    ("ANAT_AIRWAY", "endobronchial mucosa"),
    ("ANAT_LUNG_LOC", "RUL"),
    ("OBS_FINDING", "edematous"),
    ("OBS_FINDING", "friable"),
    ("ANAT_LUNG_LOC", "apical subsegment bronchus"),
    ("OBS_FINDING", "narrowed"),
    ("OBS_FINDING", "extrinsic compression"),
    ("DEV_INSTRUMENT", "diagnostic scope"),
    ("DEV_INSTRUMENT", "EBUS scope"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal lymph nodes"),
    ("MEAS_SIZE", "5mm"),
    ("PROC_METHOD", "real time EBUS"),
    ("PROC_ACTION", "TBNA"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "7"),
    ("ANAT_LN_STATION", "2R"),
    ("ANAT_LN_STATION", "10R"),
    ("ANAT_LN_STATION", "11R"),
    ("DEV_INSTRUMENT", "EBUS scope"),
    ("DEV_INSTRUMENT", "diagnostic scope"),
    ("PROC_METHOD", "Radial probe EBUS"),
    ("ANAT_LUNG_LOC", "RUL"),
    ("ANAT_LUNG_LOC", "apical subsegment"),
    ("OBS_LESION", "abnormal tissue"),
    ("MEAS_SIZE", "4cm"),
    ("DEV_INSTRUMENT", "scope"),
    ("PROC_ACTION", "biopsied"),
    ("DEV_INSTRUMENT", "needle"),
    ("DEV_INSTRUMENT", "brush"),
    ("PROC_ACTION", "BAL"),
    ("ANAT_LUNG_LOC", "RUL"),
    ("ANAT_AIRWAY", "central airways"),
    ("OUTCOME_COMPLICATION", "hemostasis"),
    ("DEV_INSTRUMENT", "scope")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = OUTPUT_DIR / "stats.json"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

def update_pipeline():
    # 1. Calculate Offsets
    final_entities = []
    current_idx = 0
    
    for label, substr in entities_to_map:
        start, end = find_entity(NOTE_TEXT, substr, current_idx)
        final_entities.append({
            "label": label,
            "start": start,
            "end": end,
            "text": substr
        })
        # Advance index to ensure sequential matching (handling duplicate words)
        current_idx = start + 1

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": NOTE_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in final_entities]
    }
    
    with open(NER_DATASET_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": NOTE_TEXT}
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
        for ent in final_entities:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    except FileNotFoundError:
        # Fallback if stats file doesn't exist yet
        stats = {
            "total_files": 0, "total_notes": 0, 
            "total_spans_raw": 0, "total_spans_valid": 0, 
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(final_entities)
    stats["total_spans_valid"] += len(final_entities)

    for ent in final_entities:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validation Log
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        for ent in final_entities:
            extracted = NOTE_TEXT[ent["start"]:ent["end"]]
            if extracted != ent["text"]:
                log.write(f"MISMATCH [{datetime.datetime.now()}]: Note {NOTE_ID}, Label {ent['label']} - Expected '{ent['text']}', found '{extracted}'\n")

    print(f"Successfully processed {NOTE_ID}. Added {len(final_entities)} entities.")

if __name__ == "__main__":
    update_pipeline()