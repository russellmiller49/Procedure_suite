import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_254"

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

# ==========================================
# 2. Raw Text Content
# ==========================================
TEXT_CONTENT = """PREOPERATIVE DIAGNOSIS: Lung mass with left main-stem obstruction
POSTOPERATIVE DIAGNOSIS: Malignant mixed intrinsic and extrinsic airway obstruction
PROCEDURE PERFORMED: Rigid bronchoscopy
INDICATIONS: left mainstem obstruction 
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
A 7.0 ETT was placed by ansesthesia followed by OG tube to decompress the stomach.
The ETT was then removed and a 12 mm ventilating rigid bronchoscope was subsequently inserted into the mid trachea and attached to the jet ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope.
On initial bronchoscopic inspection there was mild bleeding and airway trauma noted in the distal trachea likely secondary to trauma from ETT placement.
The posterior and left wall of the distal trachea had obvious submucosal tumor infiltration.
The left mainstem bronchus was completely obstructed by endoluminal tumor and the tumor involved the main carina with a mild degree of tumor ingrowth into the right mainstem but without obstruction.
At this point the EBUS bronchoscope was inserted through the rigid bronchoscope and the subcarinal mass was identified with ultrasound and 6 biopsies were performed with the 22G EBUS TBNA needle.
We then directed our attention to the left maintem. Through the use of a combination of APC, rigid electrocautery, cryotherapy and forcpts we were able to slowly debulk the tumor within the left mainstem and visualize an opening into the distal left mainstem.
A ultrathin bronchospe was advanced through the opening and purulent material was expressed from the distal airways from her post-obstructive pneumonia.
We were able to visualize the secondary carina’s within the left upper lobe and there was no obvious tumor seen.
The left lower lobe was visualized but we were unable to adequately debulk the tumor to overlying this area to confirm distal patency.
Subseuqently the left mainstem bronchus was dilated with an 8-9-10 CRE balloon with approximaly 50% improvement in luminal patency in the left mainstem which allowed introduction of the therapeutic bronchoscope.
At this point the infiltrating friable areas of tumor within the left mainstem, distal trachea and main carina were painted with argon plasma coagulation for hemostasis.
Once we were satisfied that there was no active bleeding the rigid bronchoscope was removed and the procedure was completed.
Recommendations:
Await tissue diagnosis
ASAP radiation oncology consultation for treatment of the left mainstem to attempt to prevent recurrent obstruction.
If patient develops significant hemoptysis post procedure would perform bronchoscopic intubation of the right mainstem to protect functional lung.
If obstruction recurs despite radiation therapy will likely require repeat rigid bronchoscopy with placement of silicone Y stent."""

# ==========================================
# 3. Entity Definitions (Manual Extraction)
# ==========================================
# Mapping entities based on Label_guide_UPDATED.csv
# Format: (Label, Text Search String)
# Note: This list targets specific occurrences in the text.

entity_targets = [
    ("OBS_LESION", "Lung mass"),
    ("ANAT_AIRWAY", "left main-stem"),
    ("OBS_LESION", "Malignant mixed intrinsic and extrinsic airway obstruction"), # Diagnoses often map to lesion/indication logic, though 'obstruction' is complex. 'Malignant... obstruction' describes the lesion effect.
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("ANAT_AIRWAY", "left mainstem"), # "left mainstem obstruction"
    ("PROC_METHOD", "General Anesthesia"),
    ("DEV_INSTRUMENT", "7.0 ETT"),
    ("DEV_INSTRUMENT", "OG tube"),
    ("DEV_INSTRUMENT", "ETT"), # "The ETT was then removed"
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("DEV_INSTRUMENT", "rigid optic"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("OBS_FINDING", "mild bleeding"),
    ("OBS_FINDING", "airway trauma"),
    ("OBS_LESION", "submucosal tumor infiltration"),
    ("ANAT_AIRWAY", "left mainstem bronchus"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely obstructed"),
    ("OBS_LESION", "endoluminal tumor"),
    ("OBS_LESION", "tumor"), # "tumor involved"
    ("ANAT_AIRWAY", "main carina"),
    ("OBS_LESION", "tumor ingrowth"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("PROC_METHOD", "EBUS"), # "EBUS bronchoscope" - extracting method part
    ("DEV_INSTRUMENT", "EBUS bronchoscope"),
    ("ANAT_LN_STATION", "subcarinal"), # "subcarinal mass"
    ("OBS_LESION", "subcarinal mass"),
    ("MEAS_COUNT", "6"), # "6 biopsies"
    ("PROC_ACTION", "biopsies"),
    ("DEV_NEEDLE", "22G EBUS TBNA needle"),
    ("PROC_ACTION", "APC"),
    ("PROC_ACTION", "rigid electrocautery"),
    ("PROC_ACTION", "cryotherapy"),
    ("DEV_INSTRUMENT", "forcpts"), # sic
    ("PROC_ACTION", "debulk"),
    ("DEV_INSTRUMENT", "ultrathin bronchospe"), # sic
    ("OBS_FINDING", "purulent material"),
    ("ANAT_AIRWAY", "distal airways"),
    ("OBS_LESION", "post-obstructive pneumonia"),
    ("ANAT_AIRWAY", "secondary carina’s"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("PROC_ACTION", "dilated"),
    ("DEV_INSTRUMENT", "8-9-10 CRE balloon"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "approximaly 50% improvement in luminal patency"),
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("PROC_ACTION", "painted"),
    ("PROC_ACTION", "argon plasma coagulation"),
    ("OBS_FINDING", "active bleeding"),
    ("PROC_ACTION", "bronchoscopic intubation"),
    ("DEV_STENT", "silicone Y stent")
]

# ==========================================
# 4. Processing Logic
# ==========================================

def find_spans(text, targets):
    """
    Finds start/end indices for target phrases. 
    Handles multiple occurrences by finding the next available index.
    """
    spans = []
    search_start_dict = {} # Track search position for recurring words

    for label, phrase in targets:
        start_search = search_start_dict.get(phrase, 0)
        start_idx = text.find(phrase, start_search)
        
        if start_idx != -1:
            end_idx = start_idx + len(phrase)
            
            # Verify validity
            extracted = text[start_idx:end_idx]
            if extracted != phrase:
                print(f"Warning: Mismatch '{extracted}' vs '{phrase}'")
                continue
                
            spans.append({
                "label": label,
                "text": phrase,
                "start": start_idx,
                "end": end_idx
            })
            
            # Update search cursor for this specific phrase to avoid overlapping same instance
            search_start_dict[phrase] = end_idx
        else:
            with open(LOG_PATH, "a") as f:
                f.write(f"{datetime.datetime.now()} - [WARNING] Phrase not found in NOTE_ID {NOTE_ID}: '{phrase}'\n")
    
    # Sort spans by start index
    spans.sort(key=lambda x: x['start'])
    return spans

def update_jsonl(path, data):
    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")

def update_stats(path, new_spans):
    if os.path.exists(path):
        with open(path, "r") as f:
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
    # total_files stays same if we assume appended to existing file, but we increment for tracking this batch
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans) # Assuming all valid here

    for span in new_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
    
    with open(path, "w") as f:
        json.dump(stats, f, indent=4)

# ==========================================
# 5. Execution
# ==========================================

# Generate Spans
extracted_spans = find_spans(TEXT_CONTENT, entity_targets)

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": TEXT_CONTENT,
    "entities": [
        {"label": s["label"], "start": s["start"], "end": s["end"]} 
        for s in extracted_spans
    ]
}
update_jsonl(NER_DATASET_PATH, ner_entry)

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": TEXT_CONTENT
}
update_jsonl(NOTES_PATH, note_entry)

# 3. Update spans.jsonl
for span in extracted_spans:
    span_entry = {
        "span_id": f"{span['label']}_{span['start']}",
        "note_id": NOTE_ID,
        "label": span["label"],
        "text": span["text"],
        "start": span["start"],
        "end": span["end"]
    }
    update_jsonl(SPANS_PATH, span_entry)

# 4. Update stats.json
update_stats(STATS_PATH, extracted_spans)

# 5. Validation Log
with open(LOG_PATH, "a") as f:
    for span in extracted_spans:
        check_text = TEXT_CONTENT[span["start"]:span["end"]]
        if check_text != span["text"]:
            f.write(f"{datetime.datetime.now()} - [ERROR] Alignment mismatch in {NOTE_ID}: Expected '{span['text']}', found '{check_text}'\n")

print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")