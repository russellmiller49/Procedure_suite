import json
import os
import re
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_163"
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
# 2. Input Data (Raw Text)
# ==========================================
TEXT = """NOTE_ID:  note_163 SOURCE_FILE: note_163.txt PRE-PROCEDURE DIAGNISOS: Multiple pulmonary nodule 
POST- PROCEDURE DIAGNISOS: Multiple pulmonary nodule 
PROCEDURE PERFORMED:  
Flexible bronchoscopy with electromagnetic navigation under flouroscopic and EBUS guidance with transbronchial needle aspiration, transbronchial brush and transbronchial biopsy 
CPT 31654 Bronchoscope with Endobronchial Ultrasound guidance for peripheral lesion
CPT 31629 Flexible bronchoscopy with fluoroscopic trans-bronchial needle aspiration
CPT 31628 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with transbronchial lung biopsy(s), single lobe
CPT 31623 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with brushing or protected brushings
CPT +31627 Bronchoscopy with computer assisted image guided navigation
INDICATIONS FOR EXAMINATION:   multiple pulmonary nodules suspicious for malignancy            
SEDATION: General Anesthesia
FINDINGS: Following intravenous medications as per the record the patient was intubated with an 8. 0 ET tube by anesthesia.
The T190 video bronchoscope was then introduced through the endotracheal tube and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. The super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using the navigational map created preprocedurally we advanced the 190 degree edge catheter into the proximity of the right lower lobe nodule.
Radial probe was used to attempt to confirm presence within the lesion and minor adjustments were made in positioning until a concentric US view was obtained.
Biopsies were then performed with a variety of instruments to include peripheral needle, forceps, and triple needle brush under fluoroscopic visualization.
Rapid Onsite pathological evaluation was consistent with malignancy. Airway inspection was then performed to evaluate for any evidence of active bleeding and none was seen.
The bronchoscope was removed and the procedure completed. Specimens were sent for cytology/histology assessment.
ESTIMATED BLOOD LOSS:   less than 5 cc 
COMPLICATIONS: None
IMPRESSION:  
- Successful navigational bronchoscopy localization and biopsy a right lower lobe nodule
RECOMMENDATIONS
- Transfer to post-procedural unit
- Post-procedure CXR
- D/C home once criteria met
- Await pathology"""

# ==========================================
# 3. Entity Extraction Strategy
# ==========================================
# List of (Label, String) in sequential order of appearance to ensure correct offset mapping.
# We map text exactly as it appears in the raw string.

targets = [
    # Header / Pre-procedure
    ("OBS_LESION", "nodule"), # Multiple pulmonary nodule
    ("OBS_LESION", "nodule"), # POST- PROCEDURE ... nodule
    
    # Procedure Performed block
    ("PROC_ACTION", "Flexible bronchoscopy"),
    ("PROC_METHOD", "electromagnetic navigation"),
    ("PROC_METHOD", "flouroscopic"),
    ("PROC_METHOD", "EBUS guidance"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("PROC_ACTION", "transbronchial brush"),
    ("PROC_ACTION", "transbronchial biopsy"),
    
    # CPT lines (skipping redundant generic mentions unless highly specific, focusing on narrative)
    ("DEV_INSTRUMENT", "Bronchoscope"), # CPT 31654
    ("PROC_METHOD", "Endobronchial Ultrasound guidance"),
    ("PROC_ACTION", "Flexible bronchoscopy"), # CPT 31629
    ("PROC_METHOD", "fluoroscopic"),
    ("PROC_ACTION", "trans-bronchial needle aspiration"),
    
    # Indications
    ("OBS_LESION", "nodules"), # multiple pulmonary nodules
    ("OBS_LESION", "malignancy"), # suspicious for malignancy (Target abnormality context)
    
    # Findings - Intubation
    ("MEAS_SIZE", "8. 0"), # 8. 0 ET tube
    ("DEV_INSTRUMENT", "ET tube"),
    
    # Findings - Bronchoscopy start
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("DEV_INSTRUMENT", "endotracheal tube"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    
    # Anatomy check
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "Bronchial"),
    ("OBS_LESION", "lesions"), # endobronchial lesions
    
    # Navigation
    ("DEV_INSTRUMENT", "super-dimension navigational catheter"),
    ("DEV_INSTRUMENT", "T190 therapeutic bronchoscope"),
    ("ANAT_AIRWAY", "airway"),
    ("DEV_INSTRUMENT", "190 degree edge catheter"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("OBS_LESION", "nodule"),
    
    # Confirmation/Biopsy
    ("DEV_INSTRUMENT", "Radial probe"),
    ("OBS_LESION", "lesion"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_NEEDLE", "peripheral needle"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "triple needle brush"),
    ("PROC_METHOD", "fluoroscopic visualization"),
    
    # ROSE / Inspection
    ("OBS_ROSE", "malignancy"), # consistent with malignancy
    ("ANAT_AIRWAY", "Airway"),
    ("OBS_FINDING", "active bleeding"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    
    # Outcome / Impression
    ("MEAS_VOL", "5 cc"),
    ("OUTCOME_COMPLICATION", "None"),
    ("PROC_METHOD", "navigational"),
    ("PROC_ACTION", "bronchoscopy"),
    ("PROC_ACTION", "localization"),
    ("PROC_ACTION", "biopsy"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("OBS_LESION", "nodule"),
]

# ==========================================
# 4. processing Loop
# ==========================================

entities_json = []
spans_json = []
label_counts = {}

current_pos = 0

for label, substring in targets:
    # Find next occurrence starting from current_pos
    start = TEXT.find(substring, current_pos)
    
    if start == -1:
        # Critical Error: Text mismatch in manual mapping
        print(f"ERROR: Could not find '{substring}' after index {current_pos}")
        continue
        
    end = start + len(substring)
    
    # Add to Entities List (Dataset)
    entities_json.append([start, end, label])
    
    # Add to Spans List (Granular)
    span_id = f"{label}_{start}"
    spans_json.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": label,
        "text": substring,
        "start": start,
        "end": end
    })
    
    # Update Stats
    label_counts[label] = label_counts.get(label, 0) + 1
    
    # Log alignment check
    extracted = TEXT[start:end]
    if extracted != substring:
        with open(LOG_PATH, "a") as f:
            f.write(f"MISMATCH: {NOTE_ID} | Label: {label} | Expected: '{substring}' | Found: '{extracted}'\n")
            
    # Advance position to avoid finding the same instance
    current_pos = start + 1

# ==========================================
# 5. File Updates
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": TEXT,
    "entities": entities_json
}
with open(NER_DATASET_PATH, "a") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": TEXT
}
with open(NOTES_PATH, "a") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a") as f:
    for span in spans_json:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, "r") as f:
        try:
            stats = json.load(f)
        except json.JSONDecodeError:
            stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
else:
    stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

stats["total_notes"] += 1
stats["total_files"] += 1 # Assuming 1:1 note to file
stats["total_spans_raw"] += len(spans_json)
stats["total_spans_valid"] += len(spans_json)

for label, count in label_counts.items():
    stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count

with open(STATS_PATH, "w") as f:
    json.dump(stats, f, indent=4)

print(f"Successfully processed {NOTE_ID}. Extracted {len(spans_json)} entities.")