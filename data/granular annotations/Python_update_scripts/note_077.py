import json
import os
import datetime
import re
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_077"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Definitions
# ==========================================

# Raw text reconstructed from the provided file content, stripping [source] tags
RAW_TEXT = """NOTE_ID:  note_077 SOURCE_FILE: note_077.txt INDICATION FOR OPERATION:  [REDACTED]is a 62 year old-year-old female who presents with lymphadenopathy.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
PREOPERATIVE DIAGNOSIS: R59.0 Localized enlarged lymph nodes
POSTOPERATIVE DIAGNOSIS:  R59.0 Localized enlarged lymph nodes
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)    
31653 EBUS sampling 3 or more nodes  
ANESTHESIA: 
General Anesthesia
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Linear EBUS 
Disposable Bronchoscope
ESTIMATED BLOOD LOSS:   Minimum
COMPLICATIONS:    None
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: . 
Initial Airway Inspection Findings:
Normal appearing airway anatomy and mucosa bilaterally to the segmental level.
Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius , Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus.
EBUS-Findings
Indications: Diagnostic
Technique:
All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle.
Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
4L (lower paratracheal) node
7 (subcarinal) node
11Rs lymph node
11Ri lymph node
11L lymph node
Overall ROSE Diagnosis: Granulomas
No immediate complications
Lymph Nodes Evaluated:
Site 1: The 11L lymph node was => 10 mm on CT and Hypermetabolic via PET-CT scan.
The lymph node was not photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Preliminary ROSE Cytology was reported as not adequate and suggestive of Specimen was inadequate for ROSE analysis .
Final results are pending.
Site 2: The 7 (subcarinal) node was => 10 mm on CT and Hypermetabolic via PET-CT scan.
The lymph node was not photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Preliminary ROSE Cytology was reported as adequate and suggestive of Granulomas. Final results are pending.
Site 3: The 11Ri lymph node was => 10 mm on CT and Hypermetabolic via PET-CT scan.
The lymph node was not photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Bronchial alveolar lavage was performed at Lateral Segment of RML (RB4) and Medial Segment of RML (RB5).
Instilled 40 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius , Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus, blood, and blood clots.
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
•	EBUS-TBNA 11L, 7, 11Ri
•	Right middle lobe Bronchoalveolar lavage
IMPRESSION/PLAN: [REDACTED]is a 62 year old-year-old female who presents for bronchoscopy for lymphadenopathy.
-Follow up bronchoscopic lab work"""

# Defined entities to extract
# Format: (Label, Text String)
# Duplicate strings in text will be handled by finding all unique occurrences
TARGET_ENTITIES = [
    ("OBS_LESION", "lymphadenopathy"),
    ("PROC_ACTION", "Bronchoscopy"),
    ("PROC_ACTION", "Therapeutic aspiration"),
    ("PROC_ACTION", "bronchoscope/lavage"),
    ("PROC_ACTION", "BAL"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "sampling"),
    ("PROC_METHOD", "Linear EBUS"),
    ("DEV_INSTRUMENT", "Disposable Bronchoscope"),
    ("PROC_ACTION", "therapeutic aspiration"),
    ("ANAT_AIRWAY", "Trachea (Middle 1/3)"),
    ("ANAT_AIRWAY", "Trachea (Distal 1/3)"),
    ("ANAT_AIRWAY", "Right Mainstem"),
    ("ANAT_AIRWAY", "Bronchus Intermedius"),
    ("ANAT_AIRWAY", "Left Mainstem"),
    ("ANAT_AIRWAY", "Carina"),
    ("ANAT_AIRWAY", "RUL Carina"),
    ("ANAT_AIRWAY", "RC1"),
    ("ANAT_AIRWAY", "RML Carina"),
    ("ANAT_AIRWAY", "RC2"),
    ("ANAT_AIRWAY", "LUL Lingula Carina"),
    ("ANAT_AIRWAY", "Lc1"),
    ("ANAT_AIRWAY", "Left Carina"),
    ("ANAT_AIRWAY", "LC2"),
    ("OBS_FINDING", "mucus"),
    ("MEAS_SIZE", "5 mm"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "22-gauge Needle"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "lower paratracheal"),
    ("ANAT_LN_STATION", "4L"),
    ("ANAT_LN_STATION", "7"),
    ("ANAT_LN_STATION", "subcarinal"),
    ("ANAT_LN_STATION", "11Rs"),
    ("ANAT_LN_STATION", "11Ri"),
    ("ANAT_LN_STATION", "11L"),
    ("OBS_ROSE", "Granulomas"),
    ("MEAS_SIZE", "10 mm"),
    ("MEAS_COUNT", "4"),
    ("PROC_ACTION", "endobronchial ultrasound guided transbronchial biopsies"),
    ("PROC_ACTION", "Bronchial alveolar lavage"),
    ("ANAT_LUNG_LOC", "Lateral Segment of RML"),
    ("ANAT_LUNG_LOC", "RB4"),
    ("ANAT_LUNG_LOC", "Medial Segment of RML"),
    ("ANAT_LUNG_LOC", "RB5"),
    ("MEAS_VOL", "40 cc"),
    ("MEAS_VOL", "15 cc"),
    ("SPECIMEN", "Cell Count"),
    ("SPECIMEN", "Microbiology"),
    ("SPECIMEN", "Cytology"),
    ("OBS_FINDING", "blood"),
    ("OBS_FINDING", "blood clots"),
    ("ANAT_LUNG_LOC", "Right middle lobe"),
    ("PROC_ACTION", "Bronchoalveolar lavage"),
    ("PROC_ACTION", "TBNA"),
    ("ANAT_LN_STATION", "11L"), # Checking duplicates in specimen section
    ("ANAT_LN_STATION", "7"),
    ("ANAT_LN_STATION", "11Ri")
]

# ==========================================
# 3. Processing Logic
# ==========================================

def get_entities(text, entity_list):
    entities = []
    # Sort by length descending to capture longest matches first if there is overlap logic needed,
    # but here we scan linearly.
    
    # We maintain a list of found matches to handle identical strings in different contexts
    # NOTE: This basic implementation finds ALL occurrences of the string.
    # In a production environment, context awareness (surrounding words) would be added.
    
    found_spans = []

    for label, target in entity_list:
        # Using regex to find all occurrences
        # re.escape matches special characters in the medical text (like parentheses)
        matches = [m for m in re.finditer(re.escape(target), text)]
        
        for match in matches:
            start = match.start()
            end = match.end()
            span_text = text[start:end]
            
            # Simple deduplication: Check if this specific start/end is already logged
            if (start, end) not in found_spans:
                entities.append({
                    "label": label,
                    "text": span_text,
                    "start": start,
                    "end": end
                })
                found_spans.append((start, end))

    # Sort entities by start position
    entities.sort(key=lambda x: x["start"])
    return entities

extracted_entities = get_entities(RAW_TEXT, TARGET_ENTITIES)

# ==========================================
# 4. JSONL & File Operations
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_data = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_entities
}

ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
with open(ner_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_data) + "\n")

# B. Update notes.jsonl
notes_data = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

notes_file = OUTPUT_DIR / "notes.jsonl"
with open(notes_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_data) + "\n")

# C. Update spans.jsonl
spans_file = OUTPUT_DIR / "spans.jsonl"
with open(spans_file, "a", encoding="utf-8") as f:
    for ent in extracted_entities:
        span_entry = {
            "span_id": f"{ent['label']}_{ent['start']}",
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        f.write(json.dumps(span_entry) + "\n")

# D. Update stats.json
stats_file = OUTPUT_DIR / "stats.json"
if stats_file.exists():
    with open(stats_file, "r", encoding="utf-8") as f:
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
stats["total_files"] += 1 # Assuming 1 note = 1 file context
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for ent in extracted_entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_file, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ==========================================
# 5. Validation & Logging
# ==========================================
with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as log:
    for ent in extracted_entities:
        original_slice = RAW_TEXT[ent["start"]:ent["end"]]
        if original_slice != ent["text"]:
            log.write(f"MISMATCH in {NOTE_ID}: Expected '{ent['text']}', found '{original_slice}' at {ent['start']}-{ent['end']}\n")

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")