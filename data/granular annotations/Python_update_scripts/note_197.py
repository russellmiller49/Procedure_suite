import json
import os
import datetime
from pathlib import Path

# --------------------------------------------------------------------------------
# 1. Configuration & Path Setup
# --------------------------------------------------------------------------------
NOTE_ID = "note_197"

# Define the raw text content from the source file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Diffuse parenchymal lung disease
POSTOPERATIVE DIAGNOSIS: Diffuse parenchymal lung disease 
PROCEDURE PERFORMED: Rigid bronchoscopy with transbronchial cryobiopsy, 
INDICATIONS: Diffuse parenchymal lung disease
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia

DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After receiving analgesia and paralytics the patient was bag masked and once preoxygenated a 12 mm rigid tracheoscope was inserted into the mid trachea and attached to the jet ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope.
After inspection bronchoscopy which was unremarkable a BAL was performed in the right middle lobe.
Subsequentlya Forgery balloon was inserted to the rigid bronchoscope into the anterior segment of the right lower lobe.
Under fluoroscopic guidance the cryoprobe was inserted past the balloon into the lateral left lower lobe segment under fluoroscopic guidance.
Once the pleural margin was reached the probe was withdrawn approximately 1 cm and the cryoprobe was activated for 4 seconds at which time the flexible bronchoscope and cryoprobe were removed en-bloc in the Fogarty balloon was inflated immediately after removal.
One specimen was removed from the cryoprobe the flexible bronchoscope was reinserted and the balloon was slowly deflated to assess for distal bleeding.
No blood was noted and this was repeated for a total of 6 biopsies.
Once we were confident that there was no active bleeding the flexible bronchoscope was removed.
Following completion of the procedure fluoroscopic evaluation of the pleura was performed to evaluate for pneumothorax and none was seen.
The rigid bronchoscope was subsequently removed once the patient was able to breathe spontaneously.
-	Patient to PACU
-	CXR pending
-	Await pathological evaluation of tissue"""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"
STATS_PATH = OUTPUT_DIR / "stats.json"
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"

# --------------------------------------------------------------------------------
# 2. Entity Definition
# --------------------------------------------------------------------------------
# Format: (Label, Exact Text substring)
# Order matters slightly for greedy matching if logic is simple, but we will scan
# and handle overlaps by prioritizing longer matches or distinct positions.
target_entities = [
    ("OBS_LESION", "Diffuse parenchymal lung disease"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "transbronchial cryobiopsy"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("DEV_INSTRUMENT", "jet ventilator"),
    ("DEV_INSTRUMENT", "rigid optic"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("PROC_ACTION", "inspection bronchoscopy"),
    ("PROC_ACTION", "BAL"),
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("DEV_INSTRUMENT", "Forgery balloon"),
    ("ANAT_LUNG_LOC", "anterior segment"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("PROC_METHOD", "fluoroscopic guidance"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("DEV_INSTRUMENT", "balloon"),
    ("ANAT_LUNG_LOC", "lateral left lower lobe segment"),
    ("ANAT_PLEURA", "pleural margin"),
    ("MEAS_SIZE", "1 cm"),
    ("MEAS_TIME", "4 seconds"),
    ("DEV_INSTRUMENT", "Fogarty balloon"),
    ("SPECIMEN", "specimen"),
    ("OBS_FINDING", "blood"),
    ("MEAS_COUNT", "6"),
    ("PROC_ACTION", "biopsies"),
    ("OBS_FINDING", "active bleeding"),
    ("PROC_METHOD", "fluoroscopic evaluation"),
    ("ANAT_PLEURA", "pleura"),
    ("OBS_FINDING", "pneumothorax"),
    ("SPECIMEN", "tissue")
]

# --------------------------------------------------------------------------------
# 3. Analyze & Extract (Offset Calculation)
# --------------------------------------------------------------------------------
extracted_entities = []
_search_start_indices = {text: 0 for _, text in target_entities}

# Sort entities by length (descending) to handle potential substrings correctly 
# if we were doing a single pass, but here we find all occurrences.
# We will just iterate and find every instance of every entity.
temp_found = []

for label, text in target_entities:
    start_search = 0
    while True:
        start = RAW_TEXT.find(text, start_search)
        if start == -1:
            break
        end = start + len(text)
        
        # Check for overlap with already found entities
        is_overlap = False
        for exist_start, exist_end, _, _ in temp_found:
            if not (end <= exist_start or start >= exist_end):
                is_overlap = True
                # If overlap, generally keep the longer one. 
                # For this specific script, the list is curated to avoid partial word matches
                # (e.g. "blood" vs "active bleeding"). 
                # We will handle specific sub-string overrides if necessary.
                pass 
        
        # Special handling for "blood" vs "active bleeding"
        # If we found "active bleeding", "blood" inside it shouldn't be a separate entity 
        # unless intended. We will filter strict containment later.
        
        temp_found.append((start, end, label, text))
        start_search = end

# Filter strictly contained spans (e.g., "blood" inside "active bleeding")
final_entities = []
# Sort by start position
temp_found.sort(key=lambda x: x[0])

for i in range(len(temp_found)):
    current = temp_found[i]
    c_start, c_end, c_label, c_text = current
    
    is_contained = False
    for j in range(len(temp_found)):
        if i == j: continue
        o_start, o_end, o_label, o_text = temp_found[j]
        
        # If current is strictly inside other
        if c_start >= o_start and c_end <= o_end and (o_end - o_start) > (c_end - c_start):
            is_contained = True
            break
    
    if not is_contained:
        final_entities.append({
            "start": c_start,
            "end": c_end,
            "label": c_label,
            "text": c_text
        })

# --------------------------------------------------------------------------------
# 4. JSONL Generation Prep
# --------------------------------------------------------------------------------
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": final_entities
}

note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

span_entries = []
for ent in final_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    })

# --------------------------------------------------------------------------------
# 5. File Operations
# --------------------------------------------------------------------------------

# A. Update ner_dataset_all.jsonl
with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
with open(NOTES_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, 'a', encoding='utf-8') as f:
    for span in span_entries:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
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
# Assuming 1 file per script run for this logic
stats["total_files"] += 1 
stats["total_spans_raw"] += len(final_entities)
stats["total_spans_valid"] += len(final_entities)

for ent in final_entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)

# --------------------------------------------------------------------------------
# 6. Validation & Logging
# --------------------------------------------------------------------------------
with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as log_file:
    for ent in final_entities:
        extracted_text = RAW_TEXT[ent["start"]:ent["end"]]
        if extracted_text != ent["text"]:
            log_msg = (
                f"[{datetime.datetime.now().isoformat()}] MISMATCH in {NOTE_ID}: "
                f"Expected '{ent['text']}', found '{extracted_text}' at {ent['start']}:{ent['end']}\n"
            )
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")