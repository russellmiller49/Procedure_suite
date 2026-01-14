from pathlib import Path
import json
import os
import datetime

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
NOTE_ID = "note_255"

# Raw text content reconstructed from the input file
RAW_TEXT = """NOTE_ID:  note_255 SOURCE_FILE: note_255.txt PREOPERATIVE DIAGNOSIS: Tracheobronchomalacia
POSTOPERATIVE DIAGNOSIS: Tracheobronchomalacia
PROCEDURE PERFORMED: Rigid bronchoscopy, Silicone Y-stent removal
INDICATIONS: Completed stent trial
 
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite.
Once the patient was sedated and relaxed a 12 mm non-ventilating rigid tracheoscope was inserted through the mouth into the sublottic glottic space.
A flexible Q190 Olympus bronchoscope was inserted through the tracheoscope into the trachea and airway inspection was performed.
The patient’s Y stent was well placed without mucosal debris or obstruction.
At the distal tip of the right limb was mild granulation tissue causing about 10% obstruction and at the distal tip of the left mild was moderate granulation tissue causing about 40% obstruction.
The distal airways were widely patent.  The flexible bronchoscope was removed and the rigid optic was reinserted alongside rigid alligator forceps.
The forceps were used to grasp the proximal limb of the tracheal stent and were rotated repeatedly while withdrawing the stent into the rigid bronchoscope.
The stent was subsequently removed en-bloc with the rigid bronchoscope without difficulty.
Once his stent was removed an I-gel LMA was then placed and the flexible bronchoscope was reinserted.
There was some mild erythema in the areas of the struts from the move stent however the previously covered airways appeared to be relatively normal.
At this point  the cryotherapy probe was used to perform multiple 30 second freeze thaw cycles at the areas of residual granulation tissue within the left and right mainstems.
There was some mild bleeding associated with the treatment on the left requiring cold saline and 2cc of topical epinephrine.
Once we were confident that the bleeding had resolved the flexible bronchoscope was removed and the procedure was completed.
Complications: None
EBL: 5
 
Recommendations:
-	Transfer to PACU 
-	Discharge patient once criteria is met
-	Due to lack of symptomatic response to stenting would not recommend consideration of tracheoplasty at this time.
-	Recommend continuing of non-invasive ventilation for now."""

# Ordered list of entities to extract
# Format: (Label, Exact_Substring)
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("DEV_STENT_MATERIAL", "Silicone"),
    ("DEV_STENT", "Y-stent"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "non-ventilating rigid tracheoscope"),
    ("ANAT_AIRWAY", "sublottic glottic space"),
    ("DEV_INSTRUMENT", "flexible Q190 Olympus bronchoscope"),
    ("DEV_INSTRUMENT", "tracheoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("DEV_STENT", "Y stent"),
    ("OBS_FINDING", "mucosal debris"),
    ("OBS_FINDING", "obstruction"),
    ("LATERALITY", "right"),
    ("OBS_FINDING", "granulation tissue"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "10% obstruction"),
    ("LATERALITY", "left"),
    ("OBS_FINDING", "moderate granulation tissue"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "40% obstruction"),
    ("ANAT_AIRWAY", "distal airways"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "widely patent"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid optic"),
    ("DEV_INSTRUMENT", "rigid alligator forceps"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_STENT", "tracheal stent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "I-gel LMA"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("OBS_FINDING", "erythema"),
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "airways"),
    ("DEV_INSTRUMENT", "cryotherapy probe"),
    ("MEAS_TIME", "30 second"),
    ("PROC_ACTION", "freeze thaw cycles"),
    ("OBS_FINDING", "granulation tissue"),
    ("LATERALITY", "left"),
    ("LATERALITY", "right"),
    ("ANAT_AIRWAY", "mainstems"),
    ("OUTCOME_COMPLICATION", "bleeding"),
    ("LATERALITY", "left"),
    ("MEAS_VOL", "2cc"),
    ("MEDICATION", "epinephrine"),
    ("OUTCOME_COMPLICATION", "bleeding"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("OUTCOME_COMPLICATION", "None")
]

# -------------------------------------------------------------------------
# PATH SETUP
# -------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# -------------------------------------------------------------------------
# PROCESSING LOGIC
# -------------------------------------------------------------------------

def process_note():
    # 1. Calculate Indices
    spans = []
    current_idx = 0
    
    # We loop through the ordered entities list and find them sequentially
    for label, text in ENTITIES_TO_EXTRACT:
        start = RAW_TEXT.find(text, current_idx)
        
        if start == -1:
            # Fallback: simple error logging if sequence is broken (should not happen with correct data)
            print(f"ERROR: Could not find '{text}' after index {current_idx}")
            continue
            
        end = start + len(text)
        spans.append({
            "label": label,
            "text": text,
            "start": start,
            "end": end
        })
        current_idx = start + 1 # Advance cursor slightly to allow overlap if valid, or use 'end'

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {"start": s["start"], "end": s["end"], "label": s["label"]}
            for s in spans
        ]
    }
    
    with open(NER_DATASET_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
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
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    except FileNotFoundError:
        # Initialize if missing (fallback)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0, 
            "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)

    for s in spans:
        lbl = s["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        for s in spans:
            extracted = RAW_TEXT[s["start"]:s["end"]]
            if extracted != s["text"]:
                log.write(f"{datetime.datetime.now()} - MISMATCH - Note: {NOTE_ID} - "
                          f"Expected: '{s['text']}', Found: '{extracted}' at {s['start']}:{s['end']}\n")

if __name__ == "__main__":
    process_note()
    print(f"Successfully processed {NOTE_ID} and updated ML training files.")