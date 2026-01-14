import json
import os
import datetime
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. Configuration & Setup
# ------------------------------------------------------------------------------
NOTE_ID = "note_244"
RAW_TEXT = """NOTE_ID:  note_244 SOURCE_FILE: note_244.txt PREOPERATIVE DIAGNOSIS: Endotracheal tumor 
POSTOPERATIVE DIAGNOSIS:  Endotracheal tumor s/p debulking 
PROCEDURE PERFORMED: 
1.         Rigid bronchoscopy with endoluminal tumor ablation(CPT 31641)
INDICATIONS: Tracheal Obstruction  
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives and paralytics the flexible bronchoscope was inserted through the LMA and into the pharynx.
We then advanced the bronchoscope into the subglottic space. Approximately 2.5 cm distal to the vocal cords There were 3 polypoid lesions at the same level blocking about 90% of the airway during exhalation which moved in a ball valve fashion with inhalation resulting in about 50% obstruction of the airway.
Additionally there were multiple small polypoid (> 50) lesions surrounding distal to the lesion originating from all parts of the airway (Anterior trachea, posterior trachea, lateral trachea) which terminated about 1cm proximal to the main carina.
The right sided and left sided airways to at least the first sub-segments were uninvolved with no evidence of endobronchial tumor or extrinsic obstruction.
The flexible bronchoscope and LMA were removed and a 10mm non-ventilating rigid tracheoscope was subsequently inserted into the proximal trachea just proximal to the tumor and connected to ventilator.
The T190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and the electrocautery snare was used to transect the large polypoid lesions beginning with the 3 proximal obstructive lesions and the lesions once free from the wall were easily removed from the airway with suction and collected for pathological assessment.
After these lesions were removed about 10 other lesions in the airway which were anatomically amenable to snare were removed in the same fashion.
We then used APC to paint and shave the remaining tumor area on the posterior and lateral trachea walls until we were satisfied that we had achieved adequate luminal recanalization.
At the end of the procedure the trachea was approximately 90% open in comparison to unaffected areas.
The rigid bronchoscope was then removed, and the procedure was completed. There were no complications.
Of note we considered airway stent placement as a barrier effect  as the lesions regrew very quickly (< 3 months) after the previous bronchoscopic debulking procedure however in our discussions with the patient prior to the procedure he expressed reluctance to have stent placed due to possible cough associated with the stent and the fact that he only restarted chemotherapy 2 weeks ago.
I suspect that these lesions will recur unless he has a profound response to systemic treatment and possible radiation and if I need to debulk again I will strongly advocate for placement of a covered tracheal stent.
Recommendations: 
•	Transfer patient back to ward room 
•	Await final pathology results  
•	Will need to speak with oncology regarding other treatment options which might include PDT or brachytherapy."""

# Define target paths
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ------------------------------------------------------------------------------
# 2. Define Entities
# ------------------------------------------------------------------------------
# List of (Label, Text_Snippet) tuples.
# Order matches the text flow to ensure correct index tracking.
entities_to_extract = [
    ("OBS_LESION", "Endotracheal tumor"),
    ("OBS_LESION", "Endotracheal tumor"), # Second occurrence
    ("CTX_HISTORICAL", "s/p"),
    ("PROC_ACTION", "debulking"),
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("PROC_ACTION", "endoluminal tumor ablation"),
    ("ANAT_AIRWAY", "Tracheal"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("ANAT_AIRWAY", "pharynx"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("MEAS_SIZE", "2.5 cm"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("MEAS_COUNT", "3"),
    ("OBS_LESION", "polypoid lesions"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "blocking about 90% of the airway"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "50% obstruction"),
    ("MEAS_COUNT", "> 50"),
    ("OBS_LESION", "lesions"),
    ("ANAT_AIRWAY", "Anterior trachea"),
    ("ANAT_AIRWAY", "posterior trachea"),
    ("ANAT_AIRWAY", "lateral trachea"),
    ("MEAS_SIZE", "1cm"),
    ("ANAT_AIRWAY", "main carina"),
    ("ANAT_AIRWAY", "right sided and left sided airways"),
    ("OBS_LESION", "endobronchial tumor"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"), # Second occurrence
    ("DEV_INSTRUMENT", "LMA"), # Second occurrence
    ("MEAS_SIZE", "10mm"),
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "proximal trachea"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "T190 Olympus flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "electrocautery snare"),
    ("PROC_ACTION", "transect"),
    ("OBS_LESION", "large polypoid lesions"),
    ("MEAS_COUNT", "3"), # Second occurrence (3 proximal obstructive lesions)
    ("OBS_LESION", "proximal obstructive lesions"),
    ("OBS_LESION", "lesions"), # "lesions once free"
    ("PROC_ACTION", "removed"),
    ("PROC_ACTION", "suction"),
    ("MEAS_COUNT", "10"),
    ("OBS_LESION", "lesions"), # "10 other lesions"
    ("DEV_INSTRUMENT", "snare"),
    ("PROC_ACTION", "removed"), # Second occurrence
    ("PROC_METHOD", "APC"),
    ("PROC_ACTION", "paint"),
    ("PROC_ACTION", "shave"),
    ("OBS_LESION", "tumor"), # "remaining tumor area"
    ("ANAT_AIRWAY", "posterior and lateral trachea walls"),
    ("ANAT_AIRWAY", "trachea"), # "trachea was approximately..."
    ("OUTCOME_AIRWAY_LUMEN_POST", "approximately 90% open"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # Second occurrence
    ("OUTCOME_COMPLICATION", "no complications"), # Fixed casing
    ("PROC_ACTION", "airway stent placement"),
    ("CTX_TIME", "< 3 months"),
    ("CTX_HISTORICAL", "previous"),
    ("PROC_ACTION", "bronchoscopic debulking"),
    ("CTX_TIME", "2 weeks ago"),
    ("OBS_LESION", "lesions"), # "lesions will recur"
    ("PROC_ACTION", "debulk"),
    ("DEV_STENT", "covered tracheal stent"),
    ("PROC_METHOD", "PDT"),
    ("PROC_METHOD", "brachytherapy")
]

# ------------------------------------------------------------------------------
# 3. Extraction Logic
# ------------------------------------------------------------------------------
extracted_spans = []
cursor = 0

for label, text in entities_to_extract:
    # Find match starting from current cursor to ensure correct order
    start_index = RAW_TEXT.find(text, cursor)
    
    if start_index == -1:
        print(f"WARNING: Could not find '{text}' after index {cursor}")
        continue

    end_index = start_index + len(text)
    
    span = {
        "span_id": f"{label}_{start_index}",
        "note_id": NOTE_ID,
        "label": label,
        "text": text,
        "start": start_index,
        "end": end_index
    }
    extracted_spans.append(span)
    
    # Validation (Double check)
    if RAW_TEXT[start_index:end_index] != text:
        with open(LOG_PATH, "a") as f:
            f.write(f"Mismatch: {NOTE_ID} | {label} | Expected: {text} | Found: {RAW_TEXT[start_index:end_index]}\n")
    
    # Update cursor
    cursor = start_index + 1 

# ------------------------------------------------------------------------------
# 4. File Updates
# ------------------------------------------------------------------------------

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
}
with open(NER_DATASET_PATH, "a") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
with open(NOTES_PATH, "a") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
with open(SPANS_PATH, "a") as f:
    for span in extracted_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, "r") as f:
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
stats["total_spans_raw"] += len(extracted_spans)
stats["total_spans_valid"] += len(extracted_spans)

for span in extracted_spans:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w") as f:
    json.dump(stats, f, indent=2)

print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_spans)} entities.")