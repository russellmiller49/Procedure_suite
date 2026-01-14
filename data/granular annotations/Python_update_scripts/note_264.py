import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_264"

# Raw text content from the provided file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Endotracheal tumor 
POSTOPERATIVE DIAGNOSIS:  Endotracheal tumor s/p debulking 
PROCEDURE PERFORMED: 
1.         Rigid bronchoscopy with endoluminal tumor ablation(CPT 31641)
INDICATIONS: Tracheal Obstruction  
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives and paralytics the flexible bronchoscope was inserted through the LMA and into the pharynx.
We then advanced the bronchoscope into the subglottic space. Approximately 2.5 cm distal to the vocal cords There were 3 polypoid lesions at the same level blocking about 90% of the airway during exhalation which moved in a ball valve fashion with inhalation resulting in about 50% obstruction of the airway.
Additionally there were multiple small polypoid (> 50) lesions surrounding distal to the lesion originating from all parts of the airway (Anterior trachea, posterior trachea, lateral trachea) which terminated about 1cm proximal to the main carina.
The right sided and left sided airways to at least the first sub-segments were uninvolved with no evidence of endobronchial tumor or extrinsic obstruction.
The flexible bronchoscope and LMA were removed and a 10mm non-ventilating rigid tracheoscope was subsequently inserted into the proximal trachea just proximal to the tumor and connected to ventilator.
The T190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and the electrocautery snare was used to transect the large polypoid lesions beginning with the 3 proximal obstructive lesions and the lesions once free from the wall were easily removed from the airway with suction and collected for pathological assessment.
After these lesions were removed about 10 other lesions in the airway which were anatomically amenable to snare were removed in the same fashion.
We then used APC to paint and shave the remaining tumor area on the posterior and lateral trachea walls until we were satisfied that we had achieved adequate luminal recanalization.
At the end of the procedure the trachea was approximately 90% open in comparison to unaffected areas.
The rigid bronchoscope was then removed, and the procedure was completed. There were no complications.
Of note we considered airway stent placement as a barrier effect  as the lesions regrew very quickly (< 3 months) after the previous bronchoscopic debulking procedure however in our discussions with the patient prior to the procedure he expressed reluctance to have stent placed due to possible cough associated with the stent and the fact that he only restarted chemotherapy 2 weeks ago.
I suspect that these lesions will recur unless he has a profound response to systemic treatment and possible radiation and if I need to debulk again I will strongly advocate for placement of a covered tracheal stent.
Recommendations: 
•	Transfer patient back to ward room 
•	Await final pathology results  
•	Will need to speak with oncology regarding other treatment options which might include PDT or brachytherapy."""

# Extracted Entities based on Label_guide_UPDATED.csv
# Format: (start_offset, end_offset, label)
# Offsets calculated based on the RAW_TEXT string above.
ENTITIES_DATA = [
    (115, 133, "PROC_METHOD"), # Rigid bronchoscopy
    (139, 165, "PROC_ACTION"), # endoluminal tumor ablation
    (226, 244, "PROC_METHOD"), # General Anesthesia
    (384, 405, "DEV_INSTRUMENT"), # flexible bronchoscope
    (429, 432, "ANAT_AIRWAY"), # LMA
    (446, 453, "ANAT_AIRWAY"), # pharynx
    (473, 485, "DEV_INSTRUMENT"), # bronchoscope
    (495, 511, "ANAT_AIRWAY"), # subglottic space
    (547, 558, "ANAT_AIRWAY"), # vocal cords
    (572, 588, "OBS_LESION"), # polypoid lesions
    (619, 636, "OUTCOME_AIRWAY_LUMEN_PRE"), # 90% of the airway
    (710, 725, "OUTCOME_AIRWAY_LUMEN_PRE"), # 50% obstruction
    (777, 793, "OBS_LESION"), # polypoid (> 50)
    (888, 904, "ANAT_AIRWAY"), # Anterior trachea
    (906, 923, "ANAT_AIRWAY"), # posterior trachea
    (925, 940, "ANAT_AIRWAY"), # lateral trachea
    (987, 998, "ANAT_AIRWAY"), # main carina
    (1004, 1015, "ANAT_AIRWAY"), # right sided
    (1020, 1030, "ANAT_AIRWAY"), # left sided
    (1031, 1038, "ANAT_AIRWAY"), # airways
    (1106, 1125, "OBS_LESION"), # endobronchial tumor
    (1156, 1177, "DEV_INSTRUMENT"), # flexible bronchoscope
    (1182, 1185, "ANAT_AIRWAY"), # LMA
    (1208, 1212, "MEAS_AIRWAY_DIAM"), # 10mm
    (1229, 1248, "DEV_INSTRUMENT"), # rigid tracheoscope
    (1280, 1296, "ANAT_AIRWAY"), # proximal trachea
    (1363, 1395, "DEV_INSTRUMENT"), # T190 Olympus flexible bronchoscope
    (1426, 1444, "DEV_INSTRUMENT"), # rigid bronchoscope
    (1453, 1473, "DEV_INSTRUMENT"), # electrocautery snare
    (1505, 1521, "OBS_LESION"), # polypoid lesions
    (1540, 1559, "OBS_LESION"), # obstructive lesions
    (1568, 1575, "OBS_LESION"), # lesions
    (1682, 1689, "OBS_LESION"), # lesions
    (1705, 1712, "OBS_LESION"), # lesions
    (1716, 1726, "ANAT_AIRWAY"), # the airway
    (1756, 1761, "DEV_INSTRUMENT"), # snare
    (1804, 1807, "PROC_METHOD"), # APC
    (1863, 1868, "OBS_LESION"), # tumor
    (1881, 1898, "ANAT_AIRWAY"), # posterior ... trachea
    (1903, 1918, "ANAT_AIRWAY"), # lateral trachea
    (2028, 2035, "ANAT_AIRWAY"), # trachea
    (2054, 2062, "OUTCOME_AIRWAY_LUMEN_POST"), # 90% open
    (2102, 2120, "DEV_INSTRUMENT"), # rigid bronchoscope
    (2186, 2202, "OUTCOME_COMPLICATION"), # No complications
    (2228, 2240, "DEV_STENT"), # airway stent
    (2284, 2291, "OBS_LESION"), # lesions
    (2341, 2364, "CTX_HISTORICAL"), # previous bronchoscopic
    (2365, 2374, "PROC_ACTION"), # debulking
    (2470, 2475, "DEV_STENT"), # stent
    (2519, 2524, "DEV_STENT"), # stent
    (2596, 2603, "OBS_LESION"), # lesions
    (2746, 2752, "PROC_ACTION"), # debulk
    (2796, 2818, "DEV_STENT"), # covered tracheal stent
    (2937, 2940, "PROC_METHOD"), # PDT
    (2944, 2957, "PROC_METHOD"), # brachytherapy
]

# ==========================================
# PATH SETUP
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = OUTPUT_DIR / "stats.json"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def update_stats(new_labels):
    """Updates the stats.json file with new file and label counts."""
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    else:
        # Initialize default stats structure if missing
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

    # Update global counters
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    
    # Update label counts
    for label in new_labels:
        stats["total_spans_raw"] += 1
        stats["total_spans_valid"] += 1
        current_count = stats["label_counts"].get(label, 0)
        stats["label_counts"][label] = current_count + 1

    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def append_jsonl(file_path, data):
    """Appends a dictionary as a JSON line to a file."""
    with open(file_path, 'a') as f:
        f.write(json.dumps(data) + '\n')

def validate_and_process():
    """Main processing logic."""
    print(f"Processing {NOTE_ID}...")
    
    # 1. Validate alignment and prepare entities
    valid_entities = []
    labels_found = []
    
    for start, end, label in ENTITIES_DATA:
        span_text = RAW_TEXT[start:end]
        
        # Validation check
        if not span_text:
            msg = f"[{datetime.datetime.now()}] Warning: Empty span for {label} at {start}:{end} in {NOTE_ID}"
            print(msg)
            with open(LOG_FILE, "a") as log:
                log.write(msg + "\n")
            continue

        # Create entity object
        entity_obj = {
            "start": start,
            "end": end,
            "label": label,
            "text": span_text
        }
        valid_entities.append(entity_obj)
        labels_found.append(label)

        # Append to spans.jsonl
        span_record = {
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": span_text,
            "start": start,
            "end": end
        }
        append_jsonl(SPANS_FILE, span_record)

    # 2. Update ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": valid_entities
    }
    append_jsonl(NER_DATASET_FILE, ner_record)

    # 3. Update notes.jsonl
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    append_jsonl(NOTES_FILE, note_record)

    # 4. Update stats.json
    update_stats(labels_found)

    print(f"Successfully processed {NOTE_ID}. Added {len(valid_entities)} entities.")

if __name__ == "__main__":
    try:
        validate_and_process()
    except Exception as e:
        print(f"Error processing {NOTE_ID}: {e}")