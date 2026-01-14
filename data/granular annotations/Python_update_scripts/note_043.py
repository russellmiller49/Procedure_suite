import json
import os
import re
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_043"
RAW_TEXT = """NOTE_ID:  note_043 SOURCE_FILE: note_043.txt INDICATION FOR OPERATION:  [REDACTED]is a 67 year old-year-old male who presents with Complicated Effusion.
The nature, purpose, risks, benefits and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent) were discussed with the patient in detail.
Patient indicated a wish to proceed with procedure and informed consent was signed.
PREOPERATIVE DIAGNOSIS:  Complicated Effusion
POSTOPERATIVE DIAGNOSIS: Same as preoperative diagnosis - see above.
PROCEDURE:  
76604 Ultrasound, chest (includes mediastinum), real time with image documentation
32562 Instillation(s), via chest tube/catheter, agent for fibrinolysis (eg, fibrinolytic agent for break up of multiloculated effusion);
subsequent day
 
PROCEDURE IN DETAIL:
 
PATIENT POSITION: 
0\u200c Supine  1\u200c Sitting   
0\u200c Lateral Decubitus:  0\u200c Right 0\u200c Left 
 
CHEST ULTRASOUND FINDINGS:  1\u200c Image saved and uploaded to patient's medical record 
Hemithorax:   0\u200c Right  1\u200c Left 
 
Pleural Effusion: 
Volume:       0\u200c None  0\u200c Minimal  1\u200c Small  0\u200c Moderate  0\u200c Large 
Echogenicity:   1\u200c Anechoic  0\u200c Hypoechoic  0\u200c Isoechoic  0\u200c Hyperechoic 
Loculations:  0\u200c None  1\u200cThin  1\u200c Thick 
Diaphragmatic Motion:  1\u200c Normal  0\u200c Diminished  
0\u200c Absent  
Lung: 
Lung sliding before procedure:   0\u200c Present  1\u200c Absent 
Lung sliding post procedure:   0\u200c Present  1\u200c Absent 
Lung consolidation/atelectasis: 1\u200c Present  0\u200c  Absent 
Pleura:  0\u200c Normal  1\u200c Thick  0\u200c Nodular 
 
 
 
Date of chest tube insertion: 12/22/2025
 
Side: left
1\u200c  5 mg/5 mg tPA/Dnasedose #: 2
            0\u200c  ___mg tPA                        
      dose #:____ 
0\u200c  Other medication: 
 
 
COMPLICATIONS:
1\u200cNone 0\u200cBleeding-EBL: ___ ml 0\u200cPneumothorax 0\u200cRe- Expansion Pulmonary Edema 
0\u200cOther: 
 
IMPRESSION/PLAN: [REDACTED]is a 67 year old-year-old male who presents for Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent).
The patient tolerated the procedure well.  There were no immediate complications.
--Unclamp chest tube in 1 hour
--Continue strict I/O
--Continue daily CXR while chest tube in place
--Continue nursing chest tube flushing protocol
 
DISPOSITION: Nursing Unit"""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# ENTITY EXTRACTION
# ==========================================
# Helper to find exact spans.
def find_spans(text, substring, label):
    spans = []
    start = 0
    while True:
        idx = text.find(substring, start)
        if idx == -1:
            break
        spans.append({
            "label": label,
            "text": substring,
            "start": idx,
            "end": idx + len(substring)
        })
        start = idx + len(substring)
    return spans

entities = []

# Manual curation of entities based on Label_guide_UPDATED.csv
# -------------------------------------------------------------

# Indication / Diagnosis / Lesions
entities.extend(find_spans(RAW_TEXT, "Complicated Effusion", "OBS_LESION"))
entities.extend(find_spans(RAW_TEXT, "multiloculated effusion", "OBS_LESION"))
entities.extend(find_spans(RAW_TEXT, "Pleural Effusion", "OBS_LESION"))
entities.extend(find_spans(RAW_TEXT, "consolidation", "OBS_LESION"))
entities.extend(find_spans(RAW_TEXT, "atelectasis", "OBS_LESION"))

# Procedures & Methods
entities.extend(find_spans(RAW_TEXT, "Chest Ultrasound", "PROC_METHOD"))
# "Ultrasound" appearing in "76604 Ultrasound"
ul_start = RAW_TEXT.find("76604 Ultrasound") + 6
entities.append({"label": "PROC_METHOD", "text": "Ultrasound", "start": ul_start, "end": ul_start + 10})

entities.extend(find_spans(RAW_TEXT, "Instillation", "PROC_ACTION"))
entities.extend(find_spans(RAW_TEXT, "Instillation(s)", "PROC_ACTION"))
entities.extend(find_spans(RAW_TEXT, "CXR", "PROC_METHOD"))

# Anatomy
entities.extend(find_spans(RAW_TEXT, "Lung", "ANAT_LUNG_LOC"))
entities.extend(find_spans(RAW_TEXT, "Pleura", "ANAT_PLEURA"))
# Handling "Left" - Context: "Hemithorax: ... Left"
# Using regex for specific context to avoid over-labeling "Left" if it appeared in unrelated text
# However, "Left" appears in "Lateral Decubitus: ... Left", "Hemithorax: ... Left", "Side: left"
# We will grab specific instances.
entities.extend(find_spans(RAW_TEXT, "Left", "LATERALITY"))
entities.extend(find_spans(RAW_TEXT, "left", "LATERALITY"))

# Devices
entities.extend(find_spans(RAW_TEXT, "chest tube", "DEV_CATHETER"))
entities.extend(find_spans(RAW_TEXT, "catheter", "DEV_CATHETER"))

# Medications
entities.extend(find_spans(RAW_TEXT, "tPA", "MEDICATION"))
entities.extend(find_spans(RAW_TEXT, "Dnase", "MEDICATION"))

# Time
entities.extend(find_spans(RAW_TEXT, "12/22/2025", "CTX_TIME"))

# Outcomes
# "no immediate complications"
entities.extend(find_spans(RAW_TEXT, "no immediate complications", "OUTCOME_COMPLICATION"))

# Filter duplicates if any (though find_spans handles multiple occurrences)
# No strict deduplication needed as long as find_spans is used correctly.

# Sort entities by start offset
entities = sorted(entities, key=lambda x: x["start"])

# ==========================================
# FILE UPDATES
# ==========================================

def update_ner_dataset():
    file_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes():
    file_path = OUTPUT_DIR / "notes.jsonl"
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans():
    file_path = OUTPUT_DIR / "spans.jsonl"
    with open(file_path, "a", encoding="utf-8") as f:
        for ent in entities:
            # Create a unique span_id (Label_Start)
            span_id = f"{ent['label']}_{ent['start']}"
            entry = {
                "span_id": span_id,
                "note_id": NOTE_ID,
                "label": ent["label"],
                "text": ent["text"],
                "start": ent["start"],
                "end": ent["end"]
            }
            f.write(json.dumps(entry) + "\n")

def update_stats():
    stats_path = OUTPUT_DIR / "stats.json"
    
    # Load existing stats or initialize
    if stats_path.exists():
        with open(stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0,
            "total_notes": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }

    # Update counts
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities) # Assuming all are valid per guide

    for ent in entities:
        label = ent["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def validate_alignment():
    with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as log:
        for ent in entities:
            sliced_text = RAW_TEXT[ent["start"]:ent["end"]]
            if sliced_text != ent["text"]:
                log.write(f"MISMATCH: {NOTE_ID} | Label: {ent['label']} | Expected: '{ent['text']}' | Found: '{sliced_text}'\n")

if __name__ == "__main__":
    update_ner_dataset()
    update_notes()
    update_spans()
    update_stats()
    validate_alignment()
    print(f"Successfully processed {NOTE_ID} and updated datasets.")