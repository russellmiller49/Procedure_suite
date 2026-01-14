import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_219"

# Raw text from the provided file
RAW_TEXT = """NOTE_ID:  note_219 SOURCE_FILE: note_219.txt PREOPERATIVE DIAGNOSIS:

Small Cell Lung Cancer with Central Airway Obstruction
Retained/Embedded Metallic Airway Stent
POSTOPERATIVE DIAGNOSIS:

Small Cell Lung Cancer with Central Airway Obstruction s/p Airway Stent Removal and Y-Stent Insertion
PROCEDURE PERFORMED:

INDICATIONS:
Malignant Central Airway Obstruction
Retained/Embedded Metallic Airway Stent
Informed consent was obtained from the patient after explaining the procedure's indications, details, potential risks, and alternatives in lay terms.
All questions were answered, and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedural assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed before the intervention.

Sedation: General Anesthesia

DESCRIPTION OF PROCEDURE: The procedure was carried out in the main operating room.
Following intravenous medications as per the record, a laryngeal mask airway was inserted to ensure adequate ventilation.
Topical anesthesia was applied to the upper airway, and the Boston Scientific Model B diagnostic disposable video bronchoscope was introduced through the mouth, via laryngeal mask airway, and advanced to the tracheobronchial tree.
The laryngeal mask airway was in a good position. The vocal cords appeared normal. The subglottic space was normal.
The proximal trachea was normal. The mid-trachea was free of tumor, but moderate to severe dynamic collapse was visualized (TBM).
The right mainstem was extrinsically compressed from the posterior aspect, with additional tumor studding and submucosal disease seen throughout the airway, causing approximately 70% obstruction.
A few small tumor nodules were present in the distal trachea, mostly on the posterior membrane.
The proximal left mainstem was mildly compressed externally, with submucosal tumor within the airway wall.
In the mid left mainstem, there was extensive granulation tissue causing about 75% airway obstruction just proximal to the proximal end of the known airway stent.
After gently passing the bronchoscope through the area of granulation tissue, the stent was visualized with thick purulent mucus throughout.
10cc of bicarbonate solution was instilled to thin secretions, and then the secretions were suctioned and cleared.
Significant post-obstructive pus was noted distal to the stent, primarily originating from the lower lobe bronchus, and a mini lavage was performed for culture.
After suctioning clear, tumor infiltration could be seen extending into the proximal aspect of the lower lobe and growing through the stent wall.
The left upper lobe, however, appeared free of disease.

At this point, the flexible bronchoscope and LMA were removed, and a 12mm ventilating rigid bronchoscope was subsequently inserted into the trachea and advanced into the left mainstem bronchus, then connected to the JET ventilator.
The rigid optic was removed, and the Olympus T190 Therapeutic bronchoscope was inserted through the rigid lumen and advanced to the proximal edge of the stent.
APC was used, followed by gentle shaving of coagulated tissue with the tip of the bronchoscope to remove granulation tissue.
We then utilized APC to burn the inner silicone coating from the stent and gently placed flexible forceps through the wall of the stent to peel it from the mucosa.
After this, a size 4-5-6 Merit dilatational balloon was guided similarly outside of the stent and used to further break adhesions with the underlying airway wall.
We repeated this multiple times, attempting to slowly recannulate the airway.
We then removed the flexible bronchoscope and utilized rigid forceps to grasp and remove the stent.
APC was then used to cauterize the underlying inflamed mucosa, and a 2.1 mm cryotherapy probe was used to remove debris.
Significant obstruction, both from endobronchial disease and extrinsic compression, was still present.
At this point, we focused on the right-sided airway and utilized APC with the burn and shave technique, attempting to recannulate the airway with partial success;
however, obstruction remained > 50% in the right mainstem, with tumor extending through the bronchus intermedius.
Measurements of the airway were then taken in anticipation of airway stent placement.
We customized a 14x10x10 silicone Y-stent to a length of 30mm in the tracheal limb, 35mm in the right limb, and 35mm in the left mainstem limb.
We also created a 10mm hole in the right-sided limb to allow for the right upper lobe to remain ventilated while maintaining patency of the bronchus intermedius.
The rigid bronchoscope was then advanced into the right mainstem, and the stent was deployed.
After deployment, the rigid forceps were used to manipulate the stent to adequately position the limbs within the proper airways, resulting in successful stabilization of the airway.
Persistent tumor beyond the stent remained bilaterally, with small isolates of tumor in the distal bronchus intermedius and significant residual tumor in the left lower lobe bronchus.
The rigid bronchoscope was removed, and an LMA was inserted, and the procedure was turned over to anesthesia for post-procedural care.
Recommendations:

•	Transfer to PACU
•	Obtain post-procedure chest x-ray.
•	Patient to be admitted to inpatient service for expedited radiation oncology consultation, given residual disease.
•	Patient will need TID hypertonic nebulization (4cc 3% saline) to avoid mucus impaction and obstruction of stent.
•	Management of stent-related complications was discussed with the in-patient team, and a notice for airway management precautions was placed above the patient's bed.
•	Plan to schedule the procedure in approximately 2 weeks (after the effects of radiation should be seen)."""

# Entities to be extracted (Sequential list to handle duplicates correctly)
# Format: (Text, Label)
ENTITIES_TO_EXTRACT = [
    ("Small Cell Lung Cancer", "OBS_LESION"),
    ("Central Airway Obstruction", "OBS_LESION"),
    ("Retained/Embedded", "OBS_FINDING"),
    ("Metallic", "DEV_STENT_MATERIAL"),
    ("Airway Stent", "DEV_STENT"),
    ("Small Cell Lung Cancer", "OBS_LESION"),
    ("Central Airway Obstruction", "OBS_LESION"),
    ("Airway Stent", "DEV_STENT"),
    ("Removal", "PROC_ACTION"),
    ("Y-Stent", "DEV_STENT"),
    ("Insertion", "PROC_ACTION"),
    ("Malignant", "OBS_LESION"),
    ("Central Airway Obstruction", "OBS_LESION"),
    ("Retained/Embedded", "OBS_FINDING"),
    ("Metallic", "DEV_STENT_MATERIAL"),
    ("Airway Stent", "DEV_STENT"),
    ("General Anesthesia", "PROC_METHOD"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("Boston Scientific Model B diagnostic disposable video bronchoscope", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("proximal trachea", "ANAT_AIRWAY"),
    ("mid-trachea", "ANAT_AIRWAY"),
    ("tumor", "OBS_LESION"),
    ("dynamic collapse", "OBS_FINDING"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("extrinsically compressed", "OBS_FINDING"),
    ("tumor studding", "OBS_LESION"),
    ("submucosal disease", "OBS_LESION"),
    ("70% obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("tumor nodules", "OBS_LESION"),
    ("distal trachea", "ANAT_AIRWAY"),
    ("proximal left mainstem", "ANAT_AIRWAY"),
    ("submucosal tumor", "OBS_LESION"),
    ("mid left mainstem", "ANAT_AIRWAY"),
    ("granulation tissue", "OBS_LESION"),
    ("75% airway obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("stent", "DEV_STENT"),
    ("thick purulent mucus", "OBS_FINDING"),
    ("10cc", "MEAS_VOL"),
    ("suctioned", "PROC_ACTION"),
    ("pus", "OBS_FINDING"),
    ("lower lobe bronchus", "ANAT_AIRWAY"),
    ("lavage", "PROC_ACTION"),
    ("suctioning", "PROC_ACTION"),
    ("tumor infiltration", "OBS_LESION"),
    ("stent", "DEV_STENT"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("removed", "PROC_ACTION"),
    ("12mm", "MEAS_SIZE"),
    ("ventilating rigid bronchoscope", "DEV_INSTRUMENT"),
    ("inserted", "PROC_ACTION"),
    ("trachea", "ANAT_AIRWAY"),
    ("left mainstem bronchus", "ANAT_AIRWAY"),
    ("JET ventilator", "DEV_INSTRUMENT"),
    ("Olympus T190 Therapeutic bronchoscope", "DEV_INSTRUMENT"),
    ("APC", "PROC_METHOD"),
    ("shaving", "PROC_ACTION"),
    ("coagulated tissue", "OBS_LESION"),
    ("granulation tissue", "OBS_LESION"),
    ("APC", "PROC_METHOD"),
    ("silicone", "DEV_STENT_MATERIAL"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("size 4-5-6", "MEAS_SIZE"),
    ("Merit dilatational balloon", "DEV_INSTRUMENT"),
    ("recannulate", "PROC_ACTION"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid forceps", "DEV_INSTRUMENT"),
    ("remove", "PROC_ACTION"),
    ("stent", "DEV_STENT"),
    ("APC", "PROC_METHOD"),
    ("cauterize", "PROC_ACTION"),
    ("inflamed mucosa", "OBS_FINDING"),
    ("2.1 mm", "MEAS_SIZE"),
    ("cryotherapy probe", "DEV_INSTRUMENT"),
    ("Significant obstruction", "OBS_LESION"),
    ("endobronchial disease", "OBS_LESION"),
    ("extrinsic compression", "OBS_LESION"),
    ("right-sided airway", "ANAT_AIRWAY"),
    ("APC", "PROC_METHOD"),
    ("recannulate", "PROC_ACTION"),
    ("obstruction remained > 50%", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("tumor", "OBS_LESION"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("Measurements", "PROC_ACTION"),
    ("14x10x10", "DEV_STENT_SIZE"),
    ("silicone", "DEV_STENT_MATERIAL"),
    ("Y-stent", "DEV_STENT"),
    ("30mm", "MEAS_SIZE"),
    ("35mm", "MEAS_SIZE"),
    ("35mm", "MEAS_SIZE"),
    ("left mainstem", "ANAT_AIRWAY"),
    ("10mm", "MEAS_SIZE"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("deployed", "PROC_ACTION"),
    ("rigid forceps", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("tumor", "OBS_LESION"),
    ("stent", "DEV_STENT"),
    ("tumor", "OBS_LESION"),
    ("distal bronchus intermedius", "ANAT_AIRWAY"),
    ("tumor", "OBS_LESION"),
    ("left lower lobe bronchus", "ANAT_AIRWAY"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("4cc", "MEAS_VOL"),
    ("saline", "MEDICATION"),
    ("stent", "DEV_STENT")
]

# ==========================================
# SCRIPT LOGIC
# ==========================================

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

def update_pipeline():
    # 1. Calculate Indices
    extracted_entities = []
    current_search_index = 0
    
    for text_span, label in ENTITIES_TO_EXTRACT:
        # Find the next occurrence of the text starting from current_search_index
        start_idx = RAW_TEXT.find(text_span, current_search_index)
        
        if start_idx == -1:
            print(f"WARNING: Could not find span '{text_span}' after index {current_search_index}")
            continue
            
        end_idx = start_idx + len(text_span)
        
        extracted_entities.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text_span,
            "start": start_idx,
            "end": end_idx
        })
        
        # Move search cursor forward to avoid finding the same instance
        current_search_index = start_idx + 1

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_entities
    }
    
    with open(NER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
        for entity in extracted_entities:
            f.write(json.dumps(entity) + "\n")

    # 5. Update stats.json
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
            
        stats["total_files"] += 1
        stats["total_notes"] += 1
        stats["total_spans_raw"] += len(extracted_entities)
        stats["total_spans_valid"] += len(extracted_entities)
        
        for entity in extracted_entities:
            lbl = entity["label"]
            if lbl in stats["label_counts"]:
                stats["label_counts"][lbl] += 1
            else:
                stats["label_counts"][lbl] = 1
                
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
            
    except Exception as e:
        print(f"Error updating stats.json: {e}")

    # 6. Validate
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        for entity in extracted_entities:
            extracted_text = RAW_TEXT[entity["start"]:entity["end"]]
            if extracted_text != entity["text"]:
                log_msg = f"{datetime.now().isoformat()} - MISMATCH: {entity['span_id']} expected '{entity['text']}' but found '{extracted_text}'\n"
                log.write(log_msg)
                print(log_msg.strip())

    print(f"Successfully processed {NOTE_ID} with {len(extracted_entities)} entities.")

if __name__ == "__main__":
    update_pipeline()