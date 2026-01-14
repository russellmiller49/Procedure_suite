import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_001"
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
STATS_PATH = Path("stats.json")  # Assuming stats.json is in the working directory or provide absolute path

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# RAW TEXT CONTENT
# ==========================================
RAW_TEXT = """NOTE_ID:  note_001 SOURCE_FILE: note_001.txt 
PREOPERATIVE DIAGNOSIS: broncho-esophageal(anastomosis) fistula s/p Ivor Lewis Esophagostomy 
POSTOPERATIVE DIAGNOSIS: broncho-esophageal(anastomosis) fistula s/p Ivor Lewis Esophagostomy  s/p occlusive left mainstem stent
PROCEDURE PERFORMED: Flexible, self-expandable airway stent placement
INDICATIONS: broncho-esophageal(anastomosis) fistula with persistent leak despite esophageal stent
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives a flexible bronchoscope was passed through the patients tracheostomy tube and into the airways.
The trachea was normal. Purulent secretions were seen throughout the airways.
Once secretions were suctioned inspection of the right sided airways should multiple small endobronchial nodular lesions concerning for airway metastasis.
On the left in the mid left mainstem a 1.5cm fistula was seen at the medial aspect of the posterior wall.
Distally (similar to what was seen on the right) were multiple small endobronchial lesions with an appearance suggestive of malignancy.
Multiple nodules from the left and right side were biopsied with flexible forceps and placed in formalin.
At this point we measured the length of the fistula and inserted a Jagwire through the flexible bronchoscope past the fistula within the left mainstem and using fluoroscopy marked the proximal and distal edges of the selected area required to cover the fistula with radiopaque markers (paper clips) taped to the patient’s chest wall.
The flexible bronchoscope was removed and an Aero 14x30 mm stent was advanced over the guidewire and positioned based on the external markers under fluoroscopic observation.
The stent was deployed slightly too proximally with the distal edge just covering the fistula.
We then decided to place a second 14x40 Aero stent into the previously place stent to better cover the obstruction.
This was done in a similar fashion. On inspection after placement the originally placed stent was noted to have been pushed distally by the second stent (more distal than desired and obstructing the orifice of the left upper and lower lobe. We then removed the 14x40 stent by grasping the proximal edge with forceps. The stent could not be retracted through the tracheostomy so the trach tube was removed and then the stent was pulled through the stoma, after which re re-inserted the trach over a bronchoscope and re-attached it to the ventilator. We then retraced the remaining 14x30 mm 
Aero fully covered self-expandable metallic stent into proper position (within the left mainstem covering the fistula) with forceps. Once this was done and we were satisfied with the final result the bronchoscope was removed and the procedure was completed. We then turned the patient over to anesthesia service to recover and transfer back to the ICU.
Post procedure diagnosis:
Recommendations:
- Transfer back to ICU
- Await tissue diagnosis from biopsied endobronchial nodules
- Obtain post procedure CXR
- TID saline nebulizers along with ensuring oxygen is humidified to avoid mucous impaction and obstruction of stent."""

# ==========================================
# ENTITY MAPPING
# ==========================================
# Format: (Label, Text_String, Occurrence_Index)
# Occurrence_Index: 0 for 1st match, 1 for 2nd match, etc.
entities_to_find = [
    ("OBS_LESION", "fistula", 0), # Preop
    ("LATERALITY", "left", 0), # Postop
    ("ANAT_AIRWAY", "mainstem", 0), # Postop
    ("DEV_STENT", "stent", 1), # Postop
    ("OBS_LESION", "fistula", 2), # Indications
    ("DEV_STENT", "stent", 2), # Indications
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("OBS_FINDING", "Purulent secretions", 0),
    ("ANAT_AIRWAY", "airways", 1),
    ("LATERALITY", "right", 0), # right sided
    ("ANAT_AIRWAY", "airways", 2),
    ("OBS_LESION", "endobronchial nodular lesions", 0),
    ("LATERALITY", "left", 1), # mid left
    ("ANAT_AIRWAY", "mainstem", 1), # mid left mainstem
    ("MEAS_SIZE", "1.5cm", 0),
    ("OBS_LESION", "fistula", 3),
    ("LATERALITY", "right", 1), # on the right
    ("OBS_LESION", "endobronchial lesions", 0),
    ("OBS_LESION", "nodules", 0),
    ("LATERALITY", "left", 2), # left and right side
    ("LATERALITY", "right", 2),
    ("PROC_ACTION", "biopsied", 0),
    ("DEV_INSTRUMENT", "flexible forceps", 0),
    ("OBS_LESION", "fistula", 4),
    ("DEV_INSTRUMENT", "Jagwire", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1),
    ("OBS_LESION", "fistula", 5),
    ("LATERALITY", "left", 3), # left mainstem
    ("ANAT_AIRWAY", "mainstem", 2),
    ("PROC_METHOD", "fluoroscopy", 0),
    ("OBS_LESION", "fistula", 6),
    ("ANAT_PLEURA", "chest wall", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 2),
    ("DEV_STENT_MATERIAL", "Aero", 0),
    ("DEV_STENT_SIZE", "14x30 mm", 0),
    ("DEV_STENT", "stent", 3),
    ("OBS_LESION", "fistula", 7),
    ("DEV_STENT_SIZE", "14x40", 0),
    ("DEV_STENT_MATERIAL", "Aero", 1),
    ("DEV_STENT", "stent", 4),
    ("DEV_STENT", "stent", 5),
    ("DEV_STENT", "stent", 6),
    ("DEV_STENT", "stent", 7),
    ("LATERALITY", "left", 4), # left upper
    ("ANAT_LUNG_LOC", "upper", 0),
    ("ANAT_LUNG_LOC", "lower lobe", 0),
    ("DEV_STENT_SIZE", "14x40", 1),
    ("DEV_STENT", "stent", 8),
    ("DEV_INSTRUMENT", "forceps", 1),
    ("DEV_STENT", "stent", 9),
    ("DEV_STENT", "stent", 10),
    ("DEV_INSTRUMENT", "bronchoscope", 3),
    ("DEV_STENT_SIZE", "14x30 mm", 1),
    ("DEV_STENT_MATERIAL", "Aero", 2),
    ("DEV_STENT_MATERIAL", "fully covered self-expandable metallic", 0),
    ("DEV_STENT", "stent", 11),
    ("LATERALITY", "left", 5), # left mainstem
    ("ANAT_AIRWAY", "mainstem", 3),
    ("OBS_LESION", "fistula", 8),
    ("DEV_INSTRUMENT", "forceps", 2),
    ("DEV_INSTRUMENT", "bronchoscope", 4),
    ("PROC_ACTION", "biopsied", 1),
    ("OBS_LESION", "nodules", 1),
    ("OBS_FINDING", "mucous impaction", 0),
    ("DEV_STENT", "stent", 12)
]

def map_entities(text, entity_list):
    mapped_entities = []
    
    # Track occurrence indices for text strings
    text_occurrences = {}
    
    for label, substr, target_occ_idx in entity_list:
        # Find all matches for this substring
        matches = [m for m in re.finditer(re.escape(substr), text)]
        
        if target_occ_idx < len(matches):
            match = matches[target_occ_idx]
            span = {
                "span_id": f"{label}_{match.start()}",
                "note_id": NOTE_ID,
                "label": label,
                "text": substr,
                "start": match.start(),
                "end": match.end()
            }
            mapped_entities.append(span)
        else:
            print(f"WARNING: Could not find occurrence {target_occ_idx} of '{substr}' for label {label}")
            
    return sorted(mapped_entities, key=lambda x: x['start'])

# ==========================================
# EXECUTION
# ==========================================
def main():
    # 1. Generate Entities
    final_entities = map_entities(RAW_TEXT, entities_to_find)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": final_entities
    }
    
    with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # 3. Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(OUTPUT_DIR / "notes.jsonl", "a") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(OUTPUT_DIR / "spans.jsonl", "a") as f:
        for span in final_entities:
            f.write(json.dumps(span) + "\n")

    # 5. Update stats.json
    try:
        # Check if stats file exists in the current directory, otherwise create a dummy structure
        if STATS_PATH.exists():
            with open(STATS_PATH, "r") as f:
                stats = json.load(f)
        else:
            stats = {
                "total_files": 0, "successful_files": 0, "total_notes": 0, 
                "total_spans_raw": 0, "total_spans_valid": 0, "alignment_warnings": 0, 
                "alignment_errors": 0, "label_counts": {}
            }

        stats["total_files"] += 1
        stats["successful_files"] += 1
        stats["total_notes"] += 1
        stats["total_spans_raw"] += len(final_entities)
        stats["total_spans_valid"] += len(final_entities)
        
        for span in final_entities:
            lbl = span["label"]
            stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
            
        with open(STATS_PATH, "w") as f:
            json.dump(stats, f, indent=2)
            
    except Exception as e:
        print(f"Error updating stats.json: {e}")

    # 6. Validate & Log
    log_path = OUTPUT_DIR / "alignment_warnings.log"
    with open(log_path, "a") as f:
        for span in final_entities:
            # Verify exact match
            extracted = RAW_TEXT[span["start"]:span["end"]]
            if extracted != span["text"]:
                log_msg = f"MISMATCH {NOTE_ID}: Label {span['label']} expected '{span['text']}' but found '{extracted}' at {span['start']}-{span['end']}\n"
                f.write(log_msg)
                print(log_msg.strip())

    print(f"Successfully processed {NOTE_ID} with {len(final_entities)} entities.")

if __name__ == "__main__":
    main()