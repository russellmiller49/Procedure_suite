import json
import os
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_241"
CURRENT_TIME = datetime.datetime.now().isoformat()

# Full raw text from the input note
RAW_TEXT = """NOTE_ID:  note_241 SOURCE_FILE: note_241.txt PREOPERATIVE DIAGNOSIS: Tracheal stenosis
POSTOPERATIVE DIAGNOSIS: Complex Tracheal stenosis s/p stent placement 
PROCEDURE PERFORMED: Tracheal self-expandable airway stent placement
INDICATIONS: Symptomatic tracheal stenosis
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite.
After administration of sedatives an LMA was inserted and the flexible bronchoscope was passed through the vocal cords and into the trachea.
Approximately 2.5 cm distal to the vocal cords was a long segment of A-shaped stenosis measuring 3.5 cm with maximal airway obstruction of 90%.
Distal to the stenosis the mid and distal trachea appeared normal.
All right and left sided airways to at least the first sub-segments were examined and normal without endobronchial disease or airway distortion.
External markers were placed on the patient’s chest with fluoroscopic observation at the proximal and distal edges of the stenosis.
At this point we inserted a JAG guidewire into the trachea through the flexible bronchoscope.
The bronchoscope was then removed with the jagwire left in place.
A 16x40 mm Ultraflex uncovered self-expandable metallic stent was then inserted over the guidewire and using the external markers positioned in proper place and then deployed.
The flexible bronchoscope was re-inserted. The stent was well positioned and partially compressed externally.
A 14/16.5/18 mm Elation dilatational balloon was used to dilate the stent after which the airway was approximately 90% of normal caliber.
At this point inspection was performed to evaluate for any bleeding or other complications and none was seen.
The bronchoscope was removed and the procedure was completed. 

Recommendations:
- Transfer to PACU
- Discharge once criteria met.
- Plan for repeat evaluation and possible stent replacement in approximately 2 weeks."""

# Entities to extract (in order of appearance to facilitate dynamic indexing)
# Tuples: (Label, Surface Text)
ENTITIES_TO_EXTRACT = [
    ("ANAT_AIRWAY", "Tracheal"),                    # PREOPERATIVE DIAGNOSIS
    ("OBS_LESION", "stenosis"),
    ("ANAT_AIRWAY", "Tracheal"),                    # POSTOPERATIVE DIAGNOSIS
    ("OBS_LESION", "stenosis"),
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "Tracheal"),                    # PROCEDURE PERFORMED
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "tracheal"),                    # INDICATIONS
    ("OBS_LESION", "stenosis"),
    ("DEV_INSTRUMENT", "LMA"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "trachea"),
    ("MEAS_SIZE", "2.5 cm"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("OBS_LESION", "stenosis"),
    ("MEAS_SIZE", "3.5 cm"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "obstruction of 90%"),
    ("OBS_LESION", "stenosis"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "airways"),
    ("DEV_INSTRUMENT", "JAG guidewire"),
    ("ANAT_AIRWAY", "trachea"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("DEV_INSTRUMENT", "jagwire"),
    ("DEV_STENT_SIZE", "16x40 mm"),
    ("DEV_STENT_MATERIAL", "Ultraflex"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_STENT", "stent"),
    ("MEAS_SIZE", "14/16.5/18 mm"),
    ("DEV_INSTRUMENT", "dilatational balloon"),
    ("PROC_ACTION", "dilate"),
    ("DEV_STENT", "stent"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "90% of normal caliber"),
    ("PROC_ACTION", "inspection"),
    ("OUTCOME_COMPLICATION", "none was seen"),
    ("DEV_INSTRUMENT", "bronchoscope"),
    ("DEV_STENT", "stent"),                         # Recommendations
]

# =============================================================================
# PATH SETUP
# =============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
BASE_DIR = Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner"
BASE_DIR.mkdir(parents=True, exist_ok=True)

FILE_NER_DATASET = BASE_DIR / "ner_dataset_all.jsonl"
FILE_NOTES = BASE_DIR / "notes.jsonl"
FILE_SPANS = BASE_DIR / "spans.jsonl"
FILE_STATS = BASE_DIR / "stats.json"
FILE_LOG = BASE_DIR / "alignment_warnings.log"

# =============================================================================
# PROCESSING LOGIC
# =============================================================================

def calculate_offsets(text, entity_list):
    """
    Dynamically finds start/end indices for entities to ensure alignment.
    Handles duplicate words by searching sequentially from the last found position.
    """
    spans = []
    search_head = 0
    
    for label, surface_form in entity_list:
        # Find the next occurrence of the surface form starting from search_head
        start_idx = text.find(surface_form, search_head)
        
        if start_idx == -1:
            print(f"CRITICAL ERROR: Could not find '{surface_form}' after index {search_head}")
            continue
            
        end_idx = start_idx + len(surface_form)
        
        # Verify alignment
        extracted = text[start_idx:end_idx]
        if extracted != surface_form:
            print(f"MISMATCH: Expected '{surface_form}', got '{extracted}'")
            continue
            
        span = {
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": extracted,
            "start": start_idx,
            "end": end_idx
        }
        spans.append(span)
        
        # Update search head to ensure we find the *next* occurrence next time
        # We move just past this entity to handle immediate adjacencies if necessary
        search_head = start_idx + 1

    return spans

def update_stats(new_spans):
    """Updates the stats.json file with new counts."""
    if not FILE_STATS.exists():
        print(f"Stats file not found at {FILE_STATS}")
        return

    with open(FILE_STATS, 'r') as f:
        stats = json.load(f)

    # Update Global Counts
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["successful_files"] += 1
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    # Update Label Counts
    for span in new_spans:
        lbl = span["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1

    with open(FILE_STATS, 'w') as f:
        json.dump(stats, f, indent=2)
    print("Stats updated successfully.")

def main():
    # 1. Calculate Spans
    spans = calculate_offsets(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Prepare Data Entries
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": spans
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # 3. Write to ner_dataset_all.jsonl
    with open(FILE_NER_DATASET, 'a') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 4. Write to notes.jsonl
    with open(FILE_NOTES, 'a') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 5. Write to spans.jsonl
    with open(FILE_SPANS, 'a') as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")

    # 6. Update Stats
    update_stats(spans)

    # 7. Validation Log
    with open(FILE_LOG, 'a') as log:
        for span in spans:
            check_text = RAW_TEXT[span['start']:span['end']]
            if check_text != span['text']:
                log.write(f"[{datetime.datetime.now()}] ALIGNMENT ERROR {NOTE_ID}: "
                          f"Expected '{span['text']}', found '{check_text}' at {span['start']}\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(spans)} entities.")

if __name__ == "__main__":
    main()