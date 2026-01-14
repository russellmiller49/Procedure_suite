import json
import os
import datetime
from pathlib import Path
import re

# -----------------------------------------------------------------------------
# 1. Configuration & Path Setup
# -----------------------------------------------------------------------------
NOTE_ID = "note_224"
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"
STATS_PATH = OUTPUT_DIR / "stats.json"
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"

# -----------------------------------------------------------------------------
# 2. Input Data
# -----------------------------------------------------------------------------
RAW_TEXT = """Procedure Name: Bronchoscopy with brush and BAL
Indications: FDG avid left hilar lymph node vs parenchymal lesion
Medications: via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The carina is sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
Left upper lobe stump from previous lobectomy appeared intact.Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The bronchoscope was then removed and the Q180 EBUS bronchoscope was inserted and we attempted to advance it into the proximal left upper lobe but were unable to adequately visualize lesion.
We then re-inserted the Q190 video bronchoscope and attempted to visualized lesion with radial ultrasound but were also unsuccessful.
At this point brush biopsy was performed in the proximal left  lower lobe takeoff near the area of concern followed by bronchioloalveolar lavage.
Given the proximity of the lesion to pulmonary vasculature and inability to adequately visualize with radial ultrasound biopsies with forceps or needles were deemed to be too high risk and not performed.
After samples were obtained the bronchoscope was removed and the procedure was complete
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Technically unsuccessful convex and radial ultrasound localization of left hilar abnormality 
- Uncomplicated BAL and brush biopsy of the left lower lobe 
- Will await final pathology results"""

# Define entities to extract based on Label_guide_UPDATED.csv
# Format: (Label, Text_Snippet, Occurrence_Index)
# Occurrence_Index: 0 for 1st match, 1 for 2nd match, etc. -1 for all matches (careful with overlaps)
# We will use a more robust finding mechanism below.

TARGET_ENTITIES = [
    # Header/Indications
    ("DEV_INSTRUMENT", "brush", 0),
    ("PROC_ACTION", "BAL", 0),
    ("LATERALITY", "left", 0),
    ("ANAT_LN_STATION", "hilar", 0),
    ("ANAT_LUNG_LOC", "parenchymal", 0),
    ("OBS_LESION", "lesion", 0), # "parenchymal lesion"
    
    # Body
    ("ANAT_AIRWAY", "upper airway", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 0),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope", 0),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 1),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 1),
    ("ANAT_AIRWAY", "vocal cords", 0),
    ("ANAT_AIRWAY", "subglottic space", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("ANAT_AIRWAY", "carina", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 2),
    
    # Findings
    ("ANAT_LUNG_LOC", "Left upper lobe", 0),
    ("ANAT_AIRWAY", "Bronchial mucosa", 0),
    ("OBS_LESION", "lesions", 0), # "endobronchial lesions"
    ("OBS_FINDING", "secretions", 0),
    ("DEV_INSTRUMENT", "bronchoscope", 0), # "The bronchoscope was then..."
    ("DEV_INSTRUMENT", "Q180 EBUS bronchoscope", 0),
    ("ANAT_LUNG_LOC", "left upper lobe", 1), # "proximal left upper lobe"
    ("OBS_LESION", "lesion", 1), # "visualize lesion"
    ("DEV_INSTRUMENT", "Q190 video bronchoscope", 1),
    ("OBS_LESION", "lesion", 2), # "visualized lesion"
    ("PROC_METHOD", "radial ultrasound", 0),
    
    # Procedure Actions
    ("DEV_INSTRUMENT", "brush", 1), # "brush biopsy"
    ("PROC_ACTION", "biopsy", 0), # "brush biopsy"
    ("ANAT_LUNG_LOC", "left  lower lobe", 0), # Note double space in text
    ("PROC_ACTION", "bronchioloalveolar lavage", 0),
    ("OBS_LESION", "lesion", 3), # "proximity of the lesion"
    ("PROC_METHOD", "radial ultrasound", 1),
    ("PROC_ACTION", "biopsies", 0),
    ("DEV_INSTRUMENT", "forceps", 0),
    ("DEV_NEEDLE", "needles", 0),
    ("DEV_INSTRUMENT", "bronchoscope", 1),
    ("MEAS_VOL", "5 cc", 0),
    
    # Diagnosis/Summary
    ("PROC_METHOD", "convex", 0),
    ("PROC_METHOD", "radial ultrasound", 2),
    ("LATERALITY", "left", 4), # "left hilar abnormality"
    ("ANAT_LN_STATION", "hilar", 1),
    ("OBS_LESION", "abnormality", 0),
    ("PROC_ACTION", "BAL", 1),
    ("DEV_INSTRUMENT", "brush", 2),
    ("PROC_ACTION", "biopsy", 1),
    ("ANAT_LUNG_LOC", "left lower lobe", 0), # "left lower lobe" (single space here)
]

# -----------------------------------------------------------------------------
# 3. Processing Logic
# -----------------------------------------------------------------------------

def extract_entities(text, targets):
    """
    Finds entity spans in text. Handles finding the Nth occurrence of a substring.
    """
    found_entities = []
    
    # Helper to track current search index for repeated terms
    # Maps "term" -> next_start_index
    search_cursors = {} 
    
    # We sort targets by their occurrence index to process them in order for each term
    # But since we scan manually, we just need to be careful.
    
    # Actually, a safer way is to iterate through the text for every target
    # tailored to the specific occurrence count requested.
    
    for label, substr, target_occurrence in targets:
        # Find all matches of substr
        matches = [m for m in re.finditer(re.escape(substr), text)]
        
        if len(matches) > target_occurrence:
            match = matches[target_occurrence]
            span_start = match.start()
            span_end = match.end()
            
            found_entities.append({
                "label": label,
                "text": substr,
                "start": span_start,
                "end": span_end
            })
        else:
            # Log missing if not found (strictly for debugging this script generation)
            print(f"Warning: Could not find occurrence {target_occurrence} of '{substr}'")
            
    # Sort by start index
    found_entities.sort(key=lambda x: x["start"])
    return found_entities

def update_files():
    # 1. Generate Entity List
    entities = extract_entities(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. JSONL Entries
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # 3. Write/Append to files
    
    # Update ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Update notes.jsonl
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Update spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for ent in entities:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_entry) + "\n")
            
    # 4. Update Stats
    if STATS_PATH.exists():
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
    # Assuming file count increases by 1 for this operation
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    for ent in entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
        
    # 5. Validation & Logging
    with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as log_f:
        for ent in entities:
            sliced_text = RAW_TEXT[ent['start']:ent['end']]
            if sliced_text != ent['text']:
                log_entry = f"{datetime.datetime.now()} - MISMATCH - Note: {NOTE_ID}, Label: {ent['label']}, Expected: '{ent['text']}', Got: '{sliced_text}'\n"
                log_f.write(log_entry)

if __name__ == "__main__":
    update_files()
    print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")