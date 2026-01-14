import json
import os
import datetime
from pathlib import Path

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
NOTE_ID = "note_153"
DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d")

# Raw text content of the note
RAW_TEXT = """NOTE_ID:  note_153 SOURCE_FILE: note_153.txt Indications: Hilar adenopathy, presumed metastatic breast CA
Procedure Performed: EBUS bronchoscopy single station.
Pre-operative diagnosis: hilar adenopathy 
Post-operative diagnosis: malignant hilar adenopathy 
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The carina is sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Ultrasound was utilized to identify and measure the radiographically suspicious station 11Ri lymph node.
Sampling by transbronchial needle aspiration was performed beginning with the Olympus EBUS-TBNA 22 gauge needle.
Rapid onsite evaluation read as malignancy. All samples were sent for routine cytology.
Following completion of EBUS bronchoscopy the video bronchoscope was re-inserted and blood was suctioned from the airway.
The bronchoscope was removed and procedure completed. 

Complications: No immediate complications
Estimated Blood Loss: 10 cc.
Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# Define entities to extract (Substring, Label)
# Order matters for simple sequential finding logic if duplicates exist.
TO_EXTRACT = [
    ("Hilar adenopathy", "OBS_LESION"),
    ("metastatic breast CA", "OBS_LESION"),
    ("EBUS bronchoscopy", "PROC_METHOD"),
    ("hilar adenopathy", "OBS_LESION"), # Pre-op
    ("malignant hilar adenopathy", "OBS_LESION"), # Post-op
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Bronchial mucosa", "ANAT_AIRWAY"),
    ("endobronchial lesions", "OBS_LESION"),
    ("secretions", "OBS_FINDING"),
    ("video bronchoscope", "DEV_INSTRUMENT"),
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("station 11Ri", "ANAT_LN_STATION"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("22 gauge needle", "DEV_NEEDLE"),
    ("malignancy", "OBS_ROSE"),
    ("cytology", "SPECIMEN"),
    ("EBUS bronchoscopy", "PROC_METHOD"),
    ("video bronchoscope", "DEV_INSTRUMENT"),
    ("blood", "OBS_FINDING"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("10 cc", "MEAS_VOL"),
    ("flexible bronchoscopy", "PROC_METHOD"),
    ("endobronchial ultrasound-guided biopsies", "PROC_ACTION")
]

# ----------------------------------------------------------------------------------
# PATH SETUP
# ----------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG = OUTPUT_DIR / "alignment_warnings.log"
DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"

# ----------------------------------------------------------------------------------
# PROCESSING
# ----------------------------------------------------------------------------------

def process_note():
    # 1. Calculate Indices
    entities_data = []
    search_start_idx = 0
    
    # We loop through TO_EXTRACT. To handle duplicates correctly in order,
    # we can maintain a cursor or use regex. 
    # Here, we scan sequentially to respect the order of appearance in the text
    # if the list is ordered by occurrence.
    # Note: The TO_EXTRACT list above approximates reading order.
    # For safety, we search for the FIRST occurrence after the last found index 
    # to avoid jumping backwards, assuming the list is roughly chronological.
    # If the list is NOT chronological, we would need to reset search_start_idx 
    # or simple search from 0 every time and ensure no overlaps. 
    # Given the strict requirement for valid offsets, we will do a global search 
    # but track used spans to prevent overlaps if needed.
    
    # Simpler approach for this script:
    # Iterate text to find entities.
    
    processed_spans = []
    
    current_cursor = 0
    
    for text_snippet, label in TO_EXTRACT:
        # Find snippet starting from current_cursor
        start = RAW_TEXT.find(text_snippet, current_cursor)
        
        # If not found after cursor, try from beginning (in case list wasn't perfectly ordered)
        # but warn about potential out-of-order/duplicate issues.
        if start == -1:
             start = RAW_TEXT.find(text_snippet)
        
        if start != -1:
            end = start + len(text_snippet)
            
            # Verify alignment
            extracted = RAW_TEXT[start:end]
            if extracted != text_snippet:
                with open(ALIGNMENT_LOG, "a") as log:
                    log.write(f"[{datetime.datetime.now()}] MISMATCH: {label} wanted '{text_snippet}' got '{extracted}'\n")
                continue

            # Add to entity list
            span_obj = {
                "start": start,
                "end": end,
                "label": label,
                "text": text_snippet
            }
            entities_data.append(span_obj)
            
            # Update cursor to end of this entity to find next occurrence of similar terms
            # Only update cursor if we found it forward of our previous position
            if start >= current_cursor:
                current_cursor = end
        else:
             with open(ALIGNMENT_LOG, "a") as log:
                log.write(f"[{datetime.datetime.now()}] NOT FOUND: {label} - '{text_snippet}'\n")

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities_data
    }
    
    with open(DATASET_FILE, "a", encoding="utf-8") as f:
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
        for ent in entities_data:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    if STATS_FILE.exists():
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
    else:
        stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

    stats["total_notes"] += 1
    # Assuming 1 file per note in this pipeline context
    stats["total_files"] += 1
    stats["total_spans_raw"] += len(entities_data)
    stats["total_spans_valid"] += len(entities_data)
    
    # Update label counts
    for ent in entities_data:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)
        
    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities_data)} entities.")

if __name__ == "__main__":
    process_note()