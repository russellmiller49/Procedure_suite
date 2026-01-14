from pathlib import Path
import json
import os
import datetime

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
NOTE_ID = "note_244"
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# RAW TEXT INPUT
# -------------------------------------------------------------------------
RAW_TEXT = """NOTE_ID:  note_244 SOURCE_FILE: note_244.txt PREOPERATIVE DIAGNOSIS: Endotracheal tumor 
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

# -------------------------------------------------------------------------
# ENTITY EXTRACTION LOGIC
# -------------------------------------------------------------------------
# Defined entities in order of appearance to ensure correct sequential indexing
entities_to_extract = [
    ("ANAT_AIRWAY", "Endotracheal"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "Endotracheal"),
    ("OBS_LESION", "tumor"),
    ("CTX_HISTORICAL", "s/p"),
    ("PROC_ACTION", "debulking"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("ANAT_AIRWAY", "endoluminal"),
    ("OBS_LESION", "tumor"),
    ("PROC_ACTION", "ablation"),
    ("ANAT_AIRWAY", "Tracheal"),
    ("OBS_FINDING", "Obstruction"),
    ("MEDICATION", "General Anesthesia"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("ANAT_AIRWAY", "pharynx"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("MEAS_SIZE", "2.5 cm"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("MEAS_COUNT", "3"),
    ("OBS_LESION", "polypoid lesions"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "blocking about 90% of the airway"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "50% obstruction"),
    ("OBS_LESION", "polypoid"),
    ("MEAS_COUNT", "> 50"),
    ("OBS_LESION", "lesions"),
    ("ANAT_AIRWAY", "Anterior trachea"),
    ("ANAT_AIRWAY", "posterior trachea"),
    ("ANAT_AIRWAY", "lateral trachea"),
    ("MEAS_SIZE", "1cm"),
    ("ANAT_AIRWAY", "main carina"),
    ("LATERALITY", "right sided"),
    ("LATERALITY", "left sided"),
    ("ANAT_AIRWAY", "airways"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OBS_FINDING", "extrinsic obstruction"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("MEAS_SIZE", "10mm"),
    ("DEV_INSTRUMENT", "non-ventilating rigid tracheoscope"),
    ("ANAT_AIRWAY", "proximal trachea"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "T190 Olympus flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "electrocautery snare"),
    ("PROC_ACTION", "transect"),
    ("OBS_LESION", "large polypoid lesions"),
    ("MEAS_COUNT", "3"),
    ("OBS_LESION", "lesions"),
    ("OBS_LESION", "lesions"),
    ("PROC_ACTION", "removed"),
    ("OBS_LESION", "lesions"),
    ("PROC_ACTION", "removed"),
    ("MEAS_COUNT", "10"),
    ("OBS_LESION", "lesions"),
    ("ANAT_AIRWAY", "airway"),
    ("DEV_INSTRUMENT", "snare"),
    ("PROC_ACTION", "removed"),
    ("PROC_METHOD", "APC"),
    ("PROC_ACTION", "paint and shave"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "posterior and lateral trachea walls"),
    ("ANAT_AIRWAY", "trachea"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "90% open"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("PROC_ACTION", "removed"),
    ("OUTCOME_COMPLICATION", "No complications"),
    ("DEV_STENT", "airway stent"),
    ("OBS_LESION", "lesions"),
    ("CTX_TIME", "< 3 months"),
    ("PROC_ACTION", "bronchoscopic debulking"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("MEDICATION", "chemotherapy"),
    ("OBS_LESION", "lesions"),
    ("PROC_ACTION", "debulk"),
    ("DEV_STENT", "covered tracheal stent"),
    ("PROC_METHOD", "PDT"),
    ("PROC_METHOD", "brachytherapy")
]

# Calculate spans
valid_spans = []
cursor = 0
warnings = []

for label, substring in entities_to_extract:
    start_idx = RAW_TEXT.find(substring, cursor)
    if start_idx == -1:
        warnings.append(f"WARNING: Could not find '{substring}' after index {cursor}")
        continue
    
    end_idx = start_idx + len(substring)
    
    # Validation
    matched_text = RAW_TEXT[start_idx:end_idx]
    if matched_text != substring:
        warnings.append(f"MISMATCH: Target '{substring}' != Found '{matched_text}'")
    
    valid_spans.append({
        "label": label,
        "start": start_idx,
        "end": end_idx,
        "text": matched_text
    })
    
    # Update cursor to avoid re-finding the same instance for sequential items
    cursor = start_idx + 1

# -------------------------------------------------------------------------
# UPDATE FUNCTIONS
# -------------------------------------------------------------------------

def update_ner_dataset_all():
    target_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in valid_spans]
    }
    with open(target_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes():
    target_file = OUTPUT_DIR / "notes.jsonl"
    entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(target_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans():
    target_file = OUTPUT_DIR / "spans.jsonl"
    with open(target_file, "a", encoding="utf-8") as f:
        for span in valid_spans:
            span_id = f"{span['label']}_{span['start']}"
            entry = {
                "span_id": span_id,
                "note_id": NOTE_ID,
                "label": span["label"],
                "text": span["text"],
                "start": span["start"],
                "end": span["end"]
            }
            f.write(json.dumps(entry) + "\n")

def update_stats():
    target_file = OUTPUT_DIR / "stats.json"
    
    # Load existing or create new
    if target_file.exists():
        with open(target_file, "r", encoding="utf-8") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
    else:
        stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

    # Update counts
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file for this script
    stats["total_spans_raw"] += len(valid_spans)
    stats["total_spans_valid"] += len(valid_spans)
    
    for span in valid_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def log_warnings():
    if warnings:
        target_file = OUTPUT_DIR / "alignment_warnings.log"
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(f"--- {datetime.datetime.now()} | {NOTE_ID} ---\n")
            for w in warnings:
                f.write(w + "\n")

# -------------------------------------------------------------------------
# EXECUTION
# -------------------------------------------------------------------------
if __name__ == "__main__":
    update_ner_dataset_all()
    update_notes()
    update_spans()
    update_stats()
    log_warnings()
    print(f"Successfully processed {NOTE_ID}. Data saved to {OUTPUT_DIR}")