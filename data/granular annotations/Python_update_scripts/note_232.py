import json
import os
import datetime
from pathlib import Path

# =============================================================================
# 1. CONFIGURATION & PATH SETUP
# =============================================================================
NOTE_ID = "note_232"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# 2. RAW TEXT CONTENT
# =============================================================================
# Exact text from the provided note
RAW_TEXT = """NOTE_ID:  note_232 SOURCE_FILE: note_232.txt PREOPERATIVE DIAGNOSIS: Lung cancer with tumor obstruction of bronchus intermedius
POSTOPERATIVE DIAGNOSIS: Malignant mixed intrinsic and extrinsic airway obstruction
PROCEDURE PERFORMED: Rigid bronchoscopy
INDICATIONS: Tumor obstruction of bronchus intermedius  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following induction and paralyitic administration by anesthesia a 12 mm ventilating rigid bronchoscope was inserted into the mid trachea and attached to the jet ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope.
On initial bronchoscopic inspection the trachea, left lung and right upper lobe appeared normal without evidence of endobronchial disease.
Just distal to the right upper lobe orifice in the bronchus intermedius there was extensive endobronchial tumor causing complete airway obstruction.
At this point the flexible forceps were used to take tissue samples for pathological evaluation and tumor markers.
We then began to slowly debulk the endobronchial tumor through the use of a combination of APC, cryotherapy and forceps.
A small opening was identified leading to the right lower lobe bronchus and an ultrathin bronchospe was advanced through the opening and purulent material was expressed from the distal airways from related to post-obstructive pneumonia.
We were able to visualize the secondary carina’s within the right lower lobe (basilar segments) with the exception of the superior segment which could not be identified as well and the right middle lobe.
We continued to debulk the tumor and utilizing an 8-9-10 CRE balloon were able to achieve approximately 90% recanalization of the broncus intermedius and the proximal right lower lobe orifice however there was extensive tumor infiltration deep into all of the right lower lobe segments.
The right middle lobe orifice was encased with extensive tumor and we could only achieve about 15% recanalization.
Infiltrating friable areas of tumor were painted with argon plasma coagulation for hemostasis.
Due to the extent of tumor within the distal airways we did not believe that airway stent placement would be appropriate as distal tumor ingrowth would likely occur.
Once we were satisfied that there was no active bleeding the rigid bronchoscope was removed and the procedure was completed.
Recommendations:
Await tissue diagnosis for confirmation of recurrence and molecular studies.
We expect the obstruction to recur due to the extent of tumor involvement.
Will discuss with patients primary oncologist regarding options for systemic therapy."""

# =============================================================================
# 3. ENTITY DATA
# =============================================================================
# List of entities to extract. 
# Format: (Label, substring, occurrence_index)
# occurrence_index: 0 for 1st match, 1 for 2nd match, etc.
TARGET_ENTITIES = [
    ("OBS_LESION", "Lung cancer", 0),
    ("OBS_LESION", "tumor", 0),
    ("ANAT_AIRWAY", "bronchus intermedius", 0),
    ("OBS_LESION", "airway obstruction", 0),
    ("PROC_METHOD", "Rigid", 0),
    ("PROC_ACTION", "bronchoscopy", 0),
    ("OBS_LESION", "Tumor", 0), # Case sensitive search handled in logic
    ("ANAT_AIRWAY", "bronchus intermedius", 1),
    ("MEAS_SIZE", "12 mm", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 1),
    ("ANAT_AIRWAY", "trachea", 1),
    ("ANAT_LUNG_LOC", "left lung", 0),
    ("ANAT_LUNG_LOC", "right upper lobe", 0),
    ("ANAT_LUNG_LOC", "right upper lobe", 1),
    ("ANAT_AIRWAY", "bronchus intermedius", 2),
    ("OBS_LESION", "tumor", 2),
    ("OBS_LESION", "airway obstruction", 1),
    ("DEV_INSTRUMENT", "flexible forceps", 0),
    ("PROC_ACTION", "debulk", 0),
    ("OBS_LESION", "tumor", 3),
    ("PROC_ACTION", "APC", 0),
    ("PROC_ACTION", "cryotherapy", 0),
    ("DEV_INSTRUMENT", "forceps", 1),
    ("ANAT_LUNG_LOC", "right lower lobe", 0),
    ("DEV_INSTRUMENT", "ultrathin bronchospe", 0), # Matches typo in note
    ("OBS_FINDING", "purulent material", 0),
    ("ANAT_AIRWAY", "distal airways", 0),
    ("ANAT_LUNG_LOC", "right lower lobe", 1),
    ("ANAT_LUNG_LOC", "basilar segments", 0),
    ("ANAT_LUNG_LOC", "superior segment", 0),
    ("ANAT_LUNG_LOC", "right middle lobe", 0),
    ("PROC_ACTION", "debulk", 1),
    ("OBS_LESION", "tumor", 4),
    ("DEV_INSTRUMENT", "balloon", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "90% recanalization", 0),
    ("ANAT_AIRWAY", "broncus intermedius", 0), # Matches typo in note
    ("ANAT_LUNG_LOC", "right lower lobe", 2),
    ("OBS_LESION", "tumor infiltration", 0),
    ("ANAT_LUNG_LOC", "right lower lobe", 3),
    ("ANAT_LUNG_LOC", "right middle lobe", 1),
    ("OBS_LESION", "tumor", 6),
    ("OUTCOME_AIRWAY_LUMEN_POST", "15% recanalization", 0),
    ("OBS_LESION", "tumor", 7),
    ("PROC_ACTION", "argon plasma coagulation", 0),
    ("OBS_LESION", "tumor", 8),
    ("ANAT_AIRWAY", "distal airways", 1),
    ("DEV_STENT", "airway stent", 0),
    ("OBS_LESION", "tumor", 9),
    ("OBS_FINDING", "active bleeding", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 2),
    ("OBS_LESION", "obstruction", 2),
    ("OBS_LESION", "tumor", 10)
]

def find_entity_spans(text, targets):
    """
    Locates exact start/end indices for targets within the text.
    Handles multiple occurrences by tracking current search position.
    """
    spans = []
    # To handle occurrences, we can't just find all at once. 
    # We need to iterate through the text to find the Nth occurrence.
    
    # Sort targets by their appearance in text to ensure correct indexing? 
    # Actually, we need to find the specific Nth instance requested.
    
    # We can pre-calculate all occurrences of every substring
    import re
    
    for label, substr, nth in targets:
        # Escape regex special characters in the substring
        pattern = re.escape(substr)
        # Find all matches
        matches = [m for m in re.finditer(pattern, text)]
        
        if nth < len(matches):
            match = matches[nth]
            spans.append({
                "label": label,
                "start": match.start(),
                "end": match.end(),
                "text": substr
            })
        else:
            print(f"WARNING: Could not find occurrence {nth} of '{substr}' in text.")
            
    # Sort spans by start index
    spans.sort(key=lambda x: x["start"])
    return spans

# =============================================================================
# 4. PROCESSING LOGIC
# =============================================================================

def update_ner_pipeline():
    # 1. Calculate Spans
    entities = find_entity_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # Format for ner_dataset_all.jsonl: [start, end, label]
    formatted_entities = [[e["start"], e["end"], e["label"]] for e in entities]
    
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": formatted_entities
    }

    # 2. Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    notes_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(notes_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for ent in entities:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent["label"],
                "text": ent["text"],
                "start": ent["start"],
                "end": ent["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

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
    # Assuming one file per note for this context, or reusing file count
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)

    for ent in entities:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    # 6. Validation Log
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        for ent in entities:
            extracted_text = RAW_TEXT[ent["start"]:ent["end"]]
            if extracted_text != ent["text"]:
                log.write(f"[{datetime.datetime.now()}] MISMATCH: Note {NOTE_ID}, Label {ent['label']}. Expected '{ent['text']}', found '{extracted_text}' at {ent['start']}:{ent['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    update_ner_pipeline()