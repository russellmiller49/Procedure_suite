import json
import os
import datetime
from pathlib import Path

# --- Configuration ---
NOTE_ID = "note_133"
# Raw text from the medical note
RAW_TEXT = """NOTE_ID:  note_133 SOURCE_FILE: note_133.txt Procedure Name: Bronchoscopy
Indications: Chronic cough; shortness of breath
Medications: General anesthesia; 2% lidocaine, 10 mL instilled to the tracheobronchial tree

Procedure, risks, benefits, and alternatives were explained to the patient. All questions were answered, and informed consent was documented per institutional protocol. A history and physical examination were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed. A time-out was performed prior to the intervention. Following administration of intravenous medications per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree, a 0-degree 4.0-mm rigid optic was introduced through the mouth and advanced into the tracheobronchial tree. The BF-Q190 slim video bronchoscope was then introduced through the rigid bronchoscope after removal of the telescope and advanced into the tracheobronchial tree. The BF-1TH190 therapeutic video bronchoscope was subsequently introduced in a similar fashion. The patient tolerated the procedure well.

Procedure Description:

The patient was brought to the bronchoscopy suite, where a time-out was performed and radiographic imaging was reviewed prior to the procedure. Intravenous anesthesia was administered under the direction of Dr. Sarkis. Once the patient was adequately anesthetized and neuromuscular blockade had been achieved, he was intubated without difficulty using the Dumon orange-striped rigid bronchoscope.

Oropharyngeal landmarks were visualized, revealing extensive redundant soft tissue in the oropharynx.
The vocal cords were visualized and appeared to move normally.
Chronic inflammatory changes were noted in the tracheal mucosa, with evidence of dynamic airway collapse.
The main carina was architecturally distorted, with a fibrotic stricture arising from the posterior wall of the right mainstem bronchus and tethering the anteromedial aspect of the main carina.

Findings:

Chronic cough

Fibrotic stricture of the right mainstem bronchus, excised

Stent located in the bronchus intermedius, removed en bloc

Chronic mucosal inflammation of the right mainstem bronchus

Post–stent removal luminal obstruction of the right mainstem bronchus and right bronchus intermedius estimated at approximately 30%

Post-Procedure Diagnosis:

Chronic mucosal inflammation of the right mainstem bronchus

Luminal obstruction of the right mainstem bronchus and right bronchus intermedius estimated at approximately 30% following stent removal

Technically successful rigid bronchoscopy with stent removal and stricture resection

The patient remained stable throughout the procedure and was transferred in good condition to the post-bronchoscopy recovery area, where he will be observed until discharge criteria are met. Preliminary findings were discussed with the patient, and follow-up in the pulmonary clinic in two weeks has been recommended."""

# Target Entities to extract (Label, Text Fragment)
# Note: This list allows dynamic calculation of indices to ensure alignment.
TARGET_ENTITIES = [
    ("PROC_METHOD", "Bronchoscopy"),
    ("OBS_FINDING", "Chronic cough"),
    ("OBS_FINDING", "shortness of breath"),
    ("MEDICATION", "General anesthesia"),
    ("MEDICATION", "2% lidocaine"),
    ("MEAS_VOL", "10 mL"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "0-degree 4.0-mm rigid optic"),
    ("DEV_INSTRUMENT", "BF-Q190 slim video bronchoscope"),
    ("DEV_INSTRUMENT", "BF-1TH190 therapeutic video bronchoscope"),
    ("DEV_INSTRUMENT", "Dumon orange-striped rigid bronchoscope"),
    ("OBS_FINDING", "redundant soft tissue"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("OBS_FINDING", "Chronic inflammatory changes"),
    ("ANAT_AIRWAY", "tracheal mucosa"),
    ("OBS_FINDING", "dynamic airway collapse"),
    ("ANAT_AIRWAY", "main carina"),
    ("OBS_FINDING", "architecturally distorted"),
    ("OBS_LESION", "fibrotic stricture"),
    ("ANAT_AIRWAY", "right mainstem bronchus"),
    ("OBS_FINDING", "tethering"),
    ("PROC_ACTION", "excised"),
    ("DEV_STENT", "Stent"),
    ("ANAT_AIRWAY", "bronchus intermedius"),
    ("PROC_ACTION", "removed en bloc"),
    ("OBS_FINDING", "Chronic mucosal inflammation"),
    ("OBS_LESION", "luminal obstruction"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "30%"),
    ("PROC_METHOD", "rigid bronchoscopy"),
    ("PROC_ACTION", "stent removal"),
    ("PROC_ACTION", "stricture resection"),
]

# --- Path Setup ---
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_DATASET_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_DATASET_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"


def calculate_indices(text, target_list):
    """Calculates start and end indices for target entities."""
    entities = []
    search_start_idx = 0
    
    for label, span_text in target_list:
        # Find the next occurrence of the span text
        start = text.find(span_text, search_start_idx)
        
        if start == -1:
            # If not found (e.g., searching from beginning again might be needed for duplicates, 
            # but for this linear list we assume order or uniqueness)
            # Reset search for safety or log warning
            start = text.find(span_text)
        
        if start != -1:
            end = start + len(span_text)
            entities.append({
                "label": label,
                "text": span_text,
                "start": start,
                "end": end
            })
            # Advance search index to avoid overlapping finding if desired, 
            # or keep 0 if looking for first match only. 
            # Here we advance slightly to find sequential mentions if listed sequentially.
            search_start_idx = start + 1
        else:
            print(f"Warning: Could not find span text '{span_text}' in source text.")
            
    return entities

def update_ner_dataset(entities):
    """Appends the new note with entities to ner_dataset_all.jsonl."""
    # Convert to strict schema for NER dataset: {"id": ..., "text": ..., "entities": [...]}
    # The entities list in ner_dataset usually requires just start, end, label.
    ner_entities = [{"start": e["start"], "end": e["end"], "label": e["label"]} for e in entities]
    
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": ner_entities
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes_dataset():
    """Appends the raw note to notes.jsonl."""
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans_dataset(entities):
    """Appends individual spans to spans.jsonl."""
    with open(SPANS_DATASET_PATH, "a", encoding="utf-8") as f:
        for e in entities:
            span_entry = {
                "span_id": f"{e['label']}_{e['start']}",
                "note_id": NOTE_ID,
                "label": e["label"],
                "text": e["text"],
                "start": e["start"],
                "end": e["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

def update_stats(entities):
    """Updates stats.json with new counts."""
    if not STATS_PATH.exists():
        return

    with open(STATS_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)

    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note = 1 file for this batch
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities) # Assuming all valid

    if "label_counts" not in stats:
        stats["label_counts"] = {}

    for e in entities:
        label = e["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def validate_alignment(entities):
    """Checks alignment and logs warnings."""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for e in entities:
            extracted = RAW_TEXT[e["start"]:e["end"]]
            if extracted != e["text"]:
                error_msg = {
                    "note_id": NOTE_ID,
                    "label": e["label"],
                    "span_text": e["text"],
                    "start": e["start"],
                    "end": e["end"],
                    "issue": f"alignment_error: extracted='{extracted}' vs span='{e['text']}'"
                }
                f.write(json.dumps(error_msg) + "\n")

if __name__ == "__main__":
    # 1. Calculate Indices
    extracted_entities = calculate_indices(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Update ner_dataset_all.jsonl
    update_ner_dataset(extracted_entities)
    
    # 3. Update notes.jsonl
    update_notes_dataset()
    
    # 4. Update spans.jsonl
    update_spans_dataset(extracted_entities)
    
    # 5. Update stats.json
    update_stats(extracted_entities)
    
    # 6. Validate
    validate_alignment(extracted_entities)
    
    print(f"Successfully processed {NOTE_ID} with {len(extracted_entities)} entities.")