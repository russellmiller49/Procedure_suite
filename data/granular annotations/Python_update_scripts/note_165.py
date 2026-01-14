import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_165"

# Define the exact text content of the note
# (Preserving newlines and spacing as presented in the source)
RAW_TEXT = """PRE-PROCEDURE DIAGNISOS: pulmonary nodule 
POST- PROCEDURE DIAGNISOS: pulmonary nodule 
PROCEDURE PERFORMED:  
Flexible bronchoscopy with electromagnetic navigation under flouroscopic and EBUS guidance with isocyanate green dye injection for surgical resection.
CPT 31654 Bronchoscope with Endobronchial Ultrasound guidance for peripheral lesion
CPT 31629 Flexible bronchoscopy with fluoroscopic trans-bronchial needle aspiration
CPT +31627 Bronchoscopy with computer assisted image guided navigation
INDICATIONS FOR EXAMINATION:   pulmonary nodules requiring surgical resection
SEDATION: General Anesthesia
FINDINGS: Following intravenous medications as per the record the patient was intubated with an 8. 5 ET tube by anesthesia.
The T190 video bronchoscope was then introduced through the endotracheal tube and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. The super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using the navigational map created preprocedurally we advanced the 180 degree edge catheter into the proximity of the right upper lobe nodule.
Radial probe was used to attempt to confirm presence within the lesion.
A super dimension needle was then inserted through the bronchoscope and 0.75 milliliters of isocyanate Green were injected just below the pleura adjacent to the nodule for planned robotic surgical resection immediately following.
The bronchoscope was removed and the procedure was turned over to cardiothoracic surgery.
ESTIMATED BLOOD LOSS:   less than 5 cc 
COMPLICATIONS: None
IMPRESSION:  
- Successful navigational bronchoscopy with ICG marking of right upper lobe peripheral pulmonary nodule"""

# Define the list of entities to extract strictly based on Label_guide_UPDATED.csv
# Format: (Label, substring_to_find)
# The script will find these sequentially to handle duplicates correctly.
ENTITIES_TO_FIND = [
    ("OBS_LESION", "pulmonary nodule"),          # Pre-procedure
    ("OBS_LESION", "pulmonary nodule"),          # Post-procedure
    ("PROC_METHOD", "electromagnetic navigation"),
    ("PROC_METHOD", "flouroscopic"),
    ("PROC_METHOD", "EBUS"),
    ("MEDICATION", "isocyanate green"),          # Dye injection
    ("DEV_INSTRUMENT", "Bronchoscope"),
    ("PROC_METHOD", "Endobronchial Ultrasound"),
    ("PROC_METHOD", "fluoroscopic"),
    ("PROC_ACTION", "trans-bronchial needle aspiration"),
    ("PROC_METHOD", "computer assisted image guided navigation"),
    ("OBS_LESION", "pulmonary nodules"),
    ("MEAS_SIZE", "8. 5"),
    ("DEV_CATHETER", "ET tube"),                 # Matches "chest tube" type
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("DEV_CATHETER", "endotracheal tube"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "trachea"),                  # Corrected case from "Trachea"
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "Bronchial mucosa"),
    ("OBS_LESION", "endobronchial lesions"),
    ("DEV_CATHETER", "super-dimension navigational catheter"),
    ("DEV_INSTRUMENT", "T190 therapeutic bronchoscope"),
    ("ANAT_AIRWAY", "airway"),
    ("DEV_CATHETER", "180 degree edge catheter"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("OBS_LESION", "nodule"),
    ("DEV_INSTRUMENT", "Radial probe"),
    ("DEV_NEEDLE", "super dimension needle"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("MEAS_VOL", "0.75 milliliters"),
    ("MEDICATION", "isocyanate Green"),
    ("ANAT_PLEURA", "pleura"),
    ("OBS_LESION", "nodule"),
    ("PROC_METHOD", "robotic"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("MEAS_VOL", "less than 5 cc"),
    ("PROC_METHOD", "navigational"),
    ("MEDICATION", "ICG"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("OBS_LESION", "peripheral pulmonary nodule")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = OUTPUT_DIR / "stats.json"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Analyze & Extract (Calculate Indices)
# ==========================================
entities = []
spans_jsonl_entries = []
alignment_warnings = []
current_search_index = 0

for label, substring in ENTITIES_TO_FIND:
    # Find the substring starting from the last found position
    start = RAW_TEXT.find(substring, current_search_index)
    
    if start == -1:
        # If not found, log a warning and skip (should not happen if text matches)
        alignment_warnings.append(f"Could not find entity '{substring}' after index {current_search_index}")
        continue
        
    end = start + len(substring)
    
    # Create Entity dictionary for ner_dataset_all.jsonl
    entities.append({
        "start": start,
        "end": end,
        "label": label
    })
    
    # Create Span dictionary for spans.jsonl
    span_id = f"{label}_{start}"
    spans_jsonl_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": label,
        "text": substring,
        "start": start,
        "end": end
    })
    
    # Update search index to prevent overlapping or finding previous instances
    current_search_index = start + 1

# ==========================================
# 3. File Operations
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": entities
}

with open(NER_DATASET_FILE, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_FILE, 'a', encoding='utf-8') as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_FILE, 'a', encoding='utf-8') as f:
    for entry in spans_jsonl_entries:
        f.write(json.dumps(entry) + "\n")

# D. Update stats.json
if STATS_FILE.exists():
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        stats = json.load(f)
else:
    # Fallback default if file doesn't exist
    stats = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "alignment_warnings": 0,
        "alignment_errors": 0,
        "label_counts": {}
    }

# Increment Global Counters
stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(entities)
stats["total_spans_valid"] += len(entities)
if alignment_warnings:
    stats["alignment_warnings"] += len(alignment_warnings)

# Increment Label Counts
for entity in entities:
    lbl = entity["label"]
    if lbl in stats["label_counts"]:
        stats["label_counts"][lbl] += 1
    else:
        stats["label_counts"][lbl] = 1

# Save Stats
with open(STATS_FILE, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

# E. Log Alignment Warnings
if alignment_warnings:
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"--- {datetime.datetime.now()} | {NOTE_ID} ---\n")
        for warn in alignment_warnings:
            f.write(warn + "\n")

print(f"Successfully processed {NOTE_ID}.")
print(f"Added {len(entities)} entities.")
print(f"Updated stats and appended to {OUTPUT_DIR}")