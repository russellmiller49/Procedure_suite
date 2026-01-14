import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_161"
SCRIPT_DIR = Path(__file__).resolve().parent
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (SCRIPT_DIR.parents[1] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = SCRIPT_DIR.parents[1] / "stats.json" # Assuming stats is at root or similar level, adjusting to prompt context
# Re-adjusting stats path to match the likely structure based on file upload context (usually parallel or root)
# If stats.json was provided in the context, we treat it as existing in the 'data' or root folder. 
# For this script, we will assume it is in the same directory as the script or one level up for safety, 
# but strictly following the prompt's output directory logic:
STATS_PATH = OUTPUT_DIR / "stats.json" 
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# Raw Text from note_161.txt
RAW_TEXT = """Proceduralist(s): Russell Miller MD, Pulmonologist, Jeff Biberson (Fellow)Garrett Harp, MD (Fellow)
Procedure Name: EBUS Staging Bronchoscopy.
(CPT 31652 convex probe endobronchial ultrasound sampling 2 or fewer hilar or mediastinal stations or structures).
Indications: Diagnosis and staging of presumed lung cancer
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record.
Laboratory studies and radiographs 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the ET tube into the tracheobronchial tree.
Tracheomalacia was noted in the trachea. The carina was sharp. The right-sided airway anatomy was normal.
The left sided airway anatomy was normal. No evidence of endobronchial disease was seen to at least the first sub-segments.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 11L  (5.4mm) and 4R (5.5mm) lymph nodes.
Sampling by transbronchial needle aspiration was performed beginning with the 11L Lymph node, followed by 4R lymph nodes using an Olympus Visioshot EBUSTBNA 22 gauge needle.
ROSE showed non-diagnostic tissue in the low probability 11L lymph node and benign lymphocytes in the 4Rs.
All samples were sent for routine cytology. The Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5 cc.

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# ==========================================
# ENTITY EXTRACTION LOGIC
# ==========================================
# Helper to find start/end indices
def find_entity(text, sub, label, start_search=0):
    start = text.find(sub, start_search)
    if start == -1:
        return None
    return {
        "span_id": f"{label}_{start}",
        "note_id": NOTE_ID,
        "label": label,
        "text": sub,
        "start": start,
        "end": start + len(sub)
    }

entities_to_find = [
    ("EBUS", "PROC_METHOD"),
    ("Bronchoscopy", "PROC_ACTION"),
    ("convex probe endobronchial ultrasound", "PROC_METHOD"),
    ("hilar", "ANAT_LN_STATION"),
    ("mediastinal", "ANAT_LN_STATION"),
    ("lung cancer", "OBS_LESION"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"), # Found twice
    ("tracheobronchial tree", "ANAT_AIRWAY"), # Second occurrence
    ("Tracheomalacia", "OBS_FINDING"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("right-sided airway", "ANAT_AIRWAY"),
    ("left sided airway", "ANAT_AIRWAY"),
    ("endobronchial disease", "OBS_LESION"), # Negative finding, but often captured as concept
    ("hilar", "ANAT_LN_STATION"),
    ("mediastinal", "ANAT_LN_STATION"),
    ("5mm", "MEAS_SIZE"),
    ("11L", "ANAT_LN_STATION"),
    ("5.4mm", "MEAS_SIZE"),
    ("4R", "ANAT_LN_STATION"),
    ("5.5mm", "MEAS_SIZE"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("11L", "ANAT_LN_STATION"),
    ("4R", "ANAT_LN_STATION"),
    ("Olympus Visioshot", "DEV_INSTRUMENT"),
    ("22 gauge", "DEV_NEEDLE"),
    ("non-diagnostic tissue", "OBS_ROSE"),
    ("11L", "ANAT_LN_STATION"),
    ("benign lymphocytes", "OBS_ROSE"),
    ("4Rs", "ANAT_LN_STATION"), # Plural variant
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("No immediate complications", "OUTCOME_COMPLICATION"),
    ("flexible bronchoscopy", "PROC_ACTION"),
    ("endobronchial ultrasound", "PROC_METHOD"),
    ("biopsies", "PROC_ACTION")
]

extracted_entities = []
cursor_map = {} # To track duplicates

for sub, label in entities_to_find:
    # Use cursor to handle multiple occurrences of same string
    search_start = cursor_map.get(sub, 0)
    entity = find_entity(RAW_TEXT, sub, label, search_start)
    if entity:
        extracted_entities.append(entity)
        cursor_map[sub] = entity["end"] # Update cursor for next search of this string

# ==========================================
# FILE UPDATES
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {
            "start": e["start"],
            "end": e["end"],
            "label": e["label"]
        }
        for e in extracted_entities
    ]
}

with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for entity in extracted_entities:
        f.write(json.dumps(entity) + "\n")

# 4. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    # Initialize if missing (fallback)
    stats = {
        "total_files": 0, "successful_files": 0, "total_notes": 0,
        "total_spans_raw": 0, "total_spans_valid": 0,
        "label_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for entity in extracted_entities:
    lbl = entity["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ==========================================
# VALIDATION
# ==========================================
with open(LOG_PATH, "a", encoding="utf-8") as log:
    for entity in extracted_entities:
        snippet = RAW_TEXT[entity["start"]:entity["end"]]
        if snippet != entity["text"]:
            log.write(f"MISMATCH: {NOTE_ID} - Expected '{entity['text']}', found '{snippet}'\n")

print(f"Successfully processed {NOTE_ID}. Files updated in {OUTPUT_DIR}")