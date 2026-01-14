import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_184"

# Define the full raw text of the note
RAW_TEXT = """Indications: Diagnosis and staging of presumed lung cancer
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 4R, 4L, Station 5 and 11L lymph nodes.
Sampling by transbronchial needle aspiration was performed with the Olympus EBUSTBNA 22 gauge needle beginning with the 4R Lymph node, followed by the 4L.
The 4R yielded benign lymphocytes on ROSE evaluation while the 4L was non-diagnostic.
Given that the station 11L would only stage the patient as N1 disease and the station 5 lymph nodes, which were highly suspicious for malignancy based on FDG avidity and ultrasound characteristics, after careful consideration we decided to attempt biopsy via the trans-vascular route thorough the pulmonary artery a total of 7 passes were performed, Five biopsies were performed with the Boston Scientific 25 gauge EBUS needle and an additional two with Olympus EBUSTBNA 22 gauge needle.
ROSE was consistent with poorly differentiated carcinoma. All samples were sent for routine cytology.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 10 cc.

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# Define the entities to extract (Label, Text Fragment)
# Note: The script will locate the exact index of the *first* occurrence unless specific handling is added.
# For repeating terms, we manually ensure we catch unique instances or context.
ENTITIES_TO_EXTRACT = [
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # Multiple occurrences handled in processing
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"), # Multiple occurrences
    ("ANAT_AIRWAY", "mouth"), # Multiple
    ("DEV_INSTRUMENT", "laryngeal mask airway"), # Multiple
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"), # lowercase in text "The trachea"
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "Bronchial"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"), # Multiple
    ("DEV_INSTRUMENT", "video bronchoscope"), # in "The video bronchoscope was then removed"
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "station 4R"),
    ("ANAT_LN_STATION", "4L"), # Context "4R, 4L"
    ("ANAT_LN_STATION", "Station 5"),
    ("ANAT_LN_STATION", "11L"),
    ("PROC_ACTION", "Sampling"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "Olympus EBUSTBNA 22 gauge needle"), # Multiple
    ("ANAT_LN_STATION", "4R"), # In "beginning with the 4R"
    ("OBS_ROSE", "benign lymphocytes"),
    ("OBS_ROSE", "non-diagnostic"),
    ("ANAT_LN_STATION", "station 11L"),
    ("ANAT_LN_STATION", "station 5"),
    ("OBS_LESION", "malignancy"),
    ("PROC_ACTION", "biopsy"),
    ("MEAS_COUNT", "7 passes"),
    ("MEAS_COUNT", "Five biopsies"),
    ("DEV_NEEDLE", "Boston Scientific 25 gauge EBUS needle"),
    ("MEAS_COUNT", "two"), # "additional two"
    ("OBS_ROSE", "poorly differentiated carcinoma"),
    ("PROC_METHOD", "EBUS"), # In "EBUS bronchoscopy"
    ("PROC_ACTION", "suctioning"),
    ("OBS_FINDING", "active bleeding"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "10 cc"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound")
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
# PROCESSING LOGIC
# ==========================================

def get_spans(text, entity_list):
    """
    Finds start/end indices for entities.
    Handles multiple occurrences by strictly searching sequentially if needed,
    but for this script, we assume distinct enough context or will find all valid matches.
    """
    spans = []
    # To avoid overlapping or duplicate indexing of the same instance, we track used ranges
    # Simple approach: Find all occurrences of the substring
    
    unique_spans = []
    
    for label, substr in entity_list:
        start = 0
        while True:
            idx = text.find(substr, start)
            if idx == -1:
                break
            
            end = idx + len(substr)
            
            # Check if this span is already recorded (simple de-duplication)
            is_duplicate = False
            for existing in unique_spans:
                if existing['start'] == idx and existing['end'] == end and existing['label'] == label:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                span_obj = {
                    "start": idx,
                    "end": end,
                    "label": label,
                    "text": substr
                }
                unique_spans.append(span_obj)
            
            start = end # Move past this occurrence
            
    # Sort by start index
    unique_spans.sort(key=lambda x: x['start'])
    return unique_spans

def update_stats(stats_path, new_label_counts):
    if stats_path.exists():
        with open(stats_path, 'r') as f:
            stats = json.load(f)
    else:
        # Initialize if missing
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats['total_files'] += 1
    stats['successful_files'] += 1
    stats['total_notes'] += 1
    
    total_new_spans = sum(new_label_counts.values())
    stats['total_spans_raw'] += total_new_spans
    stats['total_spans_valid'] += total_new_spans
    
    for label, count in new_label_counts.items():
        if label in stats['label_counts']:
            stats['label_counts'][label] += count
        else:
            stats['label_counts'][label] = count
            
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Extract Spans
    extracted_spans = get_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Data Structures
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_spans
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    span_entries = []
    label_counts = {}
    
    for span in extracted_spans:
        # Create span entry
        span_id = f"{span['label']}_{span['start']}"
        span_entry = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        }
        span_entries.append(span_entry)
        
        # Count labels
        label_counts[span['label']] = label_counts.get(span['label'], 0) + 1

    # 3. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + '\n')
        
    # Append to notes.jsonl
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + '\n')
        
    # Append to spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for entry in span_entries:
            f.write(json.dumps(entry) + '\n')

    # 4. Update Stats
    update_stats(STATS_PATH, label_counts)
    
    # 5. Validation Log
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        for span in extracted_spans:
            original_slice = RAW_TEXT[span['start']:span['end']]
            if original_slice != span['text']:
                log_msg = f"MISMATCH: Note {NOTE_ID} | Label {span['label']} | Expected '{span['text']}' vs Found '{original_slice}'"
                print(log_msg)
                f.write(log_msg + "\n")
                
    print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_spans)} entities.")

if __name__ == "__main__":
    main()