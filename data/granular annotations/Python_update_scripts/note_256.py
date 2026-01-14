import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_256"

# Define the exact raw text content from the source file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Bronchial stenosis
POSTOPERATIVE DIAGNOSIS: Radiation induced bronchial stenosis
PROCEDURE PERFORMED: Flexible bronchoscopy balloon dilatation 
INDICATIONS: left sided lung collapse and possible bronchial obstruction.
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the operating room.
An I-gel LMA was placed and the diagnostic flexible bronchoscope was inserted through the airway device.
The vocal cords were visualized and normal.  The subglottic space was normal.
The trachea was normal appearing with minimal mild thick secretions.
The bronchoscope was then advanced to the main carina, which was sharp.
The bronchoscope was then advanced into the right mainstem. Each segment and subsegment within the right upper, right middle, right lower lobe was well visualized.
The right sided airway anatomy was normal and no specific masses or other lesions were identified throughout the tracheobronchial tree on the right.
The bronchoscope was then withdrawn into the trachea and then advanced into the left main stem.
In the distal mainstem there was circumferential erythema of the airway wall without stenosis.
There was purulent secretions in the left upper and lower lobe.
Bronchial wash was performed in the left upper lobe for culture.
The left upper lobe airways were not stenotic but had chronic erythematous appearance consistent with radiation changes.
The left lower lobe take-off was not stenotic but there was moderate stenosis of the lateral basilar segment of the lower lobe and severe stenosis (90%) of the anterior medial segment.
No specific masses or other lesions were identified throughout the tracheobronchial tree on the left.
Following inspection we removed the diagnostic bronchoscope and introduced the T180 therapeutic bronchoscope.
Our attention to the stenosis within the lateral basilar segment of the left lower lobe and gentle dilatation was performed with the 6mm Elation dilating balloon with mild improvement in stenosis.
The airway wall was friable however and oozed easily. We then attempted to gently dilate the anterior-medial segment by bypassing the obstruction and gently inflating the balloon to partial expansion (<6mm) and pull back through the stenosis.
When this was done relatively brisk bleeding developed. We then wedged the bronchoscope in the left lower lobe for 2 minutes and reassessed.
At that point the bleeding had stopped and we felt that given the distal airway disease (likely radiation induced) and only segmental obstruction, the risk/benefit ratio of continued attempts at dilatation favored abstaining from further intervention.
At this point, one we were satisfied that there was no active bleeding the bronchoscope was removed and the procedure completed.
Recommendations:
- Patient to PACU for recovery
- Await culture results
- Follow-up with primary pulmonologist"""

# Target Directory: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Entity Definition (Manual NER)
# ==========================================
# Ordered list of entities to extract. 
# Format: (Label, Text_Snippet)
# Note: The script will find these sequentially to handle duplicates.

entities_to_extract = [
    ("ANAT_AIRWAY", "Bronchial"),
    ("OBS_FINDING", "stenosis"),
    ("ANAT_AIRWAY", "bronchial"),
    ("OBS_FINDING", "stenosis"),
    ("PROC_METHOD", "Flexible bronchoscopy"),
    ("PROC_ACTION", "balloon dilatation"),
    ("ANAT_LUNG_LOC", "left sided lung"),
    ("OBS_FINDING", "collapse"),
    ("ANAT_AIRWAY", "bronchial"),
    ("OBS_FINDING", "obstruction"),
    ("PROC_METHOD", "General Anesthesia"),
    ("DEV_INSTRUMENT", "I-gel LMA"),
    ("DEV_INSTRUMENT", "diagnostic flexible bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("OBS_FINDING", "normal"),
    ("OBS_FINDING", "minimal mild thick secretions"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_AIRWAY", "main carina"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("ANAT_LUNG_LOC", "right upper"),
    ("ANAT_LUNG_LOC", "right middle"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("OBS_FINDING", "normal"),
    ("OBS_LESION", "masses"),
    ("OBS_LESION", "lesions"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "left main stem"),
    ("ANAT_AIRWAY", "distal mainstem"),
    ("OBS_FINDING", "circumferential erythema"),
    ("ANAT_AIRWAY", "airway wall"),
    ("OBS_FINDING", "stenosis"),
    ("OBS_FINDING", "purulent secretions"),
    ("ANAT_LUNG_LOC", "left upper"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("PROC_ACTION", "Bronchial wash"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("OBS_FINDING", "stenotic"),
    ("OBS_FINDING", "erythematous appearance"),
    ("OBS_FINDING", "radiation changes"),
    ("ANAT_AIRWAY", "left lower lobe take-off"),
    ("OBS_FINDING", "stenotic"),
    ("OBS_FINDING", "stenosis"),
    ("ANAT_LUNG_LOC", "lateral basilar segment"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("OBS_FINDING", "stenosis"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "90%"),
    ("ANAT_LUNG_LOC", "anterior medial segment"),
    ("OBS_LESION", "masses"),
    ("OBS_LESION", "lesions"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "diagnostic bronchoscope"),
    ("DEV_INSTRUMENT", "T180 therapeutic bronchoscope"),
    ("OBS_FINDING", "stenosis"),
    ("ANAT_LUNG_LOC", "lateral basilar segment"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("PROC_ACTION", "dilatation"),
    ("DEV_INSTRUMENT", "6mm Elation dilating balloon"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "mild improvement"),
    ("OBS_FINDING", "stenosis"),
    ("ANAT_AIRWAY", "airway wall"),
    ("OBS_FINDING", "friable"),
    ("OBS_FINDING", "oozed easily"),
    ("PROC_ACTION", "dilate"),
    ("ANAT_LUNG_LOC", "anterior-medial segment"),
    ("OBS_FINDING", "obstruction"),
    ("PROC_ACTION", "inflating"),
    ("DEV_INSTRUMENT", "balloon"),
    ("MEAS_SIZE", "<6mm"),
    ("PROC_ACTION", "pull back"),
    ("OBS_FINDING", "stenosis"),
    ("OUTCOME_COMPLICATION", "brisk bleeding developed"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("MEAS_TIME", "2 minutes"),
    ("OUTCOME_COMPLICATION", "bleeding had stopped"),
    ("OBS_FINDING", "segmental obstruction"),
    ("PROC_ACTION", "dilatation"),
    ("OUTCOME_COMPLICATION", "no active bleeding"),
    ("DEV_INSTRUMENT", "bronchoscope")
]

# ==========================================
# 3. Processing Logic
# ==========================================

extracted_spans = []
current_search_index = 0

for label, text_match in entities_to_extract:
    # Find the entity starting from the last found index to support duplicates
    start_idx = RAW_TEXT.find(text_match, current_search_index)
    
    if start_idx == -1:
        # Fallback: Warning if not found (should not happen with correct data)
        print(f"WARNING: Could not find '{text_match}' after index {current_search_index}")
        continue
        
    end_idx = start_idx + len(text_match)
    
    # Store span
    span_obj = {
        "span_id": f"{label}_{start_idx}",
        "note_id": NOTE_ID,
        "label": label,
        "text": text_match,
        "start": start_idx,
        "end": end_idx
    }
    extracted_spans.append(span_obj)
    
    # Update search index to prevent overlapping or finding previous instances
    current_search_index = start_idx + 1

# ==========================================
# 4. File Write Operations
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
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
stats["total_files"] += 1  # Assuming 1:1 note to file ratio for this update
stats["total_spans_raw"] += len(extracted_spans)
stats["total_spans_valid"] += len(extracted_spans)

for span in extracted_spans:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# ==========================================
# 5. Validation
# ==========================================
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for span in extracted_spans:
        actual_text = RAW_TEXT[span["start"]:span["end"]]
        if actual_text != span["text"]:
            log_entry = f"[{datetime.datetime.now()}] MISMATCH: ID {NOTE_ID}, Label {span['label']}, Expected '{span['text']}', Got '{actual_text}'\n"
            log_file.write(log_entry)

print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_spans)} entities.")