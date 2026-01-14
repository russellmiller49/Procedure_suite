import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_178"

# Raw text from note_178.txt (cleaned of [source] tags)
RAW_TEXT = """Indications: Mediastinal adenopathy
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Just distal to the cricoid cartilage the suspicious 2L lymph node was identified Sampling by transbronchial needle aspiration was performed with both the Olympus 19G and Olympus 22G needles with a total of 8 passes performed.
Abundant lymphocytes were seen in rapid onsite pathological evaluation. Samples were sent for both flow and routine cytology.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Estimated Blood Loss: min

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Will await final pathology results"""

# Define entities to extract (Label, Text Fragment)
# The script will locate all exact matches of these fragments.
ENTITY_TARGETS = [
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"), # Note: Text has "The trachea", we match "trachea"
    ("ANAT_AIRWAY", "carina"),
    ("OBS_FINDING", "secretions"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "cricoid cartilage"),
    ("ANAT_LN_STATION", "2L"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "19G"),
    ("DEV_NEEDLE", "22G"),
    ("MEAS_COUNT", "8 passes"),
    ("OBS_ROSE", "lymphocytes"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "suctioning"),
    ("OBS_FINDING", "blood"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("PROC_ACTION", "biopsies")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING LOGIC
# ==========================================

def get_spans(text, targets):
    """
    Finds all non-overlapping occurrences of target strings in text.
    Returns a list of dicts: {'label': label, 'text': text, 'start': start, 'end': end}
    """
    spans = []
    text_lower = text.lower()
    
    for label, target_text in targets:
        target_lower = target_text.lower()
        search_start = 0
        while True:
            start_idx = text_lower.find(target_lower, search_start)
            if start_idx == -1:
                break
            
            end_idx = start_idx + len(target_text)
            
            # Verify exact casing match in original text if needed, 
            # or extract the actual text from the original string to ensure 1:1 mapping
            matched_text = text[start_idx:end_idx]
            
            # Basic overlap check
            is_overlap = False
            for existing in spans:
                if (start_idx < existing['end'] and end_idx > existing['start']):
                    is_overlap = True
                    break
            
            if not is_overlap:
                spans.append({
                    "label": label,
                    "text": matched_text,
                    "start": start_idx,
                    "end": end_idx
                })
            
            search_start = end_idx
            
    # Sort by start index
    spans.sort(key=lambda x: x['start'])
    return spans

def main():
    # 1. Generate Spans
    extracted_spans = get_spans(RAW_TEXT, ENTITY_TARGETS)
    
    # 2. Update ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_spans
    }
    
    ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    with open(ner_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_record) + "\n")
    
    # 3. Update notes.jsonl
    notes_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    notes_file = OUTPUT_DIR / "notes.jsonl"
    with open(notes_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(notes_record) + "\n")
        
    # 4. Update spans.jsonl
    spans_file = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file, "a", encoding="utf-8") as f:
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
    stats_file = OUTPUT_DIR / "stats.json"
    
    # Load existing stats or initialize if missing (fallback)
    if stats_file.exists():
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0,
            "total_notes": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }

    # Increment totals
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    # Update label counts
    for span in extracted_spans:
        lbl = span['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validation & Logging
    with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as log:
        for span in extracted_spans:
            # Slicing the raw text to verify exact content
            snippet = RAW_TEXT[span['start']:span['end']]
            if snippet != span['text']:
                log.write(f"WARNING: Mismatch in {NOTE_ID}. Label: {span['label']}. "
                          f"Indices: {span['start']}-{span['end']}. "
                          f"Expected: '{span['text']}', Found: '{snippet}'\n")

    print(f"Successfully processed {NOTE_ID}.")
    print(f"Extracted {len(extracted_spans)} entities.")
    print(f"Files updated in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()