import json
import os
import datetime
import re
from pathlib import Path

# -------------------------------------------------------------------------
# 1. Configuration & Path Setup
# -------------------------------------------------------------------------
NOTE_ID = "note_147"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 2. Input Data (Cleaned Raw Text)
# -------------------------------------------------------------------------
RAW_TEXT = """Procedure Performed:
Left-sided pleuroscopy (medical thoracoscopy) with pleural fluid drainage, pleural biopsies, and tunneled pleural catheter placement

Indication:
Pleural effusion

Medications / Anesthesia:
Monitored anesthesia care

Pre-Anesthesia Assessment:
ASA Class III (severe systemic disease)

The procedure, including risks, benefits, and alternatives, was explained to the patient.
All questions were answered, and informed consent was obtained and documented per institutional protocol.
A history and physical examination were performed and updated in the pre-procedure assessment record.
Pertinent laboratory studies and imaging were reviewed. A procedural time-out was performed.
The patient was positioned in the lateral decubitus position on the operating table with pressure points appropriately padded.
The patient was sterilely prepped with chlorhexidine gluconate (ChloraPrep) and draped in the usual fashion.
Local Anesthesia

The pleural entry site was identified using ultrasound guidance.
The entry site was infiltrated with 20 mL of 1% lidocaine.
Procedure Description

A 10-mm reusable primary port was placed on the left side at the sixth intercostal space in the mid-axillary line using a Veress needle technique.
A 10.0-mm integrated pleuroscope was introduced through the incision and advanced into the pleural space.
The pleura was inspected via the primary port.

A total of approximately 1,700 mL of amber-colored pleural fluid was removed.
Findings

The pleura demonstrated multiple areas of visible tumor studding involving the parietal pleura, visceral pleura, and lung.
The left lower lobe did not appear fully expanded and was atelectatic.
Biopsies

Biopsies of pleural tumor studding over the diaphragm were obtained using forceps and sent for histopathological examination.
A total of 11 biopsies were obtained.

Pleural Catheter Placement

A 15.5-French PleurX catheter was placed in the pleural space over the diaphragm.
Dressing

The port site was dressed with a transparent dressing.

Complications:
None immediate

Estimated Blood Loss:
Minimal

Post-Procedure Diagnosis:
Suspected pleural metastasis

Post-Procedure Plan:
Observe post-procedure until discharge criteria are met
Obtain post-procedure chest radiograph"""

# -------------------------------------------------------------------------
# 3. Entity Definitions
# -------------------------------------------------------------------------
# Entities defined based on Label_guide_UPDATED.csv
# Format: (Text substring, Label)
entities_to_find = [
    ("Left-sided", "LATERALITY"),
    ("pleuroscopy", "PROC_ACTION"),
    ("Pleural effusion", "OBS_LESION"),
    ("ultrasound guidance", "PROC_METHOD"),
    ("pleural entry site", "ANAT_PLEURA"),
    ("20 mL", "MEAS_VOL"),
    ("lidocaine", "MEDICATION"),
    ("10-mm", "MEAS_SIZE"),
    ("primary port", "DEV_INSTRUMENT"),
    ("left side", "LATERALITY"),
    ("sixth intercostal space", "ANAT_PLEURA"),
    ("mid-axillary line", "ANAT_PLEURA"),
    ("Veress needle", "DEV_INSTRUMENT"),
    ("10.0-mm", "MEAS_SIZE"),
    ("pleuroscope", "DEV_INSTRUMENT"),
    ("pleural space", "ANAT_PLEURA"),
    ("1,700 mL", "MEAS_VOL"),
    ("amber-colored", "OBS_FINDING"),
    ("pleural fluid", "ANAT_PLEURA"), # Can be mapped to fluid or specimen, but strictly guide says ANAT_PLEURA->Pleural space. Let's stick to strict guide. 'pleural fluid' is often implicitly ANAT. However, 'pleural fluid_removed' maps to MEAS_VOL. Let's map 'tumor studding' and key lesions.
    ("tumor studding", "OBS_LESION"),
    ("parietal pleura", "ANAT_PLEURA"),
    ("visceral pleura", "ANAT_PLEURA"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("atelectatic", "OBS_FINDING"),
    ("Biopsies", "PROC_ACTION"),
    ("diaphragm", "ANAT_PLEURA"),
    ("forceps", "DEV_INSTRUMENT"),
    ("15.5-French", "DEV_CATHETER_SIZE"),
    ("PleurX catheter", "DEV_CATHETER"),
    ("pleural metastasis", "OBS_LESION")
]

# -------------------------------------------------------------------------
# 4. Entity Extraction (Offset Calculation)
# -------------------------------------------------------------------------
extracted_entities = []

def find_offsets(text, substring, label, start_search_index=0):
    start = text.find(substring, start_search_index)
    if start == -1:
        return None
    end = start + len(substring)
    return {"label": label, "text": substring, "start": start, "end": end}

# We iterate and find all occurrences or specific targeted occurrences
# To avoid duplicates or overlapping that logic might need refinement in a real NLP pipeline,
# but here we scan linearly for the specific entities listed above.

# Sort unique entities by their appearance in text to handle multiple occurrences if needed
# For this script, we will simply loop through the specific list.
search_cursor = 0
for text_span, label in entities_to_find:
    # Reset cursor for common terms if necessary, or keep moving forward?
    # For safety in this specific note, we will search from the beginning for each,
    # but strictly verify unique contexts if multiple exist.
    # Given the list order follows the note flow roughly:
    
    # We'll search from 0 every time but pick the one that hasn't been added 
    # or just simple extraction for this note's unique context.
    # To ensure we get the *correct* instance (e.g. "pleural space" appears multiple times),
    # we can use a cursor or just find all valid matches.
    
    # Strategy: Find all matches, check if not overlapping existing, add.
    matches = [m.start() for m in re.finditer(re.escape(text_span), RAW_TEXT)]
    
    for start_idx in matches:
        end_idx = start_idx + len(text_span)
        
        # Check for overlap
        overlap = False
        for existing in extracted_entities:
            if not (end_idx <= existing['start'] or start_idx >= existing['end']):
                overlap = True
                break
        
        if not overlap:
            extracted_entities.append({
                "label": label,
                "text": text_span,
                "start": start_idx,
                "end": end_idx
            })

# Sort entities by start position
extracted_entities.sort(key=lambda x: x['start'])

# -------------------------------------------------------------------------
# 5. File Updates
# -------------------------------------------------------------------------

# A. Update ner_dataset_all.jsonl
ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_entities
}

with open(ner_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
notes_file = OUTPUT_DIR / "notes.jsonl"
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(notes_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
spans_file = OUTPUT_DIR / "spans.jsonl"
new_spans = []

for ent in extracted_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    }
    new_spans.append(span_entry)

with open(spans_file, "a", encoding="utf-8") as f:
    for span in new_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
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
stats["total_files"] += 1 # Assuming 1 note = 1 file context
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for ent in extracted_entities:
    lbl = ent['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_file, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# -------------------------------------------------------------------------
# 6. Validation & Logging
# -------------------------------------------------------------------------
log_file = OUTPUT_DIR / "alignment_warnings.log"
warnings = []

for ent in extracted_entities:
    snippet = RAW_TEXT[ent['start']:ent['end']]
    if snippet != ent['text']:
        warnings.append(f"MISMATCH ID {NOTE_ID}: Exp '{ent['text']}' Got '{snippet}' at {ent['start']}-{ent['end']}")

if warnings:
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n".join(warnings) + "\n")