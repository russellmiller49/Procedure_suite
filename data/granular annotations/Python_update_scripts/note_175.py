import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_175"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cleaned Raw Text (Source tags removed)
RAW_TEXT = (
    "Procedure Name: \n"
    "1.\tradial EBUS guided bronchoscopy with TNBA and endobronchial biopsies\n"
    "2.\tBronchoscopic intubation \n"
    "Indications: Lung cancer with suspicion for recurrence \n"
    "Medications: Propofol infusion via anesthesia assistance  \n"
    "Procedure, risks, benefits, and alternatives were explained to the patient.\n"
    "All questions were answered and informed consent was documented as per institutional protocol.\n"
    "A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.\n"
    "A time-out was performed prior to the intervention. \n"
    "Following intravenous medications as per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree the Q190 video bronchoscope was introduced through the mouth.\n"
    "The vocal cords appeared normal. The subglottic space was normal. The trachea is of normal caliber. The carina was sharp.\n"
    "Somewhat thick secretions were seen throughout the airways. The left sided airway anatomy was normal without evidence of endobronchial disease.\n"
    "On the right the patient had an anatomic variant with an accessory airway just proximal to the superior segment of the right lower lobe.\n"
    "Within that segment fibrotic endoluminal obstruction was seen but all other airways did not have visual endobronchial disease to at least the first sub-segmental level.\n"
    "Due to difficulty with maintaining position of LMA (edentulous) the decision was made to convert to endotracheal intubation.\n"
    "This was performed over the bronchoscope without difficulty and the ETT was secured approximately 2 cm above the main carina.\n"
    "Once the ETT was connected to ventilator, The flexible bronchoscope was re-inserted through the tube and advanced to the orifice of the accessory left lower lobe bronchus and the radial ultrasound was advanced through the scope into the sub-segment and a concentric view of the lesion was visualized within the segment.\n"
    "Multiple forceps biopsies were then performed. The lesion was extremely firm and samples were relatively scant.\n"
    "We then utilized the super-dimension 21G peripheral needle and the 19G Olympus peripheral needle to obtain a total of 6 endobronchial needle biopsies of the lesion which were placed in formalin.\n"
    "After adequate samples were obtained repeat inspection was performed and no evidence of bleeding or other complications were seen.\n"
    "The bronchoscope was removed and the procedure completed.  \n"
    "Complications: No immediate complications\n"
    "Estimated Blood Loss: Less than 5 cc.\n"
    "Post Procedure Diagnosis:\n"
    "- Flexible bronchoscopy with successful biopsy of left lower lobe accessory segment fibrotic endobronchial lesion.\n"
    "- Await final pathology"
)

# ==========================================
# 2. Entity Definitions (Schema: Label_guide_UPDATED.csv)
# ==========================================
# Define entities as (Label, Text_Snippet, Occurrence_Index)
# Occurrence_Index=0 means the first time the text appears, 1 is the second, etc.

entity_definitions = [
    ("PROC_METHOD", "radial EBUS", 0),
    ("PROC_ACTION", "TNBA", 0),
    ("PROC_ACTION", "endobronchial biopsies", 0),
    ("PROC_ACTION", "Bronchoscopic intubation", 0),
    ("OBS_LESION", "Lung cancer", 0),
    ("MEDICATION", "Propofol", 0),
    ("MEDICATION", "topical anesthesia", 0),
    ("ANAT_AIRWAY", "upper airway", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 0),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope", 0),
    ("ANAT_AIRWAY", "vocal cords", 0),
    ("ANAT_AIRWAY", "subglottic space", 0),
    ("ANAT_AIRWAY", "trachea", 0),
    ("ANAT_AIRWAY", "carina", 0),
    ("OBS_FINDING", "thick secretions", 0),
    ("ANAT_AIRWAY", "airways", 0),
    ("LATERALITY", "left", 0), # "The left sided"
    ("ANAT_AIRWAY", "airway", 0),
    ("OBS_LESION", "endobronchial disease", 0),
    ("LATERALITY", "right", 0), # "On the right"
    ("ANAT_AIRWAY", "accessory airway", 0),
    ("ANAT_LUNG_LOC", "superior segment", 0),
    ("ANAT_LUNG_LOC", "right lower lobe", 0),
    ("OBS_LESION", "fibrotic endoluminal obstruction", 0),
    ("OBS_LESION", "endobronchial disease", 1), # "visual endobronchial disease"
    ("DEV_INSTRUMENT", "LMA", 0),
    ("PROC_ACTION", "endotracheal intubation", 0),
    ("DEV_INSTRUMENT", "bronchoscope", 1), # "over the bronchoscope"
    ("DEV_INSTRUMENT", "ETT", 0),
    ("MEAS_SIZE", "2 cm", 0),
    ("ANAT_AIRWAY", "main carina", 0),
    ("DEV_INSTRUMENT", "ETT", 1), # "ETT was connected"
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("LATERALITY", "left", 1), # "left lower lobe"
    ("ANAT_LUNG_LOC", "left lower lobe", 0),
    ("ANAT_AIRWAY", "bronchus", 0),
    ("PROC_METHOD", "radial ultrasound", 0),
    ("OBS_LESION", "lesion", 0), # "view of the lesion"
    ("PROC_ACTION", "forceps biopsies", 0),
    ("OBS_LESION", "lesion", 1), # "The lesion was extremely firm"
    ("PROC_METHOD", "super-dimension", 0),
    ("DEV_NEEDLE", "21G", 0),
    ("DEV_INSTRUMENT", "peripheral needle", 0),
    ("DEV_NEEDLE", "19G", 0),
    ("DEV_INSTRUMENT", "Olympus peripheral needle", 0),
    ("MEAS_COUNT", "6", 0),
    ("PROC_ACTION", "endobronchial needle biopsies", 0),
    ("OBS_LESION", "lesion", 2), # "biopsies of the lesion"
    ("OBS_FINDING", "bleeding", 0),
    ("DEV_INSTRUMENT", "bronchoscope", 2), # "bronchoscope was removed"
    ("OUTCOME_COMPLICATION", "No immediate complications", 0),
    ("MEAS_VOL", "Less than 5 cc", 0),
    ("PROC_ACTION", "Flexible bronchoscopy", 0),
    ("PROC_ACTION", "biopsy", 0),
    ("ANAT_LUNG_LOC", "left lower lobe", 1),
    ("OBS_LESION", "fibrotic endobronchial lesion", 0)
]

# ==========================================
# 3. Extraction Logic
# ==========================================
def find_offsets(text, search_str, instance_idx):
    """Finds the start/end offsets of the Nth instance of a substring."""
    current_idx = -1
    start_pos = -1
    for _ in range(instance_idx + 1):
        start_pos = text.find(search_str, start_pos + 1)
        if start_pos == -1:
            return None
    return start_pos, start_pos + len(search_str)

extracted_entities = []
warnings = []

for label, substring, instance in entity_definitions:
    result = find_offsets(RAW_TEXT, substring, instance)
    if result:
        start, end = result
        span_text = RAW_TEXT[start:end]
        
        # Validation
        if span_text != substring:
            warnings.append(f"Mismatch: Expected '{substring}', got '{span_text}'")
        
        extracted_entities.append({
            "start": start,
            "end": end,
            "label": label,
            "text": span_text
        })
    else:
        warnings.append(f"NotFound: '{substring}' (instance {instance})")

# ==========================================
# 4. File Update Logic
# ==========================================

# A. ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_entities
}

with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# C. spans.jsonl
spans_entries = []
for ent in extracted_entities:
    span_id = f"{ent['label']}_{ent['start']}"
    spans_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": ent['label'],
        "text": ent['text'],
        "start": ent['start'],
        "end": ent['end']
    })

with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
    for span in spans_entries:
        f.write(json.dumps(span) + "\n")

# D. stats.json
stats_file = OUTPUT_DIR / "stats.json"
if stats_file.exists():
    with open(stats_file, "r", encoding="utf-8") as f:
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
stats["total_files"] += 1 # Assuming 1 note per file for this script
stats["total_spans_raw"] += len(extracted_entities)
stats["total_spans_valid"] += len(extracted_entities)

for ent in extracted_entities:
    lbl = ent["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_file, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# ==========================================
# 5. Logging
# ==========================================
log_file = OUTPUT_DIR / "alignment_warnings.log"
if warnings:
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n--- {NOTE_ID} ({datetime.datetime.now()}) ---\n")
        for w in warnings:
            f.write(w + "\n")
    print(f"Completed with {len(warnings)} warnings. Check {log_file}")
else:
    print(f"Success! {NOTE_ID} processed. {len(extracted_entities)} entities extracted.")