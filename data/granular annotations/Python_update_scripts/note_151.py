import json
import os
import datetime
from pathlib import Path

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
NOTE_ID = "note_151"
NOTE_TEXT = """Tube Thoracostomy Procedure Note

Indication: Hemothorax

The patient was positioned in the usual fashion and the left chest was prepped and draped in a sterile manner using chlorhexidine.
Local anesthesia was achieved with a total of 10 mL of 1% lidocaine infiltrated into the skin, subcutaneous tissue, superior aspect of the rib periosteum, and parietal pleura.
A 2-cm incision was made parallel to the rib in the left midaxillary line at the level of the fourth rib.
Blunt dissection was carried out through the subcutaneous tissue superficial and superior to the rib down to the level of the pleura.
The pleural space was entered bluntly, with immediate expression of a large volume of blood.
The parietal pleural opening was then expanded bluntly, and a finger was inserted and carefully swept in all directions to confirm intrapleural placement and to assess for adhesions.
A 34 French chest tube was then inserted using the operator’s finger as a guide.
The tube was directed inferiorly and advanced without difficulty. Blood continued to pour from the insertion site during suturing of the tube to the skin, with approximately 1 liter of dark blood lost externally, outside of the pleurovac.
The chest tube was then securely connected to a pleurovac with tape, at which time an additional approximately 1 liter of blood drained rapidly before output slowed.
A sterile occlusive dressing was applied over the insertion site.
A second, nonfunctional chest tube was removed, revealing a large fibrin clot completely occluding the lumen.
The removal site bled briskly, and three interrupted sutures were placed, after which hemostasis was achieved.
No immediate complications were noted. A post-procedure chest x-ray is pending at the time of this note.
Complications: None
Estimated Blood Loss: Approximately 2 liters"""

# Target Entities to extract (Label, Text Snippet)
# Ordered by appearance to facilitate sequential searching
TARGET_ENTITIES = [
    ("OBS_LESION", "Hemothorax"),
    ("LATERALITY", "left"),
    ("ANAT_PLEURA", "chest"),
    ("MEDICATION", "chlorhexidine"),
    ("MEAS_VOL", "10 mL"),
    ("MEDICATION", "lidocaine"),
    ("ANAT_PLEURA", "parietal pleura"),
    ("MEAS_SIZE", "2-cm"),
    ("LATERALITY", "left"),
    ("ANAT_PLEURA", "fourth rib"),
    ("ANAT_PLEURA", "pleural space"),
    ("ANAT_PLEURA", "parietal pleural"),
    ("DEV_CATHETER_SIZE", "34 French"),
    ("DEV_CATHETER", "chest tube"),
    ("MEAS_VOL", "1 liter"),
    ("DEV_CATHETER", "chest tube"),
    ("MEAS_VOL", "1 liter"),
    ("DEV_CATHETER", "chest tube"),
    ("OBS_FINDING", "fibrin clot"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("OUTCOME_COMPLICATION", "None"),
    ("MEAS_VOL", "2 liters")
]

# -------------------------------------------------------------------------
# DIRECTORY SETUP
# -------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# -------------------------------------------------------------------------
# ENTITY EXTRACTION ENGINE
# -------------------------------------------------------------------------
entities_json = []
spans_jsonl = []
current_search_index = 0
label_counts = {}

for label, snippet in TARGET_ENTITIES:
    # Find the exact start index of the snippet, searching from the last found position
    start_idx = NOTE_TEXT.find(snippet, current_search_index)
    
    if start_idx == -1:
        # Fallback: search from beginning if not found sequentially (should not happen if ordered correctly)
        start_idx = NOTE_TEXT.find(snippet)
        if start_idx == -1:
            with open(ALIGNMENT_LOG_PATH, "a") as log:
                log.write(f"[{datetime.datetime.now()}] ERROR: Could not find snippet '{snippet}' in {NOTE_ID}\n")
            continue

    end_idx = start_idx + len(snippet)
    
    # Update search index to ensure we find the *next* occurrence next time
    current_search_index = start_idx + 1

    # Update Label Counts for Stats
    label_counts[label] = label_counts.get(label, 0) + 1

    # Construct Entity Object for ner_dataset_all.jsonl
    entity_obj = {
        "start": start_idx,
        "end": end_idx,
        "label": label
    }
    entities_json.append(entity_obj)

    # Construct Span Object for spans.jsonl
    span_obj = {
        "span_id": f"{label}_{start_idx}",
        "note_id": NOTE_ID,
        "label": label,
        "text": snippet,
        "start": start_idx,
        "end": end_idx
    }
    spans_jsonl.append(span_obj)

    # Validate alignment
    extracted_text = NOTE_TEXT[start_idx:end_idx]
    if extracted_text != snippet:
        with open(ALIGNMENT_LOG_PATH, "a") as log:
            log.write(f"[{datetime.datetime.now()}] WARNING: Mismatch in {NOTE_ID}. Expected '{snippet}', got '{extracted_text}'\n")

# -------------------------------------------------------------------------
# FILE UPDATES
# -------------------------------------------------------------------------

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": NOTE_TEXT,
    "entities": entities_json
}

ner_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
with open(ner_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": NOTE_TEXT
}

notes_path = OUTPUT_DIR / "notes.jsonl"
with open(notes_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Update spans.jsonl
spans_path = OUTPUT_DIR / "spans.jsonl"
with open(spans_path, "a", encoding="utf-8") as f:
    for span in spans_jsonl:
        f.write(json.dumps(span) + "\n")

# 4. Update stats.json
stats_path = OUTPUT_DIR / "stats.json"
if stats_path.exists():
    with open(stats_path, "r", encoding="utf-8") as f:
        try:
            stats = json.load(f)
        except json.JSONDecodeError:
            stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
else:
    stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

# Increment global counters
stats["total_notes"] += 1
# Assuming 1 note = 1 file for this logic, though often files contain multiple notes
stats["total_files"] += 1 
stats["total_spans_raw"] += len(entities_json)
stats["total_spans_valid"] += len(entities_json)

# Update label counts
for label, count in label_counts.items():
    if label in stats["label_counts"]:
        stats["label_counts"][label] += count
    else:
        stats["label_counts"][label] = count

with open(stats_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")