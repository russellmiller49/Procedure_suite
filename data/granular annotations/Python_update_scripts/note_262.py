from pathlib import Path
import json
import os
import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_262"

# Raw text content from the provided note
# (Reconstructed from the provided source blocks preserving context)
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Subglottic stenosis 
POSTOPERATIVE DIAGNOSIS:  Subglottic stenosis 
PROCEDURE PERFORMED: 
1.         Flexible bronchoscopy  with endoluminal tumor ablation(CPT 31641)
INDICATIONS: Tracheal Obstruction  
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives and paralytics the flexible bronchoscope was inserted through the LMA and into the pharynx.
We then advanced the bronchoscope into the subglottic space. Approximately 2.5 cm distal to the vocal cords There were 3 polypoid lesions at the same level blocking about 90% of the airway during exhalation which moved in a ball valve fashion with inhalation resulting in about 50% obstruction of the airway.
Additionally there were multiple small polypoid (> 50) lesions surrounding distal to the lesion originating from all parts of the airway (Anterior trachea, posterior trachea, lateral trachea) which terminated about 1cm proximal to the main carina.
The right sided and left sided airways to at least the first sub-segments were uninvolved with no evidence of endobronchial tumor or extrinsic obstruction.
The flexible bronchoscope and LMA were removed and a 10mm non-ventilating rigid tracheoscope was subsequently inserted into the proximal trachea just proximal to the tumor and connected to ventilator.
The T190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and the electrocautery snare was used to transect the large polypoid lesions beginning with the 3 proximal obstructive lesions and the lesions once free from the wall were easily removed from the airway with suction and collected for pathological assessment.
After these lesions were removed about 10 other lesions in the airway which were anatomically amenable to snare were removed in the same fashion.
We then used APC to paint and shave the remaining tumor area on the posterior and lateral trachea walls until we were satisfied that we had achieved adequate luminal recanalization.
At the end of the procedure the trachea was approximately 90% open in comparison to unaffected areas.
The rigid bronchoscope was then removed, and the procedure was completed. There were no complications.
Of note we considered airway stent placement as a barrier effect  as the lesions regrew very quickly (< 3 months) after the previous bronchoscopic debulking procedure however in our discussions with the patient prior to the procedure he expressed reluctance to have stent placed due to possible cough associated with the stent and the fact that he only restarted chemotherapy 2 weeks ago.
I suspect that these lesions will recur unless he has a profound response to systemic treatment and possible radiation and if I need to debulk again I will strongly advocate for placement of a covered tracheal stent.
Recommendations: 
•	Transfer patient back to ward room 
•	Await final pathology results  
•	Will need to speak with oncology regarding other treatment options which might include PDT or brachytherapy."""

# Entities to map. Each tuple: (Label, Substring to find)
# Note: Find logic will look for the first occurrence starting from the end of the previous match 
# to handle repeats, or we can specify manual distinct fragments if repeats occur out of order.
ENTITIES_TO_EXTRACT = [
    ("PROC_METHOD", "Flexible bronchoscopy"),
    ("PROC_ACTION", "endoluminal tumor ablation"),
    ("OBS_LESION", "Tracheal Obstruction"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"), # First mention
    ("DEV_INSTRUMENT", "LMA"),
    ("ANAT_AIRWAY", "pharynx"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("OBS_LESION", "3 polypoid lesions"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "90%"), # blocking about 90%
    ("OUTCOME_AIRWAY_LUMEN_PRE", "50% obstruction"),
    ("OBS_LESION", "small polypoid (> 50) lesions"),
    ("ANAT_AIRWAY", "Anterior trachea"),
    ("ANAT_AIRWAY", "posterior trachea"),
    ("ANAT_AIRWAY", "lateral trachea"),
    ("ANAT_AIRWAY", "main carina"),
    ("LATERALITY", "right sided"),
    ("LATERALITY", "left sided"),
    ("ANAT_AIRWAY", "airways"),
    ("OBS_LESION", "endobronchial tumor"),
    ("OBS_LESION", "extrinsic obstruction"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"), # Second mention
    ("DEV_INSTRUMENT", "LMA"), # Second mention
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "proximal trachea"),
    ("OBS_LESION", "tumor"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"), # Third mention (T190)
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_INSTRUMENT", "electrocautery snare"),
    ("PROC_ACTION", "transect"),
    ("OBS_LESION", "large polypoid lesions"),
    ("DEV_INSTRUMENT", "APC"),
    ("PROC_ACTION", "paint and shave"), # Descriptive action
    ("ANAT_AIRWAY", "posterior and lateral trachea walls"),
    ("ANAT_AIRWAY", "trachea"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "90% open"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"), # Removal
    ("OUTCOME_COMPLICATION", "no complications"),
    ("DEV_STENT", "airway stent"),
    ("DEV_STENT_MATERIAL", "covered"),
    ("DEV_STENT", "tracheal stent"),
    ("PROC_METHOD", "PDT"),
    ("PROC_ACTION", "brachytherapy")
]

# =============================================================================
# SETUP PATHS
# =============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ner_dataset_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
notes_path = OUTPUT_DIR / "notes.jsonl"
spans_path = OUTPUT_DIR / "spans.jsonl"
stats_path = OUTPUT_DIR / "stats.json"
log_path = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# PROCESSING
# =============================================================================

def update_training_data():
    spans_output = []
    
    # 1. Calculate Offsets
    current_search_index = 0
    extracted_entities = []
    
    # We loop through the list. To handle duplicate substrings appearing in order,
    # we advance the search index.
    
    # NOTE: Some entities might appear out of order in the ENTITIES_TO_EXTRACT list 
    # if I manually ordered them wrong relative to text, so I will scan the whole text 
    # for each, but checking for overlaps is good practice. 
    # For this script, I assume the list roughly follows text flow or key uniqueness.
    # To be robust, I will search from 0 for every entity but ensure I pick the one 
    # that makes sense contextually if needed. 
    # However, simple ordered search is safer for "flexible bronchoscope" repeats.
    
    last_found_index = 0
    
    for label, substr in ENTITIES_TO_EXTRACT:
        # Find substring starting from last_found_index to handle repeats
        start = RAW_TEXT.find(substr, last_found_index)
        
        # If not found (e.g. list order error), try from beginning as fallback
        if start == -1:
            start = RAW_TEXT.find(substr)
            
        if start == -1:
            print(f"WARNING: Could not find span '{substr}' for label {label}")
            continue
            
        end = start + len(substr)
        
        # Validate exact match
        extracted_text = RAW_TEXT[start:end]
        if extracted_text != substr:
             with open(log_path, "a") as log:
                log.write(f"MISMATCH: {NOTE_ID} | {label} | Expected '{substr}' vs Found '{extracted_text}'\n")
        
        # Store entity
        span_id = f"{label}_{start}"
        entity_obj = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        }
        spans_output.append(entity_obj)
        extracted_entities.append([start, end, label])
        
        # Advance index to avoid finding the same instance for the next identical string
        # (Only if we assume the list is ordered by occurrence for duplicates)
        # To match the logic of "flexible bronchoscope" appearing multiple times,
        # we update last_found_index.
        last_found_index = start + 1

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_entities
    }
    
    with open(ner_dataset_path, "a") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(notes_path, "a") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(spans_path, "a") as f:
        for span in spans_output:
            f.write(json.dumps(span) + "\n")

    # 5. Update stats.json
    if stats_path.exists():
        with open(stats_path, "r") as f:
            stats = json.load(f)
    else:
        # Fallback if file doesn't exist (though strictly it should based on prompt)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(spans_output)
    stats["total_spans_valid"] += len(spans_output)
    
    for span in spans_output:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {NOTE_ID}. Stats updated.")

if __name__ == "__main__":
    update_training_data()