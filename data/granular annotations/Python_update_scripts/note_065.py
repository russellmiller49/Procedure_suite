import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_065"

# Raw text from the provided file
RAW_TEXT = """INDICATION FOR OPERATION:  [REDACTED] is a 84 year old-year-old female who presents with lung mass.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
PREOPERATIVE DIAGNOSIS: R91.8 Other nonspecific abnormal finding of lung field.
POSTOPERATIVE DIAGNOSIS:  R91.8 Other nonspecific abnormal finding of lung field.
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31652 EBUS sampling 1 or 2 nodes
 
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Linear EBUS 
Disposable Bronchoscope
 
ESTIMATED BLOOD LOSS:   None
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: . 
 
Initial Airway Inspection Findings:
 
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius , and Left Mainstem from mucus.
EBUS-Findings
Indications: Diagnostic
Technique:
All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 25-gauge Needle and 22-gauge Needle.
Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
11Rs lymph node
 
Overall ROSE Diagnosis: Positive for malignancy
 
No immediate complications
 
 
Lymph Nodes Evaluated:
Site 1: The 11Rs lymph node was => 10 mm on CT and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed. The site was sampled.. 6 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Preliminary ROSE Cytology was reported as not adequate and suggestive of blood and bronchial cells. Final results are pending.
Site 2: The 4R (lower paratracheal) node was => 10 mm on CT and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed. The site was sampled.. 8 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Preliminary ROSE Cytology was reported as adequate and suggestive of Positive for malignancy. Final results are pending.
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
TBNA and TBNB station 11R and 4R
 
IMPRESSION/PLAN: [REDACTED]is a 84 year old-year-old female who presents for bronchoscopy for lung mass.
- f/u pathology"""

# Define entities to extract (Label, Text Snippet)
# Order matters to ensure the correct occurrence is found if duplicates exist.
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "lung mass"),
    ("PROC_METHOD", "Bronchoscopy"),
    ("PROC_ACTION", "Therapeutic aspiration"),
    ("PROC_METHOD", "EBUS"),
    ("DEV_INSTRUMENT", "Linear EBUS"),
    ("DEV_INSTRUMENT", "Disposable Bronchoscope"),
    ("OUTCOME_COMPLICATION", "None"), # Under COMPLICATIONS
    ("PROC_ACTION", "therapeutic aspiration"),
    ("ANAT_AIRWAY", "Right Mainstem"),
    ("ANAT_AIRWAY", "Bronchus Intermedius"),
    ("ANAT_AIRWAY", "Left Mainstem"),
    ("MEAS_SIZE", "5 mm"),
    ("PROC_METHOD", "EBUS"), # In "Lymph node sizing was performed by EBUS"
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "25-gauge Needle"),
    ("DEV_NEEDLE", "22-gauge Needle"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "11Rs"),
    ("OBS_ROSE", "Positive for malignancy"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("ANAT_LN_STATION", "11Rs"), # Site 1
    ("MEAS_SIZE", "=> 10 mm"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "transbronchial biopsies"),
    ("OBS_ROSE", "not adequate"),
    ("ANAT_LN_STATION", "4R"), # Site 2
    ("MEAS_SIZE", "=> 10 mm"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "transbronchial biopsies"),
    ("OBS_ROSE", "adequate"),
    ("OBS_ROSE", "Positive for malignancy"),
    ("OUTCOME_COMPLICATION", "no immediate complications"),
    ("ANAT_LN_STATION", "11R"),
    ("ANAT_LN_STATION", "4R"),
    ("PROC_METHOD", "bronchoscopy"),
    ("OBS_LESION", "lung mass")
]

# Paths
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILE_NER_DATASET = OUTPUT_DIR / "ner_dataset_all.jsonl"
FILE_NOTES = OUTPUT_DIR / "notes.jsonl"
FILE_SPANS = OUTPUT_DIR / "spans.jsonl"
FILE_STATS = OUTPUT_DIR / "stats.json"
FILE_LOG = OUTPUT_DIR / "alignment_warnings.log"


def main():
    print(f"Processing Note ID: {NOTE_ID}...")
    
    # 1. Calculate Indices
    spans = []
    search_start_index = 0
    
    for label, text_snippet in ENTITIES_TO_EXTRACT:
        start = RAW_TEXT.find(text_snippet, search_start_index)
        
        if start == -1:
            # Fallback: restart search from 0 if not found (in case order in list is wrong)
            # ideally, the list should be ordered by appearance.
            start = RAW_TEXT.find(text_snippet)
            if start == -1:
                print(f"CRITICAL WARNING: Could not find '{text_snippet}' in text. Skipping.")
                continue
        
        end = start + len(text_snippet)
        
        # Verify alignment
        extracted = RAW_TEXT[start:end]
        if extracted != text_snippet:
            with open(FILE_LOG, "a") as log:
                log.write(f"[{datetime.datetime.now()}] MISMATCH: {NOTE_ID} | Label: {label} | Expected: '{text_snippet}' | Found: '{extracted}'\n")
            continue

        span_obj = {
            "start": start,
            "end": end,
            "label": label,
            "text": text_snippet
        }
        spans.append(span_obj)
        
        # Move search index forward to avoid re-matching the same instance 
        # (only if we assume strict sequential ordering in ENTITIES_TO_EXTRACT)
        # To be safe against out-of-order lists, we generally don't enforce this strictly 
        # unless we are sure of the list order. 
        # Given the list above is roughly chronological, we update search_start_index
        # but slightly conservatively to allow overlaps if necessary (though rare in NER).
        search_start_index = start + 1

    print(f"Extracted {len(spans)} valid entities.")

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": spans
    }
    
    with open(FILE_NER_DATASET, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(FILE_NOTES, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    new_span_lines = []
    for s in spans:
        span_id = f"{s['label']}_{s['start']}"
        span_entry = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": s['label'],
            "text": s['text'],
            "start": s['start'],
            "end": s['end']
        }
        new_span_lines.append(json.dumps(span_entry))
        
    with open(FILE_SPANS, "a", encoding="utf-8") as f:
        for line in new_span_lines:
            f.write(line + "\n")

    # 5. Update stats.json
    if FILE_STATS.exists():
        with open(FILE_STATS, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Fallback if stats file doesn't exist
        stats = {
            "total_files": 0, 
            "total_notes": 0, 
            "total_spans_raw": 0, 
            "total_spans_valid": 0, 
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)

    # Update label counts
    for s in spans:
        lbl = s['label']
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1

    with open(FILE_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("Success. Files updated.")

if __name__ == "__main__":
    main()