from pathlib import Path
import json
import os
import re

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_251"
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Raw Text Content
# ==========================================
RAW_TEXT = """PROCEDURE PERFORMED: Directional ultrasound with TBNA , Bronchoscopy, Flexible
INDICATIONS FOR EXAMINATION: Mediastinal adenopathy
MEDICATIONS: General anesthesia
INSTRUMENTS: #1 2401195 Q190
#9 7621262 UC180F
TECHNICAL DIFFICULTY: No
LIMITATIONS: None, TOLERANCE: Good
PROCEDURE TECHNIQUE:
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed
consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure
assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the
intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial
tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the
tracheobronchial tree.
The laryngeal mask airway was in good position.
VISUALIZATION: Good
FINDINGS: The vocal cords appeared normal. The subglottic space was normal.
The trachea
was of normal caliber however there was signifigant exhalational collapse indicitive of EDAC vs
TBM which extended into the proximal mainstem bronchi.
. The carina was sharp. The
tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa
and anatomy were normal; there are no endobronchial lesions, and no secretions.
The video
bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was
introduced through the mouth, via laryngeal mask airway and advanced to the
tracheobronchial tree.
Radiographically abnormal mediastinal lymph nodes were evaluated
and decision was made to sample the station 7 lymph node which was 9 mm in short axis
diameter and station 11L which was 7mm in short axis diameter.
Sampling by transbronchial
needle aspiration was performed with the Olympus EBUSTBNA 22 gauge needle beginning
with the station 7 Lymph node, followed by the station 11L lymph node a total of 5 biopsies
were performed in each station.
ROSE evaluation yielded benign appearing lymphocytes. All
samples were sent for routine cytology and flow cytometry.
Following completion of EBUS
bronchoscopy, the Q190 video bronchoscope was then re-inserted and BAL was performed in
the RML with 120 cc of saline instilled and 35cc return.
After suctioning blood and secretions. there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Page 2 / 2
ESTIMATED BLOOD LOSS: 2
COMPLICATIONS: None
IMPRESSION: Technically successful flexible bronchoscopy with endobronchial ultrasoundguided
biopsies and bronchioalveolar lavage.
RECOMMENDATIONS
- Will await final pathology results"""

# ==========================================
# 3. Entity Definitions
# ==========================================
# List of (Label, Text Snippet)
# The script will locate all non-overlapping instances of these strings.
entities_to_find = [
    ("PROC_METHOD", "Directional ultrasound"),
    ("PROC_ACTION", "TBNA"),
    ("PROC_ACTION", "Bronchoscopy, Flexible"),
    ("OBS_LESION", "Mediastinal adenopathy"),
    ("MEDICATION", "General anesthesia"),
    ("DEV_INSTRUMENT", "Q190"),
    ("DEV_INSTRUMENT", "UC180F"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "Trachea"),
    ("OBS_FINDING", "exhalational collapse"),
    ("OBS_FINDING", "EDAC"),
    ("OBS_FINDING", "TBM"),
    ("ANAT_AIRWAY", "proximal mainstem bronchi"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "Bronchial mucosa"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "secretions"),
    ("PROC_METHOD", "EBUS"),
    ("ANAT_LN_STATION", "mediastinal lymph nodes"),
    ("ANAT_LN_STATION", "station 7"),
    ("MEAS_SIZE", "9 mm"),
    ("ANAT_LN_STATION", "station 11L"),
    ("MEAS_SIZE", "7mm"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_INSTRUMENT", "Olympus EBUSTBNA"),
    ("DEV_NEEDLE", "22 gauge"),
    ("PROC_ACTION", "biopsies"),
    ("OBS_ROSE", "benign appearing lymphocytes"),
    ("PROC_ACTION", "BAL"),
    ("ANAT_LUNG_LOC", "RML"),
    ("MEAS_VOL", "120 cc"),
    ("MEAS_VOL", "35cc"),
    ("OBS_FINDING", "blood"),
    ("OBS_FINDING", "active bleeding"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "bronchioalveolar lavage")
]

# Special handling for short integers or tricky context
special_entities = [
    # (Label, value_to_find, context_phrase_to_locate)
    ("MEAS_COUNT", "5", "5 biopsies"),
    ("MEAS_VOL", "2", "ESTIMATED BLOOD LOSS: 2")
]

# ==========================================
# 4. Entity Extraction Logic
# ==========================================
extracted_entities = []

# Helper to find all occurrences
def find_entities(text, label, target):
    matches = []
    start = 0
    while True:
        idx = text.find(target, start)
        if idx == -1:
            break
        end = idx + len(target)
        matches.append({
            "span_id": f"{label}_{idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": target,
            "start": idx,
            "end": end
        })
        start = end
    return matches

# Process standard entities
for label, target in entities_to_find:
    extracted_entities.extend(find_entities(RAW_TEXT, label, target))

# Process special entities
for label, value, context in special_entities:
    # Find the context first
    ctx_idx = RAW_TEXT.find(context)
    if ctx_idx != -1:
        # Find value within context
        val_start = RAW_TEXT.find(value, ctx_idx)
        if val_start != -1:
            val_end = val_start + len(value)
            extracted_entities.append({
                "span_id": f"{label}_{val_start}",
                "note_id": NOTE_ID,
                "label": label,
                "text": value,
                "start": val_start,
                "end": val_end
            })

# Remove duplicates (if any) and sort by start index
unique_entities = {f"{e['start']}:{e['end']}": e for e in extracted_entities}.values()
sorted_entities = sorted(unique_entities, key=lambda x: x['start'])

# ==========================================
# 5. Output Generation
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[e["start"], e["end"], e["label"]] for e in sorted_entities]
}

with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
    for span in sorted_entities:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
stats_path = OUTPUT_DIR / "stats.json"
if stats_path.exists():
    with open(stats_path, "r", encoding="utf-8") as f:
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
stats["total_files"] += 1
stats["total_spans_raw"] += len(sorted_entities)
stats["total_spans_valid"] += len(sorted_entities)

for span in sorted_entities:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# E. Validate & Log
log_path = OUTPUT_DIR / "alignment_warnings.log"
with open(log_path, "a", encoding="utf-8") as f:
    for span in sorted_entities:
        original = RAW_TEXT[span["start"]:span["end"]]
        if original != span["text"]:
            f.write(f"MISMATCH in {NOTE_ID}: Span '{span['text']}' vs Text '{original}' at {span['start']}\n")

print(f"Successfully processed {NOTE_ID}. Data written to {OUTPUT_DIR}")