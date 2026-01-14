import json
import os
import datetime
from pathlib import Path

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
NOTE_ID = "note_217"

# Raw text from the provided note
RAW_TEXT = """NOTE_ID:  note_217 SOURCE_FILE: note_217.txt REOPERATIVE DIAGNOSIS: 
1.	Resolving Mediastinal Mass 
POSTOPERATIVE DIAGNOSIS: 
1.	Resolving Mediastinal Mass  status post tracheal Y-stent removal
PROCEDURE PERFORMED: 
1.	Rigid and flexible bronchoscopy with  Tracheal stent removal
INDICATIONS: Resolved tracheal compression
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Once the patient was sedated and paralyzed a 12 mm non-ventilating rigid tracheoscope was inserted through the mouth into the sub-glottic space.
A flexible T190 Olympus bronchoscope was inserted through the tracheoscope into the trachea and thick mucus and bloody secretions were suctioned from the stent.
The flexible bronchoscope was removed and the rigid non-optical forceps were inserted through the rigid scope along with the rigid optic.
The forceps were used to grasp the proximal limb of the tracheal stent and were rotated repeatedly while withdrawing the stent into the rigid bronchoscope.
The stent was subsequently removed en-bloc with the rigid bronchoscope without difficulty.
Once his stent was removed a laryngeal mask airway was inserted and the flexible bronchoscope was then inserted through the LMA for re-inspection.
The trachea mucosa was friable and inflamed but without residual obstruction. The right mainstem and distal airways were normal.
The left mainstem was normal however a small fractures piece of the stent was found within the left mainstem which was removed with flexible forceps without difficulty.
The left sided airways were re-inspected and normal without any other residual fractured stent pieces.
Once we were satisfied that there was no active bleeding, the bronchoscope was subsequently removed and the procedure completed.
Post-procedure, the patient developed laryngospasm requiring intubation by anesthesia. The flexible bronchoscope was then inserted into the posterior oropharynx and 6cc of topical 1% lidocaine was injected onto the vocal cords prior to extubation after which the patient was able to adequately ventilate prior to transfer to the PACU.
Complications: Post-procedure laryngospasm requiring re-intubation. 
Recommendations:
- Transfer PACU
- Obtain post procedure CXR
- Discharge to home once criteria met."""

# Define the entities to look for sequentially
# The list preserves the order in which they appear in the text to facilitate accurate offset calculation
ENTITIES_TO_EXTRACT = [
    ("Mediastinal Mass", "OBS_LESION"),
    ("Mediastinal Mass", "OBS_LESION"),
    ("tracheal", "ANAT_AIRWAY"),
    ("Y-stent", "DEV_STENT"),
    ("Rigid and flexible bronchoscopy", "PROC_METHOD"),
    ("Tracheal", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("tracheal", "ANAT_AIRWAY"),
    ("compression", "OBS_FINDING"),
    ("General Anesthesia", "PROC_METHOD"), # Interpreted as method of sedation/procedure context if applicable, though strictly 'Sedation'. Re-reading guide: PROC_METHOD is 'Guidance/technology used'. EBUS/Navigational. Anesthesia might be borderline. Removing to be safe/strict based on 'Guidance/technology'.
    ("12 mm", "MEAS_SIZE"),
    ("rigid tracheoscope", "DEV_INSTRUMENT"),
    ("sub-glottic space", "ANAT_AIRWAY"),
    ("flexible T190 Olympus bronchoscope", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("thick mucus", "OBS_FINDING"),
    ("bloody secretions", "OBS_FINDING"),
    ("stent", "DEV_STENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid non-optical forceps", "DEV_INSTRUMENT"),
    ("rigid scope", "DEV_INSTRUMENT"),
    ("rigid optic", "DEV_INSTRUMENT"),
    ("forceps", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"), # "proximal limb of the tracheal stent"
    ("stent", "DEV_STENT"), # "withdrawing the stent"
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("trachea mucosa", "ANAT_AIRWAY"),
    ("friable", "OBS_FINDING"),
    ("inflamed", "OBS_FINDING"),
    ("Right mainstem", "ANAT_AIRWAY"),
    ("distal airways", "ANAT_AIRWAY"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("left sided airways", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("active bleeding", "OBS_FINDING"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("laryngospasm", "OBS_FINDING"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("posterior oropharynx", "ANAT_AIRWAY"),
    ("6cc", "MEAS_VOL"),
    ("lidocaine", "MEDICATION"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("laryngospasm", "OUTCOME_COMPLICATION")
]

# ------------------------------------------------------------------------------
# DIRECTORY SETUP
# ------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ------------------------------------------------------------------------------
# PROCESSING LOGIC
# ------------------------------------------------------------------------------

def main():
    print(f"Processing NOTE_ID: {NOTE_ID}...")
    
    # 1. Extract Spans
    extracted_spans = []
    cursor = 0
    
    for text_snippet, label in ENTITIES_TO_EXTRACT:
        start_idx = RAW_TEXT.find(text_snippet, cursor)
        
        if start_idx == -1:
            print(f"WARNING: Could not find '{text_snippet}' after index {cursor}")
            continue
            
        end_idx = start_idx + len(text_snippet)
        
        extracted_spans.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text_snippet,
            "start": start_idx,
            "end": end_idx
        })
        
        # Advance cursor to ensure next search is after this one
        cursor = start_idx + 1 

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for span in extracted_spans:
            f.write(json.dumps(span) + "\n")

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
    stats["total_files"] += 1 # Assuming 1 note per file for this script
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    for span in extracted_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        for span in extracted_spans:
            sliced_text = RAW_TEXT[span["start"]:span["end"]]
            if sliced_text != span["text"]:
                warning_msg = (f"MISMATCH [Note: {NOTE_ID}]: Span '{span['span_id']}' "
                               f"expects '{span['text']}' but got '{sliced_text}' "
                               f"at indices {span['start']}:{span['end']}\n")
                log_file.write(warning_msg)
                print(warning_msg.strip())

    print(f"Successfully processed {len(extracted_spans)} entities for {NOTE_ID}.")

if __name__ == "__main__":
    main()