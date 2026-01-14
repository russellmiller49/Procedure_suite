from pathlib import Path
import json
import os
import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_135"
RAW_TEXT = """Procedure: Bronchoscopy (rigid + flexible)
Indication: Collapsed left lung due to left mainstem airway stent occlusion (stent placed on [REDACTED]).
Anesthesia/Ventilation: General anesthesia with jet ventilation. Topical 2% lidocaine to tracheobronchial tree (2 mL).
Pre-procedure status: ASA III, ECOG 3. Standard consent/time-out performed. Labs/imaging reviewed.
Protocol: Enrolled in protocol 2010-0990 (normal saline vs 4.2% bicarbonate solution for mucus obstruction clearance in airway stent lumen).
Technique

Q180 slim video bronchoscope introduced orally to trachea.

T180 therapeutic video bronchoscope introduced through rigid bronchoscope and advanced through the tracheobronchial tree.
Findings

Larynx: Normal.

Trachea/Carina: No significant pathology.

Right lung: No significant pathology.
Left lung:

Left mainstem bronchus: 14 mm x 4 cm Microvasive stent present.
Stent lumen completely obstructed by blood clot and clear retained secretions.
After instillation of 10 cc of “agent A” (per study protocol), clot successfully removed with no significant bleeding and no residual stent lumen obstruction (stent lumen patent).
Left lower lobe: Malignant airway disease with:

>90% near-complete obstruction of segmental bronchi from malignant extrinsic compression and submucosal infiltration.
An additional completely obstructing lesion in the LLL due to malignant disease.
Stent position: Stent covers the left upper lobe takeoff.

Impression

Complete occlusion of left mainstem stent (blood clot + secretions) causing collapsed left lung → successfully cleared, stent patent post-intervention.
Severe malignant obstruction of the left lower lobe (near-complete and complete obstructions), consistent with advanced malignant airway involvement.
No right-sided, tracheal, or carinal pathology identified.

No specimens obtained.

Complications / Blood Loss

No immediate complications.

Estimated blood loss: None."""

# Defined entities based on Label_guide_UPDATED.csv
# Format: (label, text_snippet)
# Note: The script will locate the exact offsets.
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "Bronchoscopy (rigid + flexible)"),
    ("OBS_LESION", "Collapsed left lung"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("OBS_LESION", "occlusion"),
    ("PROC_METHOD", "General anesthesia"),
    ("PROC_METHOD", "jet ventilation"),
    ("MEDICATION", "lidocaine"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("MEAS_VOL", "2 mL"),
    ("DEV_INSTRUMENT", "Q180 slim video bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("DEV_INSTRUMENT", "T180 therapeutic video bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # Second occurrence
    ("ANAT_AIRWAY", "Larynx"),
    ("ANAT_AIRWAY", "Trachea"),
    ("ANAT_AIRWAY", "Carina"),
    ("ANAT_LUNG_LOC", "Right lung"),
    ("ANAT_LUNG_LOC", "Left lung"),
    ("ANAT_AIRWAY", "Left mainstem bronchus"),
    ("DEV_STENT_SIZE", "14 mm x 4 cm"),
    ("DEV_STENT", "Microvasive stent"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely obstructed"),
    ("OBS_LESION", "blood clot"),
    ("OBS_FINDING", "secretions"),
    ("PROC_ACTION", "instillation"),
    ("MEAS_VOL", "10 cc"),
    ("OBS_LESION", "clot"),
    ("PROC_ACTION", "removed"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "no residual stent lumen obstruction"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "stent lumen patent"),
    ("ANAT_LUNG_LOC", "Left lower lobe"),
    ("OBS_LESION", "Malignant airway disease"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", ">90% near-complete obstruction"),
    ("ANAT_AIRWAY", "segmental bronchi"),
    ("OBS_LESION", "malignant extrinsic compression"),
    ("OBS_LESION", "submucosal infiltration"),
    ("OBS_LESION", "completely obstructing lesion"),
    ("ANAT_LUNG_LOC", "LLL"),
    ("OBS_LESION", "malignant disease"),
    ("DEV_STENT", "Stent"),
    ("ANAT_AIRWAY", "left upper lobe takeoff"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "Complete occlusion"),
    ("ANAT_AIRWAY", "left mainstem"), # Impression section
    ("DEV_STENT", "stent"), # Impression section
    ("OBS_LESION", "blood clot"), # Impression
    ("OBS_FINDING", "secretions"), # Impression
    ("OBS_LESION", "Collapsed left lung"), # Impression
    ("OUTCOME_AIRWAY_LUMEN_POST", "successfully cleared"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "stent patent"),
    ("OBS_LESION", "Severe malignant obstruction"),
    ("ANAT_LUNG_LOC", "left lower lobe"), # Impression
    ("OUTCOME_AIRWAY_LUMEN_PRE", "near-complete and complete obstructions"),
    ("OBS_LESION", "malignant airway involvement"),
    ("ANAT_AIRWAY", "tracheal"),
    ("ANAT_AIRWAY", "carinal"),
    ("OUTCOME_COMPLICATION", "No immediate complications")
]

# =============================================================================
# PATH SETUP
# =============================================================================
# Assuming script is in data/granular annotations/Python_update_scripts/
# Target: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def find_offsets(text, snippet, start_search_idx=0):
    """Finds the start and end index of a snippet in the text."""
    start = text.find(snippet, start_search_idx)
    if start == -1:
        return None, None
    return start, start + len(snippet)

def load_json_file(filepath, default_value=None):
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_value if default_value is not None else {}

def save_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def append_jsonl(filepath, data):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + "\n")

# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Calculate Offsets
    spans = []
    search_cursor = 0
    # Sort entities by occurrence in text to handle duplicates correctly if manual list implies order
    # However, since we define ENTITIES_TO_EXTRACT manually, we assume they appear in order or we search carefully.
    # To be robust, we search from the last found position for duplicates, OR reset if not found (risk of wrong mapping).
    # Strategy: Maintain a cursor. If the snippet is found after cursor, use it and update cursor.
    
    entities_final = []
    
    # We will search sequentially. If a snippet appears earlier in text but listed later, we reset cursor? 
    # Better strategy for this script: The provided list is roughly chronological.
    
    cursor = 0
    for label, text in ENTITIES_TO_EXTRACT:
        start, end = find_offsets(RAW_TEXT, text, cursor)
        
        # Fallback: if not found after cursor, search from beginning (maybe list wasn't perfectly ordered)
        if start is None:
            start, end = find_offsets(RAW_TEXT, text, 0)
        
        if start is not None:
            spans.append({
                "label": label,
                "start": start,
                "end": end,
                "text": text
            })
            entities_final.append({
                "label": label,
                "start_char": start,
                "end_char": end,
                "text": text # helpful for debug, strictly schema asks for start/end/label in dataset
            })
            # Move cursor to end of this entity to avoid finding the same instance for next identical term
            cursor = start + 1 
        else:
            print(f"WARNING: Could not find entity '{text}' in text.")
            with open(LOG_FILE, 'a') as log:
                log.write(f"{datetime.datetime.now()} - {NOTE_ID} - Entity not found: {text}\n")

    # 2. Update ner_dataset_all.jsonl
    # Schema: {"id": str, "text": str, "entities": [[start, end, label], ...]}
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start_char"], e["end_char"], e["label"]] for e in entities_final]
    }
    append_jsonl(NER_DATASET_FILE, ner_entry)
    print(f"Updated {NER_DATASET_FILE.name}")

    # 3. Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    append_jsonl(NOTES_FILE, note_entry)
    print(f"Updated {NOTES_FILE.name}")

    # 4. Update spans.jsonl
    # Schema: {"span_id": ..., "note_id": ..., "label": ..., "text": ..., "start": ..., "end": ...}
    for e in entities_final:
        span_entry = {
            "span_id": f"{e['label']}_{e['start_char']}",
            "note_id": NOTE_ID,
            "label": e['label'],
            "span_text": e['text'],
            "start_char": e['start_char'],
            "end_char": e['end_char'],
            "hydration_status": "hydrated_unique" # Default for this script
        }
        append_jsonl(SPANS_FILE, span_entry)
    print(f"Updated {SPANS_FILE.name}")

    # 5. Update stats.json
    if STATS_FILE.exists():
        stats = load_json_file(STATS_FILE)
        stats["total_notes"] += 1
        stats["total_files"] += 1
        stats["total_spans_raw"] += len(entities_final)
        stats["total_spans_valid"] += len(entities_final)
        
        # Update label counts
        for e in entities_final:
            lbl = e['label']
            stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
            
        save_json_file(STATS_FILE, stats)
        print(f"Updated {STATS_FILE.name}")
    else:
        print(f"WARNING: {STATS_FILE} not found. Skipping stats update.")

    # 6. Validate
    # Re-read the output to ensure integrity (simulation)
    # Check for negative length or out of bounds
    for e in entities_final:
        if RAW_TEXT[e['start_char']:e['end_char']] != e['text']:
            err_msg = f"MISMATCH: {e['text']} vs {RAW_TEXT[e['start_char']:e['end_char']]}"
            print(err_msg)
            with open(LOG_FILE, 'a') as log:
                log.write(f"{datetime.datetime.now()} - {NOTE_ID} - {err_msg}\n")

if __name__ == "__main__":
    main()