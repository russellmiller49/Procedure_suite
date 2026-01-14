import json
import re
import os
from pathlib import Path

# ==============================================================================
# 1. CONFIGURATION & INPUT DATA
# ==============================================================================

NOTE_ID = "note_156"

# Raw text of the note (cleaned of [source] tags for production use)
RAW_TEXT = """NOTE_ID:  note_156 SOURCE_FILE: note_156.txt Indications: Mediastinal adenopathy
Procedure: EBUS bronchoscopy – single station
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
A large, station 7, lymph node was identified and sampling by transbronchial needle aspiration was performed with the Olympus 22G EBUS-TBNA needles with a total of 7 passes performed.
Rapid onsite pathological evaluation showed malignancy. Samples were sent for both flow and routine cytology.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and DECAMP research bronchoscopy was performed with endobronchial forceps biopsy of the right upper lobe, right middle lobe and left upper lobe as well as endobronchial brushing of bronchus intermedius.
After suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5cc
Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies and DECAMP research protocol.
- The patient has remained stable and has been transferred in good condition to the post-procedural monitoring unit.
- Will await final pathology results"""

# Entities to extract based on Label_guide_UPDATED.csv
# Format: (Text substring, Label, Occurrence Index (0-based))
ENTITIES_TO_EXTRACT = [
    ("Mediastinal adenopathy", "OBS_LESION", 0),
    ("EBUS bronchoscopy", "PROC_METHOD", 0),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT", 0),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 0),
    ("vocal cords", "ANAT_AIRWAY", 0),
    ("subglottic space", "ANAT_AIRWAY", 0),
    ("trachea", "ANAT_AIRWAY", 0),
    ("carina", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 1), # Context: "examined to at least..."
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT", 0),
    ("station 7", "ANAT_LN_STATION", 0),
    ("transbronchial needle aspiration", "PROC_ACTION", 0),
    ("22G", "DEV_NEEDLE", 0),
    ("7 passes", "MEAS_COUNT", 0),
    ("malignancy", "OBS_ROSE", 0),
    ("EBUS bronchoscopy", "PROC_METHOD", 1), # "Following completion of..."
    ("Q190 video bronchoscope", "DEV_INSTRUMENT", 1), # "re-inserted"
    ("forceps", "DEV_INSTRUMENT", 0),
    ("biopsy", "PROC_ACTION", 0), # in "forceps biopsy"
    ("right upper lobe", "ANAT_LUNG_LOC", 0),
    ("right middle lobe", "ANAT_LUNG_LOC", 0),
    ("left upper lobe", "ANAT_LUNG_LOC", 0),
    ("brushing", "PROC_ACTION", 0),
    ("bronchus intermedius", "ANAT_AIRWAY", 0),
    ("No immediate complications", "OUTCOME_COMPLICATION", 0),
    ("5cc", "MEAS_VOL", 0)
]

# ==============================================================================
# 2. PATH SETUP
# ==============================================================================

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# 3. EXTRACTION LOGIC
# ==============================================================================

def get_span_indices(text, substring, occurrence=0):
    """Finds the start/end indices of the Nth occurrence of a substring."""
    matches = [m for m in re.finditer(re.escape(substring), text)]
    if len(matches) > occurrence:
        m = matches[occurrence]
        return m.start(), m.end()
    return None, None

extracted_spans = []
label_counts_update = {}

for sub, label, occ in ENTITIES_TO_EXTRACT:
    start, end = get_span_indices(RAW_TEXT, sub, occ)
    
    if start is not None:
        # Create span object
        span_id = f"{label}_{start}"
        span_obj = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": label,
            "text": sub,
            "start": start,
            "end": end
        }
        extracted_spans.append(span_obj)
        
        # Update local counts
        label_counts_update[label] = label_counts_update.get(label, 0) + 1
        
        # Validation
        if RAW_TEXT[start:end] != sub:
            with open(LOG_PATH, "a") as log:
                log.write(f"MISMATCH: {span_id} expected '{sub}' got '{RAW_TEXT[start:end]}'\n")
    else:
        with open(LOG_PATH, "a") as log:
            log.write(f"MISSING: Could not find '{sub}' occurrence {occ} in {NOTE_ID}\n")

# ==============================================================================
# 4. FILE UPDATES
# ==============================================================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_spans
}

with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in extracted_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
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
# Assuming 1 file per script run for this workflow
stats["total_files"] += 1 
stats["total_spans_raw"] += len(extracted_spans)
stats["total_spans_valid"] += len(extracted_spans)

for label, count in label_counts_update.items():
    stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_spans)} entities.")