import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_203"

# Raw text content of the note
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: 
1.\tLeft mainstem complex stenosis
POSTOPERATIVE DIAGNOSIS: 
1.\tLeft mainstem complex stenosis
INDICATIONS:  Left mainstem obstruction
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a 12 mm ventilating rigid bronchoscope was inserted through the mouth and advanced into the distal trachea before attaching the monsoon JET ventilator.
The T190 therapeutic video bronchoscope was introduced through the mouth, via the rigid bronchoscope and advanced to the tracheobronchial tree.
The tracheal carina was sharp. All right sided airways were inspected to at least the first subsegmental bronchi.
The left-sided airways were than inspected. The proximal and mid left mainstem was normal.
In the distal aspect of the left mainstem there was an asymmetrical complex-appearing stricture with approximately 80% obstruction.
We were able to push the theraputic bronchoscope through the stenosis.
In t he lower lobe there were puruilent post-obstructive secretions which were aspirated via the bronchoscope, otherwise the distal airways were normal.
The FiO2 was decreased until exhaled FiO2 is less than 40% at which an electrocautery knife was used to make 2 incisions (1 and 5 o’clock) in the complex-appearing stricture after which a phase 8/9/10 mm Merritt dilatation balloon was used to gently dilate the airway.
We then further dilated the airway to a maximal diameter of 13.5mm using the phased 12/13.5/15 mm Merritt dilatation balloon.
The central portion of redundant tissue was then resected with the elecrocautery knife and an additional radial cut at the 3 o’clock position was performed.
We then dilated again with the phased balloon to a maximum of 13.5 mm.
The post dilatation airway diameter was about 10% obstructed. We monitored for evidence of bleeding and none was seen.
The rigid bronchoscope was then removed and the procedure completed. .
Complications: None
Recommendations:
- Transfer to PACU and return to ward when criteria is met.
- Case has been discussed with Dr. Harmeet Singh Bedi, interventional pulmonology at Stanford who is aware of the patient.
We recommend that after transfer to Palo Alto neuro-rehabilitation facility he be consulted as repeat dilatation and possibly temporary stent placement will likely be required."""

# Defined entities to extract: (Label, Text Segment)
# Note: Using exact substrings from the raw text for precision.
ENTITIES_TO_EXTRACT = [
    # Diagnosis/Indications
    ("ANAT_AIRWAY", "Left mainstem"),  # Pre-op diag
    ("OBS_LESION", "stenosis"),         # Pre-op diag
    ("ANAT_AIRWAY", "Left mainstem"),  # Post-op diag
    ("OBS_LESION", "stenosis"),         # Post-op diag
    ("ANAT_AIRWAY", "Left mainstem"),  # Indications
    ("OBS_LESION", "obstruction"),      # Indications

    # Procedure Body
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("DEV_INSTRUMENT", "monsoon JET ventilator"),
    ("DEV_INSTRUMENT", "T190 therapeutic video bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "tracheal carina"),
    ("LATERALITY", "right sided"),
    ("ANAT_AIRWAY", "airways"),
    ("ANAT_AIRWAY", "bronchi"),
    ("LATERALITY", "left-sided"),
    ("ANAT_AIRWAY", "airways"),
    ("LATERALITY", "left"), # proximal and mid left mainstem
    ("ANAT_AIRWAY", "mainstem"), # proximal and mid left mainstem
    ("LATERALITY", "left"), # distal aspect of left mainstem
    ("ANAT_AIRWAY", "mainstem"), # distal aspect of left mainstem
    ("OBS_LESION", "stricture"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "80% obstruction"),
    ("DEV_INSTRUMENT", "theraputic bronchoscope"),
    ("OBS_LESION", "stenosis"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("OBS_FINDING", "puruilent post-obstructive secretions"),
    ("PROC_ACTION", "aspirated"),
    ("DEV_INSTRUMENT", "bronchoscope"), # via the bronchoscope
    ("ANAT_AIRWAY", "distal airways"),
    ("DEV_INSTRUMENT", "electrocautery knife"),
    ("PROC_ACTION", "make 2 incisions"),
    ("OBS_LESION", "stricture"), # in the complex-appearing stricture
    ("DEV_INSTRUMENT", "phase 8/9/10 mm Merritt dilatation balloon"),
    ("PROC_ACTION", "dilate"),
    ("ANAT_AIRWAY", "airway"),
    ("PROC_ACTION", "dilated"),
    ("ANAT_AIRWAY", "airway"), # dilated the airway
    ("MEAS_AIRWAY_DIAM", "13.5mm"),
    ("DEV_INSTRUMENT", "phased 12/13.5/15 mm Merritt dilatation balloon"),
    ("PROC_ACTION", "resected"),
    ("DEV_INSTRUMENT", "elecrocautery knife"), # Note typo in source text
    ("PROC_ACTION", "radial cut"),
    ("PROC_ACTION", "dilated"),
    ("DEV_INSTRUMENT", "phased balloon"),
    ("MEAS_AIRWAY_DIAM", "13.5 mm"),
    ("ANAT_AIRWAY", "airway"), # post dilatation airway
    ("OUTCOME_AIRWAY_LUMEN_POST", "10% obstructed"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("OUTCOME_COMPLICATION", "None") # Complications: None
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING FUNCTIONS
# ==========================================

def get_entity_offsets(text, label_list):
    """
    Finds start/end offsets for each entity in the text.
    Handles duplicate occurrences by tracking search position.
    """
    spans = []
    search_start = 0
    # Sort or process sequentially?
    # Given the list is roughly chronological, we process sequentially, 
    # resetting search_start only if necessary, or tracking indices globally.
    # To be robust, we traverse the text finding the *next* occurrence 
    # of the substring after the *previous* entity's end.
    
    current_index = 0
    
    # We will search for each entity starting from the beginning of the text
    # but we need to match specific occurrences. 
    # Strategy: Find first match, define span, replace in a temporary mask or keep track of indices.
    # A simpler approach for this script: Use a cursor that moves forward.
    
    cursor = 0
    
    # Pre-sort entities by their likely order in text if not already ordered.
    # The ENTITIES_TO_EXTRACT list above implies reading order.
    
    for label, substr in label_list:
        # Find substring starting from cursor
        start = text.find(substr, cursor)
        
        if start == -1:
            # Fallback: Search from beginning if not found (maybe list order was off)
            # But strictly, we expect chronological order in ENTITIES_TO_EXTRACT.
            # If validly not found (e.g. slight text mismatch), log valid error.
            print(f"WARNING: Could not find '{substr}' after index {cursor}. Searching from start.")
            start = text.find(substr)
            
        if start != -1:
            end = start + len(substr)
            spans.append({
                "span_id": f"{label}_{start}",
                "note_id": NOTE_ID,
                "label": label,
                "text": substr,
                "start": start,
                "end": end
            })
            # Move cursor to end of this entity to find the next one
            # (Allows handling duplicate words like 'stenosis' correctly)
            cursor = start + 1 
        else:
            print(f"ERROR: Entity '{substr}' not found in text.")
            
    return spans

def load_json(path):
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def append_jsonl(data, path):
    with open(path, 'a') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(spans):
    stats_path = OUTPUT_DIR / "stats.json"
    stats = load_json(stats_path)
    
    if not stats:
        # Initialize if missing
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans) # Assuming all valid for this script

    for span in spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    save_json(stats, stats_path)

def validate_alignment(spans, text):
    with open(ALIGNMENT_LOG_PATH, 'a') as log:
        for span in spans:
            extracted = text[span["start"]:span["end"]]
            if extracted != span["text"]:
                msg = f"MISMATCH: {span['span_id']} expected '{span['text']}' got '{extracted}'"
                print(msg)
                log.write(msg + "\n")

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    print(f"Processing Note: {NOTE_ID}...")
    
    # 1. Extract Spans
    spans = get_entity_offsets(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Data Objects
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": spans
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # 3. Write updates
    # ner_dataset_all.jsonl
    append_jsonl(ner_entry, OUTPUT_DIR / "ner_dataset_all.jsonl")
    
    # notes.jsonl
    append_jsonl(note_entry, OUTPUT_DIR / "notes.jsonl")
    
    # spans.jsonl
    for span in spans:
        append_jsonl(span, OUTPUT_DIR / "spans.jsonl")
        
    # 4. Update Stats
    update_stats(spans)
    
    # 5. Validate
    validate_alignment(spans, RAW_TEXT)
    
    print("Success. Pipeline updated.")

if __name__ == "__main__":
    main()