import json
import os
import datetime
from pathlib import Path

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
NOTE_ID = "note_196"

# Raw text extracted from note_196.txt, cleaned of source tags
RAW_TEXT = """Indications: Hodgkin’s Lymphoma with possible recurrence
Medications: General Anesthesia,
Procedure: EBUS guided bronchoscopy 
CPT Codes: 31653 bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed with endobronchial ultrasound (EBUS) guided transtracheal and/or transbronchial sampling 3 or more structures.
Procedural Details: 
The patient provided informed consent for the procedure after receiving an explanation in lay terms about the indications, details of the procedure, potential risks, and alternatives.
All questions were addressed, and informed consent was documented in accordance with institutional protocol.
A history and physical examination were conducted, and the findings were updated in the pre-procedure assessment record.
Laboratory studies and radiographs were reviewed. A time-out was performed before the intervention.
The patient received intravenous medications, as documented in the record, and topical anesthesia was applied to the upper airway and tracheobronchial tree.
The Q190 video bronchoscope was introduced through the mouth via a laryngeal mask airway and advanced into the tracheobronchial tree.
The laryngeal mask airway was properly positioned. The vocal cords appeared normal, and the subglottic space was unremarkable.
The trachea had a normal caliber, and the carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
The bronchial mucosa and anatomy were normal, with no endobronchial lesions or secretions observed.
The Q190 video bronchoscope was removed, and the UC180F convex probe endobronchial ultrasound (EBUS) bronchoscope was introduced through the mouth via the laryngeal mask airway and advanced into the tracheobronchial tree.
A directed EBUS examination was performed to evaluate the abnormal lymph node that had been previously identified and biopsied as follows
1.	After identification of the 11Rs lymph node transbronchial needle aspiration (TBNA) was performed using the 19-gauge and 21 gauge Olympus ViziShot 2 EBUS-TBNA needles .
A total of eight biopsies were performed. Rapid on-site evaluation (ROSE) yielded lymphocytes.
2.	After identification of the station 7 lymph node transbronchial needle aspiration (TBNA) was performed using the 19-gauge and 21 gauge Olympus ViziShot 2 EBUS-TBNA needles .
A total of eight biopsies were performed. Rapid on-site evaluation (ROSE) yielded lymphocytes.
3.	After identification of the station 4R lymph node transbronchial needle aspiration (TBNA) was performed using the 19-gauge Olympus ViziShot 2 EBUS-TBNA needle and ROSE yielded scant tissue from a single pass, and it was decided to return our focus to a more abnormal appearing node given known Hodgkin’s and higher yield with larger tissue samples.
4.	We then returned to the station 7 lymph node and created a tract with the 19-gauge Olympus ViziShot 2 EBUS-TBNA needle using the sheath to dilate the tract, the spybite mini-forceps were inserted through the tract and into the lymph node under EBUS guidance and tissue biopsies were obtained.
A total of four tissue samples were obtained.  
Following the completion of EBUS bronchoscopy, the Q190 video bronchoscope was re-inserted.
After suctioning blood and secretions, no evidence of active bleeding was observed. The bronchoscope was subsequently removed.
All TBNA samples were sent for routine cytology and mini-forceps sample were sent for histology.
Complications: No immediate complications
Estimated Blood Loss: 10 cc

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided needle and forceps biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# Ordered list of entities to extract. 
# The script will match these sequentially to handle duplicates correctly.
ENTITIES_TO_EXTRACT = [
    {"label": "MEDICATION", "text": "General Anesthesia"},
    {"label": "PROC_METHOD", "text": "EBUS"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"}, # In CPT code section
    {"label": "PROC_METHOD", "text": "endobronchial ultrasound"},
    {"label": "PROC_METHOD", "text": "EBUS"},
    {"label": "MEDICATION", "text": "topical anesthesia"},
    {"label": "ANAT_AIRWAY", "text": "upper airway"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "DEV_INSTRUMENT", "text": "Q190 video bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "laryngeal mask airway"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "DEV_INSTRUMENT", "text": "laryngeal mask airway"},
    {"label": "ANAT_AIRWAY", "text": "vocal cords"},
    {"label": "ANAT_AIRWAY", "text": "subglottic space"},
    {"label": "ANAT_AIRWAY", "text": "trachea"},
    {"label": "ANAT_AIRWAY", "text": "carina"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "ANAT_AIRWAY", "text": "bronchial mucosa"},
    {"label": "DEV_INSTRUMENT", "text": "Q190 video bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "UC180F convex probe endobronchial ultrasound (EBUS) bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "laryngeal mask airway"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "PROC_METHOD", "text": "EBUS"},
    {"label": "ANAT_LN_STATION", "text": "11Rs"},
    {"label": "PROC_ACTION", "text": "transbronchial needle aspiration"},
    {"label": "PROC_ACTION", "text": "TBNA"},
    {"label": "DEV_NEEDLE", "text": "19-gauge"},
    {"label": "DEV_NEEDLE", "text": "21 gauge"},
    {"label": "MEAS_COUNT", "text": "eight"},
    {"label": "PROC_ACTION", "text": "biopsies"},
    {"label": "OBS_ROSE", "text": "lymphocytes"},
    {"label": "ANAT_LN_STATION", "text": "station 7"},
    {"label": "PROC_ACTION", "text": "transbronchial needle aspiration"},
    {"label": "PROC_ACTION", "text": "TBNA"},
    {"label": "DEV_NEEDLE", "text": "19-gauge"},
    {"label": "DEV_NEEDLE", "text": "21 gauge"},
    {"label": "MEAS_COUNT", "text": "eight"},
    {"label": "PROC_ACTION", "text": "biopsies"},
    {"label": "OBS_ROSE", "text": "lymphocytes"},
    {"label": "ANAT_LN_STATION", "text": "station 4R"},
    {"label": "PROC_ACTION", "text": "transbronchial needle aspiration"},
    {"label": "PROC_ACTION", "text": "TBNA"},
    {"label": "DEV_NEEDLE", "text": "19-gauge"},
    {"label": "OBS_ROSE", "text": "scant tissue"},
    {"label": "MEAS_COUNT", "text": "single pass"},
    {"label": "ANAT_LN_STATION", "text": "station 7"},
    {"label": "DEV_NEEDLE", "text": "19-gauge"},
    {"label": "DEV_INSTRUMENT", "text": "sheath"},
    {"label": "DEV_INSTRUMENT", "text": "spybite mini-forceps"},
    {"label": "PROC_METHOD", "text": "EBUS"},
    {"label": "PROC_ACTION", "text": "biopsies"},
    {"label": "MEAS_COUNT", "text": "four"},
    {"label": "PROC_METHOD", "text": "EBUS"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"},
    {"label": "DEV_INSTRUMENT", "text": "Q190 video bronchoscope"},
    {"label": "PROC_ACTION", "text": "suctioning"},
    {"label": "OBS_FINDING", "text": "no evidence of active bleeding"},
    {"label": "DEV_INSTRUMENT", "text": "bronchoscope"},
    {"label": "PROC_ACTION", "text": "TBNA"},
    {"label": "DEV_INSTRUMENT", "text": "mini-forceps"},
    {"label": "OUTCOME_COMPLICATION", "text": "No immediate complications"},
    {"label": "MEAS_VOL", "text": "10 cc"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"},
    {"label": "PROC_METHOD", "text": "endobronchial ultrasound-guided"},
    {"label": "DEV_NEEDLE", "text": "needle"},
    {"label": "DEV_INSTRUMENT", "text": "forceps"},
    {"label": "PROC_ACTION", "text": "biopsies"}
]

# ----------------------------------------------------------------------------------
# PATH SETUP
# ----------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# PROCESSING LOGIC
# ----------------------------------------------------------------------------------

def find_spans(text, entity_list):
    """
    Finds start/end indices for entities sequentially to avoid overlap issues.
    """
    spans = []
    current_idx = 0
    
    for ent in entity_list:
        target = ent['text']
        label = ent['label']
        
        # Search from current_idx onwards
        start = text.find(target, current_idx)
        
        if start == -1:
            print(f"WARNING: Could not find '{target}' after index {current_idx}")
            continue
            
        end = start + len(target)
        spans.append({
            "start": start,
            "end": end,
            "label": label,
            "text": target
        })
        
        # Update current_idx to avoid re-matching the same instance
        # if the next entity is the same text
        current_idx = start + 1
        
    return spans

def update_dataset_files(note_id, text, spans, output_dir):
    """
    Updates ner_dataset_all.jsonl, notes.jsonl, spans.jsonl, and stats.json.
    """
    ner_file = output_dir / "ner_dataset_all.jsonl"
    notes_file = output_dir / "notes.jsonl"
    spans_file = output_dir / "spans.jsonl"
    stats_file = output_dir / "stats.json"

    # 1. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": note_id,
        "text": text,
        "entities": spans
    }
    with open(ner_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 2. Update notes.jsonl
    note_entry = {
        "id": note_id,
        "text": text
    }
    with open(notes_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 3. Update spans.jsonl
    with open(spans_file, "a", encoding="utf-8") as f:
        for s in spans:
            span_entry = {
                "span_id": f"{s['label']}_{s['start']}",
                "note_id": note_id,
                "label": s['label'],
                "text": s['text'],
                "start": s['start'],
                "end": s['end']
            }
            f.write(json.dumps(span_entry) + "\n")

    # 4. Update stats.json
    if stats_file.exists():
        with open(stats_file, "r", encoding="utf-8") as f:
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
    stats["total_files"] += 1 # Assuming 1 note = 1 file context
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)

    for s in spans:
        lbl = s['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

def validate_alignment(text, spans, log_path):
    """
    Checks if span indices match the text content.
    """
    warnings = []
    for s in spans:
        extracted = text[s['start']:s['end']]
        if extracted != s['text']:
            msg = f"MISMATCH: Label {s['label']} at {s['start']}:{s['end']} expected '{s['text']}' but got '{extracted}'"
            warnings.append(msg)
            print(msg)
    
    if warnings:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"--- Validation for {NOTE_ID} ---\n")
            for w in warnings:
                f.write(w + "\n")

# ----------------------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    # Calculate Spans
    detected_spans = find_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # Run Updates
    update_dataset_files(NOTE_ID, RAW_TEXT, detected_spans, OUTPUT_DIR)
    
    # Validate
    validate_alignment(RAW_TEXT, detected_spans, ALIGNMENT_LOG_PATH)
    
    print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")