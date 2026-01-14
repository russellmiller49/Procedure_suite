import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_236"  # ID derived from filename
NOW = datetime.datetime.now().isoformat()

# Raw text content of the note
RAW_TEXT = """NOTE_ID:  note_236 SOURCE_FILE: note_236.txt PREOPERATIVE DIAGNOSIS: 
1.	Bronchus-intermedius obstruction secondary to Broncholithiasis
POSTOPERATIVE DIAGNOSIS: 
1.	 Resolved Bronchus-intermedius obstruction 
PROCEDURE PERFORMED: 
1.	CPT 31640 Rigid and flexible bronchoscopy with removal of broncholith 
2.	CPT 31641 Argon plasma coagulation for destruction of tissue.
1.	INDICATIONS:  1.Bronchus-intermedius obstruction secondary to broncholith
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the distal trachea and advanced into the distal trachea before attaching the monsoon JET ventilator.
Using the flexible bronchoscope airway inspection was performed. The tracheal carina was sharp. All left sided airways were normal.
The right mainstem and right upper lobe were normal. In the proximal bronchus intermedius there was a 60% obstructing polypoid endobronchial mass at area of known broncholith.
The rigid bronchoscope was then advanced into the right mainstem.
Gentle pressure was applied to the lesion with the flexible bronchoscopy allowing the broncholith to be extracted from the airway wall and then removed with suction.
This resulted in about 90% opening of the bronchus intermedius.
There was some brisk bleeding which was controlled with topical ice saline and balloon tamponade.
A small residual area of broncholith was seen and was extracted with flexible forceps.
Argon plasma coagulation was used to cauterize and destroy the oozing, mild residual obstruction from excess tissue at the base of the lesion.
Once we were satisfied that there was no residual bleeding the rigid bronchoscope was removed and the procedure complete.
Complications: None
Estimated blood loss: 10cc
Specimens: none
Recommendations:
- Admit to IM ward
- Advance diet as tolerated.
- Likely D/C in AM"""

# Target Entities to extract (Label, Text Fragment, Occurrence Index)
# Occurrence Index: 0 for 1st match, 1 for 2nd match, etc.
TARGET_SPANS = [
    ("PROC_METHOD", "Rigid and flexible bronchoscopy", 0),
    ("OBS_LESION", "broncholith", 0), # Header
    ("PROC_METHOD", "Argon plasma coagulation", 0),
    ("OBS_LESION", "broncholith", 1), # Indications
    ("MEAS_SIZE", "12 mm", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("ANAT_AIRWAY", "trachea", 0), # distal trachea 1
    ("ANAT_AIRWAY", "trachea", 1), # distal trachea 2
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("ANAT_AIRWAY", "tracheal carina", 0),
    ("LATERALITY", "left", 0),
    ("ANAT_AIRWAY", "airways", 0),
    ("LATERALITY", "right", 0),
    ("ANAT_AIRWAY", "mainstem", 0),
    ("ANAT_LUNG_LOC", "right upper lobe", 0),
    ("ANAT_AIRWAY", "bronchus intermedius", 0), # proximal...
    ("OUTCOME_AIRWAY_LUMEN_PRE", "60% obstructing", 0),
    ("OBS_LESION", "polypoid endobronchial mass", 0),
    ("OBS_LESION", "broncholith", 2), # known broncholith
    ("DEV_INSTRUMENT", "rigid bronchoscope", 1),
    ("LATERALITY", "right", 1),
    ("ANAT_AIRWAY", "mainstem", 1),
    ("PROC_METHOD", "flexible bronchoscopy", 0),
    ("OBS_LESION", "broncholith", 3), # extracted
    ("DEV_INSTRUMENT", "suction", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "90% opening", 0),
    ("ANAT_AIRWAY", "bronchus intermedius", 1),
    ("OUTCOME_COMPLICATION", "brisk bleeding", 0),
    ("DEV_INSTRUMENT", "balloon", 0),
    ("PROC_ACTION", "tamponade", 0),
    ("OBS_LESION", "broncholith", 4), # residual area
    ("DEV_INSTRUMENT", "flexible forceps", 0),
    ("PROC_METHOD", "Argon plasma coagulation", 1),
    ("PROC_ACTION", "cauterize", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 2),
    ("MEAS_VOL", "10cc", 0)
]

# ==========================================
# PATH SETUP
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILE_NER_DATASET = OUTPUT_DIR / "ner_dataset_all.jsonl"
FILE_NOTES = OUTPUT_DIR / "notes.jsonl"
FILE_SPANS = OUTPUT_DIR / "spans.jsonl"
FILE_STATS = OUTPUT_DIR / "stats.json"
FILE_LOG = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING & VALIDATION
# ==========================================

def find_offset(text, substring, match_index=0):
    """Finds the start/end indices of the Nth occurrence of a substring."""
    current_idx = -1
    for _ in range(match_index + 1):
        current_idx = text.find(substring, current_idx + 1)
        if current_idx == -1:
            return None, None
    return current_idx, current_idx + len(substring)

entities_data = []
spans_data = []
alignment_errors = []

for label, subtext, idx in TARGET_SPANS:
    start, end = find_offset(RAW_TEXT, subtext, idx)
    
    # Validation
    if start is None:
        alignment_errors.append(f"ERROR: Could not find '{subtext}' (index {idx}) in text.")
        continue
    
    extracted_text = RAW_TEXT[start:end]
    if extracted_text != subtext:
        alignment_errors.append(f"MISMATCH: Expected '{subtext}', got '{extracted_text}' at {start}-{end}")
        continue

    # Entity Object for ner_dataset_all.jsonl
    entities_data.append({
        "label": label,
        "start_offset": start,
        "end_offset": end,
        "text": subtext
    })

    # Span Object for spans.jsonl
    span_id = f"{label}_{start}"
    spans_data.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": label,
        "text": subtext,
        "start": start,
        "end": end
    })

# ==========================================
# FILE UPDATES
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": entities_data
}

with open(FILE_NER_DATASET, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(FILE_NOTES, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Update spans.jsonl
with open(FILE_SPANS, "a", encoding="utf-8") as f:
    for span in spans_data:
        f.write(json.dumps(span) + "\n")

# 4. Update stats.json
if os.path.exists(FILE_STATS):
    with open(FILE_STATS, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    # Fallback initialization if stats.json missing
    stats = {
        "total_files": 0, "successful_files": 0, "total_notes": 0,
        "total_spans_raw": 0, "total_spans_valid": 0,
        "alignment_warnings": 0, "alignment_errors": 0,
        "label_counts": {}
    }

# Increment global counters
stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(entities_data)
stats["total_spans_valid"] += len(entities_data)

# Update label counts
for ent in entities_data:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(FILE_STATS, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# 5. Log Warnings/Errors
if alignment_errors:
    with open(FILE_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n[{NOW}] Processing {NOTE_ID}:\n")
        for err in alignment_errors:
            f.write(f"  {err}\n")

print(f"Successfully processed {NOTE_ID}.")
print(f"Extracted {len(entities_data)} entities.")
if alignment_errors:
    print(f"WARNING: {len(alignment_errors)} alignment errors logged.")