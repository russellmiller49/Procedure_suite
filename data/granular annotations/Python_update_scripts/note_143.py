from pathlib import Path
import json
import os

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
NOTE_ID = "note_143"
RAW_TEXT = """NOTE_ID:  note_143 SOURCE_FILE: note_143.txt Procedure Name: Pleuroscopy
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
A 10.0-mm integrated pleuroscope was introduced through the incision and advanced into the pleural space.
Local Anesthesia

The pleural entry site was infiltrated with 30 mL of 1% lidocaine.
A 10-mm reusable primary port was placed on the right side at the 5th intercostal space along the mid-axillary line using a Veress needle technique.
Pleuroscopy Findings

Nodularity of the lung parenchyma, predominantly involving the lower lobe.
The pleura appeared grossly normal but demonstrated excessive adipose tissue and diffuse white fibrinous strands enveloping the pleura and lung.
Small areas of pleural studding were noted; differentiation between fat versus tumor studding was uncertain.
A mass was visualized in the posterior pleural space near the spine;
it appeared highly vascular and was not biopsied due to bleeding risk.
Approximately 2,000 mL of milky-appearing pleural fluid was removed and sent for analysis.
Biopsy

Biopsies of a pleural mucosal abnormality over the diaphragm were obtained using forceps and sent for histopathologic evaluation.
Eleven samples were obtained.

A 15.5-Fr PleurX catheter was placed in the pleural space over the diaphragm.
Dressing

Port sites were dressed with a transparent dressing.

Estimated Blood Loss

Minimal

Complications

None immediate

Post-Procedure Diagnosis

Pleural adhesions

Post-Procedure Plan

The patient will be observed post-procedure until all discharge criteria are met.
Chest X-ray to be obtained post-procedure."""

# Define entities manually to ensure strict adherence to Label_guide_UPDATED.csv
# Order matters for finding the correct occurrence if text repeats.
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Pleural effusion"),
    ("PROC_METHOD", "ultrasound guidance"),
    ("MEAS_SIZE", "10.0-mm"),
    ("DEV_INSTRUMENT", "integrated pleuroscope"),
    ("ANAT_PLEURA", "pleural space"),
    ("ANAT_PLEURA", "pleural entry site"),
    ("MEAS_VOL", "30 mL"),
    ("MEDICATION", "1% lidocaine"),
    ("MEAS_SIZE", "10-mm"),
    ("LATERALITY", "right"),
    ("ANAT_PLEURA", "5th intercostal space"),
    ("ANAT_PLEURA", "mid-axillary line"),
    ("DEV_NEEDLE", "Veress needle"),
    ("OBS_LESION", "Nodularity"),
    ("ANAT_LUNG_LOC", "lung parenchyma"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("ANAT_PLEURA", "pleura"), # "The pleura appeared..."
    ("OBS_FINDING", "diffuse white fibrinous strands"),
    ("ANAT_PLEURA", "pleura"), # "...enveloping the pleura..."
    ("ANAT_LUNG_LOC", "lung"),
    ("OBS_LESION", "pleural studding"),
    ("OBS_LESION", "mass"),
    ("ANAT_PLEURA", "posterior pleural space"),
    ("MEAS_VOL", "2,000 mL"),
    ("OBS_FINDING", "milky-appearing"),
    ("SPECIMEN", "pleural fluid"),
    ("PROC_ACTION", "Biopsies"),
    ("OBS_LESION", "pleural mucosal abnormality"),
    ("ANAT_PLEURA", "diaphragm"), # "...over the diaphragm..."
    ("DEV_INSTRUMENT", "forceps"),
    ("MEAS_COUNT", "Eleven"),
    ("DEV_CATHETER_SIZE", "15.5-Fr"),
    ("DEV_CATHETER", "PleurX catheter"),
    ("ANAT_PLEURA", "pleural space"),
    ("ANAT_PLEURA", "diaphragm"),
    ("OUTCOME_COMPLICATION", "None immediate"),
    ("OBS_LESION", "Pleural adhesions")
]

# ----------------------------------------------------------------------------------
# SETUP PATHS
# ----------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# PROCESSING LOGIC
# ----------------------------------------------------------------------------------

def find_offsets(text, entity_list):
    """
    Locates exact start/end indices for entities.
    Handles multiple occurrences by scanning strictly sequentially.
    """
    results = []
    search_start_index = 0
    
    for label, substr in entity_list:
        start = text.find(substr, search_start_index)
        if start == -1:
            # Fallback: restart search from beginning if not found sequentially 
            # (though strictly we should follow flow, this handles minor out-of-order definitions)
            start = text.find(substr)
            
        if start != -1:
            end = start + len(substr)
            results.append({
                "label": label,
                "start": start,
                "end": end,
                "text": substr
            })
            # Update search index to avoid re-matching earlier instances of the same word
            # But ensure we don't skip too far if entities are nested/close. 
            # For this strict sequential input, we move search_start_index forward.
            search_start_index = start + 1
        else:
            print(f"WARNING: Could not find exact match for '{substr}'")
            
    return results

def update_jsonl_file(path, new_record):
    """Appends a single JSON record to a JSONL file."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def update_stats(extracted_entities):
    """Updates stats.json with new counts."""
    if STATS_PATH.exists():
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0,
            "successful_files": 0,
            "total_notes": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "alignment_warnings": 0,
            "alignment_errors": 0,
            "label_counts": {},
            "hydration_status_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_entities)
    stats["total_spans_valid"] += len(extracted_entities)

    for entity in extracted_entities:
        lbl = entity["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        # Assume generic status for manual extraction
        stats["hydration_status_counts"]["hydrated_unique"] = stats["hydration_status_counts"].get("hydrated_unique", 0) + 1

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Calculate Offsets
    extracted_data = find_offsets(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Validate Alignment
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        for item in extracted_data:
            snippet = RAW_TEXT[item["start"]:item["end"]]
            if snippet != item["text"]:
                log.write(f"MISMATCH in {NOTE_ID}: Expected '{item['text']}', found '{snippet}' at {item['start']}\n")

    # 3. Update ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[item["start"], item["end"], item["label"]] for item in extracted_data]
    }
    update_jsonl_file(NER_DATASET_PATH, ner_record)

    # 4. Update notes.jsonl
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    update_jsonl_file(NOTES_PATH, note_record)

    # 5. Update spans.jsonl
    for item in extracted_data:
        span_record = {
            "span_id": f"{item['label']}_{item['start']}",
            "note_id": NOTE_ID,
            "label": item["label"],
            "span_text": item["text"],
            "start_char": item["start"],
            "end_char": item["end"],
            "hydration_status": "hydrated_unique"
        }
        update_jsonl_file(SPANS_PATH, span_record)

    # 6. Update Stats
    update_stats(extracted_data)
    
    print(f"Successfully processed {NOTE_ID} with {len(extracted_data)} entities.")

if __name__ == "__main__":
    main()