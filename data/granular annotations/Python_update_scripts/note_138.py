import json
import os
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_137"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text Data
# ==========================================
raw_text = """NOTE_ID:  note_137 SOURCE_FILE: note_137.txt Proceduralist(s):
Procedure Name: Pleuroscopy
Indication: Pleural effusion
Anesthesia: Monitored Anesthesia Care

Pre-Anesthesia Assessment

ASA Physical Status: III – Patient with severe systemic disease

The procedure, including risks, benefits, and alternatives, was explained to the patient.
All questions were answered, and informed consent was obtained and documented per institutional protocol.
A focused history and physical examination were performed and updated in the pre-procedure assessment record.
Relevant laboratory studies and imaging were reviewed. A procedural time-out was performed prior to initiation.
Procedure Description

The patient was placed on the operating table in the lateral decubitus position with appropriate padding of all pressure points.
The procedural site was identified using ultrasound guidance and was sterilely prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual fashion.
Local Anesthesia

The pleural entry site was infiltrated with 15 mL of 1% lidocaine.
A 10-mm reusable primary port was placed on the left side at the 6th intercostal space along the anterior axillary line using a Veress needle technique.
An LTF VP Endoeye thoracoscope was introduced through the incision and advanced into the pleural space, followed by a 0-degree 2.0-mm pleuroscopy telescope and then a 0-degree 7.0-mm pleuroscopy telescope.
Pleuroscopy Findings

Extensive adhesions were present throughout the left hemithorax.

Adhesions in the upper hemithorax were soft and thin and were successfully lysed using the pleuroscope.
Dense, thick adhesions were noted in the lower hemithorax and were not taken down due to concern for bleeding.
The parietal pleura was carefully inspected and demonstrated multiple tumor masses involving the posterior mid and upper parietal pleura.
These masses were exophytic, friable, and fungating.

The visceral pleura overlying the upper lobe was thickened but without discrete tumor nodules.
Biopsy

Biopsies of the parietal pleural masses in the mid pleura were obtained using forceps and sent for histopathologic evaluation.
Fourteen samples were obtained.

Careful inspection of the pleural space following biopsy confirmed complete hemostasis at all biopsy sites.
The previously placed 15.5-Fr PleurX catheter was left in place in the pleural space over the diaphragm.
The port site was closed with three interrupted 3-0 silk sutures.

Dressing

Port sites were dressed with a transparent dressing.
Estimated Blood Loss

Minimal

Complications

None immediate

Post-Procedure Diagnosis

Suspected pleural metastasis

Post-Procedure Plan

The patient will be observed post-procedure until all discharge criteria are met.
Chest X-ray to be obtained post-procedure."""

# ==========================================
# 3. Entity Extraction Strategy
# ==========================================
# List of (Label, Text_Snippet) tuples in order of appearance to ensure correct offset calculation.
entities_to_extract = [
    ("OBS_LESION", "Pleural effusion"),
    ("PROC_METHOD", "ultrasound"),
    ("ANAT_PLEURA", "pleural entry site"),
    ("MEAS_VOL", "15 mL"),
    ("MEDICATION", "lidocaine"),
    ("MEAS_SIZE", "10-mm"),
    ("LATERALITY", "left"),
    ("ANAT_PLEURA", "6th intercostal space"),
    ("DEV_INSTRUMENT", "LTF VP Endoeye thoracoscope"),
    ("ANAT_PLEURA", "pleural space"),
    ("DEV_INSTRUMENT", "0-degree 2.0-mm pleuroscopy telescope"),
    ("DEV_INSTRUMENT", "0-degree 7.0-mm pleuroscopy telescope"),
    ("OBS_FINDING", "adhesions"),
    ("LATERALITY", "left"),
    ("ANAT_PLEURA", "hemithorax"),
    ("OBS_FINDING", "Adhesions"),
    ("ANAT_PLEURA", "upper hemithorax"),
    ("OBS_FINDING", "adhesions"),
    ("ANAT_PLEURA", "lower hemithorax"),
    ("ANAT_PLEURA", "parietal pleura"),
    ("OBS_LESION", "tumor masses"),
    ("ANAT_PLEURA", "parietal pleura"),
    ("OBS_LESION", "masses"),
    ("ANAT_PLEURA", "visceral pleura"),
    ("ANAT_LUNG_LOC", "upper lobe"),
    ("OBS_LESION", "tumor nodules"),
    ("PROC_ACTION", "Biopsies"),
    ("ANAT_PLEURA", "parietal pleural"),
    ("OBS_LESION", "masses"),
    ("ANAT_PLEURA", "mid pleura"),
    ("DEV_INSTRUMENT", "forceps"),
    ("MEAS_COUNT", "Fourteen samples"),
    ("ANAT_PLEURA", "pleural space"),
    ("MEAS_PLEURAL_DRAIN", "15.5-Fr"),
    ("DEV_CATHETER", "PleurX catheter"),
    ("ANAT_PLEURA", "pleural space"),
    ("ANAT_PLEURA", "diaphragm"),
    ("OUTCOME_COMPLICATION", "None immediate"),
    ("OBS_LESION", "pleural metastasis"),
]

# ==========================================
# 4. Data Processing & Validation
# ==========================================
entities = []
cursor = 0
warnings = []

for label, substring in entities_to_extract:
    start_idx = raw_text.find(substring, cursor)
    
    if start_idx == -1:
        # Fallback: search from beginning if not found sequentially (though unsafe for duplicates)
        # Should not happen if the list is ordered correctly
        warnings.append(f"WARNING: Could not find '{substring}' after index {cursor}. Skipping.")
        continue
        
    end_idx = start_idx + len(substring)
    
    # Validation
    extracted_text = raw_text[start_idx:end_idx]
    if extracted_text != substring:
        warnings.append(f"MISMATCH: Expected '{substring}', got '{extracted_text}' at {start_idx}-{end_idx}")
    
    entities.append({
        "label": label,
        "start": start_idx,
        "end": end_idx
    })
    
    # Update cursor to search after this occurrence
    cursor = start_idx + 1

# ==========================================
# 5. File Update Functions
# ==========================================

def append_jsonl(filepath, data):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

def update_stats(new_entities):
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
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
    stats["total_spans_raw"] += len(new_entities)
    stats["total_spans_valid"] += len(new_entities) # Assuming valid if we generated them
    
    for entity in new_entities:
        lbl = entity["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

# ==========================================
# 6. Execution
# ==========================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": raw_text,
    "entities": [[e["start"], e["end"], e["label"]] for e in entities]
}
append_jsonl(NER_DATASET_FILE, ner_entry)

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": raw_text
}
append_jsonl(NOTES_FILE, note_entry)

# 3. Update spans.jsonl
for e in entities:
    span_entry = {
        "span_id": f"{e['label']}_{e['start']}",
        "note_id": NOTE_ID,
        "label": e['label'],
        "text": raw_text[e['start']:e['end']],
        "start": e['start'],
        "end": e['end']
    }
    append_jsonl(SPANS_FILE, span_entry)

# 4. Update stats.json
update_stats(entities)

# 5. Logging
if warnings:
    with open(LOG_FILE, "a") as f:
        f.write(f"\n--- Processing {NOTE_ID} ---\n")
        for w in warnings:
            f.write(w + "\n")
            print(w)
else:
    print(f"Successfully processed {NOTE_ID} with {len(entities)} entities.")