import json
import os
import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NOTE_ID = "note_192"

# Raw text content reconstructed from the input file
# Note: Double spaces and newlines preserved to match source formatting.
TEXT = """Indications: Left upper lobe mass 
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree the Q190 video bronchoscope was introduced through the mouth.
The vocal cords appeared normal. The subglottic space was normal. The trachea is of normal caliber. The carina was sharp.
All left and right sided airways were normal without endobronchial disease.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 11Ri (5.0 mm), and 11Rs(6.6 mm).
Additionally the 4L was 4.9 mm but slightly hypoechoic and decision was made to sample this node as well.
Sampling by transbronchial needle aspiration was performed in these lymph nodes using an Olympus Visioshot 2 EBUSTBNA 21 gauge needle.
All samples were sent for routine cytology. We then removed the EBUS bronchoscopy and the super-dimension navigational catheter was inserted through the therapeutic bronchoscope and advanced into the airway.
Using navigational map we advanced the 180  degree edge catheter into the proximity of the lesion within the left upper lobe.
Confirmation of placement once at the point of interest with radial ultrasound showed a concentric view.
Biopsies were then performed with a variety of instruments to include peripheral needle, triple needle brush and forceps, under fluoroscopic visualization.
After adequate samples were obtained the bronchoscope was removed. Fluoroscopic inspection was performed and no pneumothorax was visualized at the conclusion of the procedure.
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Flexible bronchoscopy with successful and biopsy of left upper nodule
- Negative Staging EBUS on preliminary evaluation 
- Await final pathology  
- Post-procedure xray did not show pneumothorax.
- Patient was noted to be slightly hypoxic post-procedure likely as a result of sedation and decision was made to admit patient for overnight observation."""

# Define entities to extract (Label, Substring)
# Order matters: text is searched sequentially to handle duplicates correctly.
ENTITIES_TO_EXTRACT = [
    ("ANAT_LUNG_LOC", "Left upper lobe"),
    ("OBS_LESION", "mass"),
    ("MEDICATION", "Propofol"),
    ("ANAT_AIRWAY", "upper airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "left and right sided airways"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "station 11Ri"),
    ("MEAS_SIZE", "5.0 mm"),
    ("ANAT_LN_STATION", "11Rs"),
    ("MEAS_SIZE", "6.6 mm"),
    ("ANAT_LN_STATION", "4L"),
    ("MEAS_SIZE", "4.9 mm"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_INSTRUMENT", "Olympus Visioshot 2 EBUSTBNA"),
    ("DEV_NEEDLE", "21 gauge"),
    ("PROC_METHOD", "EBUS"),
    ("DEV_INSTRUMENT", "super-dimension navigational catheter"),
    ("PROC_METHOD", "navigational"),
    ("DEV_INSTRUMENT", "180  degree edge catheter"),
    ("OBS_LESION", "lesion"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("PROC_METHOD", "radial ultrasound"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_INSTRUMENT", "peripheral needle"),
    ("DEV_INSTRUMENT", "triple needle brush"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_METHOD", "fluoroscopic"),
    ("PROC_METHOD", "Fluoroscopic"),
    ("OUTCOME_COMPLICATION", "no pneumothorax"),
    ("OUTCOME_COMPLICATION", "No immediate complications"),
    ("MEAS_VOL", "5 cc"),
    ("PROC_ACTION", "Flexible bronchoscopy"),
    ("PROC_ACTION", "biopsy"),
    ("ANAT_LUNG_LOC", "left upper"),
    ("OBS_LESION", "nodule"),
    ("PROC_METHOD", "EBUS"),
    ("OUTCOME_COMPLICATION", "did not show pneumothorax"),
    ("OUTCOME_SYMPTOMS", "slightly hypoxic")
]

# Paths
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILE_NER_DATASET = OUTPUT_DIR / "ner_dataset_all.jsonl"
FILE_NOTES = OUTPUT_DIR / "notes.jsonl"
FILE_SPANS = OUTPUT_DIR / "spans.jsonl"
FILE_STATS = OUTPUT_DIR / "stats.json"
FILE_LOG = OUTPUT_DIR / "alignment_warnings.log"


# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

def get_entities_with_indices(text, entity_list):
    """
    Finds start/end indices for entities.
    Consumes text to ensure duplicates are mapped to correct occurrences sequentially.
    """
    results = []
    search_start = 0
    
    for label, substr in entity_list:
        start = text.find(substr, search_start)
        if start == -1:
            # Fallback: if not found sequentially (e.g. out of order in list), search from beginning
            # Warning: This is a fallback and might map to wrong duplicate if order was crucial.
            start = text.find(substr)
            if start == -1:
                print(f"CRITICAL WARNING: Entity '{substr}' not found in text.")
                continue
        
        end = start + len(substr)
        
        # Validate exact match
        extracted = text[start:end]
        if extracted != substr:
            print(f"MISMATCH: Expected '{substr}', got '{extracted}'")
            continue
            
        results.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        
        # Advance search_start to avoid re-matching the same span if not intended, 
        # but be careful not to skip overlapping entities (though NER usually disjoint).
        # We assume entities in the list appear in order of the text.
        search_start = start + 1

    return results

def update_jsonl(filepath, data):
    """Appends a JSON line to a file."""
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

def update_stats(filepath, entities, successful=True):
    """Updates the stats.json file."""
    if not filepath.exists():
        print(f"Stats file not found at {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    if successful:
        stats["total_files"] += 1
        stats["successful_files"] += 1
        stats["total_notes"] += 1
        stats["total_spans_raw"] += len(entities)
        stats["total_spans_valid"] += len(entities)
        
        # Update label counts
        for ent in entities:
            label = ent['label']
            if label in stats["label_counts"]:
                stats["label_counts"][label] += 1
            else:
                stats["label_counts"][label] = 1
    else:
        stats["total_files"] += 1
        stats["alignment_errors"] += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def validate_alignment(text, entities, log_path):
    """Checks alignment and logs warnings."""
    with open(log_path, 'a', encoding='utf-8') as log:
        for ent in entities:
            extracted = text[ent['start']:ent['end']]
            if extracted != ent['text']:
                msg = f"[{datetime.datetime.now()}] ALIGNMENT ERROR: {NOTE_ID} - Expected '{ent['text']}', found '{extracted}' at {ent['start']}:{ent['end']}\n"
                log.write(msg)

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Extract Entities
    found_entities = get_entities_with_indices(TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Update ner_dataset_all.jsonl
    # Schema: {"id": "note_X", "text": "...", "entities": [[start, end, label], ...]}
    ner_entry = {
        "id": NOTE_ID,
        "text": TEXT,
        "entities": [[e['start'], e['end'], e['label']] for e in found_entities]
    }
    update_jsonl(FILE_NER_DATASET, ner_entry)
    
    # 3. Update notes.jsonl
    notes_entry = {
        "id": NOTE_ID,
        "text": TEXT
    }
    update_jsonl(FILE_NOTES, notes_entry)
    
    # 4. Update spans.jsonl
    for ent in found_entities:
        span_entry = {
            "span_id": f"{ent['label']}_{ent['start']}",
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        }
        update_jsonl(FILE_SPANS, span_entry)
        
    # 5. Update stats.json
    update_stats(FILE_STATS, found_entities)
    
    # 6. Validation
    validate_alignment(TEXT, found_entities, FILE_LOG)
    
    print(f"Successfully processed {NOTE_ID}. Added {len(found_entities)} entities.")

if __name__ == "__main__":
    main()