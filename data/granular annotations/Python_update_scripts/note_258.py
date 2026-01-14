import json
import os
import datetime
from pathlib import Path

# ==========================================
# Configuration
# ==========================================
NOTE_ID = "note_258"
SCRIPT_NAME = "update_ner_note_258.py"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# Raw Text Definition
# ==========================================
# Reconstructed exactly from the provided text content
RAW_TEXT = (
    "NOTE_ID:  note_258 SOURCE_FILE: note_258.txt PROCEDURE TECHNIQUE: Procedure, risks, benefits, and "
    "alternatives were explained to the patient. All questions were answered and informed consent was "
    "documented as per institutional protocol. A history and physical were performed and updated in the "
    "preprocedure assessment record. Laboratory studies and radiographs were reviewed. A time-out was "
    "performed prior to the intervention. Following intravenous medications as per the record and topical "
    "anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced "
    "through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree. The laryngeal "
    "mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal. "
    "The trachea was of normal caliber. The carina was sharp. The tracheobronchial tree was examined to at "
    "least the first subsegmental level. Bronchial mucosa and anatomy were normal; there are no endobronchial "
    "lesions, and no secretions, there was extrinsic compression noted in the superior segment of the left "
    "lower lobe which precluded deeper visual inspection of suspected endobronchial disease within the "
    "segment. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was "
    "introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree. "
    "A systematic hilar and mediastinal lymph node survey was carried out. Sampling criteria (5mm short axis "
    "diameter) was met in station 11L lymph node. Further details regarding nodal size are in the table "
    "below. The EBUS scope was positioned in the origin of the left lower lobe and turned posteriorly to "
    "visualize the lung mass abutting the airway which measured 31.5mm in short axis diameter. Sampling by "
    "transbronchial needle aspiration was performed beginning with the 11L Lymph node using an Olympus "
    "EBUSTBNA 21 gauge needle. ROSE indicated adequate lymph node sampling. We then reintroduced the EBUS "
    "scope into the left lower lobe and visualized the mass abutting the airway and EBUS guided sampling "
    "was performed of the mass with the EBUSTBNA 21 gauge needle. ROSE evaluation yielded tissue concerning "
    "for malignancy. All samples were sent for routine cytology and additional needle passes were performed "
    "for molecular studies. Following completion of EBUS bronchoscopy the video bronchoscope was re-inserted "
    "and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope "
    "was subsequently removed. There were no complications. Estimated Blood Loss: Less than 5 cc.\n"
    "Post Procedure Diagnosis:\n"
    "- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.\n"
    "- The patient has remained stable and has been transferred in good condition to the post-surgical "
    "monitoring unit.\n"
    "- Will await final pathology results\n"
    "Station:	EBUS Size (mm)	Number of passes	ROSE Findings\n"
    "11Rs	3.7	0	\n"
    "11Ri	N/A	0	\n"
    "4R	4.0	0	\n"
    "2R	3.3	0	\n"
    "2L	3.3	0	\n"
    "4L	3.7	0	\n"
    "7	4.9	0	\n"
    "11L	7.0	6	Lymphocytes\n"
    "Lung Mass	31.5	8	Malignancy"
)

# ==========================================
# Entity Extraction Helper
# ==========================================
def find_entity(text, substring, label, start_search=0, instance_num=1):
    """
    Finds the start and end indices of a substring within the text.
    instance_num: Which occurrence to find (1-based index).
    """
    current_pos = start_search
    for _ in range(instance_num):
        start = text.find(substring, current_pos)
        if start == -1:
            return None
        current_pos = start + 1
    
    start = text.find(substring, start_search) if instance_num == 1 else start # Reset for safety if needed, but logic above holds
    
    # Recalculate exact start based on instance loop
    current_pos = start_search
    found_start = -1
    for _ in range(instance_num):
        found_start = text.find(substring, current_pos)
        if found_start == -1:
            return None
        current_pos = found_start + 1
    
    return {
        "label": label,
        "text": substring,
        "start": found_start,
        "end": found_start + len(substring)
    }

# ==========================================
# Define Entities
# ==========================================
entities = []

# Main text entities
entities.append(find_entity(RAW_TEXT, "tracheobronchial tree", "ANAT_AIRWAY", instance_num=1))
entities.append(find_entity(RAW_TEXT, "Q190 video bronchoscope", "DEV_INSTRUMENT"))
entities.append(find_entity(RAW_TEXT, "laryngeal mask airway", "DEV_INSTRUMENT", instance_num=1))
entities.append(find_entity(RAW_TEXT, "tracheobronchial tree", "ANAT_AIRWAY", instance_num=2))
entities.append(find_entity(RAW_TEXT, "laryngeal mask airway", "DEV_INSTRUMENT", instance_num=2))
entities.append(find_entity(RAW_TEXT, "trachea", "ANAT_AIRWAY"))
entities.append(find_entity(RAW_TEXT, "carina", "ANAT_AIRWAY"))
entities.append(find_entity(RAW_TEXT, "tracheobronchial tree", "ANAT_AIRWAY", instance_num=3))
entities.append(find_entity(RAW_TEXT, "extrinsic compression", "OBS_FINDING")) # General finding, not specific lesion
entities.append(find_entity(RAW_TEXT, "superior segment of the left lower lobe", "ANAT_LUNG_LOC"))
entities.append(find_entity(RAW_TEXT, "video bronchoscope", "DEV_INSTRUMENT", instance_num=2)) # "The video bronchoscope was then removed..."
entities.append(find_entity(RAW_TEXT, "UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT"))
entities.append(find_entity(RAW_TEXT, "laryngeal mask airway", "DEV_INSTRUMENT", instance_num=3))
entities.append(find_entity(RAW_TEXT, "tracheobronchial tree", "ANAT_AIRWAY", instance_num=4))
entities.append(find_entity(RAW_TEXT, "station 11L", "ANAT_LN_STATION"))
entities.append(find_entity(RAW_TEXT, "5mm", "MEAS_SIZE"))
entities.append(find_entity(RAW_TEXT, "left lower lobe", "ANAT_LUNG_LOC", instance_num=2)) # "...origin of the left lower lobe"
entities.append(find_entity(RAW_TEXT, "lung mass", "OBS_LESION"))
entities.append(find_entity(RAW_TEXT, "31.5mm", "MEAS_SIZE"))
entities.append(find_entity(RAW_TEXT, "transbronchial needle aspiration", "PROC_ACTION"))
entities.append(find_entity(RAW_TEXT, "11L Lymph node", "ANAT_LN_STATION", instance_num=2))
entities.append(find_entity(RAW_TEXT, "21 gauge needle", "DEV_NEEDLE", instance_num=1))
entities.append(find_entity(RAW_TEXT, "adequate lymph node sampling", "OBS_ROSE"))
entities.append(find_entity(RAW_TEXT, "left lower lobe", "ANAT_LUNG_LOC", instance_num=3)) # "...into the left lower lobe"
entities.append(find_entity(RAW_TEXT, "mass", "OBS_LESION", instance_num=2)) # "...visualized the mass abutting..."
entities.append(find_entity(RAW_TEXT, "EBUS guided sampling", "PROC_ACTION"))
entities.append(find_entity(RAW_TEXT, "mass", "OBS_LESION", instance_num=3)) # "...performed of the mass..."
entities.append(find_entity(RAW_TEXT, "21 gauge needle", "DEV_NEEDLE", instance_num=2))
entities.append(find_entity(RAW_TEXT, "concerning for malignancy", "OBS_ROSE"))
entities.append(find_entity(RAW_TEXT, "flexible bronchoscopy", "PROC_ACTION"))
entities.append(find_entity(RAW_TEXT, "endobronchial ultrasound", "PROC_METHOD"))
entities.append(find_entity(RAW_TEXT, "biopsies", "PROC_ACTION"))
entities.append(find_entity(RAW_TEXT, "Less than 5 cc", "MEAS_VOL"))

# Table Entities (Finding by context)
table_start = RAW_TEXT.find("Station:	EBUS Size (mm)")

# Row 1: 11Rs
entities.append(find_entity(RAW_TEXT, "11Rs", "ANAT_LN_STATION", start_search=table_start))
entities.append(find_entity(RAW_TEXT, "3.7", "MEAS_SIZE", start_search=table_start)) # 11Rs size

# Row 2: 11Ri - N/A size
entities.append(find_entity(RAW_TEXT, "11Ri", "ANAT_LN_STATION", start_search=table_start))

# Row 3: 4R
entities.append(find_entity(RAW_TEXT, "4R", "ANAT_LN_STATION", start_search=table_start))
entities.append(find_entity(RAW_TEXT, "4.0", "MEAS_SIZE", start_search=table_start)) 

# Row 4: 2R
entities.append(find_entity(RAW_TEXT, "2R", "ANAT_LN_STATION", start_search=table_start))
# Note: "3.3" appears twice in sequence (2R and 2L). Need precise index.
entities.append(find_entity(RAW_TEXT, "3.3", "MEAS_SIZE", start_search=table_start, instance_num=1))

# Row 5: 2L
entities.append(find_entity(RAW_TEXT, "2L", "ANAT_LN_STATION", start_search=table_start))
entities.append(find_entity(RAW_TEXT, "3.3", "MEAS_SIZE", start_search=table_start, instance_num=2))

# Row 6: 4L
entities.append(find_entity(RAW_TEXT, "4L", "ANAT_LN_STATION", start_search=table_start))
entities.append(find_entity(RAW_TEXT, "3.7", "MEAS_SIZE", start_search=table_start, instance_num=2)) # 1st was 11Rs

# Row 7: 7
entities.append(find_entity(RAW_TEXT, "7", "ANAT_LN_STATION", start_search=table_start)) # Searching "7" might match 3.7. Need exact match
# Let's use specific context for "7" in table
idx_7 = RAW_TEXT.find("\n7\t", table_start) # Finding "newline 7 tab"
if idx_7 != -1:
    entities.append({"label": "ANAT_LN_STATION", "text": "7", "start": idx_7 + 1, "end": idx_7 + 2})
entities.append(find_entity(RAW_TEXT, "4.9", "MEAS_SIZE", start_search=table_start))

# Row 8: 11L
entities.append(find_entity(RAW_TEXT, "11L", "ANAT_LN_STATION", start_search=table_start, instance_num=3)) # 1st was text, 2nd was text, 3rd is table?
# Actually checking text again:
# 1. "...station 11L lymph node"
# 2. "...with the 11L Lymph node"
# 3. Table: "11L"
entities.append(find_entity(RAW_TEXT, "7.0", "MEAS_SIZE", start_search=table_start))
entities.append(find_entity(RAW_TEXT, "6", "MEAS_COUNT", start_search=table_start + 500)) # Search late in text to avoid "6" in dates/times
# Actually, safer to find "6\tLymphocytes"
idx_6 = RAW_TEXT.find("\t6\tLymphocytes")
if idx_6 != -1:
    entities.append({"label": "MEAS_COUNT", "text": "6", "start": idx_6 + 1, "end": idx_6 + 2})
entities.append(find_entity(RAW_TEXT, "Lymphocytes", "OBS_ROSE", start_search=table_start))

# Row 9: Lung Mass
entities.append(find_entity(RAW_TEXT, "Lung Mass", "OBS_LESION", start_search=table_start))
entities.append(find_entity(RAW_TEXT, "31.5", "MEAS_SIZE", start_search=table_start))
idx_8 = RAW_TEXT.find("\t8\tMalignancy")
if idx_8 != -1:
    entities.append({"label": "MEAS_COUNT", "text": "8", "start": idx_8 + 1, "end": idx_8 + 2})
entities.append(find_entity(RAW_TEXT, "Malignancy", "OBS_ROSE", start_search=table_start))

# Filter None
entities = [e for e in entities if e is not None]

# ==========================================
# File Updating Logic
# ==========================================

def update_jsonl(path, new_entry, key="id"):
    """Appends a new entry to a JSONL file."""
    with open(path, "a") as f:
        f.write(json.dumps(new_entry) + "\n")

def update_stats(path, new_entities):
    """Updates the stats.json file with new counts."""
    with open(path, "r") as f:
        stats = json.load(f)
    
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(new_entities)
    stats["total_spans_valid"] += len(new_entities)
    
    for entity in new_entities:
        label = entity["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1
        
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)

def log_alignment_error(expected_text, actual_text, start, end):
    with open(LOG_PATH, "a") as f:
        f.write(f"MISMATCH: Expected '{expected_text}', got '{actual_text}' at {start}:{end}\n")

# Execution
try:
    # 1. Update ner_dataset_all.jsonl
    ner_entry = {"id": NOTE_ID, "text": RAW_TEXT, "entities": entities}
    update_jsonl(NER_DATASET_PATH, ner_entry)
    
    # 2. Update notes.jsonl
    notes_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    update_jsonl(NOTES_PATH, notes_entry)
    
    # 3. Update spans.jsonl
    for entity in entities:
        # Verify alignment
        extracted = RAW_TEXT[entity["start"]:entity["end"]]
        if extracted != entity["text"]:
            log_alignment_error(entity["text"], extracted, entity["start"], entity["end"])
        
        span_entry = {
            "span_id": f"{entity['label']}_{entity['start']}",
            "note_id": NOTE_ID,
            "label": entity['label'],
            "text": entity['text'],
            "start": entity['start'],
            "end": entity['end']
        }
        update_jsonl(SPANS_PATH, span_entry)
    
    # 4. Update stats.json
    update_stats(STATS_PATH, entities)
    
    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

except Exception as e:
    print(f"Error processing {NOTE_ID}: {e}")