import json
import os
import datetime
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_220"
RAW_TEXT = """Procedure Name: Inspection bronchoscopy with bronchial lavage
Indications: Right lower lobe collapse and possible BP fistula
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record.
Laboratory studies and radiographs 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. The left sided airways were normal.
Significant pus was encountered within the right mainstem which was suctioned.
Once we’re able to better visualize the airways the 3 mm hole, noted on previous bronchoscopy, consistent with the BP fistula actively oozing purulent material was seen in the stump from the posterior segment of the right upper lobe.
A proximally 20 cc of gross pus was suctioned. The superior segment of the right lower lobe was open.
The basilar segments of the right lower lobe were completely obstructed due to bronchial kink without endobronchial disease which we could not pass.
Purulent material was expressed from this area as well consistent with a post-obstructive pneumonia.
We then returned to the posterior segment of the right upper lobe at the site of the BP fistula.
At this point the Veno-seal sealant delivery system catheter was advanced through the working channel of the bronchoscope and glue was then carefully applied to seal the fistula which appeared to be successful.
The bronchoscope was then removed and our portion of the procedure was completed.
Complications: None 
Estimated Blood Loss: 0

Post Procedure Diagnosis:
BF fistula with successful occlusion via sealant.
-BP fistula in the posterior segment of the right upper lobe stump."""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# ENTITY EXTRACTION LOGIC
# ==========================================
# List of entities to find. Order matters for finding the correct occurrence if duplicates exist.
# Format: (Text_Substring, Label, Occurrence_Index)
# Occurrence_Index: 0 for 1st match, 1 for 2nd match, etc.

entities_to_map = [
    ("bronchial lavage", "PROC_ACTION", 0),
    ("Right lower lobe", "ANAT_LUNG_LOC", 0),
    ("collapse", "OBS_FINDING", 0),
    ("BP fistula", "OBS_LESION", 0),
    ("upper airway", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 0),
    ("T190 video bronchoscope", "DEV_INSTRUMENT", 0),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 1),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 1),
    ("vocal cords", "ANAT_AIRWAY", 0),
    ("subglottic space", "ANAT_AIRWAY", 0),
    ("trachea", "ANAT_AIRWAY", 0),
    ("carina", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 2),
    ("left", "LATERALITY", 0),
    ("airways", "ANAT_AIRWAY", 3), # "left sided airways"
    ("pus", "OBS_FINDING", 0),
    ("right mainstem", "ANAT_AIRWAY", 0),
    ("suctioned", "PROC_ACTION", 0), # "Lavage" logic or action
    ("airways", "ANAT_AIRWAY", 4), # "visualize the airways"
    ("3 mm", "MEAS_SIZE", 0),
    ("hole", "OBS_LESION", 0),
    ("BP fistula", "OBS_LESION", 1),
    ("purulent material", "OBS_FINDING", 0),
    ("posterior segment of the right upper lobe", "ANAT_LUNG_LOC", 0),
    ("20 cc", "MEAS_VOL", 0),
    ("pus", "OBS_FINDING", 1), # "gross pus"
    ("superior segment of the right lower lobe", "ANAT_LUNG_LOC", 0),
    ("basilar segments of the right lower lobe", "ANAT_LUNG_LOC", 0),
    ("bronchial", "ANAT_AIRWAY", 1), # "bronchial kink"
    ("kink", "OBS_FINDING", 0),
    ("Purulent material", "OBS_FINDING", 1),
    ("post-obstructive pneumonia", "OBS_LESION", 0), # Infiltrate/Mass context
    ("posterior segment of the right upper lobe", "ANAT_LUNG_LOC", 1),
    ("BP fistula", "OBS_LESION", 2),
    ("Veno-seal sealant delivery system catheter", "DEV_INSTRUMENT", 0),
    ("bronchoscope", "DEV_INSTRUMENT", 1),
    ("bronchoscope", "DEV_INSTRUMENT", 2),
    ("BF fistula", "OBS_LESION", 0),
    ("BP fistula", "OBS_LESION", 3),
    ("posterior segment of the right upper lobe", "ANAT_LUNG_LOC", 2)
]

def find_spans(text, entity_list):
    spans = []
    # Track used spans to prevent overlaps if necessary, though simple NER usually allows nesting or strict handling
    # Here we assume simple sequential finding based on occurrence index
    
    for substr, label, occurrence in entity_list:
        # Find all start indices of the substring
        matches = [m.start() for m in re.finditer(re.escape(substr), text)]
        
        if len(matches) > occurrence:
            start_idx = matches[occurrence]
            end_idx = start_idx + len(substr)
            
            # Create span object
            span = {
                "start": start_idx,
                "end": end_idx,
                "label": label,
                "text": substr
            }
            spans.append(span)
        else:
            print(f"Warning: Could not find occurrence {occurrence} of '{substr}' in text.")
            
    return spans

final_spans = find_spans(RAW_TEXT, entities_to_map)

# ==========================================
# FILE UPDATE OPERATIONS
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": final_spans
}

with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Update spans.jsonl
span_entries = []
for span in final_spans:
    span_id = f"{span['label']}_{span['start']}"
    entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": span['label'],
        "text": span['text'],
        "start": span['start'],
        "end": span['end']
    }
    span_entries.append(entry)

with open(SPANS_PATH, 'a', encoding='utf-8') as f:
    for entry in span_entries:
        f.write(json.dumps(entry) + "\n")

# 4. Update stats.json
if STATS_PATH.exists():
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
stats["total_files"] += 1 # Assuming 1 note per file context here
stats["total_spans_raw"] += len(final_spans)
stats["total_spans_valid"] += len(final_spans)

for span in final_spans:
    lbl = span['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)

# 5. Validation & Logging
with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
    timestamp = datetime.datetime.now().isoformat()
    for span in final_spans:
        extracted = RAW_TEXT[span['start']:span['end']]
        if extracted != span['text']:
            log_msg = f"[{timestamp}] Mismatch in {NOTE_ID}: Expected '{span['text']}' but got '{extracted}' at {span['start']}:{span['end']}\n"
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")