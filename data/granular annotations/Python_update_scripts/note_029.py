import json
import os
import datetime
from pathlib import Path

# =============================================================================
# 1. CONFIGURATION & RAW TEXT
# =============================================================================

NOTE_ID = "note_029"

# Raw text from note_029.txt
RAW_TEXT = """INDICATION FOR OPERATION:  [REDACTED]is a 30 year old-year-old male who presents with Pleural Effusion.
The nature, purpose, risks, benefits and alternatives to Chest Ultrasound and Chest tube placement were discussed with the patient in detail.
Patient indicated a wish to proceed with procedure and informed consent was signed.
 
CONSENT : Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form / provided consent over the phone.
The consent was witnessed by an assisting medical professional.
 
PREOPERATIVE DIAGNOSIS:  Pleural Effusion
POSTOPERATIVE DIAGNOSIS: Same as preoperative diagnosis - see above.
PROCEDURE:  
76604 Ultrasound, chest (includes mediastinum), real time with image documentation
32557 Insert catheter pleura with imaging (chest tube)
 
25 Added to the E&M Encounter bill which is separate from a procedure if it is done the same day
 MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
PROCEDURE IN DETAIL:
 
 
PATIENT POSITION: 
1‌ Supine  0‌ Sitting   
0‌ Lateral Decubitus:  0‌ Right 0‌ Left 
 
CHEST ULTRASOUND FINDINGS:  1‌ Image saved and printed 
Hemithorax:   0‌ Right  1‌ Left 
 
Pleural Effusion: 
Volume:       0‌ None  0‌ Minimal  0‌ Small  0‌ Moderate  1‌ Large 
Echogenicity:   1‌ Anechoic  0‌ Hypoechoic  0‌ Isoechoic  0‌ Hyperechoic 
Loculations:  0‌ None  1‌Thin  0‌ Thick 
Diaphragmatic Motion:  1‌ Normal  0‌ Diminished  0‌ Absent  
Lung: 
Lung 
sliding before procedure:   1‌ Present  0‌ Absent 
Lung sliding post procedure:   0‌ Present  0‌ Absent 
Lung consolidation/atelectasis: 0‌ Present  0‌  Absent 
Pleura:  1‌ Normal  0‌ Thick  0‌ Nodular 
 
Insertion site prepped and draped in sterile fashion.
ANESTHESIA:   Lidocaine 1%: ___15___ ml      Other: ______ 
Entry Site: 
0‌ Right ___ Intercostal Space   1‌ Left  _4th__ Intercostal Space 
0‌ Mid-clavicular   1‌ Mid-axillary  0‌ Mid-scapular  0‌ Other: 
 
Size:  0‌ 6Fr  0‌ 8Fr   0‌ 12FR   1‌ 14Fr  0‌ 16Fr   0‌ 18Fr  0‌ 24Fr   0‌ 32 Fr   0‌ Other: 
Sutured: 1‌ Yes 0‌ No 
 
PROCEDURE FINDINGS: 
A  pigtail catheter was inserted using the Seldinger technique.
Entry into the pleural space was confirmed with the easy removal of minimal serous appearing pleural fluid and air bubbles.
A guidewire was inserted using the introducer needle pointed in the apical posterior direction. The introducer needle was then removed.
A dilator was then inserted over the wire with a twisting motion in order to form a tract for catheter insertion.
The dilator was removed and the pigtail catheter (with trochar) was advanced over the guidewire.
The catheter was inserted into the chest until all catheter holes were well within the chest.
The guidewire and trochar were then removed.  The tube was then attached to the collection drain apparatus and secured in place with suture and covered.
Fluid Removed: __300___ ml 
1‌ Serous  0‌ Serosanguinous 0‌ Bloody  0‌ Chylous 0‌ Other: 
 
Pleural pressures:   If not measured, please check here 1‌
Opening:    cmH20   
500 ml:       cmH20   
1000ml:      cmH20       
1500ml:      cmH20   
2000ml       cmH20.
Drainage device:   1‌ Pleurovac    0‌ Drainage Bag  0‌ Heimlich Valve  0‌ Pneumostat  0‌ Other: 
Suction: 1‌ No 0‌Yes, - ___ cmH20 
 
 
SPECIMEN(S): 
0‌None           1‌PH               1‌ LDH                        1‌Glucose       1‌T.
Protein    1‌Cholesterol
1‌Cell Count   0‌ ADA             0‌Triglycerides            0‌Amylase 
1‌Gram Stain/ Culture            1‌AFB                         1‌Fungal Culture 
1‌Cytology      0‌Flow Cytometry                 
              0‌Other: 
 
CXR ordered: 1‌ Yes 0‌ No 
 
 
 
COMPLICATIONS:
1‌None 0‌Bleeding-EBL: ___ ml 0‌Pneumothorax 0‌Re- Expansion Pulmonary Edema 
0‌Other: 
 
IMPRESSION/PLAN: [REDACTED]is a 30 year old-year-old male who presents for Chest Ultrasound and Chest tube placement on the LEFT.
The patient tolerated the procedure well.  There were no immediate complications.
- f/u post-op CXR
- f/u pleural fluid studies 
- keep chest tube to waterseal
- small bore chest tube flushing q8h as per orders
- daily CXR while chest tube is in place 
 
 
DISPOSITION: Nursing Unit"""

# Target annotations based on Label_guide_UPDATED.csv
# Order must match the occurrence in text to allow sequential searching.
ENTITIES_TO_FIND = [
    ("Pleural", "ANAT_PLEURA"),
    ("Effusion", "OBS_LESION"),
    ("Ultrasound", "PROC_METHOD"),
    ("Chest tube", "DEV_CATHETER"),
    # PREOPERATIVE DIAGNOSIS
    ("Pleural", "ANAT_PLEURA"),
    ("Effusion", "OBS_LESION"),
    # PROCEDURE block
    ("Ultrasound", "PROC_METHOD"),
    ("Insert", "PROC_ACTION"),
    ("catheter", "DEV_CATHETER"),
    ("pleura", "ANAT_PLEURA"),
    ("chest tube", "DEV_CATHETER"),
    # CHEST ULTRASOUND FINDINGS
    ("Left", "LATERALITY"),
    ("Pleural", "ANAT_PLEURA"),
    ("Effusion", "OBS_LESION"),
    ("Lung", "ANAT_LUNG_LOC"),
    ("Pleura", "ANAT_PLEURA"),
    # ANESTHESIA / ENTRY SITE
    ("Lidocaine", "MEDICATION"),
    ("15", "MEAS_VOL"),
    ("Left", "LATERALITY"),
    ("4th", "ANAT_PLEURA"), # Specific rib space
    ("Intercostal Space", "ANAT_PLEURA"),
    ("14Fr", "DEV_CATHETER_SIZE"),
    # PROCEDURE FINDINGS
    ("pigtail catheter", "DEV_CATHETER"),
    ("Seldinger technique", "PROC_METHOD"),
    ("pleural space", "ANAT_PLEURA"),
    ("pleural fluid", "SPECIMEN"),
    ("air bubbles", "OBS_FINDING"),
    ("guidewire", "DEV_INSTRUMENT"),
    ("introducer needle", "DEV_NEEDLE"),
    ("dilator", "DEV_INSTRUMENT"),
    ("pigtail catheter", "DEV_CATHETER"),
    ("guidewire", "DEV_INSTRUMENT"),
    ("tube", "DEV_CATHETER"),
    ("300", "MEAS_VOL"),
    ("Serous", "OBS_FINDING"),
    # IMPRESSION/PLAN
    ("Ultrasound", "PROC_METHOD"),
    ("Chest tube", "DEV_CATHETER"),
    ("LEFT", "LATERALITY"),
    ("chest tube", "DEV_CATHETER"),
    ("chest tube", "DEV_CATHETER")
]

# =============================================================================
# 2. SETUP PATHS
# =============================================================================

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# 3. PROCESSING & EXTRACTION
# =============================================================================

spans = []
last_idx = 0
found_entities = []

for text_to_find, label in ENTITIES_TO_FIND:
    start = RAW_TEXT.find(text_to_find, last_idx)
    
    if start == -1:
        # Fallback: if not found (e.g., slight typo or formatting issue), log warning
        # Note: In a production script, we might want to halt or search from 0 again if out of order.
        # Here we just log and skip to keep the script robust.
        with open(LOG_PATH, "a") as f:
            f.write(f"[{datetime.datetime.now()}] WARNING: Entity '{text_to_find}' not found after index {last_idx} in {NOTE_ID}.\n")
        continue

    end = start + len(text_to_find)
    
    # Store valid span
    span = {
        "span_id": f"{label}_{start}",
        "note_id": NOTE_ID,
        "label": label,
        "text": text_to_find,
        "start": start,
        "end": end
    }
    spans.append(span)
    
    # Simple dict for the ner_dataset_all format
    found_entities.append([start, end, label])
    
    # Advance cursor
    last_idx = start + 1

# =============================================================================
# 4. DATA WRITING
# =============================================================================

# 1. Append to ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": found_entities
}
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Append to notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Append to spans.jsonl
with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in spans:
        f.write(json.dumps(span) + "\n")

# =============================================================================
# 5. STATS UPDATE
# =============================================================================

if STATS_PATH.exists():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        try:
            stats = json.load(f)
        except json.JSONDecodeError:
            stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
else:
    stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

stats["total_notes"] += 1
# Assuming 1 file processed per script run
stats["total_files"] += 1 
stats["total_spans_raw"] += len(spans)
stats["total_spans_valid"] += len(spans)

# Update label counts
current_counts = stats.get("label_counts", {})
for span in spans:
    lbl = span["label"]
    current_counts[lbl] = current_counts.get(lbl, 0) + 1
stats["label_counts"] = current_counts

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

print(f"Successfully processed {NOTE_ID}. Extracted {len(spans)} entities.")