import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_193"

# Raw text exactly as provided in the input file
RAW_TEXT = """NOTE_ID:  note_193 SOURCE_FILE: note_193.txt PREOPERATIVE DIAGNOSIS: lung cancer endobronchial tumor obstruction of trachea and right mainstem 
POSTOPERATIVE DIAGNOSIS: Resolved airway obstruction s/p silicone Y-stent
PROCEDURE PERFORMED: Rigid bronchoscopy with tumor debulking and silicone tracheobronchial Y- stent placement 
INDICATIONS: Airway obstruction/hemoptysis
Consent was obtained from the family prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient’s family acknowledged and gave consent.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives the a10mm ventilating rigid bronchoscope was subsequently inserted into the posterior oropharynx.
The ETT was removed and the rigid bronchoscope was advanced past the vocal cords into the mid trachea and connected to ventilator.
Airway inspection was performed using the T190 theraputic flexible bronchoscope. The upper trachea was normal.
The mid trachea had friable tumor mostly at the posterior wall causing about 30% airway obstruction.
The distal trachea had extensive tumor predominantly involving the right lateral and posterior wall and extending into the carina.
The very proximal left mainstem was partially obstructed from tumor infiltration of the main carina.
Beyond this area the left mainstem, left upper and left lower lobe appeared normal without tumor involvement.
At the proximal aspect of the right mainstem was intrinsic tumor causing near complete obstruction (95%).
Tumor extraction was performed using APC and flexible forceps to “burn and shave” the tumor within the trachea and proximal right mainstem.
Once we were able to open the right mainstem up to the point that we could inspect the more distal airways we found extensive circumferential tumor infiltration extending to about 5mm distal to the right upper lobe.
Distally from that point there was no evidence of tumor infiltration. There was extensive tumor within the right upper lobe.
We debulked the right mainstem and proximal BI area in a similar fashion.
We could not make out tissue plains as the tumor had completely infiltrated the airways.
We were able to achieve about 85% opening of the distal tracheal and 50% opening of the right mainstem.
At this point due to significant residual disease and fear that further debulking could result in airway perforation given that the airway tissue planes were completely lost from tumor infiltration the decision was made to place a silicone Y-stent for both improved patency and to prevent tumor ingrowth.
We also decided to extend stent beyond right upper lobe and “jail” the lobe due to tumor extension from within the right upper lobe which extended into the proximal bronchus intermedius.
After measuring the airways we customized a 15x12x12 silicone Y-stent to a length of 80mm in the tracheal limb, 30mm in the right mainstem limb and 30mm in the left mainstem limb.
The rigid bronchoscope was then removed and a 13mm ventilating rigid bronchoscope (required for Y-stent insertion) was inserted through the cords and advanced into the proximal left mainstem and the stent was deployed.
Through the use of rigid forceps, and manipulation with the tip of the flexible bronchoscope we attempted to seed the stent in place however there was significant difficultly getting the right sided limb past the carinal infiltrative tumor and at one point the stent was noted to tear in the right sided limb.
We then removed the stent and inserted another stent of the same size using the same technique.
Again it was extremely difficult to get the stent to seed into proper position however after manipulating the stent with rigid forceps and by manipulation with the tip of the flexible bronchoscope we were eventually able to adequately position the limbs within the proper airways resulting in successful stabilization of the airway.
At this point inspection was performed to evaluate for any bleeding or other complications and none was seen.
Due to the prolonged nature of the procedure decision was made to intubate the patient prior to transfer back to the ICU.
We then removed the rigid bronchoscope and inserted a 7.0 ETT into the airway over a flexible bronchoscope to allow for visualization of the distal tip and directed the tip of the ETT into the proximal limb of the stent (about 2.5 cm into the stent) inflated the pilot balloon and secured the ETT in place.
At this point the procedure was completed and the case was turned over to anesthesia.
Recommendations:
-          Transfer back to ICU
-          Post-procedure x-ray
-          Start 3% saline nebs 4cc 3 times daily for stent maintenance.
-          Ensure supplemental oxygen is humidified
-          Please arrange for patient to have nebulizer at home for continued hypertonic saline nebs post-discharge.
-           Extubation must be performed with flexible bronchoscope to allow visualization of the stent and using flexible forceps to apply downward pressure on the main carina while retracting the ETT to avoid dislodging of the stent.
-	If invasive ventilatory support is required after ETT removal blind intubation (direct laryngoscopy, glidescope) should be avoided as it can result in dislodgment of the tracheal stent and potential catastrophic airway obstruction.
Intubation should be performed with a 7.0 or smaller ETT with bronchoscopic insertion to visualize the distal tip of the endotracheal tube.
The endotracheal tube should be advanced approximately 3 cm into the tracheal limb of the stent and secured."""

# List of manual targets to find. 
# Format: (Label, Specific Text Segment to Match)
TARGETS = [
    # Diagnosis/Indications
    ("OBS_LESION", "lung cancer"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OBS_LESION", "Airway obstruction"), # From indications
    ("OBS_FINDING", "hemoptysis"),
    
    # Anatomy
    ("ANAT_AIRWAY", "trachea"), 
    ("ANAT_AIRWAY", "right mainstem"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("ANAT_AIRWAY", "upper trachea"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("ANAT_LUNG_LOC", "left upper"), # Context: left upper and left lower
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("ANAT_AIRWAY", "bronchus intermedius"),

    # Procedure/Method
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("PROC_ACTION", "tumor debulking"),
    ("PROC_ACTION", "burn and shave"),
    ("PROC_ACTION", "inspection"),
    ("PROC_ACTION", "Intubation"),
    ("PROC_ACTION", "Extubation"),

    # Devices
    ("DEV_STENT", "silicone Y-stent"),
    ("DEV_STENT", "silicone tracheobronchial Y- stent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid forceps"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("DEV_INSTRUMENT", "APC"),
    ("DEV_INSTRUMENT", "ETT"),

    # Measurements & Outcomes
    ("MEAS_SIZE", "10mm"),
    ("MEAS_SIZE", "5mm"),
    ("MEAS_SIZE", "80mm"),
    ("MEAS_SIZE", "30mm"),
    ("MEAS_SIZE", "13mm"),
    ("MEAS_SIZE", "7.0"), # ETT size
    ("MEAS_SIZE", "3 cm"),
    ("DEV_STENT_SIZE", "15x12x12"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "30% airway obstruction"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "near complete obstruction (95%)"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "85% opening"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "50% opening"),
    
    # Medications
    ("MEDICATION", "3% saline"),
]

# ==========================================
# SCRIPT LOGIC
# ==========================================

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

def extract_entities(text, targets):
    entities = []
    # Use a set to track used indices to avoid overlapping spans if necessary, 
    # though for this simple pass we allow all distinct matches.
    
    for label, substr in targets:
        start_search = 0
        while True:
            start = text.find(substr, start_search)
            if start == -1:
                break
            
            end = start + len(substr)
            
            # Verify alignment
            extracted = text[start:end]
            if extracted != substr:
                with open(LOG_FILE, "a") as log:
                    log.write(f"WARNING: Mismatch for {label} at {start}:{end}. Expected '{substr}', got '{extracted}'\n")
            
            entities.append({
                "label": label,
                "text": substr,
                "start": start,
                "end": end
            })
            
            # Move search forward
            start_search = end
            
    # Sort by start index
    entities.sort(key=lambda x: x["start"])
    return entities

def update_files():
    # 1. Extract Entities
    entities = extract_entities(RAW_TEXT, TARGETS)
    
    # 2. Prepare Data Objects
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    span_entries = []
    label_counts = {}
    
    for e in entities:
        span_id = f"{e['label']}_{e['start']}"
        span_entries.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": e['label'],
            "text": e['text'],
            "start": e['start'],
            "end": e['end']
        })
        label_counts[e['label']] = label_counts.get(e['label'], 0) + 1

    # 3. Write to JSONL files
    with open(NER_DATASET_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
        for span in span_entries:
            f.write(json.dumps(span) + "\n")

    # 4. Update Stats
    if STATS_FILE.exists():
        with open(STATS_FILE, "r", encoding="utf-8") as f:
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
    # Assuming one file per note for this workflow
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    for label, count in label_counts.items():
        if label in stats["label_counts"]:
            stats["label_counts"][label] += count
        else:
            stats["label_counts"][label] = count

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    update_files()