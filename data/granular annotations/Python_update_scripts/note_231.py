import json
import re
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_230"

# Exact text from the procedure note (cleaned of source tags)
RAW_TEXT = """Procedure Name: EBUS Staging Bronchoscopy.
Indications: diagnosis and staging of suspected lung cancer
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record.
Laboratory studies and radiographs 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal.
No evidence of endobronchial disease was seen to at least the first sub-segments.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 4R and 10R lymph nodes.
Sampling by transbronchial needle aspiration was performed beginning with the 4R Lymph node, using an Olympus Visioshot2 EBUSTBNA 22 gauge needle.
ROSE was consistent with malignancy. After obtaining adequate tissue for diagnosis and molecular markers the EBUS bronchoscope was removed and the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: None
Estimated Blood Loss: 5 cc.

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-procedural monitoring unit.
- Will await final pathology results"""

# Entity Definitions based on Label_guide_UPDATED.csv
# Order matters: Longer phrases are prioritized to prevent partial overlaps (Greedy Match)
ENTITIES_TO_EXTRACT = [
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("PROC_METHOD", "endobronchial ultrasound"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("PROC_ACTION", "flexible bronchoscopy"),
    ("MEDICATION", "General Anesthesia"),
    ("MEDICATION", "topical anesthesia"),
    ("ANAT_LN_STATION", "station 4R"),
    ("OBS_LESION", "lung cancer"),
    ("DEV_NEEDLE", "22 gauge"),
    ("OBS_ROSE", "malignancy"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("PROC_ACTION", "biopsies"),
    ("PROC_METHOD", "EBUS"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "10R"),
    ("ANAT_LN_STATION", "4R"),
    ("OUTCOME_COMPLICATION", "None") # Matches "Complications: None"
]

# ==============================================================================
# PATH SETUP
# ==============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILE_NER_DATASET = OUTPUT_DIR / "ner_dataset_all.jsonl"
FILE_NOTES = OUTPUT_DIR / "notes.jsonl"
FILE_SPANS = OUTPUT_DIR / "spans.jsonl"
FILE_STATS = OUTPUT_DIR / "stats.json"
FILE_LOG = OUTPUT_DIR / "alignment_warnings.log"

# ==============================================================================
# EXTRACTION LOGIC
# ==============================================================================
def extract_spans(text, entity_list):
    """
    Finds entities in text using a greedy strategy (longest match first).
    Returns a list of dicts with start, end, label, text.
    """
    spans = []
    # Create a boolean mask to track occupied characters
    mask = [False] * len(text)
    
    # Sort entities by length (descending) to prioritize specific phrases over substrings
    # e.g. Match "station 4R" before "4R"
    sorted_entities = sorted(entity_list, key=lambda x: len(x[1]), reverse=True)

    for label, phrase in sorted_entities:
        # Use regex escape to handle special chars like '.' or '()'
        pattern = re.escape(phrase)
        for match in re.finditer(pattern, text):
            start, end = match.start(), match.end()
            
            # Check if this span overlaps with an existing one
            if not any(mask[start:end]):
                # Mark text as occupied
                for i in range(start, end):
                    mask[i] = True
                
                spans.append({
                    "start": start,
                    "end": end,
                    "label": label,
                    "text": phrase,
                    "span_id": f"{label}_{start}"
                })
    
    # Sort spans by appearance in text
    return sorted(spans, key=lambda x: x['start'])

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Extract Spans
    extracted_spans = extract_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in extracted_spans]
    }
    
    with open(FILE_NER_DATASET, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(FILE_NOTES, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(FILE_SPANS, "a", encoding="utf-8") as f:
        for span in extracted_spans:
            span_entry = {
                "span_id": span["span_id"],
                "note_id": NOTE_ID,
                "label": span["label"],
                "text": span["text"],
                "start": span["start"],
                "end": span["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    if FILE_STATS.exists():
        with open(FILE_STATS, "r", encoding="utf-8") as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans)
    
    for span in extracted_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(FILE_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    with open(FILE_LOG, "a", encoding="utf-8") as f:
        for span in extracted_spans:
            text_slice = RAW_TEXT[span["start"]:span["end"]]
            if text_slice != span["text"]:
                log_msg = f"[{datetime.datetime.now()}] MISMATCH {NOTE_ID}: Span {span['span_id']} expected '{span['text']}' but got '{text_slice}'\n"
                f.write(log_msg)
                print(f"WARNING: {log_msg.strip()}")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_spans)} entities.")
    print(f"Output saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()