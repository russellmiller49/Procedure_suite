from pathlib import Path
import json
import os
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_234"
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# RAW TEXT CONTENT
# ==========================================
raw_text = """PREOPERATIVE DIAGNOSIS:

1.       Tracheal stenosis

POSTOPERATIVE DIAGNOSIS:

1.       Tracheal stenosis

PROCEDURE PERFORMED:

1.       Rigid and flexible bronchoscopy with Tracheal stent revision

INDICATIONS:  Stent evaluation and pre-surgical stenosis measurements

Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent.

Sedation: General Anesthesia

DESCRIPTION OF PROCEDURE: The procedure was performed in OR 23. Following intravenous medications as per the record the ventilator was attached to the patients t-tube and an laryngeal mask airway was inserted.
Topical anesthesia was then applied to the upper airway and the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The supraglottic space was edematous.
Granulation tissue was seen at the level of the vocal cords causing complete obstruction and inability to visualize the proximal aspect of the t-tube.
The T190 bronchoscope was removed and the P190 ultrathin bronchoscope was inserted in a similar fashion.
By applying gentle tressure we were able to advance the bronchoscope through the granulation tissue and into the t-tube.
Thich dry secretions were visualized within the t-tube and were removed with a combination of suction, cryotherapy and flexible forceps.
To improve patency. Once past the T-tube Moderate amount of secretions were seen in the trachea and proximal bronchi bilaterally and were suctioned clear.
The distal tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions, and no secretions. The flexible bronchoscope was removed and inserted through the external limb of the t-tube and thick secretions were removed in a similar fashion using suction, cryotherapy and forceps.
The bronchoscope was then reinserted through the LMA. The neck was cleaned with chlorhexidine and a guidewire was inserted into the t-tube.
Using gentle tugging the t-tube was removed leaving the guidewire in-place.
At this point a blue rhino dilator and guide sheath was inserted over the wire using a Seldinger technique to dilate the stoma.
The dilator was removed and a 6.0 uncuffed Shiley tracheostomy was inserted with the blue rhino introducer into the airway.
The guidewire, introducer sheath and introducer catheter were then removed leaving the tracheostomy tube in place.
The bronchoscope was then inserted into the tracheostomy tube to confirm position.
At this point the therapeutic bronchoscope was introduced through the LMA and using APC we attempted to debulk the subglottic granulation tissue.
We were not able to easy remove enough tissue to visualize the tracheostomy tube and the decision was made to not undergo further attempts at this time.
The bronchoscope was removed, and the procedure competed. 

. Approximately 4 cm below the vocal cords the previously placed silicone tube stent was visualized.
There was mild granulation tissue at the proximal end which was non-obstructive.
The stent was widely patent and clear of debris. .
At this point the flexible bronchoscope and LMA were removed and a 14mm non-ventilating rigid tracheoscope was subsequently inserted into the upper trachea.
Dual action rigid forceps were used to grasp the proximal end of the stent and were rotated repeatedly while withdrawing the stent into the rigid tracheoscope.
The stent could not be easily withdrawn through the lumen of the scope and the rigid bronchoscope was removed en-bloc with the stent which was then removed from the lumen.
An LMA was re-inserted and the flexible bronchoscope inserted into the subglottic space.
The exposed mucosa in the area of the previous stent was evaluated.
The mucosa was irritated and friable for the extent of the stent.
The A-shaped stenosis was noted causing approximately 30% obstruction and was measured at 1.5cm in length, The distance from the vocal cords to the proximal edge of the stenosis was 4.5 cm and the distance from the cricoid cartilage to the proximal edge of the stenosis was 3 cm.
At this point the flexible bronchoscope and LMA were removed and a 14mm non-ventilating rigid tracheoscope was subsequently re-inserted into the upper trachea.
The excised 15x50mm silicone stent was cleaned and loaded into the Efer-dumon stent loading system and deployed through the rigid bronchoscope into the previous location without difficulty.
The stent was well seated with the proximal limb approximately XXX cm distal to the vocal cords and the airway was 100% patent.
The bronchoscope was subsequently removed, and the procedure completed.

Recommendations:

- Transfer PACU

- D/C home when criteria met

- Will discuss surgical planning with otolaryngology."""

# ==========================================
# ENTITIES LIST
# ==========================================
# List of (Text, Label) to search and map
entities_to_find = [
    # Header/Diagnosis
    ("Tracheal", "ANAT_AIRWAY"),
    ("stenosis", "OBS_LESION"),
    ("Tracheal", "ANAT_AIRWAY"),
    ("stenosis", "OBS_LESION"),
    
    # Procedure
    ("Tracheal", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    
    # Body
    ("t-tube", "DEV_STENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("Topical anesthesia", "MEDICATION"),
    ("upper airway", "ANAT_AIRWAY"),
    ("T190 video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("supraglottic space", "ANAT_AIRWAY"),
    ("edematous", "OBS_FINDING"),
    ("Granulation tissue", "OBS_LESION"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("complete obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("t-tube", "DEV_STENT"),
    ("T190 bronchoscope", "DEV_INSTRUMENT"),
    ("P190 ultrathin bronchoscope", "DEV_INSTRUMENT"),
    ("granulation tissue", "OBS_LESION"),
    ("t-tube", "DEV_STENT"),
    ("Thich dry secretions", "OBS_FINDING"),
    ("t-tube", "DEV_STENT"),
    ("suction", "PROC_ACTION"),
    ("cryotherapy", "PROC_ACTION"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("T-tube", "DEV_STENT"),
    ("secretions", "OBS_FINDING"),
    ("trachea", "ANAT_AIRWAY"),
    ("proximal bronchi", "ANAT_AIRWAY"),
    ("bilaterally", "LATERALITY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Bronchial mucosa", "ANAT_AIRWAY"),
    ("endobronchial lesions", "OBS_LESION"),
    ("secretions", "OBS_FINDING"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("t-tube", "DEV_STENT"),
    ("thick secretions", "OBS_FINDING"),
    ("suction", "PROC_ACTION"),
    ("cryotherapy", "PROC_ACTION"),
    ("forceps", "DEV_INSTRUMENT"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("chlorhexidine", "MEDICATION"),
    ("guidewire", "DEV_INSTRUMENT"),
    ("t-tube", "DEV_STENT"),
    ("t-tube", "DEV_STENT"),
    ("guidewire", "DEV_INSTRUMENT"),
    ("blue rhino dilator", "DEV_INSTRUMENT"),
    ("guide sheath", "DEV_INSTRUMENT"),
    ("Seldinger technique", "PROC_METHOD"),
    ("dilate", "PROC_ACTION"),
    ("stoma", "ANAT_AIRWAY"),
    ("dilator", "DEV_INSTRUMENT"),
    ("6.0 uncuffed Shiley tracheostomy", "DEV_STENT"),
    ("blue rhino introducer", "DEV_INSTRUMENT"),
    ("airway", "ANAT_AIRWAY"),
    ("guidewire", "DEV_INSTRUMENT"),
    ("introducer sheath", "DEV_INSTRUMENT"),
    ("introducer catheter", "DEV_CATHETER"),
    ("tracheostomy tube", "DEV_STENT"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("tracheostomy tube", "DEV_STENT"),
    ("therapeutic bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("APC", "PROC_METHOD"),
    ("debulk", "PROC_ACTION"),
    ("subglottic", "ANAT_AIRWAY"),
    ("granulation tissue", "OBS_LESION"),
    ("tracheostomy tube", "DEV_STENT"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("4 cm", "MEAS_SIZE"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("silicone", "DEV_STENT_MATERIAL"),
    ("tube stent", "DEV_STENT"),
    ("mild granulation tissue", "OBS_LESION"),
    ("stent", "DEV_STENT"),
    ("widely patent", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("14mm", "MEAS_SIZE"),
    ("non-ventilating rigid tracheoscope", "DEV_INSTRUMENT"),
    ("upper trachea", "ANAT_AIRWAY"),
    ("rigid forceps", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("rigid tracheoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("A-shaped stenosis", "OBS_LESION"),
    ("30% obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("1.5cm", "MEAS_SIZE"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("stenosis", "OBS_LESION"),
    ("4.5 cm", "MEAS_SIZE"),
    ("cricoid cartilage", "ANAT_AIRWAY"),
    ("stenosis", "OBS_LESION"),
    ("3 cm", "MEAS_SIZE"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("14mm", "MEAS_SIZE"),
    ("non-ventilating rigid tracheoscope", "DEV_INSTRUMENT"),
    ("upper trachea", "ANAT_AIRWAY"),
    ("15x50mm", "DEV_STENT_SIZE"),
    ("silicone", "DEV_STENT_MATERIAL"),
    ("stent", "DEV_STENT"),
    ("Efer-dumon stent loading system", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("airway", "ANAT_AIRWAY"),
    ("100% patent", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("bronchoscope", "DEV_INSTRUMENT")
]

# ==========================================
# PROCESSING LOGIC
# ==========================================

def get_entities_with_indices(text, entity_list):
    """
    Finds exact start/end indices for entities in the text.
    Handles multiple occurrences by keeping a cursor.
    """
    entities = []
    cursor = 0
    # Sort distinct occurrences by order in text to avoid backtracking issues if list isn't ordered
    # But strictly, we must find them in order or handle overlapping searches.
    # Simple approach: Search from last cursor for each entity found.
    # To handle the list provided (which implies order), we iterate.
    
    # Note: The manual list above is roughly in order. 
    # To ensure accuracy, we will search for the next occurrence of the string after the previous cursor.
    
    for term, label in entity_list:
        start = text.find(term, cursor)
        if start == -1:
            # Fallback: restart search from 0 if out of order (rare case in this strict manual flow)
            # or log warning. For this script, we assume approximate linear order or independent search.
            # Use independent search for safety if logical flow breaks, but strictly
            # we want to map specific instances.
            # Let's try searching from 0 if not found, to catch missed ones, 
            # BUT we must ensure we don't pick the same one twice if intended distinct.
            # Given the detailed list, we assume linear progression.
            # If not found, skip to avoid bad data.
            print(f"Warning: Entity '{term}' not found after index {cursor}.")
            continue
        
        end = start + len(term)
        entities.append({
            "start": start,
            "end": end,
            "label": label,
            "text": term
        })
        cursor = end # Move cursor forward to avoid re-matching the same span immediately
        
    return entities

# Extract entities
extracted_entities = get_entities_with_indices(raw_text, entities_to_find)

# ==========================================
# FILE UPDATE FUNCTIONS
# ==========================================

def update_ner_dataset(file_path, note_id, text, entities):
    data = {"id": note_id, "text": text, "entities": []}
    for ent in entities:
        data["entities"].append({
            "start_offset": ent["start"],
            "end_offset": ent["end"],
            "label": ent["label"]
        })
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

def update_notes_file(file_path, note_id, text):
    data = {"id": note_id, "text": text}
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

def update_spans_file(file_path, note_id, entities):
    with open(file_path, "a", encoding="utf-8") as f:
        for ent in entities:
            span_id = f"{ent['label']}_{ent['start']}"
            data = {
                "span_id": span_id,
                "note_id": note_id,
                "label": ent["label"],
                "text": ent["text"],
                "start": ent["start"],
                "end": ent["end"]
            }
            f.write(json.dumps(data) + "\n")

def update_stats_file(file_path, entities):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file context here
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities) # All considered valid in this script
    
    for ent in entities:
        label = ent["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def validate_alignment(text, entities, log_path):
    with open(log_path, "a", encoding="utf-8") as log:
        for ent in entities:
            snippet = text[ent["start"]:ent["end"]]
            if snippet != ent["text"]:
                error_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{ent['text']}' but found '{snippet}' at {ent['start']}:{ent['end']}\n"
                log.write(error_msg)

# ==========================================
# EXECUTION
# ==========================================

if __name__ == "__main__":
    # 1. Update NER Dataset
    update_ner_dataset(NER_DATASET_PATH, NOTE_ID, raw_text, extracted_entities)
    
    # 2. Update Notes
    update_notes_file(NOTES_PATH, NOTE_ID, raw_text)
    
    # 3. Update Spans
    update_spans_file(SPANS_PATH, NOTE_ID, extracted_entities)
    
    # 4. Update Stats
    update_stats_file(STATS_PATH, extracted_entities)
    
    # 5. Validate
    validate_alignment(raw_text, extracted_entities, LOG_PATH)
    
    print(f"Successfully processed {NOTE_ID} with {len(extracted_entities)} entities.")