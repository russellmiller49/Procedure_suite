import json
import os
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_249"

# Raw text content of the note (exact copy to ensure index alignment)
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Tracheal-esophageal fistula secondary to esophageal CA 
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

# Ordered list of entities to extract
# Format: (Label, Text_Snippet)
# Note: These must appear in the text in this exact order for the simple locator logic to work.
ENTITIES_TO_EXTRACT = [
    ("OBS_LESION", "Tracheal-esophageal fistula"),
    ("OBS_LESION", "esophageal CA"),
    ("OBS_LESION", "Tracheal-esophageal fistula"),
    ("OBS_LESION", "esophageal CA"),
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("ANAT_AIRWAY", "Tracheal"),
    ("DEV_STENT", "airway stent"),
    ("DEV_STENT", "Stent"), # In "Stent migration"
    ("DEV_STENT", "stent"), # In "stent infection"
    ("DEV_INSTRUMENT", "LMA"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "thick purulent material"),
    ("OBS_FINDING", "infection"),
    ("ANAT_AIRWAY", "distal tracheal"),
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "right mainstem"),
    ("OBS_FINDING", "occlusion"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "LMA"),
    ("MEAS_SIZE", "12mm"),
    ("DEV_INSTRUMENT", "rigid tracheoscope"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid"), # Referring to scope
    ("DEV_STENT", "stent"),
    ("PROC_ACTION", "Bronchial lavage"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "pus"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid optic"),
    ("DEV_INSTRUMENT", "rigid forceps"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stents"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "airways"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "erythematous"),
    ("OBS_FINDING", "friable"),
    ("OBS_FINDING", "airway obstruction"),
    ("OBS_LESION", "esophageal mass"),
    ("DEV_STENT", "esophageal stent"),
    ("ANAT_AIRWAY", "posterior trachea"),
    ("OBS_LESION", "TE fistula"),
    ("ANAT_AIRWAY", "airways"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("DEV_STENT", "Stent"),
    ("OBS_FINDING", "infection"),
    ("DEV_STENT", "Stent"),
    ("OBS_LESION", "pneumonia"),
    ("OBS_LESION", "TE fistula"),
    ("DEV_STENT", "esophageal stent"),
    ("DEV_STENT", "airway stent"),
    ("DEV_STENT", "esophageal stent"),
    ("OBS_LESION", "TE fistula")
]

# Directory setup
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

def update_dataset():
    # 1. Calculate Spans
    spans = []
    cursor = 0
    
    for label, substr in ENTITIES_TO_EXTRACT:
        # Find next occurrence of substring from current cursor
        start = RAW_TEXT.find(substr, cursor)
        
        if start == -1:
            print(f"Error: Could not find '{substr}' after index {cursor}")
            continue
            
        end = start + len(substr)
        
        # Verify text match
        extracted_text = RAW_TEXT[start:end]
        if extracted_text != substr:
            with open(LOG_PATH, "a") as log:
                log.write(f"Mismatch in {NOTE_ID}: Expected '{substr}', got '{extracted_text}' at {start}:{end}\n")
        
        spans.append({
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": extracted_text,
            "start": start,
            "end": end
        })
        
        # Advance cursor to avoid re-matching the same instance
        cursor = start + 1

    # 2. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": spans
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Append to spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")

    # 5. Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Initialize if missing (fallback)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)

    for span in spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {NOTE_ID}. Added {len(spans)} entities.")

if __name__ == "__main__":
    update_dataset()