from pathlib import Path
import json
import os
import datetime

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
NOTE_ID = "note_170"
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Raw text content of the note
RAW_TEXT = """Indications: right lower lobe nodule 
Medications: Propofol infusion via anesthesia assistance  
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. A polyp wasseen on the left vocal cord.
The subglottic space was normal. The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. We then removed the diagnostic Q190 bronchoscopy and the super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using navigational map we attempted to advance the 180 degree edge catheter into the proximity of the lesion within the right lower lobe.
Confirmation of placement once at the point of interest with radial ultrasound showed a concentric view within the lesion.
Biopsies were then performed with a variety of instruments to include peripheral needle, brush, triple needle brush and forceps, under fluoroscopic visualization.
After adequate samples were obtained the bronchoscope was removed and the procedure completed
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Flexible bronchoscopy with successful navigational biopsy of right lower lobe nodule.
-Vocal Cord polyp
Recommendations
- Await final pathology
- ENT consultation for eval of vocal cord polyp"""

# -------------------------------------------------------------------------
# ENTITY EXTRACTION & MAPPING
# -------------------------------------------------------------------------
# List of entities to find. 
# Format: (Text_Snippet, Label, Occurrence_Index)
# Occurrence_Index: 0 for first match, 1 for second, etc.
target_entities = [
    ("right lower lobe", "ANAT_LUNG_LOC", 0),
    ("nodule", "OBS_LESION", 0),
    ("Propofol", "MEDICATION", 0),
    ("upper airway", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 0),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 1),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 1),
    ("polyp", "OBS_LESION", 0),
    ("left", "LATERALITY", 0),
    ("vocal cord", "ANAT_AIRWAY", 0),
    ("subglottic space", "ANAT_AIRWAY", 0),
    ("trachea", "ANAT_AIRWAY", 0),
    ("carina", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 2),
    ("Bronchial mucosa", "ANAT_AIRWAY", 0),
    ("endobronchial", "ANAT_AIRWAY", 0),
    ("lesions", "OBS_LESION", 0),
    ("super-dimension", "PROC_METHOD", 0),
    ("navigational catheter", "DEV_INSTRUMENT", 0),
    ("airway", "ANAT_AIRWAY", 4), # "into the airway." (after "upper airway", "tracheobronchial" x2, "laryngeal mask airway" x2... wait. 'airway' substring counts)
    ("navigational map", "PROC_METHOD", 0),
    ("180 degree edge catheter", "DEV_INSTRUMENT", 0),
    ("lesion", "OBS_LESION", 1), # "proximity of the lesion"
    ("right lower lobe", "ANAT_LUNG_LOC", 1),
    ("radial ultrasound", "PROC_METHOD", 0),
    ("lesion", "OBS_LESION", 2), # "within the lesion"
    ("Biopsies", "PROC_ACTION", 0),
    ("peripheral needle", "DEV_INSTRUMENT", 0),
    ("brush", "DEV_INSTRUMENT", 0),
    ("triple needle brush", "DEV_INSTRUMENT", 0),
    ("forceps", "DEV_INSTRUMENT", 0),
    ("fluoroscopic", "PROC_METHOD", 0),
    ("Flexible bronchoscopy", "PROC_METHOD", 0),
    ("navigational", "PROC_METHOD", 2), # 0 is in 'navigational catheter', 1 is in 'navigational map', 2 is 'navigational biopsy'
    ("biopsy", "PROC_ACTION", 0),
    ("right lower lobe", "ANAT_LUNG_LOC", 2),
    ("nodule", "OBS_LESION", 1),
    ("Vocal Cord", "ANAT_AIRWAY", 0), # capitalized
    ("polyp", "OBS_LESION", 1),
    ("vocal cord", "ANAT_AIRWAY", 1), # lower case end
    ("polyp", "OBS_LESION", 2)
]

# Helper to locate entities with precise offsets
def find_entity_spans(text, entities_config):
    spans = []
    # Track used indices to handle multiple occurrences
    # Mapping: text_snippet -> list of start_indices found so far
    occurrence_tracker = {} 
    
    # Pre-calculate all start indices for every unique string
    all_occurrences = {}
    
    # Sort config to ensure we process systematically, though logic below is robust
    for text_snip, label, occurrence_idx in entities_config:
        if text_snip not in all_occurrences:
            starts = []
            current_idx = 0
            while True:
                idx = text.find(text_snip, current_idx)
                if idx == -1:
                    break
                starts.append(idx)
                current_idx = idx + 1
            all_occurrences[text_snip] = starts
        
        if occurrence_idx < len(all_occurrences[text_snip]):
            start = all_occurrences[text_snip][occurrence_idx]
            end = start + len(text_snip)
            
            # Special check for "airway" distinct from "upper airway" etc if needed
            # For this specific note, simple find is risky for "airway" 
            # because "airway" is inside "upper airway". 
            # We must verify exact context for generic words if they overlap.
            # However, looking at the list, I used index 4 for "airway".
            # Occurrences of "airway":
            # 1. "upper airway"
            # 2. "laryngeal mask airway"
            # 3. "laryngeal mask airway"
            # 4. "into the airway" (index 945 approx) -> This is the one we want.
            
            span = {
                "span_id": f"{label}_{start}",
                "note_id": NOTE_ID,
                "label": label,
                "text": text_snip,
                "start": start,
                "end": end
            }
            spans.append(span)
        else:
            print(f"Warning: Occurrence {occurrence_idx} not found for '{text_snip}'")
            
    return sorted(spans, key=lambda x: x['start'])

# Execute extraction
extracted_spans = find_entity_spans(RAW_TEXT, target_entities)

# -------------------------------------------------------------------------
# FILE UPDATES
# -------------------------------------------------------------------------

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {"label": s["label"], "start_offset": s["start"], "end_offset": s["end"]} 
        for s in extracted_spans
    ]
}

with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
notes_entry = {"id": NOTE_ID, "text": RAW_TEXT}
with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# 3. Update spans.jsonl
with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
    for span in extracted_spans:
        f.write(json.dumps(span) + "\n")

# 4. Update stats.json
stats_path = OUTPUT_DIR / "stats.json"
if stats_path.exists():
    with open(stats_path, "r", encoding="utf-8") as f:
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
stats["total_spans_raw"] += len(extracted_spans)
stats["total_spans_valid"] += len(extracted_spans)

for span in extracted_spans:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# 5. Validation Logging
log_path = OUTPUT_DIR / "alignment_warnings.log"
with open(log_path, "a", encoding="utf-8") as log:
    for span in extracted_spans:
        text_slice = RAW_TEXT[span["start"]:span["end"]]
        if text_slice != span["text"]:
            log.write(f"MISMATCH {NOTE_ID}: Span '{span['text']}' != Text '{text_slice}' at {span['start']}\n")

print(f"Successfully processed {NOTE_ID} with {len(extracted_spans)} entities.")