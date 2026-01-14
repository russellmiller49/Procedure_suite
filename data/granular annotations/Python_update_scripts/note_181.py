import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_181"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# We use .parents[2] assuming this script is run from the 'Python_update_scripts' folder structure
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Definition
# ==========================================
RAW_TEXT = """NOTE_ID:  note_181 SOURCE_FILE: note_181.txt PRE-PROCEDURE DIAGNISOS: LEFT UPPER LOBE PULMONARY NODULE
POST- PROCEDURE DIAGNISOS: LEFT UPPER LOBE PULMONARY NODULE
PROCEDURE PERFORMED:  
Flexible bronchoscopy with electromagnetic navigation under flouroscopic and EBUS guidance with transbronchial needle aspiration, Transbronchial biopsy and bronchioalveolar lavage.
CPT 31654 Bronchoscope with Endobronchial Ultrasound guidance for peripheral lesion
CPT 31629 Flexible bronchoscopy with fluoroscopic trans-bronchial needle aspiration
CPT 31628 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with transbronchial lung biopsy(s), single lobe
CPT +31624 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with bronchial alveolar lavage
CPT +31627 Bronchoscopy with computer assisted image guided navigation
INDICATIONS FOR EXAMINATION:   Left upper lobe lung nodule            
MEDICATIONS:    GA
FINDINGS: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the endotracheal tube and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. We then removed the diagnostic Q190 bronchoscope and the super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using navigational map we attempted to advance the 180 degree edge catheter into the proximity of the lesion within apico-posterior branch of left upper lobe.
Radial probe was used to attempt to confirm presence within the lesion.
Although we were able to navigate directly to the lesion with navigation the radial probe view was suboptimal.
Biopsy was performed initially with triple needle brush and TBNA needle.
ROSE did not reveal evidence to support that we were within the lesion.
Multiple attempts were made to manipulate the catheter and biopsies were then performed with a variety of instruments to include peripheral needle, and forceps, brush under fluoroscopic visualization.
The specimens reviewed on-site remained suboptimal.  Multiple forceps biopsies were performed within the location of the lesion and placed in cell-block.
After which a mini-BAL was then performed through the super-D catheter.
We then removed the therapeutic bronchoscope with super-D catheter and reinserted the diagnostic scope at which point repeat airway inspection was then performed and once we were satisfied that no bleeding occurred, the bronchoscope was removed and the procedure completed.
ESTIMATED BLOOD LOSS:   None 
COMPLICATIONS:                 None

IMPRESSION:  
- S/P bronchoscopy with biopsy and lavage.
- Suboptimal navigational localization 
RECOMMENDATIONS
- Transfer to post-procedural unit
- Post-procedure CXR
- D/C home once criteria met
- Await pathology"""

# Entity list based on Label_guide_UPDATED.csv
# Order matters: text is searched sequentially to handle duplicates.
ENTITIES_TO_EXTRACT = [
    # Header / Pre-op
    ("ANAT_LUNG_LOC", "LEFT UPPER LOBE"),
    ("OBS_LESION", "PULMONARY NODULE"),
    ("ANAT_LUNG_LOC", "LEFT UPPER LOBE"), # Post-procedure line
    ("OBS_LESION", "PULMONARY NODULE"),
    
    # Procedure Performed
    ("PROC_ACTION", "Flexible bronchoscopy"),
    ("PROC_METHOD", "electromagnetic navigation"),
    ("PROC_METHOD", "flouroscopic"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("PROC_ACTION", "Transbronchial biopsy"),
    ("PROC_ACTION", "bronchioalveolar lavage"),
    
    # Indications
    ("ANAT_LUNG_LOC", "Left upper lobe"),
    ("OBS_LESION", "lung nodule"),
    
    # Findings - Paragraph 1
    ("ANAT_AIRWAY", "tracheobronchial tree"), # "topical anesthesia to the..."
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # "...advanced to the..."
    
    # Findings - Paragraph 2
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    
    # Findings - Paragraph 3
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("OBS_LESION", "endobronchial lesions"),
    ("DEV_INSTRUMENT", "Q190 bronchoscope"),
    ("DEV_INSTRUMENT", "super-dimension navigational catheter"),
    ("DEV_INSTRUMENT", "T190 therapeutic bronchoscope"),
    
    # Findings - Paragraph 4
    ("ANAT_LUNG_LOC", "apico-posterior branch of left upper lobe"),
    
    # Findings - Paragraph 5
    ("DEV_INSTRUMENT", "Radial probe"),
    ("OBS_LESION", "lesion"),
    
    # Findings - Paragraph 6
    ("OBS_LESION", "lesion"),
    ("DEV_INSTRUMENT", "radial probe"),
    
    # Findings - Paragraph 7
    ("PROC_ACTION", "Biopsy"),
    ("DEV_INSTRUMENT", "triple needle brush"),
    ("DEV_NEEDLE", "TBNA needle"),
    
    # Findings - Paragraph 8
    ("OBS_LESION", "lesion"),
    
    # Findings - Paragraph 9
    ("DEV_CATHETER", "catheter"), # "manipulate the catheter" - contextually referring to the nav catheter, but usually DEV_CATHETER matches "catheter" if not specific instrument.
    # Note: Schema says DEV_CATHETER is "Pleural/drainage". However, nav catheter often gets tagged DEV_INSTRUMENT if specific, or generic catheter. 
    # Given "super-dimension navigational catheter" was DEV_INSTRUMENT, we will treat generic "catheter" here as DEV_INSTRUMENT to match context, or skip if ambiguous.
    # Let's skip generic "catheter" here to avoid polluting DEV_CATHETER (drainage).
    
    ("PROC_ACTION", "biopsies"),
    ("DEV_NEEDLE", "peripheral needle"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "brush"),
    ("PROC_METHOD", "fluoroscopic"),
    
    # Findings - Paragraph 10
    ("DEV_INSTRUMENT", "forceps"), # "forceps biopsies" - splitting as DEV + ACTION
    ("PROC_ACTION", "biopsies"),
    ("OBS_LESION", "lesion"),
    ("SPECIMEN", "cell-block"),
    
    # Findings - Paragraph 11
    ("PROC_ACTION", "mini-BAL"),
    ("DEV_INSTRUMENT", "super-D catheter"),
    
    # Findings - Paragraph 12
    ("DEV_INSTRUMENT", "therapeutic bronchoscope"),
    ("DEV_INSTRUMENT", "super-D catheter"),
    ("DEV_INSTRUMENT", "diagnostic scope"),
    
    # Impression
    ("PROC_ACTION", "bronchoscopy"),
    ("PROC_ACTION", "biopsy"),
    ("PROC_ACTION", "lavage"),
    ("OBS_FINDING", "Suboptimal navigational localization")
]

# ==========================================
# 3. Execution Engine
# ==========================================

def update_ner_pipeline():
    # 1. Calculate Offsets
    processed_entities = []
    search_start_index = 0
    
    for label, substr in ENTITIES_TO_EXTRACT:
        start = RAW_TEXT.find(substr, search_start_index)
        
        if start == -1:
            # Fallback: search from beginning if not found sequentially (should not happen if ordered correctly)
            start = RAW_TEXT.find(substr)
            if start == -1:
                print(f"Warning: Could not find entity '{substr}' in text.")
                continue
        
        end = start + len(substr)
        processed_entities.append({
            "start": start,
            "end": end,
            "label": label,
            "text": substr
        })
        
        # Update search index to just after this match to find the next sequential one
        search_start_index = start + 1

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in processed_entities]
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    spans_entries = []
    for e in processed_entities:
        span_id = f"{e['label']}_{e['start']}"
        spans_entries.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        })
    
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for entry in spans_entries:
            f.write(json.dumps(entry) + "\n")

    # 5. Update stats.json
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Initialize default if missing (unlikely based on prompt)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(processed_entities)
    stats["total_spans_valid"] += len(processed_entities)

    for e in processed_entities:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        for e in processed_entities:
            extracted_text = RAW_TEXT[e["start"]:e["end"]]
            if extracted_text != e["text"]:
                log_msg = f"MISMATCH: ID {NOTE_ID}, Label {e['label']}, Expected '{e['text']}', Got '{extracted_text}'"
                print(log_msg)
                log_file.write(log_msg + "\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(processed_entities)} entities.")

if __name__ == "__main__":
    update_ner_pipeline()