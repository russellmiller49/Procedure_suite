import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_199"
# Script location: data/granular annotations/Python_update_scripts/
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
# 2. Raw Text & Extraction Logic
# ==========================================
RAW_TEXT = """NOTE_ID:  note_199 SOURCE_FILE: note_199.txt Indications: right lower lobe nodule
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the endotracheal tube.
The trachea was of normal caliber. The carina was boggy and edematous consistent with chronic radiation bronchitis.
The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, there were thick non-purulent sections in multiple airways which were suctioned.
Following inspection the super-dimension navigational catheter was inserted through the therapeutic bronchoscope and advanced into the airway.
Due to software issues the navigational catheter was mis-registering in relationship to the navigational map.
We attempted to use manual registration and were able to navigate to the nodule based on the navigational software however a suboptimal image was seen when the radial EBUS was inserted through the ENB catheter.
TBNAs were obtained and on ROSE showed lymphocytes which is unusual.
Due to concern that registration led to inaccurate navigation we converted to conventional bronchoscopy.
Using the P190 thin bronchoscope we advance into the area of interest based on imaging.
A concentric EBUS view was seen however when we attempted to insert the super-dimension TBNA needle the needle stiffness made in difficult to enter the target airway.
We then attempted to use the therapeutic bronchoscope we navigated a sheath catheter into the segment of interest within the right lower lobe and peripheral radial probe was inserted into the catheter to confirm location.
Ultrasound visualization yielded an eccentric view of the lesion. Similar issues with advancing the biopsy tools through the catheter were encountered and biopsies were suboptimal.
We then attempted to again navigate to the nodule with the thin bronchoscope and were able to advance to the target airway and forceps biopsies were performed under fluoroscopic imagine.
After samples were obtained and we were confident that there was no active bleeding, the bronchoscope was removed and the procedure concluded.
Complications: No immediate complications
Estimated Blood Loss: Less than 10 cc.
Recommendation:
- CXR to r/o PTX
- Await path results"""

# Sequential list of entities to extract (Label, Text Fragment)
# The script will search for these sequentially to handle duplicates correctly.
ENTITIES_TO_EXTRACT = [
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("OBS_LESION", "nodule"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # "topical anesthesia to... tracheobronchial tree"
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "trachea"), # Case insensitive match logic will be used below, but text in list matches casing for clarity
    ("ANAT_AIRWAY", "carina"),
    ("OBS_FINDING", "boggy"),
    ("OBS_FINDING", "edematous"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # "The tracheobronchial tree was examined..."
    ("ANAT_AIRWAY", "Bronchial"),
    ("OBS_FINDING", "thick non-purulent sections"),
    ("DEV_INSTRUMENT", "super-dimension navigational catheter"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("DEV_INSTRUMENT", "navigational catheter"),
    ("OBS_LESION", "nodule"),
    ("PROC_METHOD", "radial EBUS"),
    ("DEV_INSTRUMENT", "ENB catheter"),
    ("PROC_ACTION", "TBNAs"),
    ("OBS_ROSE", "lymphocytes"),
    ("PROC_METHOD", "conventional bronchoscopy"),
    ("DEV_INSTRUMENT", "P190 thin bronchoscope"),
    ("PROC_METHOD", "EBUS"), # "concentric EBUS view"
    ("DEV_NEEDLE", "super-dimension TBNA needle"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("DEV_INSTRUMENT", "sheath catheter"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("DEV_INSTRUMENT", "peripheral radial probe"),
    ("PROC_METHOD", "Ultrasound"),
    ("PROC_ACTION", "biopsies"), # "biopsies were suboptimal"
    ("OBS_LESION", "nodule"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "biopsies"), # "forceps biopsies"
    ("PROC_METHOD", "fluoroscopic"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "10 cc")
]

def extract_entities(text, entities_list):
    extracted = []
    current_idx = 0
    
    for label, substr in entities_list:
        # Find substring starting from current_idx, case-insensitive
        # (Though we use the exact casing in the list for simplicity, strict matching preferred)
        start = text.find(substr, current_idx)
        
        if start == -1:
            # Fallback: try case-insensitive
            lower_text = text.lower()
            lower_sub = substr.lower()
            start = lower_text.find(lower_sub, current_idx)
            
            if start != -1:
                # Recover exact text from original string
                substr = text[start : start + len(substr)]
            else:
                print(f"WARNING: Could not find '{substr}' after index {current_idx}")
                continue

        end = start + len(substr)
        extracted.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        current_idx = end # Move pointer forward to handle duplicates
        
    return extracted

# Run extraction
entities = extract_entities(RAW_TEXT, ENTITIES_TO_EXTRACT)

# ==========================================
# 3. File Operations
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[e["start"], e["end"], e["label"]] for e in entities]
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
new_spans = []
for e in entities:
    span_entry = {
        "span_id": f"{e['label']}_{e['start']}",
        "note_id": NOTE_ID,
        "label": e["label"],
        "text": e["text"],
        "start": e["start"],
        "end": e["end"]
    }
    new_spans.append(span_entry)

with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in new_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if os.path.exists(STATS_PATH):
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
stats["total_files"] += 1 # Assuming 1 note per file context
stats["total_spans_raw"] += len(entities)
stats["total_spans_valid"] += len(entities)

for e in entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# E. Validation & Logging
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for e in entities:
        extracted_text = RAW_TEXT[e["start"]:e["end"]]
        if extracted_text != e["text"]:
            log_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{e['text']}', found '{extracted_text}' at {e['start']}:{e['end']}\n"
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")