import json
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_194"
TIMESTAMP = datetime.datetime.now().isoformat()

# Raw text content of the note (preserving exact formatting and typos from source)
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Malignant Central Airway Obstruction 

POSTOPERATIVE DIAGNOSIS: Malignant Central Airway Obstruction

PROCEDURE PERFORMED: 
CPT 31641 Bronchoscopy destruction of tumor or relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
CPT 31624 Bronchoscopy with bronchial alveolar lavage
INDICATIONS: Airway stent occlusion 

Sedation: General Anesthesia

DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite.
After administration of sedatives an LMA was inserted and the therapeutic flexible bronchoscope was passed through the vocal cords and into the trachea.
The patients known Silicone Y-stent was well positioned. There was signifigant thich dry mucous with mild obstruction of the tracheal limb, moderate obstruction of the left bronchial limb and significant obstruction of the right bronchial limb and the telescoping right mainstem covered metallic stent.
The right upper lobe was partially obstructed by the distal tip of the SEM but there was no evidence of post-obstructive pneumonia and all right sided segmental airways were patent without endobronchial disease.
On the left the distal mainstem, lower lobe bronchi were patient without evidence of endobronchial disease.
At the anterior aspect of the left upper lobe takeoff there was partially obstructive endobronchial tumor causing approximately 40% reduction in caliber which did not warrant treatment at this time.
Through a combination of mechanical debulking with the bronchoscope tip, forceps debulking and use of sodium bicarbonate instillation the adhesive mucous was slowly removed, with near complete recanalization of the stents.
Subsequently a mini BAL was performed in the anterior segment of the left upper lobe with 40cc instillation and 30cc return.
At this point inspection was performed to evaluate for any bleeding or other complications and none was seen.
The bronchoscope was removed and the procedure was completed. 

Recommendations:
- Transfer to PACU
- Discharge once criteria met."""

# ==============================================================================
# ENTITY EXTRACTION
# ==============================================================================
# Manually mapped entities based on Label_guide_UPDATED.csv
# Format: (Text substring, Label)
# Note: Offsets will be calculated dynamically to ensure precision.

ENTITIES_TO_EXTRACT = [
    ("Malignant Central Airway Obstruction", "OBS_LESION"),  # Pre-op
    ("Malignant Central Airway Obstruction", "OBS_LESION"),  # Post-op
    ("Bronchoscopy", "PROC_ACTION"),                         # CPT 31641
    ("destruction of tumor", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),                                 # within destruction of tumor
    ("relief of stenosis", "PROC_ACTION"),
    ("stenosis", "OBS_LESION"),                              # within relief of stenosis
    ("laser therapy", "PROC_ACTION"),
    ("cryotherapy", "PROC_ACTION"),
    ("Bronchoscopy", "PROC_ACTION"),                         # CPT 31624
    ("bronchial alveolar lavage", "PROC_ACTION"),
    ("Airway stent occlusion", "OBS_LESION"),                # Indication
    ("sedatives", "MEDICATION"),
    ("LMA", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("Silicone Y-stent", "DEV_STENT"),
    ("signifigant thich dry mucous", "OBS_FINDING"),         # preserving typos
    ("mild obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("tracheal limb", "ANAT_AIRWAY"),
    ("moderate obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("left bronchial limb", "ANAT_AIRWAY"),
    ("significant obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("right bronchial limb", "ANAT_AIRWAY"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("covered metallic stent", "DEV_STENT"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("partially obstructed", "OBS_FINDING"),
    ("SEM", "DEV_STENT"),
    ("post-obstructive pneumonia", "OBS_LESION"),
    ("right sided", "LATERALITY"),
    ("segmental airways", "ANAT_AIRWAY"),
    ("endobronchial disease", "OBS_LESION"),
    ("left", "LATERALITY"),                                  # "On the left..."
    ("distal mainstem", "ANAT_AIRWAY"),
    ("lower lobe bronchi", "ANAT_LUNG_LOC"),                 # Segmental/Lobar airway -> Lung Loc per guide logic (RUL/RB1)
    ("endobronchial disease", "OBS_LESION"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("endobronchial tumor", "OBS_LESION"),
    ("40% reduction in caliber", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("mechanical debulking", "PROC_ACTION"),
    ("bronchoscope tip", "DEV_INSTRUMENT"),
    ("forceps debulking", "PROC_ACTION"),
    ("sodium bicarbonate", "MEDICATION"),
    ("instillation", "PROC_ACTION"),                         # Context: sodium bicarb instillation
    ("adhesive mucous", "OBS_FINDING"),
    ("near complete recanalization", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("stents", "DEV_STENT"),
    ("mini BAL", "PROC_ACTION"),
    ("anterior segment", "ANAT_LUNG_LOC"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("40cc", "MEAS_VOL"),
    ("30cc", "MEAS_VOL"),
    ("bleeding", "OBS_FINDING"),
    ("bronchoscope", "DEV_INSTRUMENT"),
]

# ==============================================================================
# DIRECTORY SETUP
# ==============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"
STATS_PATH = OUTPUT_DIR / "stats.json"
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def find_offsets(text, search_text, start_search_index=0):
    """Finds exact start/end indices of a substring starting search from a specific index."""
    start = text.find(search_text, start_search_index)
    if start == -1:
        return None, None
    return start, start + len(search_text)

def process_note():
    entities = []
    current_search_index = 0
    
    # Sort entities by their occurrence in text to handle duplicates strictly in order
    # (Note: This simple logic assumes the ENTITIES_TO_EXTRACT list is ordered by appearance.
    # If not, we would need a more complex sliding window. The list above is roughly ordered,
    # but to be safe, we will scan from the last found position or reset if needed, 
    # but strict sequential scanning is best for duplicates like 'Bronchoscopy'.)
    
    processed_spans = []
    
    # Tracking distinct occurrences
    # We iterate the list. For each item, we find the next occurrence in text
    # after the 'last_index' found to handle repeats correctly.
    
    last_index_map = {} # Key: text, Value: last end index

    for text_match, label in ENTITIES_TO_EXTRACT:
        # Determine where to start searching
        # If we have seen this exact text before, start after its last location
        # Otherwise start from 0 (or optimize to start from the min of known locations, but 0 is safer for mixed order)
        
        # However, to avoid overlapping incorrectly with previous distinct entities,
        # we generally search forward. But since our list might not be perfectly chronological
        # (though I tried to make it so), we search from 0 and check against used ranges.
        # BETTER STRATEGY for this script: Use a cursor that moves forward only if we assume the list is ordered.
        # Since the list IS ordered by reading the text, we will maintain a `cursor`.
        
        start, end = find_offsets(RAW_TEXT, text_match, current_search_index)
        
        # If not found after cursor, try from 0 (in case list order was slightly off),
        # but ensure we don't pick a span that overlaps an already used one.
        if start is None:
            start, end = find_offsets(RAW_TEXT, text_match, 0)
        
        # Logic to ensure we find the *correct* instance (the next available one)
        # We will loop find until we hit a span that isn't colliding.
        search_cursor = 0
        while True:
            start, end = find_offsets(RAW_TEXT, text_match, search_cursor)
            if start is None:
                break # Not found
            
            # Check collision with existing entities
            collision = False
            for e in entities:
                if (start < e['end'] and end > e['start']):
                    collision = True
                    break
            
            if not collision:
                # Found a valid free spot
                break
            else:
                # Try next occurrence
                search_cursor = start + 1
        
        if start is not None:
            entities.append({
                "start": start,
                "end": end,
                "label": label,
                "text": text_match
            })
            # Update global cursor to help next search (optional optimization)
            if end > current_search_index:
                current_search_index = start # Don't push end too far, or we miss nested items
        else:
            print(f"WARNING: Could not find exact match for '{text_match}'")

    # Sort entities by start time for JSONL
    entities.sort(key=lambda x: x['start'])

    # 1. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 2. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 3. Update spans.jsonl
    new_spans_count = 0
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for ent in entities:
            span_id = f"{ent['label']}_{ent['start']}"
            span_entry = {
                "span_id": span_id,
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_entry) + "\n")
            new_spans_count += 1

    # 4. Update stats.json
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
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += new_spans_count
    stats["total_spans_valid"] += new_spans_count # Assuming all are valid

    for ent in entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

    # 5. Validation & Logging
    with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as log:
        for ent in entities:
            extracted = RAW_TEXT[ent['start']:ent['end']]
            if extracted != ent['text']:
                log.write(f"[{datetime.datetime.now()}] MISMATCH {NOTE_ID}: "
                          f"Expected '{ent['text']}', found '{extracted}' at {ent['start']}-{ent['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Added {new_spans_count} entities.")

if __name__ == "__main__":
    process_note()