from pathlib import Path
import json
import os
import datetime

# ----------------------------------------------------------------------------------
# 1. Configuration & Path Setup
# ----------------------------------------------------------------------------------
NOTE_ID = "note_164"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define paths for the specific files
DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# 2. Raw Text Data
# ----------------------------------------------------------------------------------
RAW_TEXT = """NOTE_ID:  note_164 SOURCE_FILE: note_164.txt Indications: Mediastinal adenopathy of unclear etiology
Procedure Performed: CPT 31653 EBUS bronchoscopy single station.
Pre-operative diagnosis: Mediastinal adenopathy 
Post-operative diagnosis: Mediastinal  adenopathy 
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The distal right trachea was partially externally compressed and the right mainstem at the orifice was significantly externally compressed (85%) which opened up to normal in the distal right mainstem.
The left mainstem and takeoff were normal. The tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa and anatomy were normal; there are no endobronchial lesions, and moderate thick secretions.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Ultrasound was utilized to identify and measure the radiographically suspicious station paratracheal mediastinal mass (level of 4R lymph node).
The mass measured in short axis at 4.8 cm. Sampling by transbronchial needle aspiration was performed beginning with the Olympus EBUS-TBNA 19 gauge Visioshot-2 needle with a total of 6 needle passes.
Rapid onsite evaluation read as suspicious for lymphoma. All samples were sent for routine cytology or flow cytometry.
Following completion of EBUS bronchoscopy the video bronchoscope was re-inserted and blood was suctioned from the airway.
The bronchoscope was removed and procedure completed. 

Complications: No immediate complications
Estimated Blood Loss: 3 cc.
Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# ----------------------------------------------------------------------------------
# 3. Entity Extraction & Indexing
# ----------------------------------------------------------------------------------
# Helper to find exact start/end indices
def find_entity(text, sub, label, start_search=0):
    start = text.find(sub, start_search)
    if start == -1:
        return None
    end = start + len(sub)
    return {"start": start, "end": end, "label": label, "text": sub}

entities_to_find = [
    # Indications/Diagnosis
    ("Mediastinal adenopathy", "OBS_LESION"),
    ("Mediastinal adenopathy", "OBS_LESION"), # Pre-op
    ("Mediastinal  adenopathy", "OBS_LESION"), # Post-op (note extra space in text)
    
    # Procedure
    ("EBUS bronchoscopy", "PROC_METHOD"),
    
    # Anatomy & Findings
    ("distal right trachea", "ANAT_AIRWAY"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("85%", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("distal right mainstem", "ANAT_AIRWAY"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("moderate thick secretions", "OBS_FINDING"),
    
    # Instruments
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT"),
    
    # EBUS Target
    ("paratracheal mediastinal mass", "OBS_LESION"),
    ("4R lymph node", "ANAT_LN_STATION"),
    ("4.8 cm", "MEAS_SIZE"),
    
    # Sampling
    ("transbronchial needle aspiration", "PROC_METHOD"),
    ("19 gauge", "DEV_NEEDLE"),
    ("6 needle passes", "MEAS_COUNT"),
    ("suspicious for lymphoma", "OBS_ROSE"),
    
    # Outcomes
    ("No immediate complications", "OUTCOME_COMPLICATION"),
    ("3 cc", "MEAS_VOL")
]

entities = []
cursor = 0
for text_sub, label in entities_to_find:
    ent = find_entity(RAW_TEXT, text_sub, label, cursor)
    if ent:
        entities.append(ent)
        # Move cursor to avoid overlapping same-text matches if logical, 
        # though for this specific list order matters.
        # We generally search from 0 for unique distinct entities, or update cursor 
        # if the text repeats and we want the next one.
        # Resetting cursor for safety unless we explicitly want sequential.
        # In this specific note, "Mediastinal adenopathy" appears multiple times.
        # We will manually handle duplicates or just finding the first occurrence relative to context if needed.
        # For simplicity in this script generation, I will find them sequentially.
        cursor = ent["end"]
    else:
        # Fallback: try searching from 0 if not found sequentially (e.g. if list order is mixed)
        ent = find_entity(RAW_TEXT, text_sub, label, 0)
        if ent:
            entities.append(ent)

# ----------------------------------------------------------------------------------
# 4. JSONL Generation
# ----------------------------------------------------------------------------------

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": entities
}

with open(DATASET_FILE, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_FILE, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
new_spans = []
for ent in entities:
    span_id = f"{ent['label']}_{ent['start']}"
    span_entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent["label"],
        "text": ent["text"],
        "start": ent["start"],
        "end": ent["end"]
    }
    new_spans.append(span_entry)

with open(SPANS_FILE, "a", encoding="utf-8") as f:
    for span in new_spans:
        f.write(json.dumps(span) + "\n")

# ----------------------------------------------------------------------------------
# 5. Stats Update
# ----------------------------------------------------------------------------------
if STATS_FILE.exists():
    with open(STATS_FILE, "r", encoding="utf-8") as f:
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
# Assuming 1 note = 1 file in this context, or increment if tracking distinct files
stats["total_files"] += 1 
stats["total_spans_raw"] += len(entities)
stats["total_spans_valid"] += len(entities)

for ent in entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_FILE, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ----------------------------------------------------------------------------------
# 6. Validation & Logging
# ----------------------------------------------------------------------------------
with open(LOG_FILE, "a", encoding="utf-8") as log:
    timestamp = datetime.datetime.now().isoformat()
    for ent in entities:
        extracted = RAW_TEXT[ent["start"]:ent["end"]]
        if extracted != ent["text"]:
            log.write(f"[{timestamp}] MISMATCH {NOTE_ID}: Expected '{ent['text']}', found '{extracted}' at {ent['start']}:{ent['end']}\n")

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")