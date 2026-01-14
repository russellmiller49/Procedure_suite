import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_132"
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text Content
# ==========================================
RAW_TEXT = """NOTE_ID:  note_132 SOURCE_FILE: note_132.txt Procedure Name: Bronchoscopy
Indications: Chronic cough, Shortness of breath
Medications: General Anesthesia, 2% Lidocaine, tracheobronchial tree 10 mL

Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree.The 0 degree 4.0mm rigid optic was introduced through the mouth and advanced to the tracheobronchial tree.
The BF-Q190 slim video bronchoscope was introduced through the rigid bronchoscope (after telescope was removed) and advanced to the tracheobronchial tree.
The BF-1TH190 therapeutic video bronchoscope was introduced through the rigid bronchoscope (after telescope was removed) and advanced to the tracheobronchial tree.
The patient tolerated the procedure well. 
Procedure Description:
Patient was brought to the bronchoscopy suite, where a timeout was performed and the radiographic reviewed prior to the procedure.
Intravenous sedation was administered under the direction of Dr. Sarkis, once patient was adequately sedated and neuromuscular blockade had been provided, he was intubated without difficulty using the Dumon Orange striped bronchoscope.
Oropharyngeal landmarks were visualized, with extensive redundant soft tissue in the oropharynx.
The vocal cords visualized the appeared to be moving normally.
Chronic inflammatory changes were noted in the tracheal mucosa, with dynamic airway collapse noted.
The main carina was architecturally distorted, with a fibrotic stricture noted to be stretching from the posterior wall of the right mainstem bronchus and tethering the anteromedial aspect of the main carina.
Right and left lungs were explored segmentally and subsegmentally using the Q190 video bronchoscope introduced through the rigid bronchoscope.
Exploration of the left lung revealed chronic inflammatory changes in the bronchial mucosa, with dynamic airway collapse that resulted in less than 50% occlusion of the airway lumen with respirations.
Exploration of the right lung revealed the previously placed stent in place with 90% obstruction of the right middle lobe bronchus from what appeared to be bronchial mucosal edema and granulation tissue.
The stent was also heavily coated with thick mucopurulent secretions. The right lower lobe bronchus appeared to be patent.
Given the findings, particularly the degree of obstruction of the right middle lobe bronchus and the exuberant granulation tissue noted, we elected to remove the stent currently in place.
This was done en bloc using forceps without difficulty. Following the removal of the stent, the reconstructed right bronchus intermedius was carefully examined and was noted to have dynamic airway collapse though the degree of luminal obstruction is estimated at less than 50%.
The weblike fibrotic stricture arising from the posterior aspect of the right mainstem bronchus and tethering the anteromedial aspect of the main carina was divided using electrocautery knife.
This resulted in some freeing of the stricture, but the dynamic airway collapse continued to bring the tissues into apposition during respirations.
The diode laser was used to fulgurate the abutting tissue with the intent to discourage additional stricture formation.
Once a space had been developed, cryotherapy was used at the edges, also to discourage restenosis.
Given the fact that the luminal obstruction during respiration was less than 50%, and there was evidence of granulation tissue formation, we elected not to place a stent at this point in time.
The plan will be to bring him back for airway examination in 2 weeks to decide if silicone stent would be appropriate.
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc."""

# ==========================================
# 3. Entity Extraction Logic
# ==========================================
# List of entities to extract: (Label, Text Segment)
# Order matters for simple sequential searching to avoid ambiguity
entities_to_map = [
    ("PROC_METHOD", "Bronchoscopy"),
    ("MEDICATION", "Lidocaine"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # 1st mention
    ("ANAT_AIRWAY", "tracheobronchial tree"), # 2nd mention
    ("DEV_INSTRUMENT", "rigid optic"),
    ("ANAT_AIRWAY", "tracheobronchial tree"), # 3rd mention
    ("PROC_METHOD", "BF-Q190 slim video bronchoscope"),
    ("PROC_METHOD", "rigid bronchoscope"), # 1st mention
    ("ANAT_AIRWAY", "tracheobronchial tree"), # 4th mention
    ("PROC_METHOD", "BF-1TH190 therapeutic video bronchoscope"),
    ("PROC_METHOD", "rigid bronchoscope"), # 2nd mention
    ("ANAT_AIRWAY", "tracheobronchial tree"), # 5th mention
    ("PROC_METHOD", "Dumon Orange striped bronchoscope"),
    ("ANAT_AIRWAY", "tracheal mucosa"),
    ("OBS_FINDING", "dynamic airway collapse"), # 1st
    ("ANAT_AIRWAY", "main carina"),
    ("OBS_LESION", "fibrotic stricture"),
    ("ANAT_AIRWAY", "right mainstem bronchus"),
    ("ANAT_AIRWAY", "main carina"),
    ("ANAT_LUNG_LOC", "Right and left lungs"),
    ("PROC_METHOD", "Q190 video bronchoscope"),
    ("PROC_METHOD", "rigid bronchoscope"), # 3rd mention
    ("ANAT_LUNG_LOC", "left lung"),
    ("ANAT_AIRWAY", "bronchial mucosa"),
    ("OBS_FINDING", "dynamic airway collapse"), # 2nd
    ("ANAT_LUNG_LOC", "right lung"),
    ("DEV_STENT", "stent"), # 1st
    ("OUTCOME_AIRWAY_LUMEN_PRE", "90% obstruction"),
    ("ANAT_AIRWAY", "right middle lobe bronchus"),
    ("OBS_FINDING", "bronchial mucosal edema"),
    ("OBS_LESION", "granulation tissue"),
    ("DEV_STENT", "stent"), # 2nd
    ("ANAT_AIRWAY", "right lower lobe bronchus"),
    ("ANAT_AIRWAY", "right middle lobe bronchus"),
    ("OBS_LESION", "granulation tissue"),
    ("PROC_ACTION", "remove"),
    ("DEV_STENT", "stent"), # 3rd
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "removal"),
    ("DEV_STENT", "stent"), # 4th
    ("ANAT_AIRWAY", "right bronchus intermedius"),
    ("OBS_FINDING", "dynamic airway collapse"), # 3rd
    ("OUTCOME_AIRWAY_LUMEN_POST", "less than 50%"),
    ("OBS_LESION", "fibrotic stricture"),
    ("ANAT_AIRWAY", "right mainstem bronchus"),
    ("ANAT_AIRWAY", "main carina"),
    ("DEV_INSTRUMENT", "electrocautery knife"),
    ("OBS_LESION", "stricture"),
    ("OBS_FINDING", "dynamic airway collapse"), # 4th
    ("DEV_INSTRUMENT", "diode laser"),
    ("PROC_ACTION", "fulgurate"),
    ("OBS_LESION", "stricture"),
    ("PROC_ACTION", "cryotherapy"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "less than 50%"), # 2nd mention
    ("OBS_LESION", "granulation tissue"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT_MATERIAL", "silicone"),
    ("DEV_STENT", "stent"),
    ("OUTCOME_COMPLICATION", "No immediate complications")
]

processed_entities = []
cursor = 0

for label, text_snippet in entities_to_map:
    start_idx = RAW_TEXT.find(text_snippet, cursor)
    if start_idx == -1:
        # Fallback: restart cursor if snippet likely appears earlier but was missed due to strict sequential assumption
        # Note: In production, more robust regex/multi-pass logic is used.
        start_idx = RAW_TEXT.find(text_snippet)
    
    if start_idx != -1:
        end_idx = start_idx + len(text_snippet)
        processed_entities.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text_snippet,
            "start": start_idx,
            "end": end_idx
        })
        cursor = start_idx + 1 # Advance cursor
    else:
        print(f"WARNING: Could not locate snippet '{text_snippet}' for label {label}")

# ==========================================
# 4. File Update Functions
# ==========================================

def update_ner_dataset():
    entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in processed_entities]
    }
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")

def update_notes():
    entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")

def update_spans():
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for entity in processed_entities:
            f.write(json.dumps(entity) + "\n")

def update_stats():
    if not STATS_PATH.exists():
        print("Stats file not found, skipping stats update.")
        return

    with open(STATS_PATH, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    # Update global counts
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(processed_entities)
    stats["total_spans_valid"] += len(processed_entities)

    # Update label counts
    for entity in processed_entities:
        lbl = entity["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1

    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def validate_alignment():
    warnings = []
    for entity in processed_entities:
        snippet_in_text = RAW_TEXT[entity["start"]:entity["end"]]
        if snippet_in_text != entity["text"]:
            warnings.append(f"Mismatch {entity['span_id']}: Expected '{entity['text']}', found '{snippet_in_text}'")
    
    if warnings:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            for w in warnings:
                f.write(f"{datetime.datetime.now().isoformat()} - {w}\n")

# ==========================================
# 5. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Processing {NOTE_ID}...")
    try:
        update_ner_dataset()
        update_notes()
        update_spans()
        update_stats()
        validate_alignment()
        print(f"Successfully updated pipeline with {len(processed_entities)} entities.")
    except Exception as e:
        print(f"Error updating pipeline: {e}")