from pathlib import Path
import json
import os
import datetime

# -------------------------------------------------------------------------
# 1. Setup & Configuration
# -------------------------------------------------------------------------
NOTE_ID = "note_146"
SOURCE_FILENAME = "note_146.txt"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_JSONL_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_JSONL_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# -------------------------------------------------------------------------
# 2. Raw Text Content
# -------------------------------------------------------------------------
raw_text = """Procedure: Rigid and flexible bronchoscopy with endobronchial biopsy, tumor debulking, APC ablation, and silicone Y-stent placement
Indication: Mediastinal adenopathy, diagnostic and therapeutic
Anesthesia: General anesthesia; topical 2% lidocaine to tracheobronchial tree (10 mL)

Pre-Procedure

Standard informed consent and time-out performed.

History/physical updated; labs and imaging reviewed.
Patient tolerated induction and procedure well.

Technique

Rigid bronchoscopy: Black bronchial tube 12.0–11.0 via mouth with 0° 4.0-mm rigid telescope.
Flexible bronchoscopy: Q180 slim and T180 therapeutic bronchoscopes passed through the rigid bronchoscope.
Therapeutic tools: Electrocautery snare, XPS 3000 microdebrider, ERBE APC VIO 300D (argon plasma coagulation).

Airway Findings

Vocal cords: Normal mobility.
Subglottis: Normal.

Proximal trachea: Normal caliber.

Distal trachea / carina:

Mixed obstruction (extrinsic compression + endoluminal tumor) arising from the right lateral distal trachea, extending to involve the main carina and both mainstem bronchi over ~1 cm.
~75% luminal occlusion in the lower trachea.

Carinal mass large, friable, infiltrative, and submucosal with prominent endobronchial component.
Interventions

Electrocautery snare debulking of carinal mass → ~60% recanalization at carina.

Resected tissue sent to pathology.
Endobronchial biopsies (cup forceps) from lower trachea and carina (5 samples) sent for histopathology.
Microdebrider resection of additional lower tracheal tumor → partial recanalization to ~50% of normal.
APC ablation to residual tumor in the trachea, carina, left and right mainstem bronchi → post-ablation lumen ~70% of normal.
Airway stenting:

Silicone Y-stent (Novatec 14–10–10 mm) selected and customized (6 cm tracheal limb; 1 cm each mainstem limb).
Deployed under direct vision across trachea, carina, and both mainstem bronchi.

Post-stent lumen ~90% of normal; no airway orifices obstructed;
final position satisfactory.

Complications / Blood Loss

No immediate complications.

Estimated blood loss: < 5 cc.
Impression

Severe malignant airway obstruction at the distal trachea/carina with bilateral mainstem involvement.
Technically successful rigid bronchoscopy with diagnostic biopsies, multimodal tumor debulking/ablation, and silicone Y-stent placement resulting in substantial airway patency restoration.
Post-Procedure Plan

Observe in post-bronchoscopy recovery until discharge criteria met.

Await pathology results.
Follow up with requesting/oncology service to review final histopathology and guide definitive therapy."""

# -------------------------------------------------------------------------
# 3. Entity Extraction Strategy
# -------------------------------------------------------------------------
# We will define a list of (label, substring) tuples.
# For repeated substrings, we must strictly order them as they appear in text.
# We will use a cursor to search sequentially.

entities_to_find = [
    ("PROC_METHOD", "Rigid"),
    ("PROC_METHOD", "flexible bronchoscopy"),
    ("PROC_ACTION", "endobronchial biopsy"),
    ("PROC_ACTION", "tumor debulking"),
    ("PROC_ACTION", "APC ablation"),
    ("DEV_STENT_MATERIAL", "silicone"),
    ("DEV_STENT", "Y-stent"),
    ("PROC_ACTION", "placement"),
    ("OBS_LESION", "Mediastinal adenopathy"),
    ("MEDICATION", "2% lidocaine"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("MEAS_VOL", "10 mL"),
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("DEV_INSTRUMENT", "Black bronchial tube"),
    ("MEAS_SIZE", "12.0–11.0"),
    ("MEAS_SIZE", "4.0-mm"),
    ("DEV_INSTRUMENT", "rigid telescope"),
    ("PROC_METHOD", "Flexible bronchoscopy"),
    ("DEV_INSTRUMENT", "Q180 slim"),
    ("DEV_INSTRUMENT", "T180 therapeutic bronchoscopes"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "Electrocautery snare"),
    ("DEV_INSTRUMENT", "XPS 3000 microdebrider"),
    ("DEV_INSTRUMENT", "ERBE APC VIO 300D"),
    ("PROC_METHOD", "argon plasma coagulation"),
    ("ANAT_AIRWAY", "Vocal cords"),
    ("ANAT_AIRWAY", "Subglottis"),
    ("ANAT_AIRWAY", "Proximal trachea"),
    ("ANAT_AIRWAY", "Distal trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("OBS_FINDING", "obstruction"),
    ("OBS_LESION", "tumor"),
    ("LATERALITY", "right"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "main carina"),
    ("LATERALITY", "both"),
    ("ANAT_AIRWAY", "mainstem bronchi"),
    ("MEAS_SIZE", "~1 cm"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "~75% luminal occlusion"),
    ("ANAT_AIRWAY", "lower trachea"),
    ("ANAT_AIRWAY", "Carinal"),
    ("OBS_LESION", "mass"),
    ("PROC_ACTION", "Electrocautery snare debulking"),
    ("ANAT_AIRWAY", "carinal"),
    ("OBS_LESION", "mass"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "~60% recanalization"),
    ("ANAT_AIRWAY", "carina"),
    ("PROC_ACTION", "Endobronchial biopsies"),
    ("DEV_INSTRUMENT", "cup forceps"),
    ("ANAT_AIRWAY", "lower trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("MEAS_COUNT", "5 samples"),
    ("PROC_ACTION", "Microdebrider resection"),
    ("ANAT_AIRWAY", "lower tracheal"),
    ("OBS_LESION", "tumor"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "partial recanalization to ~50% of normal"),
    ("PROC_ACTION", "APC ablation"),
    ("OBS_LESION", "residual tumor"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("LATERALITY", "left"),
    ("LATERALITY", "right"),
    ("ANAT_AIRWAY", "mainstem bronchi"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "post-ablation lumen ~70% of normal"),
    ("PROC_ACTION", "Airway stenting"),
    ("DEV_STENT_MATERIAL", "Silicone"),
    ("DEV_STENT", "Y-stent"),
    ("DEV_STENT_MATERIAL", "Novatec"),
    ("DEV_STENT_SIZE", "14–10–10 mm"),
    ("MEAS_SIZE", "6 cm"),
    ("ANAT_AIRWAY", "tracheal"),
    ("MEAS_SIZE", "1 cm"),
    ("ANAT_AIRWAY", "mainstem"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("LATERALITY", "both"),
    ("ANAT_AIRWAY", "mainstem bronchi"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "Post-stent lumen ~90% of normal"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "5 cc"),
    ("OBS_FINDING", "airway obstruction"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("LATERALITY", "bilateral"),
    ("ANAT_AIRWAY", "mainstem"),
    ("PROC_METHOD", "rigid bronchoscopy"),
    ("PROC_ACTION", "biopsies"),
    ("PROC_ACTION", "tumor debulking"),
    ("PROC_ACTION", "ablation"),
    ("DEV_STENT_MATERIAL", "silicone"),
    ("DEV_STENT", "Y-stent"),
    ("PROC_ACTION", "placement")
]

extracted_entities = []
cursor = 0

for label, substring in entities_to_find:
    start_idx = raw_text.find(substring, cursor)
    if start_idx == -1:
        # Warning log if not found (helps debugging)
        print(f"WARNING: Could not find '{substring}' after index {cursor}")
        continue
    
    end_idx = start_idx + len(substring)
    
    # Store entity
    extracted_entities.append({
        "label": label,
        "text": substring,
        "start": start_idx,
        "end": end_idx
    })
    
    # Update cursor
    cursor = end_idx

# -------------------------------------------------------------------------
# 4. Generate JSON Data
# -------------------------------------------------------------------------

# A. ner_dataset_all.jsonl (Training Record)
ner_entry = {
    "id": NOTE_ID,
    "text": raw_text,
    "entities": [
        {
            "id": f"{e['label']}_{e['start']}",
            "label": e['label'],
            "start_offset": e['start'],
            "end_offset": e['end']
        }
        for e in extracted_entities
    ]
}

# B. notes.jsonl (Raw Text Map)
note_entry = {
    "id": NOTE_ID,
    "text": raw_text
}

# C. spans.jsonl (Granular Entity Database)
span_entries = []
for e in extracted_entities:
    span_entries.append({
        "span_id": f"{e['label']}_{e['start']}",
        "note_id": NOTE_ID,
        "label": e['label'],
        "text": e['text'],
        "start": e['start'],
        "end": e['end']
    })

# -------------------------------------------------------------------------
# 5. File Operations
# -------------------------------------------------------------------------

# Append to ner_dataset_all.jsonl
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# Append to notes.jsonl
with open(NOTES_JSONL_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# Append to spans.jsonl
with open(SPANS_JSONL_PATH, "a", encoding="utf-8") as f:
    for span in span_entries:
        f.write(json.dumps(span) + "\n")

# Update stats.json
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
stats["total_files"] += 1
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for e in extracted_entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# Verification & Logging
with open(LOG_PATH, "a", encoding="utf-8") as f:
    for e in extracted_entities:
        original_slice = raw_text[e['start']:e['end']]
        if original_slice != e['text']:
            f.write(f"{datetime.datetime.now()} - MISMATCH: {NOTE_ID} - Expected '{e['text']}' but found '{original_slice}' at {e['start']}:{e['end']}\n")

print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")