import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & PATH SETUP
# ==========================================
NOTE_ID = "note_195"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# The Raw Text from the Input File
RAW_TEXT = """Procedure Name: Pleuroscopy
Indications: Pleural effusion
Medications: Fentanyl 3, versed 75, Lidocaine 30cc 1%
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. The patient was placed on the standard procedural bed in the L lateral decubitus position and sites of compression were well padded.
The pleural entry site was identified by means of the ultrasound.
The patient was sterilely prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual fashion.
The entry sites was infiltrated with a 10mL solution of 1% lidocaine.
Following instillation of subcutaneous lidocaine a 1 cm subcutaneous incision was made and gentle dissection was performed until the pleural space was entered.
An 8 mm disposable primary port was then placed on the left side at the 6th anterior axillary line.
After allowing air entrainment and lung deflation, suction was applied through the port to remove pleural fluid with removal of approximately 700cc of serosanguinous fluid.
The rigid pleuroscopy telescope was then introduced through the trocar and advanced into the pleural space.
There was diffuse pleural studding observed. The pleura was gernerally unremarkable with the execution of a few white and yellow plaques as well as some mild tethering of the right upper lobe to the chest wall.
Biopsies of the abnormal areas in the parietal pleura posteriorly were performed with forceps and sent for histopathology examination with approximately 5 total biopsies taken.
There was brisk but transient bleeding after the initial biopsy ans subsequently protamine was given to completely reverse patients heparin (which was held for the procedure).
The pleuroscopy telescope was then removed and a 15.5 pleural catheter was placed into the pleural space through the primary port with tunneling anteriorly.
PleurX Catheter Placement:

A guide wire was inserted into the site of pleuroscopy entry and the port was removed.
A separate skin site was identified ~5cm inferior to the guidewire insertion site and lidocaine was injected for local analgesia and a <1cm incision was then performed.
A subcutaneous tract was then established to the guidewire insertion site with the provided blunt tunneler.
The Pleurx catheter was attached to the tunneler and pulled through the subcutaneous tract, followed by dilatation of the pleural access tract with the 16 fr peel away sheath via seldinger technique.
The Pleurx catheter was then inserted through the 16 fr. peel away sheath.
Both incisions were closed with subcuticular 0 silk suture. The area was then dressed.
The catheter was subsequently connected to the drainage wall suction and <100cc of serosanguinous fluid was drained.
The catheter tip was then capped and the pleurx was dressed and covered with a transulent dressing.
The patient tolerated the procedural well.
Post-procedure chest radiograph showed minimal residual pleural air with
pleural catheter in place tracking upwards.
Complications: No immediate complications
Estimated Blood Loss: 20cc
Post Procedure Diagnosis: Pleural effusion 
Recommendation:
Will await pathology and microbiological studies
Patient education on pleural catheter draining and will return tomorrow for initial drainage.
Hold heparin drip until 6 hours post-procedure (19:00 tonight)"""

# ==========================================
# 2. ENTITY DEFINITIONS
# ==========================================
# List of entities to extract: (Label, Text, Occurrence_Index)
# Occurrence_Index=0 means find the first match after the previous entity, 
# ensuring sequential processing.
entities_to_extract = [
    ("PROC_ACTION", "Pleuroscopy"),
    ("OBS_LESION", "Pleural effusion"),
    ("MEDICATION", "Fentanyl"),
    ("MEDICATION", "versed"),
    ("MEDICATION", "Lidocaine"),
    ("MEAS_VOL", "30cc"),
    ("ANAT_PLEURA", "pleural entry site"),
    ("PROC_METHOD", "ultrasound"),
    ("MEDICATION", "chlorhexidine gluconate"),
    ("MEAS_VOL", "10mL"),
    ("MEDICATION", "lidocaine"),
    ("MEDICATION", "lidocaine"), # Subcutaneous lidocaine
    ("MEAS_SIZE", "1 cm"),
    ("ANAT_PLEURA", "pleural space"),
    ("MEAS_SIZE", "8 mm"),
    ("LATERALITY", "left side"),
    ("ANAT_PLEURA", "6th anterior axillary line"),
    ("MEAS_VOL", "700cc"),
    ("DEV_INSTRUMENT", "rigid pleuroscopy telescope"),
    ("ANAT_PLEURA", "pleural space"),
    ("OBS_LESION", "pleural studding"),
    ("ANAT_PLEURA", "pleura"),
    ("OBS_LESION", "plaques"),
    ("OBS_FINDING", "tethering"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("ANAT_PLEURA", "chest wall"),
    ("OBS_LESION", "abnormal areas"),
    ("ANAT_PLEURA", "parietal pleura"),
    ("DEV_INSTRUMENT", "forceps"),
    ("MEAS_COUNT", "5"),
    ("PROC_ACTION", "biopsies"),
    ("MEDICATION", "protamine"),
    ("MEDICATION", "heparin"),
    ("DEV_INSTRUMENT", "pleuroscopy telescope"),
    ("DEV_CATHETER_SIZE", "15.5"),
    ("DEV_CATHETER", "pleural catheter"),
    ("ANAT_PLEURA", "pleural space"),
    ("DEV_CATHETER", "PleurX Catheter"),
    ("DEV_INSTRUMENT", "guide wire"),
    ("MEAS_SIZE", "5cm"),
    ("MEDICATION", "lidocaine"),
    ("MEAS_SIZE", "1cm"),
    ("DEV_INSTRUMENT", "tunneler"),
    ("DEV_CATHETER", "Pleurx catheter"),
    ("DEV_INSTRUMENT", "tunneler"),
    ("MEAS_SIZE", "16 fr"),
    ("DEV_INSTRUMENT", "peel away sheath"),
    ("DEV_CATHETER", "Pleurx catheter"),
    ("MEAS_SIZE", "16 fr."),
    ("DEV_INSTRUMENT", "peel away sheath"),
    ("DEV_INSTRUMENT", "0 silk suture"),
    ("MEAS_VOL", "100cc"),
    ("DEV_CATHETER", "pleural catheter"),
    ("OBS_LESION", "Pleural effusion"),
    ("MEDICATION", "heparin")
]

# ==========================================
# 3. ANALYSIS & EXTRACTION LOGIC
# ==========================================
def extract_entities(text, entity_list):
    extracted_spans = []
    current_idx = 0
    
    for label, substr in entity_list:
        # Find substring starting from current_idx
        start = text.find(substr, current_idx)
        
        if start == -1:
            # Fallback: Try from beginning if not found sequentially (should not happen if ordered)
            start = text.find(substr)
            if start == -1:
                print(f"Warning: Entity '{substr}' not found in text.")
                continue
                
        end = start + len(substr)
        
        extracted_spans.append({
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        
        # Advance current_idx to avoid overlapping previous finds or finding previous instances
        current_idx = end
        
    return extracted_spans

spans = extract_entities(RAW_TEXT, entities_to_extract)

# ==========================================
# 4. FILE UPDATES
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": spans
}

ner_dataset_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
with open(ner_dataset_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

notes_path = OUTPUT_DIR / "notes.jsonl"
with open(notes_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# C. Update spans.jsonl
spans_path = OUTPUT_DIR / "spans.jsonl"
with open(spans_path, "a", encoding="utf-8") as f:
    for span in spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
stats_path = OUTPUT_DIR / "stats.json"

if stats_path.exists():
    with open(stats_path, "r", encoding="utf-8") as f:
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
stats["total_files"] += 1 # Assuming 1 note per file for this pipeline
stats["total_spans_raw"] += len(spans)
stats["total_spans_valid"] += len(spans)

for span in spans:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# ==========================================
# 5. VALIDATION & LOGGING
# ==========================================
with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as log:
    for span in spans:
        extracted = RAW_TEXT[span["start"]:span["end"]]
        if extracted != span["text"]:
            log_msg = (
                f"[{datetime.now()}] MISMATCH in {NOTE_ID}: "
                f"Label {span['label']} expected '{span['text']}' "
                f"but found '{extracted}' at {span['start']}:{span['end']}\n"
            )
            log.write(log_msg)

print(f"Successfully processed {NOTE_ID}. Extracted {len(spans)} entities.")
print(f"Data appended to {OUTPUT_DIR}")