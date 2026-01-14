from pathlib import Path
import json
import os
import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

NOTE_ID = "note_162"

# Definition of the raw text (cleaned of source tags)
RAW_TEXT = """Procedure Name: EBUS Bronchoscopy
Indications: lung cancer diagnosis and staging (left upper lobe tumor)
Medications: General Anesthesia
Procedure performed:
: 31653 bronchoscopy with endobronchial ultrasound (EBUS) guided transbronchial sampling > 2 structures.
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
 Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, except for in the left lower lobe in which the proximal origin was mildly extrinsically compressed.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 11Rs (6.7mm), 10R (5.7mm), 4R (9.1mm), 2R (7.1 mm), 7 (15.7mm), 4L (6.9mm),  and 11L (21.1mm)  lymph nodes.
Sampling by transbronchial needle aspiration was performed beginning with the 11Rs Lymph node followed by 7, and 4R, 2R lymph nodes using an Olympus EBUSTBNA 22 gauge needle.
ROSE showed malignant cells in the 4R and 2R station consistent with N3 disease.
We then moved to the large 11L lymph node and took 8 additional passes for molecular studies.
All samples were sent for routine cytology and a dedicated pass from the 11L was sent for flow cytometry.
The Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: 5 cc.

Post Procedure Recommendations:
- Transfer to post-procedure unit and home per protocol
- Will await final pathology results"""

# Ordered list of entities to extract. 
# Logic: (LABEL, TEXT_STRING)
# The script will locate these sequentially to handle duplicates (e.g., "4R") correctly.
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "EBUS"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("OBS_LESION", "tumor"),
    ("PROC_ACTION", "bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "transbronchial sampling"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
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
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_FINDING", "extrinsically compressed"),
    ("DEV_INSTRUMENT", "video bronchoscope"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("ANAT_LN_STATION", "lymph node"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "11Rs"),
    ("MEAS_SIZE", "6.7mm"),
    ("ANAT_LN_STATION", "10R"),
    ("MEAS_SIZE", "5.7mm"),
    ("ANAT_LN_STATION", "4R"),
    ("MEAS_SIZE", "9.1mm"),
    ("ANAT_LN_STATION", "2R"),
    ("MEAS_SIZE", "7.1 mm"),
    ("ANAT_LN_STATION", "7"),
    ("MEAS_SIZE", "15.7mm"),
    ("ANAT_LN_STATION", "4L"),
    ("MEAS_SIZE", "6.9mm"),
    ("ANAT_LN_STATION", "11L"),
    ("MEAS_SIZE", "21.1mm"),
    ("ANAT_LN_STATION", "lymph nodes"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("ANAT_LN_STATION", "11Rs"),
    ("ANAT_LN_STATION", "7"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "2R"),
    ("ANAT_LN_STATION", "lymph nodes"),
    ("DEV_NEEDLE", "22 gauge needle"),
    ("OBS_ROSE", "malignant cells"),
    ("ANAT_LN_STATION", "4R"),
    ("ANAT_LN_STATION", "2R"),
    ("ANAT_LN_STATION", "11L"),
    ("MEAS_COUNT", "8"),
    ("ANAT_LN_STATION", "11L"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("OBS_FINDING", "blood"),
    ("OBS_FINDING", "secretions"),
    ("OBS_FINDING", "active bleeding"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "5 cc"),
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_spans(text, entity_definitions):
    """
    Calculates start/end indices for entities.
    Maintains a cursor to ensure we find the *next* occurrence of a term 
    to handle duplicates (e.g. '4R' appearing multiple times) correctly.
    """
    spans = []
    cursor = 0
    
    for label, substr in entity_definitions:
        # Search from current cursor position
        start = text.find(substr, cursor)
        
        if start == -1:
            # If not found sequentially, log a strict error (or retry from 0 if out of order)
            # For this pipeline, we assume the list above is in order of appearance.
            print(f"CRITICAL WARNING: Could not find '{substr}' after index {cursor}")
            continue
            
        end = start + len(substr)
        
        span_obj = {
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        }
        spans.append(span_obj)
        
        # Update cursor to end of this find to ensure next search is forward-looking
        # We assume entities do not overlap in a way that breaks this logic 
        # (nested entities are okay if the inner one appears later in list, 
        # but typically NER lists are sorted by start_char).
        # To be safe for close proximity, we move cursor to start + 1 or end.
        cursor = start + 1 

    return spans

def update_jsonl(path, data):
    """Appends a single JSON object as a new line."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(path, new_spans):
    """Updates the stats.json file."""
    if not path.exists():
        stats = {
            "total_notes": 0, 
            "total_files": 0, 
            "total_spans_raw": 0, 
            "total_spans_valid": 0,
            "label_counts": {}
        }
    else:
        with open(path, 'r', encoding='utf-8') as f:
            stats = json.load(f)

    stats["total_notes"] += 1
    stats["total_files"] += 1  # Assuming 1 note per file context
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def validate_alignment(text, spans):
    """Checks if span indices match the text content."""
    warnings = []
    for span in spans:
        sliced = text[span["start"]:span["end"]]
        if sliced != span["text"]:
            warnings.append(f"MISMATCH {span['span_id']}: Expected '{span['text']}', found '{sliced}'")
    
    if warnings:
        with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as f:
            for w in warnings:
                f.write(f"{datetime.datetime.now().isoformat()} - {NOTE_ID} - {w}\n")

# =============================================================================
# EXECUTION
# =============================================================================

def main():
    # 1. Calculate Indices
    spans = calculate_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    # Schema: {"id": ..., "text": ..., "entities": [[start, end, label], ...]}
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in spans]
    }
    update_jsonl(OUTPUT_DIR / "ner_dataset_all.jsonl", ner_entry)

    # 3. Update notes.jsonl
    notes_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    update_jsonl(OUTPUT_DIR / "notes.jsonl", notes_entry)

    # 4. Update spans.jsonl
    for span in spans:
        update_jsonl(OUTPUT_DIR / "spans.jsonl", span)

    # 5. Update stats.json
    update_stats(OUTPUT_DIR / "stats.json", spans)

    # 6. Validate
    validate_alignment(RAW_TEXT, spans)
    
    print(f"Successfully processed {NOTE_ID} with {len(spans)} entities.")

if __name__ == "__main__":
    main()