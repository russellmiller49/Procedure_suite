import json
import os
import datetime
import re
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_187"

# The raw content of the note provided in the input
RAW_TEXT = """Procedure Name: EBUS bronchoscopy, transbronchial lung biopsy and bronchoalveolar lavage
Indications: Mediastinal adenopathy and interstitial lung disease 
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The carina is sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Ultrasound was utilized to identify and measure the radiographically enlarged station 7, 4R and 11Rs lymph nodes.
Sampling by transbronchial needle aspiration was performed beginning with the station 4R lymph node, followed by the station 7 lymph node and finally the 4L lymph node using an Olympus EBUSTBNA 22 gauge needle.
Rapid onsite evaluation read as benign lymphoid tissue in all sampled nodes.
All samples were sent for routine cytology and flow cytometry.
Following completion of EBUS bronchoscopy the video bronchoscope was re-inserted and blood was suctioned from the airway.
Using fluoroscopy transbronchial forceps lung biopsies were performed in both the right middle lobe and right lower lobe.
Finally BAL was performed with 120cc instillation and 40cc return.
Prior to removing the bronchoscope an airway examination was performed and no evidence of active bleeding was seen.
The bronchoscope was removed and procedure completed. 

Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Technically successful EBUS bronchoscopy, transbronchial lung biopsy and bronchoalveolar lavage 
- Will await final pathology and culture results"""

# Define entities to extract based on the Rulebook (Label_guide_UPDATED.csv)
# We map specific text phrases to their strict labels.
TARGET_ENTITIES = [
    {"label": "PROC_METHOD", "text": "EBUS"}, # From "EBUS bronchoscopy" header
    {"label": "PROC_ACTION", "text": "bronchoscopy"}, # From header
    {"label": "PROC_ACTION", "text": "transbronchial lung biopsy"}, # From header
    {"label": "PROC_ACTION", "text": "bronchoalveolar lavage"}, # From header
    {"label": "OBS_LESION", "text": "Mediastinal adenopathy"},
    {"label": "MEDICATION", "text": "Propofol"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"}, # First occurrence
    {"label": "DEV_INSTRUMENT", "text": "video bronchoscope"}, # Q190
    {"label": "ANAT_AIRWAY", "text": "trachea"},
    {"label": "ANAT_AIRWAY", "text": "carina"},
    {"label": "ANAT_AIRWAY", "text": "Bronchial"}, # From "Bronchial mucosa"
    {"label": "DEV_INSTRUMENT", "text": "video bronchoscope"}, # Second occurrence
    {"label": "DEV_INSTRUMENT", "text": "EBUS bronchoscope"}, # UC180F
    {"label": "PROC_METHOD", "text": "Ultrasound"},
    {"label": "ANAT_LN_STATION", "text": "station 7"},
    {"label": "ANAT_LN_STATION", "text": "4R"},
    {"label": "ANAT_LN_STATION", "text": "11Rs"},
    {"label": "PROC_ACTION", "text": "transbronchial needle aspiration"},
    {"label": "ANAT_LN_STATION", "text": "station 4R"},
    {"label": "ANAT_LN_STATION", "text": "station 7"}, # Second occurrence
    {"label": "ANAT_LN_STATION", "text": "4L"},
    {"label": "DEV_NEEDLE", "text": "22 gauge needle"},
    {"label": "OBS_ROSE", "text": "benign lymphoid tissue"},
    {"label": "PROC_METHOD", "text": "EBUS"}, # From "completion of EBUS"
    {"label": "PROC_ACTION", "text": "bronchoscopy"}, # From "completion of EBUS bronchoscopy"
    {"label": "DEV_INSTRUMENT", "text": "video bronchoscope"}, # Third occurrence
    {"label": "PROC_METHOD", "text": "fluoroscopy"},
    {"label": "DEV_INSTRUMENT", "text": "forceps"}, # implied in "transbronchial forceps lung biopsies" -> "forceps" is DEV_INSTRUMENT
    {"label": "PROC_ACTION", "text": "transbronchial forceps lung biopsies"}, # Or just biopsy. "lung biopsies" is safer but "transbronchial..." matches header.
    {"label": "ANAT_LUNG_LOC", "text": "right middle lobe"},
    {"label": "ANAT_LUNG_LOC", "text": "right lower lobe"},
    {"label": "PROC_ACTION", "text": "BAL"},
    {"label": "MEAS_VOL", "text": "120cc"},
    {"label": "MEAS_VOL", "text": "40cc"},
    {"label": "OUTCOME_COMPLICATION", "text": "No immediate complications"},
    {"label": "MEAS_VOL", "text": "5 cc"},
]

# =============================================================================
# SETUP PATHS
# =============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PATH_NER_DATASET = OUTPUT_DIR / "ner_dataset_all.jsonl"
PATH_NOTES = OUTPUT_DIR / "notes.jsonl"
PATH_SPANS = OUTPUT_DIR / "spans.jsonl"
PATH_STATS = OUTPUT_DIR / "stats.json"
PATH_LOG = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def find_spans(raw_text, entities):
    """
    Finds exact start/end indices for entities in the text.
    Handles multiple occurrences by keeping track of the search cursor.
    """
    spans = []
    # We sort entities by their order of appearance to ensure we find the correct sequential duplicates
    # However, since the input list `TARGET_ENTITIES` is manually ordered by appearance in text, 
    # we can iterate strictly.
    
    # To be robust against manual list ordering errors, we scan the text.
    # But for strict sequential annotation, we maintain a cursor.
    cursor = 0
    
    for item in entities:
        label = item["label"]
        phrase = item["text"]
        
        # Find the next occurrence of the phrase starting from cursor
        idx = raw_text.find(phrase, cursor)
        
        if idx == -1:
            # Fallback: reset cursor and search from start (in case list wasn't perfectly ordered)
            # This risks mapping to the wrong previous instance, but is a safety net.
            idx = raw_text.find(phrase)
            if idx == -1:
                print(f"WARNING: Could not find phrase '{phrase}' in text.")
                continue
        
        start = idx
        end = idx + len(phrase)
        
        span_obj = {
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": phrase,
            "start": start,
            "end": end
        }
        spans.append(span_obj)
        
        # Update cursor to avoid re-matching the exact same characters for the same logical entity 
        # (though strictly overlaps are allowed, we usually move forward)
        cursor = start + 1 

    return spans

def update_jsonl(file_path, new_record):
    """Appends a JSON line to a file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def update_stats(file_path, spans):
    """Updates the stats.json file with new counts."""
    if not os.path.exists(file_path):
        print("Stats file not found, creating new.")
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)

    for span in spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def log_warning(message):
    """Logs alignment warnings."""
    with open(PATH_LOG, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")

# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    print(f"Processing {NOTE_ID}...")

    # 1. Extract Spans
    spans = find_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Validate Spans
    valid_spans = []
    for span in spans:
        extracted = RAW_TEXT[span['start']:span['end']]
        if extracted != span['text']:
            log_warning(f"Mismatch in {NOTE_ID}: Expected '{span['text']}', found '{extracted}' at {span['start']}")
        else:
            valid_spans.append(span)

    # 3. Construct Datasets
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": valid_spans
    }
    
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # 4. Write Updates
    print(f"Appending to {PATH_NER_DATASET}...")
    update_jsonl(PATH_NER_DATASET, ner_record)

    print(f"Appending to {PATH_NOTES}...")
    update_jsonl(PATH_NOTES, note_record)

    print(f"Appending {len(valid_spans)} spans to {PATH_SPANS}...")
    for span in valid_spans:
        update_jsonl(PATH_SPANS, span)

    # 5. Update Stats
    print(f"Updating stats in {PATH_STATS}...")
    update_stats(PATH_STATS, valid_spans)

    print("Done.")

if __name__ == "__main__":
    main()