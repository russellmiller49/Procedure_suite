from pathlib import Path
import json
import os
import datetime

# -------------------------------------------------------------------------
# CONFIGURATION & SETUP
# -------------------------------------------------------------------------
NOTE_ID = "note_225"

# Raw text content from the provided file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: left mainstem stem obstruction
POSTOPERATIVE DIAGNOSIS: left lower lobe obstruction secondary to intraluminal fibrinous material.
PROCEDURE PERFORMED: flexible bronchoscopy with cryodebulking 
INDICATIONS: complete lobar collapse  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The trachea and right sided airways were normal. The left mainstem stent was widely patent without evidence of obstruction.
At the takeoff of the left lower lobe just beyond surgical stump there was complete obstruction of the left lower lobe orifice secondary to adherent white waxy fibrinous tissue.
Using the 1.9 mm cryoprobe we are able to extract some of the tissue to visualize the segmental stenosis in the left lower lobe.
We then utilized flexible forceps to slowly debulk the abnormal tissue.
Once we were able to pass the left lower lobe orifice there was continued areas of white necrotic tissue obstruction in the superior segment and anteriomedial segments of the left lower lobe and extending to just proximal to the basilar segments (very similar appearance and location as previous bronchoscopy).
This tissue was also slowly debulked with the flexible forceps until we were able to achieve relatively preserved luminal diameter.
Once we were satisfied that no further intervention was required the flexible bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
Recommendations:
-\tTransfer patient to ward
-\tPlan for IR guided lymphangiogram on 6/20/19 to evaluate for potential plastic bronchitis."""

# Target definitions based on Label_guide_UPDATED.csv
# Format: (Label, Text_Snippet)
# Note: Offsets will be calculated dynamically to ensure precision.
ENTITIES_TO_EXTRACT = [
    ("ANAT_AIRWAY", "left mainstem"), # "left mainstem stem" in text, mapping valid anatomy
    ("OBS_FINDING", "obstruction"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_FINDING", "obstruction"),
    ("OBS_FINDING", "intraluminal fibrinous material"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("PROC_ACTION", "cryodebulking"),
    ("OBS_FINDING", "complete lobar collapse"),
    ("MEDICATION", "topical anesthesia"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("ANAT_AIRWAY", "mouth"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "right sided airways"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "widely patent"), # Matches example in guide
    ("OBS_FINDING", "obstruction"),
    ("ANAT_LUNG_LOC", "takeoff of the left lower lobe"),
    ("ANAT_AIRWAY", "surgical stump"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "complete obstruction"),
    ("ANAT_LUNG_LOC", "left lower lobe orifice"),
    ("OBS_FINDING", "adherent white waxy fibrinous tissue"),
    ("MEAS_SIZE", "1.9 mm"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("PROC_ACTION", "extract"),
    ("OBS_FINDING", "segmental stenosis"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("PROC_ACTION", "debulk"),
    ("OBS_FINDING", "abnormal tissue"),
    ("ANAT_LUNG_LOC", "left lower lobe orifice"),
    ("OBS_FINDING", "white necrotic tissue obstruction"),
    ("ANAT_LUNG_LOC", "superior segment"),
    ("ANAT_LUNG_LOC", "anteriomedial segments"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("ANAT_LUNG_LOC", "basilar segments"),
    ("PROC_ACTION", "debulked"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "preserved luminal diameter"),
    ("DEV_INSTRUMENT", "flexible bronchoscope")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# -------------------------------------------------------------------------
# PROCESSING LOGIC
# -------------------------------------------------------------------------

def find_entity_spans(text, entity_list):
    """
    Finds strict character offsets for entities.
    Handles multiple occurrences by tracking search position.
    """
    spans = []
    # To handle multiple occurrences of the same text, we keep a cursor
    # But since the list is defined in order of appearance in a real extraction scenario,
    # we just need to ensure we find the *correct* instance.
    # For this script, we will scan sequentially to map the defined list to the text.
    
    current_search_index = 0
    
    for label, substr in entity_list:
        start = text.find(substr, current_search_index)
        if start == -1:
            # Fallback: if not found relative to previous, search from beginning (should not happen if ordered)
            start = text.find(substr)
            if start == -1:
                print(f"WARNING: Could not locate entity '{substr}' in text.")
                continue
        
        end = start + len(substr)
        
        # Verify
        extracted = text[start:end]
        if extracted != substr:
             print(f"CRITICAL: Mismatch '{extracted}' vs '{substr}'")
             continue

        span = {
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        }
        spans.append(span)
        
        # Move search index forward to avoid overlapping same-text matches if intended to be sequential
        # (Though some entities might overlap in complex nested NER, here we assume flat or ordered list)
        current_search_index = start + 1 

    return spans

def update_ner_dataset(output_dir, note_id, text, spans):
    file_path = output_dir / "ner_dataset_all.jsonl"
    
    # Construct entry
    entry = {
        "id": note_id,
        "text": text,
        "entities": spans
    }
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes(output_dir, note_id, text):
    file_path = output_dir / "notes.jsonl"
    entry = {"id": note_id, "text": text}
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans(output_dir, note_id, spans):
    file_path = output_dir / "spans.jsonl"
    with open(file_path, "a", encoding="utf-8") as f:
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

def update_stats(output_dir, spans):
    file_path = output_dir / "stats.json"
    
    # Initialize defaults if file missing
    if not file_path.exists():
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {
                    "total_notes": 0,
                    "total_files": 0,
                    "total_spans_raw": 0,
                    "total_spans_valid": 0,
                    "label_counts": {}
                }

    # Update counts
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note = 1 file context here
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)
    
    for s in spans:
        lbl = s["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

def validate_and_log(output_dir, text, spans):
    log_path = output_dir / "alignment_warnings.log"
    warnings = []
    
    for s in spans:
        extracted = text[s['start']:s['end']]
        if extracted != s['text']:
            warnings.append(f"Mismatch in {NOTE_ID}: Expected '{s['text']}', found '{extracted}' at {s['start']}:{s['end']}")
            
    if warnings:
        with open(log_path, "a", encoding="utf-8") as f:
            for w in warnings:
                f.write(f"[{datetime.datetime.now()}] {w}\n")

# -------------------------------------------------------------------------
# EXECUTION
# -------------------------------------------------------------------------

def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Calc Indices
    spans = find_entity_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    update_ner_dataset(OUTPUT_DIR, NOTE_ID, RAW_TEXT, spans)
    
    # 3. Update notes.jsonl
    update_notes(OUTPUT_DIR, NOTE_ID, RAW_TEXT)
    
    # 4. Update spans.jsonl
    update_spans(OUTPUT_DIR, NOTE_ID, spans)
    
    # 5. Update stats.json
    update_stats(OUTPUT_DIR, spans)
    
    # 6. Validate
    validate_and_log(OUTPUT_DIR, RAW_TEXT, spans)
    
    print(f"Success. Output generated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()