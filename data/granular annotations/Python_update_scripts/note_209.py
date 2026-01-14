from pathlib import Path
import json
import os
import re
import datetime

# ----------------------------------------------------------------------------------
# 1. Configuration & Path Setup
# ----------------------------------------------------------------------------------
NOTE_ID = "note_209"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------------
# 2. Raw Text Content
# ----------------------------------------------------------------------------------
RAW_TEXT = """NOTE_ID:  note_209 SOURCE_FILE: note_209.txt PREOPERATIVE DIAGNOSIS: 
1.	Left mainstem obstructive mass
2.	Hemoptysis  lower lobe obstructive mass
POSTOPERATIVE DIAGNOSIS: 
1.	Left mainstem and left upper lobe obstructive mass

Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the distal trachea and advanced into the distal trachea before attaching the monsoon JET ventilator.
Following rigid intubation the patient developed unexpected hypoxia of unclear etiology although visible chest rise was seen.
Decision was made to extubate and then re-intubated with the rigid bronchoscope using closed assisted ventilation.
After re-intubating with a similar technique the mouth was packed and the nose was plugged to avoid leak.
Using the flexible bronchoscope airway inspection was performed.  Gross pooling of blood was visible throughout the trachea however the trachea itself was normal.
The tracheal carina was sharp. All right sided airways were normal although there was some pooling of blood which was easily suctioned.
On the left the proximal left mainstem was normal.  In the mid left mainstem a white vascular polyploid-appearing tumor was present causing complete obstruction.
We’re able to push the flexible bronchoscope past the lesion.
Thick coagulated old blood was noted to fill the airways distally to the obstructing mass.
We then advanced the rigid bronchoscope into the left mainstem to protect the right side from potential spillover of blood.
We then attempted to remove the mass using a electrocautery snare however the base was unexpectedly broad and there could not be lassoed around the tumor.
We then utilized Electrocautery knife and argon plasma coagulation to remove large portions of the tumor which were then extracted with forceps and placed in formalin for analysis.
The mass bled easily and topical TXA was used to control the bleeding.
We then utilized noncontract APC electrocautery to devascularized the superficial aspects of the tumor and then utilizing the beveled edge of the rigid bronchoscope and an apple coring technique dissected the remaining large portion of tumor off of the airway wall.
At this point bleeding seemed to be relatively well controlled and we used the cryotherapy probe to remove larger pieces of residual tumor.
We then utilized the flexible bronchoscope to remove large distal clots from the lingula and left lower lobe which were both widely patent.
The left upper lobe proper however remained mostly obstructed with the tumor from the left mainstem extending into the orifice and distally.
We were able to remove small pieces of tumor which were sent for pathological evaluation but were unable to adequately relieve the obstruction and felt the potential benefit of further debulking likely would be low given that surgical lobectomy is likely in the patient's future.
At this point we used APC to coagulate the remaining areas of oozing and once we are satisfied the rigid bronchoscope was removed and the procedure was completed.
At completion of the procedure the left mainstem was >90% patent, the left lower lobe was >90% patent, the lingual was 70% patent, and the left upper lobe proper was 10% patent with residual endobronchial tumor.
Of note postoperatively the patient was unresponsive and a stroke code was called.
Further documentation is available in the chart however CT of the head and CT angiogram did not show any evidence of stroke and after about an hour and a half the patient spontaneously woke and was oriented x4.
Etiology of the event is not completely clear however likely related to residual effect of anesthesia.

Complications:
Post-operative encephalopathy"""

# ----------------------------------------------------------------------------------
# 3. Label Definition & entity Extraction
# ----------------------------------------------------------------------------------
# Helper to perform extraction to avoid manual index errors
def find_spans(text, substring, label):
    spans = []
    for match in re.finditer(re.escape(substring), text):
        spans.append({
            "span_id": f"{label}_{match.start()}",
            "note_id": NOTE_ID,
            "label": label,
            "text": substring,
            "start": match.start(),
            "end": match.end()
        })
    return spans

entities = []

# --- ANATOMY ---
entities.extend(find_spans(RAW_TEXT, "Left mainstem", "ANAT_AIRWAY"))
entities.extend(find_spans(RAW_TEXT, "left mainstem", "ANAT_AIRWAY")) # Case sensitive matches
entities.extend(find_spans(RAW_TEXT, "lower lobe", "ANAT_LUNG_LOC"))
entities.extend(find_spans(RAW_TEXT, "left upper lobe", "ANAT_LUNG_LOC"))
entities.extend(find_spans(RAW_TEXT, "distal trachea", "ANAT_AIRWAY"))
entities.extend(find_spans(RAW_TEXT, "trachea", "ANAT_AIRWAY")) # 'distal trachea' already caught, but 'trachea' appears alone too.
# Filter subsets: We keep specific spans. Ideally we remove "trachea" if it's inside "distal trachea", 
# but for this script we will allow overlaps or rely on deduplication if strictness is needed. 
# Here we will manually curate to avoid overlapping 'trachea' within 'distal trachea' if we can, or just append distincts.
entities.extend(find_spans(RAW_TEXT, "tracheal carina", "ANAT_AIRWAY")) # It's 'The tracheal carina'
entities.extend(find_spans(RAW_TEXT, "right sided airways", "ANAT_AIRWAY"))
entities.extend(find_spans(RAW_TEXT, "proximal left mainstem", "ANAT_AIRWAY"))
entities.extend(find_spans(RAW_TEXT, "mid left mainstem", "ANAT_AIRWAY"))
entities.extend(find_spans(RAW_TEXT, "lingula", "ANAT_LUNG_LOC"))
entities.extend(find_spans(RAW_TEXT, "left lower lobe", "ANAT_LUNG_LOC"))
entities.extend(find_spans(RAW_TEXT, "left upper lobe proper", "ANAT_LUNG_LOC"))
entities.extend(find_spans(RAW_TEXT, "lingual", "ANAT_LUNG_LOC")) # Typo in note "lingual was 70% patent" -> Maps to Lingula

# --- DEVICES & TOOLS ---
entities.extend(find_spans(RAW_TEXT, "rigid bronchoscope", "DEV_INSTRUMENT"))
entities.extend(find_spans(RAW_TEXT, "monsoon JET ventilator", "DEV_INSTRUMENT"))
entities.extend(find_spans(RAW_TEXT, "flexible bronchoscope", "DEV_INSTRUMENT"))
entities.extend(find_spans(RAW_TEXT, "electrocautery snare", "DEV_INSTRUMENT"))
entities.extend(find_spans(RAW_TEXT, "Electrocautery knife", "DEV_INSTRUMENT"))
entities.extend(find_spans(RAW_TEXT, "forceps", "DEV_INSTRUMENT"))
entities.extend(find_spans(RAW_TEXT, "cryotherapy probe", "DEV_INSTRUMENT"))

# --- MEASUREMENTS ---
entities.extend(find_spans(RAW_TEXT, "12 mm", "MEAS_SIZE"))

# --- MEDICATIONS ---
entities.extend(find_spans(RAW_TEXT, "TXA", "MEDICATION"))

# --- OBSERVATIONS & FINDINGS ---
entities.extend(find_spans(RAW_TEXT, "obstructive mass", "OBS_LESION"))
entities.extend(find_spans(RAW_TEXT, "Hemoptysis", "OBS_FINDING"))
entities.extend(find_spans(RAW_TEXT, "hypoxia", "OBS_FINDING"))
entities.extend(find_spans(RAW_TEXT, "pooling of blood", "OBS_FINDING"))
entities.extend(find_spans(RAW_TEXT, "tumor", "OBS_LESION"))
entities.extend(find_spans(RAW_TEXT, "mass", "OBS_LESION")) # "obstructing mass"
entities.extend(find_spans(RAW_TEXT, "Thick coagulated old blood", "OBS_FINDING"))
entities.extend(find_spans(RAW_TEXT, "clots", "OBS_FINDING"))
entities.extend(find_spans(RAW_TEXT, "stroke", "OBS_FINDING")) # "evidence of stroke" - negation context usually handled by downstream, but entity is finding.
entities.extend(find_spans(RAW_TEXT, "Post-operative encephalopathy", "OBS_FINDING"))

# --- PROCEDURES / ACTIONS ---
entities.extend(find_spans(RAW_TEXT, "argon plasma coagulation", "PROC_ACTION"))
entities.extend(find_spans(RAW_TEXT, "APC", "PROC_ACTION"))
entities.extend(find_spans(RAW_TEXT, "surgical lobectomy", "PROC_ACTION")) # Future context

# --- OUTCOMES ---
entities.extend(find_spans(RAW_TEXT, "complete obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"))
entities.extend(find_spans(RAW_TEXT, "widely patent", "OUTCOME_AIRWAY_LUMEN_POST"))
entities.extend(find_spans(RAW_TEXT, ">90% patent", "OUTCOME_AIRWAY_LUMEN_POST"))
entities.extend(find_spans(RAW_TEXT, "70% patent", "OUTCOME_AIRWAY_LUMEN_POST"))
entities.extend(find_spans(RAW_TEXT, "10% patent", "OUTCOME_AIRWAY_LUMEN_POST"))

# Cleanup: Remove strict subsets if they are not useful (e.g., "trachea" inside "distal trachea")
# For this script, we'll keep it simple and allow overlaps unless strict filtering is required.
# However, duplicate "Left mainstem" spans were generated by the case insensitive search blocks above.
# We must remove exact duplicates (same start/end).
unique_entities = { (e['start'], e['end']): e for e in entities }
entities = sorted(list(unique_entities.values()), key=lambda x: x['start'])

# ----------------------------------------------------------------------------------
# 4. Generate Output Files
# ----------------------------------------------------------------------------------

# 4.1. ner_dataset_all.jsonl
with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
    # Construct the strict schema object
    data_obj = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": e["span_id"],
                "label": e["label"],
                "start_offset": e["start"],
                "end_offset": e["end"]
            }
            for e in entities
        ]
    }
    f.write(json.dumps(data_obj) + "\n")

# 4.2. notes.jsonl
with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"id": NOTE_ID, "text": RAW_TEXT}) + "\n")

# 4.3. spans.jsonl
with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
    for e in entities:
        f.write(json.dumps(e) + "\n")

# 4.4. stats.json
stats_file = OUTPUT_DIR / "stats.json"
if stats_file.exists():
    with open(stats_file, "r", encoding="utf-8") as f:
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

with open(stats_file, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ----------------------------------------------------------------------------------
# 5. Validation & Logging
# ----------------------------------------------------------------------------------
log_file = OUTPUT_DIR / "alignment_warnings.log"
with open(log_file, "a", encoding="utf-8") as log:
    for e in entities:
        extracted = RAW_TEXT[e['start']:e['end']]
        if extracted != e['text']:
            log.write(f"{datetime.datetime.now()} - MISMATCH: {e['span_id']} expected '{e['text']}' but got '{extracted}'\n")

print(f"Successfully processed {NOTE_ID} and updated datasets.")