import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_212"

# The full raw text of the note
RAW_TEXT = """Procedure Name: Medical Thoracoscopy (pleuroscopy) with parietal pleural biopsies
CPT code(s): CPT 320098 Thoracotomy, with biopsy(ies) of pleura
Indications: Left sided pleural effusion
Medications: As per anesthesia record
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. The patient was placed on the standard procedural bed in the right lateral decubitus position and sites of compression were well padded.
The pleural entry site was identified by means of the ultrasound.
The patient was sterilely prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual fashion.
The entry sites was infiltrated with a 10mL solution of 1% lidocaine.
Following instillation of subcutaneous lidocaine a 1.5 cm subcutaneous incision was made and gentle dissection was performed until the pleural space was entered.
A 5 mm disposable primary port was then placed on the left side at the 6th anterior axillary line.
After allowing air entrainment and lung deflation, suction was applied through the port to remove pleural fluid with removal of approximately 700cc of serosanguinous fluid.
The rigid pleuroscopy telescope was then introduced through the trocar and advanced into the pleural space.
The pleura was had multiple simple appearing adhesions and small whitish plaques were seen along the posterior parietal pleural.
The 5mm disposable primary port was then replaced with an 8mm disposable primary port via the same tract and optical cupped biopsy forceps were introduced through the trocar and advanced into the pleural space.
After gentle lysis of simple adhesions with the blunt closed forceps, biopsies of the suspicious areas in the parietal pleura posteriorly were performed with rigid cupped forceps and sent for histopathological and microbiological examination with approximately 8 total biopsies taken.
There was minimal bleeding associated with the biopsies. After residual bleeding had subsided, a 14 French pigtail catheter was inserted through the port site and attached to pleuro-vac with suction.
After air evacuation with cessation of bubbling in pleuro-vac the chest tube was removed and the site sutured and dressed.
Complications: None
The patient tolerated the procedural well.
Post-procedure chest radiograph showed full lung re-expansion with minimal residual pleural effusion.
Estimated Blood Loss: 10cc
Post Procedure Diagnosis: Pleural effusion 
Recommendation:
Discharge once post-op criteria met
Will await pathology and microbiological studies"""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# ENTITY DEFINITIONS
# ==========================================
# List of (Label, Surface Text)
# The script will locate these in the RAW_TEXT to generate offsets.
entities_to_extract = [
    ("PROC_ACTION", "Medical Thoracoscopy"),
    ("PROC_ACTION", "pleuroscopy"),
    ("ANAT_PLEURA", "parietal pleural"),
    ("PROC_ACTION", "biopsies"),
    ("PROC_ACTION", "Thoracotomy"),
    ("PROC_ACTION", "biopsy(ies)"),
    ("ANAT_PLEURA", "pleura"),
    ("LATERALITY", "Left"),
    ("OBS_FINDING", "pleural effusion"),
    ("PROC_METHOD", "ultrasound"),
    ("MEAS_VOL", "10mL"),
    ("MEDICATION", "lidocaine"),
    ("MEDICATION", "lidocaine"), # Second occurrence
    ("MEAS_SIZE", "1.5 cm"),
    ("ANAT_PLEURA", "pleural space"),
    ("MEAS_SIZE", "5 mm"),
    ("DEV_INSTRUMENT", "disposable primary port"),
    ("LATERALITY", "left"),
    ("PROC_ACTION", "suction"),
    ("SPECIMEN", "pleural fluid"),
    ("MEAS_VOL", "700cc"),
    ("OBS_FINDING", "serosanguinous fluid"),
    ("DEV_INSTRUMENT", "rigid pleuroscopy telescope"),
    ("DEV_INSTRUMENT", "trocar"),
    ("ANAT_PLEURA", "pleural space"), # Second occurrence
    ("ANAT_PLEURA", "pleura"), # Second occurrence
    ("OBS_FINDING", "adhesions"),
    ("OBS_FINDING", "small whitish plaques"),
    ("ANAT_PLEURA", "posterior parietal pleural"),
    ("MEAS_SIZE", "5mm"),
    ("DEV_INSTRUMENT", "disposable primary port"), # Second occurrence
    ("MEAS_SIZE", "8mm"),
    ("DEV_INSTRUMENT", "disposable primary port"), # Third occurrence
    ("DEV_INSTRUMENT", "optical cupped biopsy forceps"),
    ("DEV_INSTRUMENT", "trocar"), # Second occurrence
    ("ANAT_PLEURA", "pleural space"), # Third occurrence
    ("PROC_ACTION", "lysis"),
    ("OBS_FINDING", "adhesions"), # Second occurrence
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "biopsies"), # Second occurrence
    ("ANAT_PLEURA", "parietal pleura"),
    ("DEV_INSTRUMENT", "rigid cupped forceps"),
    ("MEAS_COUNT", "8"),
    ("PROC_ACTION", "biopsies"), # Third occurrence
    ("DEV_CATHETER", "14 French pigtail catheter"),
    ("PROC_ACTION", "suction"), # Second occurrence
    ("DEV_CATHETER", "chest tube"),
    ("OUTCOME_PLEURAL", "lung re-expansion"),
    ("OBS_FINDING", "pleural effusion"), # Second occurrence
    ("MEAS_VOL", "10cc"),
    ("OBS_FINDING", "Pleural effusion") # Third occurrence
]

# ==========================================
# PROCESSING LOGIC
# ==========================================

def get_entity_spans(text, entity_list):
    """
    Finds strict start/end character indices for the entities.
    Handles duplicate terms by advancing the search cursor.
    """
    spans = []
    cursor = 0
    # Keep track of last index found for repeated terms to avoid overlap if needed,
    # but strictly following the list order allows mapping sequential duplicates correctly.
    
    # We need to process the list in order of appearance in the text to handle duplicates correctly.
    # However, the input list above isn't perfectly sorted by offset.
    # Strategy: Find all occurrences of a term, pop the first one that is >= cursor.
    
    # To be robust, we will iterate through the provided list.
    # For each entity, we find the first match AFTER the *previous* entity's end
    # if it's a repeat, or simply find the best match. 
    # NOTE: The manual list above implies a reading order.
    
    # Global cursor for the whole file? No, terms might jump back if list isn't sorted.
    # Better approach for this script: 
    # 1. Find all matches for a term.
    # 2. Assign them to the entities requested based on proximity to expected flow or just
    #    greedy allocation.
    
    # Simpler approach since I constructed the list:
    # I will iterate the text and match them sequentially.
    
    current_search_start = 0
    
    final_spans = []
    
    for label, surface in entity_list:
        # specific fix for Python string finding
        idx = text.find(surface, current_search_start)
        
        if idx == -1:
            # Fallback: restart search from 0 if not found (in case list order was slightly off)
            idx = text.find(surface, 0)
        
        if idx != -1:
            start = idx
            end = idx + len(surface)
            final_spans.append({
                "start": start,
                "end": end,
                "label": label,
                "text": surface
            })
            # Advance cursor to avoid re-finding the same exact instance 
            # for the NEXT entity if it happens to be the same string.
            current_search_start = start + 1
        else:
            print(f"WARNING: Could not find entity '{surface}' in text.")

    return final_spans

def update_ner_dataset(output_dir, note_id, text, entities):
    file_path = output_dir / "ner_dataset_all.jsonl"
    
    # Construct the entry
    entry = {
        "id": note_id,
        "text": text,
        "entities": entities
    }
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes(output_dir, note_id, text):
    file_path = output_dir / "notes.jsonl"
    entry = {"id": note_id, "text": text}
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans(output_dir, note_id, entities):
    file_path = output_dir / "spans.jsonl"
    with open(file_path, "a", encoding="utf-8") as f:
        for ent in entities:
            # Create a unique span_id (e.g., Label_StartOffset)
            span_id = f"{ent['label']}_{ent['start']}"
            entry = {
                "span_id": span_id,
                "note_id": note_id,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(entry) + "\n")

def update_stats(output_dir, new_entities):
    file_path = output_dir / "stats.json"
    
    if file_path.exists():
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
    # Assuming one note per file in this workflow, or just incrementing files generally
    stats["total_files"] += 1
    stats["total_spans_raw"] += len(new_entities)
    stats["total_spans_valid"] += len(new_entities)
    
    for ent in new_entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def log_alignment(text, entities):
    with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as f:
        for ent in entities:
            sliced = text[ent['start']:ent['end']]
            if sliced != ent['text']:
                log_msg = f"[{datetime.datetime.now()}] MISMATCH: {ent['label']} expected '{ent['text']}' but got '{sliced}' at {ent['start']}:{ent['end']}\n"
                f.write(log_msg)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Calculate Spans
    extracted_entities = get_entity_spans(RAW_TEXT, entities_to_extract)
    
    # 2. Update ner_dataset_all.jsonl
    update_ner_dataset(OUTPUT_DIR, NOTE_ID, RAW_TEXT, extracted_entities)
    
    # 3. Update notes.jsonl
    update_notes(OUTPUT_DIR, NOTE_ID, RAW_TEXT)
    
    # 4. Update spans.jsonl
    update_spans(OUTPUT_DIR, NOTE_ID, extracted_entities)
    
    # 5. Update stats.json
    update_stats(OUTPUT_DIR, extracted_entities)
    
    # 6. Validate
    log_alignment(RAW_TEXT, extracted_entities)
    
    print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")