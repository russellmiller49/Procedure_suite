import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
NOTE_ID = "note_260"
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
# RAW TEXT INPUT
# ==========================================
text = """NOTE_ID:  note_260 SOURCE_FILE: note_260.txt PREOPERATIVE DIAGNOSIS: Malignant lung mass with left lower lobe and partial left main-stem obstruction
POSTOPERATIVE DIAGNOSIS: Malignant airway obstruction 
PROCEDURE PERFORMED: Rigid bronchoscopy with airway debulking
INDICATIONS: left mainstem obstruction 
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T180 therapeutic video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Right sided bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions.  The proximal and mid left mainstem were normal.
In the distal left mainstem a white fungating tumor was seen causing complete obstruction of the left lower lobe and extending from the left lower lobe bronchus to causing complete obstruction of the lingula and 80% obstruction of the left mainstem.
The LMA was then removed and a 12 mm ventilating rigid bronchoscope was subsequently inserted into the mid trachea and attached to the jet ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope.
We then utilized cryoextraction to remove large pieces of tumor piece meal.
Most of the superficial tumor was avascular and did not bleed but as we continued debulking into less necrotic tumor mild bleeding occurred and was treated with cold saline flushes.
After extensive debulking we were able to advance the bronchoscope into the lingula were some purulent secretions were seen and performed mini BAL.
The tumor however extended into the subsegments of the lingula and deemed likely not salvageable with endobronchial treatment alone.
APC was then used to coagulate the residual superficial layer of oozing tumor.
At the end of the procedure distal left mainstem was only 15% obstructed.
The left upper lobe proper (anterior and apical posterior segments) were completely patent.
The lingula was 80% obstructed and the left lower lobe remained completely obstructed with distal tumor.
Once we were satisfied that there was no active bleeding the rigid bronchoscope was removed and the procedure was completed.
Recommendations:
Transfer to PACU and then home once discharge criteria met.
Will discuss with oncology if biopsy samples obtained during procedure need any specific mutational analysis.
Defer to oncology regarding medical and radiation treatment. 
Will monitor for symptoms or radiographic signs of tumor regrowth and possible need for repeat debulking to salvage left upper lobe."""

# ==========================================
# ENTITY EXTRACTION DEFINITIONS
# ==========================================
# List of entities to extract. 
# Format: (Text_Span, Label)
# Order matters for simple sequential search.
entities_to_find = [
    ("Malignant lung mass", "OBS_LESION"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("left main-stem", "ANAT_AIRWAY"),
    ("Malignant airway obstruction", "OBS_LESION"),
    ("Rigid bronchoscopy", "PROC_METHOD"),
    ("airway debulking", "PROC_ACTION"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("T180 therapeutic video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Right sided bronchial", "ANAT_AIRWAY"),
    ("proximal and mid left mainstem", "ANAT_AIRWAY"),
    ("distal left mainstem", "ANAT_AIRWAY"),
    ("white fungating tumor", "OBS_LESION"),
    ("complete obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("left lower lobe bronchus", "ANAT_AIRWAY"),
    ("complete obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("lingula", "ANAT_LUNG_LOC"),
    ("80% obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("LMA", "DEV_INSTRUMENT"),
    ("12 mm", "MEAS_SIZE"),
    ("ventilating rigid bronchoscope", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("rigid optic", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("cryoextraction", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),
    ("tumor", "OBS_LESION"),
    ("bleeding", "OBS_FINDING"),
    ("tumor", "OBS_LESION"),
    ("bleeding", "OBS_FINDING"),
    ("lingula", "ANAT_LUNG_LOC"),
    ("purulent secretions", "OBS_FINDING"),
    ("mini BAL", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),
    ("lingula", "ANAT_LUNG_LOC"),
    ("APC", "PROC_METHOD"),
    ("tumor", "OBS_LESION"),
    ("distal left mainstem", "ANAT_AIRWAY"),
    ("15% obstructed", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("left upper lobe proper", "ANAT_LUNG_LOC"),
    ("anterior and apical posterior segments", "ANAT_LUNG_LOC"),
    ("lingula", "ANAT_LUNG_LOC"),
    ("80% obstructed", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("completely obstructed", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("tumor", "OBS_LESION"),
    ("bleeding", "OBS_FINDING"),
    ("rigid bronchoscope", "DEV_INSTRUMENT")
]

# ==========================================
# PROCESSING LOGIC
# ==========================================

extracted_entities = []
search_start_index = 0

for span_text, label in entities_to_find:
    start_idx = text.find(span_text, search_start_index)
    
    # If not found from current position, try from beginning (in case of out-of-order manual entry error),
    # but preferably we strictly move forward to handle duplicates correctly.
    if start_idx == -1:
        start_idx = text.find(span_text) # Fallback to search from start if missed
    
    if start_idx != -1:
        end_idx = start_idx + len(span_text)
        extracted_entities.append({
            "start": start_idx,
            "end": end_idx,
            "label": label,
            "text": span_text
        })
        # Update search index to end of current match to find next occurrence
        search_start_index = end_idx
    else:
        print(f"WARNING: Entity '{span_text}' not found in text.")

# ==========================================
# FILE UPDATES
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": text,
    "entities": extracted_entities
}

with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": text
}

with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# 3. Update spans.jsonl
new_spans = []
for ent in extracted_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent["label"],
        "text": ent["text"],
        "start": ent["start"],
        "end": ent["end"]
    }
    new_spans.append(span_entry)

with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in new_spans:
        f.write(json.dumps(span) + "\n")

# 4. Update stats.json
with open(STATS_PATH, "r", encoding="utf-8") as f:
    stats = json.load(f)

stats["total_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for ent in extracted_entities:
    label = ent["label"]
    if label in stats["label_counts"]:
        stats["label_counts"][label] += 1
    else:
        stats["label_counts"][label] = 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# 5. Validation & Logging
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for ent in extracted_entities:
        extracted_text = text[ent["start"]:ent["end"]]
        if extracted_text != ent["text"]:
            log_msg = f"MISMATCH: ID {NOTE_ID}, Label {ent['label']}, Expected '{ent['text']}', Found '{extracted_text}'\n"
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_entities)} entities.")