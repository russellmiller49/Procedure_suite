import json
import os
import datetime
from pathlib import Path
import re

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_248"

# Defines the target directory relative to this script's location
# Script assumption: Located in data/granular annotations/Python_update_scripts/
# Target: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = Path(__file__).resolve().parents[2] / "stats.json"

# ==========================================
# 2. Raw Text Content
# ==========================================
RAW_TEXT = """NOTE_ID:  note_248 SOURCE_FILE: note_248.txt PREOPERATIVE DIAGNOSIS: Tracheal-esophageal fistula presumed malignant tracheal obstruction 
POSTOPERATIVE DIAGNOSIS: Tracheal-esophageal fistula with mixed intrinsic/extrinsic presumed malignant tracheal obstruction 
PROCEDURE PERFORMED: Rigid bronchoscopy, Dual tracheal self-expandable airway stent placement
INDICATIONS: Tracheal-esophageal fistula with tracheal obstruction
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives an LMA was inserted and the flexible bronchoscope was passed through the vocal cords and into the trachea.
Approximately 3 cm distal to the vocal cords was a long segment of airway obstruction from extrinsic compression as well as submucosal infiltration.
At the maximum obstruction (mid trachea the airway was approximately 70% obstructed. The tumor was mostly confined to the posterior and left lateral wall. At the distal aspect of the tumor (3cm proximal to the main carina there was an obvious fistulous communication with the esophagus in the left recess between the posterior and lateral tracheal wall.  The distal 3 cm of the trachea appeared normal. There was purulent material in the left mainstem which was suctioned and all airways beyond the trachea appeared normal without evidence of mucosal irregularities of endobronchial disease. The flexible bronchoscope and LMA were 
removed and a 14mm non-ventilating rigid tracheoscope was subsequently inserted into the mid trachea and connected to ventilator. At this point we inserted a JAG guidewire into the trachea and with bronchoscopic observation placed a 16x60 mm Aero fully covered self-expandable metallic stent. The stent deployed more distally than expected with the distal edge within the right mainstem and the proximal edge not fully covering the obstruction.
We were able to pull the stent proximally but slightly more proximal than expected to cover the upper tracheal obstruction but the distal margin and TE fistula remained exposed.
At this point our thought was that the obstruction was covered and that GI would place a stent to cover the fistula.
The rigid bronchoscope was removed and GI then attempted through EGD to place the stent but were unable to bypass the esophageal obstruction.
We then re-intubated with the tracheoscope and using a similar technique to before and using forceps biopsied the exposed tumor.
We then placed a second 16X60 aero SEM into the distal trachea telescoping into the more proximal stent.
This resulted in complete occlusion of the fistula and complete opening of the trachea to a normal diameter.
At this point inspection was performed to evaluate for any bleeding or other complications and none was seen.
Once the patient was felt to be able to adequately protect airway the rigid bronchoscope was removed and the procedure was completed.
Post procedure diagnosis:
Mixed infiltrative tumor of the trachea and TE fistula s/p tracheal stenting with complete recanalization and obstruction of fistula 
Recommendations:
- Transfer to PACU
- Await tissue diagnosis
- Obtain post procedure CXR- TID saline nebulizers to avoid mucous impaction and obstruction of stent"""

# ==========================================
# 3. Entity Definitions
# ==========================================
# Format: (Label, substring_to_match, occurrence_index)
# occurrence_index: 0 for 1st match, 1 for 2nd match, etc.
# Use -1 to match ALL occurrences safely (only if text is unique enough)

ENTITY_TARGETS = [
    ("OBS_LESION", "Tracheal-esophageal fistula", 0),
    ("OBS_LESION", "malignant tracheal obstruction", 0),
    ("PROC_METHOD", "Rigid bronchoscopy", 0),
    ("DEV_STENT", "airway stent", 0),
    ("PROC_ACTION", "placement", 0), # Context: stent placement
    ("OBS_LESION", "Tracheal-esophageal fistula", 1), # Indications
    ("OBS_LESION", "tracheal obstruction", 0),
    ("DEV_INSTRUMENT", "LMA", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("ANAT_AIRWAY", "vocal cords", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("OBS_LESION", "airway obstruction", 0),
    ("OBS_LESION", "extrinsic compression", 0),
    ("OBS_LESION", "submucosal infiltration", 0),
    ("ANAT_AIRWAY", "mid trachea", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "70% obstructed", 0),
    ("OBS_LESION", "tumor", 0),
    ("ANAT_AIRWAY", "main carina", 0),
    ("OBS_LESION", "fistulous communication", 0),
    ("ANAT_AIRWAY", "left mainstem", 0),
    ("OBS_FINDING", "purulent material", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1),
    ("DEV_INSTRUMENT", "LMA", 1),
    ("MEAS_SIZE", "14mm", 0),
    ("DEV_INSTRUMENT", "rigid tracheoscope", 0),
    ("ANAT_AIRWAY", "mid trachea", 1),
    ("DEV_INSTRUMENT", "JAG guidewire", 0),
    ("DEV_STENT_SIZE", "16x60 mm", 0),
    ("DEV_STENT", "Aero fully covered self-expandable metallic stent", 0),
    ("ANAT_AIRWAY", "right mainstem", 0),
    ("OBS_LESION", "TE fistula", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("PROC_METHOD", "EGD", 0),
    ("DEV_INSTRUMENT", "tracheoscope", 0),
    ("DEV_INSTRUMENT", "forceps", 0),
    ("PROC_ACTION", "biopsied", 0),
    ("OBS_LESION", "tumor", 2), # exposed tumor
    ("DEV_STENT_SIZE", "16X60", 0),
    ("DEV_STENT", "aero SEM", 0),
    ("ANAT_AIRWAY", "distal trachea", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "complete occlusion of the fistula", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "complete opening of the trachea to a normal diameter", 0),
    ("OUTCOME_COMPLICATION", "none was seen", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 1),
    ("OUTCOME_AIRWAY_LUMEN_POST", "complete recanalization", 0)
]

# ==========================================
# 4. Processing Logic
# ==========================================

def get_spans(text, targets):
    spans = []
    # Sort by text length descending to handle overlapping substrings if necessary, 
    # though strict indexing is used here.
    
    for label, sub, index in targets:
        # Find all start indices of the substring
        matches = [m.start() for m in re.finditer(re.escape(sub), text)]
        
        if not matches:
            print(f"WARNING: Substring '{sub}' not found for label {label}")
            continue
            
        if index >= len(matches):
            print(f"WARNING: Index {index} out of bounds for '{sub}' (found {len(matches)})")
            continue
            
        start_char = matches[index]
        end_char = start_char + len(sub)
        
        # Validation
        extracted = text[start_char:end_char]
        if extracted != sub:
            print(f"ERROR: Mismatch processing '{sub}'")
            continue
            
        spans.append({
            "span_id": f"{label}_{start_char}",
            "note_id": NOTE_ID,
            "label": label,
            "text": extracted,
            "start": start_char,
            "end": end_char
        })
    
    return spans

def update_stats(new_spans):
    if not STATS_FILE.exists():
        print("Stats file not found, skipping stats update.")
        return

    with open(STATS_FILE, 'r') as f:
        stats = json.load(f)

    # Update global counters
    stats["total_notes"] += 1
    stats["total_files"] += 1
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    # Update label counts
    for span in new_spans:
        lbl = span["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1

    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    print("Stats updated.")

def write_data(spans):
    # 1. Update ner_dataset_all.jsonl
    ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": spans
    }
    
    with open(ner_file, 'a') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 2. Update notes.jsonl
    notes_file = OUTPUT_DIR / "notes.jsonl"
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(notes_file, 'a') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 3. Update spans.jsonl
    spans_file = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file, 'a') as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")

    # 4. Alignment Log
    log_file = OUTPUT_DIR / "alignment_warnings.log"
    with open(log_file, 'a') as f:
        for span in spans:
            # Double check alignment
            if RAW_TEXT[span["start"]:span["end"]] != span["text"]:
                f.write(f"MISALIGNMENT: {NOTE_ID} - {span['label']} - Expected '{span['text']}'\n")

# ==========================================
# 5. Execution
# ==========================================
if __name__ == "__main__":
    extracted_spans = get_spans(RAW_TEXT, ENTITY_TARGETS)
    
    if extracted_spans:
        write_data(extracted_spans)
        
        # Try to locate stats file relative to output dir if standard path fails
        # (Handling the environment difference between creating script and running it)
        if not STATS_FILE.exists():
            STATS_FILE = OUTPUT_DIR.parents[1] / "stats.json"
        
        update_stats(extracted_spans)
        
        print(f"Successfully processed {NOTE_ID} with {len(extracted_spans)} entities.")
    else:
        print("No entities extracted. Check text alignment.")