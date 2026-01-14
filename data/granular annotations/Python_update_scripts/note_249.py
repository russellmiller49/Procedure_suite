import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_249"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# We resolve parents to get to the root 'data' folder structure relative to this script
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Definition
# ==========================================
# The exact text content from note_249.txt
TEXT = """NOTE_ID:  note_249 SOURCE_FILE: note_249.txt PREOPERATIVE DIAGNOSIS: Tracheal-esophageal fistula secondary to esophageal CA 
POSTOPERATIVE DIAGNOSIS: Tracheal-esophageal fistula secondary to esophageal CA 
PROCEDURE PERFORMED: Rigid bronchoscopy, Tracheal self-expandable airway stent removal
INDICATIONS: Stent migration and presumed stent infection
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After administration of sedatives an LMA was inserted and the flexible bronchoscope was passed through the vocal cords and into the trachea.
Approximately 2 cm distal to the vocal cords the patients previous stent could be visualized.
Throughout the stent were thick purulent material consistent with infection.
The telescoped distal tracheal stent was noted to have migrated into the right mainstem causing complete occlusion of the left mainstem.
The flexible bronchoscope and LMA were removed and a 12mm non-ventilating rigid tracheoscope was subsequently inserted into the mid trachea and connected to ventilator.
The flexible bronchoscope was inserted through the rigid and into the stent.
Bronchial lavage was performed with specimen obtained by trap and sent for culture.
The proximal edge of the distal telescoped stent was visualized and using flexible forceps we secured the proximal knot and attempted to withdraw the stent.
The stent moved only slightly but enough to visualize copious amounts of post-obstructive pus being expressed from the previously obstructed left mainstem.
The material was collected in a trap for culture. We then removed the flexible bronchoscope and inserted the rigid optic alongside the non-optical rigid forceps.
The proximal edge of the distal stent was secured and the stent retracted with the rigid bronchoscope which was removed while grasping tightly to the stent.
Both stents were removed with this maneuver and the patient was re-intubated with the rigid bronchoscope.
The airways which were previously covered by the stent were erythematous and friable, however there was no evidence of airway obstruction from external compression related to esophageal mass.
The patient’s esophageal stent could be seen through the posterior trachea covering the TE fistula.
The airways were irrigated and cleaned and once we were confident there was no evidence of active bleeding the rigid bronchoscope was removed and the procedure completed.
Post procedure diagnosis:
-	Stent infection
-	Stent migration resulting in post-obstructive pneumonia.
-	Persistent TE fistula covered by esophageal stent 
-	s/p airway stent removal
Recommendations:
- Transfer to PACU
- Await cultures
- consider gastrograffin swallow to ensure esophageal stent is adequately occluding TE fistula
- Saline nebs 2-3 times per day for 3 days to thin residual blood and secretions allowing for expectoration."""

# Define entities to extract sequentially. 
# Format: (Substring, Label)
# The order MUST match the occurrence in the text to ensure correct sequential finding.
ENTITIES_TO_EXTRACT = [
    ("Tracheal-esophageal fistula", "OBS_LESION"),
    ("esophageal CA", "OBS_LESION"),
    ("Tracheal-esophageal fistula", "OBS_LESION"),
    ("esophageal CA", "OBS_LESION"),
    ("Rigid bronchoscopy", "PROC_ACTION"),
    ("Tracheal", "ANAT_AIRWAY"),
    ("self-expandable", "DEV_STENT_MATERIAL"),
    ("airway stent", "DEV_STENT"),
    ("removal", "PROC_ACTION"),
    ("Stent migration", "OBS_FINDING"),
    ("stent infection", "OBS_FINDING"),
    ("LMA", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("2 cm", "MEAS_SIZE"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("thick purulent material", "OBS_FINDING"),
    ("infection", "OBS_FINDING"),
    ("tracheal stent", "DEV_STENT"),
    ("right", "LATERALITY"),
    ("mainstem", "ANAT_AIRWAY"),
    ("complete occlusion", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("left", "LATERALITY"),
    ("mainstem", "ANAT_AIRWAY"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("LMA", "DEV_INSTRUMENT"),
    ("12mm", "MEAS_SIZE"),
    ("rigid tracheoscope", "DEV_INSTRUMENT"),
    ("mid trachea", "ANAT_AIRWAY"),
    ("ventilator", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid", "DEV_INSTRUMENT"), # referring to rigid scope
    ("stent", "DEV_STENT"),
    ("Bronchial", "ANAT_AIRWAY"),
    ("lavage", "PROC_ACTION"),
    ("specimen", "SPECIMEN"),
    ("stent", "DEV_STENT"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("pus", "OBS_FINDING"),
    ("left", "LATERALITY"),
    ("mainstem", "ANAT_AIRWAY"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("rigid optic", "DEV_INSTRUMENT"),
    ("rigid forceps", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("stent", "DEV_STENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("stents", "DEV_STENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("stent", "DEV_STENT"),
    ("erythematous", "OBS_FINDING"),
    ("friable", "OBS_FINDING"),
    ("airway obstruction", "OUTCOME_AIRWAY_LUMEN_POST"), # context: no evidence of
    ("esophageal mass", "OBS_LESION"),
    ("esophageal stent", "DEV_STENT"),
    ("posterior trachea", "ANAT_AIRWAY"),
    ("TE fistula", "OBS_LESION"),
    ("active bleeding", "OUTCOME_COMPLICATION"), # context: no evidence of
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("Stent infection", "OBS_FINDING"),
    ("Stent migration", "OBS_FINDING"),
    ("pneumonia", "OBS_LESION"),
    ("TE fistula", "OBS_LESION"),
    ("esophageal stent", "DEV_STENT"),
    ("s/p", "CTX_HISTORICAL"),
    ("airway stent", "DEV_STENT"),
    ("removal", "PROC_ACTION"),
    ("esophageal stent", "DEV_STENT"),
    ("TE fistula", "OBS_LESION"),
    ("Saline", "MEDICATION"),
    ("3 days", "CTX_TIME")
]

# ==========================================
# 3. Processing & validation logic
# ==========================================

def create_dataset_entry(note_id, text, entities):
    """Creates the dictionary for ner_dataset_all.jsonl"""
    return {
        "id": note_id,
        "text": text,
        "entities": entities
    }

def process_text_and_extract(text, entity_list, note_id):
    """
    scans text for entities sequentially to handle duplicates correctly.
    Returns:
        valid_entities_dataset: list of dicts for ner_dataset_all [{'id':..., 'label':..., 'start':..., 'end':...}]
        valid_entities_spans: list of dicts for spans.jsonl
    """
    valid_entities_dataset = []
    valid_entities_spans = []
    
    cursor = 0
    
    for sub_text, label in entity_list:
        start = text.find(sub_text, cursor)
        if start == -1:
            # Fallback: search from beginning if not found (though sequential list implies order)
            # This handles cases where human ordering in list might be slightly off, 
            # but ideally we want strict sequential to distinguish specific instances.
            # Warning logged.
            start = text.find(sub_text)
            if start == -1:
                with open(LOG_PATH, "a") as f:
                    f.write(f"WARNING: Entity '{sub_text}' not found in {note_id}\n")
                continue
        
        end = start + len(sub_text)
        
        # Verify extraction
        extracted = text[start:end]
        if extracted != sub_text:
             with open(LOG_PATH, "a") as f:
                    f.write(f"ERROR: Mismatch {note_id}: Expected '{sub_text}', got '{extracted}'\n")
             continue

        # Dataset format
        # Note: ner_dataset_all schema usually asks for [start, end, label] or similar.
        # Based on Prompt instruction: "entities": [ ...list of spans... ] 
        # We will use the standard explicit format.
        dataset_span = {
            "id": f"{label}_{start}",
            "label": label,
            "start": start,
            "end": end,
            # "text": sub_text # Optional depending on schema, usually not needed for pure NER training input if start/end exist
        }
        valid_entities_dataset.append(dataset_span)

        # Spans format
        span_obj = {
            "span_id": f"{label}_{start}",
            "note_id": note_id,
            "label": label,
            "text": sub_text,
            "start": start,
            "end": end
        }
        valid_entities_spans.append(span_obj)
        
        # Update cursor to avoid finding the same instance again if we meant the next one
        cursor = start + 1 

    return valid_entities_dataset, valid_entities_spans

# ==========================================
# 4. Execution
# ==========================================

def main():
    # A. Extract Data
    dataset_entities, span_lines = process_text_and_extract(TEXT, ENTITIES_TO_EXTRACT, NOTE_ID)

    # B. Update ner_dataset_all.jsonl
    dataset_entry = create_dataset_entry(NOTE_ID, TEXT, dataset_entities)
    with open(NER_DATASET_PATH, "a") as f:
        f.write(json.dumps(dataset_entry) + "\n")

    # C. Update notes.jsonl
    notes_entry = {"id": NOTE_ID, "text": TEXT}
    with open(NOTES_PATH, "a") as f:
        f.write(json.dumps(notes_entry) + "\n")

    # D. Update spans.jsonl
    with open(SPANS_PATH, "a") as f:
        for span in span_lines:
            f.write(json.dumps(span) + "\n")

    # E. Update stats.json
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, "r") as f:
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
    # stats["total_files"]  # Assuming this script runs per file or we increment if new file
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(ENTITIES_TO_EXTRACT)
    stats["total_spans_valid"] += len(dataset_entities)

    for span in dataset_entities:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w") as f:
        json.dump(stats, f, indent=4)

    print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()