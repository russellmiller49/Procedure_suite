from pathlib import Path
import json
import os
import datetime

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_206"
script_dir = Path(__file__).resolve()

# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = script_dir.parents[2] / "ml_training" / "granular_ner"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. Raw Text & Entity Definition
# ==========================================
# Exact text reconstruction from the provided note
RAW_TEXT = (
    "Procedure Name: EBUS Staging Bronchoscopy.\n"
    "(CPT 31653 convex probe endobronchial ultrasound sampling 3 or more hilar or mediastinal stations or structures).\n"
    "Indications: diagnosis and staging of suspected lung cancer\n"
    "Medications: General Anesthesia\n"
    "Procedure, risks, benefits, and alternatives were explained to the patient.\n"
    "All questions were answered and informed consent was documented as per institutional protocol.\n"
    "A history and physical were performed and updated in the pre-procedure assessment record.\n"
    "Laboratory studies and radiographs \n"
    "Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.\n"
    "The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.\n"
    "The trachea was of normal caliber. The carina was sharp.\n"
    "The tracheobronchial tree was examined to at least the first sub-segmental level.\n"
    "In the right lower lobe there was extrinsic compression seen most prominently in the superior segment.\n"
    "Bronchial mucosa and anatomy were otherwise normal; there are no endobronchial lesions, and no secretions.\n"
    "No evidence of endobronchial disease was seen to at least the first sub-segments.\n"
    "A systematic hilar and mediastinal lymph node survey was carried out.\n"
    "Sampling criteria (5mm short axis diameter) were met in station 4L and 7 lymph nodes.\n"
    "Sampling by transbronchial needle aspiration was performed beginning with the 4L Lymph node, using an Olympus Visioshot2 EBUSTBNA 22 gauge needle.\n"
    "ROSE did not show evidence of malignancy. We then used the EBUS scope to visualize the 3cm mass adjacent to the right lower lobe and were able to access it with the EBUS TBNA needle.\n"
    "Preliminary ROSE was consistent with malignancy. Finally the EBUS bronchoscope was removed and utilizing the BF-XP190 ultrathin bronchoscope we were able to access the anterior segment if the right lower lobe and biopsy the distal endobronchial tumor with mini-forceps.\n"
    "The ultrathin bronchoscope was removed and the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.\n"
    "Complications: None\n"
    "Estimated Blood Loss: 5 cc.\n\n"
    "Post Procedure Diagnosis:\n"
    "- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.\n"
    "- The patient has remained stable and has been transferred in good condition to the post-procedural monitoring unit.\n"
    "- Will await final pathology results"
)

# Entities defined chronologically to ensure accurate sequential mapping
# Format: (Text_Snippet, Label)
ENTITIES_TO_MAP = [
    ("EBUS", "PROC_METHOD"),
    ("convex probe endobronchial ultrasound", "PROC_METHOD"),
    ("sampling", "PROC_ACTION"),
    ("3", "MEAS_COUNT"), # "3 or more"
    ("hilar", "ANAT_LN_STATION"),
    ("mediastinal", "ANAT_LN_STATION"),
    ("lung cancer", "OBS_LESION"),
    ("upper airway", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("mouth", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("extrinsic compression", "OBS_FINDING"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("endobronchial lesions", "OBS_LESION"),
    ("secretions", "OBS_FINDING"),
    ("endobronchial disease", "OBS_LESION"),
    ("hilar", "ANAT_LN_STATION"),
    ("mediastinal", "ANAT_LN_STATION"),
    ("5mm", "MEAS_SIZE"),
    ("station 4L", "ANAT_LN_STATION"),
    ("7", "ANAT_LN_STATION"),
    ("Sampling", "PROC_ACTION"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("4L", "ANAT_LN_STATION"),
    ("Olympus Visioshot2 EBUSTBNA", "DEV_INSTRUMENT"),
    ("22 gauge", "DEV_NEEDLE"),
    ("ROSE", "PROC_METHOD"), # The action/test itself
    ("malignancy", "OBS_ROSE"), # The result
    ("EBUS scope", "DEV_INSTRUMENT"),
    ("3cm", "MEAS_SIZE"),
    ("mass", "OBS_LESION"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("EBUS TBNA needle", "DEV_NEEDLE"),
    ("ROSE", "PROC_METHOD"),
    ("malignancy", "OBS_ROSE"),
    ("EBUS bronchoscope", "DEV_INSTRUMENT"),
    ("BF-XP190 ultrathin bronchoscope", "DEV_INSTRUMENT"),
    ("anterior segment", "ANAT_LUNG_LOC"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("biopsy", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),
    ("mini-forceps", "DEV_INSTRUMENT"),
    ("ultrathin bronchoscope", "DEV_INSTRUMENT"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("secretions", "OBS_FINDING"),
    ("active bleeding", "OBS_FINDING"),
    ("5 cc", "MEAS_VOL"),
    ("endobronchial ultrasound", "PROC_METHOD"),
    ("biopsies", "PROC_ACTION")
]

# ==========================================
# 3. Processing Logic
# ==========================================

def calculate_offsets(text, entities_list):
    """
    Scans the text sequentially to find start/end indices for entities.
    """
    results = []
    search_cursor = 0
    
    for entity_text, label in entities_list:
        start = text.find(entity_text, search_cursor)
        
        if start == -1:
            print(f"WARNING: Could not find '{entity_text}' after index {search_cursor}")
            continue
            
        end = start + len(entity_text)
        results.append({
            "label": label,
            "text": entity_text,
            "start": start,
            "end": end
        })
        # Advance cursor to avoid re-matching the same instance text if it repeats
        search_cursor = start + 1
        
    return results

def update_file(path, data, mode='a'):
    """Helper to append JSON lines to files."""
    with open(path, mode, encoding='utf-8') as f:
        f.write(json.dumps(data) + "\n")

# Extract spans
valid_spans = calculate_offsets(RAW_TEXT, ENTITIES_TO_MAP)

# ==========================================
# 4. File Updates
# ==========================================

# A. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[s["start"], s["end"], s["label"]] for s in valid_spans]
}
update_file(NER_DATASET_PATH, ner_entry)

# B. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
update_file(NOTES_PATH, note_entry)

# C. Update spans.jsonl
with open(SPANS_PATH, 'a', encoding='utf-8') as f:
    for span in valid_spans:
        span_entry = {
            "span_id": f"{span['label']}_{span['start']}",
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        }
        f.write(json.dumps(span_entry) + "\n")

# D. Update stats.json
if STATS_PATH.exists():
    with open(STATS_PATH, 'r', encoding='utf-8') as f:
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
stats["total_files"] += 1  # Assuming 1:1 note to file
stats["total_spans_raw"] += len(valid_spans)
stats["total_spans_valid"] += len(valid_spans)

for span in valid_spans:
    lbl = span['label']
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

# E. Alignment Verification & Logging
with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
    timestamp = datetime.datetime.now().isoformat()
    for span in valid_spans:
        extracted = RAW_TEXT[span['start']:span['end']]
        if extracted != span['text']:
            log_msg = f"[{timestamp}] MISMATCH: {NOTE_ID} | Exp: '{span['text']}' vs Act: '{extracted}'"
            log_file.write(log_msg + "\n")
            print(log_msg)

print(f"Successfully processed {NOTE_ID}. Extracted {len(valid_spans)} entities.")