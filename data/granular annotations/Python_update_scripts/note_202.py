import json
import os
import datetime
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_202"
RAW_TEXT = """NOTE_ID:  note_202 SOURCE_FILE: note_202.txt PREOPERATIVE DIAGNOSIS: 
1.	Lung cancer with tumor obstruction
2.	Right Pleural effusion
POSTOPERATIVE DIAGNOSIS: 
1.	tumor infiltration within the bronchus intermedius RUL and RLL
2.	Pleural effusion
PROCEDURE PERFORMED: 
1.	Rigid bronchoscopy with tumor debulking and Aero tracheobronchial stent placement
2.	Right sided tunneled indwelling catheter insertion.
INDICATIONS: Malignant Airway Obstruction  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a laryngeal mask airway was inserted.
Topical anesthesia was then applied to the upper airway and the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
On initial bronchoscopic inspection the trachea, and left lung appeared normal without evidence of endobronchial disease.
The right mainstem was normal. At the level of the RUL submucosal tumor infiltration was noted wxtending into the right upper lobe causin about 70% obstruction.
The upper lobe subsegments could be visualize but tumor infiltration extended beyond view.
Submucosal tumor infiltration was seen extending through the bronchus intermedius into the proximal right lower lobe.
The RML was nearly completely obstructed. The superior segment had tumor infiltration extending into the subsegmental airways.
The basilar segments of the RLL were uneffaced.  The LMA was removed and a 12 mm ventilating rigid bronchoscope was inserted and easily passed into the airway and advanced to the distal trachea and then attached to the jet ventilator.
The rigid bronchsocpe was attached to the JET ventilator. Tumor debulking was performed with APC and flexible forceps using the therapeutic flexible bronchoscope and the beveled tip of the rigid bronchoscope.
Using a Fogarty balloon we attempted to remove tumor from the right upper lobe , RML and sup segment of RLL but lumens remained obstructed due to extent of disease..  At this point we measured the length of the obstruction and inserted a Jagwire through the flexible bronchoscope.
The flexible bronchoscope was removed and an Aero 30mm x 10mm fully covered self-expandable metallic stent loading device was advanced over the guidewire with direct visualization side by side with a ultrathin disposable bronchoscope (Boston Scientific Model B) and the stent was positioned with the proximal end just distal to the RUL.
The stent was deployed without difficulty and after minor adjustment  the stent was observed to be well-seated in the bronchus intermedius allowing aeration of the right upper lobe.
The non-functional RML and superior segments were occluded to prevent distal tumor ingrowth and preserve the right lower lobe basilar segments.
Once we were satisfied that no further intervention was required the rigid bronchoscope was removed and LMA was reinserted.
At this point we prepped the patient for indwelling pleural catheter insertion.
Bedside ultrasound was used to localize an optimal window for tube placement.
The site was identified in the right 4th intercostal space latterally.
The site was marked, prepped and draped in usual sterile fashion.
1% Lidocaine was used to anesthetize the skin down to the rib and along the proposed insertion path for the tube.
A 20 gauge Yueh-centesis needle with syringe attached was inserted into the pleural space with aspiration of air / fluid to verify placement.
The needle was removed and the catheter left in place.
A guide wire was advanced into the pleural space through the catheter and the catheter was then withdrawn.
A 1 cm insision was made over the wire and a  separate skin site was identified ~5cm anterior to the guidewire insertion site and lidocaine was injected for local analgesia and a <0.5 cm incision was then performed.
A subcutaneous tract was then established to the guidewire insertion site with the provided blunt tunneler.
The Pleurx catheter was attached to the tunneler and pulled through the subcutaneous tract, followed by dilatation of the pleural access tract with the 16 fr peel away sheath via seldinger technique.
The Pleurx catheter was then inserted through the 16 fr. peel away sheath.
Both incisions were closed with subcuticular 0 silk suture. The area was then dressed.
The catheter was subsequently connected to the IPC bottle and 300cc of serous fluid was removed.
The catheter tip was then capped and the Pleurx was dressed and covered with a translucent dressing.
The patient tolerated the procedural well.
Post-procedure chest radiograph showed 
Complications: No immediate complications"""

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
# ENTITY EXTRACTION
# ==========================================
# Helper to find exact offsets. 
# Usage: find_offsets(substring, start_search_index=0)
def find_offsets(text, substring, start_index=0):
    start = text.find(substring, start_index)
    if start == -1:
        return None
    return start, start + len(substring)

# List of target entities to extract based on the text and Label_guide_UPDATED.csv
# Format: (Text_Snippet, Label)
# Note: Order matters for sequential search to avoid finding the wrong instance of repeated terms.
targets = [
    ("Lung cancer", "OBS_LESION"),
    ("tumor obstruction", "OBS_LESION"),
    ("Right", "LATERALITY"),
    ("Pleural effusion", "OBS_LESION"),
    ("tumor infiltration", "OBS_LESION"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("RUL", "ANAT_LUNG_LOC"),
    ("RLL", "ANAT_LUNG_LOC"),
    ("Pleural effusion", "OBS_LESION"),
    ("Rigid bronchoscopy", "PROC_METHOD"),
    ("tumor debulking", "PROC_ACTION"),
    ("Aero", "DEV_STENT"), # Brand
    ("tracheobronchial stent", "DEV_STENT"),
    ("Right", "LATERALITY"),
    ("tunneled indwelling catheter", "DEV_CATHETER"),
    ("Malignant Airway Obstruction", "OBS_LESION"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("Topical anesthesia", "MEDICATION"), # Or method, usually meds like lido
    ("T190 video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("left", "LATERALITY"),
    ("lung", "ANAT_LUNG_LOC"),
    ("endobronchial disease", "OBS_LESION"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("RUL", "ANAT_LUNG_LOC"),
    ("submucosal tumor infiltration", "OBS_LESION"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("70% obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("upper lobe", "ANAT_LUNG_LOC"),
    ("tumor infiltration", "OBS_LESION"),
    ("Submucosal tumor infiltration", "OBS_LESION"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("proximal right lower lobe", "ANAT_LUNG_LOC"),
    ("RML", "ANAT_LUNG_LOC"),
    ("obstructed", "OBS_LESION"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("tumor infiltration", "OBS_LESION"),
    ("basilar segments", "ANAT_LUNG_LOC"),
    ("RLL", "ANAT_LUNG_LOC"),
    ("LMA", "DEV_INSTRUMENT"),
    ("12 mm", "MEAS_SIZE"),
    ("ventilating rigid bronchoscope", "DEV_INSTRUMENT"),
    ("distal trachea", "ANAT_AIRWAY"),
    ("jet ventilator", "DEV_INSTRUMENT"),
    ("rigid bronchsocpe", "DEV_INSTRUMENT"), # Typo in note preserved
    ("JET ventilator", "DEV_INSTRUMENT"),
    ("Tumor debulking", "PROC_ACTION"),
    ("APC", "DEV_INSTRUMENT"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("therapeutic flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("Fogarty balloon", "DEV_INSTRUMENT"),
    ("tumor", "OBS_LESION"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("RML", "ANAT_LUNG_LOC"),
    ("sup segment", "ANAT_LUNG_LOC"),
    ("RLL", "ANAT_LUNG_LOC"),
    ("obstructed", "OBS_LESION"),
    ("Jagwire", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("Aero", "DEV_STENT"),
    ("30mm x 10mm", "DEV_STENT_SIZE"),
    ("fully covered self-expandable metallic stent", "DEV_STENT_MATERIAL"),
    ("ultrathin disposable bronchoscope", "DEV_INSTRUMENT"),
    ("Boston Scientific Model B", "DEV_INSTRUMENT"), # Specific model
    ("stent", "DEV_STENT"),
    ("RUL", "ANAT_LUNG_LOC"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("RML", "ANAT_LUNG_LOC"),
    ("superior segments", "ANAT_LUNG_LOC"),
    ("tumor ingrowth", "OBS_LESION"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("basilar segments", "ANAT_LUNG_LOC"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("indwelling pleural catheter", "DEV_CATHETER"),
    ("Bedside ultrasound", "PROC_METHOD"),
    ("right", "LATERALITY"),
    ("4th intercostal space", "ANAT_PLEURA"), # Chest wall boundary
    ("1% Lidocaine", "MEDICATION"),
    ("20 gauge", "DEV_NEEDLE"),
    ("Yueh-centesis needle", "DEV_NEEDLE"),
    ("pleural space", "ANAT_PLEURA"),
    ("needle", "DEV_NEEDLE"),
    ("catheter", "DEV_CATHETER"),
    ("guide wire", "DEV_INSTRUMENT"),
    ("pleural space", "ANAT_PLEURA"),
    ("catheter", "DEV_CATHETER"),
    ("catheter", "DEV_CATHETER"),
    ("1 cm", "MEAS_SIZE"),
    ("wire", "DEV_INSTRUMENT"),
    ("lidocaine", "MEDICATION"),
    ("<0.5 cm", "MEAS_SIZE"),
    ("blunt tunneler", "DEV_INSTRUMENT"),
    ("Pleurx catheter", "DEV_CATHETER"),
    ("tunneler", "DEV_INSTRUMENT"),
    ("16 fr", "MEAS_PLEURAL_DRAIN"), # Dilation size
    ("peel away sheath", "DEV_INSTRUMENT"),
    ("Pleurx catheter", "DEV_CATHETER"),
    ("16 fr.", "MEAS_PLEURAL_DRAIN"),
    ("peel away sheath", "DEV_INSTRUMENT"),
    ("IPC bottle", "DEV_INSTRUMENT"),
    ("300cc", "MEAS_VOL"),
    ("catheter", "DEV_CATHETER"),
    ("Pleurx", "DEV_CATHETER"),
    ("No immediate complications", "OUTCOME_COMPLICATION")
]

entities = []
cursor = 0

for text, label in targets:
    # Find the text starting from the current cursor to handle duplicates correctly
    match = find_offsets(RAW_TEXT, text, cursor)
    if match:
        start, end = match
        entities.append({
            "start": start,
            "end": end,
            "label": label,
            "text": text
        })
        # Update cursor to avoid overlapping same instance if not nested (strict sequential assumption here for safety)
        # However, some entities might be nested or close. We simply move cursor to 'start + 1' to allow overlaps if valid,
        # but for this list, we generally want to move forward. 
        # To match the sequential reading of the note:
        cursor = start + 1
    else:
        # Log missing entity for debugging
        print(f"Warning: Could not find '{text}' after index {cursor}")

# ==========================================
# FILE GENERATION & UPDATES
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[e["start"], e["end"], e["label"]] for e in entities]
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
    for e in entities:
        span_entry = {
            "span_id": f"{e['label']}_{e['start']}",
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        }
        f.write(json.dumps(span_entry) + "\n")

# 4. Update stats.json
if STATS_PATH.exists():
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
stats["total_files"] += 1 # Assuming 1 note per file for this script
stats["total_spans_raw"] += len(entities)
stats["total_spans_valid"] += len(entities)

for e in entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# 5. Validation Logging
with open(LOG_PATH, "a", encoding="utf-8") as log:
    for e in entities:
        extracted = RAW_TEXT[e["start"]:e["end"]]
        if extracted != e["text"]:
            log.write(f"MISMATCH {NOTE_ID}: Expected '{e['text']}' but got '{extracted}' at {e['start']}-{e['end']}\n")

print(f"Successfully processed {NOTE_ID} and updated datasets.")