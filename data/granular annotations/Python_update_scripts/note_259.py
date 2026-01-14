from pathlib import Path
import json
import os
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_259"

# Raw text content exactly as provided in the source file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Malignant central airway obstruction. 
POSTOPERATIVE DIAGNOSIS: 
1.	Intraoperative death.
CPT Codes:
CPT 31640: Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed; with excision of tumor.
CPT 31645: bronchoscopy with therapeutic aspiration
CPT 31630 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with tracheal/bronchial dilation or closed reduction of fracture
CPT 32556 Chest tube insertion- left side
CPT 32556 Chest tube insertion- right side

PROCEDURE PERFORMED: Rigid bronchoscopy with endobronchial debulking and balloon dilatation.
INDICATIONS: Right mainstem endobronchial obstruction 
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient’s family acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the distal trachea and advanced into the distal trachea before attaching the monsoon JET ventilator.
The T180 theraputic flexible bronchoscope was insterted through the rigid bronchoscope and airway inspection was performed.
The proximal and mid trachea were normal. There was tumor infiltration within the distal trachea just proximal to the main carina on the right lateral wall with slowly oozing blood visualized.
That main carina was involved on the right side. The left sided aiways were normal.
The proximal right mainstem was completely obstructed with friable enbdobronchial tumor APC was used to burn and shave the tumor and flexible forceps were used for biopsy.
As we slowly debulked the tumor it became clear that the involvement was extensive.
Using the P90 slim bronchoscope we were able to bypass tumor using saline aliquots to stent the airway open and eventually could visualize the basilar segments of the lower lobe where persistent tumor was seen.
Using a forgery balloon and the pullback method we were able to dilate the airway slightly and then using an 8,9,10 CRE balloon gently dilated the BI and RLL bronchus.
While bleeding was encountered it was not brisk and was controlled with tropical TXA, epi and cold saline.
While considering stent placement the patient’s blood pressure began to slowly drop despite increasing vasopressor requirement and patient went into PEA/Asystole.
Code blue was called and CRP initiated. A left sided chest tube was placed and there was no gush of air concerning for PTX.
Ultrasound showed no cardiac motion and no evidence of pericardial effusion.
Patient received multiple doses of epinephrine and chest compressions but remained in non-shockable rhythm (asystole).
Decision was made to attempt TPA given that all other H’s and T’s were considered and not apparent.
This did not have any effect. While we were confident that a right sided PTX was not present (lung completely obstructed by tumor and atelectatic) A right sided chest tube was placed to attempt to offload pressure from known pleural effusion again without response.
At hat 15:10 after approximately 30 minutes of CPR the patient was declared dead.
Family was notified and handled information appropriately. Medical examiner was contacted and declined case.
Complications:  Intra-operative death (direct cause unclear)"""

# Ordered list of entities to match sequentially
# Format: (Label, Text Snippet)
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Malignant central airway obstruction"),
    ("OUTCOME_COMPLICATION", "Intraoperative death"),
    ("PROC_ACTION", "Bronchoscopy"),
    ("PROC_ACTION", "excision"),
    ("OBS_LESION", "tumor"),
    ("PROC_ACTION", "bronchoscopy"),
    ("PROC_ACTION", "therapeutic aspiration"),
    ("PROC_ACTION", "Bronchoscopy"),
    ("PROC_ACTION", "tracheal/bronchial dilation"),
    ("PROC_ACTION", "closed reduction"),
    ("PROC_ACTION", "Chest tube insertion"),
    ("PROC_ACTION", "Chest tube insertion"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "endobronchial debulking"),
    ("PROC_ACTION", "balloon dilatation"),
    ("ANAT_AIRWAY", "Right mainstem"),
    ("OBS_LESION", "endobronchial obstruction"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("DEV_INSTRUMENT", "monsoon JET ventilator"),
    ("DEV_INSTRUMENT", "T180 theraputic flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "proximal and mid trachea"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "main carina"),
    ("ANAT_AIRWAY", "right lateral wall"),
    ("ANAT_AIRWAY", "main carina"),
    ("ANAT_AIRWAY", "left sided aiways"),
    ("ANAT_AIRWAY", "proximal right mainstem"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "APC"),
    ("PROC_ACTION", "burn"),
    ("PROC_ACTION", "shave"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("PROC_ACTION", "biopsy"),
    ("PROC_ACTION", "debulked"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "P90 slim bronchoscope"),
    ("OBS_LESION", "tumor"),
    ("ANAT_LUNG_LOC", "basilar segments"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "forgery balloon"),
    ("PROC_ACTION", "dilate"),
    ("MEAS_SIZE", "8,9,10"),
    ("DEV_INSTRUMENT", "CRE balloon"),
    ("PROC_ACTION", "dilated"),
    ("ANAT_AIRWAY", "BI"),
    ("ANAT_AIRWAY", "RLL bronchus"),
    ("OUTCOME_COMPLICATION", "bleeding"),
    ("MEDICATION", "TXA"),
    ("MEDICATION", "epi"),
    ("MEDICATION", "saline"),
    ("PROC_ACTION", "stent placement"),
    ("MEDICATION", "vasopressor"),
    ("OUTCOME_COMPLICATION", "PEA/Asystole"),
    ("DEV_CATHETER", "chest tube"),
    ("OBS_FINDING", "PTX"),
    ("MEDICATION", "epinephrine"),
    ("PROC_ACTION", "chest compressions"),
    ("OUTCOME_COMPLICATION", "asystole"),
    ("MEDICATION", "TPA"),
    ("OBS_FINDING", "PTX"),
    ("OBS_LESION", "tumor"),
    ("DEV_CATHETER", "chest tube"),
    ("OBS_FINDING", "pleural effusion"),
    ("CTX_TIME", "15:10"),
    ("CTX_TIME", "30 minutes"),
    ("PROC_ACTION", "CPR"),
    ("OUTCOME_COMPLICATION", "Intra-operative death"),
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"


def find_offsets_sequential(text, entities):
    """
    Finds start/end offsets for a list of entity text snippets, 
    searching sequentially to handle duplicates.
    """
    results = []
    current_pos = 0
    
    for label, snippet in entities:
        # Find next occurrence of snippet starting from current_pos
        start = text.find(snippet, current_pos)
        
        if start == -1:
            # If not found, log warning and skip (critical for data integrity)
            warning = f"WARNING: Could not find '{snippet}' after index {current_pos}"
            print(warning)
            with open(ALIGNMENT_LOG_PATH, "a") as f:
                f.write(f"{datetime.datetime.now()} - {warning}\n")
            continue
            
        end = start + len(snippet)
        
        results.append({
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": snippet,
            "start": start,
            "end": end
        })
        
        # Advance current_pos to avoid finding the same instance again 
        # (unless we want overlap, but usually we move past)
        current_pos = start + 1 
        
    return results

def update_ner_dataset(entities):
    """Updates ner_dataset_all.jsonl"""
    file_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
    
    # Construct the JSON object
    data = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": []
    }
    
    for e in entities:
        data["entities"].append({
            "start": e["start"],
            "end": e["end"],
            "label": e["label"]
        })
        
    with open(file_path, "a") as f:
        f.write(json.dumps(data) + "\n")

def update_notes_file():
    """Updates notes.jsonl"""
    file_path = OUTPUT_DIR / "notes.jsonl"
    data = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(file_path, "a") as f:
        f.write(json.dumps(data) + "\n")

def update_spans_file(entities):
    """Updates spans.jsonl"""
    file_path = OUTPUT_DIR / "spans.jsonl"
    with open(file_path, "a") as f:
        for e in entities:
            f.write(json.dumps(e) + "\n")

def update_stats_file(entities):
    """Updates stats.json"""
    file_path = OUTPUT_DIR / "stats.json"
    
    if file_path.exists():
        with open(file_path, "r") as f:
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
    stats["total_files"] += 1 # Assuming 1 note = 1 file in this context
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    for e in entities:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(file_path, "w") as f:
        json.dump(stats, f, indent=2)

def validate_alignment(entities):
    """Checks exact text matches."""
    with open(ALIGNMENT_LOG_PATH, "a") as f:
        for e in entities:
            extracted = RAW_TEXT[e["start"]:e["end"]]
            if extracted != e["text"]:
                msg = f"MISMATCH: ID {e['span_id']} expected '{e['text']}' but got '{extracted}'"
                print(msg)
                f.write(f"{datetime.datetime.now()} - {msg}\n")

def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Calculate Indices
    entities_with_indices = find_offsets_sequential(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Validate
    validate_alignment(entities_with_indices)
    
    # 3. Update Files
    update_ner_dataset(entities_with_indices)
    update_notes_file()
    update_spans_file(entities_with_indices)
    update_stats_file(entities_with_indices)
    
    print("Success. Files updated.")

if __name__ == "__main__":
    main()