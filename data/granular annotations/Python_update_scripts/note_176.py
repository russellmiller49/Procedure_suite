import json
import os
import re
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_176"

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
# 2. Raw Text Content
# ==========================================
RAW_TEXT = """Indications: Mediastinal adenopathy
Procedure: EBUS bronchoscopy – single station CPT 31652
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
A large, station 4R, lymph node was identified and sampling by transbronchial needle aspiration was performed with the Olympus 19G Visioshot EBUS-TBNA needles with a total of 7 passes performed.
Initial rapid onsite evaluation showed scattered lymphocytes but no evidence of malignancy or granuloma.
We then placed the Olympus mini-forceps through the working channel of the EBUS scope and adnaved the forceps through a tract in the airway created by the EBUS needle.
We were able to visualize the forceps using the EBUS ultrasound within the lymph node.
We then closed and retracted the forceps. This was performed twice and touchpreps were made with the collected specimins which showed abundant non-caseating granulomas on rapid onsite pathological evaluation.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5cc
Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided needle and mini-forceps.
- The patient has remained stable and has been transferred in good condition to the post-procedural monitoring unit.
- Will await final pathology results"""

# ==========================================
# 3. Entity Definitions (Label, Text)
# ==========================================
# Note: This list allows multiple matches. We will align them sequentially.
entities_to_find = [
    ("OBS_LESION", "Mediastinal adenopathy"),
    ("PROC_METHOD", "EBUS bronchoscopy"),
    ("MEDICATION", "General Anesthesia"),
    ("MEDICATION", "topical anesthesia"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "mouth"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "Bronchial mucosa"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "video bronchoscope"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "mouth"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_LN_STATION", "station 4R"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "19G"),
    ("MEAS_COUNT", "7 passes"),
    ("OBS_ROSE", "lymphocytes"),
    ("OBS_ROSE", "malignancy"),
    ("OBS_ROSE", "granuloma"),
    ("DEV_INSTRUMENT", "Olympus mini-forceps"),
    ("DEV_INSTRUMENT", "EBUS scope"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_NEEDLE", "EBUS needle"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_METHOD", "EBUS ultrasound"),
    ("DEV_INSTRUMENT", "forceps"),
    ("OBS_ROSE", "non-caseating granulomas"),
    ("PROC_METHOD", "EBUS bronchoscopy"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("OBS_FINDING", "blood"),
    ("OBS_FINDING", "secretions"),
    ("OBS_FINDING", "active bleeding"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "5cc"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("DEV_INSTRUMENT", "mini-forceps"),
]

# ==========================================
# 4. Processing & alignment
# ==========================================

processed_entities = []
search_cursor = 0

for label, text in entities_to_find:
    # Find the next occurrence starting from search_cursor
    start = RAW_TEXT.find(text, search_cursor)
    
    if start == -1:
        # If not found forward, try resetting (in case list order is slightly off, 
        # though strict order is preferred for accuracy)
        start = RAW_TEXT.find(text) 
        if start == -1:
            print(f"WARNING: Could not find '{text}' in text. Skipping.")
            continue
            
    end = start + len(text)
    
    processed_entities.append({
        "label": label,
        "start": start,
        "end": end,
        "text": text
    })
    
    # Update cursor to avoid re-matching the same span for identical text later
    # We move cursor only if we found it after the previous cursor
    if start >= search_cursor:
        search_cursor = start + 1

# ==========================================
# 5. File Update Functions
# ==========================================

def append_jsonl(path, data):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(new_label_counts):
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
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
    stats["total_files"] += 1 # Assuming 1 note = 1 file in this context
    stats["total_spans_raw"] += len(processed_entities)
    stats["total_spans_valid"] += len(processed_entities)
    
    for label, count in new_label_counts.items():
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count
        
    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def log_warnings():
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        for ent in processed_entities:
            extracted = RAW_TEXT[ent['start']:ent['end']]
            if extracted != ent['text']:
                f.write(f"MISMATCH [{datetime.datetime.now()}]: ID {NOTE_ID} - Expected '{ent['text']}' but got '{extracted}' at {ent['start']}:{ent['end']}\n")

# ==========================================
# 6. Execution
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        [ent["start"], ent["end"], ent["label"]] for ent in processed_entities
    ]
}
append_jsonl(NER_DATASET_PATH, ner_entry)

# 2. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
append_jsonl(NOTES_PATH, notes_entry)

# 3. Update spans.jsonl
label_counts = {}
for ent in processed_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    }
    append_jsonl(SPANS_PATH, span_entry)
    
    # Count for stats
    label_counts[ent['label']] = label_counts.get(ent['label'], 0) + 1

# 4. Update stats.json
update_stats(label_counts)

# 5. Log alignment checks
log_warnings()

print(f"Successfully processed {NOTE_ID}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Extracted {len(processed_entities)} entities.")