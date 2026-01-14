import json
import re
from pathlib import Path

# ==========================================
# 1. Configuration & Input Data
# ==========================================
NOTE_ID = "note_207"

# Raw text content from the provided file
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: Metastatic squamous cell carcinoma (head and neck) 
POSTOPERATIVE DIAGNOSIS: 
Malignant obstruction of Right middle lobe, right lower lobe, and left mainstem.
PROCEDURE PERFORMED: Rigid bronchoscopy with tumor debulking (APC and cryodebulking) 
INDICATIONS: multilobar tumor obstruction.
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The trachea was normal with the exception of some small tumor infiltration which was non-obstructive in the left lateral gutter approximately 4cm above the main carina.
On the right the mainstem and right upper lobe were normal without endobronchial disease.
There was tumor on the posterior wall of the bronchus intermedius causing about 25% obstruction.
The right middle lobe was completely obstructed by endobronchial tumor.
The right lower lobe orifice was completely obstructed by endobronchial tumor as well.
On the left there was extensive tumor within the mainstem beginning just after the main carina causing about 80-85% obstruction with tumor extending to approximately 2 cm proximal to the LC1 carina.
Within the left upper lobe and left lower lobe there is no evidence of endobronchial tumor and the airways were normal.
After inspection the flexible bronchoscope was removed and the patient was given paralytics by anesthesia after which a 12 mm ventilating rigid bronchoscope was easily passed into the airway and advanced to the distal trachea and then attached to the ventilator.
Initially biopsies were taken from the distal trachea just proximal to the left mainstem and the right lower lobe and tissue was given to clinical trial team and also collected for pathological review.
We began debulking the tumor in the right middle lobe.
APC was used to de-vascularize the superficial layer and cryotherapy, forceps were used to slowly debulk the lesion.
WE were eventually able to open up the airway to where we could see the medial and lateral segments and copious post-obstructive pus was expressed and suctioned with specimen collected for culture.
Tumor continued deep into the subsegmental bronchi and we could only achieve about 40% recanalization.
We then moved to right lower lobe and debulked in a similar fashion.
We were able to get slightly better recanalization in this lobe but could only achieve approximatly 60% recanalization.
Like in the middle lobe tumor extended distally into the subsegments.
The tumor at in the bronchus intermedius was then debulked with APC using the “burn and shave” technique with complete recanalization.
We then moved to the left mainstem and again using a similar technique with APC and forceps were able to achieve about 80% recanalization.
APC was used at the end of the procedure to paint and cauterize any active oozing and once we were satisfied that no further intervention was required and that there was no evidence of active bleeding the flexible bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
Recommendations:
-	Transfer patient PACU
-	Follow-up PRN if return of symptoms
-	Treatment of metastatic foci per oncology"""

# Targeted Entities (Label, Text Snippet)
# Order matters: this list preserves the order of appearance in the text to allow linear scanning.
ENTITIES_TO_FIND = [
    # Header info
    ("OBS_LESION", "Metastatic squamous cell carcinoma"),
    ("OBS_LESION", "Malignant obstruction"),
    ("ANAT_LUNG_LOC", "Right middle lobe"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("ANAT_AIRWAY", "left mainstem"),
    
    # Procedure Performed
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("PROC_ACTION", "tumor debulking"),
    ("PROC_METHOD", "APC"),
    ("PROC_ACTION", "cryodebulking"),
    ("OBS_LESION", "tumor"), # in indications
    ("OBS_FINDING", "obstruction"),
    
    # Description
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    
    # Findings - Trachea
    ("ANAT_AIRWAY", "trachea"),
    ("OBS_LESION", "tumor infiltration"),
    ("ANAT_AIRWAY", "main carina"),
    
    # Findings - Right
    ("LATERALITY", "right"),
    ("ANAT_AIRWAY", "mainstem"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("OBS_LESION", "endobronchial disease"),
    
    # Findings - BI
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "bronchus intermedius"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "25% obstruction"),
    
    # Findings - RML
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely obstructed"),
    ("OBS_LESION", "endobronchial tumor"),
    
    # Findings - RLL
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely obstructed"),
    ("OBS_LESION", "endobronchial tumor"),
    
    # Findings - Left
    ("LATERALITY", "left"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "mainstem"),
    ("ANAT_AIRWAY", "main carina"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "80-85% obstruction"),
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "LC1 carina"),
    
    # Findings - LUL/LLL
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_LESION", "endobronchial tumor"),
    
    # Procedure steps
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("ANAT_AIRWAY", "distal trachea"),
    
    ("PROC_ACTION", "biopsies"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("SPECIMEN", "tissue"),
    
    ("PROC_ACTION", "debulking"),
    ("OBS_LESION", "tumor"),
    ("ANAT_LUNG_LOC", "right middle lobe"),
    
    ("PROC_METHOD", "APC"),
    ("PROC_METHOD", "cryotherapy"),
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "debulk"),
    ("OBS_LESION", "lesion"),
    
    ("SPECIMEN", "pus"),
    
    ("OBS_LESION", "Tumor"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "40% recanalization"),
    
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("PROC_ACTION", "debulked"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "60% recanalization"),
    
    ("OBS_LESION", "tumor"), # "tumor extended"
    
    ("OBS_LESION", "tumor"),
    ("ANAT_AIRWAY", "bronchus intermedius"),
    ("PROC_ACTION", "debulked"),
    ("PROC_METHOD", "APC"),
    ("PROC_METHOD", "burn and shave"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "complete recanalization"),
    
    ("ANAT_AIRWAY", "left mainstem"),
    ("PROC_METHOD", "APC"),
    ("DEV_INSTRUMENT", "forceps"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "80% recanalization"),
    
    ("PROC_METHOD", "APC"),
    ("PROC_ACTION", "cauterize"),
    ("DEV_INSTRUMENT", "flexible bronchoscope")
]

# ==========================================
# 2. Setup Paths
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 3. Processing Logic
# ==========================================

def extract_entities(text, entity_list):
    """
    Finds entities in text linearly to handle duplicates correctly.
    """
    results = []
    current_idx = 0
    
    for label, substr in entity_list:
        # Find next occurrence of substring starting from current_idx
        # Case insensitive match for robustness, though we use exact text in list
        start = text.find(substr, current_idx)
        
        if start == -1:
            # Fallback: simple search from 0 if linear assumption fails due to typos in list,
            # but log warning. For this script, we assume strict linear order in ENTITIES_TO_FIND.
            print(f"WARNING: Could not find '{substr}' after index {current_idx}")
            continue
            
        end = start + len(substr)
        
        results.append({
            "label": label,
            "text": substr,
            "start": start,
            "end": end
        })
        
        # Move cursor forward
        current_idx = start + 1 
        
    return results

def update_stats(stats_path, new_entities):
    """Updates the stats.json file."""
    if stats_path.exists():
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(new_entities)
    stats["total_spans_valid"] += len(new_entities)

    for entity in new_entities:
        lbl = entity["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Extract Entities
    entities = extract_entities(RAW_TEXT, ENTITIES_TO_FIND)
    
    # 2. Prepare Data Objects
    
    # ner_dataset_all.jsonl entry
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": f"{e['label']}_{e['start']}",
                "label": e['label'],
                "start_offset": e['start'],
                "end_offset": e['end']
            }
            for e in entities
        ]
    }
    
    # notes.jsonl entry
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # spans.jsonl entries
    span_entries = []
    for e in entities:
        span_entries.append({
            "span_id": f"{e['label']}_{e['start']}",
            "note_id": NOTE_ID,
            "label": e['label'],
            "text": e['text'],
            "start": e['start'],
            "end": e['end']
        })

    # 3. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Append to notes.jsonl
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Append to spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for span in span_entries:
            f.write(json.dumps(span) + "\n")
            
    # Update stats
    update_stats(STATS_PATH, entities)
    
    # 4. Validation
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        for e in entities:
            extracted_text = RAW_TEXT[e['start']:e['end']]
            if extracted_text != e['text']:
                log.write(f"MISMATCH {NOTE_ID}: Exp '{e['text']}' Got '{extracted_text}' at {e['start']}\n")

    print(f"Successfully processed {NOTE_ID}. Added {len(entities)} entities.")

if __name__ == "__main__":
    main()