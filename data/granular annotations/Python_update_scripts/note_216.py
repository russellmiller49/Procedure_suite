import json
import os
import datetime
from pathlib import Path

# ----------------------------------------------------------------------------------
# 1. CONFIGURATION & PATH SETUP
# ----------------------------------------------------------------------------------
NOTE_ID = "note_216"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------------
# 2. RAW TEXT CONTENT
# ----------------------------------------------------------------------------------
# Exact text content from note_216.txt (stripped of source tags for NLP training)
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Mediastinal adenopathy with extrinsic tracheal compression
POSTOPERATIVE DIAGNOSIS: Mediastinal adenopathy with extrinsic tracheal compression s/p airway stent placement
PROCEDURE PERFORMED: Rigid bronchoscopy, Silicone Y-stent placement
INDICATIONS: Severe extrinsic tracheal compression
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a laryngeal mask airway was inserted and thewe assured the patient could be adequately ventilation.
Topical anesthesia was then applied to the upper airway and the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
Approximately 3 cm below the vocal cords there was significant extrinsic compression predominantly in the lateral aspects of the airway causing about 8% obstruction of the trachea.
The obstruction continued for approximately 6cm before opening to normal caliber 4cm above the main carinal. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. Measurements of the airway were then taken in anticipation of airway stent placement.
At this point the flexible bronchoscope and LMA were removed and a 14mm ventilating rigid bronchoscope was subsequently inserted into the upper trachea and advanced past the tracheal extrinsic compression and connected to the Jet ventilator while in the distal trachea.
The T190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and into the airways.
We the customized a 15x13x13 silicone Y-stent to a length of 103mm in the tracheal limb, 13mm in the right mainstem limb and 20mm in the left mainstem limb.
The rigid bronchoscope was then advanced into the left mainstem and the stent was deployed.
After deployment, the rigid forceps were used to manipulate the stent to adequately position the limbs within the proper airways resulting in successful stabilization of the airway.
The rigid bronchoscope was removed and an LMA was inserted.
The flexible bronchoscope was then inserted through the LMA for re-inspection.
The Stent was well seated with the proximal limb approximately 3 cm distal to the vocal cords.
The mid-stent was compressed approximately 20% by the extrinsic force of the mediastinal mass.
The distal trachea, left mainstem and right mainstem were widely patent. The bronchoscope was subsequently removed and the procedure completed.
Recommendations:
- Transfer PACU
- Obtain post procedure CXR
- Will arrange for patient to have nebulizer at home for TID hypertonic nebulization (4cc 3% saline) to avoid mucous impaction and obstruction of stent.
- If invasive ventilatory support is required blind intubation (direct laryngoscopy, glidescope) should be avoided as it can result in dislodgment of the tracheal stent and potential catastrophic airway obstruction.
Intubation should be performed with a 6.5 or smaller ETT with bronchoscopic insertion to visualize the distal tip of the endotracheal tube.
The endotracheal tube should be advanced approximately 3 cm into the tracheal limb of the stent and secured.
- Extubation must be performed with flexible bronchoscope to allow visualization of the stent and using flexible forceps to apply downward pressure on the main carina while retracting the ETT to avoid dislodging of the stent."""

# ----------------------------------------------------------------------------------
# 3. ENTITY EXTRACTION
# ----------------------------------------------------------------------------------
# List of (Label, Exact Phrase) to map.
# Order matters: Longer/Specific matches generally first to ensure they are captured distinctively.
TARGET_ENTITIES = [
    ("OBS_LESION", "Mediastinal adenopathy"),
    ("OBS_FINDING", "Severe extrinsic tracheal compression"),
    ("OBS_FINDING", "extrinsic tracheal compression"),
    ("CTX_HISTORICAL", "s/p"),
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("DEV_STENT_MATERIAL", "Silicone"),
    ("DEV_STENT", "Y-stent"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("MEAS_SIZE", "3 cm"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "8% obstruction"),
    ("ANAT_AIRWAY", "trachea"),
    ("MEAS_SIZE", "6cm"),
    ("MEAS_SIZE", "4cm"),
    ("ANAT_AIRWAY", "main carinal"),
    ("ANAT_AIRWAY", "carina"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("MEAS_SIZE", "14mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("ANAT_AIRWAY", "upper trachea"),
    ("DEV_INSTRUMENT", "Jet ventilator"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("DEV_INSTRUMENT", "T190 Olympus flexible bronchoscope"),
    ("DEV_STENT_SIZE", "15x13x13"),
    ("DEV_STENT_MATERIAL", "silicone"),
    ("MEAS_SIZE", "103mm"),
    ("MEAS_SIZE", "13mm"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("MEAS_SIZE", "20mm"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "Stent"),
    ("DEV_INSTRUMENT", "rigid forceps"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "widely patent"),
    ("MEDICATION", "3% saline"),
    ("DEV_INSTRUMENT", "endotracheal tube"),
    ("DEV_INSTRUMENT", "ETT"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("OBS_FINDING", "extrinsic compression"),
]

def extract_entities(text, targets):
    """
    Finds all occurrences of target phrases in text.
    Returns a list of dicts: {"label": label, "start": start, "end": end, "text": span_text}
    """
    found_entities = []
    
    # We use a set to track (start, end) to prevent identical duplicates 
    # if a phrase is in the list twice, but allow overlaps for different labels if needed.
    seen_spans = set()

    for label, substring in targets:
        start_search = 0
        while True:
            start = text.find(substring, start_search)
            if start == -1:
                break
            
            end = start + len(substring)
            span_id = f"{start}_{end}_{label}"
            
            if span_id not in seen_spans:
                found_entities.append({
                    "label": label,
                    "text": substring,
                    "start": start,
                    "end": end
                })
                seen_spans.add(span_id)
            
            start_search = start + 1
            
    # Sort by start offset
    found_entities.sort(key=lambda x: x["start"])
    return found_entities

entities_list = extract_entities(RAW_TEXT, TARGET_ENTITIES)

# ----------------------------------------------------------------------------------
# 4. FILE UPDATES
# ----------------------------------------------------------------------------------

def append_jsonl(path, data):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

# A. ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {"start": e["start"], "end": e["end"], "label": e["label"]}
        for e in entities_list
    ]
}
append_jsonl(OUTPUT_DIR / "ner_dataset_all.jsonl", ner_entry)

# B. notes.jsonl
note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
append_jsonl(OUTPUT_DIR / "notes.jsonl", note_entry)

# C. spans.jsonl
spans_path = OUTPUT_DIR / "spans.jsonl"
for e in entities_list:
    span_id = f"{e['label']}_{e['start']}"
    span_entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": e["label"],
        "text": e["text"],
        "start": e["start"],
        "end": e["end"]
    }
    append_jsonl(spans_path, span_entry)

# D. stats.json
stats_path = OUTPUT_DIR / "stats.json"
if stats_path.exists():
    with open(stats_path, "r", encoding="utf-8") as f:
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
stats["total_files"] += 1 # Assuming 1 note per file for this pipeline
stats["total_spans_raw"] += len(entities_list)
stats["total_spans_valid"] += len(entities_list)

for e in entities_list:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ----------------------------------------------------------------------------------
# 5. VALIDATION & LOGGING
# ----------------------------------------------------------------------------------
log_path = OUTPUT_DIR / "alignment_warnings.log"
with open(log_path, "a", encoding="utf-8") as f:
    for e in entities_list:
        extracted = RAW_TEXT[e["start"]:e["end"]]
        if extracted != e["text"]:
            log_msg = f"MISMATCH {NOTE_ID}: Exp '{e['text']}' Got '{extracted}' at {e['start']}:{e['end']}\n"
            f.write(log_msg)
            print(log_msg)

print(f"Successfully processed {NOTE_ID}. Files updated in {OUTPUT_DIR}")