import json
import re
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_227"
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# RAW TEXT
# ==============================================================================
RAW_TEXT = """NOTE_ID:  note_227 SOURCE_FILE: note_227.txt PREOPERATIVE DIAGNOSIS: Lung cancer with tumor obstruction of left lower lobe
POSTOPERATIVE DIAGNOSIS: 
1.	tumor obstruction of the left lower lobe 
PROCEDURE PERFORMED: Rigid bronchoscopy with tumor debulking and Aero tracheobronchial stent placement
INDICATIONS: Tumor obstruction of left lower lobe  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient’s family acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite.
Following anesthetic induction the endotracheal tube was removed and a 12 mm ventilating rigid bronchoscope was inserted and easily passed into the airway and advanced to the distal trachea and then attached to the jet ventilator.
The flexible bronchoscope was then advanced through the rigid bronchoscope into the airway.
On initial bronchoscopic inspection the trachea, and right lung appeared normal without evidence of endobronchial disease.
The left mainstem also appeared normal. At the left of the LC2 carina (bifurcation between left upper and left lower lobe) the left upper lobe stump from previous lobectomy appeared intact.
The left lower lobe was completely obstructed with tumor. Forceps biopsy was performed of the visible endobronchial tumor and samples were placed in formalin.
Next the Corecath electrocautery suction device was used to dubulk the tumor followed by cryotherapy for removal of retained tumor.
We were able to achieve approximately 80% luminal re-cannulation. Mild tumor infiltration was present in the airway wall until just proximal to the takeoff of the anterior-medial segment of the left lower lobe and distal to that the airways were un-effected.
Given that the patient has had tumor progression despite chemotherapy we felt that airway stent placement was warranted to preserve the lower lobe and prevent regrowth of tumor (barrier effect) with the understanding that this would “jail” the superior segment of the lower lobe and we would essentially sacrifice one segment to preserve the rest of the lobe.
At this point we measured the length of the obstruction and inserted a Jagwire through the flexible bronchoscope past the lesion and using fluoroscopy marked the proximal and distal edges of the obstructed bronchus intermedius with radiopaque markers (paper clips) taped to the patient’s chest wall.
The flexible bronchoscope was removed and a Ultraflex 30mm x 10mm stent was advanced over the guidewire and positioned for an appointment based on the external markers under fluoroscopic observation.
The stent was deployed however slightly too proximal and subsequently was removed using forceps.
The jagwire was re-inserted and using a similar technique an Aero 30mm x 12mm fully covered self-expandable metallic stent loading device was advanced over the guidewire and positioned for an appointment based on the external markers under fluoroscopic observation.
The stent was deployed without difficulty and the flexible bronchoscope was then re-inserted through the rigid bronchoscope and the stent was observed to be well-seated in the left lower lobe and distal mainstem with the distal tip just proximal to the basilar segments of the lower lobe.
Once we were satisfied that no further intervention was required the rigid bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
A few minutes later while anesthesia was bagging the patient as she emerged she became difficult to ventilate and hypoxic.
An LMA was inserted but she could still not ventilate and anesthesia then inserted an endotracheal tube after which ventilation was restored and hypoxia resolved.
It was felt this episode was caused by acute laryngospasm.
We then inserted a flexible bronchoscope through the ETT to inspect the airways and reposition the tube proximal to the carina (was right mainstem intubated. The stent appeared in-place without issues. The patient was then transferred to the ICU for observation with plan to extubate later today. 
Recommendations:
-	Transfer patient to the ICU
-	Post-procedure x-ray
-	Attempt extubation when deemed appropriate by ICU 
-	Await path on biopsy specimens 
-	Start 3% saline nebs 3cc combined with 2cc albuterol 3 times daily for stent maintenance. 
-	Ensure supplemental oxygen is humidified 
-	Please arrange for patient to have nebulizer at home for continued hypertonic saline nebs post-discharge."""

# ==============================================================================
# ENTITY EXTRACTION
# ==============================================================================
# Defined Entities based on Label_guide_UPDATED.csv
# Order matches appearance in text to facilitate linear search
entities_to_find = [
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("Rigid bronchoscopy", "PROC_METHOD"),
    ("tumor debulking", "PROC_ACTION"),
    ("Aero", "DEV_STENT_MATERIAL"),
    ("tracheobronchial stent", "DEV_STENT"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("endotracheal tube", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("right lung", "ANAT_LUNG_LOC"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("LC2 carina", "ANAT_AIRWAY"),
    ("left upper", "ANAT_LUNG_LOC"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("completely obstructed", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("Forceps", "DEV_INSTRUMENT"),
    ("biopsy", "PROC_ACTION"),
    ("Corecath electrocautery suction device", "DEV_INSTRUMENT"),
    ("dubulk", "PROC_ACTION"), # Note: Typo in original text 'dubulk' preserved
    ("cryotherapy", "PROC_ACTION"),
    ("80% luminal re-cannulation", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("anterior-medial segment", "ANAT_LUNG_LOC"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("airway stent", "DEV_STENT"),
    ("lower lobe", "ANAT_LUNG_LOC"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("lower lobe", "ANAT_LUNG_LOC"),
    ("Jagwire", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("Ultraflex", "DEV_STENT_MATERIAL"),
    ("30mm x 10mm", "DEV_STENT_SIZE"),
    ("stent", "DEV_STENT"),
    ("forceps", "DEV_INSTRUMENT"),
    ("jagwire", "DEV_INSTRUMENT"),
    ("Aero", "DEV_STENT_MATERIAL"),
    ("30mm x 12mm", "DEV_STENT_SIZE"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("distal mainstem", "ANAT_AIRWAY"),
    ("basilar segments", "ANAT_LUNG_LOC"),
    ("lower lobe", "ANAT_LUNG_LOC"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("endotracheal tube", "DEV_INSTRUMENT"),
    ("acute laryngospasm", "OUTCOME_COMPLICATION"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("ETT", "DEV_INSTRUMENT"),
    ("carina", "ANAT_AIRWAY"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("3% saline", "MEDICATION"),
    ("albuterol", "MEDICATION")
]

extracted_entities = []
search_start_index = 0

for text_span, label in entities_to_find:
    start = RAW_TEXT.find(text_span, search_start_index)
    if start == -1:
        print(f"WARNING: Could not find '{text_span}' after index {search_start_index}")
        continue
    
    end = start + len(text_span)
    extracted_entities.append({
        "span_id": f"{label}_{start}",
        "note_id": NOTE_ID,
        "label": label,
        "text": text_span,
        "start": start,
        "end": end
    })
    search_start_index = start + 1  # Advance index to handle duplicates

# ==============================================================================
# FILE UPDATES
# ==============================================================================

# 1. Update ner_dataset_all.jsonl
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    json_line = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in extracted_entities]
    }
    f.write(json.dumps(json_line) + "\n")

# 2. Update notes.jsonl
with open(NOTES_PATH, "a", encoding="utf-8") as f:
    json_line = {"id": NOTE_ID, "text": RAW_TEXT}
    f.write(json.dumps(json_line) + "\n")

# 3. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for entity in extracted_entities:
        f.write(json.dumps(entity) + "\n")

# 4. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
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

# 5. Validation Log
with open(LOG_PATH, "a", encoding="utf-8") as f:
    for entity in extracted_entities:
        original_slice = RAW_TEXT[entity["start"]:entity["end"]]
        if original_slice != entity["text"]:
            log_entry = f"[{datetime.datetime.now()}] MISMATCH: {NOTE_ID} - Span '{entity['text']}' != Text '{original_slice}' at {entity['start']}:{entity['end']}\n"
            f.write(log_entry)

print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_entities)} entities.")