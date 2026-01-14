from pathlib import Path
import json
import os
import datetime

# ------------------------------------------------------------------------------
# 1. Configuration & Path Setup
# ------------------------------------------------------------------------------
NOTE_ID = "note_182"
SCRIPT_DIR = Path(__file__).resolve()
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = SCRIPT_DIR.parents[2] / "ml_training" / "granular_ner"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ------------------------------------------------------------------------------
# 2. Raw Text Content
# ------------------------------------------------------------------------------
RAW_TEXT = """NOTE_ID:  note_182 SOURCE_FILE: note_182.txt PRE-PROCEDURE DIAGNISOS: RIGHT UPPER LOBE PULMONARY NODULE
POST- PROCEDURE DIAGNISOS: RIGHT UPPER LOBE PULMONARY NODULE
PROCEDURE PERFORMED:  
Flexible bronchoscopy with electromagnetic navigation under flouroscopic and EBUS guidance with transbronchial needle aspiration, Transbronchial biopsy and bronchioalveolar brush.
INDICATIONS FOR EXAMINATION:   Left upper lobe lung nodule            
MEDICATIONS:    GA
Pre-operative diagnosis: Right upper lobe nodule
Post-operative diagnosis: SAA
Anesthesia: General per Anesthesia

PROCEDURE: History and physical has been performed.
The risks and benefits of the procedure were discussed with the patient.
All questions were answered and informed consent was obtained. Patient identification and proposed procedure were verified by the physician, anesthesia team, nurse, and pulmonary team.
Time out was performed at 0819. The bronchoscope was introduced through the laryngeal mask airway and into the trachea.
The trachea is of normal caliber. The carina is sharp.
The tracheobronchial tree of bilateral lungs was examined to at least the first subsegmental level.
The right upper lobe was noted to have an anomalous inferior takeoff in addition to the anterior, apical, and posterior segments.
There were no endobronchial lesions and no excessive secretions.
 The Covidien superDimension probe was then advanced and registration was performed.
The right upper lobe nodule was accessed by the anomalous segment (see below), located using electromagnetic navigation and the site confirmed with radial ultrasound.
Transbronchial needle aspiration was performed under flouroscopic guidance and adequate tissue confirmed by ROSE.
Multiple insturments to include transbronchoscopic needles, forceps (tranbronchial lung biopsy) and brushes were utilized.
Five needle biopsies three forceps biopsies, and one needle brush biopsy were obtained in total.
Finally, inspection bronchoscopy was performed and hemostasis was confirmed. The procedure was accomplished without difficulty.
The patient tolerated the procedure well without immediate complications. EBL 5cc.
SPECIMEN SENT TO THE LABORATORY:
--5 needle biopsies of the right middle lobe
--1 brush biopsies of the  right middle lobe
--3 forceps biopsies

The patient tolerated the procedure well without complications.
RECOMMENDATIONS:
-D/C From CEC when discharge criteria are met
-Patient will be notified when biopsy results return"""

# ------------------------------------------------------------------------------
# 3. Entity Definitions (Label, Text, Occurrence Index)
# ------------------------------------------------------------------------------
# We define a list of (label, text_fragment) to locate in the text.
# The `find_all` logic will handle multiple occurrences if needed, 
# but for precision, we list them in order or specific unique fragments.

entities_to_find = [
    ("ANAT_LUNG_LOC", "RIGHT UPPER LOBE"),
    ("OBS_LESION", "PULMONARY NODULE"),
    ("ANAT_LUNG_LOC", "RIGHT UPPER LOBE"), # Second occurrence
    ("OBS_LESION", "PULMONARY NODULE"), # Second occurrence
    ("PROC_METHOD", "Flexible bronchoscopy"),
    ("PROC_METHOD", "electromagnetic navigation"),
    ("PROC_METHOD", "flouroscopic"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("PROC_ACTION", "Transbronchial biopsy"),
    ("PROC_ACTION", "bronchioalveolar brush"),
    ("ANAT_LUNG_LOC", "Left upper lobe"),
    ("OBS_LESION", "lung nodule"),
    ("ANAT_LUNG_LOC", "Right upper lobe"),
    ("OBS_LESION", "nodule"),
    ("CTX_TIME", "0819"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_AIRWAY", "trachea"), # First occurrence
    ("ANAT_AIRWAY", "trachea"), # Second occurrence
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_LUNG_LOC", "bilateral lungs"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("ANAT_LUNG_LOC", "anomalous inferior takeoff"), # Treating as specific location descriptor per context
    ("ANAT_LUNG_LOC", "anterior"),
    ("ANAT_LUNG_LOC", "apical"),
    ("ANAT_LUNG_LOC", "posterior segments"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "superDimension probe"),
    ("ANAT_LUNG_LOC", "right upper lobe"), # Next occurrence
    ("OBS_LESION", "nodule"), # Next occurrence
    ("ANAT_LUNG_LOC", "anomalous segment"),
    ("PROC_METHOD", "electromagnetic navigation"), # Next occurrence
    ("PROC_METHOD", "radial ultrasound"),
    ("PROC_ACTION", "Transbronchial needle aspiration"),
    ("PROC_METHOD", "flouroscopic"), # Next occurrence
    ("SPECIMEN", "tissue"),
    ("DEV_NEEDLE", "transbronchoscopic needles"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "tranbronchial lung biopsy"),
    ("DEV_INSTRUMENT", "brushes"),
    ("MEAS_COUNT", "Five"),
    ("PROC_ACTION", "needle biopsies"), # Action context
    ("MEAS_COUNT", "three"),
    ("PROC_ACTION", "forceps biopsies"), # Action context
    ("MEAS_COUNT", "one"),
    ("PROC_ACTION", "needle brush biopsy"),
    ("PROC_METHOD", "inspection bronchoscopy"),
    ("OBS_FINDING", "hemostasis"),
    ("OUTCOME_COMPLICATION", "without immediate complications"),
    ("MEAS_VOL", "5cc"),
    ("MEAS_COUNT", "5"),
    ("SPECIMEN", "needle biopsies"), # Specimen context
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("MEAS_COUNT", "1"),
    ("SPECIMEN", "brush biopsies"),
    ("ANAT_LUNG_LOC", "right middle lobe"), # Second occurrence in specimen
    ("MEAS_COUNT", "3"),
    ("SPECIMEN", "forceps biopsies"),
    ("OUTCOME_COMPLICATION", "without complications")
]

# ------------------------------------------------------------------------------
# 4. Processing Logic
# ------------------------------------------------------------------------------

def get_entities_with_indices(text, entity_list):
    """
    Finds entities in text. Handles duplicate strings by tracking current position.
    Assumes entity_list is ordered by appearance in text.
    """
    results = []
    current_pos = 0
    
    for label, substr in entity_list:
        start = text.find(substr, current_pos)
        if start == -1:
            # Fallback: search from beginning if not found sequentially (should not happen if ordered)
            start = text.find(substr)
            if start == -1:
                print(f"Warning: Could not find '{substr}' in text.")
                continue
        
        end = start + len(substr)
        results.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        # Advance current_pos to avoid finding the same instance unless intended
        # We assume strict ordering in definitions list for recurring terms
        current_pos = start + 1 
        
    return results

# Extract entities
extracted_entities = get_entities_with_indices(RAW_TEXT, entities_to_find)

# Prepare JSONL objects
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_entities
}

note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

span_entries = []
for ent in extracted_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    })

# ------------------------------------------------------------------------------
# 5. File Operations
# ------------------------------------------------------------------------------

# Append to ner_dataset_all.jsonl
with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ner_entry) + '\n')

# Append to notes.jsonl
with open(NOTES_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(note_entry) + '\n')

# Append to spans.jsonl
with open(SPANS_PATH, 'a', encoding='utf-8') as f:
    for span in span_entries:
        f.write(json.dumps(span) + '\n')

# Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, 'r', encoding='utf-8') as f:
        stats = json.load(f)
else:
    stats = {
        "total_files": 0, "successful_files": 0, "total_notes": 0,
        "total_spans_raw": 0, "total_spans_valid": 0,
        "alignment_warnings": 0, "alignment_errors": 0,
        "label_counts": {}, "hydration_status_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for ent in extracted_entities:
    lbl = ent['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

# Alignment Validation & Logging
with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
    for ent in extracted_entities:
        original_slice = RAW_TEXT[ent['start']:ent['end']]
        if original_slice != ent['text']:
            error_msg = f"Mismatch in {NOTE_ID}: Label {ent['label']} expected '{ent['text']}' but found '{original_slice}' at {ent['start']}:{ent['end']}\n"
            log_file.write(error_msg)
            # Note: We are not incrementing alignment_errors in stats here for simplicity in this script, 
            # but in a full pipeline, we would.

print(f"Successfully processed {NOTE_ID} and updated datasets.")