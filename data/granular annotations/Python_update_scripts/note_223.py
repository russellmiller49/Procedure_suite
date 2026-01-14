import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. CONFIGURATION & PATH SETUP
# ==========================================
NOTE_ID = "note_223"
SCRIPT_DIR = Path(__file__).resolve()
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = SCRIPT_DIR.parents[2] / "ml_training" / "granular_ner"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. RAW TEXT INPUT
# ==========================================
# Exact text from the provided file content
RAW_TEXT = """PROCEDURE PERFORMED: flexible bronchoscopy with electrocautery tissue debulking and balloon dilatation.
INDICATIONS: complete lobar collapse  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
There were red petechiae throughout the tracheal mucosa of unclear etiology. The trachea and right sided airways were otherwise normal.
The left mainstem stent was widely patent without evidence of obstruction in the proximal and mid portions.
There was a small area of abnormal mucosal thickening in the proximal posterior wall which we attempted to biopsy with forceps but specimen was lost during forceps extraction.
At the distal le mainstem there was complete obstruction secondary to circumferential fibrinous scar.
We were able to identify a pin-hole using the thin bronchoscope but could not view distally of bypass with the scope.
A Fogarty balloon was then passed through the hole and inflated and then retracted through the stenosis to gently dilate the airway.
Purulent material was visualized and collected via trap. This was repeated multiple times with varying sized of Fogarty balloons.
The electrocautery knife was then used to make linear incisions within the scar after which serial proximal dilatations were performed with the 6,7,8 Merit phased dilatational balloon.
Continued purulent return indicated intraluminal dilatation. We were eventually able to pass the central obstruction with the therapeutic bronchoscope but distal visualization was limited.
With the P190X thin bronchoscope we were able to visualize free wires from previous left upper lobe resection and stenotic distal airways with associated bronchomalacia and adherent white waxy fibrinous tissue.
While one airway was clearly visualized with distal carinas seen, the anatomy was extremely distorted and the extensive fibrinous material/inflammation made it impossible to confidently confirm that the other associated orifices e were not in a false lumen.
At this point we obtained forceps biopsies from the abnormal tissue and the case was completed with plan to reassess after repeat CT.
Recommendations:
-	CXR in PACU
-	Transfer patient to ward
-	Repeat CT today"""

# ==========================================
# 3. ENTITY EXTRACTION
# ==========================================
# List of (Label, Text_Segment) in order of appearance to ensure correct offset calculation
entities_to_map = [
    ("PROC_METHOD", "flexible bronchoscopy"),
    ("PROC_ACTION", "electrocautery tissue debulking"),
    ("PROC_ACTION", "balloon dilatation"),
    ("OBS_FINDING", "complete lobar collapse"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("OBS_FINDING", "red petechiae"),
    ("ANAT_AIRWAY", "tracheal mucosa"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "right sided airways"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "abnormal mucosal thickening"),
    ("ANAT_AIRWAY", "proximal posterior wall"),
    ("PROC_ACTION", "biopsy"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "forceps"),
    ("ANAT_AIRWAY", "distal le mainstem"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "complete obstruction"),
    ("OBS_FINDING", "circumferential fibrinous scar"),
    ("DEV_INSTRUMENT", "thin bronchoscope"),
    ("DEV_INSTRUMENT", "Fogarty balloon"),
    ("PROC_ACTION", "dilate"),
    ("ANAT_AIRWAY", "airway"),
    ("OBS_FINDING", "Purulent material"),
    ("DEV_INSTRUMENT", "Fogarty balloons"),
    ("DEV_INSTRUMENT", "electrocautery knife"),
    ("PROC_ACTION", "linear incisions"),
    ("OBS_FINDING", "scar"),
    ("PROC_ACTION", "proximal dilatations"),
    ("MEAS_SIZE", "6,7,8"),
    ("DEV_INSTRUMENT", "Merit phased dilatational balloon"),
    ("OBS_FINDING", "purulent return"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("DEV_INSTRUMENT", "P190X thin bronchoscope"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_AIRWAY", "distal airways"),
    ("OBS_FINDING", "bronchomalacia"),
    ("OBS_FINDING", "adherent white waxy fibrinous tissue"),
    ("ANAT_AIRWAY", "airway"),
    ("ANAT_AIRWAY", "distal carinas"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "biopsies")
]

final_entities = []
search_start_index = 0

for label, text in entities_to_map:
    start_idx = RAW_TEXT.find(text, search_start_index)
    if start_idx == -1:
        # Fallback to search from beginning if out of order, though strict order is preferred
        start_idx = RAW_TEXT.find(text)
    
    if start_idx != -1:
        end_idx = start_idx + len(text)
        
        # Verify exact match
        extracted_text = RAW_TEXT[start_idx:end_idx]
        if extracted_text != text:
             with open(LOG_PATH, "a") as log:
                log.write(f"MISMATCH: Expected '{text}' but got '{extracted_text}' at {start_idx}\n")
        
        entity = {
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": extracted_text,
            "start": start_idx,
            "end": end_idx
        }
        final_entities.append(entity)
        # Advance search index to avoid re-matching the same instance
        search_start_index = start_idx + 1
    else:
        with open(LOG_PATH, "a") as log:
            log.write(f"NOT FOUND: '{text}' could not be located in {NOTE_ID}\n")

# ==========================================
# 4. FILE UPDATES
# ==========================================

# A. Append to ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": final_entities
}
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Append to notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# C. Append to spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for ent in final_entities:
        f.write(json.dumps(ent) + "\n")

# D. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    # Fallback initialization if file missing
    stats = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "alignment_warnings": 0,
        "alignment_errors": 0,
        "label_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(final_entities)
stats["total_spans_valid"] += len(final_entities)

for ent in final_entities:
    lbl = ent["label"]
    if lbl in stats["label_counts"]:
        stats["label_counts"][lbl] += 1
    else:
        stats["label_counts"][lbl] = 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")