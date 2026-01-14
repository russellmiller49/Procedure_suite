import json
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_189"
TIMESTAMP = datetime.datetime.now().isoformat()

# Target Directories
# Script location: data/granular_annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# RAW TEXT CONTENT
# ==============================================================================
# Cleaned text from note_189.txt (Sources tags removed)
RAW_TEXT = """NOTE_ID:  note_189 SOURCE_FILE: note_189.txt Procedure Name: EBUS bronchoscopy, radial EBUS guided bronchoscopy
Indications: Pulmonary nodule requiring diagnosis/staging.
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree the Q190 video bronchoscope was introduced through the mouth.
The vocal cords appeared normal. The subglottic space was normal. The trachea is of normal caliber. The carina was sharp.
All left and right sided airways were normal without endobronchial disease to the first segmental branch.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 11L, station 7, 10R 11Rs lymph nodes.
Sampling by transbronchial needle aspiration was performed in these lymph nodes using an Olympus EBUSTBNA 22 gauge needle beginning at the N3 (11L) lymph nodes -->7-->11Rs-->10R.
Further details regarding nodal size and number of samples are included in the attached EBUS procedural sheet.
All samples were sent for routine cytology. Onsite path eval did not identify malignancy.
We then removed the EBUS bronchoscopy and the ultrathin bronchoscope was inserted and based on anatomical knowledge advanced into the right middle lobe to the area of known nodule using radial EBUS confirmed a concentric view within the lesion.
Biopsies were then performed with a variety of instruments to include peripheral needle, forceps and brush.
After adequate samples were obtained the bronchoscope was removed. While emerging from anesthesia patient had large volume emesis and possible aspiration event.
He was immediately placed on right side. He transiently became hypoxic but saturations improved relatively quickly.
Patinet was then transferred to the PACU. X-ray was performed which right greater than left patchy opacities with increased pulmonary vasculature and interstitial markings alone with a small right apical pneumothorax.
Right sided airspace opacities, although possibly representing aspiration event, are more likely related to retained saline instilled during bronchoscopy and is not unexpected.
Patient was informed of pneumothorax. He was hemodynamically stable and oxygenating well.
Repeat CXR 1 hour later showed no expansion of pneumothorax and decision was made to observe for expansion and not place chest tube unless he develops symptoms or has expansion of pneumothorax.
Complications: 
1.	Small left apical pneumothorax
2.	Post procedure emesis with possible aspiration  
Estimated Blood Loss: Less than 10 cc.
Recommendations:
- Admit to IM for overnight observation
- Repeat CXR in 4 hours and then AM if not changes
- Consider diuresis given pulmonary edema and Systolic heart failure
- Continue to hold Plavix for now.
- Would NOT treat with antibiotics 
- Await final pathology"""

# ==============================================================================
# ENTITY MAPPING
# ==============================================================================
# List of (Label, Substring) to map. 
# The script will locate the exact offsets dynamically to ensure alignment.
ENTITIES_TO_MAP = [
    ("PROC_METHOD", "EBUS"), # First EBUS in Procedure Name
    ("PROC_ACTION", "bronchoscopy"),
    ("PROC_METHOD", "radial EBUS"),
    ("PROC_ACTION", "bronchoscopy"), # Second bronchoscopy
    ("OBS_LESION", "Pulmonary nodule"),
    ("MEDICATION", "Propofol"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "left and right sided airways"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # Second mention
    ("ANAT_LN_STATION", "station 11L"),
    ("ANAT_LN_STATION", "station 7"),
    ("ANAT_LN_STATION", "10R"),
    ("ANAT_LN_STATION", "11Rs"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "Olympus EBUSTBNA 22 gauge needle"),
    ("ANAT_LN_STATION", "11L"), # Inside N3 (11L)
    ("ANAT_LN_STATION", "7"), # In arrow list
    ("ANAT_LN_STATION", "11Rs"), # In arrow list
    ("ANAT_LN_STATION", "10R"), # In arrow list
    ("OBS_ROSE", "malignancy"), # Context: "did not identify malignancy"
    ("DEV_INSTRUMENT", "ultrathin bronchoscope"),
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("OBS_LESION", "nodule"),
    ("PROC_METHOD", "radial EBUS"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_NEEDLE", "peripheral needle"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "brush"),
    ("OBS_LESION", "pneumothorax"), # First mention (small right apical...)
    ("OBS_LESION", "pneumothorax"), # informed of...
    ("OBS_LESION", "pneumothorax"), # no expansion of...
    ("OBS_LESION", "pneumothorax"), # expansion of...
    ("OUTCOME_COMPLICATION", "Small left apical pneumothorax"), # In Complications list
    ("OUTCOME_COMPLICATION", "emesis"), # Post procedure emesis
    ("OUTCOME_COMPLICATION", "aspiration"), # with possible aspiration
    ("MEAS_VOL", "10 cc"),
]

# ==============================================================================
# PROCESSING LOGIC
# ==============================================================================

def update_dataset():
    entities = []
    current_search_index = 0
    label_counts = {}
    
    # 1. Calculate Offsets
    for label, substr in ENTITIES_TO_MAP:
        start_idx = RAW_TEXT.find(substr, current_search_index)
        
        if start_idx == -1:
            # Fallback search from beginning if not found strictly sequentially 
            # (though strictly sequential is preferred for this note's flow)
            start_idx = RAW_TEXT.find(substr)
            
        if start_idx == -1:
            print(f"WARNING: Could not find '{substr}' in text. Skipping.")
            with open(LOG_PATH, "a") as log:
                log.write(f"{datetime.datetime.now()} - Missing entity: {substr} ({label})\n")
            continue

        end_idx = start_idx + len(substr)
        
        # Verify alignment
        extracted = RAW_TEXT[start_idx:end_idx]
        if extracted != substr:
             print(f"ERROR: Mismatch at {start_idx}. Expected '{substr}', got '{extracted}'")
             continue

        # Add to list
        entities.append({
            "start": start_idx,
            "end": end_idx,
            "label": label,
            "text": substr
        })
        
        # Update counts
        label_counts[label] = label_counts.get(label, 0) + 1
        
        # Advance search index to avoid re-matching the same instance
        current_search_index = end_idx

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
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
        for ent in entities:
            span_id = f"{ent['label']}_{ent['start']}"
            span_entry = {
                "span_id": span_id,
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
        # Fallback if file doesn't exist (though it should)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0, 
            "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    for label, count in label_counts.items():
        if label in stats["label_counts"]:
            stats["label_counts"][label] += count
        else:
            stats["label_counts"][label] = count

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {NOTE_ID}. Added {len(entities)} entities.")

if __name__ == "__main__":
    update_dataset()