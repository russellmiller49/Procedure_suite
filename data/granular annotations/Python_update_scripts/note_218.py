import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_218"
RAW_TEXT = """PREOPERATIVE DIAGNOSIS:
1. Small Cell Lung Cancer 

POSTOPERATIVE DIAGNOSIS:
1. Small Cell Lung Cancer 
INDICATIONS:
1. Stent eval and removal 

PROCEDURE PERFORMED:
Flexible and rigid bronchoscopy with therapeutic aspiration and Tracheal stent removal.
CPT CODES:
CPT 31635: Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with removal of foreign body
CPT 31641: Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with destruction of tumor or relief of stenosis by any method other than excision (e.g., laser therapy, cryotherapy)
CPT 31645: Bronchoscopy with therapeutic aspiration
Sedation: General Anesthesia

Informed consent was obtained from the patient after explaining the procedure's indications, details, potential risks, and alternatives in lay terms.
All questions were answered, and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedural assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed before the intervention.
 

DESCRIPTION OF PROCEDURE: The procedure was carried out in the main operating room.
Following intravenous medications as per the record, a laryngeal mask airway was inserted to ensure adequate ventilation.
Topical anesthesia was applied to the upper airway, and the T190 therapeutic video bronchoscope was introduced through the mouth, via laryngeal mask airway, and advanced to the tracheobronchial tree.
The laryngeal mask airway was in a good position. The vocal cords appeared normal. The subglottic space was normal.
The proximal trachea was normal. The previously placed Y-stent was in appropriate position with thick mucus coating the inner aspect of the stent.
The tracheal limb was about 40% obstructed with mucous, the right sided limb was about 60% obstructed and the left sided limb was completely obstructed.
The flexible bronchoscope with suction was used to re-canulate the stent and saline instillation was used to thin the adherent mucous to allow for further removal via suction.
The flexible bronchoscope and LMA were then removed, and a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the mid trachea.
rigid non-optical forceps were inserted through the rigid scope along with the rigid optic.
The forceps were used to grasp the proximal limb of the tracheal stent and were rotated repeatedly while withdrawing the stent into the rigid bronchoscope.
The stent was subsequently removed en-bloc with the rigid bronchoscope without difficulty.
Once his stent was removed a laryngeal mask airway was inserted and the flexible bronchoscope was then inserted through the LMA for re-inspection.
Post stent removal the airways were widely patent. White plaques were seen in the posterior aspect of the right mainstem and left mainstem consistent with post-treatment effects from tumor.
At the location of distal edge of the removed stent granulation tissue was seem both in the BI and the left mainstem.
Cryotherapy was performed with three 30 second freeze thaw cycles in the areas of granulation.
After this further suction was performed of residual mucous from the more distal airways.
Once we were confident that the airways were patent and there was no active bleeding the flexible bronchoscope was removed, and the patient turned over to anesthesia who extubated the patient in the OR.
Complications: None 
Recommendations:
- Transfer to PACU
- Obtain post procedure CXR
- Discharge to home once criteria met."""

# Entities defined in sequential order of appearance to ensure accurate index calculation
# Tuple Format: (Label, Text_Snippet)
ENTITIES_TO_EXTRACT = [
    ("PROC_ACTION", "removal"), # In Indications
    ("PROC_METHOD", "Flexible and rigid bronchoscopy"),
    ("PROC_ACTION", "therapeutic aspiration"),
    ("DEV_STENT", "Tracheal stent"),
    ("PROC_ACTION", "removal"), # In Procedure Performed
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("DEV_INSTRUMENT", "T190 therapeutic video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "proximal trachea"),
    ("DEV_STENT", "Y-stent"),
    ("OBS_FINDING", "mucus"),
    ("DEV_STENT", "stent"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "40% obstructed"),
    ("OBS_FINDING", "mucous"),
    ("LATERALITY", "right"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "60% obstructed"),
    ("LATERALITY", "left"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely obstructed"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("PROC_ACTION", "suction"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "mucous"),
    ("PROC_ACTION", "suction"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("DEV_INSTRUMENT", "rigid non-optical forceps"),
    ("DEV_INSTRUMENT", "rigid scope"),
    ("DEV_INSTRUMENT", "rigid optic"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_STENT", "tracheal stent"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("DEV_STENT", "stent"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "widely patent"),
    ("OBS_FINDING", "White plaques"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("OBS_LESION", "tumor"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "granulation tissue"),
    ("ANAT_AIRWAY", "BI"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("PROC_METHOD", "Cryotherapy"),
    ("MEAS_TIME", "30 second"),
    ("OBS_FINDING", "granulation"),
    ("PROC_ACTION", "suction"),
    ("OBS_FINDING", "mucous"),
    ("ANAT_AIRWAY", "distal airways"),
    ("OUTCOME_COMPLICATION", "no active bleeding"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("OUTCOME_COMPLICATION", "None")
]

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
# PROCESSING LOGIC
# ==========================================

def calculate_spans(text, entities_list):
    """
    Calculates start/end indices for sequential entities.
    """
    spans = []
    current_index = 0
    
    for label, substr in entities_list:
        start = text.find(substr, current_index)
        if start == -1:
            # Fallback: restart search from 0 if out of order (though list should be sequential)
            start = text.find(substr)
            
        if start != -1:
            end = start + len(substr)
            spans.append({
                "label": label,
                "text": substr,
                "start": start,
                "end": end
            })
            current_index = start + 1 # Advance index to avoid finding same substring repeatedly
        else:
            print(f"WARNING: Could not find '{substr}' in text.")
            
    return spans

def update_files():
    # 1. Calculate Spans
    extracted_spans = calculate_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_spans
    }
    
    with open(NER_DATASET_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
        for span in extracted_spans:
            span_entry = {
                "span_id": f"{span['label']}_{span['start']}",
                "note_id": NOTE_ID,
                "label": span['label'],
                "text": span['text'],
                "start": span['start'],
                "end": span['end']
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    for span in extracted_spans:
        lbl = span['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log Alignment
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        for span in extracted_spans:
            sliced_text = RAW_TEXT[span['start']:span['end']]
            if sliced_text != span['text']:
                log_msg = f"MISMATCH: {NOTE_ID} | Label: {span['label']} | Expected: '{span['text']}' | Found: '{sliced_text}'\n"
                log.write(log_msg)

    print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")

if __name__ == "__main__":
    update_files()