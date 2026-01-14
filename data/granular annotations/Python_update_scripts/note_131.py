import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_131"
TIMESTAMP = datetime.datetime.now().isoformat()

# Raw text content of note_131.txt
RAW_TEXT = """Procedure Name: Pleuroscopy
Indication: Pleural effusion
Anesthesia: Monitored Anesthesia Care

Pre-Anesthesia Assessment

ASA Physical Status: III – Patient with severe systemic disease

The procedure, including risks, benefits, and alternatives, was explained to the patient.
All questions were answered, and informed consent was obtained and documented per institutional protocol.
A focused history and physical examination were performed and updated in the pre-procedure assessment record.
Relevant laboratory studies and imaging were reviewed. A procedural time-out was performed prior to initiation.
Procedure Description

The patient was placed on the operating table in the lateral decubitus position with appropriate padding of pressure points.
The procedural site was identified using ultrasound guidance and was sterilely prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual fashion.
Local Anesthesia

The pleural entry site was infiltrated with 19 mL of 1% lidocaine.
A 10-mm reusable primary port was placed on the right side at the 6th intercostal space along the anterior axillary line using a Veress needle technique.
A 0-degree 2.0-mm pleuroscopy telescope was introduced through the incision and advanced into the pleural space, followed by a 50-degree 7.0-mm pleuroscopy optic.
Pleuroscopy Findings

Serous pleural effusion was present; approximately 3,000 mL was suctioned.
Small white and reddish raised lesions were identified on the diaphragmatic parietal pleura.

The visceral pleura appeared normal.
The chest wall (parietal) pleura was hyperemic with areas of brownish discoloration.
All three lobes collapsed easily and re-expanded fully with suction.
Biopsy

Targeted biopsies of nodular lesions on the diaphragmatic pleura were obtained using forceps (three samples) and sent for histopathologic evaluation.
Additional biopsies were obtained from the brownish lesions on the chest wall pleura.
A 15.5-Fr PleurX catheter was placed in the pleural space over the diaphragm.
Dressing

Port sites were dressed with a transparent dressing.

Estimated Blood Loss

Minimal

Complications

None immediate

Impression

Exudative pleural effusion with predominantly normal pleura, except for small diaphragmatic and chest wall lesions.
Post-Procedure Plan

The patient will be observed post-procedure until discharge criteria are met.

Chest X-ray to be obtained post-procedure."""

# Entities list - ORDER MATTERS for the cursor logic
# Format: (Label, Text Fragment)
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Pleural effusion"), # Indication
    ("PROC_METHOD", "ultrasound"),
    ("MEDICATION", "chlorhexidine gluconate"),
    ("MEDICATION", "Chloraprep"),
    ("ANAT_PLEURA", "pleural entry site"),
    ("MEAS_VOL", "19 mL"),
    ("MEDICATION", "1% lidocaine"),
    ("MEAS_SIZE", "10-mm"),
    ("DEV_INSTRUMENT", "primary port"),
    ("LATERALITY", "right"),
    ("ANAT_PLEURA", "6th intercostal space"),
    ("DEV_NEEDLE", "Veress needle"),
    ("MEAS_SIZE", "2.0-mm"),
    ("DEV_INSTRUMENT", "pleuroscopy telescope"),
    ("ANAT_PLEURA", "pleural space"),
    ("MEAS_SIZE", "7.0-mm"),
    ("DEV_INSTRUMENT", "pleuroscopy optic"),
    ("OBS_LESION", "pleural effusion"), # Findings (Serous...)
    ("MEAS_VOL", "3,000 mL"),
    ("OBS_LESION", "lesions"),
    ("ANAT_PLEURA", "diaphragmatic parietal pleura"),
    ("ANAT_PLEURA", "visceral pleura"),
    ("ANAT_PLEURA", "chest wall (parietal) pleura"),
    ("OBS_FINDING", "hyperemic"),
    ("OBS_FINDING", "brownish discoloration"),
    ("OUTCOME_PLEURAL", "re-expanded fully"),
    ("OBS_LESION", "nodular lesions"),
    ("ANAT_PLEURA", "diaphragmatic pleura"),
    ("DEV_INSTRUMENT", "forceps"),
    ("MEAS_COUNT", "three samples"),
    ("OBS_LESION", "brownish lesions"),
    ("ANAT_PLEURA", "chest wall pleura"),
    ("DEV_CATHETER_SIZE", "15.5-Fr"),
    ("DEV_CATHETER", "PleurX"),
    ("DEV_CATHETER", "catheter"),
    ("ANAT_PLEURA", "pleural space"),
    ("ANAT_PLEURA", "diaphragm"),
    ("OBS_LESION", "Exudative pleural effusion"),
    ("OBS_LESION", "chest wall lesions"),
    ("PROC_METHOD", "Chest X-ray")
]

# ==========================================
# PATH SETUP
# ==========================================
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING LOGIC
# ==========================================

def update_datasets():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Calculate Offsets
    final_entities = []
    cursor = 0
    
    for label, text_fragment in ENTITIES_TO_EXTRACT:
        start_idx = RAW_TEXT.find(text_fragment, cursor)
        
        if start_idx == -1:
            # Fallback: Search from beginning if not found after cursor (should not happen if ordered correctly)
            start_idx = RAW_TEXT.find(text_fragment)
            if start_idx == -1:
                print(f"CRITICAL WARNING: Could not find entity '{text_fragment}'")
                continue
        
        end_idx = start_idx + len(text_fragment)
        
        # Verify alignment
        extracted = RAW_TEXT[start_idx:end_idx]
        if extracted != text_fragment:
            with open(LOG_PATH, "a") as log:
                log.write(f"[{TIMESTAMP}] Mismatch in {NOTE_ID}: Expected '{text_fragment}', got '{extracted}'\n")
            continue
            
        final_entities.append({
            "start": start_idx,
            "end": end_idx,
            "label": label,
            "text": text_fragment
        })
        
        # Update cursor to prevent finding previous instances
        cursor = start_idx + 1

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": final_entities
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for ent in final_entities:
            span_id = f"{ent['label']}_{ent['start']}"
            span_entry = {
                "span_id": span_id,
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Default fallback if stats don't exist
        stats = {
            "total_files": 0,
            "successful_files": 0,
            "total_notes": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }

    # Increment globals
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(final_entities)
    stats["total_spans_valid"] += len(final_entities)

    # Increment labels
    for ent in final_entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {NOTE_ID} with {len(final_entities)} entities.")

if __name__ == "__main__":
    update_datasets()