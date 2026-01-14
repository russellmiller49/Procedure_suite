import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_169"  # User can update this ID if needed

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
# RAW TEXT CONTENT
# ==========================================
RAW_TEXT = """PRE-PROCEDURE DIAGNISOS: LEFT UPPER LOBE PULMONARY NODULE
POST- PROCEDURE DIAGNISOS: RIGHT UPPER LOBE CAVITARY PULMONARY NODULE
PROCEDURE PERFORMED:   Flexible bronchoscopy with electromagnetic navigation under flouroscopic and EBUS guidance with transbronchial needle aspiration, Transbronchial biopsy and bronchioalveolar lavage.
MEDICATIONS:    GA
FINDINGS: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the laryngeal airway and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. The super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using navigational map we advanced the 180 degree edge catheter into the proximity of the lesion right upper lobe.
Radial probe was used to attempt to confirm presence within the lesion and minor adjustments were made in positioning until a concentric US view was obtained.
Biopsies were then performed with a variety of instruments to include peripheral needle, forceps, and brush under fluoroscopic visualization.
After which a mini-BAL was then performed through the super-D catheter.
We then removed the therapeutic bronchoscope with super-D catheter and reinserted the diagnostic scope at which point repeat airway inspection was then performed and once we were satisfied that no bleeding occurred, the bronchoscope was removed and the procedure completed.
Specimens were sent for both microbiological and cytology/histology assessment.

ESTIMATED BLOOD LOSS:   None 
COMPLICATIONS:                 None

IMPRESSION:  
- S/P bronchoscopy with biopsy and lavage.
- Successful navigational localization and biopsy 
RECOMMENDATIONS
- Transfer to post-procedural unit
- Post-procedure CXR
- D/C home once criteria met
- Await pathology"""

# ==========================================
# ENTITY DEFINITIONS (Sequential)
# ==========================================
# Based on Label_guide_UPDATED.csv
# Order matches appearance in text to ensure correct .find() behavior
ENTITIES_TO_EXTRACT = [
    ("ANAT_LUNG_LOC", "LEFT UPPER LOBE"),
    ("OBS_LESION", "PULMONARY NODULE"),
    ("ANAT_LUNG_LOC", "RIGHT UPPER LOBE"),
    ("OBS_LESION", "CAVITARY PULMONARY NODULE"),
    ("PROC_ACTION", "Flexible bronchoscopy"),
    ("PROC_METHOD", "electromagnetic navigation"),
    ("PROC_METHOD", "flouroscopic"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("PROC_ACTION", "Transbronchial biopsy"),
    ("PROC_ACTION", "bronchioalveolar lavage"),
    # FINDINGS
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("ANAT_AIRWAY", "laryngeal airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("OBS_LESION", "endobronchial lesions"),
    ("DEV_INSTRUMENT", "super-dimension navigational catheter"),
    ("DEV_INSTRUMENT", "T190 therapeutic bronchoscope"),
    ("ANAT_AIRWAY", "airway"),
    ("PROC_METHOD", "navigational map"),
    ("DEV_INSTRUMENT", "180 degree edge catheter"),
    ("OBS_LESION", "lesion"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("DEV_INSTRUMENT", "Radial probe"),
    ("OBS_LESION", "lesion"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_NEEDLE", "peripheral needle"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "brush"),
    ("PROC_METHOD", "fluoroscopic visualization"),
    ("PROC_ACTION", "mini-BAL"),
    ("DEV_INSTRUMENT", "super-D catheter"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("DEV_INSTRUMENT", "super-D catheter"),
    ("DEV_INSTRUMENT", "diagnostic scope"),
    # IMPRESSION
    ("PROC_ACTION", "bronchoscopy"),
    ("PROC_ACTION", "biopsy"),
    ("PROC_ACTION", "lavage"),
    ("PROC_METHOD", "navigational localization"),
    ("PROC_ACTION", "biopsy")
]

# ==========================================
# PROCESSING LOGIC
# ==========================================

def process_note():
    entities = []
    current_idx = 0
    
    # 1. Extract Spans
    for label, text_snippet in ENTITIES_TO_EXTRACT:
        start = RAW_TEXT.find(text_snippet, current_idx)
        if start == -1:
            print(f"WARNING: Could not find '{text_snippet}' after index {current_idx}")
            continue
            
        end = start + len(text_snippet)
        
        entities.append({
            "label": label,
            "text": text_snippet,
            "start": start,
            "end": end
        })
        
        # Advance index to avoid overlapping matches or finding previous instances
        current_idx = end

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": f"{e['label']}_{e['start']}",
                "label": e['label'],
                "start_offset": e['start'],
                "end_offset": e['end']
            }
            for e in entities
        ]
    }
    
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    new_spans = []
    for e in entities:
        span_entry = {
            "span_id": f"{e['label']}_{e['start']}",
            "note_id": NOTE_ID,
            "label": e['label'],
            "text": e['text'],
            "start": e['start'],
            "end": e['end']
        }
        new_spans.append(span_entry)

    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for span in new_spans:
            f.write(json.dumps(span) + "\n")

    # 5. Update stats.json
    update_stats(len(entities), entities)

    # 6. Validate
    validate_alignment(entities)

    print(f"Successfully processed {NOTE_ID} with {len(entities)} entities.")

def update_stats(new_span_count, entities):
    if not os.path.exists(STATS_PATH):
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    else:
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
            stats = json.load(f)

    stats["total_notes"] += 1
    stats["total_files"] += 1  # Assuming 1 note per file context
    stats["total_spans_raw"] += new_span_count
    stats["total_spans_valid"] += new_span_count

    for e in entities:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def validate_alignment(entities):
    with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
        for e in entities:
            extracted = RAW_TEXT[e['start']:e['end']]
            if extracted != e['text']:
                msg = f"MISMATCH {NOTE_ID}: Expected '{e['text']}' but found '{extracted}' at {e['start']}-{e['end']}\n"
                log_file.write(msg)
                print(msg.strip())

if __name__ == "__main__":
    process_note()