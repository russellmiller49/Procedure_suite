from pathlib import Path
import json
import os
import datetime

# ==========================================
# CONFIGURATION & PATH SETUP
# ==========================================
NOTE_ID = "note_158"
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
RAW_TEXT = """Procedure Name: 
1.	radial EBUS guided bronchoscopy with TNBA and endobronchial biopsies
Indications: Pulmonary Nodule
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The arytenoids were large with a large and floppy epiglottis. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The carina was sharp.
On the right the patient had an anatomic variant with an accessory airway just distal to the superior segment of the right lower lobe.
The left sided airway anatomy was normal. No evidence of endobronchial disease was seen to at least the first sub-segments.
We then removed the bronchoscope and inserted the P190 slim bronchoscope into the airway.
We attempted to visualize endobronchial disease within the anterior basilar segment of the left lower lobe but could not advance the scope distally enough.
We then inserted the radial ultrasound through the working channel of the bronchoscope and an eccentric view of the kno0wn nodule was obtained.
We then performed peripheral TBNAs of the point of interest. ROSE did not show obvious malignancy.
At this point we removed the slim scope and inserted the UC180F convex probe EBUS bronchoscope through the mouth, and advanced into the tracheobronchial tree.
We attempted to wedge the scope in the lower lobe to potentially visualize the tumor with ultrasound.
We saw an unusual area of soft tissue which did not obviously look like would be expected from the nodule.
Two biopsies were performed using the 22G EBUS-TBNA needle. ROSE however showed only blood.
Finally, fluoroscopy was brought into the room and the T190 therapeutic video bronchoscope was inserted into the airway and based on anatomical knowledge advanced into the left lower lobe and a large sheath catheter with radial ultrasound to the area of known nodule and a concentric view of the lesion was identified with the radial EBUS.
Biopsies were then performed with a variety of instruments to include peripheral needle forceps and brush with fluoroscopic guidance through the sheath.
After adequate samples were obtained the bronchoscope was removed. ROSE did not identify malignancy on preliminary samples.
After suctioning blood and secretions and once we were confident that there was no active bleeding the bronchoscope was removed and the procedure completed.
Following completion of the procedure the patient was noted to have audible upper airway sounds and ventilation was difficult.
And decision was made to convert to endotracheal intubation. Initially this was attempted over the bronchoscope however edema within the structures of the middle laryngeal cavity (above the vocal cords this was unsuccessful. Anesthesia was then able to intubate with the glideslope. The bronchoscope was then inserted through the ETT to confirm positioning 2cm above the carina and to suction secretions. The patient was then transferred to the ICU. 

Complications: Unexpected admission
Estimated Blood Loss: Less than 10 cc.
Post Procedure Diagnosis:
- Flexible bronchoscopy with successful biopsy of left lower lobe pulmonary nodule
- Will transfer to the ICU and attempt extubation later 
today. 
- Await final pathology"""

# ==========================================
# ENTITY EXTRACTION
# ==========================================
# Helper to find exact offsets
def find_offsets(text, search_str, start_search=0):
    start = text.find(search_str, start_search)
    if start == -1:
        return None, None
    return start, start + len(search_str)

entities = []
search_cursor = 0

# Line 2: radial EBUS guided bronchoscopy with TNBA and endobronchial biopsies
s, e = find_offsets(RAW_TEXT, "radial EBUS", search_cursor)
entities.append({"label": "PROC_METHOD", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "bronchoscopy", search_cursor) # In procedure name line
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "TNBA", search_cursor)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "biopsies", search_cursor)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})

# Line 3: Indications
s, e = find_offsets(RAW_TEXT, "Pulmonary Nodule", search_cursor)
entities.append({"label": "OBS_LESION", "start": s, "end": e})

# Line 4: Medications
s, e = find_offsets(RAW_TEXT, "Propofol", search_cursor)
entities.append({"label": "MEDICATION", "start": s, "end": e})

# Line 9: Anesthesia
s, e = find_offsets(RAW_TEXT, "topical anesthesia", search_cursor)
entities.append({"label": "MEDICATION", "start": s, "end": e}) # Broadly fits medication/method, sticking to med context
s, e = find_offsets(RAW_TEXT, "upper airway", search_cursor)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "tracheobronchial tree", search_cursor)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "laryngeal mask airway", search_cursor)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e}) # Device
s, e = find_offsets(RAW_TEXT, "tracheobronchial tree", e) # Second occurrence
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})

# Line 10: Anatomy
s, e = find_offsets(RAW_TEXT, "arytenoids", search_cursor)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "epiglottis", search_cursor)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "vocal cords", search_cursor)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "subglottic space", search_cursor)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})

# Line 11: Trachea
s, e = find_offsets(RAW_TEXT, "Trachea", search_cursor) # Capital T in text: "The trachea" -> "The Trachea"? Text says "The trachea"
# Wait, checking raw text line 6: "The trachea is of normal caliber."
s, e = find_offsets(RAW_TEXT, "trachea", 700) # search roughly after prev
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "carina", s)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})

# Line 12: Anatomic variant
s, e = find_offsets(RAW_TEXT, "superior segment of the right lower lobe", s)
entities.append({"label": "ANAT_LUNG_LOC", "start": s, "end": e})

# Line 13: Left sided
s, e = find_offsets(RAW_TEXT, "left sided airway", s)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})

# Line 15: anterior basilar segment
s, e = find_offsets(RAW_TEXT, "anterior basilar segment of the left lower lobe", s)
entities.append({"label": "ANAT_LUNG_LOC", "start": s, "end": e})

# Line 16: radial ultrasound
s, e = find_offsets(RAW_TEXT, "radial ultrasound", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e}) # "inserted the radial ultrasound" -> implies device
s, e = find_offsets(RAW_TEXT, "nodule", s)
entities.append({"label": "OBS_LESION", "start": s, "end": e})

# Line 17: TBNAs
s, e = find_offsets(RAW_TEXT, "peripheral TBNAs", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "malignancy", s)
entities.append({"label": "OBS_ROSE", "start": s, "end": e})

# Line 18: EBUS bronchoscope
s, e = find_offsets(RAW_TEXT, "tracheobronchial tree", s)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})

# Line 19: wedge
s, e = find_offsets(RAW_TEXT, "lower lobe", s)
entities.append({"label": "ANAT_LUNG_LOC", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "tumor", s)
entities.append({"label": "OBS_LESION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "ultrasound", s)
entities.append({"label": "PROC_METHOD", "start": s, "end": e}) # "with ultrasound" -> Method

# Line 20: soft tissue
# "soft tissue" not strictly in guide as lesion, but "unusual area" is vague. 
# "nodule" again
s, e = find_offsets(RAW_TEXT, "nodule", s)
entities.append({"label": "OBS_LESION", "start": s, "end": e})

# Line 21: Biopsies
s, e = find_offsets(RAW_TEXT, "Two biopsies", s)
# "biopsies" is action
s, e = find_offsets(RAW_TEXT, "biopsies", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "22G", s)
entities.append({"label": "DEV_NEEDLE", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "EBUS-TBNA needle", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "blood", s)
entities.append({"label": "OBS_ROSE", "start": s, "end": e})

# Line 22: Fluoroscopy
s, e = find_offsets(RAW_TEXT, "fluoroscopy", s)
entities.append({"label": "PROC_METHOD", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "left lower lobe", s)
entities.append({"label": "ANAT_LUNG_LOC", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "sheath", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e}) # sheath catheter
s, e = find_offsets(RAW_TEXT, "radial ultrasound", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e}) # "with radial ultrasound" (device context)
s, e = find_offsets(RAW_TEXT, "nodule", s)
entities.append({"label": "OBS_LESION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "lesion", s)
entities.append({"label": "OBS_LESION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "radial EBUS", s)
entities.append({"label": "PROC_METHOD", "start": s, "end": e})

# Line 23: Biopsies
s, e = find_offsets(RAW_TEXT, "Biopsies", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "forceps", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "brush", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "fluoroscopic", s) # "fluoroscopic guidance" -> PROC_METHOD
entities.append({"label": "PROC_METHOD", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "sheath", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e})

# Line 24: ROSE
s, e = find_offsets(RAW_TEXT, "malignancy", s)
entities.append({"label": "OBS_ROSE", "start": s, "end": e})

# Line 25: secretions
s, e = find_offsets(RAW_TEXT, "secretions", s)
entities.append({"label": "OBS_FINDING", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "active bleeding", s)
# "no active bleeding" -> "active bleeding" is the finding/complication context
entities.append({"label": "OBS_FINDING", "start": s, "end": e}) # Using OBS_FINDING for bleeding status

# Line 26: Complications/Findings
s, e = find_offsets(RAW_TEXT, "audible upper airway sounds", s)
entities.append({"label": "OBS_FINDING", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "ventilation was difficult", s) # Symptom/Finding
entities.append({"label": "OBS_FINDING", "start": s, "end": e})

# Line 27: Intubation
s, e = find_offsets(RAW_TEXT, "endotracheal intubation", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "edema", s)
entities.append({"label": "OBS_FINDING", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "middle laryngeal cavity", s)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "vocal cords", s)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "glideslope", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "ETT", s)
entities.append({"label": "DEV_INSTRUMENT", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "carina", s)
entities.append({"label": "ANAT_AIRWAY", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "suction", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "secretions", s)
entities.append({"label": "OBS_FINDING", "start": s, "end": e})

# Estimated Blood Loss
s, e = find_offsets(RAW_TEXT, "Less than 10 cc", s)
entities.append({"label": "MEAS_VOL", "start": s, "end": e})

# Post Procedure Diagnosis
s, e = find_offsets(RAW_TEXT, "Flexible bronchoscopy", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "biopsy", s)
entities.append({"label": "PROC_ACTION", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "left lower lobe", s)
entities.append({"label": "ANAT_LUNG_LOC", "start": s, "end": e})
s, e = find_offsets(RAW_TEXT, "pulmonary nodule", s)
entities.append({"label": "OBS_LESION", "start": s, "end": e})

# Validate Entities
valid_entities = []
for ent in entities:
    if ent['start'] is not None and ent['end'] is not None:
        ent['text'] = RAW_TEXT[ent['start']:ent['end']]
        valid_entities.append(ent)
    else:
        # Should not happen with careful find_offsets logic but good safety
        pass

# ==========================================
# FILE UPDATES
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": valid_entities
}

with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Update spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for ent in valid_entities:
        span_entry = {
            "span_id": f"{ent['label']}_{ent['start']}",
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        f.write(json.dumps(span_entry) + "\n")

# 4. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        try:
            stats = json.load(f)
        except json.JSONDecodeError:
            stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
else:
    stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

stats["total_notes"] += 1
# Assuming 1 note per file for this script context
stats["total_files"] += 1 
stats["total_spans_raw"] += len(valid_entities)
stats["total_spans_valid"] += len(valid_entities)

for ent in valid_entities:
    lbl = ent['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# 5. Validate & Log
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for ent in valid_entities:
        extracted = RAW_TEXT[ent['start']:ent['end']]
        if extracted != ent['text']:
            log_entry = f"[{datetime.datetime.now()}] MISMATCH: ID={NOTE_ID} Label={ent['label']} Expected='{ent['text']}' Found='{extracted}'\n"
            log_file.write(log_entry)

print(f"Successfully processed {NOTE_ID} with {len(valid_entities)} entities.")