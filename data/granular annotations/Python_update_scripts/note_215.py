import json
import os
import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# CONFIGURATION & INPUT DATA
# -----------------------------------------------------------------------------
NOTE_ID = "note_215"
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# The raw text from the provided file
RAW_TEXT = """NOTE_ID:  note_215 SOURCE_FILE: note_215.txt Procedure Name: EBUS Staging Bronchoscopy.
(CPT 31653 convex probe endobronchial ultrasound sampling 3 or more hilar or mediastinal stations or structures).
Indications: staging of know LUL squamous cell carcinoma
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record.
Laboratory studies and radiographs 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal fold on the left was slightly edematous but the cords appeared normal.
The subglottic space was normal.  The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level.
There was significant distortion of the right sided airways with approximately 60% obstruction from external compression (seen on CT and known to be due to “pinching” from the spine and pulmonary artery).
Right sided bronchial mucosa was otherwise normal; there are no endobronchial lesions, and no secretions.
No evidence of endobronchial disease was seen to at least the first sub-segments.
On the left the proximal mainstem appeared normal. At the distal main stem tumor completely obstructing the right upper lobe and causing about 90% obstruction of the left lower lobe with some degree of submucosal infiltration seen at the LC1 carina.
We did not attempt to pass the obstruction. A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 11Rs, 4R, 7 and 8 (visible from the left mainstem posteriorly) lymph nodes.
Sampling by transbronchial needle aspiration was performed beginning with the 11Rs Lymph node, using an Olympus Visioshot EBUSTBNA 22 gauge needle.
Sampling continued in a systematic fashion from the N3N2 lymph nodes.
The station 8 had features highly concerning for malignancy (round hypoechoic, sharp boarders) and initial sampling was read as non-diagnostic by ROSE, to better sample the node mini-forceps were inserted through the puncture hole from TBNA and into the lymph node with ultrasound visualization and forceps biopsy was obtained.
This was performed 3 times.  There was direct tumor invasion of the N1 lymph node (11L) and it was not specifically sampled.
ROSE did not show clear evidence of malignancy of nodal sampling.
We then used the EBUS scope to visualize the 4cm mass adjacent to the left mainstem bronchi and were able to access it with the EBUS TBNA needle.
Preliminary ROSE was consistent with malignancy. Finally the EBUS bronchoscope was removed and the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: None
Estimated Blood Loss: 10cc 

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-procedural monitoring unit.
- Will await final pathology results"""

# Define target entities. 
# Helper tuple format: (Label, Text_to_Find, Occurrence_Index)
# Occurrence_Index: 0 for first match, 1 for second, etc.
ENTITY_DEFINITIONS = [
    ("PROC_METHOD", "EBUS", 0),
    ("PROC_ACTION", "Staging Bronchoscopy", 0),
    ("PROC_METHOD", "convex probe endobronchial ultrasound", 0),
    ("ANAT_LN_STATION", "hilar", 0),
    ("ANAT_LN_STATION", "mediastinal", 0),
    ("ANAT_LUNG_LOC", "LUL", 0),
    ("OBS_LESION", "squamous cell carcinoma", 0),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope", 0),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("ANAT_AIRWAY", "carina", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "60% obstruction", 0),
    ("OBS_FINDING", "secretions", 0), # First mention
    ("ANAT_AIRWAY", "proximal mainstem", 0),
    ("ANAT_AIRWAY", "distal main stem", 0),
    ("OBS_LESION", "tumor", 0), # "tumor completely obstructing"
    ("ANAT_LUNG_LOC", "right upper lobe", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "90% obstruction", 0),
    ("ANAT_LUNG_LOC", "left lower lobe", 0),
    ("ANAT_AIRWAY", "LC1 carina", 0),
    ("ANAT_LN_STATION", "hilar", 1), # systematic hilar...
    ("ANAT_LN_STATION", "mediastinal", 1), # ...and mediastinal
    ("MEAS_SIZE", "5mm", 0),
    ("ANAT_LN_STATION", "11Rs", 0),
    ("ANAT_LN_STATION", "4R", 0),
    ("ANAT_LN_STATION", "7", 0),
    ("ANAT_LN_STATION", "8", 0),
    ("PROC_ACTION", "transbronchial needle aspiration", 0),
    ("DEV_NEEDLE", "22 gauge", 0),
    ("ANAT_LN_STATION", "N3", 0),
    ("ANAT_LN_STATION", "N2", 0),
    ("OBS_FINDING", "round hypoechoic", 0), # Features concerning for malignancy
    ("OBS_ROSE", "non-diagnostic", 0),
    ("DEV_INSTRUMENT", "mini-forceps", 0),
    ("PROC_METHOD", "ultrasound", 1), # "with ultrasound visualization"
    ("PROC_ACTION", "forceps biopsy", 0),
    ("MEAS_COUNT", "3 times", 0),
    ("ANAT_LN_STATION", "N1", 0),
    ("ANAT_LN_STATION", "11L", 0),
    ("MEAS_SIZE", "4cm", 0),
    ("OBS_LESION", "mass", 0),
    ("OUTCOME_COMPLICATION", "None", 0), # In "Complications: None"
    ("MEAS_VOL", "10cc", 0) # Estimated Blood Loss
]

# -----------------------------------------------------------------------------
# DIRECTORY SETUP
# -----------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "ner_dataset": OUTPUT_DIR / "ner_dataset_all.jsonl",
    "notes": OUTPUT_DIR / "notes.jsonl",
    "spans": OUTPUT_DIR / "spans.jsonl",
    "stats": OUTPUT_DIR / "stats.json",
    "log": OUTPUT_DIR / "alignment_warnings.log"
}

# -----------------------------------------------------------------------------
# ENTITY EXTRACTION LOGIC
# -----------------------------------------------------------------------------
def locate_entities(text, entity_defs):
    """
    Locates entities in the text based on substring and occurrence index.
    Returns a list of dictionaries with 'start', 'end', 'label', 'text'.
    """
    found_entities = []
    
    for label, substr, occurrence in entity_defs:
        start_idx = -1
        # Loop to find the Nth occurrence
        for _ in range(occurrence + 1):
            start_idx = text.find(substr, start_idx + 1)
            if start_idx == -1:
                break
        
        if start_idx != -1:
            end_idx = start_idx + len(substr)
            found_entities.append({
                "label": label,
                "text": substr,
                "start": start_idx,
                "end": end_idx
            })
        else:
            print(f"Warning: Could not find '{substr}' (occurrence {occurrence}) in text.")
            
    return sorted(found_entities, key=lambda x: x['start'])

# -----------------------------------------------------------------------------
# FILE UPDATE FUNCTIONS
# -----------------------------------------------------------------------------
def append_jsonl(filepath, data):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(filepath, entities):
    # Load existing stats or initialize default
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}
        }
    
    # Update counters
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    # Update label counts
    for ent in entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def log_warning(filepath, message):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

# -----------------------------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------------------------
def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Calculate Offsets
    entities = locate_entities(RAW_TEXT, ENTITY_DEFINITIONS)
    
    # 2. Validation
    valid_entities = []
    for ent in entities:
        span_text = RAW_TEXT[ent['start']:ent['end']]
        if span_text != ent['text']:
            msg = f"Alignment Error in {NOTE_ID}: Expected '{ent['text']}', found '{span_text}' at {ent['start']}:{ent['end']}"
            print(msg)
            log_warning(FILES['log'], msg)
        else:
            valid_entities.append(ent)

    # 3. Update ner_dataset_all.jsonl
    # Format: {"id": "note_id", "text": "...", "entities": [{"start": 1, "end": 5, "label": "X"}, ...]}
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [{"start": e['start'], "end": e['end'], "label": e['label']} for e in valid_entities]
    }
    append_jsonl(FILES['ner_dataset'], ner_entry)

    # 4. Update notes.jsonl
    notes_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    append_jsonl(FILES['notes'], notes_entry)

    # 5. Update spans.jsonl
    # Format: {"span_id": "Label_Offset", "note_id": ..., "label": ..., "text": ..., "start": ..., "end": ...}
    for ent in valid_entities:
        span_id = f"{ent['label']}_{ent['start']}"
        span_entry = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        append_jsonl(FILES['spans'], span_entry)

    # 6. Update Stats
    update_stats(FILES['stats'], valid_entities)

    print(f"Successfully processed {NOTE_ID}.")
    print(f"Added {len(valid_entities)} entities to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()