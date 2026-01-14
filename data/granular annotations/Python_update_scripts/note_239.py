import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_239"
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Extraction
# ==========================================

RAW_TEXT = """NOTE_ID:  note_239 SOURCE_FILE: note_239.txt PREOPERATIVE DIAGNOSIS: Tracheobronchomalacia
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

# Helper to find offsets
def find_offsets(text, substring, start_search=0):
    start = text.find(substring, start_search)
    if start == -1:
        return None
    return start, start + len(substring)

# Entities to map [Label, Text Segment]
entities_to_map = [
    # Header
    ("ANAT_AIRWAY", "Tracheobronchomalacia"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("DEV_STENT_MATERIAL", "Silicone"),
    ("DEV_STENT", "Y-stent"),
    ("PROC_ACTION", "removal"),
    
    # Body
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "sublottic glottic space"),
    ("DEV_INSTRUMENT", "Q190 Olympus bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("PROC_ACTION", "airway inspection"),
    ("DEV_STENT", "Y stent"),
    ("OBS_FINDING", "mucosal debris"),
    ("OBS_FINDING", "obstruction"),
    
    ("LATERALITY", "right"),
    ("OBS_FINDING", "granulation tissue"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "10% obstruction"),
    ("LATERALITY", "left"),
    ("OBS_FINDING", "granulation tissue"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "40% obstruction"),
    
    ("OUTCOME_AIRWAY_LUMEN_POST", "widely patent"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid alligator forceps"),
    
    # Extraction Sequence (Source 8 & 9)
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_STENT", "stent"), # "...tracheal stent..."
    ("DEV_STENT", "stent"), # "...withdrawing the stent..." (Added to maintain cursor alignment)
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # Source 8
    
    ("DEV_STENT", "stent"), # Source 9: "The stent..."
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # Source 9: "...with the rigid bronchoscope..."
    
    ("DEV_STENT", "stent"), # Source 10: "Once his stent..."
    ("DEV_INSTRUMENT", "I-gel LMA"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    
    ("OBS_FINDING", "erythema"),
    ("DEV_STENT", "stent"), # Source 11: "...move stent..."
    
    ("DEV_INSTRUMENT", "cryotherapy probe"),
    ("MEAS_TIME", "30 second"),
    ("PROC_ACTION", "freeze thaw cycles"),
    ("OBS_FINDING", "granulation tissue"),
    ("LATERALITY", "left"),
    ("LATERALITY", "right"),
    ("ANAT_AIRWAY", "mainstems"),
    
    ("OBS_FINDING", "bleeding"),
    ("LATERALITY", "left"),
    ("MEAS_VOL", "2cc"),
    ("MEDICATION", "epinephrine"), # Fixed case (Epinephrine -> epinephrine)
    
    ("OUTCOME_COMPLICATION", "bleeding had resolved"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("OUTCOME_COMPLICATION", "None"),
]

# Processing
processed_entities = []
cursor = 0

for label, substring in entities_to_map:
    span = find_offsets(RAW_TEXT, substring, cursor)
    if span:
        start, end = span
        processed_entities.append({
            "label": label,
            "text": substring,
            "start": start,
            "end": end
        })
        cursor = start  # Move cursor forward
    else:
        with open(LOG_FILE, "a") as log:
            log.write(f"[{datetime.datetime.now()}] Warning: Could not find '{substring}' in {NOTE_ID}\n")

# ==========================================
# 3. File Updates
# ==========================================

# A. Update ner_dataset_all.jsonl
new_dataset_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": processed_entities
}

with open(DATASET_FILE, "a") as f:
    f.write(json.dumps(new_dataset_entry) + "\n")

# B. Update notes.jsonl
new_note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_FILE, "a") as f:
    f.write(json.dumps(new_note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_FILE, "a") as f:
    for ent in processed_entities:
        span_id = f"{ent['label']}_{ent['start']}"
        span_entry = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        f.write(json.dumps(span_entry) + "\n")

# D. Update stats.json
if os.path.exists(STATS_FILE):
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
stats["total_spans_raw"] += len(processed_entities)
stats["total_spans_valid"] += len(processed_entities)

for ent in processed_entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_FILE, "w") as f:
    json.dump(stats, f, indent=4)

# ==========================================
# 4. Validation
# ==========================================
with open(LOG_FILE, "a") as log:
    for ent in processed_entities:
        extracted = RAW_TEXT[ent["start"]:ent["end"]]
        if extracted != ent["text"]:
            log.write(f"[{datetime.datetime.now()}] MISMATCH in {NOTE_ID}: Expected '{ent['text']}', got '{extracted}'\n")

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")