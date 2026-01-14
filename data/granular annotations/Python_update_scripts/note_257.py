import json
import os
import datetime
from pathlib import Path
import re

# ---------------------------------------------------------
# 1. CONFIGURATION & TEXT DEFINITION
# ---------------------------------------------------------
NOTE_ID = "note_257"

# Cleaned text (removed '' tags for ML training quality)
RAW_TEXT = """NOTE_ID:  note_257 SOURCE_FILE: note_257.txt INDICATION FOR OPERATION:  Marcelo Gadea is a 53 year old-year-old male who presents with proximal tracheal stent migration after placement 1 week ago for complete subglottic stenosis.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.
 
CONSENT: Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form / provided consent over the phone.
The consent was witnessed by an assisting medical professional.
 
PREOPERATIVE DIAGNOSIS: J98.09 Other diseases of bronchus, not elsewhere classified
 
POSTOPERATIVE DIAGNOSIS:  J98.09 Other diseases of bronchus, not elsewhere classified
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31630 Balloon dilation
31638 Revision of tracheal/bronchial stent     
 
General Anesthesia
 
ANESTHESIA: 
Local anesthesia with: Lidocaine 2% Solution ~8ml via flexible bronchoscope
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
ESTIMATED BLOOD LOSS:   None
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
The procedure was performed in the bronchoscopy suite.
After administration of sedatives an LMA was placed and the therapeutic flexible bronchoscope was inserted through the LMA.
The vocal cords were edematous but open.  The patients known tracheal 12X20 Bonostent was visualized with the proximal edge abutting the distal aspect of the true vocal folds.
There was significant thick dry mucous with mild obstruction however the stent was otherwise patent.
Just distal to the stent was a 4cm long complex tracheal stenosis with circumferential friable and edematous mucosa.
An “A-shaped” deformity was visualized within the segment consistent with tracheal cartilage injury along with overlying granulation tissue creating a slit light obstruction of approximately 80% of the normal tracheal lumen.
The mid to distal trachea was normal and full inspection of the distal tracheobronchial tree revealed no other abnormalities and all bronchial segments were widely patent to at least the 1st sub-segmental branch.
The laryngeal mask airway was removed and a a 12 mm non-ventilating rigid tracheoscope was inserted through the mouth into the supra-glottic space.
Rigid alligator forceps were used to grasp the proximal limb of the tracheal stent and were rotated repeatedly while withdrawing the stent into the rigid bronchoscope.
The stent was subsequently removed without difficulty.  The rigid bronchoscope was then advanced through the vocal cords into the subglottic space and attached the jet ventilator.
Balloon dilatation of the stenotic segment was performed with a phased 8-9-10 Merit dilatational balloon.
Due to the deformity and lack of cartilaginous structure this only provided mild additional benefit.
The 10 mm rigid bronchosocpe was then telescoped into the tracheoscope and approximated to the level of the most significant stenosis.
The beveled tip was used to gently debulk granulation tissue with an apple coring technique.
At this point a 12 X 40 bonostent was placed under direct visualization with the proximal edge at the level of the cricoid cartilage about 2 cm distal to the true vocal folds and the distal edge 1 cm beyond the distal stenotic segment.
Balloon dilatation of stent was performed using a phased 12-13.5-15 Merit dilatational balloon.
Following dilatation the trachea was widely patent with a luminal diameter approximately 95% of the normal.
The rigid bronchoscope was then removed and the LMA re-inserted.
Final inspection of the airway was performed and images captures after which the patient was turned over to anesthesia for recovery.
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was transported to the recovery room in stable condition.
SPECIMEN(S): 
None
 
IMPRESSION: Marcelo Gadea is a 53 year old-year-old male with complex tracheal stenosis s/p tracheal stent revision.
RECOMMENDATIONS:
-	Transfer to PACU 
-	Discharge patient once criteria is met
-	Recommend continuing hypertonic saline for stent hydration
-           Follow-up in 2 weeks."""

# ---------------------------------------------------------
# 2. PATH SETUP
# ---------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ---------------------------------------------------------
# 3. ENTITY EXTRACTION LOGIC
# ---------------------------------------------------------
# Define targets to find. Order matters for sequential search.
# Structure: (Label, Search String, Occurrence Index [0-based, Optional- defaults to next found])
# Note: Occurrence Logic -> 0 means first found after current cursor.
targets = [
    # Indication
    ("ANAT_AIRWAY", "tracheal", 0),
    ("DEV_STENT", "stent", 0),
    ("CTX_TIME", "1 week ago", 0),
    ("OBS_LESION", "subglottic stenosis", 0),
    # Procedure List
    ("PROC_ACTION", "Therapeutic aspiration", 0),
    ("PROC_ACTION", "Balloon dilation", 0),
    ("PROC_ACTION", "Revision", 0),
    ("DEV_STENT", "tracheal/bronchial stent", 0),
    # Anesthesia
    ("MEDICATION", "Lidocaine", 0),
    ("MEAS_VOL", "8ml", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    # Procedure Detail
    ("DEV_INSTRUMENT", "LMA", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("DEV_INSTRUMENT", "LMA", 0),
    ("ANAT_AIRWAY", "vocal cords", 0),
    ("OBS_FINDING", "edematous", 0),
    ("ANAT_AIRWAY", "tracheal", 0),
    ("DEV_STENT_SIZE", "12X20", 0),
    ("DEV_STENT_MATERIAL", "Bonostent", 0),
    ("ANAT_AIRWAY", "true vocal folds", 0),
    ("OBS_FINDING", "thick dry mucous", 0),
    ("OBS_FINDING", "mild obstruction", 0),
    ("DEV_STENT", "stent", 0),
    ("MEAS_SIZE", "4cm", 0),
    ("OBS_LESION", "tracheal stenosis", 0),
    ("OBS_FINDING", "circumferential friable and edematous mucosa", 0),
    ("OBS_FINDING", "“A-shaped” deformity", 0),
    ("OBS_LESION", "tracheal cartilage injury", 0),
    ("OBS_LESION", "granulation tissue", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "obstruction of approximately 80% of the normal tracheal lumen", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 0),
    ("ANAT_AIRWAY", "bronchial segments", 0),
    ("DEV_INSTRUMENT", "laryngeal mask airway", 0),
    ("MEAS_SIZE", "12 mm", 0),
    ("DEV_INSTRUMENT", "rigid tracheoscope", 0),
    ("ANAT_AIRWAY", "supra-glottic space", 0),
    ("DEV_INSTRUMENT", "rigid alligator forceps", 0),
    ("DEV_STENT", "tracheal stent", 0),
    ("DEV_STENT", "stent", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("DEV_STENT", "stent", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("ANAT_AIRWAY", "vocal cords", 0),
    ("ANAT_AIRWAY", "subglottic space", 0),
    ("DEV_INSTRUMENT", "jet ventilator", 0),
    ("PROC_ACTION", "Balloon dilatation", 0),
    ("MEAS_SIZE", "8-9-10", 0),
    ("DEV_INSTRUMENT", "Merit dilatational balloon", 0),
    ("OBS_FINDING", "deformity", 0),
    ("MEAS_SIZE", "10 mm", 0),
    ("DEV_INSTRUMENT", "rigid bronchosocpe", 0), # Preserving typo in note
    ("DEV_INSTRUMENT", "tracheoscope", 0),
    ("OBS_LESION", "stenosis", 0),
    ("PROC_ACTION", "debulk", 0),
    ("OBS_LESION", "granulation tissue", 0),
    ("DEV_STENT_SIZE", "12 X 40", 0),
    ("DEV_STENT_MATERIAL", "bonostent", 0),
    ("ANAT_AIRWAY", "cricoid cartilage", 0),
    ("ANAT_AIRWAY", "true vocal folds", 0),
    ("PROC_ACTION", "Balloon dilatation", 0),
    ("DEV_STENT", "stent", 0),
    ("MEAS_SIZE", "12-13.5-15", 0),
    ("DEV_INSTRUMENT", "Merit dilatational balloon", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "widely patent with a luminal diameter approximately 95% of the normal", 0),
    ("DEV_INSTRUMENT", "rigid bronchoscope", 0),
    ("DEV_INSTRUMENT", "LMA", 0),
    # Impression
    ("OBS_LESION", "tracheal stenosis", 0),
    ("CTX_HISTORICAL", "s/p", 0),
    ("DEV_STENT", "tracheal stent", 0),
    ("PROC_ACTION", "revision", 0)
]

extracted_entities = []
cursor = 0

for label, text_snippet, _ in targets:
    # Find next occurrence after cursor
    start_idx = RAW_TEXT.find(text_snippet, cursor)
    
    if start_idx == -1:
        print(f"WARNING: Could not find '{text_snippet}' after index {cursor}")
        continue
        
    end_idx = start_idx + len(text_snippet)
    
    # Store entity
    extracted_entities.append({
        "start": start_idx,
        "end": end_idx,
        "label": label,
        "text": text_snippet
    })
    
    # Move cursor to end of found entity to enable sequential search
    cursor = end_idx

# ---------------------------------------------------------
# 4. FILE UPDATES
# ---------------------------------------------------------

# A. Update notes.jsonl
with open(NOTES_FILE, "a", encoding="utf-8") as f:
    json_record = {"id": NOTE_ID, "text": RAW_TEXT}
    f.write(json.dumps(json_record) + "\n")

# B. Update ner_dataset_all.jsonl
with open(NER_DATASET_FILE, "a", encoding="utf-8") as f:
    # Schema: {"id": ..., "text": ..., "entities": [[start, end, label], ...]}
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in extracted_entities]
    }
    f.write(json.dumps(ner_record) + "\n")

# C. Update spans.jsonl
with open(SPANS_FILE, "a", encoding="utf-8") as f:
    for e in extracted_entities:
        span_id = f"{e['label']}_{e['start']}"
        span_record = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        }
        f.write(json.dumps(span_record) + "\n")

# D. Update stats.json
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
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
stats["total_files"] += 1
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for e in extracted_entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_FILE, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# ---------------------------------------------------------
# 5. VALIDATION
# ---------------------------------------------------------
with open(LOG_FILE, "a", encoding="utf-8") as f:
    for e in extracted_entities:
        original = RAW_TEXT[e["start"]:e["end"]]
        if original != e["text"]:
            log_msg = f"[{datetime.datetime.now()}] MISMATCH in {NOTE_ID}: Span '{e['text']}' != Text '{original}' at {e['start']}:{e['end']}\n"
            f.write(log_msg)
            print(log_msg)

print(f"Successfully processed {NOTE_ID} with {len(extracted_entities)} entities.")