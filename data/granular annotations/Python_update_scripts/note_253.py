import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_253"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Definitions
# ==========================================
RAW_TEXT = """Preoperative Diagnosis:
•	Lung mass with complete left upper lobe and partial left lower lobe obstruction.
Postoperative Diagnosis:
•	Persistent tumor obstruction of the left mainstem, left upper, and left lower lobes.
Procedure Performed: 
•	Rigid bronchoscopy with tumor debulking
Indications: 
•	Airway obstruction and need for tissue biopsy
Consent: 
•	Obtained from the patient and their family after a detailed explanation of the procedure, potential risks, and alternatives.
Sedation: 
•	General Anesthesia

Description of Procedure:
The procedure was performed in the main operatingroom.
Following anesthetic induction, a 12 mm ventilating rigid bronchoscope was inserted into the airway and advanced to the distal trachea, where it was attached to the jet ventilator.
A flexible bronchoscope was then introduced through the rigid bronchoscope.
Upon initial inspection, the trachea and right lung appeared normal, without evidence of endobronchial disease.
The mid-left mainstem showed mucosal changes consistent with submucosal tumor involvement and lymphatic obstruction but was patent.
At the LC2 carina, there was extensive tumor infiltration causing 100% obstruction of the left upper lobe and 95% obstruction of the left lower lobe.
Purulent secretions were observed, and bronchial lavage with specimen collection for culture was performed.
Forceps biopsy was carried out on the visible endobronchial tumor, and samples were placed in formalin.
The tumor was friable and bled upon contact. APC was used to revascularize the tumor, and a combination of flexible and rigid forceps, as well as cryotherapy, was employed for debulking.
Additional biopsy samples were also collected and preserved in formalin.
During the procedure, a Fogarty balloon was passed into the lower lobe, inflated, and retracted in an attempt to open the airway.
Copious purulent secretions were observed and suctioned following the maneuver.
Despite this, due to the extent of the disease, adequate recanalization of the airway could not be achieved.
The patient experienced two episodes of significant hypoxia, with saturations dropping into the 50s.
This required clot extraction, repositioning, and direct oxygen insufflation via the flexible bronchoscope. Saturations later stabilized to >90%.
Attempts to recanalize the airways were unsuccessful due to extensive disease. APC was again used for hemostasis.
No further debulking was considered warranted at this time.
Once we were satisfied that there was no active bleeding the rigid bronchoscope was removed and the patient was turned over to anesthesia for continued care.
Complications:
•	None
Estimated Blood Loss: 
•	100cc
Recommendations:
•	Admit to ICU for overnight observation with a bronchial blocker available in case of massive hemoptysis.
•	Obtain a chest X-ray (CXR).
•	Await biopsy results.
•	Initiate palliative chemotherapy and radiation therapy (XRT) based on biopsy findings, as required."""

# Ordered list of entities to extract: (Label, substring)
# Order matters for duplicate strings to be found correctly.
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Lung mass"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_LESION", "tumor"),                  # Persistent tumor
    ("OBS_FINDING", "obstruction"),           # obstruction of the left mainstem...
    ("ANAT_AIRWAY", "left mainstem"),
    ("ANAT_LUNG_LOC", "left upper"),
    ("ANAT_LUNG_LOC", "left lower lobes"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "tumor debulking"),
    ("OBS_FINDING", "Airway obstruction"),
    ("PROC_ACTION", "tissue biopsy"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_LUNG_LOC", "right lung"),
    ("ANAT_AIRWAY", "mid-left mainstem"),
    ("OBS_LESION", "submucosal tumor"),
    ("OBS_FINDING", "lymphatic obstruction"),
    ("ANAT_AIRWAY", "LC2 carina"),
    ("OBS_LESION", "extensive tumor infiltration"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "100% obstruction"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "95% obstruction"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_FINDING", "Purulent secretions"),
    ("PROC_ACTION", "bronchial lavage"),
    ("PROC_ACTION", "Forceps biopsy"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OBS_LESION", "tumor"),                  # The tumor was friable
    ("PROC_ACTION", "APC"),
    ("OBS_LESION", "tumor"),                  # revascularize the tumor
    ("DEV_INSTRUMENT", "flexible and rigid forceps"),
    ("PROC_ACTION", "cryotherapy"),
    ("PROC_ACTION", "debulking"),
    ("DEV_INSTRUMENT", "Fogarty balloon"),
    ("ANAT_LUNG_LOC", "lower lobe"),
    ("OBS_FINDING", "Copious purulent secretions"),
    ("OBS_FINDING", "hypoxia"),
    ("PROC_ACTION", "clot extraction"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("OUTCOME_SYMPTOMS", "Saturations later stabilized to >90%"),
    ("PROC_ACTION", "APC"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("MEAS_VOL", "100cc"),
    ("DEV_INSTRUMENT", "bronchial blocker"),
    ("PROC_METHOD", "chest X-ray"),
    ("PROC_METHOD", "CXR")
]

# ==========================================
# 3. Execution & Processing
# ==========================================

def main():
    # --- A. Calculate Offsets ---
    valid_entities = []
    cursor = 0
    
    for label, substr in ENTITIES_TO_EXTRACT:
        start_idx = RAW_TEXT.find(substr, cursor)
        if start_idx == -1:
            print(f"CRITICAL ERROR: Could not find '{substr}' after index {cursor}")
            continue
            
        end_idx = start_idx + len(substr)
        
        valid_entities.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": substr,
            "start": start_idx,
            "end": end_idx
        })
        
        # Advance cursor to avoid re-finding the same instance
        cursor = start_idx + 1

    # --- B. Update ner_dataset_all.jsonl ---
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {"label": e["label"], "start": e["start"], "end": e["end"]}
            for e in valid_entities
        ]
    }
    
    with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # --- C. Update notes.jsonl ---
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # --- D. Update spans.jsonl ---
    with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
        for entity in valid_entities:
            f.write(json.dumps(entity) + "\n")

    # --- E. Update stats.json ---
    stats_path = OUTPUT_DIR / "stats.json"
    
    # Initialize defaults if file missing
    if not stats_path.exists():
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    else:
        with open(stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)

    # Update counts
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note = 1 file in this workflow
    stats["total_spans_raw"] += len(valid_entities)
    stats["total_spans_valid"] += len(valid_entities)
    
    for e in valid_entities:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    # --- F. Validation & Logging ---
    with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as log:
        for entity in valid_entities:
            sliced_text = RAW_TEXT[entity["start"]:entity["end"]]
            if sliced_text != entity["text"]:
                log.write(f"{datetime.datetime.now()} | MISMATCH | {NOTE_ID} | {entity['label']} | Expected: '{entity['text']}' | Found: '{sliced_text}'\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(valid_entities)} entities.")

if __name__ == "__main__":
    main()