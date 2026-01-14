import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. CONFIGURATION & INPUT DATA
# ==========================================
NOTE_ID = "note_134"

# Raw text cleaned from the provided source (removing tags)
RAW_TEXT = """Procedure Name: Bronchoscopy with Endobronchial Ultrasound
Indications: Right upper lobe mass, diagnostic
Medications: General anesthesia;
2% lidocaine, tracheobronchial tree 10 mL

Pre-Procedure

Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered, and informed consent was documented per institutional protocol.
A history and physical examination were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.

Following intravenous medications per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree, the Q180 slim video bronchoscope was introduced through the mouth via laryngeal mask airway and advanced into the tracheobronchial tree.
The UC180F convex probe EBUS bronchoscope was subsequently introduced via the same route. The patient tolerated the procedure well.
Procedure Description

The laryngeal mask airway was in normal position. The vocal cords moved normally with respiration.
The subglottic space was normal. The trachea was of normal caliber, and the carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa and anatomy were normal, with no endobronchial lesions or secretions except as outlined below.
Evidence of prior surgery was noted in the left mainstem bronchus. The bronchial stump appeared well healed.
The flexible bronchoscope was withdrawn and replaced with the EBUS bronchoscope.
A systematic hilar and mediastinal lymph node survey was performed.
Lymph Nodes and Mass Evaluation

Lymph node sizing was performed using endobronchial ultrasound.
Sampling was performed using an Olympus 22-gauge EBUS-TBNA needle and sent for routine cytology.
Station 4R (lower paratracheal): Measured 1.9 mm by EBUS and 2.4 mm by CT. PET negative.
Ultrasound characteristics included hypoechoic, heterogeneous, irregular shape with sharp margins.
This node was not biopsied due to benign ultrasound characteristics and size criteria.
Station 7 (subcarinal): Measured 5.4 mm by EBUS and 4.8 mm by CT. PET negative.
Ultrasound characteristics included hypoechoic, heterogeneous, irregular shape with sharp margins.
This node was biopsied using a 22-gauge needle with five passes. ROSE preliminary analysis indicated adequate tissue.
Station 10R (hilar): Measured 3.4 mm by EBUS and 0.1 mm by CT. PET negative.
Ultrasound characteristics included hypoechoic, heterogeneous, irregular shape with sharp margins.
This node was not biopsied due to benign ultrasound characteristics and size criteria.
Station 11Rs: Measured 7.3 mm by EBUS and 5.4 mm by CT. PET negative.
Ultrasound characteristics included hypoechoic, heterogeneous, irregular shape with sharp margins.
This node was biopsied using a 22-gauge needle with five passes. ROSE preliminary analysis indicated adequate tissue.
Right upper lobe mass: Measured 19 mm by EBUS and 22 mm by CT. PET positive.
Ultrasound characteristics included hypoechoic, heterogeneous, irregular shape with sharp margins.
This lesion was biopsied using a 22-gauge needle with eight passes. ROSE preliminary analysis indicated malignancy.
All specimens were sent to cytopathology for review.

Additional Sampling

Fluoroscopically guided transbronchial brushings were obtained from the right upper lobe and sent for routine cytology.
Two samples were obtained.

Transbronchial biopsies were performed in the right upper lobe apical segment (B1) using forceps under fluoroscopic guidance.
Five biopsy passes were performed, yielding five biopsy specimens, which were sent for histopathologic examination.

Complications

No immediate complications.
Estimated Blood Loss

Less than 5 mL.

Impression

Technically successful flexible bronchoscopy with endobronchial ultrasound-guided lymph node and mass sampling

Evidence of prior left mainstem bronchial surgery with well-healed stump

Transbronchial lung biopsies performed

Lymph node sizing and sampling performed

Fluoroscopically guided transbronchial brushings obtained

Post-Procedure Diagnosis

As above.
The patient remained stable and was transferred in good condition to the post-bronchoscopy recovery area, where he will be observed until discharge criteria are met.
Preliminary findings were discussed with the patient. Follow-up with the requesting service for final pathology results was recommended.
Plan:

Await cytology and histopathology results."""

# Ordered list of entities to extract based on the Rulebook (Label_guide_UPDATED.csv)
# Format: (Label, Text Segment)
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "Bronchoscopy"),
    ("PROC_METHOD", "Endobronchial Ultrasound"),
    ("ANAT_LUNG_LOC", "Right upper lobe"),
    ("OBS_LESION", "mass"),
    ("MEDICATION", "lidocaine"),
    ("DEV_INSTRUMENT", "Q180 slim video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "left mainstem bronchus"),
    ("ANAT_AIRWAY", "bronchial stump"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "EBUS bronchoscope"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("DEV_NEEDLE", "22-gauge"),
    ("ANAT_LN_STATION", "Station 4R"),
    ("MEAS_SIZE", "1.9 mm"),
    ("MEAS_SIZE", "2.4 mm"),
    ("ANAT_LN_STATION", "Station 7"),
    ("MEAS_SIZE", "5.4 mm"),
    ("MEAS_SIZE", "4.8 mm"),
    ("DEV_NEEDLE", "22-gauge"),
    ("MEAS_COUNT", "five passes"),
    ("OBS_ROSE", "adequate tissue"),
    ("ANAT_LN_STATION", "Station 10R"),
    ("MEAS_SIZE", "3.4 mm"),
    ("MEAS_SIZE", "0.1 mm"),
    ("ANAT_LN_STATION", "Station 11Rs"),
    ("MEAS_SIZE", "7.3 mm"),
    ("MEAS_SIZE", "5.4 mm"),
    ("DEV_NEEDLE", "22-gauge"),
    ("MEAS_COUNT", "five passes"),
    ("OBS_ROSE", "adequate tissue"),
    ("ANAT_LUNG_LOC", "Right upper lobe"),
    ("OBS_LESION", "mass"),
    ("MEAS_SIZE", "19 mm"),
    ("MEAS_SIZE", "22 mm"),
    ("DEV_NEEDLE", "22-gauge"),
    ("MEAS_COUNT", "eight passes"),
    ("OBS_ROSE", "malignancy"),
    ("PROC_METHOD", "Fluoroscopically"),
    ("PROC_ACTION", "transbronchial brushings"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("PROC_ACTION", "Transbronchial biopsies"),
    ("ANAT_LUNG_LOC", "right upper lobe apical segment (B1)"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_METHOD", "fluoroscopic guidance"),
    ("MEAS_COUNT", "Five biopsy passes"),
    ("MEAS_VOL", "5 mL"),
    ("PROC_METHOD", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("ANAT_AIRWAY", "left mainstem bronchial"),
    ("PROC_ACTION", "Transbronchial lung biopsies"),
    ("PROC_METHOD", "Fluoroscopically"),
    ("PROC_ACTION", "transbronchial brushings")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_FILE_PATH = OUTPUT_DIR / "stats.json"
LOG_FILE_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. ENTITY EXTRACTION & ALIGNMENT
# ==========================================

extracted_entities = []
cursor = 0

with open(LOG_FILE_PATH, "a") as log_file:
    for label, substr in ENTITIES_TO_EXTRACT:
        start_idx = RAW_TEXT.find(substr, cursor)
        
        if start_idx == -1:
            log_msg = f"WARNING: Could not find '{substr}' after index {cursor} in {NOTE_ID}.\n"
            print(log_msg.strip())
            log_file.write(log_msg)
            continue
            
        end_idx = start_idx + len(substr)
        
        # Validation
        extracted_text = RAW_TEXT[start_idx:end_idx]
        if extracted_text != substr:
            log_msg = f"ERROR: Mismatch at {start_idx}:{end_idx}. Expected '{substr}', got '{extracted_text}'.\n"
            log_file.write(log_msg)
            continue

        extracted_entities.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": extracted_text,
            "start": start_idx,
            "end": end_idx
        })
        
        # Update cursor to avoid finding the same instance twice
        cursor = start_idx + 1

# ==========================================
# 3. FILE UPDATES
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_entities
}
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
with open(NOTES_FILE_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_FILE_PATH, "a", encoding="utf-8") as f:
    for span in extracted_entities:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if os.path.exists(STATS_FILE_PATH):
    with open(STATS_FILE_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "label_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for span in extracted_entities:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_entities)} entities.")