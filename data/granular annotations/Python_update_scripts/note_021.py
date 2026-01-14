import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration
# ==========================================
NOTE_ID = "note_021"
# Target Directory: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Input Data (Raw Text & Entity definitions)
# ==========================================
raw_text = """NOTE_ID:  note_021 SOURCE_FILE: note_021.txt INDICATION FOR OPERATION:  [REDACTED]is a 68 year old-year-old male who presents with persistent airleak.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.
 
CONSENT : Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form / provided consent over the phone.
The consent was witnessed by an assisting medical professional.
 
PREOPERATIVE DIAGNOSIS: J93.82 Other airleaks
 
POSTOPERATIVE DIAGNOSIS:  J93.82 Other airleaks
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)    
31634 Balloon occlusion or placement of occlusive substance 
31635 Foreign body removal
31647 Bronchial valve insert initial lobe 
 
22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)  31624 BAL done in multiple lobes.
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Flexible Therapeutic Bronchoscope
Flexible Hybrid (Pedatric) Bronchoscope
 
ESTIMATED BLOOD LOSS:   None
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: . 
 
Initial Airway Inspection Findings:
 
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius , and Left Mainstem from mucus and mucus plug.
Bronchial alveolar lavage was performed at Superior Segment of Lingula (LB4) and Inferior Segment of Lingula (LB5).
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
Bronchial alveolar lavage was performed at Lateral-basal Segment of RLL (RB9).
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
Serial occlusion with endobronchial blocker (ardnts 7Fr) and Fogarty balloon was done to isolate the airleak to be at the RLL (Lateral and Posterior subsegment).
Airleak was reproduced with inspiratory hold at 30 and suction on pleurovac on -20cmH20.
Tisseel 2cc was used to block off a subsegment of the RLL posterior branch.
Size 7 spiration valve was placed but noted to be too large for the airway (RB10).  This was subsequently removed.
Then Size 6 spiration valve was placed in RB9, in good position.
Then size 6 spiration valve was placed in RB10, noted to be in poor position, this was removed again and replaced with another size 6 spiration valve in a better angle.
Final: 
RB9 - size 6 spiration valve
RB10- size 6 spiration valve
 
With airleak significantly decreased.
See Dr. Thistlethwaite's note for VATS and pleurodesis. 
 
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
BAL (x2) 
 
IMPRESSION/PLAN: [REDACTED]is a 68 year old-year-old male who presents for bronchoscopy for BAL and valve placement.
- f/u in BAL results
- f/u in 6 weeks for valve removal"""

# Define entities to extract (Label, Text Snippet)
# Order matters roughly for context, but the script handles global search.
targets = [
    ("OBS_FINDING", "airleak"),
    ("PROC_METHOD", "Bronchoscopy"),
    ("PROC_ACTION", "Therapeutic aspiration"),
    ("PROC_ACTION", "Bronchial alveolar lavage"),
    ("PROC_ACTION", "Balloon occlusion"),
    ("PROC_ACTION", "Foreign body removal"),
    ("PROC_ACTION", "Bronchial valve insert"),
    ("PROC_ACTION", "BAL"),
    ("DEV_INSTRUMENT", "Flexible Therapeutic Bronchoscope"),
    ("DEV_INSTRUMENT", "Flexible Hybrid (Pedatric) Bronchoscope"),
    ("ANAT_AIRWAY", "Right Mainstem"),
    ("ANAT_AIRWAY", "Bronchus Intermedius"),
    ("ANAT_AIRWAY", "Left Mainstem"),
    ("OBS_FINDING", "mucus"),
    ("OBS_FINDING", "mucus plug"),
    ("ANAT_LUNG_LOC", "Superior Segment of Lingula"),
    ("ANAT_LUNG_LOC", "LB4"),
    ("ANAT_LUNG_LOC", "Inferior Segment of Lingula"),
    ("ANAT_LUNG_LOC", "LB5"),
    ("MEAS_VOL", "60 cc"),
    ("MEAS_VOL", "15 cc"),
    ("ANAT_LUNG_LOC", "Lateral-basal Segment of RLL"),
    ("ANAT_LUNG_LOC", "RB9"),
    ("DEV_INSTRUMENT", "endobronchial blocker"),
    ("MEAS_SIZE", "7Fr"),
    ("DEV_INSTRUMENT", "Fogarty balloon"),
    ("ANAT_LUNG_LOC", "RLL"),
    ("ANAT_LUNG_LOC", "Lateral and Posterior subsegment"),
    ("MEAS_PRESS", "-20cmH20"),
    ("MEDICATION", "Tisseel"),
    ("MEAS_VOL", "2cc"),
    ("ANAT_LUNG_LOC", "posterior branch"),
    ("MEAS_SIZE", "Size 7"),
    ("DEV_VALVE", "spiration valve"),
    ("ANAT_LUNG_LOC", "RB10"),
    ("MEAS_SIZE", "Size 6"),
    ("MEAS_SIZE", "size 6"),
    ("PROC_METHOD", "VATS"),
    ("PROC_ACTION", "pleurodesis"),
]

# ==========================================
# 3. Processing Logic
# ==========================================

def get_spans(text, targets):
    """
    Finds all occurrences of target strings in text.
    Returns list of dicts: {'label':..., 'text':..., 'start':..., 'end':...}
    """
    found_spans = []
    # Sort by length descending to prioritize longer matches (greedy) if needed, 
    # though strict exact match is used here.
    
    # We want to find ALL occurrences of each target
    for label, substr in targets:
        start_index = 0
        while True:
            idx = text.find(substr, start_index)
            if idx == -1:
                break
            
            span = {
                "label": label,
                "text": substr,
                "start": idx,
                "end": idx + len(substr)
            }
            
            # Avoid duplicate spans if multiple targets define the same text 
            # (simple dedupe based on start/end)
            if not any(s['start'] == span['start'] and s['end'] == span['end'] for s in found_spans):
                found_spans.append(span)
            
            start_index = idx + 1
            
    return sorted(found_spans, key=lambda x: x['start'])

# Extract Spans
entities = get_spans(raw_text, targets)

# ==========================================
# 4. File Updates
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": raw_text,
    "entities": entities
}

with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": raw_text
}

with open(NOTES_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(note_entry) + "\n")

# C. Update spans.jsonl
new_spans = []
for ent in entities:
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

with open(SPANS_PATH, 'a', encoding='utf-8') as f:
    for span in new_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, 'r', encoding='utf-8') as f:
        stats = json.load(f)
else:
    stats = {
        "total_files": 0, "successful_files": 0, "total_notes": 0, 
        "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1 # Assuming success if we reached here
stats["total_notes"] += 1
stats["total_spans_raw"] += len(entities)
stats["total_spans_valid"] += len(entities)

# Update Label Counts
for ent in entities:
    lbl = ent['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

# E. Validation & Logging
with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
    for ent in entities:
        extracted = raw_text[ent['start']:ent['end']]
        if extracted != ent['text']:
            log_msg = f"{datetime.datetime.now().isoformat()} - ALIGNMENT ERROR: {NOTE_ID} - Expected '{ent['text']}' but found '{extracted}' at {ent['start']}:{ent['end']}\n"
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID}.")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Extracted {len(entities)} entities.")