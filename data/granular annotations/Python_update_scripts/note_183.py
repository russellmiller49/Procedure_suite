import json
import os
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_183"

# Raw text exactly as provided in the source file
RAW_TEXT = """NOTE_ID:  note_183 SOURCE_FILE: note_183.txt PRE-PROCEDURE DIAGNISOS: LEFT UPPER LOBE PULMONARY NODULE
POST- PROCEDURE DIAGNISOS: LEFT UPPER LOBE PULMONARY NODULE
PROCEDURE PERFORMED:  
Flexible bronchoscopy with electromagnetic navigation under flouroscopic and EBUS guidance with transbronchial needle aspiration, Transbronchial biopsy and bronchioalveolar lavage.
CPT 31654 Bronchoscope with Endobronchial Ultrasound guidance for peripheral lesion
CPT 31628 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with transbronchial lung biopsy(s), single lobe
CPT +31624 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with bronchial alveolar lavage
CPT +31627 Bronchoscopy with computer assisted image guided navigation
INDICATIONS FOR EXAMINATION:   Left upper lobe lung nodule            
MEDICATIONS:    GA
FINDINGS: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the endotracheal tube and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. We then removed the diagnostic Q190 bronchoscope and the super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using navigational map we attempted to advance the 180 degree edge catheter into the proximity of the lesion within apico-posterior branch of left upper lobe.
Radial probe was used to attempt to confirm presence within the lesion.
Although we were able to navigate directly to the lesion with navigation the radial probe view was suboptimal.
Biopsy was performed initially with triple needle brush and TBNA needle.
ROSE did not reveal evidence to support that we were within the lesion.
Multiple attempts were made to manipulate the catheter and biopsies were then performed with a variety of instruments to include peripheral needle, and forceps, brush under fluoroscopic visualization.
The specimens reviewed on-site remained suboptimal.  Multiple forceps biopsies were performed within the location of the lesion and placed in cell-block.
After which a mini-BAL was then performed through the super-D catheter.
We then removed the therapeutic bronchoscope with super-D catheter and reinserted the diagnostic scope at which point repeat airway inspection was then performed and once we were satisfied that no bleeding occurred, the bronchoscope was removed and the procedure completed.
ESTIMATED BLOOD LOSS:   None 
COMPLICATIONS:                 None

IMPRESSION:  
- S/P bronchoscopy with biopsy and lavage.
- Suboptimal navigational localization 
RECOMMENDATIONS
- Transfer to post-procedural unit
- Post-procedure CXR
- D/C home once criteria met
- Await pathology"""

# Entity definitions based on Label_guide_UPDATED.csv
# Format: (Text_Snippet, Label)
# Order matters for sequential search to handle duplicates correctly if needed
ENTITY_CANDIDATES = [
    ("LEFT UPPER LOBE", "ANAT_LUNG_LOC"),
    ("PULMONARY NODULE", "OBS_LESION"),
    ("LEFT UPPER LOBE", "ANAT_LUNG_LOC"),
    ("PULMONARY NODULE", "OBS_LESION"),
    ("Flexible bronchoscopy", "PROC_ACTION"),
    ("electromagnetic navigation", "PROC_METHOD"),
    ("flouroscopic", "PROC_METHOD"), # Capture exact typo from text
    ("EBUS", "PROC_METHOD"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("Transbronchial biopsy", "PROC_ACTION"),
    ("bronchioalveolar lavage", "PROC_ACTION"),
    ("Endobronchial Ultrasound", "PROC_METHOD"),
    ("fluoroscopic", "PROC_METHOD"),
    ("transbronchial lung biopsy(s)", "PROC_ACTION"),
    ("bronchial alveolar lavage", "PROC_ACTION"),
    ("computer assisted image guided navigation", "PROC_METHOD"),
    ("Left upper lobe", "ANAT_LUNG_LOC"),
    ("lung nodule", "OBS_LESION"),
    ("GA", "MEDICATION"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"), # Second mention
    ("The trachea", "ANAT_AIRWAY"),
    ("The carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"), # Third mention
    ("apico-posterior branch of left upper lobe", "ANAT_LUNG_LOC"),
    ("Radial probe", "DEV_INSTRUMENT"),
    ("triple needle brush", "DEV_INSTRUMENT"),
    ("TBNA needle", "DEV_NEEDLE"),
    ("peripheral needle", "DEV_NEEDLE"),
    ("forceps", "DEV_INSTRUMENT"),
    ("brush", "DEV_INSTRUMENT"),
    ("fluoroscopic", "PROC_METHOD"),
    ("forceps", "DEV_INSTRUMENT"),
    ("cell-block", "SPECIMEN"),
    ("mini-BAL", "PROC_ACTION"),
]

# =============================================================================
# SETUP
# =============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# PROCESSING
# =============================================================================

def update_pipeline():
    print(f"Processing note: {NOTE_ID}...")
    
    # 1. Calculate Offsets
    entities = []
    search_cursor = 0
    
    # Iterate through candidates and find them in the raw text relative to the last find
    # This simple logic assumes the candidates list is ordered by appearance in text.
    # If the candidate list isn't strictly ordered, we scan from 0 for each, but we must avoid overlapping logic if needed.
    # Given the nature of this task, we will scan from the beginning for every entity to find the correct instance, 
    # but we need to handle duplicates (like "LEFT UPPER LOBE").
    
    # Refined Strategy: Find all occurrences of each specific string and map them.
    # Since manual labeling usually implies context, we will iterate the text and match the list provided sequentially.
    # However, to ensure robustness in this script without manual indices, we will use a cursor.
    
    text_lower = RAW_TEXT.lower()
    
    # Re-ordering candidates to match text flow for cursor-based extraction
    # This ensures we pick up the specific mentions in order.
    ordered_candidates = [
        ("LEFT UPPER LOBE", "ANAT_LUNG_LOC"),
        ("PULMONARY NODULE", "OBS_LESION"),
        ("LEFT UPPER LOBE", "ANAT_LUNG_LOC"),
        ("PULMONARY NODULE", "OBS_LESION"),
        ("Flexible bronchoscopy", "PROC_ACTION"),
        ("electromagnetic navigation", "PROC_METHOD"),
        ("flouroscopic", "PROC_METHOD"),
        ("EBUS", "PROC_METHOD"),
        ("transbronchial needle aspiration", "PROC_ACTION"),
        ("Transbronchial biopsy", "PROC_ACTION"),
        ("bronchioalveolar lavage", "PROC_ACTION"),
        # Skipping CPT code descriptions usually, but if needed, they are in the text
        ("Endobronchial Ultrasound", "PROC_METHOD"),
        ("fluoroscopic", "PROC_METHOD"),
        ("transbronchial lung biopsy(s)", "PROC_ACTION"),
        ("bronchial alveolar lavage", "PROC_ACTION"),
        ("computer assisted image guided navigation", "PROC_METHOD"),
        ("Left upper lobe", "ANAT_LUNG_LOC"),
        ("lung nodule", "OBS_LESION"),
        ("GA", "MEDICATION"),
        ("tracheobronchial tree", "ANAT_AIRWAY"),
        ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
        ("tracheobronchial tree", "ANAT_AIRWAY"),
        ("trachea", "ANAT_AIRWAY"),
        ("carina", "ANAT_AIRWAY"),
        ("tracheobronchial tree", "ANAT_AIRWAY"),
        ("Q190 bronchoscope", "DEV_INSTRUMENT"),
        ("apico-posterior branch of left upper lobe", "ANAT_LUNG_LOC"),
        ("Radial probe", "DEV_INSTRUMENT"),
        ("radial probe", "DEV_INSTRUMENT"),
        ("Biopsy", "PROC_ACTION"),
        ("triple needle brush", "DEV_INSTRUMENT"),
        ("TBNA needle", "DEV_NEEDLE"),
        ("ROSE", "OBS_ROSE"), # Added based on review of text
        ("biopsies", "PROC_ACTION"),
        ("peripheral needle", "DEV_NEEDLE"),
        ("forceps", "DEV_INSTRUMENT"),
        ("brush", "DEV_INSTRUMENT"),
        ("fluoroscopic", "PROC_METHOD"),
        ("forceps biopsies", "PROC_ACTION"),
        ("cell-block", "SPECIMEN"),
        ("mini-BAL", "PROC_ACTION"),
        ("bronchoscopy", "PROC_ACTION"), # In impression
        ("biopsy", "PROC_ACTION"), # In impression
        ("lavage", "PROC_ACTION") # In impression
    ]

    found_entities = []
    
    current_pos = 0
    for text_to_find, label in ordered_candidates:
        # Find next occurrence starting from current_pos
        start_idx = RAW_TEXT.find(text_to_find, current_pos)
        
        if start_idx != -1:
            end_idx = start_idx + len(text_to_find)
            
            # Validation: Ensure strict matching
            extracted = RAW_TEXT[start_idx:end_idx]
            if extracted != text_to_find:
                 with open(LOG_FILE, "a") as log:
                    log.write(f"[{datetime.datetime.now()}] Mismatch: {text_to_find} vs {extracted}\n")
            
            entity_obj = {
                "label": label,
                "start": start_idx,
                "end": end_idx,
                "text": text_to_find
            }
            found_entities.append(entity_obj)
            
            # Move cursor past this entity to find the next one
            # We don't necessarily update current_pos to end_idx for EVERYTHING, 
            # because sometimes we might want to capture overlapping nested entities,
            # but for this specific linear list, we update to avoid re-finding the same instance.
            current_pos = end_idx
        else:
            with open(LOG_FILE, "a") as log:
                log.write(f"[{datetime.datetime.now()}] Entity not found in sequential search: '{text_to_find}'\n")

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in found_entities]
    }
    
    with open(NER_FILE, "a") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(NOTES_FILE, "a") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 4. Update spans.jsonl
    with open(SPANS_FILE, "a") as f:
        for e in found_entities:
            span_entry = {
                "span_id": f"{e['label']}_{e['start']}",
                "note_id": NOTE_ID,
                "label": e["label"],
                "text": e["text"],
                "start": e["start"],
                "end": e["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

    # 5. Update stats.json
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
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
    stats["total_files"] += 1 # Assuming 1 note = 1 file context here
    stats["total_spans_raw"] += len(found_entities)
    stats["total_spans_valid"] += len(found_entities)

    for e in found_entities:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {len(found_entities)} entities for {NOTE_ID}.")

if __name__ == "__main__":
    update_pipeline()