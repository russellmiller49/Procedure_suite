import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 1. CONFIGURATION & RAW DATA
# ==============================================================================

NOTE_ID = "note_186"
RAW_TEXT = """Indications: Pulmonary nodule requiring diagnosis/staging.
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level without endobronchial lesions visualized.
Anatomy was normal with exception of fish mouth dynamic obstruction of the right middle lobe.
The bronchoscope was then removed and the P190 ultrathin video bronchoscope was inserted into the airway and advanced into the apical segment of the right upper lobe were endobronchial tumor was visualized.
The radial EBUS probe was inserted through the bronchoscope and advanced into the airway and an eccentric view of the lesion was identified.
Biopsies were then performed with a variety of instruments to include peripheral needle forceps and brush. ROSE identified malignancy.
After adequate samples were obtained, the video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) was only met in station station 4R and 11Rs.
Sampling by transbronchial needle aspiration was performed using an Olympus EBUSTBNA 22 gauge needle.
All samples were sent for routine cytology. Onsite path evaluation showed adequate lymphocytes in the 4R lymph node and were non-diagnostic in the 11Rs.
The bronchoscope was then removed and the P190 ultrathin video bronchoscope was inserted again into the airway and 5 more forceps biopsies were obtained in the apical segment of the right upper lobe for cell block and molecular analysis.
The bronchoscope was then removed and the Q190 re-inserted into the airways.
DECAMP research samples were then performed with brushing within the right upper lobe, right middle lobe and transbronchial biopsies in the RUL, RML and LUL.
We then observed for evidence of active bleeding and none was identified. The bronchoscope was removed and the procedure completed.
Complications: 	
-None 
Estimated Blood Loss:  5 cc.
Recommendations:
- Transfer to post-procedure unit
- Await biopsy results 
- Discharge home once criteria met.
Dr. Miller (Attending) was personally present and involved in all key phases of the procedure."""

# Define target entities based on Label_guide_UPDATED.csv
# Format: (Text_Snippet, Label)
# Note: This list allows duplicates if the same text appears in different contexts with the same label.
# Unique context handling is done via the `find_spans` helper.

TARGETS = [
    ("Pulmonary nodule", "OBS_LESION"),
    ("Propofol", "MEDICATION"),
    ("upper airway", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("mouth", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"), # Fits 'Other transient tools' or specific airway device
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("endobronchial lesions", "OBS_LESION"),
    ("fish mouth dynamic obstruction", "OBS_FINDING"),
    ("right middle lobe", "ANAT_LUNG_LOC"),
    ("P190 ultrathin video bronchoscope", "DEV_INSTRUMENT"),
    ("apical segment of the right upper lobe", "ANAT_LUNG_LOC"),
    ("endobronchial tumor", "OBS_LESION"),
    ("radial EBUS probe", "DEV_INSTRUMENT"),
    ("lesion", "OBS_LESION"),
    ("Biopsies", "PROC_ACTION"),
    ("peripheral needle forceps", "DEV_INSTRUMENT"),
    ("brush", "DEV_INSTRUMENT"),
    ("malignancy", "OBS_ROSE"), # From "ROSE identified malignancy"
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT"),
    ("4R", "ANAT_LN_STATION"),
    ("11Rs", "ANAT_LN_STATION"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("22 gauge", "DEV_NEEDLE"),
    ("lymphocytes", "OBS_ROSE"),
    ("non-diagnostic", "OBS_ROSE"),
    ("P190 ultrathin video bronchoscope", "DEV_INSTRUMENT"),
    ("forceps", "DEV_INSTRUMENT"),
    ("Biopsies", "PROC_ACTION"), # Context: "5 more forceps biopsies" - matched by text generally
    ("apical segment of the right upper lobe", "ANAT_LUNG_LOC"),
    ("cell block", "SPECIMEN"),
    ("Q190", "DEV_INSTRUMENT"),
    ("brushing", "PROC_ACTION"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("right middle lobe", "ANAT_LUNG_LOC"),
    ("transbronchial biopsies", "PROC_ACTION"),
    ("RUL", "ANAT_LUNG_LOC"),
    ("RML", "ANAT_LUNG_LOC"),
    ("LUL", "ANAT_LUNG_LOC"),
    ("None", "OUTCOME_COMPLICATION"),
    ("5 cc", "MEAS_VOL"),
    ("5mm", "MEAS_SIZE")
]

# ==============================================================================
# 2. SETUP PATHS
# ==============================================================================

# Dynamic path resolution using pathlib
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================

def find_spans(text, targets):
    """
    Finds all occurrences of target strings in the text and returns valid span objects.
    Handles multiple occurrences by finding them sequentially.
    """
    spans = []
    text_lower = text.lower()
    
    # Sort targets by length (descending) to prioritize longer matches if needed,
    # though strict sequential finding is usually sufficient.
    # We maintain a cursor for each unique target text to handle duplicates.
    
    # Group targets by text to handle same text -> different label (unlikely here but good practice)
    # or same text -> multiple occurrences
    
    # Simple approach: Find all iterations of the target string
    found_offsets = set() # (start, end)
    
    for target_text, label in targets:
        # Create a regex to find the target text (case-insensitive for safety, 
        # but exact match preferred if capitalization matters. Given input, usually exact).
        # Using re.escape to handle punctuation like '(' or ')' in text.
        pattern = re.escape(target_text)
        
        # Iterate over all matches
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = match.start()
            end = match.end()
            
            # Check overlap logic if necessary, or just add all valid ones.
            # We filter duplicates (same start/end/label) later.
            
            # Ensure we capture the exact original casing from the raw text for the record
            actual_text = text[start:end]
            
            span_obj = {
                "start": start,
                "end": end,
                "label": label,
                "text": actual_text
            }
            
            # Create a unique key to prevent exact duplicate processing
            span_key = (start, end, label)
            
            if span_key not in found_offsets:
                spans.append(span_obj)
                found_offsets.add(span_key)
                
    # Sort spans by start index
    spans.sort(key=lambda x: x["start"])
    return spans

# ==============================================================================
# 4. EXECUTION
# ==============================================================================

def main():
    # 1. Extract Spans
    extracted_spans = find_spans(RAW_TEXT, TARGETS)
    
    # 2. Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # 3. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "start": span["start"],
                "end": span["end"],
                "label": span["label"]
            }
            for span in extracted_spans
        ]
    }
    with open(NER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # 4. Update spans.jsonl
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
        for span in extracted_spans:
            span_record = {
                "span_id": f"{span['label']}_{span['start']}",
                "note_id": NOTE_ID,
                "label": span['label'],
                "text": span['text'],
                "start": span['start'],
                "end": span['end']
            }
            f.write(json.dumps(span_record) + "\n")
            
    # 5. Update stats.json
    # Load existing stats
    if STATS_FILE.exists():
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Fallback initialization if file missing (unlikely based on prompt)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    # Update counts
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    # Update label counts
    for span in extracted_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    # Save stats
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Verification & Logging
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        for span in extracted_spans:
            # Verify text alignment
            snippet = RAW_TEXT[span["start"]:span["end"]]
            if snippet != span["text"]:
                log.write(f"MISMATCH {NOTE_ID}: Expected '{span['text']}' but got '{snippet}' at {span['start']}:{span['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Added {len(extracted_spans)} entities.")

if __name__ == "__main__":
    main()