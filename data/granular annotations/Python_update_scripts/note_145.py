import json
import os
import re
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_145"

# Raw text content of note_145.txt (Cleaned of [source] tags)
RAW_TEXT = """Procedure Name: Pleuroscopy
Indications: Pleural effusion
Medications: Monitored anesthesia care

Pre-Anesthesia Assessment

ASA Physical Status: III – A patient with severe systemic disease

Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered, and informed consent was documented per institutional protocol.
A history and physical examination were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.

The patient was sterilely prepped, and pleuroscopy was performed.
Procedure Description
Positioning and Preparation

The patient was placed on the operating table in the lateral decubitus position, and all pressure points were adequately padded.
The skin was prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual sterile fashion.
Local Anesthesia

The pleural entry site was identified using ultrasound guidance.
The entry site was infiltrated with 30 mL of 1% lidocaine.
Incision and Port Placement

A 10-mm reusable primary port was placed on the left side at the seventh intercostal space along the anterior axillary line using a Veress needle technique.
Pleuroscopy

A 0-degree 7.0-mm pleuroscopy telescope was introduced through the incision and advanced into the pleural space.
A 0-degree 4.0-mm pleuroscopy telescope was subsequently introduced through the same incision for further inspection.
The pleura was systematically inspected via the primary port.

Findings

There was extensive pleural studding throughout the pleural space.
No purulent collections were identified. Thick pleural adhesions were present throughout.
Biopsy and Interventions

Biopsies of pleural adhesions were obtained from the upper pleura using forceps and sent for histopathologic examination.
Five biopsy specimens were obtained. An additional five specimens were sent for microbiologic cultures.
A 15.5-French PleurX catheter was placed in the pleural space over the diaphragm.
Dressing

Port sites were dressed with a transparent dressing.

Complications

No immediate complications.

Estimated Blood Loss

Minimal.
Post-Procedure Diagnosis

Pleural metastases

Post-Procedure Care

The patient will be observed post-procedure until all discharge criteria are met.
Chest radiograph to be obtained post-procedure."""

# Target Entities (Manual Extraction based on Label_guide_UPDATED.csv)
# Format: (Text_Span, Label, Occurrence_Index)
# Occurrence_Index: 0 for first match, 1 for second, etc.
TARGET_ENTITIES = [
    ("Pleuroscopy", "PROC_ACTION", 0),
    ("Pleural effusion", "OBS_LESION", 0),
    ("chlorhexidine gluconate", "MEDICATION", 0),
    ("Chloraprep", "MEDICATION", 0),
    ("pleural entry site", "ANAT_PLEURA", 0),
    ("ultrasound", "PROC_METHOD", 0),
    ("30 mL", "MEAS_VOL", 0),
    ("lidocaine", "MEDICATION", 0),
    ("10-mm", "MEAS_SIZE", 0),
    ("left", "LATERALITY", 0),
    ("seventh intercostal space", "ANAT_PLEURA", 0),
    ("anterior axillary line", "ANAT_PLEURA", 0),
    ("Veress needle", "DEV_NEEDLE", 0),
    ("7.0-mm", "MEAS_SIZE", 0),
    ("pleuroscopy telescope", "DEV_INSTRUMENT", 0),
    ("pleural space", "ANAT_PLEURA", 0),
    ("4.0-mm", "MEAS_SIZE", 0),
    ("pleuroscopy telescope", "DEV_INSTRUMENT", 1),
    ("pleura", "ANAT_PLEURA", 0), # "The pleura was..."
    ("pleural studding", "OBS_LESION", 0),
    ("pleural space", "ANAT_PLEURA", 1), # "...throughout the pleural space"
    ("purulent collections", "OBS_FINDING", 0),
    ("pleural adhesions", "OBS_FINDING", 0),
    ("Biopsies", "PROC_ACTION", 0),
    ("pleural adhesions", "OBS_FINDING", 1),
    ("upper pleura", "ANAT_PLEURA", 0),
    ("forceps", "DEV_INSTRUMENT", 0),
    ("Five", "MEAS_COUNT", 0),
    ("biopsy specimens", "SPECIMEN", 0),
    ("five", "MEAS_COUNT", 0), # "five specimens" (lowercase)
    ("specimens", "SPECIMEN", 1), # "five specimens"
    ("15.5-French", "DEV_CATHETER_SIZE", 0),
    ("PleurX catheter", "DEV_CATHETER", 0),
    ("pleural space", "ANAT_PLEURA", 2), # "...placed in the pleural space"
    ("diaphragm", "ANAT_PLEURA", 0),
    ("Pleural metastases", "OBS_LESION", 0)
]

# =============================================================================
# SETUP PATHS
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
# PROCESSING FUNCTIONS
# =============================================================================

def find_entity_spans(text, entities):
    """
    Locates exact start/end indices for entities handling multiple occurrences.
    """
    results = []
    
    # Track used indices to ensure no overlap if needed, 
    # though strict sequential finding by occurrence index is usually safer
    
    for text_span, label, occurrence in entities:
        matches = [m for m in re.finditer(re.escape(text_span), text)]
        
        if occurrence < len(matches):
            match = matches[occurrence]
            start = match.start()
            end = match.end()
            results.append({
                "span_id": f"{label}_{start}",
                "note_id": NOTE_ID,
                "label": label,
                "text": text_span,
                "start": start,
                "end": end
            })
        else:
            print(f"WARNING: Could not find occurrence {occurrence} of '{text_span}' in text.")
            
    # Sort by start index
    return sorted(results, key=lambda x: x['start'])

def update_jsonl(path, data):
    """Appends a dictionary as a JSON line to a file."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(new_spans):
    """Updates the global stats.json file."""
    if STATS_PATH.exists():
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
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
    # total_files is often same as total_notes in this context, or tracked externally
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def validate_and_log(spans, raw_text):
    """Checks alignment and logs warnings."""
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        for span in spans:
            extracted = raw_text[span['start']:span['end']]
            if extracted != span['text']:
                msg = f"[{datetime.datetime.now()}] MISMATCH in {NOTE_ID}: Expected '{span['text']}', found '{extracted}' at {span['start']}:{span['end']}\n"
                log.write(msg)
                print(msg.strip())

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print(f"Processing {NOTE_ID}...")

    # 1. Calculate Spans
    valid_spans = find_entity_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": s["span_id"],
                "label": s["label"],
                "start_offset": s["start"],
                "end_offset": s["end"]
            }
            for s in valid_spans
        ]
    }
    update_jsonl(NER_DATASET_PATH, ner_entry)

    # 3. Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    update_jsonl(NOTES_PATH, note_entry)

    # 4. Update spans.jsonl
    for span in valid_spans:
        update_jsonl(SPANS_PATH, span)

    # 5. Update stats.json
    update_stats(valid_spans)

    # 6. Validate
    validate_and_log(valid_spans, RAW_TEXT)

    print(f"Successfully processed {len(valid_spans)} entities for {NOTE_ID}.")