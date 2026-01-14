import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_201"
SCRIPT_DIR = Path(__file__).resolve().parent
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text Data
# ==========================================
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: 
1.	Right lower lobe obstructive mass
POSTOPERATIVE DIAGNOSIS: 
1.	Right lower lobe obstructive mass
PROCEDURE PERFORMED: 
CPT 31641: Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with destruction of tumor or relief of stenosis by any method other than excision (eg, laser therapy, cryotherapy)
CPT 31640 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with excision of tumor
CPT 31645  bronchoscopy with therapeutic aspiration
CPT 31625 Bronchoscopy with endobronchial biopsy(s)
INDICATIONS:  Airway obstruction and need for tissue biopsy
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the distal trachea and advanced into the distal trachea before attaching the monsoon JET ventilator.
Using the flexible bronchoscope airway inspection was performed. The tracheal was normal. The tracheal carina was sharp.
All left sided airways were normal. The right mainstem, right upper lobe, bronchus intermedius and right middle lobe were normal.
In the proximal right lower lobe there was a completely obstructing endobronchial mass just distal to the uninvolved superior segment.
We were unable to bypass the mass with the flexible bronchoscope and the mass was friable.
We initially attempted to utilize electrocautery snare to remove the tumor but due to the broad base were unsuccessful.
Bleeding which was controlled with topical epinephrine and iced saline.
APC was used to then paint the lesion and then debulking was performed with a combination of cryoprobe, flexible and rigid forceps.
The tumor persisted past the trifurcation of the basilar segments however we were able to bypass the tumor and visualize uninvolved distal airway to at least the first order sub-segments in the medial, anterior, lateral and posterior basal segments.
Due to the extent of involvement we did not feel additional debulking was warranted at this time.
The total endoluminal obstruction in the right lower lobe was approximately 60% at the end of the procedure.
Once we were satisfied that there was no active bleeding the rigid bronchoscope was removed and the patient was turned over to anesthesia for continued care.
Complications: None
Recommendations:
- To PACU and return to ward once criteria met
- Obtain CXR
- Will await biopsy results."""

# ==========================================
# 3. Define Entities (Manual Extraction based on Rules)
# ==========================================
# List of tuples: (Label, Search String, Starting Search Index to resolve duplicates)
# Note: Starting Index is optional if unique or sequential search is handled manually.
# For robustness, we will map them directly to character indices.

entities_to_map = [
    # Header / Diagnosis
    ("ANAT_LUNG_LOC", "Right lower lobe", 0),
    ("OBS_LESION", "mass", 0), # in Preop
    ("ANAT_LUNG_LOC", "Right lower lobe", 80), # in Postop
    ("OBS_LESION", "mass", 80), # in Postop
    
    # Procedures (CPT Lines)
    ("PROC_ACTION", "Bronchoscopy", 120),
    ("PROC_METHOD", "fluoroscopic guidance", 120),
    ("OBS_LESION", "tumor", 200),
    ("PROC_METHOD", "laser therapy", 200),
    ("PROC_METHOD", "cryotherapy", 200),
    
    ("PROC_ACTION", "Bronchoscopy", 300),
    ("PROC_METHOD", "fluoroscopic guidance", 300),
    ("PROC_ACTION", "excision", 400),
    ("OBS_LESION", "tumor", 400),
    
    ("PROC_ACTION", "bronchoscopy", 430),
    ("PROC_ACTION", "aspiration", 430),
    
    ("PROC_ACTION", "Bronchoscopy", 480),
    ("PROC_ACTION", "biopsy", 480), # endobronchial biopsy
    
    # Indications
    ("OBS_LESION", "Airway obstruction", 530),
    ("PROC_ACTION", "tissue biopsy", 530),
    
    # Description
    ("MEAS_SIZE", "12 mm", 800),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 800),
    ("ANAT_AIRWAY", "distal trachea", 850),
    ("ANAT_AIRWAY", "distal trachea", 900),
    ("DEV_INSTRUMENT", "monsoon JET ventilator", 900), # Specific device
    
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1000),
    ("PROC_ACTION", "airway inspection", 1000),
    ("ANAT_AIRWAY", "tracheal", 1060), # "The tracheal was normal"
    ("ANAT_AIRWAY", "tracheal carina", 1080),
    
    ("ANAT_AIRWAY", "left sided airways", 1100),
    ("ANAT_AIRWAY", "right mainstem", 1100),
    ("ANAT_LUNG_LOC", "right upper lobe", 1100),
    ("ANAT_AIRWAY", "bronchus intermedius", 1100),
    ("ANAT_LUNG_LOC", "right middle lobe", 1100),
    
    ("ANAT_LUNG_LOC", "right lower lobe", 1250),
    ("OBS_LESION", "mass", 1300),
    ("ANAT_LUNG_LOC", "superior segment", 1300),
    
    ("OBS_LESION", "mass", 1380), # bypass the mass
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1380),
    ("OBS_LESION", "mass", 1400), # mass was friable
    ("OBS_FINDING", "friable", 1430),
    
    ("DEV_INSTRUMENT", "electrocautery snare", 1450),
    ("PROC_ACTION", "remove", 1450),
    ("OBS_LESION", "tumor", 1480),
    
    ("OUTCOME_COMPLICATION", "Bleeding which was controlled", 1540),
    ("MEDICATION", "epinephrine", 1540),
    ("MEDICATION", "iced saline", 1540), # Valid per context of application
    
    ("PROC_METHOD", "APC", 1600),
    ("OBS_LESION", "lesion", 1600),
    ("PROC_ACTION", "debulking", 1600),
    ("DEV_INSTRUMENT", "cryoprobe", 1650),
    ("DEV_INSTRUMENT", "flexible and rigid forceps", 1650),
    
    ("OBS_LESION", "tumor", 1700),
    ("ANAT_LUNG_LOC", "basilar segments", 1700), # "trifurcation of..."
    ("OBS_LESION", "tumor", 1750), # bypass the tumor
    ("ANAT_LUNG_LOC", "medial, anterior, lateral and posterior basal segments", 1800),
    
    ("PROC_ACTION", "debulking", 1900),
    
    ("ANAT_LUNG_LOC", "right lower lobe", 2000),
    ("OUTCOME_AIRWAY_LUMEN_POST", "approximately 60%", 2000), # "obstruction... was approximately 60%"
    
    ("OBS_FINDING", "active bleeding", 2100),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 2100),
    
    ("OUTCOME_COMPLICATION", "None", 2250)
]

# Helper to find exact spans
entities_final = []
search_cursor = 0

def find_nth_occurrence(substring, text, n=1, start_search=0):
    start = start_search
    for _ in range(n):
        idx = text.find(substring, start)
        if idx == -1:
            return -1
        start = idx + 1
    return start - 1

# Process mapping
# We iterate and find indices. Since the text is static, we can use simple .find() 
# but need to ensure we don't pick up earlier occurrences for later items.
# We will use the 'start_search' hint from our list or the previous end index.

current_idx = 0
for label, txt, hint_idx in entities_to_map:
    # Use the hint_idx to jump ahead if provided, else use 0
    start_search = hint_idx if hint_idx > 0 else 0
    
    start = RAW_TEXT.find(txt, start_search)
    
    if start == -1:
        print(f"Warning: Could not find '{txt}' starting at {start_search}")
        continue
        
    end = start + len(txt)
    entities_final.append({
        "label": label,
        "text": txt,
        "start": start,
        "end": end
    })

# ==========================================
# 4. JSON Generation & File Updates
# ==========================================

def update_files():
    # 1. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities_final]
    }
    
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 2. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 3. Update spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for ent in entities_final:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent["label"],
                "text": ent["text"],
                "start": ent["start"],
                "end": ent["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

    # 4. Update stats.json
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, "r", encoding="utf-8") as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += len(entities_final)
    stats["total_spans_valid"] += len(entities_final)
    
    for ent in entities_final:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    # 5. Validation Log
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for ent in entities_final:
            extracted = RAW_TEXT[ent["start"]:ent["end"]]
            if extracted != ent["text"]:
                log_msg = f"[{datetime.datetime.now()}] Mismatch in {NOTE_ID}: Expected '{ent['text']}' but got '{extracted}' at {ent['start']}:{ent['end']}\n"
                f.write(log_msg)

if __name__ == "__main__":
    update_files()
    print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")