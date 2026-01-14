import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_136"

# The raw text from the provided file
RAW_TEXT = """Procedure Performed:
Flexible bronchoscopy with endobronchial ultrasound–guided transbronchial needle aspiration

Indication:
Diagnostic evaluation and mediastinal staging

Medications:
General anesthesia
Topical anesthesia: Lidocaine 2%, 10 mL to the tracheobronchial tree

The procedure, including risks, benefits, and alternatives, was explained to the patient.
All questions were answered, and informed consent was obtained and documented per institutional protocol.
A history and physical examination were performed and updated in the pre-procedure assessment record.
Pertinent laboratory studies and imaging were reviewed. A procedural time-out was performed.
Following administration of intravenous medications per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree, a Q180 slim video bronchoscope was introduced orally via a laryngeal mask airway and advanced into the tracheobronchial tree.
Subsequently, a UC180F convex-probe EBUS bronchoscope was introduced orally via the laryngeal mask airway and advanced into the tracheobronchial tree.
The patient tolerated the procedure well.

Airway Examination

The laryngeal mask airway was in good position.
The vocal cords moved normally with respiration. The subglottic space was normal.
The trachea was of normal caliber, and the carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa and anatomy were normal, with no endobronchial lesions or significant secretions.
A bronchial stump was noted without evidence of recurrence.

Endobronchial Ultrasound Findings and Sampling

The bronchoscope was withdrawn and replaced with the EBUS bronchoscope to perform ultrasound evaluation.
A systematic mediastinal and hilar lymph node survey was conducted.
Lymph node sizing and sampling were performed for non–small cell lung cancer staging using an Olympus 22-gauge EBUS-TBNA needle.
Samples were obtained from the following stations and sent for routine cytology:

Station 4L (left lower paratracheal):
Measured 4.6 mm by EBUS and 5 mm by CT;
PET negative. On ultrasound, the lymph node appeared hypoechoic, heterogeneous, irregularly shaped, with sharp margins.
The node was biopsied using a 22-gauge needle. A total of five needle passes were obtained.
Rapid on-site evaluation indicated adequate tissue.

Station 5 (subaortic):
Measured 20.7 mm by EBUS and 24.1 mm by CT; PET positive.
This node was accessed via the esophagus and biopsy was technically challenging.
On ultrasound, the lymph node appeared hypoechoic, heterogeneous, irregularly shaped, with sharp margins.
The node was biopsied using a 22-gauge needle. A total of eight needle passes were obtained.
Rapid on-site evaluation was suspicious for malignancy.

All samples were submitted to cytopathology for review.
Complications:
None immediate

Estimated Blood Loss:
<5 mL

Post-Procedure Diagnosis:

Technically successful flexible bronchoscopy with EBUS-guided transbronchial needle aspiration

Normal endobronchial examination

Mediastinal lymph node sampling performed

Disposition:
The patient remained stable and was transferred in good condition to the bronchoscopy recovery area, where he will be observed until discharge criteria are met.
Preliminary findings were discussed with the patient. Follow-up with the requesting service for final pathology results was recommended.
Recommendations:

Await cytology results

Consider CT-guided biopsy if EBUS sampling is nondiagnostic"""

# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# ENTITY DEFINITIONS
# ==========================================
# We define the entities strictly based on Label_guide_UPDATED.csv
# Order matters here for sequential searching in the text to handle duplicates correctly.

ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "Flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("MEDICATION", "Lidocaine"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # In medications section
    ("DEV_INSTRUMENT", "Q180 slim video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # In insertion section
    ("DEV_INSTRUMENT", "UC180F convex-probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # In examination section
    ("ANAT_AIRWAY", "Bronchial mucosa"),
    ("ANAT_AIRWAY", "bronchial stump"),
    ("DEV_NEEDLE", "22-gauge"), # In general description
    # Station 4L Block
    ("ANAT_LN_STATION", "Station 4L"),
    ("MEAS_SIZE", "4.6 mm"),
    ("MEAS_SIZE", "5 mm"),
    ("OBS_FINDING", "hypoechoic"),
    ("OBS_FINDING", "heterogeneous"),
    ("OBS_FINDING", "irregularly shaped"),
    ("OBS_FINDING", "sharp margins"),
    ("DEV_NEEDLE", "22-gauge"), # Specific to 4L
    ("MEAS_COUNT", "five"),
    ("OBS_ROSE", "adequate tissue"),
    # Station 5 Block
    ("ANAT_LN_STATION", "Station 5"),
    ("MEAS_SIZE", "20.7 mm"),
    ("MEAS_SIZE", "24.1 mm"),
    ("OBS_FINDING", "hypoechoic"),
    ("OBS_FINDING", "heterogeneous"),
    ("OBS_FINDING", "irregularly shaped"),
    ("OBS_FINDING", "sharp margins"),
    ("DEV_NEEDLE", "22-gauge"), # Specific to Station 5
    ("MEAS_COUNT", "eight"),
    ("OBS_ROSE", "suspicious for malignancy"),
    # Post-procedure section
    ("PROC_METHOD", "flexible bronchoscopy"), # Lowercase in diagnosis
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("OUTCOME_COMPLICATION", "None immediate") # Complications section
]

# ==========================================
# PROCESSING LOGIC
# ==========================================

def get_entities_with_indices(text, entity_list):
    """
    Finds entities in text sequentially to ensure correct indices for duplicates.
    Returns a list of dicts suitable for the JSONL format.
    """
    results = []
    search_cursor = 0
    
    for label, span_text in entity_list:
        start = text.find(span_text, search_cursor)
        
        if start == -1:
            # Fallback: if not found relative to cursor, try from beginning (safety net)
            # but ideally we want sequential processing.
            start = text.find(span_text)
            if start == -1:
                print(f"WARNING: Could not find span '{span_text}' in text.")
                continue
        
        end = start + len(span_text)
        
        results.append({
            "start": start,
            "end": end,
            "label": label,
            "text": span_text
        })
        
        # Move cursor to end of this found entity to find the next one (if it appears later)
        # We only move forward if the next entity is expected to be after this one.
        # Given the list is ordered by appearance, we update the cursor.
        search_cursor = start + 1

    return results

def update_files():
    # 1. Extract Entities
    entities = get_entities_with_indices(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
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
        for ent in entities:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
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
        # Fallback if file doesn't exist (though strictly it should based on input)
        stats = {
            "total_files": 0,
            "successful_files": 0,
            "total_notes": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "alignment_warnings": 0,
            "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)

    for ent in entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validation & Logging
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        for ent in entities:
            extracted = RAW_TEXT[ent['start']:ent['end']]
            if extracted != ent['text']:
                log.write(f"[{datetime.datetime.now()}] ALIGNMENT ERROR: {NOTE_ID} - Expected '{ent['text']}' but got '{extracted}' at {ent['start']}:{ent['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")

if __name__ == "__main__":
    update_files()