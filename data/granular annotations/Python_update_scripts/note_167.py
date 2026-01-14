import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_167"
SCRIPT_NAME = "update_ner_167.py"

# Raw text from note_167.txt
RAW_TEXT = """Indications: Mediastinal adenopathy in setting of known lung cancer
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record the Q190 video bronchoscope was introduced through the endotracheal tube and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Right sided bronchial mucosa and anatomy were normal;
without endobronchial lesions, and no secretions. Left proximal left mainstem was normal.
There was submucosal tumor infiltration in the distal 3 cm of the left mainstem circumferentially.
The left lower lobe was completely obstructed by endobronchial tumor.
The left upper lobe orifice was approximately 70% obstructed with tumor and the LC1 carina was infiltrated with tumor.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 7, 4L lymph nodes.
Sampling by transbronchial needle aspiration was performed with the Olympus EBUSTBNA 22 gauge needle beginning with the 7 Lymph node, followed by the 4L lymph node.
ROSE evaluation yielded benign lymphocytes in the station 7 and scant lymphocytes in station 4L.
All samples were sent for routine cytology. Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Decision was made to not proceed with mediastinoscopy as the left mainstem and upper lobe disease would preclude previously considered surgical resection and treatment would not be effected by the presence of N2 disease.
Complications: No immediate complications
Estimated Blood Loss: 5cc

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results
- Will present at tumor board for consideration of chemo-rads"""

# Ordered list of entities to extract. 
# The script will find these sequentially to handle duplicates (e.g. "Left", "tracheobronchial tree") correctly.
ENTITIES_TO_EXTRACT = [
    ("ANAT_LN_STATION", "Mediastinal"),
    ("OBS_LESION", "adenopathy"),
    ("OBS_LESION", "lung cancer"),
    ("MEDICATION", "General Anesthesia"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "endotracheal tube"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("LATERALITY", "Right"),
    ("ANAT_AIRWAY", "bronchial mucosa"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("LATERALITY", "Left"),
    ("LATERALITY", "left"),
    ("ANAT_AIRWAY", "mainstem"),
    ("OBS_LESION", "submucosal tumor infiltration"),
    ("MEAS_SIZE", "3 cm"),
    ("LATERALITY", "left"),
    ("ANAT_AIRWAY", "mainstem"),
    ("LATERALITY", "left"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely obstructed"),
    ("OBS_LESION", "endobronchial tumor"),
    ("LATERALITY", "left"),
    ("ANAT_LUNG_LOC", "upper lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "70% obstructed"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "LC1 carina"),
    ("OBS_LESION", "infiltrated with tumor"),
    ("DEV_INSTRUMENT", "video bronchoscope"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "station 7"),
    ("ANAT_LN_STATION", "4L"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_INSTRUMENT", "Olympus EBUSTBNA"),
    ("DEV_NEEDLE", "22 gauge"),
    ("ANAT_LN_STATION", "7 Lymph node"),
    ("ANAT_LN_STATION", "4L lymph node"),
    ("OBS_ROSE", "benign lymphocytes"),
    ("ANAT_LN_STATION", "station 7"),
    ("OBS_ROSE", "scant lymphocytes"),
    ("ANAT_LN_STATION", "station 4L"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "bronchoscopy"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("OBS_FINDING", "blood"),
    ("OBS_FINDING", "secretions"),
    ("OBS_FINDING", "active bleeding"),
    ("PROC_ACTION", "mediastinoscopy"),
    ("LATERALITY", "left"),
    ("ANAT_AIRWAY", "mainstem"),
    ("ANAT_LUNG_LOC", "upper lobe"),
    ("MEAS_VOL", "5cc"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "biopsies")
]

# ==========================================
# PATH SETUP
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING LOGIC
# ==========================================

def calculate_spans(text, entity_list):
    """
    Finds entities in text sequentially to ensure correct offsets for duplicates.
    Returns a list of dicts with 'label', 'text', 'start', 'end'.
    """
    spans = []
    cursor = 0
    
    for label, substr in entity_list:
        start = text.find(substr, cursor)
        if start == -1:
            # Fallback: Warning only, normally this shouldn't happen with valid copy-paste
            print(f"WARNING: Could not find '{substr}' starting from index {cursor}")
            continue
            
        end = start + len(substr)
        
        spans.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        
        # Move cursor to end of current match to handle sequential duplicates
        cursor = end
        
    return spans

def main():
    # 1. Calculate Spans
    extracted_spans = calculate_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_spans
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    new_span_lines = []
    label_counts_update = {}
    
    for span in extracted_spans:
        span_id = f"{span['label']}_{span['start']}"
        span_obj = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        }
        new_span_lines.append(json.dumps(span_obj))
        
        # Track counts for stats
        label_counts_update[span['label']] = label_counts_update.get(span['label'], 0) + 1

    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for line in new_span_lines:
            f.write(line + "\n")

    # 5. Update stats.json
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
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    for label, count in label_counts_update.items():
        if label in stats["label_counts"]:
            stats["label_counts"][label] += count
        else:
            stats["label_counts"][label] = count
            
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        for span in extracted_spans:
            text_slice = RAW_TEXT[span['start']:span['end']]
            if text_slice != span['text']:
                log_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{span['text']}', found '{text_slice}' at {span['start']}-{span['end']}\n"
                log_file.write(log_msg)

    print(f"Successfully processed {NOTE_ID}. Added {len(extracted_spans)} entities.")

if __name__ == "__main__":
    main()