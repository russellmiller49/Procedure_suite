import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_252"

# Cleaning the raw text from source tags and reconstructing the note
RAW_TEXT = (
    "Procedure Name: Bronchoscopy with endobronchial glue instillation \n"
    "Indications: Post-pneumonectomy broncho-pleural fistula\n"
    "Medications: Per anesthesia\n"
    "Patient intubated by anesthesia with 8.5 ETT prior to case.\n"
    "The Q190 video bronchoscope was introduced through ETT and advanced to the tracheobronchial tree.\n"
    "ETT tip was approximately 4cm above carina. The distal trachea was of normal caliber. The carina was sharp.\n"
    "The right sided tracheobronchial tree was examined to at least the first subsegmental level and bronchial mucosa and anatomy were normal without endobronchial lesions or secretions.\n"
    "The left mainstem stump was then visualized with obvious pinpoint BP fistula, the remained of the stump appeared to be intact however we did not probe the stump due to concern for extending the fistula.\n"
    "At this point the Veno-seal sealant delivery system catheter was advanced through the working channel of the bronchoscope and glue was then carefully applied to seal the fistula which appeared to be successful.\n"
    "The bronchoscope was then removed and our portion of the procedure was completed.\n"
    "Complications: none\n"
    "Estimated Blood Loss: None\n"
    "Post-procedure diagnosis: BF fistula with successful occlusion via sealant."
)

# Entities identified based on Label_guide_UPDATED.csv
# Each entry: (Label, Text_Span)
# Note: Offsets will be calculated dynamically to ensure precision.
ENTITY_DATA = [
    ("PROC_ACTION", "Bronchoscopy"),
    ("PROC_ACTION", "endobronchial glue instillation"),
    ("CTX_HISTORICAL", "Post-pneumonectomy"),
    ("OBS_LESION", "broncho-pleural fistula"),
    ("MEAS_SIZE", "8.5"),
    ("DEV_INSTRUMENT", "ETT"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "ETT"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "ETT"),
    ("MEAS_SIZE", "4cm"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("LATERALITY", "right sided"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "bronchial mucosa"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("LATERALITY", "left"),
    ("ANAT_AIRWAY", "mainstem stump"),
    ("OBS_LESION", "BP fistula"),
    ("ANAT_AIRWAY", "stump"),
    ("ANAT_AIRWAY", "stump"),
    ("OBS_LESION", "fistula"),
    ("DEV_CATHETER", "Veno-seal sealant delivery system catheter"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("PROC_ACTION", "seal"),
    ("OBS_LESION", "fistula"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("OBS_LESION", "BF fistula")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"


def calculate_offsets(text, entity_data):
    """
    Calculates start/end offsets for entities. 
    Handles duplicate terms by tracking search cursor position.
    """
    spans = []
    search_cursor = 0
    # To handle overlapping searches or non-sequential list if necessary, 
    # typically we scan sequentially. However, simply finding the *next* occurrence 
    # is usually safer for sequential narratives.
    
    # We will iterate through the text. To allow for non-sequential data in ENTITY_DATA
    # (though in this script they are ordered), we should be careful. 
    # For this script, we assume ENTITY_DATA is in order of appearance in text.
    
    last_idx = 0
    for label, substr in entity_data:
        start = text.find(substr, last_idx)
        if start == -1:
            # Fallback: search from beginning if not found sequentially (should not happen if data is correct)
            start = text.find(substr)
            if start == -1:
                print(f"Warning: '{substr}' not found in text.")
                continue
        
        end = start + len(substr)
        spans.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        last_idx = start + 1 # Advance cursor just past start to allow overlapping/nested logic if needed, 
                             # or 'end' if strictly non-overlapping. 
                             # 'start + 1' allows catching distinct entities sharing text if needed, 
                             # but here we rely on the specific order.
    
    return spans

def main():
    # 1. Calculate Spans
    spans = calculate_offsets(RAW_TEXT, ENTITY_DATA)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in spans]
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
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for s in spans:
            span_entry = {
                "span_id": f"{s['label']}_{s['start']}",
                "note_id": NOTE_ID,
                "label": s["label"],
                "text": s["text"],
                "start": s["start"],
                "end": s["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
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
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans) # All assumed valid in this controlled script

    for s in spans:
        lbl = s["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for s in spans:
            extracted = RAW_TEXT[s["start"]:s["end"]]
            if extracted != s["text"]:
                log_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{s['text']}', found '{extracted}' at {s['start']}:{s['end']}\n"
                f.write(log_msg)

    print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()