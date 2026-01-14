import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. CONFIGURATION & PATH SETUP
# ==========================================
NOTE_ID = "note_052"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. INPUT DATA
# ==========================================
RAW_TEXT = """NOTE_ID:  note_052 SOURCE_FILE: note_052.txt INDICATION FOR OPERATION:  [REDACTED]is a 82 year old-year-old female who presents with lymphadenopathy.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.
PREOPERATIVE DIAGNOSIS: R59.0 Localized enlarged lymph nodes
POSTOPERATIVE DIAGNOSIS:  R59.0 Localized enlarged lymph nodes
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31653 EBUS sampling 3 or more nodes  
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets 
76983 Ultrasound Elastography, Additional Target 2
 
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Flexible Therapeutic Bronchoscope
Linear EBUS 
 
ESTIMATED BLOOD LOSS:   None
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: . 
 
Initial Airway Inspection Findings:
 
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius , and Left Mainstem from mucus.
EBUS-Findings
Indications: Diagnostic
Technique:
All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 25-gauge Needle and 22-gauge Needle.
Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
11Rs lymph node
11L lymph node
 
Overall ROSE Diagnosis: Suggestive of benign-appearing lymphoid tissue
 
No immediate complications
 
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
Elastography provided a semi-quantitative classification (Type 1–3), which was used to guide biopsy site selection and sampling strategy.
Lymph Nodes Evaluated:
Site 1: The 11L lymph node was => 10 mm on CT and Hypermetabolic via PET-CT scan.
The lymph node was photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
Preliminary ROSE Cytology was reported as adequate and suggestive of anthracotic pigments. Final results are pending.
Site 2: The 4R (lower paratracheal) node was => 10 mm on CT and Hypermetabolic via PET-CT scan.
The lymph node was photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
Preliminary ROSE Cytology was reported as adequate and suggestive of anthracotic pigments. Final results are pending.
Site 3: The 11Rs lymph node was => 10 mm on CT and Hypermetabolic via PET-CT scan.
The lymph node was photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
Preliminary ROSE Cytology was reported as adequate and suggestive of anthracotic pigments. Final results are pending.
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
11L, 11Rs, 4R TBNA
 
IMPRESSION/PLAN: [REDACTED]is a 82 year old-year-old female who presents for bronchoscopy for lymphadenopathy.
- f/u final path
- f/u in clinic"""

# Entities to be extracted. List of tuples: (Label, Surface Text)
# Order matters to ensure we find the correct instance when text repeats.
ENTITIES_TO_EXTRACT = [
    ("PROC_ACTION", "Bronchoscopy"),
    ("PROC_ACTION", "Therapeutic aspiration"),
    ("PROC_METHOD", "EBUS"), # in 'EBUS sampling'
    ("DEV_INSTRUMENT", "Flexible Therapeutic Bronchoscope"),
    ("DEV_INSTRUMENT", "Linear EBUS"),
    ("PROC_ACTION", "therapeutic aspiration"), # in 'PROCEDURE IN DETAIL'
    ("ANAT_AIRWAY", "Right Mainstem"),
    ("ANAT_AIRWAY", "Bronchus Intermedius"),
    ("ANAT_AIRWAY", "Left Mainstem"),
    ("OBS_FINDING", "mucus"),
    ("PROC_METHOD", "EBUS"), # 'EBUS-Findings'
    ("MEAS_SIZE", "5 mm"),
    ("PROC_METHOD", "EBUS"), # 'Lymph node sizing was performed by EBUS'
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "25-gauge Needle"),
    ("DEV_NEEDLE", "22-gauge Needle"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "11Rs"),
    ("ANAT_LN_STATION", "11L"),
    ("OBS_ROSE", "benign-appearing lymphoid tissue"),
    ("PROC_METHOD", "Endobronchial ultrasound (EBUS)"), # elastography context
    ("ANAT_LN_STATION", "11L"), # Site 1
    ("MEAS_SIZE", "10 mm"),
    ("MEAS_COUNT", "4"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "transbronchial biopsies"),
    ("PROC_METHOD", "Endobronchial ultrasound (EBUS)"),
    ("PROC_ACTION", "TBNA"),
    ("OBS_ROSE", "anthracotic pigments"),
    ("ANAT_LN_STATION", "4R"), # Site 2
    ("MEAS_SIZE", "10 mm"),
    ("MEAS_COUNT", "4"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "transbronchial biopsies"),
    ("PROC_METHOD", "Endobronchial ultrasound (EBUS)"),
    ("PROC_ACTION", "TBNA"),
    ("OBS_ROSE", "anthracotic pigments"),
    ("ANAT_LN_STATION", "11Rs"), # Site 3
    ("MEAS_SIZE", "10 mm"),
    ("MEAS_COUNT", "4"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "transbronchial biopsies"),
    ("PROC_METHOD", "Endobronchial ultrasound (EBUS)"),
    ("PROC_ACTION", "TBNA"),
    ("OBS_ROSE", "anthracotic pigments"),
    ("ANAT_LN_STATION", "11L"), # Specimen list
    ("ANAT_LN_STATION", "11Rs"),
    ("ANAT_LN_STATION", "4R"),
    ("PROC_ACTION", "TBNA"),
    ("PROC_ACTION", "bronchoscopy"), # Impression
]

# ==========================================
# 3. PROCESSING & EXTRACTION
# ==========================================

extracted_spans = []
cursor = 0

for label, surface_text in ENTITIES_TO_EXTRACT:
    start_idx = RAW_TEXT.find(surface_text, cursor)
    
    if start_idx == -1:
        # Fallback: search from beginning if not found from cursor (though duplicates might map wrongly)
        # This safeguard ensures we don't crash, but ideally list is ordered.
        start_idx = RAW_TEXT.find(surface_text)
        
    if start_idx != -1:
        end_idx = start_idx + len(surface_text)
        span_obj = {
            "start": start_idx,
            "end": end_idx,
            "label": label,
            "text": surface_text
        }
        extracted_spans.append(span_obj)
        # Update cursor to avoid finding the same instance again if next item is identical
        cursor = start_idx + 1 
    else:
        # Log missing entities to alignment log
        with open(LOG_PATH, "a") as log:
            log.write(f"[{datetime.datetime.now()}] Warning: Could not find '{surface_text}' in {NOTE_ID}\n")

# ==========================================
# 4. FILE UPDATES
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_spans
}

with open(NER_DATASET_PATH, "a") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_PATH, "a") as f:
    f.write(json.dumps(notes_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a") as f:
    for span in extracted_spans:
        span_id = f"{span['label']}_{span['start']}"
        span_row = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        }
        f.write(json.dumps(span_row) + "\n")

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
stats["total_files"] += 1 # Assuming 1 note per file for this script
stats["total_spans_raw"] += len(extracted_spans)
stats["total_spans_valid"] += len(extracted_spans)

for span in extracted_spans:
    lbl = span['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w") as f:
    json.dump(stats, f, indent=4)

# ==========================================
# 5. VALIDATION
# ==========================================
with open(LOG_PATH, "a") as log:
    for span in extracted_spans:
        extracted = RAW_TEXT[span['start']:span['end']]
        if extracted != span['text']:
            log.write(f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{span['text']}', found '{extracted}' at {span['start']}:{span['end']}\n")

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")