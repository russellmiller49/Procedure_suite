import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_239"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text Content
# ==========================================
TEXT_CONTENT = """NOTE_ID:  note_239 SOURCE_FILE: note_239.txt PREOPERATIVE DIAGNOSIS: Tracheobronchomalacia
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

# ==========================================
# 3. Entity Definitions
# ==========================================
# List of (Label, Text_Segment, Occurrence_Index)
# Occurrence_Index helps handle duplicate phrases (0 = 1st instance, 1 = 2nd, etc.)
entities_to_extract = [
    ("OBS_FINDING", "Tracheobronchomalacia", 0),
    ("OBS_FINDING", "Tracheobronchomalacia", 1),
    ("PROC_METHOD", "Rigid bronchoscopy", 0),
    ("DEV_STENT_MATERIAL", "Silicone", 0),
    ("DEV_STENT", "Y-stent", 0),
    ("PROC_ACTION", "removal", 0), # "Silicone Y-stent removal"
    ("MEAS_SIZE", "12 mm", 0),
    ("DEV_INSTRUMENT", "rigid tracheoscope", 0),
    ("ANAT_AIRWAY", "sublottic glottic space", 0),
    ("DEV_INSTRUMENT", "Q190 Olympus bronchoscope", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("DEV_STENT", "Y stent", 0), # "The patient's Y stent"
    ("LATERALITY", "right", 0), # "right limb"
    ("OBS_FINDING", "granulation tissue", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "10% obstruction", 0),
    ("LATERALITY", "left", 0), # "left mild was moderate..."
    ("OBS_FINDING", "granulation tissue", 1),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "40% obstruction", 0),
    ("ANAT_AIRWAY", "distal airways", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "widely patent", 0), # Pre-removal assessment of distal
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("DEV_INSTRUMENT", "rigid optic", 0),
    ("DEV_INSTRUMENT", "rigid alligator forceps", 0),
    ("DEV_STENT", "tracheal stent", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 1), # "into the rigid bronchoscope"
    ("DEV_STENT", "stent", 2), # "withdrawing the stent"
    ("PROC_ACTION", "removed", 1), # "stent was subsequently removed"
    ("DEV_INSTRUMENT", "rigid bronchoscope", 2), # "with the rigid bronchoscope"
    ("DEV_STENT", "stent", 3), # "Once his stent was removed"
    ("PROC_ACTION", "removed", 2), # "Once his stent was removed"
    ("DEV_INSTRUMENT", "I-gel LMA", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1),
    ("OBS_FINDING", "erythema", 0),
    ("DEV_STENT", "stent", 4), # "move stent" (likely typo in note for 'removed', but labeling entity)
    ("DEV_INSTRUMENT", "cryotherapy probe", 0),
    ("MEAS_TIME", "30 second", 0),
    ("PROC_ACTION", "freeze thaw cycles", 0),
    ("OBS_FINDING", "granulation tissue", 2), # "residual granulation tissue"
    ("LATERALITY", "left", 1),
    ("LATERALITY", "right", 1),
    ("ANAT_AIRWAY", "mainstems", 0),
    ("OBS_FINDING", "bleeding", 0),
    ("MEAS_VOL", "2cc", 0),
    ("MEDICATION", "Epinephrine", 0),
    ("OUTCOME_COMPLICATION", "bleeding had resolved", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 2),
    ("OUTCOME_COMPLICATION", "None", 0)
]

# ==========================================
# 4. Processing & Extraction Logic
# ==========================================
extracted_entities = []
warnings = []

# Helper to find offsets
def find_offsets(text, substring, occurrence):
    start = -1
    for _ in range(occurrence + 1):
        start = text.find(substring, start + 1)
        if start == -1:
            return None, None
    return start, start + len(substring)

for label, subtext, occ in entities_to_extract:
    start, end = find_offsets(TEXT_CONTENT, subtext, occ)
    if start is not None:
        extracted_entities.append({
            "label": label,
            "text": subtext,
            "start": start,
            "end": end
        })
    else:
        warnings.append(f"Could not find '{subtext}' (occurrence {occ}) in note.")

# Sort entities by start index
extracted_entities.sort(key=lambda x: x["start"])

# ==========================================
# 5. File Operations
# ==========================================

# A. Append to ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": TEXT_CONTENT,
    "entities": [[e["start"], e["end"], e["label"]] for e in extracted_entities]
}

with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Append to notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": TEXT_CONTENT
}

with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Append to spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for e in extracted_entities:
        span_entry = {
            "span_id": f"{e['label']}_{e['start']}",
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        }
        f.write(json.dumps(span_entry) + "\n")

# D. Update stats.json
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
# Assuming 1 file per script run for simplicity in this context
stats["total_files"] += 1 
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for e in extracted_entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# E. Log Warnings (Validation)
with open(LOG_PATH, "a", encoding="utf-8") as f:
    timestamp = datetime.datetime.now().isoformat()
    if warnings:
        for w in warnings:
            f.write(f"[{timestamp}] [NOTE: {NOTE_ID}] {w}\n")
    
    # Verify strict string matching again for log
    for e in extracted_entities:
        sliced_text = TEXT_CONTENT[e["start"]:e["end"]]
        if sliced_text != e["text"]:
            f.write(f"[{timestamp}] [NOTE: {NOTE_ID}] Mismatch: Expected '{e['text']}' but found '{sliced_text}' at {e['start']}:{e['end']}\n")

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}.")