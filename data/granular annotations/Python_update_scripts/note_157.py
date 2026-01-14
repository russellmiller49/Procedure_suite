import json
import os
import re
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_157"
RAW_TEXT = """Indications: Left lower lobe nodule
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the 7.5 ETT.
The airways were friable and significant blood was present from difficult intubation.  The trachea was of normal caliber.
The carina was sharp. On the right the patient had an anatomic variant with an accessory airway just distal to the superior segment of the right lower lobe.
The left sided airway anatomy was normal. No evidence of endobronchial disease was seen to at least the first sub-segments.
Following inspection the super-dimension navigational catheter was inserted through the therapeutic bronchoscope and advanced into the airway.
Using navigational map we were able to advance the 180 degree edge catheter into the anterior-medial segment on the left lower lobe and navigated to within 1cm of the lesion.
The navigational probe was then removed and peripheral radial probe was inserted into the catheter to confirm location.
Ultrasound visualization yielded a concentric view affirming the location.  Needle biopsies were performed with fluoroscopic guidance. ROSE was non-diagnostic.
The catheter was repositioned to sample other areas of the lesion and radial probe continued to show a concentric view of the tumor.
ROSE again was read as non-diagnostic. Tissue biopsies were then performed using forceps under fluoroscopic visualization along with brush and triple needle brush biopsies.
After samples were obtained the bronchoscope was removed and the diagnostic bronchoscope was re-inserted into the airway.
Subsequent inspection did not show evidence of active bleeding and the bronchoscope was removed from the airway.
Following completion of the procedure the patient was noted to lack audible airleak when the ETT balloon was deflated.
Given the difficult intubation, anesthesia decided to leave patient intubated and transfer to the ICU to monitor and extubate when deemed appropriate.
Complications: None
Estimated Blood Loss: Less than 10 cc.
Post Procedure Diagnosis:
- Flexible bronchoscopy with successful biopsy of left lower lobe pulmonary nodule
- Will transfer to the ICU and attempt extubation later today.
- Await final pathology"""

# Define the target entities (Label, Text Fragment)
# The script will scan the text to find the correct indices for these fragments.
TARGET_ENTITIES = [
    ("ANAT_LUNG_LOC", "Left lower lobe"),
    ("OBS_LESION", "nodule"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("MEAS_SIZE", "7.5"),
    ("ANAT_AIRWAY", "airways"),
    ("OBS_FINDING", "friable"),
    ("OBS_FINDING", "blood"), # "blood was present"
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("LATERALITY", "right"), # "On the right"
    ("ANAT_AIRWAY", "accessory airway"),
    ("ANAT_LUNG_LOC", "superior segment"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("LATERALITY", "left"), # "left sided"
    ("ANAT_AIRWAY", "airway"), # "left sided airway"
    ("OBS_LESION", "endobronchial disease"),
    ("DEV_INSTRUMENT", "super-dimension navigational catheter"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("ANAT_AIRWAY", "airway"), # "into the airway"
    ("PROC_METHOD", "navigational map"),
    ("DEV_INSTRUMENT", "180 degree edge catheter"),
    ("ANAT_LUNG_LOC", "anterior-medial segment"),
    ("ANAT_LUNG_LOC", "left lower lobe"), # 2nd occurrence
    ("MEAS_SIZE", "1cm"),
    ("OBS_LESION", "lesion"),
    ("DEV_INSTRUMENT", "navigational probe"),
    ("DEV_INSTRUMENT", "peripheral radial probe"),
    ("PROC_METHOD", "Ultrasound"),
    ("PROC_ACTION", "Needle biopsies"),
    ("PROC_METHOD", "fluoroscopic"),
    ("OBS_ROSE", "non-diagnostic"),
    ("DEV_INSTRUMENT", "radial probe"),
    ("OBS_LESION", "tumor"),
    ("OBS_ROSE", "non-diagnostic"), # 2nd occurrence
    ("PROC_ACTION", "Tissue biopsies"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_METHOD", "fluoroscopic"), # 2nd occurrence
    ("DEV_INSTRUMENT", "brush"),
    ("DEV_INSTRUMENT", "triple needle brush"),
    ("PROC_ACTION", "biopsies"), # "...brush biopsies"
    ("DEV_INSTRUMENT", "diagnostic bronchoscope"),
    ("ANAT_AIRWAY", "airway"), # "into the airway"
    ("OBS_FINDING", "active bleeding"),
    ("ANAT_AIRWAY", "airway"), # "removed from the airway"
    ("OBS_FINDING", "airleak"),
    ("DEV_INSTRUMENT", "balloon"),
    ("PROC_ACTION", "Flexible bronchoscopy"),
    ("PROC_ACTION", "biopsy"),
    ("ANAT_LUNG_LOC", "left lower lobe"), # 3rd occurrence
    ("OBS_LESION", "pulmonary nodule")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

def find_spans(text, targets):
    """
    Finds entity spans in the text.
    Handles multiple occurrences by keeping track of the search cursor.
    """
    spans = []
    # To handle duplicates correctly in order, we iterate through the text 
    # and match the sequence of targets as they appear.
    # However, since targets are listed in reading order above, we can assume sequential search.
    
    cursor = 0
    for label, substr in targets:
        # Find the next occurrence of the substring starting from cursor
        start = text.find(substr, cursor)
        
        if start == -1:
            # Fallback: simple error logging if not found (should not happen with correct extraction)
            print(f"WARNING: Could not find '{substr}' after index {cursor}")
            continue
            
        end = start + len(substr)
        span_id = f"{label}_{start}"
        
        spans.append({
            "span_id": span_id,
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        
        # Move cursor to end of found span to find next occurrence
        cursor = start + 1 
        
    return spans

def update_jsonl(file_path, new_record):
    """Appends a JSON record to a JSONL file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def update_stats(stats_path, new_spans):
    """Updates the stats.json file."""
    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    # Update general counts
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans) # Assuming all valid for this script

    # Update label counts
    for span in new_spans:
        label = span["label"]
        if label in stats["label_counts"]:
            stats["label_counts"][label] += 1
        else:
            stats["label_counts"][label] = 1

    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Extract Spans
    entities = find_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Prepare Data Structures
    
    # ner_dataset_all.jsonl record
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    
    # notes.jsonl record
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # spans.jsonl records
    # (entities list is already in the correct dict format, just need to add note_id)
    span_records = []
    for e in entities:
        record = e.copy()
        record["note_id"] = NOTE_ID
        span_records.append(record)

    # 3. Write to Files
    
    # Update ner_dataset_all.jsonl
    update_jsonl(OUTPUT_DIR / "ner_dataset_all.jsonl", ner_record)
    
    # Update notes.jsonl
    update_jsonl(OUTPUT_DIR / "notes.jsonl", note_record)
    
    # Update spans.jsonl
    for span in span_records:
        update_jsonl(OUTPUT_DIR / "spans.jsonl", span)
        
    # 4. Update Stats
    update_stats(OUTPUT_DIR / "stats.json", entities)
    
    # 5. Validation & Logging
    with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as log_file:
        for span in entities:
            extracted_text = RAW_TEXT[span['start']:span['end']]
            if extracted_text != span['text']:
                log_msg = f"MISMATCH {NOTE_ID}: Span {span['span_id']} expected '{span['text']}' but got '{extracted_text}'\n"
                log_file.write(log_msg)
                print(log_msg.strip())

    print(f"Successfully updated files for {NOTE_ID} with {len(entities)} entities.")

if __name__ == "__main__":
    main()