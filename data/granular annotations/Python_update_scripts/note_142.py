import json
import os
import datetime
from pathlib import Path

# --- CONFIGURATION ---
NOTE_ID = "note_142"
SOURCE_FILE = "note_142.txt"

# The raw text content of the note
RAW_TEXT = """Procedure Name: Bronchoscopy

Indications:

Hilar mass

Anesthesia:
General anesthesia with topical anesthesia using 2% lidocaine to the tracheobronchial tree (8 mL).
See anesthesia record for administered medications.

Pre-Procedure Assessment

The procedure, including risks, benefits, and alternatives, was explained to the patient.
All questions were answered, and informed consent was obtained and documented per institutional protocol.
A history and physical examination were performed and updated in the pre-procedure assessment record.
Relevant laboratory studies and radiographic imaging were reviewed. A procedural time-out was performed prior to the intervention.
Following administration of intravenous anesthetic medications and topical anesthesia to the upper airway and tracheobronchial tree, the Q180 slim video bronchoscope was introduced through the mouth via a laryngeal mask airway and advanced into the tracheobronchial tree.
The UC180F convex probe EBUS bronchoscope was subsequently introduced through the mouth via the laryngeal mask airway and advanced into the tracheobronchial tree.
The patient tolerated the procedure well.

Procedure Description and Findings

The laryngeal mask airway was in normal position.
The vocal cords moved normally with respiration. The subglottic space was normal.
The trachea was of normal caliber, and the carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa and anatomy were normal, with no endobronchial lesions identified, except for extrinsic compression of the left upper lobe posterior segment.
No significant secretions were present.

Endobronchial Ultrasound Findings

The bronchoscope was withdrawn and replaced with the EBUS bronchoscope to perform ultrasound evaluation.
A systematic hilar and mediastinal lymph node survey was conducted, revealing visible lymph nodes.
Lymph node sizing and sampling were performed using endobronchial ultrasound with an Olympus EBUS-TBNA 22-gauge needle.
Specimens were sent for routine cytopathologic evaluation.

The left upper lobe mass measured 24.2 mm by EBUS and 24 mm by CT.
PET imaging was not available. On ultrasound, the mass appeared hypoechoic, heterogeneous, irregularly shaped, with sharp margins.
Multiple surrounding vessels were noted, limiting safe needle trajectory. A small window for safe needle access was identified, and the mass was biopsied with a single pass using a 22-gauge needle.
ROSE preliminary analysis demonstrated atypical cells. However, brisk bleeding occurred following the first needle pass, and no additional ultrasound-guided passes were performed.
An esophageal approach was attempted but did not allow adequate visualization of the mass.
The EBUS bronchoscope was withdrawn, and a therapeutic bronchoscope was introduced.
A conventional TBNA was attempted in the region of extrinsic compression in the left upper lobe posterior segment;
however, the return was bloody, and no further passes were performed.

All samples were sent to cytopathology for review.
Complications

No immediate complications.

Estimated Blood Loss

Less than 5 mL.

Impression

Normal bronchoscopic examination except for extrinsic compression of the left upper lobe posterior segment

Lymph node sizing and limited sampling performed via EBUS-TBNA

Post-Procedure Diagnosis

Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsy

The patient remained stable throughout the procedure and was transferred in good condition to the post-bronchoscopy recovery area for observation until discharge criteria were met.
Preliminary findings were discussed with the patient. Follow-up with the requesting service for final cytology results was recommended."""

# Extracted Entities List
# Structure: (label, text_fragment)
# Note: Offsets will be calculated dynamically to avoid manual error.
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Hilar mass"),
    ("PROC_METHOD", "General anesthesia"),
    ("PROC_METHOD", "topical anesthesia"),
    ("MEDICATION", "lidocaine"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("MEAS_VOL", "8 mL"),
    ("PROC_METHOD", "intravenous anesthetic"),
    ("PROC_METHOD", "topical anesthesia"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q180 slim video bronchoscope"),
    ("ANAT_AIRWAY", "mouth"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "mouth"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "Bronchial"),
    ("OBS_LESION", "endobronchial lesions"),
    ("OBS_FINDING", "extrinsic compression"),
    ("ANAT_LUNG_LOC", "left upper lobe posterior segment"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("DEV_INSTRUMENT", "EBUS bronchoscope"),
    ("PROC_METHOD", "ultrasound"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal lymph node"),
    ("OBS_FINDING", "visible lymph nodes"),
    ("PROC_ACTION", "sizing"),
    ("PROC_ACTION", "sampling"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("DEV_NEEDLE", "Olympus EBUS-TBNA 22-gauge needle"),
    ("OBS_LESION", "left upper lobe mass"),
    ("MEAS_SIZE", "24.2 mm"),
    ("PROC_METHOD", "EBUS"),
    ("MEAS_SIZE", "24 mm"),
    ("PROC_METHOD", "CT"),
    ("PROC_METHOD", "PET"),
    ("PROC_METHOD", "ultrasound"),
    ("OBS_LESION", "mass"),
    ("PROC_ACTION", "biopsied"),
    ("MEAS_COUNT", "single pass"),
    ("DEV_NEEDLE", "22-gauge needle"),
    ("OBS_ROSE", "atypical cells"),
    ("OBS_FINDING", "bleeding"),
    ("MEAS_COUNT", "first needle pass"),
    ("PROC_METHOD", "ultrasound-guided"),
    ("ANAT_AIRWAY", "esophageal"),
    ("OBS_LESION", "mass"),
    ("DEV_INSTRUMENT", "EBUS bronchoscope"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("PROC_ACTION", "TBNA"),
    ("OBS_FINDING", "extrinsic compression"),
    ("ANAT_LUNG_LOC", "left upper lobe posterior segment"),
    ("OBS_FINDING", "return was bloody"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "Less than 5 mL"),
    ("OBS_FINDING", "extrinsic compression"),
    ("ANAT_LUNG_LOC", "left upper lobe posterior segment"),
    ("PROC_ACTION", "sizing"),
    ("PROC_ACTION", "sampling"),
    ("PROC_ACTION", "EBUS-TBNA"),
    ("PROC_METHOD", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "biopsy")
]

# --- DIRECTORY SETUP ---
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"

# --- HELPER FUNCTIONS ---

def find_entity_spans(raw_text, entities):
    """
    Finds start/end indices for entities in the text.
    Handles multiple occurrences by tracking search position.
    """
    spans = []
    search_start_map = {}  # Tracks last found position for each unique entity text to handle duplicates

    for label, entity_text in entities:
        start_search_at = search_start_map.get(entity_text, 0)
        
        start = raw_text.find(entity_text, start_search_at)
        
        if start == -1:
            # If not found after the previous occurrence, try from beginning (in case of out-of-order definition in list)
            # or log a warning. For this script, we assume strict order or non-overlapping enough to find.
            # Fallback: simple find from 0 if not found from last pos (rare case in linear extraction).
            start = raw_text.find(entity_text)
            if start == -1:
                print(f"WARNING: Entity '{entity_text}' not found in text.")
                continue

        end = start + len(entity_text)
        
        # Verify alignment
        extracted = raw_text[start:end]
        if extracted != entity_text:
            print(f"CRITICAL ERROR: Mismatch at {start}:{end} expected '{entity_text}' got '{extracted}'")
            continue

        spans.append({
            "label": label,
            "text": entity_text,
            "start": start,
            "end": end
        })
        
        # Update search start to avoid re-matching the same instance if text repeats
        search_start_map[entity_text] = end

    return spans

def update_jsonl(file_path, new_record):
    """Appends a JSON line to the file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def update_stats(file_path, new_spans):
    """Updates the stats.json file."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
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
    stats["total_files"] += 1  # Assuming 1 note per file for this script context
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

def log_alignment(file_path, spans, raw_text):
    """Logs alignment checks."""
    with open(file_path, 'a', encoding='utf-8') as f:
        for span in spans:
            start, end = span['start'], span['end']
            original = raw_text[start:end]
            if original != span['text']:
                log_msg = f"MISMATCH: Note {NOTE_ID} | Label {span['label']} | Exp: '{span['text']}' | Got: '{original}'\n"
                f.write(log_msg)

# --- MAIN EXECUTION ---

def main():
    print(f"Processing Note ID: {NOTE_ID}...")
    
    # 1. Calculate Spans
    final_spans_data = find_entity_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Records
    # ner_dataset_all.jsonl record
    # Strict Schema: {"id": NOTE_ID, "text": RAW_TEXT, "entities": [[start, end, label], ...]}
    ner_entities = [[s['start'], s['end'], s['label']] for s in final_spans_data]
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": ner_entities
    }

    # notes.jsonl record
    notes_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # 3. Write to Files
    print(f"Appending to {NER_DATASET_PATH}...")
    update_jsonl(NER_DATASET_PATH, ner_record)

    print(f"Appending to {NOTES_PATH}...")
    update_jsonl(NOTES_PATH, notes_record)

    print(f"Appending to {SPANS_PATH}...")
    # spans.jsonl requires individual span objects
    for s in final_spans_data:
        span_record = {
            "span_id": f"{s['label']}_{s['start']}",
            "note_id": NOTE_ID,
            "label": s['label'],
            "text": s['text'],
            "start": s['start'],
            "end": s['end']
        }
        update_jsonl(SPANS_PATH, span_record)

    # 4. Update Stats
    print(f"Updating stats at {STATS_PATH}...")
    update_stats(STATS_PATH, final_spans_data)

    # 5. Log Alignments
    print(f"Verifying alignments in {ALIGNMENT_LOG_PATH}...")
    log_alignment(ALIGNMENT_LOG_PATH, final_spans_data, RAW_TEXT)

    print("Success. Pipeline updated.")

if __name__ == "__main__":
    main()