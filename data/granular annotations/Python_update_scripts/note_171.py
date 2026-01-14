from pathlib import Path
import json
import os
import datetime

# --- Configuration & Path Setup ---
NOTE_ID = "note_171"

# The raw text content of the note
RAW_TEXT = """Procedure Name: EBUS bronchoscopy
Indications: Pulmonary nodule requiring diagnosis/staging.
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree the Q190 video bronchoscope was introduced through the mouth.
The vocal cords appeared normal. The subglottic space was normal. The trachea is of normal caliber. The carina was sharp.
All left sided airways were normal without endobronchial disease to the first segmental branch.
The right upper and lower lobe airways were normal without endobronchial disease to the first segmental branch.
Within the right middle lobe a shiny vascular obstructive endobronchial tumor was visualized within the lateral segment of the right middle lobe.
The lesion was friable and bled easily with minimal manipulation. Subsequently 6 endobronchial needle biopsies of the nodule were performed.
Due to bleeding from the lesion a total of 4ml of 10mg/10ml tranexamic acid was applied topically with subsequent resolution of bleeding.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 4L, station 4R, station 7 and station 11Rs lymph nodes.
Sampling by transbronchial needle aspiration was performed in these lymph nodes using an Olympus EBUSTBNA 22 gauge needle beginning at the N3 (4L) lymph nodes 74R11Rs.
Further details regarding nodal size and number of samples are included in the EBUS procedural sheet in AHLTA.
All samples were sent for routine cytology. Onsite path evaluation did not identify malignancy.
We then removed the EBUS bronchoscopy and inserted the therapeutic T190 Olympus bronchoscope and advanced the scope into the right middle lobe where 5 forceps endobronchial biopsies were performed.
Bleeding was moderate and required intermittent mechanical tamponade with the tip of the bronchoscope.
After biopsies were completed we monitored for evidence of active bleeding and none was seen.
At this point the bronchoscope was removed and the procedure completed. 

Complications: 
-None 
Estimated Blood Loss:  10 cc.
Recommendations:
- Transfer to PACU
- Await biopsy results 
- Discharge home once criteria met."""

# Entity extraction based on Label_guide_UPDATED.csv
ENTITIES = [
    {"start": 16, "end": 33, "label": "PROC_METHOD"}, # EBUS bronchoscopy
    {"start": 48, "end": 64, "label": "OBS_LESION"}, # Pulmonary nodule
    {"start": 107, "end": 115, "label": "MEDICATION"}, # Propofol
    {"start": 540, "end": 545, "label": "ANAT_AIRWAY"}, # mouth
    {"start": 551, "end": 562, "label": "ANAT_AIRWAY"}, # vocal cords
    {"start": 583, "end": 599, "label": "ANAT_AIRWAY"}, # subglottic space
    {"start": 615, "end": 622, "label": "ANAT_AIRWAY"}, # trachea
    {"start": 649, "end": 655, "label": "ANAT_AIRWAY"}, # carina
    {"start": 672, "end": 690, "label": "ANAT_AIRWAY"}, # left sided airways
    {"start": 766, "end": 804, "label": "ANAT_AIRWAY"}, # right upper and lower lobe airways
    {"start": 871, "end": 888, "label": "ANAT_LUNG_LOC"}, # right middle lobe
    {"start": 924, "end": 943, "label": "OBS_LESION"}, # endobronchial tumor
    {"start": 967, "end": 999, "label": "ANAT_LUNG_LOC"}, # lateral segment of the right middle lobe
    {"start": 1006, "end": 1012, "label": "OBS_LESION"}, # lesion
    {"start": 1088, "end": 1089, "label": "MEAS_COUNT"}, # 6
    {"start": 1090, "end": 1119, "label": "PROC_ACTION"}, # endobronchial needle biopsies
    {"start": 1127, "end": 1133, "label": "OBS_LESION"}, # nodule
    {"start": 1169, "end": 1177, "label": "OBS_FINDING"}, # bleeding
    {"start": 1187, "end": 1193, "label": "OBS_LESION"}, # lesion
    {"start": 1205, "end": 1208, "label": "MEAS_VOL"}, # 4ml
    {"start": 1222, "end": 1237, "label": "MEDICATION"}, # tranexamic acid
    {"start": 1269, "end": 1277, "label": "OBS_FINDING"}, # bleeding
    {"start": 1348, "end": 1365, "label": "PROC_METHOD"}, # EBUS bronchoscope
    {"start": 1394, "end": 1399, "label": "ANAT_AIRWAY"}, # mouth
    {"start": 1423, "end": 1445, "label": "ANAT_AIRWAY"}, # tracheobronchial tree
    {"start": 1460, "end": 1465, "label": "ANAT_LN_STATION"}, # hilar
    {"start": 1470, "end": 1492, "label": "ANAT_LN_STATION"}, # mediastinal lymph node
    {"start": 1533, "end": 1536, "label": "MEAS_SIZE"}, # 5mm
    {"start": 1567, "end": 1577, "label": "ANAT_LN_STATION"}, # station 4L
    {"start": 1579, "end": 1589, "label": "ANAT_LN_STATION"}, # station 4R
    {"start": 1591, "end": 1600, "label": "ANAT_LN_STATION"}, # station 7
    {"start": 1605, "end": 1617, "label": "ANAT_LN_STATION"}, # station 11Rs
    {"start": 1618, "end": 1629, "label": "ANAT_LN_STATION"}, # lymph nodes
    {"start": 1643, "end": 1675, "label": "PROC_ACTION"}, # transbronchial needle aspiration
    {"start": 1697, "end": 1708, "label": "ANAT_LN_STATION"}, # lymph nodes
    {"start": 1738, "end": 1746, "label": "DEV_NEEDLE"}, # 22 gauge
    {"start": 1747, "end": 1753, "label": "DEV_NEEDLE"}, # needle
    {"start": 1771, "end": 1773, "label": "ANAT_LN_STATION"}, # N3
    {"start": 1775, "end": 1777, "label": "ANAT_LN_STATION"}, # 4L
    {"start": 1779, "end": 1790, "label": "ANAT_LN_STATION"}, # lymph nodes
    {"start": 1792, "end": 1793, "label": "ANAT_LN_STATION"}, # 7
    {"start": 1794, "end": 1796, "label": "ANAT_LN_STATION"}, # 4R
    {"start": 1797, "end": 1801, "label": "ANAT_LN_STATION"}, # 11Rs
    {"start": 1915, "end": 1922, "label": "SPECIMEN"}, # samples
    {"start": 1937, "end": 1953, "label": "PROC_ACTION"}, # routine cytology
    {"start": 1962, "end": 1983, "label": "OBS_ROSE"}, # Onsite path evaluation
    {"start": 2000, "end": 2010, "label": "OBS_ROSE"}, # malignancy
    {"start": 2027, "end": 2044, "label": "PROC_METHOD"}, # EBUS bronchoscopy
    {"start": 2105, "end": 2122, "label": "ANAT_LUNG_LOC"}, # right middle lobe
    {"start": 2129, "end": 2130, "label": "MEAS_COUNT"}, # 5
    {"start": 2131, "end": 2138, "label": "DEV_INSTRUMENT"}, # forceps
    {"start": 2139, "end": 2160, "label": "PROC_ACTION"}, # endobronchial biopsies
    {"start": 2177, "end": 2185, "label": "OBS_FINDING"}, # Bleeding
    {"start": 2225, "end": 2228, "label": "DEV_INSTRUMENT"}, # tip
    {"start": 2250, "end": 2258, "label": "PROC_ACTION"}, # biopsies
    {"start": 2304, "end": 2312, "label": "OBS_FINDING"}, # bleeding
    {"start": 2406, "end": 2410, "label": "OUTCOME_COMPLICATION"}, # None
    {"start": 2436, "end": 2441, "label": "MEAS_VOL"}, # 10 cc
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def update_ner_dataset():
    """Updates ner_dataset_all.jsonl"""
    file_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
    
    # Transform entities to [start, end, label] format
    entities_list = [[e["start"], e["end"], e["label"]] for e in ENTITIES]
    
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities_list
    }
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes():
    """Updates notes.jsonl"""
    file_path = OUTPUT_DIR / "notes.jsonl"
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans():
    """Updates spans.jsonl"""
    file_path = OUTPUT_DIR / "spans.jsonl"
    
    with open(file_path, "a", encoding="utf-8") as f:
        for entity in ENTITIES:
            # Extract the actual text for the span
            span_text = RAW_TEXT[entity["start"]:entity["end"]]
            
            entry = {
                "span_id": f"{entity['label']}_{entity['start']}",
                "note_id": NOTE_ID,
                "label": entity["label"],
                "text": span_text,
                "start": entity["start"],
                "end": entity["end"]
            }
            f.write(json.dumps(entry) + "\n")

def update_stats():
    """Updates stats.json"""
    file_path = OUTPUT_DIR / "stats.json"
    
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    
    # Update counters
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming one note per file for this script
    stats["total_spans_raw"] += len(ENTITIES)
    stats["total_spans_valid"] += len(ENTITIES)
    
    # Update label counts
    for entity in ENTITIES:
        label = entity["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

def validate_and_log():
    """Validates alignment and logs warnings."""
    log_path = OUTPUT_DIR / "alignment_warnings.log"
    
    with open(log_path, "a", encoding="utf-8") as f:
        for entity in ENTITIES:
            extracted_text = RAW_TEXT[entity["start"]:entity["end"]]
            # Sanity check: if extracted text is empty or index is out of bounds
            if not extracted_text or entity["end"] > len(RAW_TEXT):
                log_entry = f"{datetime.datetime.now().isoformat()} - WARNING: Alignment mismatch in {NOTE_ID} for label {entity['label']} at [{entity['start']}:{entity['end']}]\n"
                f.write(log_entry)

if __name__ == "__main__":
    try:
        print(f"Processing {NOTE_ID}...")
        update_ner_dataset()
        update_notes()
        update_spans()
        update_stats()
        validate_and_log()
        print(f"Success! Data for {NOTE_ID} has been added to {OUTPUT_DIR}")
    except Exception as e:
        print(f"Error: {e}")