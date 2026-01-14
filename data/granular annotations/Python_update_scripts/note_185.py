import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_185"

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
# 2. Raw Text & Annotations
# ==========================================
RAW_TEXT = """Procedure Name: EBUS Bronchoscopy
Indications: staging of bilateral lung cancer (metastatic vs synchronous primary)
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
 Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 4LR,7, and 4R lymph nodes.
Sampling by transbronchial needle aspiration was performed beginning with the 4L Lymph node followed by 7, and 4R lymph nodes using an Olympus EBUSTBNA 22 gauge needle.
The 4L lymph node was extremely difficult to access due to angle of left mainstem and after one biopsy no further attempts performed.
Further details regarding nodal size and number of samples are included in the EBUS procedural sheet which is available in EMR.
ROSE showed non-diagnostic tissue in the 4L and 4R lymph nodes and benign lymphocytes in the station 7 lymph node.
All samples were sent for routine cytology. The Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5 cc.

Post Procedure Recommendations:
- Transfer to PACU and home per protocol
- Will await final pathology results"""

# Define entities to match strict Label_guide_UPDATED.csv
# Format: (Label, Text_to_find)
# Note: We will find ALL occurrences of these strings to maximize capture
TARGET_ENTITIES = [
    ("PROC_METHOD", "EBUS"),
    ("OBS_LESION", "lung cancer"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"), # Case insensitive search applied below
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "Bronchial mucosa"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "video bronchoscope"), # Covers generic mentions
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("ANAT_LN_STATION", "lymph node"), # Captures general mentions
    ("ANAT_LN_STATION", "lymph nodes"),
    ("ANAT_LN_STATION", "station 4LR"),
    ("ANAT_LN_STATION", "7"),
    ("ANAT_LN_STATION", "4R"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("ANAT_LN_STATION", "4L"),
    ("DEV_NEEDLE", "22 gauge needle"),
    ("OBS_ROSE", "non-diagnostic tissue"),
    ("OBS_ROSE", "benign lymphocytes"),
    ("ANAT_LN_STATION", "station 7"),
    ("OBS_FINDING", "active bleeding"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "5 cc")
]

# ==========================================
# 3. Processing Logic
# ==========================================

def find_entities(text, entity_list):
    """
    Finds all non-overlapping occurrences of entities in the text.
    """
    spans = []
    text_lower = text.lower()
    
    for label, entity_text in entity_list:
        start = 0
        while True:
            # Case-insensitive search for robustness, but extract exact casing
            idx = text_lower.find(entity_text.lower(), start)
            if idx == -1:
                break
            
            end = idx + len(entity_text)
            
            # Check for overlap with existing spans
            is_overlap = False
            for existing in spans:
                if not (end <= existing['start'] or idx >= existing['end']):
                    is_overlap = True
                    # Prefer longer matches (greedy) - simplified here by list order
                    break
            
            if not is_overlap:
                # Extract exact text from raw (preserves case)
                actual_text = text[idx:end]
                spans.append({
                    "span_id": f"{label}_{idx}",
                    "note_id": NOTE_ID,
                    "label": label,
                    "text": actual_text,
                    "start": idx,
                    "end": end
                })
            
            start = end
            
    # Sort by start index
    spans.sort(key=lambda x: x['start'])
    return spans

# Extract spans
valid_spans = find_entities(RAW_TEXT, TARGET_ENTITIES)

# Prepare NER dataset entry
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {"id": s["span_id"], "label": s["label"], "start_offset": s["start"], "end_offset": s["end"]}
        for s in valid_spans
    ]
}

# ==========================================
# 4. File Operations
# ==========================================

# A. Update ner_dataset_all.jsonl
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps({"id": NOTE_ID, "text": RAW_TEXT}) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in valid_spans:
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
stats["total_files"] += 1 # Assuming 1 note = 1 file context
stats["total_spans_raw"] += len(valid_spans)
stats["total_spans_valid"] += len(valid_spans)

for span in valid_spans:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# E. Validation & Logging
with open(LOG_PATH, "a", encoding="utf-8") as log:
    for span in valid_spans:
        extracted = RAW_TEXT[span['start']:span['end']]
        if extracted != span['text']:
            timestamp = datetime.datetime.now().isoformat()
            log.write(f"[{timestamp}] WARNING: Mismatch in {NOTE_ID}. "
                      f"Span: {span['span_id']}. "
                      f"Expected: '{span['text']}', Found: '{extracted}'\n")

print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")