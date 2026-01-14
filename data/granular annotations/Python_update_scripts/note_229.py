import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_229"

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
# 2. Raw Text & Entity Definitions
# ==========================================
RAW_TEXT = """NOTE_ID:  note_229 SOURCE_FILE: note_229.txt PREOPERATIVE DIAGNOSIS: Malignant central airway obstruction.
POSTOPERATIVE DIAGNOSIS: Resolved airway obstruction s/p silicone Y-stent
PROCEDURE PERFORMED: Rigid bronchoscopy with tumor debulking and silicone tracheobronchial Y- stent placement 
INDICATIONS: Airway obstruction
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient’s family acknowledged and gave consent.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives the a14mm ventilating rigid bronchoscope insertion was attempted.
Due to poor mouth opening and glottic irregularities (related to previous head and neck radiation) we were unable to pass the large rigid bronchoscope through the cords and has to convert to a 12mm rigid ventilating bronchoscope which was advanced past the vocal cords into the mid trachea and connected to jet ventilator.
Unfortunately due to a combination of extremely poor dentition and poor mouth opening two teeth were lost during the intubation procedure.
Airway inspection was performed using the T190 therapeutic flexible bronchoscope. The upper trachea was normal.
The mid trachea had friable tumor mostly at the right lateral wall causing about 30% airway obstruction.
The distal trachea had extensive tumor involving both mainstem with carinal tumor infiltration as well.
The distal trachea was about 20% patient. The left mainstem was completely occluded and the right mainstem was 30% patent.
It appeared that intrinsic tumor ingrowth was the predominant issue will only mild extrinsic compression.
Tumor debulking  was performed using APC to  “burn and shave” the tumor within the trachea and proximal bilateral mainstem along with cryotherapy to remove loose debris and blood clots.
Once we were able to bypass the central tumor the left mainstem tumor only extended about 1cm pass the main carina and the distal left mainstem and left sided bronchi were normal and fully patent.
The right mainstem involvement also limited to the first cm pass the main carina.
There was non-obstructive tumor infiltration in the posterior segment of the right upper lobe but the right sided airways were otherwise uninvolved.
After measuring the airways we customized a 15x12x12 silicone Y-stent to a length of 65mm in the tracheal limb, 17.5 mm in the right mainstem limb and 40mm in the left mainstem limb.
The rigid bronchoscope was then removed as the stent was too large to insert through the rigid and using Fritag forceps along with a bougie inserted into the left limb we were able to blindly pass the stent through the vocal cords into the trachea.
The rigid bronchoscope was then re-inserted. Through the use of rigid forceps, and manipulation with the tip of the flexible bronchoscope we were eventually able to seed the stent into proper position.
Post-insertion the trachea, right mainstem and left mainstem were all at least 90% patent.
We then removed the rigid bronchoscope turned over the case to anesthesia for recovery.
Recommendations:
-          Transfer back to ICU
-          Post-procedure x-ray
-          Start 3% saline nebs 4cc 3 times daily for stent maintenance.
-          Ensure supplemental oxygen is humidified
-          Please arrange for patient to have nebulizer at home for continued hypertonic saline nebs post-discharge.
-	If invasive ventilatory support is required blind intubation (direct laryngoscopy, glidescope) should be avoided as it can result in dislodgment of the tracheal stent and potential catastrophic airway obstruction.
Intubation should be performed with a 7.0 or smaller ETT with bronchoscopic insertion to visualize the distal tip of the endotracheal tube.
The endotracheal tube should be advanced approximately 3 cm into the tracheal limb of the stent and secured."""

# Ordered list of entities to extract. 
# Format: (Label, Exact Text Fragment)
# The script will locate these sequentially to handle duplicates correctly.
ENTITIES_TO_EXTRACT = [
    ("OBS_ROSE", "Malignant"), # Diagnosis context
    ("DEV_STENT_MATERIAL", "silicone"),
    ("DEV_STENT", "Y-stent"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "tumor debulking"),
    ("DEV_STENT_MATERIAL", "silicone"),
    ("DEV_STENT", "Y- stent"), # Note space in source text
    ("OBS_LESION", "Airway obstruction"),
    ("MEAS_SIZE", "14mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "cords"),
    ("MEAS_SIZE", "12mm"),
    ("DEV_INSTRUMENT", "rigid ventilating bronchoscope"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("DEV_INSTRUMENT", "T190 therapeutic flexible bronchoscope"),
    ("ANAT_AIRWAY", "upper trachea"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("OBS_LESION", "friable tumor"),
    ("ANAT_AIRWAY", "right lateral wall"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "30% airway obstruction"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "mainstem"),
    ("ANAT_AIRWAY", "carinal"),
    ("OBS_LESION", "tumor infiltration"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "20% patient"), # Source text typo preserved
    ("ANAT_AIRWAY", "Left mainstem"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely occluded"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "30% patent"),
    ("OBS_LESION", "intrinsic tumor ingrowth"),
    ("PROC_ACTION", "Tumor debulking"),
    ("PROC_METHOD", "APC"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "mainstem"),
    ("PROC_ACTION", "cryotherapy"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("OBS_LESION", "tumor"),
    ("MEAS_SIZE", "1cm"),
    ("ANAT_AIRWAY", "main carina"),
    ("ANAT_AIRWAY", "distal left mainstem"),
    ("ANAT_AIRWAY", "left sided bronchi"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("MEAS_SIZE", "first cm"), # Approximating as size context
    ("ANAT_AIRWAY", "main carina"),
    ("OBS_LESION", "tumor infiltration"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("ANAT_AIRWAY", "right sided airways"),
    ("DEV_STENT_SIZE", "15x12x12"),
    ("DEV_STENT_MATERIAL", "silicone"),
    ("DEV_STENT", "Y-stent"),
    ("MEAS_SIZE", "65mm"),
    ("ANAT_AIRWAY", "tracheal limb"),
    ("MEAS_SIZE", "17.5 mm"),
    ("ANAT_AIRWAY", "right mainstem limb"),
    ("MEAS_SIZE", "40mm"),
    ("ANAT_AIRWAY", "left mainstem limb"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "Fritag forceps"),
    ("DEV_INSTRUMENT", "bougie"),
    ("ANAT_AIRWAY", "left limb"),
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "trachea"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "rigid forceps"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "90% patent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("MEDICATION", "3% saline nebs"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "nebulizer"),
    ("MEDICATION", "hypertonic saline nebs"),
    ("DEV_STENT", "tracheal stent"),
    ("MEAS_SIZE", "7.0"),
    ("DEV_INSTRUMENT", "ETT"),
    ("DEV_INSTRUMENT", "endotracheal tube"),
    ("DEV_INSTRUMENT", "endotracheal tube"),
    ("MEAS_SIZE", "3 cm"),
    ("ANAT_AIRWAY", "tracheal limb"),
    ("DEV_STENT", "stent")
]

# ==========================================
# 3. Processing Logic
# ==========================================

def calculate_spans(text, entity_list):
    """
    Finds entities in text sequentially to ensure correct indices 
    for duplicate words.
    """
    spans = []
    current_index = 0
    
    for label, target_text in entity_list:
        start = text.find(target_text, current_index)
        
        if start == -1:
            # Fallback: search from beginning if not found sequentially 
            # (though strictly we want sequential for this note's flow)
            start = text.find(target_text)
            if start == -1:
                print(f"WARNING: Could not find '{target_text}' in text.")
                continue
                
        end = start + len(target_text)
        
        spans.append({
            "label": label,
            "text": target_text,
            "start": start,
            "end": end
        })
        
        # Move index forward to avoid re-matching the same instance 
        # immediately if the next entity is identical
        current_index = start + 1 

    return spans

def update_file(path, data, mode='a'):
    with open(path, mode, encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def main():
    # 1. Calculate Spans
    extracted_spans = calculate_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }
    update_file(NER_DATASET_PATH, ner_record)
    
    # 3. Update notes.jsonl
    note_record = {"id": NOTE_ID, "text": RAW_TEXT}
    update_file(NOTES_PATH, note_record)
    
    # 4. Update spans.jsonl
    for span in extracted_spans:
        span_record = {
            "span_id": f"{span['label']}_{span['start']}",
            "note_id": NOTE_ID,
            "label": span["label"],
            "text": span["text"],
            "start": span["start"],
            "end": span["end"]
        }
        update_file(SPANS_PATH, span_record)
        
    # 5. Update stats.json
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
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
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    for span in extracted_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
        
    # 6. Verification & Logging
    with open(LOG_PATH, 'a', encoding='utf-8') as log_f:
        for span in extracted_spans:
            excerpt = RAW_TEXT[span["start"]:span["end"]]
            if excerpt != span["text"]:
                log_f.write(f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{span['text']}' but found '{excerpt}' at {span['start']}:{span['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Data written to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()