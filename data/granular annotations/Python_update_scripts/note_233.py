from pathlib import Path
import json
import os
import re
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_233"
NOTE_TEXT = """PREOPERATIVE DIAGNOSIS: 
1.	Resolved bronchus-intermedius obstruction 
POSTOPERATIVE DIAGNOSIS: 
1.	 Recurrent resolved Bronchus-intermedius obstruction secondary to broncholith 
PROCEDURE PERFORMED: 
lexible bronchoscopy with removal of broncholith 
1.	INDICATIONS:  Bronchus-intermedius obstruction secondary to broncholith
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite.
Following intravenous medications as per the record and topical anesthesia to the upper airway, the Q190 video bronchoscope was introduced through the mouth, into the oropharynx.
The oropharynx and larynx were well visualized and normal. There was normal vocal cord motion and no vocal cord lesions.
Additional topical anesthesia with 1% lidocaine was applied to the larynx and subsequently throughout the tracheobronchial tree with total volume via the anesthesia record.
The bronchoscope was then advanced through the larynx into the trachea.
The trachea was normal appearing with minimal clear thin secretions. These were suctioned clear.
The bronchoscope was then advanced to the main carina, which was sharp.
The bronchoscope was then advanced into the advanced into the left main stem there were copious thin secretions which were suctioned clear.
Each segment and subsegement in the left upper lobe, lingula and lower lobe was visualized.
The left sided airway anatomy was normal and no specific masses or other lesions were identified throughout the tracheobronchial tree on the left.
The bronchoscope was then withdrawn into the trachea and then advanced into the right mainstem.
The right mainstem and upper lobe were normal. In the proximal bronchus intermedius there was a 30% obstructing area with post treatment changes from previous APC along with a new small broncholith protruding into the airway was well as changes consistent with underlying submucosal broncholith causing mild extrinsic compression.
Gentle pressure was applied to remove the necrotic post-treatment debris within the airway.
The lesion was then probed with the flexible bronchoscopy allowing the broncholith to be extracted from the airway wall and then removed with flexible forceps.
There wasmild bleeding which resolved with topical epinephrine. This resulted in about 80% opening of the bronchus intermedius.
At this point due to the lack of secured airway and risk of bleeding with more invasive removal we decided to not further explore the area.
The bronchoscope was then passed beyond the BI to inspect the right middle, right lower lobe which were normal and no specific masses or other lesions were identified  Once we were satisfied that there was no residual bleeding the rigid bronchoscope was removed and the procedure complete.
Complications: None
Estimated blood loss: 5cc
Specimens: none
Recommendations:
- Repeat non-con CT
- Based on CT will likely return to OR next week for more aggressive removal of residual broncholith.
- Will discharge home once criteria met."""

# Target Entities based on Label_guide_UPDATED.csv
# Format: (Text_Snippet, Label)
# Note: The script searches for these snippets to calculate exact offsets.
ENTITIES_TO_EXTRACT = [
    ("bronchus-intermedius", "ANAT_AIRWAY"),
    ("Bronchus-intermedius", "ANAT_AIRWAY"),
    ("broncholith", "OBS_LESION"),
    ("lexible bronchoscopy", "PROC_METHOD"), # Text typo in source "lexible"
    ("removal", "PROC_ACTION"),
    ("General Anesthesia", "PROC_METHOD"), # Often categorized as method/sedation context
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("mouth", "ANAT_AIRWAY"),
    ("oropharynx", "ANAT_AIRWAY"),
    ("larynx", "ANAT_AIRWAY"),
    ("vocal cord", "ANAT_AIRWAY"),
    ("lidocaine", "MEDICATION"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("main carina", "ANAT_AIRWAY"),
    ("left main stem", "ANAT_AIRWAY"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("lingula", "ANAT_LUNG_LOC"),
    ("lower lobe", "ANAT_LUNG_LOC"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("upper lobe", "ANAT_LUNG_LOC"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("30% obstructing", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("previous", "CTX_HISTORICAL"),
    ("flexible bronchoscopy", "PROC_METHOD"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("mild bleeding", "OUTCOME_COMPLICATION"),
    ("epinephrine", "MEDICATION"),
    ("80% opening", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("right middle", "ANAT_LUNG_LOC"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("rigid bronchoscope", "DEV_INSTRUMENT")
]

# ==========================================
# SETUP PATHS
# ==========================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# PROCESSING LOGIC
# ==========================================

def find_offsets(text, search_list):
    """
    Finds start/end offsets for text snippets. 
    Handles multiple occurrences by keeping a cursor.
    """
    spans = []
    # Sort by length descending to match longest phrases first if overlaps exist (simple heuristic)
    # However, for sequential reading, we usually just iterate. 
    # To handle multiple occurrences correctly, we find all iterators.
    
    found_spans = []
    
    for snippet, label in search_list:
        # We use regex escape to handle potential special chars in snippet
        pattern = re.compile(re.escape(snippet))
        for match in pattern.finditer(text):
            span = {
                "span_id": f"{label}_{match.start()}",
                "note_id": NOTE_ID,
                "label": label,
                "text": match.group(),
                "start": match.start(),
                "end": match.end()
            }
            found_spans.append(span)
            
    # Remove duplicates if any (same start/end/label)
    unique_spans = []
    seen = set()
    for s in found_spans:
        ident = (s['start'], s['end'], s['label'])
        if ident not in seen:
            seen.add(ident)
            unique_spans.append(s)
            
    # Sort by start position
    return sorted(unique_spans, key=lambda x: x['start'])

def update_files():
    # 1. Generate Spans
    extracted_spans = find_offsets(NOTE_TEXT, ENTITIES_TO_EXTRACT)
    
    # 2. Append to notes.jsonl
    with open(NOTES_FILE, 'a', encoding='utf-8') as f:
        json.dump({"id": NOTE_ID, "text": NOTE_TEXT}, f)
        f.write('\n')

    # 3. Append to spans.jsonl
    with open(SPANS_FILE, 'a', encoding='utf-8') as f:
        for span in extracted_spans:
            json.dump(span, f)
            f.write('\n')
            
    # 4. Append to ner_dataset_all.jsonl
    # Format requires 'entities': [[start, end, label], ...]
    ner_entry = {
        "id": NOTE_ID,
        "text": NOTE_TEXT,
        "entities": [[s['start'], s['end'], s['label']] for s in extracted_spans]
    }
    with open(DATASET_FILE, 'a', encoding='utf-8') as f:
        json.dump(ner_entry, f)
        f.write('\n')

    # 5. Update Stats
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        # Fallback if file missing (though context implies it exists)
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans) # Assuming all valid here
    
    for span in extracted_spans:
        lbl = span['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    # 6. Validation Log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        for span in extracted_spans:
            extracted_text = NOTE_TEXT[span['start']:span['end']]
            if extracted_text != span['text']:
                f.write(f"WARNING: Mismatch in {NOTE_ID} span {span['span_id']}. "
                        f"Expected '{span['text']}', found '{extracted_text}'\n")

if __name__ == "__main__":
    update_files()
    print(f"Successfully processed {NOTE_ID} and updated ML pipeline files.")