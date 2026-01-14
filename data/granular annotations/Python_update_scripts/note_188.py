import json
import os
import re
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_188"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# We traverse up 3 levels from the script execution location to reach 'data' (assuming standard repo structure)
# If running standalone, ensure this path aligns with your directory structure.
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Extraction Targets
# ==========================================
RAW_TEXT = """NOTE_ID:  note_188 SOURCE_FILE: note_188.txt Procedure Name: EBUS bronchoscopy and peripheral biopsy
Indications: Pulmonary nodule requiring diagnosis/staging.
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level without endobronchial lesions visualized.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) was only met in station station 7. Sampling by transbronchial needle aspiration was performed using an Olympus EBUSTBNA 22 gauge needle.
All samples were sent for routine cytology. Onsite path evaluation revealed benign lymphocytes.
The bronchoscope was then removed and the PX190 ultrathin video bronchoscope was inserted into the airway and based on anatomical knowledge advanced into the left upper lobe to the area of known nodule within the Apical-posterior segment the lesion was identified visually.
Biopsies were then performed with micro forceps.  After adequate samples were obtained the bronchoscope was removed.
ROSE was consistent with malignancy within the lesion.  The bronchoscope was then removed and the P190 re-inserted into the airways.
We then observed for evidence of active bleeding and none was identified. The bronchoscope was removed and the procedure completed.
Complications: 	
-None 
Estimated Blood Loss:  less than 5 cc.
Recommendations:
- Transfer to post-op ward
- Await biopsy results 
- Discharge home once criteria met."""

# Order matters: Specific/Longer matches first to avoid partial overlap issues (e.g. "Pulmonary nodule" before "nodule")
TARGETS = [
    ("PROC_METHOD", "EBUS"), # In Title
    ("PROC_ACTION", "peripheral biopsy"),
    ("OBS_LESION", "Pulmonary nodule"),
    ("MEDICATION", "Propofol"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # Multiple occurrences
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"), # Case insensitive search logic handles "The trachea"
    ("ANAT_AIRWAY", "carina"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_LN_STATION", "station 7"),
    ("MEAS_SIZE", "5mm"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "22 gauge"),
    ("OBS_ROSE", "benign lymphocytes"),
    ("DEV_INSTRUMENT", "PX190 ultrathin video bronchoscope"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("OBS_LESION", "nodule"), # In "known nodule"
    ("ANAT_LUNG_LOC", "Apical-posterior segment"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_INSTRUMENT", "micro forceps"),
    ("OBS_ROSE", "malignancy"),
    ("DEV_INSTRUMENT", "P190"),
    ("OUTCOME_COMPLICATION", "None"),
    ("MEAS_VOL", "less than 5 cc"),
]

# ==========================================
# 3. Extraction Logic
# ==========================================
def extract_entities(text, targets):
    entities = []
    # Track occupied indices to prevent overlapping spans
    occupied_mask = [False] * len(text)
    
    for label, substr in targets:
        # Case insensitive search
        pattern = re.compile(re.escape(substr), re.IGNORECASE)
        for match in pattern.finditer(text):
            start, end = match.span()
            
            # Check for overlap
            if any(occupied_mask[start:end]):
                continue # Skip if overlaps with higher priority entity
                
            # Mark indices as occupied
            for i in range(start, end):
                occupied_mask[i] = True
            
            entities.append({
                "label": label,
                "text": text[start:end], # Use actual text from span (preserves case)
                "start": start,
                "end": end
            })
            
    # Sort by start position
    entities.sort(key=lambda x: x["start"])
    return entities

found_entities = extract_entities(RAW_TEXT, TARGETS)

# ==========================================
# 4. File Update Operations
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_record = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": found_entities
}
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_record) + "\n")

# B. Update notes.jsonl
note_record = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_record) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for ent in found_entities:
        span_record = {
            "span_id": f"{ent['label']}_{ent['start']}",
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        f.write(json.dumps(span_record) + "\n")

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
# Assuming 1 note = 1 file in this workflow context
stats["total_files"] += 1 
stats["total_spans_raw"] += len(found_entities)
stats["total_spans_valid"] += len(found_entities)

for ent in found_entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ==========================================
# 5. Validation & Logging
# ==========================================
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for ent in found_entities:
        extracted = RAW_TEXT[ent["start"]:ent["end"]]
        if extracted != ent["text"]:
            log_msg = f"[{datetime.datetime.now()}] MISMATCH in {NOTE_ID}: Span '{ent['text']}' vs Text '{extracted}' at {ent['start']}:{ent['end']}\n"
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID}. Extracted {len(found_entities)} entities.")