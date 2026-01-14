import json
import os
import datetime
from pathlib import Path

# -------------------------------------------------------------------------
# 1. Configuration & Path Setup
# -------------------------------------------------------------------------
NOTE_ID = "note_191"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# This ensures the script works relative to its location in the repo
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# -------------------------------------------------------------------------
# 2. Input Data (Raw Text & Entity Definitions)
# -------------------------------------------------------------------------
# The raw text corresponds to the content of note_191.txt
RAW_TEXT = """NOTE_ID:  note_191 SOURCE_FILE: note_191.txt Procedure Name: EBUS bronchoscopy
Indications: Mediastinal adenopathy 
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The carina is sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Ultrasound was utilized to identify and measure the radiographically enlarged station 7, 4R and 4L lymph nodes.
Sampling by transbronchial needle aspiration using Olympus EBUSTBNA 22 gauge and 19G needles.
At least 5 needle passes were performed at each lymph node station. All samples were sent for routine cytology.
ROSE identified granulomas within the 4R lymph node. Following completion of EBUS bronchoscopy the video bronchoscope was re-inserted and blood was suctioned from the airway.
There was no evidence of active bleeding and the bronchoscope was removed and procedure completed.
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Technically successful EBUS bronchoscopy
- Will await final pathology results"""

# Ordered list of entities to extract. 
# The script scans the text linearly to find specific instances.
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "EBUS bronchoscopy"),
    ("OBS_LESION", "Mediastinal adenopathy"),
    ("MEDICATION", "Propofol"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "video bronchoscope"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("PROC_METHOD", "Ultrasound"),
    ("ANAT_LN_STATION", "station 7"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "4L"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "22 gauge"),
    ("DEV_NEEDLE", "19G"),
    ("MEAS_COUNT", "5 needle passes"),
    ("OBS_ROSE", "granulomas"),
    ("ANAT_LN_STATION", "4R"),
    ("PROC_METHOD", "EBUS bronchoscopy"),
    ("OBS_FINDING", "active bleeding"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "Less than 5 cc"),
]

# -------------------------------------------------------------------------
# 3. Processing & Extraction Logic
# -------------------------------------------------------------------------
calculated_spans = []
cursor = 0
label_counts_update = {}

# Open log file for warnings
with open(LOG_PATH, "a") as log_file:
    for label, surface_form in ENTITIES_TO_EXTRACT:
        # Find the next occurrence of the text starting from 'cursor'
        start_idx = RAW_TEXT.find(surface_form, cursor)
        
        if start_idx == -1:
            # Log error if entity not found (prevents silent failures)
            log_file.write(f"[{datetime.datetime.now()}] WARNING: Could not find '{surface_form}' after index {cursor} in note {NOTE_ID}.\n")
            continue
            
        end_idx = start_idx + len(surface_form)
        
        # Create span object
        span_obj = {
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": surface_form,
            "start": start_idx,
            "end": end_idx
        }
        
        # Validation: check alignment
        extracted_text = RAW_TEXT[start_idx:end_idx]
        if extracted_text != surface_form:
             log_file.write(f"[{datetime.datetime.now()}] ALIGNMENT ERROR: Index mismatch for '{surface_form}' (found '{extracted_text}').\n")
        else:
            calculated_spans.append(span_obj)
            
            # Update local stats count
            label_counts_update[label] = label_counts_update.get(label, 0) + 1
        
        # Advance cursor to avoid overlapping same-text matches if strictly sequential
        cursor = start_idx + 1

# -------------------------------------------------------------------------
# 4. File Updates
# -------------------------------------------------------------------------

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[s["start"], s["end"], s["label"]] for s in calculated_spans]
}

with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in calculated_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if os.path.exists(STATS_PATH):
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        try:
            stats = json.load(f)
        except json.JSONDecodeError:
            stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
else:
    stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

# Increment global counters
stats["total_notes"] += 1
stats["total_files"] += 1 # Assuming 1 note = 1 file for this batch
stats["total_spans_raw"] += len(calculated_spans)
stats["total_spans_valid"] += len(calculated_spans)

# Increment label counts
for label, count in label_counts_update.items():
    stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count

# Save stats
with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

print(f"Successfully processed {NOTE_ID}. Extracted {len(calculated_spans)} entities.")