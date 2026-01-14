import json
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_160"
NOTE_FILENAME = "note_160.txt"

# Raw text content derived from the provided file (source markers removed)
RAW_TEXT = """Procedure Name: 
1. Electromagnetic navigation bronchoscopy
Indications: Pulmonary Nodule
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The arytenoids were large with a large and floppy epiglottis. The vocal cords appeared normal. The subglottic space was normal.
Tracheomalacia was noted as we advanced the scope to the carina. The carina was sharp.
The right and left sided airway anatomy was normal. No evidence of endobronchial disease was seen to at least the first sub-segments.
We then removed the bronchoscope and inserted the EBUS bronchoscope into the airway.
We attempted to visualize the nodule with endobronchial ultrasound but did not see the nodule with ultrasound.
We then inserted the therapeutic bronchoscope for electromagnetic navigation bronchoscopy.
We were not able to get to the nodule using the navigation equipment.
After suctioning blood and secretions and once we were confident that there was no active bleeding the bronchoscope was removed and the procedure completed.
Complications: None.
Estimated Blood Loss: Less than 10 cc.  No specimens were obtained for path review.
Post Procedure Diagnosis:
- Discuss his case at cardiothoracic tumor board next Tuesday to determine best next step in workup"""

# Target Entities to Extract (based on Label_guide_UPDATED.csv)
# Format: (Text, Label, Optional: specific occurrence index or context hint)
TARGETS = [
    ("Electromagnetic navigation bronchoscopy", "PROC_METHOD"),
    ("Pulmonary Nodule", "OBS_LESION"),
    ("Propofol", "MEDICATION"),
    ("upper airway", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("arytenoids", "ANAT_AIRWAY"),
    ("epiglottis", "ANAT_AIRWAY"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("Tracheomalacia", "OBS_FINDING"),
    ("carina", "ANAT_AIRWAY"),
    ("right", "LATERALITY"),
    ("left", "LATERALITY"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("EBUS bronchoscope", "DEV_INSTRUMENT"),
    ("nodule", "OBS_LESION"),
    ("endobronchial ultrasound", "PROC_METHOD"),
    ("ultrasound", "PROC_METHOD"),
    ("therapeutic bronchoscope", "DEV_INSTRUMENT"),
    ("electromagnetic navigation bronchoscopy", "PROC_METHOD"),
    ("navigation equipment", "DEV_INSTRUMENT"),
    ("blood", "OBS_FINDING"),
    ("secretions", "OBS_FINDING"),
    ("None", "OUTCOME_COMPLICATION"),
    ("10 cc", "MEAS_VOL")
]

# ==========================================
# PATH SETUP
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
# PROCESSING LOGIC
# ==========================================

def get_spans(text, targets):
    """
    Finds entity spans in text. Handles multiple occurrences by strictly finding
    the next occurrence after the previous one to maintain order if possible,
    or using regex to find all.
    """
    spans = []
    found_offsets = set()
    
    for target_text, label in targets:
        # Simple exact match search; finding all instances and selecting the correct one 
        # requires context, but here we will greedily match to simulate annotation.
        # To avoid overlapping sub-matches (e.g. "bronchoscope" inside "video bronchoscope"),
        # we check existing coverage.
        
        matches = [m for m in re.finditer(re.escape(target_text), text)]
        
        for match in matches:
            start, end = match.span()
            # Check for overlap with existing valid spans
            if any(start < existing_end and end > existing_start for existing_start, existing_end in found_offsets):
                continue
            
            # Additional Context Filtering for generic terms
            context_pre = text[max(0, start-20):start]
            context_post = text[end:min(len(text), end+20)]
            
            # "None" validation: strictly for Complications
            if target_text == "None" and "Complications:" not in context_pre:
                continue

            # "right"/"left" validation: ensure it refers to anatomy (simple heuristic)
            if label == "LATERALITY" and "sided" not in context_post and "airway" not in context_post:
                # In this note: "right and left sided airway..." -> matches.
                pass 
                
            spans.append({
                "span_id": f"{label}_{start}",
                "note_id": NOTE_ID,
                "label": label,
                "text": target_text,
                "start": start,
                "end": end
            })
            found_offsets.add((start, end))
            
    return sorted(spans, key=lambda x: x['start'])

def update_files():
    # 1. Generate Spans
    entities = get_spans(RAW_TEXT, TARGETS)
    
    # 2. JSONL Formatting
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # 3. Write to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + '\n')
        
    # 4. Write to notes.jsonl
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + '\n')
        
    # 5. Write to spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for entity in entities:
            f.write(json.dumps(entity) + '\n')
            
    # 6. Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        # Fallback initialization if file missing
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0, 
            "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}
        }
        
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    for entity in entities:
        lbl = entity["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
        
    # 7. Alignment Check
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        for entity in entities:
            extracted = RAW_TEXT[entity["start"]:entity["end"]]
            if extracted != entity["text"]:
                log.write(f"MISMATCH: {NOTE_ID} - Exp: {entity['text']} vs Act: {extracted}\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    update_files()