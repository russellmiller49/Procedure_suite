from pathlib import Path
import json
import datetime
import os

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_261"
TIMESTAMP = datetime.datetime.now().isoformat()

# Cleaned text from the note (Source tags removed)
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Hemoptysis
POSTOPERATIVE DIAGNOSIS: 
1.	Endobronchial tumor 
PROCEDURE PERFORMED: Therapeutic bronchoscopy with tumor debulking 
INDICATIONS: Tumor obstruction of left lower lobe  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient  acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following anesthetic induction and endotracheal tube insertion , the flexible bronchoscope was advanced through the ETT into the airway.
On initial bronchoscopic inspection the trachea, and left lung appeared normal without evidence of endobronchial disease.
The proximal right mainstem and right upper lobe were normal.
In the distal right mainstem endobronchial tumor with active oozing was seen and extended into the bronchus intermedius causing near complete obstruction.
Forceps biopsy was performed of the visible endobronchial tumor and samples were placed in formalin.
Next APC was used to debulk and devascularize the endobronchial tumor utilizing a “burn and shave” method.
Tumor was seen within the right middle lobe causing complete obstruction and extending into the lower lobe subsegments.
APC was used in a similar fashion to paint and coagulate the remaining visible endobronchial tumor.
Re-establishment of patency was not complete due to the extent of distal tumor spread.
Once we were satisfied that no further intervention was required, and bleeding was controlled the bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
Recommendations:
-	Return patient to the ICU
-	Follow-up biopsy results
-	Continue to monitor for evidence of recurrent hemoptysis 
-	Initiate radiation therapy as soon as possible per oncology consultation."""

# Entities to extract based on Label_guide_UPDATED.csv
# Order must match the occurrence in the text to ensure correct indexing
ENTITIES_TO_FIND = [
    ("OBS_FINDING", "Hemoptysis"),
    ("OBS_LESION", "Endobronchial tumor"),
    ("PROC_ACTION", "Therapeutic bronchoscopy"),
    ("PROC_ACTION", "tumor debulking"),
    ("OBS_LESION", "Tumor"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_LUNG_LOC", "left lung"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("OBS_LESION", "endobronchial tumor"),
    ("ANAT_AIRWAY", "bronchus intermedius"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "near complete obstruction"),
    ("DEV_INSTRUMENT", "Forceps"),
    ("PROC_ACTION", "biopsy"),
    ("OBS_LESION", "endobronchial tumor"),
    ("PROC_METHOD", "APC"),
    ("PROC_ACTION", "debulk"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OBS_LESION", "Tumor"),
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "complete obstruction"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("PROC_METHOD", "APC"),
    ("PROC_ACTION", "coagulate"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OUTCOME_COMPLICATION", "bleeding was controlled"),
    ("OBS_FINDING", "hemoptysis")
]

# ==========================================
# SETUP PATHS
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
# HELPER FUNCTIONS
# ==========================================
def find_spans(text, entity_list):
    """
    Locates entities in the text sequentially to calculate start/end indices.
    """
    spans = []
    current_index = 0
    
    for label, substr in entity_list:
        start = text.find(substr, current_index)
        if start == -1:
            print(f"WARNING: Could not find '{substr}' after index {current_index}")
            continue
        
        end = start + len(substr)
        spans.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        current_index = start + 1 # Advance index to allow overlapping searches if needed, or end for strict sequential
    
    return spans

def update_stats(new_label_counts):
    """
    Updates the stats.json file with new counts.
    """
    if STATS_PATH.exists():
        with open(STATS_PATH, 'r') as f:
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
    stats["total_files"] += 1
    stats["total_spans_raw"] += len(new_label_counts)
    stats["total_spans_valid"] += len(new_label_counts) # Assuming all are valid per guide
    
    for label in new_label_counts:
        current_count = stats["label_counts"].get(label, 0)
        stats["label_counts"][label] = current_count + 1
        
    with open(STATS_PATH, 'w') as f:
        json.dump(stats, f, indent=4)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print(f"Processing {NOTE_ID}...")
    
    # 1. Extract Spans
    extracted_spans = find_spans(RAW_TEXT, ENTITIES_TO_FIND)
    
    # 2. Prepare Data Structures
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    span_entries = []
    label_list_for_stats = []
    
    for s in extracted_spans:
        span_id = f"{s['label']}_{s['start']}"
        span_entries.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": s["label"],
            "text": s["text"],
            "start": s["start"],
            "end": s["end"]
        })
        label_list_for_stats.append(s["label"])

    # 3. Write to Files
    
    # Update ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Update notes.jsonl
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Update spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for entry in span_entries:
            f.write(json.dumps(entry) + "\n")
            
    # Update stats.json
    update_stats(label_list_for_stats)
    
    # 4. Validation & Logging
    with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
        for span in span_entries:
            extracted_text = RAW_TEXT[span['start']:span['end']]
            if extracted_text != span['text']:
                error_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{span['text']}' but got '{extracted_text}' at {span['start']}:{span['end']}\n"
                log_file.write(error_msg)
                print(f"ERROR: {error_msg.strip()}")

    print(f"Successfully processed {NOTE_ID}. Data written to {OUTPUT_DIR}")