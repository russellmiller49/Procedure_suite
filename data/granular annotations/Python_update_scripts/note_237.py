import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_237"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# Using Path(__file__) requires the script to be saved to a file. 
# For this standalone execution, we assume standard structure or create it.
try:
    BASE_DIR = Path(__file__).resolve().parents[2]
except NameError:
    # Fallback for interactive environments (Jupyter/REPL)
    BASE_DIR = Path(".").resolve()

OUTPUT_DIR = BASE_DIR / "ml_training" / "granular_ner"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Log file for alignment warnings
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# Input Text (Raw content from note_237.txt)
RAW_TEXT = """NOTE_ID:  note_237 SOURCE_FILE: note_237.txt PREOPERATIVE DIAGNOSIS: lung cancer with complete left mainstem stenosis.
POSTOPERATIVE DIAGNOSIS: Resolved mainstem obstruction s/p areo stent
PROCEDURE PERFORMED: Rigid bronchoscopy with Aero tracheobronchial stent placement in the left mainstem
INDICATIONS: Obstruction of left mainstem bronchus
Consent was obtained from the family prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient’s family acknowledged and gave consent.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives the a10mm ventilating rigid bronchoscope was subsequently inserted into the posterior oropharynx.
The ETT was removed and the rigid bronchoscope was advanced past the vocal cords into the distal trachea and connected to ventilator.
Airway inspection was performed and the tracheal and right sided airways were normal.
At the proximal aspect of the left mainstem was intrinsic tumor causing complete obstruction of the airway.
Using the 2.4 mm cryoprobe we are able to extract portions of the tumor slowly and further extraction was performed using utilized APC and flexible forceps to “burn and shave” the remaining until eventually the LC1 carina was seen.
In the left upper lobe the airways appeared normal without evidence of tumor while in the left lower lobe mucosal tumor invasion was present but non-obstructive to at least the first subsegments.
Although we were able to debulk the majority of tumor in the mainstem there remained significant residual tumor burden causing partial airway obstruction and it was decided to place and Aero SEMS to maintain patency and for barrier effect.
At this point we measured the length of the obstruction and inserted a Jagwire through the flexible bronchoscope into the left lower lobe past the mainstem and using fluoroscopy marked the proximal and distal edges of the obstructed left mainstem with radiopaque markers (paper clips) taped to the patient’s chest wall.
The flexible bronchoscope was removed and an Aero 12x40 mm stent was advanced over the guidewire and positioned based on the external markers under fluoroscopic observation.
The flexible bronchoscope was re-inserted and the stent was evaluated and was in appropriate position with a residual airway of >90% of normal.
Once we were satisfied that no further intervention was required and that there was no evidence of active bleeding the flexible bronchoscope was removed and bronchoscopic intubation was performed with an 8.0 ETT and the procedure was completed.
Recommendations:
-          Transfer back to ICU
-          Post-procedure x-ray
-          Start 3% saline nebs 4cc 3 times daily for stent maintenance.
-          Ensure supplemental oxygen is humidified
-          Please arrange for patient to have nebulizer at home for continued hypertonic saline nebs post-discharge."""

# ==========================================
# 2. Entity Definition (Manual Extraction)
# ==========================================
# Format: (Label, Text_Snippet, Occurrence_Index)
# Occurrence_Index: 0 for 1st match, 1 for 2nd match, etc.
extracted_entities_data = [
    ("OBS_LESION", "lung cancer", 0),
    ("ANAT_AIRWAY", "left mainstem", 0),
    ("OBS_LESION", "stenosis", 0),
    ("PROC_METHOD", "Rigid bronchoscopy", 0),
    ("DEV_STENT", "Aero tracheobronchial stent", 0),
    ("ANAT_AIRWAY", "left mainstem", 1),
    ("OBS_LESION", "Obstruction", 0),
    ("ANAT_AIRWAY", "left mainstem bronchus", 0),
    ("MEAS_SIZE", "10mm", 0),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope", 0),
    ("ANAT_AIRWAY", "posterior oropharynx", 0),
    ("DEV_INSTRUMENT", "ETT", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("ANAT_AIRWAY", "distal trachea", 0),
    ("ANAT_AIRWAY", "tracheal", 0),
    ("ANAT_AIRWAY", "right sided airways", 0),
    ("ANAT_AIRWAY", "left mainstem", 2),
    ("OBS_LESION", "intrinsic tumor", 0),
    ("OBS_LESION", "obstruction", 1),
    ("MEAS_SIZE", "2.4 mm", 0),
    ("DEV_INSTRUMENT", "cryoprobe", 0),
    ("PROC_ACTION", "extract", 0),
    ("OBS_LESION", "tumor", 1),
    ("DEV_INSTRUMENT", "APC", 0),
    ("DEV_INSTRUMENT", "flexible forceps", 0),
    ("PROC_ACTION", "burn and shave", 0),
    ("ANAT_AIRWAY", "LC1 carina", 0),
    ("ANAT_LUNG_LOC", "left upper lobe", 0),
    ("OBS_LESION", "tumor", 2),
    ("ANAT_LUNG_LOC", "left lower lobe", 0),
    ("OBS_LESION", "mucosal tumor invasion", 0),
    ("PROC_ACTION", "debulk", 0),
    ("OBS_LESION", "tumor", 3),
    ("ANAT_AIRWAY", "mainstem", 0),
    ("OBS_LESION", "residual tumor burden", 0),
    ("DEV_STENT", "Aero SEMS", 0),
    ("DEV_INSTRUMENT", "Jagwire", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("ANAT_LUNG_LOC", "left lower lobe", 1),
    ("ANAT_AIRWAY", "mainstem", 1),
    ("PROC_METHOD", "fluoroscopy", 0),
    ("ANAT_AIRWAY", "left mainstem", 3),
    ("DEV_INSTRUMENT", "radiopaque markers", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1),
    ("DEV_STENT", "Aero", 2),
    ("DEV_STENT_SIZE", "12x40 mm", 0),
    ("DEV_STENT", "stent", 2),
    ("PROC_METHOD", "fluoroscopic", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 2),
    ("DEV_STENT", "stent", 3),
    ("OUTCOME_AIRWAY_LUMEN_POST", ">90% of normal", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 3),
    ("PROC_ACTION", "bronchoscopic intubation", 0),
    ("MEAS_SIZE", "8.0", 0),
    ("DEV_INSTRUMENT", "ETT", 1),
    ("MEDICATION", "3% saline", 0),
    ("MEDICATION", "supplemental oxygen", 0),
    ("MEDICATION", "hypertonic saline", 0)
]

# Helper to calculate precise offsets handling duplicates
def calculate_spans(text, entities_data):
    spans = []
    # Keep track of last index found for each token to handle sequential search if needed
    # However, strict occurrence indexing is safer for this script.
    
    for label, substr, occurrence in entities_data:
        start = -1
        current_occurrence = 0
        search_pos = 0
        
        while True:
            idx = text.find(substr, search_pos)
            if idx == -1:
                break
            if current_occurrence == occurrence:
                start = idx
                break
            current_occurrence += 1
            search_pos = idx + 1
            
        if start != -1:
            end = start + len(substr)
            spans.append({
                "label": label,
                "start": start,
                "end": end,
                "text": substr
            })
        else:
            with open(LOG_FILE, "a") as f:
                f.write(f"[{datetime.datetime.now()}] Warning: Could not find occurrence {occurrence} of '{substr}' in {NOTE_ID}\n")
    
    return spans

# Calculate Spans
VALID_SPANS = calculate_spans(RAW_TEXT, extracted_entities_data)

# ==========================================
# 3. File Update Logic
# ==========================================

def update_ner_dataset():
    fpath = OUTPUT_DIR / "ner_dataset_all.jsonl"
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in VALID_SPANS]
    }
    with open(fpath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes():
    fpath = OUTPUT_DIR / "notes.jsonl"
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(fpath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans():
    fpath = OUTPUT_DIR / "spans.jsonl"
    with open(fpath, "a", encoding="utf-8") as f:
        for span in VALID_SPANS:
            span_id = f"{span['label']}_{span['start']}"
            entry = {
                "span_id": span_id,
                "note_id": NOTE_ID,
                "label": span["label"],
                "text": span["text"],
                "start": span["start"],
                "end": span["end"]
            }
            f.write(json.dumps(entry) + "\n")

def update_stats():
    fpath = OUTPUT_DIR / "stats.json"
    
    # Load existing or create new
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
    else:
        stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

    # Update counts
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file for this pipeline
    stats["total_spans_raw"] += len(VALID_SPANS)
    stats["total_spans_valid"] += len(VALID_SPANS)
    
    for span in VALID_SPANS:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

def validate_alignment():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for span in VALID_SPANS:
            extracted = RAW_TEXT[span["start"]:span["end"]]
            if extracted != span["text"]:
                f.write(f"[{datetime.datetime.now()}] ALIGNMENT ERROR {NOTE_ID}: Span {span['start']}-{span['end']} expected '{span['text']}' but got '{extracted}'\n")

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Processing {NOTE_ID}...")
    
    # 1. Update NER Dataset
    update_ner_dataset()
    
    # 2. Update Notes
    update_notes()
    
    # 3. Update Spans
    update_spans()
    
    # 4. Update Stats
    update_stats()
    
    # 5. Validate
    validate_alignment()
    
    print(f"Successfully updated pipeline in {OUTPUT_DIR}")