import json
import os
import datetime
import re
from pathlib import Path

# =============================================================================
# 1. CONFIGURATION & DATA DEFINITION
# =============================================================================

NOTE_ID = "note_214"

# Raw text exactly as provided in the source file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Airway Stenosis with possible tumor recurrence.
POSTOPERATIVE DIAGNOSIS: Airway Stenosis likely without tumor recurrence. 
PROCEDURE PERFORMED: CPT 31630 Rigid bronchoscopy with Balloon dilatation, CPT 31652 Single station EBUS with TBNA, 
INDICATIONS: Airway Stenosis with possible tumor recurrence
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives an LMA was inserted and the flexible bronchoscope was passed through the vocal cords and into the trachea.
The trachea was of normal caliber. The carina was sharp.
The right sided tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal.
No evidence of endobronchial disease was seen to at least the first sub-segments.
The proximal left mainstem was normal The left upper lobe was essentially completely closed due to what appeared to be scan and granulation tissue while the left lower lobe was approximately 80% obstructed due to mostly anatomical distortion as well as some degree related to granulation tissue.
We could not bypass the obstruction with the diagnostic bronchoscope.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The EBUS bronchoscope was first used to inspect the level of the 10L lymph node due to radiographic suspicion for disease.
No evidence of adenopathy was seen. We then evaluated the sation 7 lymph node due to radiographic concerns.
Sampling by transbronchial needle aspiration was performed with the Olympus EBUSTBNA 22 gauge needle for a total of 4 passes.
ROSE did not show evidence suspicious for malignancy. The EBUS bronchoscope was removed and an 11 mm ventilating rigid bronchoscope was inserted into the mid trachea and attached to the ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope.
We then inserted therapeutic T190 flexible bronchoscope into the airway and advanced to the left upper lobe orifice.
We attempted to gently dilate the orifice using a 6-7-8 CRE balloon in sequential fashion but were unable to clearly define branching segments and aborted we then dilated the orifice of the left lower lobe starting with a 6-7-8 CRE balloon in sequential fashion before converting to an 8.9.10 balloon also dilating with a similar technique.
The orifice post dilatation was approximately 70% open. We then were able to advance the therapeutic bronchoscope into the left lower lobe.
Segmental stricturing was seen in the superior segment and the medial basal segment if the left lower lobe.
Gentile dilatation was performed within the segments resulting in significant improvement in diameter.
Once this was completed, we inspected the airway for evidence of bleeding and none was seen.
The rigid bronchoscope was removed and an LMA was inserted while awaiting emergence and the procedure was completed.
Complications: None
Recommendations: 
- Transfer to PACU then home once criteria are met.
- Wil follow-up in pulm clinic for re-evaluation and repeat CT in 1 week."""

# Define target entities to extract. 
# Format: (Label, Exact Text Substring)
# Note: The script logic below automatically finds the correct indices.
TARGETS = [
    ("OBS_LESION", "Airway Stenosis"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "Balloon dilatation"),
    ("PROC_METHOD", "EBUS"),
    ("PROC_ACTION", "TBNA"),
    ("DEV_INSTRUMENT", "LMA"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "right sided tracheobronchial tree"),
    ("ANAT_AIRWAY", "proximal left mainstem"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("OBS_FINDING", "granulation tissue"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "approximately 80% obstructed"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_LN_STATION", "10L"),
    ("ANAT_LN_STATION", "sation 7"), # Capturing 'sation' per source text typo
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "22 gauge"),
    ("MEAS_COUNT", "4 passes"),
    ("MEAS_SIZE", "11 mm"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "T190 flexible bronchoscope"),
    ("DEV_INSTRUMENT", "6-7-8 CRE balloon"),
    ("DEV_INSTRUMENT", "8.9.10 balloon"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "approximately 70% open"),
    ("ANAT_LUNG_LOC", "superior segment"),
    ("ANAT_LUNG_LOC", "medial basal segment")
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG = OUTPUT_DIR / "alignment_warnings.log"


# =============================================================================
# 2. HELPER FUNCTIONS
# =============================================================================

def extract_entities(text, targets):
    """
    Finds targets in text and returns a list of dictionaries with valid start/end indices.
    Handles multiple occurrences by finding them sequentially.
    """
    entities = []
    # Track search position to handle duplicates roughly in order if needed, 
    # but for this logic we will find the *first* match of specific phrases 
    # or all matches if the definition implies generic usage.
    # To be safe and avoid duplicates in this specific list, we use a set of found spans.
    found_spans = set()

    for label, substr in targets:
        # We find the substring. If it appears multiple times, we need to be careful.
        # For this specific note, we will assume the first finding is the primary target
        # unless it is a generic term like 'trachea' used in anatomy description.
        
        # Simple strategy: Find all non-overlapping occurrences of the substring
        for match in re.finditer(re.escape(substr), text):
            start, end = match.span()
            span_sig = (start, end, label)
            
            # Avoid adding the exact same span twice
            if span_sig not in found_spans:
                entities.append({
                    "start": start,
                    "end": end,
                    "label": label,
                    "text": substr
                })
                found_spans.add(span_sig)
                
                # If we only want the first match for unique things (like Preop Diagnosis),
                # we could break here. However, capturing all instances is generally 
                # better for NER training unless it's a false positive context.
                # Given the specificity of the TARGETS list, we include matches.
    
    # Sort by start index
    entities.sort(key=lambda x: x["start"])
    return entities

def update_jsonl(filepath, new_record):
    """Appends a JSON record to a JSONL file."""
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def load_json(filepath):
    if not filepath.exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


# =============================================================================
# 3. MAIN EXECUTION
# =============================================================================

def main():
    print(f"Processing NOTE_ID: {NOTE_ID}...")

    # 1. Analyze & Extract
    entities = extract_entities(RAW_TEXT, TARGETS)
    
    # 2. Update ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    update_jsonl(OUTPUT_DIR / "ner_dataset_all.jsonl", ner_record)

    # 3. Update notes.jsonl
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    update_jsonl(OUTPUT_DIR / "notes.jsonl", note_record)

    # 4. Update spans.jsonl
    # We iterate and append individually
    spans_file = OUTPUT_DIR / "spans.jsonl"
    for ent in entities:
        # Unique span ID: Label_StartOffset
        span_id = f"{ent['label']}_{ent['start']}"
        span_record = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        update_jsonl(spans_file, span_record)

    # 5. Update stats.json
    stats_path = OUTPUT_DIR / "stats.json"
    
    # Initialize defaults if file missing
    if stats_path.exists():
        stats = load_json(stats_path)
    else:
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }

    # Update counts
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities) # Assuming all extracted are valid

    # Update label counts
    for ent in entities:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
    
    save_json(stats_path, stats)

    # 6. Validate & Log
    # Check alignment
    with open(ALIGNMENT_LOG, 'a', encoding='utf-8') as log:
        for ent in entities:
            extracted_text = RAW_TEXT[ent['start']:ent['end']]
            if extracted_text != ent['text']:
                timestamp = datetime.datetime.now().isoformat()
                log_msg = f"[{timestamp}] MISMATCH: Note {NOTE_ID}, Span {ent['start']}-{ent['end']}. Expected '{ent['text']}', found '{extracted_text}'\n"
                log.write(log_msg)
                print(f"WARNING: Alignment mismatch found. See {ALIGNMENT_LOG}")

    print(f"Successfully processed {NOTE_ID}. Data saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()