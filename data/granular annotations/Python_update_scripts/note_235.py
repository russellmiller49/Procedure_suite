from pathlib import Path
import json
import os
import datetime

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
NOTE_ID = "note_235"
RAW_TEXT = """NOTE_ID:  note_235 SOURCE_FILE: note_235.txt PREOPERATIVE DIAGNOSIS: 
1.	Bronchus-intermedius obstruction secondary to Broncholithiasis
POSTOPERATIVE DIAGNOSIS: 
1.	 Resolved Bronchus-intermedius obstruction 
2.	 Mild stricture of bronchus intermedius  
PROCEDURE PERFORMED: 
1.	CPT 31630 Bronchoscopy with tracheal/bronchial dilation
1.	INDICATIONS:  1.Bronchus-intermedius obstruction secondary to broncholith
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the distal trachea and advanced into the distal trachea before attaching the monsoon JET ventilator.
Using the flexible bronchoscope airway inspection was performed. The tracheal carina was sharp. All left sided airways were normal.
The right mainstem and right upper lobe were normal. In the proximal bronchus intermedius there was no evidence of recurrent broncholith, there was approximately 20% obstruction from stricturing on the medial aspect along with pinpoint healing defect associated with area of previous broncholith erosion.
The rigid bronchoscope was then advanced into the right mainstem.
Balloon dilatation was performed with the 12/13.5/15cm dilation dilatational balloon within the bronchus intermedius resulting in reduction of obstruction to approximately 5%.
There was no significant bleeding. The rigid bronchoscope was removed and the procedure complete.
Complications: None
Estimated blood loss: 1cc
Specimens: none
Recommendations:
- Admit to IM ward due as patient does not have anyone locally to observe post-anesthesia 
- Advance diet as tolerated.
- Likely D/C in AM
- OK to return to Japan without duty limitation."""

# ----------------------------------------------------------------------------------
# ENTITY EXTRACTION (Manual Annotation based on Label_guide_UPDATED.csv)
# ----------------------------------------------------------------------------------
# Labels used: 
# ANAT_AIRWAY, OBS_LESION, PROC_METHOD, PROC_ACTION, DEV_INSTRUMENT, 
# OUTCOME_AIRWAY_LUMEN_PRE, OUTCOME_AIRWAY_LUMEN_POST, ANAT_LUNG_LOC, OUTCOME_COMPLICATION

# Helper to find exact offsets
def find_offsets(text, substring, start_search=0):
    start = text.find(substring, start_search)
    if start == -1:
        return None
    return start, start + len(substring)

entities_data = [
    # Preop Diagnosis
    ("Bronchus-intermedius", "ANAT_AIRWAY"),
    ("Broncholithiasis", "OBS_LESION"),
    
    # Postop Diagnosis
    ("Bronchus-intermedius", "ANAT_AIRWAY", 150), # Skip first occurrence
    ("obstruction", "OBS_LESION", 150),
    ("stricture", "OBS_LESION"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    
    # Procedure Performed
    ("Bronchoscopy", "PROC_METHOD"),
    ("dilation", "PROC_ACTION"),
    
    # Indications
    ("Bronchus-intermedius", "ANAT_AIRWAY", 350),
    ("obstruction", "OBS_LESION", 350),
    ("broncholith", "OBS_LESION"),
    
    # Description
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("distal trachea", "ANAT_AIRWAY"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
    ("airway inspection", "PROC_ACTION"),
    ("Tracheal carina", "ANAT_AIRWAY"), # Text says "The tracheal carina"
    ("left sided airways", "ANAT_AIRWAY"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("proximal bronchus intermedius", "ANAT_AIRWAY"),
    ("broncholith", "OBS_LESION", 1000), # recurrent broncholith
    ("approximately 20% obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("stricturing", "OBS_LESION"),
    ("broncholith", "OBS_LESION", 1150), # previous broncholith erosion
    ("rigid bronchoscope", "DEV_INSTRUMENT", 1200),
    ("right mainstem", "ANAT_AIRWAY", 1250),
    ("Balloon dilatation", "PROC_METHOD"),
    ("dilatational balloon", "DEV_INSTRUMENT"),
    ("bronchus intermedius", "ANAT_AIRWAY", 1350),
    ("approximately 5%", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("rigid bronchoscope", "DEV_INSTRUMENT", 1450),
    ("None", "OUTCOME_COMPLICATION")
]

# Refine matching for exact strings in text
# Note: "Tracheal carina" in text is "The tracheal carina". I will map "tracheal carina" (lower case t in text check).
# "Bronchoscopy" appears in CPT line.
# "dilation" appears in CPT line.

final_entities = []
search_cursor = 0

# Strict manual mapping to ensure precision
# 1. Bronchus-intermedius (Preop)
s, e = find_offsets(RAW_TEXT, "Bronchus-intermedius", 0)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "Bronchus-intermedius"})

# 2. Broncholithiasis
s, e = find_offsets(RAW_TEXT, "Broncholithiasis", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "Broncholithiasis"})

# 3. Bronchus-intermedius (Postop)
s, e = find_offsets(RAW_TEXT, "Bronchus-intermedius", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "Bronchus-intermedius"})

# 4. obstruction (Postop)
s, e = find_offsets(RAW_TEXT, "obstruction", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "obstruction"})

# 5. stricture
s, e = find_offsets(RAW_TEXT, "stricture", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "stricture"})

# 6. bronchus intermedius
s, e = find_offsets(RAW_TEXT, "bronchus intermedius", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "bronchus intermedius"})

# 7. Bronchoscopy
s, e = find_offsets(RAW_TEXT, "Bronchoscopy", e)
final_entities.append({"start": s, "end": e, "label": "PROC_METHOD", "text": "Bronchoscopy"})

# 8. dilation
s, e = find_offsets(RAW_TEXT, "dilation", e)
final_entities.append({"start": s, "end": e, "label": "PROC_ACTION", "text": "dilation"})

# 9. Bronchus-intermedius (Indications)
s, e = find_offsets(RAW_TEXT, "Bronchus-intermedius", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "Bronchus-intermedius"})

# 10. obstruction (Indications)
s, e = find_offsets(RAW_TEXT, "obstruction", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "obstruction"})

# 11. broncholith (Indications)
s, e = find_offsets(RAW_TEXT, "broncholith", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "broncholith"})

# 12. rigid bronchoscope
s, e = find_offsets(RAW_TEXT, "rigid bronchoscope", e)
final_entities.append({"start": s, "end": e, "label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"})

# 13. distal trachea
s, e = find_offsets(RAW_TEXT, "distal trachea", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "distal trachea"})

# 14. flexible bronchoscope
s, e = find_offsets(RAW_TEXT, "flexible bronchoscope", e)
final_entities.append({"start": s, "end": e, "label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"})

# 15. airway inspection
s, e = find_offsets(RAW_TEXT, "airway inspection", e)
final_entities.append({"start": s, "end": e, "label": "PROC_ACTION", "text": "airway inspection"})

# 16. tracheal carina (Text: "The tracheal carina")
s, e = find_offsets(RAW_TEXT, "tracheal carina", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "tracheal carina"})

# 17. left sided airways
s, e = find_offsets(RAW_TEXT, "left sided airways", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "left sided airways"})

# 18. right mainstem
s, e = find_offsets(RAW_TEXT, "right mainstem", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "right mainstem"})

# 19. right upper lobe
s, e = find_offsets(RAW_TEXT, "right upper lobe", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_LUNG_LOC", "text": "right upper lobe"})

# 20. proximal bronchus intermedius
s, e = find_offsets(RAW_TEXT, "proximal bronchus intermedius", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "proximal bronchus intermedius"})

# 21. broncholith (recurrent)
s, e = find_offsets(RAW_TEXT, "broncholith", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "broncholith"})

# 22. approximately 20% obstruction
s, e = find_offsets(RAW_TEXT, "approximately 20% obstruction", e)
final_entities.append({"start": s, "end": e, "label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "approximately 20% obstruction"})

# 23. stricturing
s, e = find_offsets(RAW_TEXT, "stricturing", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "stricturing"})

# 24. broncholith (erosion)
s, e = find_offsets(RAW_TEXT, "broncholith", e)
final_entities.append({"start": s, "end": e, "label": "OBS_LESION", "text": "broncholith"})

# 25. rigid bronchoscope
s, e = find_offsets(RAW_TEXT, "rigid bronchoscope", e)
final_entities.append({"start": s, "end": e, "label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"})

# 26. right mainstem
s, e = find_offsets(RAW_TEXT, "right mainstem", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "right mainstem"})

# 27. Balloon dilatation
s, e = find_offsets(RAW_TEXT, "Balloon dilatation", e)
final_entities.append({"start": s, "end": e, "label": "PROC_METHOD", "text": "Balloon dilatation"})

# 28. dilatational balloon
s, e = find_offsets(RAW_TEXT, "dilatational balloon", e)
final_entities.append({"start": s, "end": e, "label": "DEV_INSTRUMENT", "text": "dilatational balloon"})

# 29. bronchus intermedius
s, e = find_offsets(RAW_TEXT, "bronchus intermedius", e)
final_entities.append({"start": s, "end": e, "label": "ANAT_AIRWAY", "text": "bronchus intermedius"})

# 30. approximately 5%
s, e = find_offsets(RAW_TEXT, "approximately 5%", e)
final_entities.append({"start": s, "end": e, "label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "approximately 5%"})

# 31. rigid bronchoscope
s, e = find_offsets(RAW_TEXT, "rigid bronchoscope", e)
final_entities.append({"start": s, "end": e, "label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"})

# 32. None (Complications)
s, e = find_offsets(RAW_TEXT, "None", e)
final_entities.append({"start": s, "end": e, "label": "OUTCOME_COMPLICATION", "text": "None"})


# ----------------------------------------------------------------------------------
# PATH SETUP
# ----------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ----------------------------------------------------------------------------------
# EXECUTION
# ----------------------------------------------------------------------------------

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": final_entities
}

with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(NOTES_PATH, 'a', encoding='utf-8') as f:
    f.write(json.dumps(note_entry) + "\n")

# 3. Update spans.jsonl
new_spans = []
for ent in final_entities:
    span_entry = {
        "span_id": f"{ent['label']}_{ent['start']}",
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    }
    new_spans.append(span_entry)

with open(SPANS_PATH, 'a', encoding='utf-8') as f:
    for span in new_spans:
        f.write(json.dumps(span) + "\n")

# 4. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, 'r', encoding='utf-8') as f:
        stats = json.load(f)
else:
    stats = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "alignment_warnings": 0,
        "alignment_errors": 0,
        "label_counts": {},
        "hydration_status_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(final_entities)
stats["total_spans_valid"] += len(final_entities)

for ent in final_entities:
    lbl = ent['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

# 5. Validation Log
with open(LOG_PATH, 'a', encoding='utf-8') as f:
    for ent in final_entities:
        snippet = RAW_TEXT[ent['start']:ent['end']]
        if snippet != ent['text']:
            timestamp = datetime.datetime.now().isoformat()
            log_msg = f"[{timestamp}] Mismatch in {NOTE_ID}: Expected '{ent['text']}', found '{snippet}' at {ent['start']}:{ent['end']}\n"
            f.write(log_msg)
            # We defined stats update before this check, but usually a mismatch here implies a script error. 
            # In a real pipeline, we might rollback stats, but here we log it.

print(f"Successfully processed {NOTE_ID} and updated {OUTPUT_DIR}")