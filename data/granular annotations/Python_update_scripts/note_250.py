import json
import os
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_250"
TIMESTAMP = datetime.datetime.now().isoformat()

# Raw text content from note_250.txt
# Note: Preserving original whitespace and typos (e.g., "dubulking") is critical for offset accuracy.
TEXT = """PREOPERATIVE DIAGNOSIS: Endoluminal right mainstem obstruction secondary to presumed RCC.
POSTOPERATIVE DIAGNOSIS: Tumor obstruction of the bronchus intermedius 
PROCEDURE PERFORMED: Rigid bronchoscopy with endobronchial dubulking
INDICATIONS: Tumor obstruction of right mainstem with complete lung collapse  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following induction and paralyitic administration by anesthesia an 11 mm ventilating rigid bronchoscope was inserted into the mid trachea and attached to the ventilator.
The rigid optic was then removed and the flexible bronchoscope was inserted through the rigid bronchoscope.
On initial bronchoscopic inspection the trachea, left lung appeared normal without evidence of endobronchial disease.
In the orifice of the right mainstem, protruding slightly into the supra-carinal space was a large mass causing complete obstruction.
The lesion appeared to have a stock/base and we therefore secured the polypoid lesion using the electrocautery snare.
The lesion was snared and immediately hemorrhaged briskly completely obscuring the field of view.
The rigid bronchoscope was advanced into the right mainstem to attempt to isolate the bleeding however the patient’s oxygen saturation continued to fall and the decision was made to remove the rigid scope and insert an ETT.
This was done by anesthesia using an 8.0 ETT. The patient was placed right side down to protect the left lung and while suctioning blood via a flexible bronchoscope in the ETT.
Vision remained poor and we utilized topical TXA and epi to try to slow the bleeding while using cryotherapy probe to pull blood clots from the airways.
Eventually the bleeding stopped and the patient’s oxygen saturation returned to normal.
Once we were able to better visualize the airways we found that the left side had relatively mild blood spillover and at the LC1 carina the transected tumor was seen which was removed piecemeal using the cryotherapy probe.
Subsequently we began to debulk further into right lung. The right upper lobe was eventually visualized.
We attempted to use APC to "burn and shave" residual airway tumor however patient would quickly desat with drops in FIO2 required to safely use thermal therapies.
We were able to debulk until what was likely the distal aspect of the BI but significant tumor still remained.
Patient had extremely low reserve and since he continued to desaturate limiting our ability to continue debulk we decided to APC the base or the tumor as well as the residual tumor in the airway wall until we were confident that there was no active bleeding and abort attempts to further debulk for now and to consider returning to the OR at a later date.
Once this was accomplished the ETT position was confirmed to be 3cm above the carina.
The bronchoscope was removed and there procedure completed. Decision in consultation with anesthesia was for patient to remain intubated for now and transfer to the ICU.
Specimens: Right mainstem tumor
Fluids/Blood Products:
IVF: 1500  EBL: 200cc  Blood Products: None
 Complications: Severe hemorrhage, severe hypoxia, Escalation in level of care.
Recommendations: 
-	Patient to remain intubated overnight, with endobronchial blocker at bedside.
-	If no bleeding overnight plan to extubate tomorrow.
-	Will need to discuss options moving forward. Given the extent of the tumor risk/benefit ratio of re-attempting debulking needs to be carefully considered along with alternative options such as radiotherapy."""

# Target Entities to Extract
# Format: (Label, Phrase) - duplicates in text will be handled by the extraction logic
TARGETS = [
    ("ANAT_AIRWAY", "right mainstem"),
    ("OBS_LESION", "presumed RCC"),
    ("OBS_LESION", "Tumor"),
    ("ANAT_AIRWAY", "bronchus intermedius"),
    ("PROC_ACTION", "Rigid bronchoscopy"),
    ("PROC_ACTION", "endobronchial dubulking"), # Preserving typo from source
    ("MEAS_SIZE", "11 mm"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "mid trachea"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_LUNG_LOC", "left lung"),
    ("ANAT_AIRWAY", "supra-carinal space"),
    ("OBS_LESION", "large mass"),
    ("OBS_LESION", "polypoid lesion"),
    ("DEV_INSTRUMENT", "electrocautery snare"),
    ("OBS_LESION", "lesion"),
    ("DEV_INSTRUMENT", "rigid scope"),
    ("DEV_INSTRUMENT", "ETT"),
    ("MEAS_SIZE", "8.0"),
    ("MEDICATION", "TXA"),
    ("MEDICATION", "epi"),
    ("DEV_INSTRUMENT", "cryotherapy probe"),
    ("ANAT_AIRWAY", "LC1 carina"),
    ("OBS_LESION", "tumor"),
    ("PROC_ACTION", "debulk"),
    ("ANAT_LUNG_LOC", "right lung"),
    ("ANAT_LUNG_LOC", "Right upper lobe"),
    ("PROC_METHOD", "APC"),
    ("ANAT_AIRWAY", "BI"),
    ("OUTCOME_COMPLICATION", "Severe hemorrhage"),
    ("OUTCOME_COMPLICATION", "severe hypoxia"),
    ("MEAS_VOL", "1500"),
    ("MEAS_VOL", "200cc"),
    ("DEV_INSTRUMENT", "endobronchial blocker"),
    ("OBS_LESION", "Right mainstem tumor")
]

# =============================================================================
# PATH SETUP
# =============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"

# =============================================================================
# PROCESSING LOGIC
# =============================================================================

def find_all_entities(text, targets):
    """
    Finds all occurrences of target phrases in the text.
    Returns a list of unique [start, end, label] lists.
    """
    found_entities = []
    # To prevent overlapping or duplicate processing of same indices for different labels (unlikely here but good practice)
    occupied_indices = set() 
    
    # Sort targets by length (descending) to prioritize longer matches if needed
    # (though in this script we strictly look for listed targets)
    sorted_targets = sorted(targets, key=lambda x: len(x[1]), reverse=True)

    for label, phrase in sorted_targets:
        start = 0
        while True:
            idx = text.find(phrase, start)
            if idx == -1:
                break
            
            end = idx + len(phrase)
            
            # Create a unique key for this span
            span_signature = (idx, end)
            
            # Simple conflict check: if exact span not already recorded with this label
            # We allow the same span to have different labels if logically required, 
            # but usually we want one label per span in NER. 
            # This script allows overlaps if they are strictly different definitions, 
            # but for this specific request, we just append valid finds.
            
            # Check if this exact span+label exists
            if not any(e[0] == idx and e[1] == end and e[2] == label for e in found_entities):
                found_entities.append([idx, end, label])
            
            start = end # Move past this occurrence
            
    # Sort by start index
    found_entities.sort(key=lambda x: x[0])
    return found_entities

def update_files():
    # 1. Extract Entities
    entities = find_all_entities(TEXT, TARGETS)
    
    # 2. Validate Alignment
    with open(ALIGNMENT_LOG_PATH, "a") as log:
        for start, end, label in entities:
            extracted = TEXT[start:end]
            # Verify extracted text aligns with what we searched for (basic sanity check)
            # Since we used .find(), this should be perfect, but useful for logic errors.
            if start < 0 or end > len(TEXT):
                 log.write(f"[{datetime.datetime.now()}] BOUNDS ERROR: {NOTE_ID} {label} ({start},{end})\n")

    # 3. Append to ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": TEXT,
        "entities": entities
    }
    
    with open(NER_DATASET_PATH, "a") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 4. Append to notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": TEXT
    }
    
    with open(NOTES_PATH, "a") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 5. Append to spans.jsonl
    new_spans = []
    for start, end, label in entities:
        span_text = TEXT[start:end]
        span_id = f"{label}_{start}"
        span_obj = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": label,
            "text": span_text,
            "start": start,
            "end": end
        }
        new_spans.append(span_obj)
        
    with open(SPANS_PATH, "a") as f:
        for span in new_spans:
            f.write(json.dumps(span) + "\n")

    # 6. Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, "r") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}
    else:
        stats = {"total_notes": 0, "total_files": 0, "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}}

    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file context here
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    # Update label counts
    for _, _, label in entities:
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(STATS_PATH, "w") as f:
        json.dump(stats, f, indent=4)

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    update_files()