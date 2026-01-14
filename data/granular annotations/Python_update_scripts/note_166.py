import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_166"
TIMESTAMP = datetime.datetime.now().isoformat()

# Dynamic output directory based on requirements
# Script location assumption: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Input Data (Raw Text)
# ==========================================
RAW_TEXT = """Indications: Mediastinal adenopathy
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
The 11Ri lymph node was identified and sampling by transbronchial needle aspiration was performed with the Olympus 22G EBUS-TBNA needles with a total of 6 passes performed.
Rapid onsite pathological evaluation showed occasional lymphocytes but malignancy was not identified.
The 11Rs lymph node was then identified and sampling by transbronchial needle aspiration was performed with the Olympus 22G EBUS-TBNA needles with a total of 5 passes performed.
Rapid onsite pathological evaluation did not identify malignancy.  Samples were sent for both flow and routine cytology.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5cc
Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-procedural monitoring unit.
- Will await final pathology results"""

# ==========================================
# 3. Entity Definitions (Strict Mapping)
# ==========================================
# Helper to find exact offsets
def find_entity(text, phrase, label, occurrences=1):
    start = 0
    spans = []
    for _ in range(occurrences):
        idx = text.find(phrase, start)
        if idx == -1:
            break # Stop if not found
        spans.append({
            "label": label,
            "start": idx,
            "end": idx + len(phrase),
            "text": phrase
        })
        start = idx + len(phrase)
    return spans

# Extract Entities
entities_to_find = [
    ("Mediastinal adenopathy", "OBS_LESION", 1),
    ("tracheobronchial tree", "ANAT_AIRWAY", 4), # Appears multiple times
    ("Q190 video bronchoscope", "DEV_INSTRUMENT", 2),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 3),
    ("vocal cords", "ANAT_AIRWAY", 1),
    ("subglottic space", "ANAT_AIRWAY", 1),
    ("trachea", "ANAT_AIRWAY", 1), # Note lowercase in text 'The trachea'
    ("carina", "ANAT_AIRWAY", 1),
    ("Bronchial mucosa", "ANAT_AIRWAY", 1),
    ("secretions", "OBS_FINDING", 2), # "no secretions", "suctioning... secretions"
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT", 1),
    ("11Ri", "ANAT_LN_STATION", 1),
    ("transbronchial needle aspiration", "PROC_ACTION", 2),
    ("22G", "DEV_NEEDLE", 2),
    ("6 passes", "MEAS_COUNT", 1),
    ("lymphocytes", "OBS_ROSE", 1),
    ("malignancy", "OBS_ROSE", 2),
    ("11Rs", "ANAT_LN_STATION", 1),
    ("5 passes", "MEAS_COUNT", 1),
    ("suctioning", "PROC_ACTION", 1),
    ("blood", "OBS_FINDING", 1),
    ("5cc", "MEAS_VOL", 1),
    ("flexible bronchoscopy", "PROC_ACTION", 1),
    ("EBUS bronchoscopy", "PROC_ACTION", 1)
]

detected_entities = []

# Case-insensitive search simulation by matching exact strings in text
# (Note: The text variable provided above preserves case)
for phrase, label, count in entities_to_find:
    # We perform a case-insensitive search to locate the index, then grab the exact text
    # However, find_entity uses exact string match. We must match the raw text case.
    # Adjusting specific queries to match raw text casing:
    
    search_phrase = phrase
    if phrase == "trachea": search_phrase = "The trachea"[4:] # "trachea" is lowercase in sentence
    
    found = find_entity(RAW_TEXT, search_phrase, label, count)
    detected_entities.extend(found)

# Sort entities by start offset
detected_entities.sort(key=lambda x: x['start'])

# ==========================================
# 4. JSON Line Generation
# ==========================================

# 4.1 Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[e["start"], e["end"], e["label"]] for e in detected_entities]
}

# 4.2 Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

# 4.3 Update spans.jsonl
span_entries = []
for ent in detected_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    })

# ==========================================
# 5. File Operations & Validation
# ==========================================

def append_jsonl(path, data):
    with open(path, 'a', encoding='utf-8') as f:
        if isinstance(data, list):
            for item in data:
                f.write(json.dumps(item) + '\n')
        else:
            f.write(json.dumps(data) + '\n')

# Execute Appends
print(f"Updating {NER_DATASET_PATH}...")
append_jsonl(NER_DATASET_PATH, ner_entry)

print(f"Updating {NOTES_PATH}...")
append_jsonl(NOTES_PATH, note_entry)

print(f"Updating {SPANS_PATH}...")
append_jsonl(SPANS_PATH, span_entries)

# 5.1 Update stats.json
print(f"Updating {STATS_PATH}...")
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
stats["total_files"] += 1 # Assuming 1 note per file for this pipeline
stats["total_spans_raw"] += len(detected_entities)
stats["total_spans_valid"] += len(detected_entities)

for ent in detected_entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

# 5.2 Validate & Log
print(f"Validating alignments...")
with open(LOG_PATH, 'a', encoding='utf-8') as log:
    for ent in detected_entities:
        extracted = RAW_TEXT[ent['start']:ent['end']]
        if extracted != ent['text']:
            err_msg = f"[{datetime.datetime.now()}] MISMATCH in {NOTE_ID}: Label {ent['label']} expected '{ent['text']}' but found '{extracted}' at {ent['start']}:{ent['end']}\n"
            log.write(err_msg)
            print(f"WARNING: {err_msg.strip()}")

print("Update complete.")