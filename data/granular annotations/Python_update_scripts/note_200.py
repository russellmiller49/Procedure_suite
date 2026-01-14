from pathlib import Path
import json
import os
import datetime

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
NOTE_ID = "note_200"
RAW_TEXT = """NOTE_ID:  note_200 SOURCE_FILE: note_200.txt Procedure Name: Medical Thoracoscopy (pleuroscopy)
Indications: Right sided Pleural effusion
Medications: As per anesthesia record
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. The patient was placed on the standard procedural bed in the left lateral decubitus position and sites of compression were well padded.
The pleural entry site was identified by means of the ultrasound.
The patient was sterilely prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual fashion.
The entry sites was infiltrated with a 10mL solution of 1% lidocaine.
Following instillation of subcutaneous lidocaine a 1.5 cm subcutaneous incision was made and gentle dissection was performed until the pleural space was entered.
An 8 mm disposable primary port was then placed on the left side at the 6th anterior axillary line.
After allowing air entrainment and lung deflation, suction was applied through the port to remove pleural fluid with removal of approximately 1600cc of serosanguinous fluid.
The rigid pleuroscopy telescope was then introduced through the trocar and advanced into the pleural space.
The pleura was had diffuse carcinomatosis with multiple hard white pleural nodules covering the parietal and visceral pleura.
No adhesions were present Biopsies of the abnormal areas in the parietal pleura posteriorly were performed with forceps and sent for histopathological and microbiological examination with approximately 12 total biopsies taken.
There was minimal bleeding associated with the biopsies. After residual bleeding had subsided, the pleuroscopy telescope was then removed and a 15.5 pleural catheter was placed into the pleural space through the primary port with tunneling anteriorly.
Complications: None
The patient tolerated the procedural well.
Post-procedure chest radiograph showed mild post-procedural subcutaneous air with full lung re-expansion and IPC in place
Estimated Blood Loss: 15cc
Post Procedure Diagnosis: Pleural effusion 
Recommendation:
Will await pathology and microbiological studies
Patient education on pleural catheter draining and will next week for initial drainage."""

# Entity definitions based on Label_guide_UPDATED.csv
# Format: (Label, Text Span)
# Note: For duplicate strings, we'll implement a mechanism to find the correct one.
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "Medical Thoracoscopy (pleuroscopy)"),
    ("LATERALITY", "Right sided"),
    ("OBS_LESION", "Pleural effusion"), # First occurrence in Indications
    ("ANAT_PLEURA", "pleural entry site"),
    ("PROC_METHOD", "ultrasound"),
    ("MEAS_VOL", "10mL"),
    ("MEDICATION", "1% lidocaine"),
    ("MEAS_SIZE", "1.5 cm"),
    ("ANAT_PLEURA", "pleural space"), # First occurrence
    ("MEAS_SIZE", "8 mm"),
    ("DEV_INSTRUMENT", "primary port"),
    ("LATERALITY", "left side"),
    ("ANAT_PLEURA", "6th anterior axillary line"),
    ("PROC_ACTION", "remove"),
    ("MEAS_VOL", "1600cc"),
    ("DEV_INSTRUMENT", "rigid pleuroscopy telescope"),
    ("ANAT_PLEURA", "pleural space"), # Second occurrence (advanced into...)
    ("OBS_LESION", "diffuse carcinomatosis"),
    ("OBS_LESION", "pleural nodules"),
    ("ANAT_PLEURA", "parietal and visceral pleura"),
    ("PROC_ACTION", "Biopsies"),
    ("ANAT_PLEURA", "parietal pleura posteriorly"),
    ("DEV_INSTRUMENT", "forceps"),
    ("MEAS_COUNT", "12"),
    ("DEV_INSTRUMENT", "pleuroscopy telescope"),
    ("DEV_CATHETER_SIZE", "15.5"),
    ("DEV_CATHETER", "pleural catheter"),
    ("ANAT_PLEURA", "pleural space"), # Third occurrence (placed into...)
    ("OUTCOME_COMPLICATION", "None"),
    ("OBS_FINDING", "subcutaneous air"),
    ("OUTCOME_PLEURAL", "lung re-expansion"),
    ("DEV_CATHETER", "IPC"),
    ("MEAS_VOL", "15cc")
]

# ----------------------------------------------------------------------------------
# DYNAMIC PATH SETUP
# ----------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
WARNINGS_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------
def find_nth_occurrence(substring, text, n=1):
    """Finds the start index of the nth occurrence of a substring."""
    start = -1
    for _ in range(n):
        start = text.find(substring, start + 1)
        if start == -1:
            return -1
    return start

def update_stats(label_counts, total_spans_valid):
    """Updates the stats.json file."""
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}, "hydration_status_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += total_spans_valid
    stats["total_spans_valid"] += total_spans_valid

    for label, count in label_counts.items():
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def main():
    entities = []
    label_counts = {}
    occurrence_map = {} # Track occurrence counts for duplicate strings

    # 1. Calculate Indices
    for label, span_text in ENTITIES_TO_EXTRACT:
        # Determine occurrence number
        if span_text not in occurrence_map:
            occurrence_map[span_text] = 1
        else:
            occurrence_map[span_text] += 1
        
        n = occurrence_map[span_text]
        start_idx = find_nth_occurrence(span_text, RAW_TEXT, n)

        if start_idx == -1:
            print(f"Error: Could not find occurrence {n} of '{span_text}' in text.")
            continue

        end_idx = start_idx + len(span_text)
        
        # Verify alignment
        extracted_text = RAW_TEXT[start_idx:end_idx]
        if extracted_text != span_text:
            with open(WARNINGS_FILE, "a") as f:
                f.write(f"Mismatch: Expected '{span_text}', found '{extracted_text}' at {start_idx}\n")
            continue

        entities.append({
            "label": label,
            "start_offset": start_idx,
            "end_offset": end_idx,
            "span_text": span_text
        })
        
        label_counts[label] = label_counts.get(label, 0) + 1

    # 2. Append to ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    with open(NER_DATASET_FILE, "a") as f:
        f.write(json.dumps(ner_record) + "\n")

    # 3. Append to notes.jsonl
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(NOTES_FILE, "a") as f:
        f.write(json.dumps(note_record) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_FILE, "a") as f:
        for ent in entities:
            span_record = {
                "span_id": f"{ent['label']}_{ent['start_offset']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['span_text'],
                "start": ent['start_offset'],
                "end": ent['end_offset']
            }
            f.write(json.dumps(span_record) + "\n")

    # 5. Update stats.json
    update_stats(label_counts, len(entities))

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    main()