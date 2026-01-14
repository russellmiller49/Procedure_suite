import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_159"
RAW_TEXT = """Indications: Left upper lobe mass 
Medications: Propofol infusion via anesthesia assistance  
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. We then removed the diagnostic Q190 bronchoscopy and the super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using navigational map we attempted to advance the 90 degree edge catheter into the proximity of the lesion within the left upper lobe.
Confirmation of placement once at the point of interest with radial ultrasound showed a concentric view within the lesion.
Biopsies were then performed with a variety of instruments to include peripheral needle, brush, triple needle brush and forceps, under fluoroscopic visualization.
After adequate samples were obtained the bronchoscope was removed and the procedure completed
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Flexible bronchoscopy with successful navigational biopsy of left upper lobe nodule.  
- Await final pathology"""

# Define entities to extract (Strictly matching Label_guide_UPDATED.csv)
# Format: (Text_Substring, Label)
ENTITIES_TO_EXTRACT = [
    ("Left upper lobe", "ANAT_LUNG_LOC"),
    ("mass", "OBS_LESION"),
    ("Propofol", "MEDICATION"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("endobronchial lesions", "OBS_LESION"),
    ("Q190 bronchoscopy", "DEV_INSTRUMENT"), # Context: "removed the diagnostic..."
    ("super-dimension navigational catheter", "DEV_INSTRUMENT"),
    ("T190 therapeutic bronchoscope", "DEV_INSTRUMENT"),
    ("navigational", "PROC_METHOD"), # In 'navigational map'
    ("90 degree edge catheter", "DEV_INSTRUMENT"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("radial ultrasound", "PROC_METHOD"),
    ("Biopsies", "PROC_ACTION"),
    ("peripheral needle", "DEV_NEEDLE"),
    ("brush", "DEV_INSTRUMENT"),
    ("triple needle brush", "DEV_INSTRUMENT"),
    ("forceps", "DEV_INSTRUMENT"),
    ("fluoroscopic", "PROC_METHOD"),
    ("bronchoscopy", "PROC_ACTION"), # In post-procedure diagnosis
    ("navigational", "PROC_METHOD"),
    ("biopsy", "PROC_ACTION"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("nodule", "OBS_LESION"),
]

# ==========================================
# PATH SETUP
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING LOGIC
# ==========================================

def update_dataset():
    # 1. Calculate Spans
    spans = []
    cursor = 0
    # Sort entities to ensure we find them in order or handle multiple occurrences correctly
    # Simple strategy: search from last cursor position
    
    # We will iterate through the list defined above. 
    # NOTE: This assumes the list ENTITIES_TO_EXTRACT is ordered roughly by appearance 
    # or that we scan from 0 for each unique text if we want all, but here we want specific instances.
    # To be robust, we will find the *next* occurrence of the text after the current cursor.
    
    formatted_entities = []
    
    current_search_index = 0
    
    for text, label in ENTITIES_TO_EXTRACT:
        # Find text starting from current_search_index
        start = RAW_TEXT.find(text, current_search_index)
        
        if start == -1:
            # Fallback: specific handling if order in list doesn't match text order
            # Try searching from beginning if not found (risk of mapping wrong instance)
            start = RAW_TEXT.find(text)
            if start == -1:
                log_warning(f"Entity not found: '{text}'")
                continue
        
        end = start + len(text)
        
        # Verify alignment
        extracted = RAW_TEXT[start:end]
        if extracted != text:
             log_warning(f"Mismatch: Expected '{text}', got '{extracted}'")
             continue

        span_obj = {
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text,
            "start": start,
            "end": end
        }
        spans.append(span_obj)
        
        # For the NER training file, the format is [start, end, label]
        formatted_entities.append([start, end, label])
        
        # Update cursor to avoid finding the same instance for the next identical entity
        current_search_index = start + 1

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": formatted_entities
    }
    
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")

    # 5. Update stats.json
    update_stats(spans)
    
    print(f"Successfully processed {NOTE_ID}.")
    print(f"Extracted {len(spans)} entities.")

def update_stats(new_spans):
    if not STATS_PATH.exists():
        print("Stats file not found, skipping stats update.")
        return

    with open(STATS_PATH, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    # Increment totals
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans) # Assuming all valid for this script

    # Update label counts
    for span in new_spans:
        lbl = span["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def log_warning(message):
    timestamp = datetime.now().isoformat()
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {NOTE_ID}: {message}\n")
    print(f"WARNING: {message}")

if __name__ == "__main__":
    update_dataset()