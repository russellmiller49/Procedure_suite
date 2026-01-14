import json
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_243"

# Raw text extracted from the provided note_243.txt content.
# Formatting (newlines) is preserved to match the visual structure of the file.
RAW_TEXT = """NOTE_ID:  note_243 SOURCE_FILE: note_243.txt PREOPERATIVE DIAGNOSIS: Endotracheal tumor 
POSTOPERATIVE DIAGNOSIS:  Endotracheal tumor s/p debulking 
PROCEDURE PERFORMED: 
1.         Rigid bronchoscopy with endoluminal tumor ablation(CPT 31641)
INDICATIONS: Tracheal Obstruction  
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives and paralytics the flexible bronchoscope was inserted through the LMA and into the pharynx.
We then advanced the bronchoscope into the subglottic space. The subglottic area and proximal trachea were normal.
At the level of the med trachea there was a large polypoid tumor with a ball valve effect with the base at the left posterior tracheal wall.
The tumor was about 90% obstructive of the normal tracheal diameter.
Additionally there wer multiple small polypoid lesions surrounding the large obstructive mass mostly on the posterior wall of the trachea but also on the anterior and right tracheal wall.
These findings extended for about 3cm. We did not attempt to pass the polypoid lesion with the bronchoscope during the initial inspection.
The flexible bronchoscope and LMA were removed and a 10mm non-ventilating rigid tracheoscope was subsequently inserted into the mid trachea just proximal to the tumor and connected to ventilator.
The T190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and the electrocautery snare was used to transect the obstructive mass at its base.
We then inserted the 1.9mm cryotherapy probe through the flexible bronchoscope and attached the probe using cryotherapy to the resected tumor and attempted to extract it through the rigid bronchoscope.
The tumor however was too large and repeatedly fell off of the cryoprobe when trying to pull it through the rigid scope.
We then switched to the large 2.4mm cryoprobe and again using the same technique were able to pull pieces of the tumor out if a piecemeal fashion and residual pieces of the resected tumor were then extracted with flexible forceps.
After the primary tumor was removed we then used APC to paint and shave the remaining tumor area on the posterior and lateral trachea walls until we were satisfied that we had achieved adequate luminal recanalization.
At the end of the procedure the trachea was approximately 95% open in comparison to unaffected areas.
We then were able to complete the distal airway inspection.
The lower trachea, right sided and left sided airways to at least the first sub-segments were uninvolved with no evidence of endobronchial tumor or extrinsic obstruction.
The rigid bronchoscope was then removed, and the procedure was completed. There were no complications.
Recommendations:
·           Transfer patient back to ICU 
·           Obtain post procedure CXR
·           Await final pathology results"""

# Defined entities based on Label_guide_UPDATED.csv
# Format: (Label, Text Span)
# Note: The script will calculate exact offsets dynamically to ensure robustness.
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Endotracheal tumor"), # Pre-op
    ("OBS_LESION", "Endotracheal tumor"), # Post-op
    ("PROC_ACTION", "debulking"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "tumor ablation"),
    ("ANAT_AIRWAY", "Tracheal"), # Indications
    ("OBS_FINDING", "Obstruction"), # Indications
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "pharynx"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "subglottic area"),
    ("ANAT_AIRWAY", "proximal trachea"),
    ("ANAT_AIRWAY", "med trachea"),
    ("OBS_LESION", "polypoid tumor"),
    ("LATERALITY", "left"),
    ("ANAT_AIRWAY", "posterior tracheal wall"),
    ("OBS_LESION", "tumor"), # "The tumor was about..."
    ("OUTCOME_AIRWAY_LUMEN_PRE", "90% obstructive"),
    ("ANAT_AIRWAY", "tracheal"), # "tracheal diameter"
    ("OBS_LESION", "polypoid lesions"),
    ("OBS_LESION", "obstructive mass"),
    ("ANAT_AIRWAY", "posterior wall of the trachea"),
    ("LATERALITY", "right"),
    ("ANAT_AIRWAY", "tracheal wall"),
    ("MEAS_SIZE", "3cm"),
    ("OBS_LESION", "polypoid lesion"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"), # Second mention
    ("MEAS_SIZE", "10mm"),
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("OBS_LESION", "tumor"), # "...proximal to the tumor"
    ("DEV_INSTRUMENT", "T190 Olympus flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # "...through the rigid bronchoscope"
    ("DEV_INSTRUMENT", "electrocautery snare"),
    ("PROC_ACTION", "transect"),
    ("OBS_LESION", "obstructive mass"), # "...transect the obstructive mass"
    ("MEAS_SIZE", "1.9mm"),
    ("DEV_INSTRUMENT", "cryotherapy probe"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"), # "...through the flexible bronchoscope"
    ("PROC_ACTION", "cryotherapy"),
    ("OBS_LESION", "resected tumor"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # "...extract it through the rigid..."
    ("OBS_LESION", "tumor"), # "The tumor however was too large"
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("DEV_INSTRUMENT", "rigid scope"),
    ("MEAS_SIZE", "2.4mm"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("OBS_LESION", "tumor"), # "...pieces of the tumor"
    ("OBS_LESION", "resected tumor"), # "...residual pieces of the resected tumor"
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("OBS_LESION", "primary tumor"),
    ("PROC_ACTION", "APC"),
    ("OBS_LESION", "tumor area"),
    ("ANAT_AIRWAY", "posterior and lateral trachea walls"),
    ("ANAT_AIRWAY", "trachea"), # "At the end ... the trachea"
    ("OUTCOME_AIRWAY_LUMEN_POST", "95% open"),
    ("ANAT_AIRWAY", "distal airway"),
    ("ANAT_AIRWAY", "lower trachea"),
    ("LATERALITY", "right sided"),
    ("LATERALITY", "left sided"),
    ("ANAT_AIRWAY", "airways"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OBS_FINDING", "extrinsic obstruction"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # "The rigid bronchoscope was then removed"
    ("OUTCOME_COMPLICATION", "no complications")
]

# ==============================================================================
# PATH SETUP
# ==============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# LOGIC
# ==============================================================================

def find_entity_spans(text, entities):
    """
    Finds strict start/end indices for entities.
    Handles multiple occurrences by keeping a cursor.
    """
    spans = []
    cursor = 0
    
    # We sort entities by their order of appearance to use a running cursor
    # However, the input list 'entities' is already roughly ordered.
    # To be safe, we will search from the last found position for duplicates.
    # A more robust way is to just search linearly and advance cursor.
    
    # Since the input list provided above is manual, we need to map them to text positions.
    # We will search for the first occurrence AFTER the previous entity's end.
    
    current_search_index = 0
    
    for label, substr in entities:
        start = text.find(substr, current_search_index)
        
        if start == -1:
            # Fallback: Restart search from 0 if out of order (though not expected with this list)
            start = text.find(substr)
            if start == -1:
                print(f"WARNING: Could not find '{substr}' in text.")
                continue
        
        end = start + len(substr)
        
        spans.append({
            "start": start,
            "end": end,
            "label": label,
            "text": substr
        })
        
        # Advance cursor to avoid overlapping same-text matches if they appear sequentially
        # But allow overlap if different text entities are nested (not common here)
        current_search_index = start + 1 
        
    return spans

def update_stats(stats_path, new_note_id, new_spans):
    """Updates the stats.json file."""
    if stats_path.exists():
        with open(stats_path, "r") as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file for this pipeline
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Calculate Spans
    extracted_spans = find_entity_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Data Objects
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_spans
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    span_entries = []
    for span in extracted_spans:
        span_entries.append({
            "span_id": f"{span['label']}_{span['start']}",
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        })

    # 3. Write to Files
    
    # ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, "a") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # notes.jsonl
    with open(NOTES_PATH, "a") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # spans.jsonl
    with open(SPANS_PATH, "a") as f:
        for entry in span_entries:
            f.write(json.dumps(entry) + "\n")
            
    # stats.json
    update_stats(STATS_PATH, NOTE_ID, extracted_spans)
    
    # 4. Validation & Logging
    with open(LOG_PATH, "a") as log:
        for span in extracted_spans:
            original = RAW_TEXT[span['start']:span['end']]
            if original != span['text']:
                log.write(f"MISMATCH [{datetime.datetime.now()}]: Note {NOTE_ID}, Label {span['label']}. Expected '{span['text']}', found '{original}' at {span['start']}:{span['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()