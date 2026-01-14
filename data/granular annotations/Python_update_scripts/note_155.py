import json
import os
import re
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_155"
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text Content
# ==========================================
RAW_TEXT = """Procedure Name: EBUS bronchoscopy, peripheral bronchoscopy
Indications: Pulmonary nodule requiring diagnosis/staging.
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level without endobronchial lesions visualized.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) was met in station 11RS and 7. Sampling by transbronchial needle aspiration was performed using an Olympus EBUSTBNA 22 gauge needle.
Further details regarding nodal size and number of samples are included in the EBUS procedural sheet in AHLTA.
All samples were sent for routine cytology. Onsite path evaluation did not identify malignancy.
The bronchoscope was then removed and the T190 therapeutic video bronchoscope was inserted into the airway and based on anatomical knowledge advanced into the left upper lobe and a large sheath catheter with radial ultrasound to the area of known nodule and a concentric view of the lesion was identified with the radial EBUS.
Biopsies were then performed with a variety of instruments to include peripheral needle forceps and brush with fluoroscopic guidance through the sheath.
After adequate samples were obtained the bronchoscope was removed. ROSE did not identify malignancy on preliminary samples.
The bronchoscope was then removed and the Q190 re-inserted into the airways.
To remove secretions and blood and once confident that there was no active bleeding the bronchoscope was removed and the procedure completed.
Complications: \t
-None 
Estimated Blood Loss:  10 cc.
Recommendations:
- Admit for overnight observation given the late hour of procedural completion
- Await biopsy results 
- Discharge home once criteria met."""

# ==========================================
# 3. Entity Definitions (Label, Text)
# ==========================================
# These map directly to Label_guide_UPDATED.csv
TARGET_ENTITIES = [
    ("PROC_METHOD", "EBUS"),
    ("OBS_LESION", "Pulmonary nodule"),
    ("MEDICATION", "Propofol"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "station 11RS"),
    ("ANAT_LN_STATION", "7"), # station 7
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "22 gauge"),
    ("OBS_ROSE", "malignancy"), # "did not identify malignancy"
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("PROC_METHOD", "radial ultrasound"),
    ("OBS_LESION", "nodule"),
    ("PROC_METHOD", "radial EBUS"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "brush"),
    ("PROC_METHOD", "fluoroscopic guidance"),
    ("OBS_FINDING", "secretions"),
    ("OBS_FINDING", "blood")
]

# ==========================================
# 4. Helper Functions
# ==========================================
def find_entity_spans(text, targets):
    """
    Scans text for target phrases and returns valid span objects.
    Handles multiple occurrences by finding all non-overlapping matches.
    """
    spans = []
    # Sort targets by length (desc) to prioritize longer matches if needed, 
    # though strict exact matching is used here.
    
    # We use a set to track indices we've already covered to prevent overlap if necessary
    # (Simple approach for this data: just find iter)
    
    found_spans = []
    
    for label, substring in targets:
        # Use regex escape to handle potential special chars in medical text
        pattern = re.escape(substring)
        # Word boundary check is safer for short terms like "7"
        if len(substring) < 3:
             # Add strict boundaries for short tokens
             pattern = r'(?<!\w)' + pattern + r'(?!\w)'
        
        for match in re.finditer(pattern, text):
            start = match.start()
            end = match.end()
            span_text = text[start:end]
            
            # Create entity object
            entity = {
                "label": label,
                "text": span_text,
                "start": start,
                "end": end
            }
            found_spans.append(entity)

    # Sort by start index
    found_spans.sort(key=lambda x: x["start"])
    return found_spans

def update_stats(new_labels_count):
    """Updates the stats.json file."""
    if STATS_PATH.exists():
        with open(STATS_PATH, 'r') as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += sum(new_labels_count.values())
    stats["total_spans_valid"] += sum(new_labels_count.values())

    for label, count in new_labels_count.items():
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count

    with open(STATS_PATH, 'w') as f:
        json.dump(stats, f, indent=4)

# ==========================================
# 5. Execution Logic
# ==========================================
def main():
    # 1. Extract Spans
    entities = find_entity_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # Count labels for stats
    label_counts = {}
    for ent in entities:
        lbl = ent["label"]
        label_counts[lbl] = label_counts.get(lbl, 0) + 1

    # 2. Prepare Data Objects
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # 3. Write to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 4. Write to notes.jsonl
    with open(NOTES_PATH, 'a') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 5. Write to spans.jsonl
    with open(SPANS_PATH, 'a') as f:
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

    # 6. Update Stats
    update_stats(label_counts)

    # 7. Validate & Log
    with open(LOG_PATH, 'a') as log_file:
        for ent in entities:
            extracted_text = RAW_TEXT[ent['start']:ent['end']]
            if extracted_text != ent['text']:
                log_msg = f"WARNING: Mismatch in {NOTE_ID}. Span: {ent['label']} ({ent['start']}-{ent['end']}). Expected '{ent['text']}', found '{extracted_text}'\n"
                log_file.write(log_msg)
                print(log_msg)

    print(f"Successfully processed {NOTE_ID}. Artifacts updated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()