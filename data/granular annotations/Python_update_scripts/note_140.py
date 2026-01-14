import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_140"

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
# 2. Raw Text & Entity Definition
# ==========================================
# Exact content of note_140.txt
TEXT = """Procedure: Bronchoscopy with radial probe endobronchial ultrasound (RP-EBUS)
Indication: Esophageal cancer with suspected malignant airway involvement
Anesthesia/Ventilation: General anesthesia with controlled mechanical ventilation.
Topical 2% lidocaine to tracheobronchial tree (6 mL).
Pre-procedure status: ASA III. Standard consent and time-out performed.
Labs and imaging reviewed.

Technique

Q180 slim video bronchoscope introduced via tracheostomy to the tracheobronchial tree.
T180 therapeutic bronchoscope also introduced via tracheostomy.

UM-BS20-26R 20 MHz radial probe ultrasound advanced through the working channel to assess airway wall and adjacent structures.
Airway Examination

Tracheostomy stoma: Normal.

Trachea: Normal caliber.

Carina: Sharp.

Bronchial tree: Examined to at least the first subsegmental level.
Mucosa/anatomy: Normal throughout; no endobronchial lesions and no secretions.

Radial Probe Ultrasound Findings

Radial EBUS performed at:

Proximal left mainstem bronchus takeoff

Mid and distal trachea

Esophageal tumor visualized infiltrating the adventitia of the posterior wall of the left mainstem bronchus.
Minimum distance from esophageal mass to left mainstem bronchial lumen: 3.2 mm.

No intraluminal airway invasion identified on bronchoscopic inspection.
Impression

Malignant extrinsic airway involvement from esophageal cancer, affecting the adventitia of the posterior wall of the left mainstem bronchus.
No endobronchial disease and no intrinsic airway obstruction at time of examination.
Findings suggest high-risk proximity of tumor to airway, relevant for oncologic planning and future airway risk assessment.
Complications / Blood Loss

No immediate complications.

Estimated blood loss: None.

Specimens: None collected.
Post-Procedure Plan

Routine post-procedure observation until discharge criteria met.

Follow-up with primary/oncology team as previously scheduled."""

# Entities to extract based on Label_guide_UPDATED.csv
# Format: (Label, Surface Text)
# Note: Order matches appearance in text to facilitate simpler start_index tracking
TARGET_ENTITIES = [
    ("PROC_ACTION", "Bronchoscopy"),
    ("PROC_METHOD", "radial probe endobronchial ultrasound"),
    ("PROC_METHOD", "RP-EBUS"),
    ("OBS_LESION", "Esophageal cancer"),
    ("OBS_LESION", "malignant airway involvement"),
    ("MEDICATION", "lidocaine"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("MEAS_VOL", "6 mL"),
    ("DEV_INSTRUMENT", "Q180 slim video bronchoscope"),
    ("ANAT_AIRWAY", "tracheostomy"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "T180 therapeutic bronchoscope"),
    ("ANAT_AIRWAY", "tracheostomy"),
    ("DEV_INSTRUMENT", "UM-BS20-26R 20 MHz radial probe ultrasound"),
    ("ANAT_AIRWAY", "airway wall"),
    ("ANAT_AIRWAY", "Tracheostomy stoma"),
    ("ANAT_AIRWAY", "Trachea"),
    ("ANAT_AIRWAY", "Carina"),
    ("ANAT_AIRWAY", "Bronchial tree"),
    ("PROC_METHOD", "Radial EBUS"),
    ("ANAT_AIRWAY", "left mainstem bronchus"),
    ("ANAT_AIRWAY", "trachea"),
    ("OBS_LESION", "Esophageal tumor"),
    ("ANAT_AIRWAY", "left mainstem bronchus"),
    ("OBS_LESION", "esophageal mass"),
    ("ANAT_AIRWAY", "left mainstem bronchial lumen"),
    ("MEAS_SIZE", "3.2 mm"),
    ("OBS_LESION", "Malignant extrinsic airway involvement"),
    ("OBS_LESION", "esophageal cancer"),
    ("ANAT_AIRWAY", "left mainstem bronchus"),
    ("OUTCOME_COMPLICATION", "No immediate complications")
]

# ==========================================
# 3. Processing Logic
# ==========================================

def update_dataset():
    # 1. Calculate Offsets
    entities_with_indices = []
    search_start = 0
    
    for label, substr in TARGET_ENTITIES:
        start = TEXT.find(substr, search_start)
        if start == -1:
            print(f"WARNING: Could not find '{substr}' after index {search_start}")
            continue
        
        end = start + len(substr)
        
        # Verify alignment
        extracted = TEXT[start:end]
        if extracted != substr:
             with open(LOG_PATH, "a") as log:
                log.write(f"MISMATCH: {NOTE_ID} | Label: {label} | Expected: {substr} | Got: {extracted}\n")
        
        entities_with_indices.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        
        # Advance search start to avoid finding the same instance twice if they overlap or repeat
        search_start = start + 1

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": TEXT,
        "entities": [
            {"label": e["label"], "start_offset": e["start"], "end_offset": e["end"]}
            for e in entities_with_indices
        ]
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {"id": NOTE_ID, "text": TEXT}
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for e in entities_with_indices:
            span_id = f"{e['label']}_{e['start']}"
            span_entry = {
                "span_id": span_id,
                "note_id": NOTE_ID,
                "label": e["label"],
                "text": e["text"],
                "start": e["start"],
                "end": e["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
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
    stats["total_files"] += 1 # Assuming 1 note per file for this pipeline
    stats["total_spans_raw"] += len(entities_with_indices)
    stats["total_spans_valid"] += len(entities_with_indices)

    for e in entities_with_indices:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {NOTE_ID} with {len(entities_with_indices)} entities.")

if __name__ == "__main__":
    update_dataset()