import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_130"

# Target Directory Structure
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = Path("stats.json") # Assuming relative path for the provided file context
ALIGNMENT_LOG = Path("alignment_warnings.log")

# ==========================================
# 2. Raw Text Data
# ==========================================
# Exact text from Source 1-31
TEXT = """Procedure Name: Bronchoscopy

Indications:

Known lung cancer of the right lower lobe

Malignant airway disease

Evaluation for mediastinal staging

Anesthesia:
General anesthesia with controlled mechanical ventilation.
Topical anesthesia with 2% lidocaine to the tracheobronchial tree (9 mL).
See the anesthesia record for full documentation of administered medications.
Pre-Anesthesia Assessment:

ASA Physical Status Classification: III (patient with severe systemic disease)

The procedure, including risks, benefits, and alternatives, was explained to the patient.
All questions were answered, and informed consent was obtained and documented per institutional protocol.
A history and physical examination were performed and updated in the pre-procedure assessment record.
Relevant laboratory studies and radiographic imaging were reviewed. A procedural time-out was performed prior to the intervention.
Following administration of intravenous anesthetic medications and topical anesthesia to the upper airway and tracheobronchial tree, the Q180 slim video bronchoscope was introduced through the mouth via a laryngeal mask airway and advanced into the tracheobronchial tree.
The UC180F convex probe EBUS bronchoscope was subsequently introduced through the mouth via the laryngeal mask airway and advanced into the tracheobronchial tree.
A black rigid bronchial tube (12.0–11.0 mm) was introduced through the mouth and advanced into the tracheobronchial tree.
A 0-degree, 4.0-mm rigid telescope was introduced through the rigid bronchoscope and advanced into the airway.
The T180 therapeutic video bronchoscope was then introduced through the rigid bronchoscope following removal of the telescope and advanced into the tracheobronchial tree.
Procedure Description and Findings

Larynx:
Normal appearance.

Trachea and Carina:
No evidence of significant pathology.

Left Lung:
No evidence of significant pathology.
Right Lung:
A nearly obstructing (>90% obstruction) endobronchial mass was identified proximally in the apical segment of the right upper lobe (B1).
The lesion was not traversed.

A second nearly obstructing (>90% obstruction) large endobronchial mass was identified proximally within the bronchus intermedius.
This lesion was successfully traversed, allowing visualization of the distal airway.
The bronchoscope was withdrawn and replaced with the EBUS bronchoscope to perform endobronchial ultrasound examination.
Lymph Node Assessment

Lymph node sizing and sampling were performed using endobronchial ultrasound for staging of non-small cell lung cancer.
Transbronchial needle aspiration was performed using an Olympus EBUS-TBNA needle at the following stations, with specimens sent for histopathologic examination:

Station 11L (interlobar): ROSE demonstrated adequate tissue.
Five needle passes obtained.

Station 4L (lower paratracheal): Not sampled.

Station 2L (upper paratracheal): ROSE demonstrated non-diagnostic tissue.
Five needle passes obtained.

Station 2R (upper paratracheal): Not sampled.

Station 4R (lower paratracheal): ROSE demonstrated adequate tissue.
Five needle passes obtained.

Station 7 (subcarinal): ROSE demonstrated adequate tissue. Five needle passes obtained.
Stations 11Rs and 11Ri were not sampled due to direct invasion by the primary tumor.
Therapeutic Intervention

The endobronchial tumor within the right bronchus intermedius was mechanically excised using rigid bronchoscopy and rigid suction.
Following tumor debulking, the right middle lobe bronchus was patent.
The right lower lobe bronchi were noted to be occluded at the subsegmental level due to malignant disease.
A portion of the endobronchial tumor arising from the apical segment of the right upper lobe and occluding the right upper lobe bronchus was also removed using biopsy forceps.
The anterior and posterior segmental bronchi of the right upper lobe were patent;
however, the apical segmental bronchus remained completely occluded.

Complications

No immediate complications.

Estimated Blood Loss

Less than 5 mL.
Impression

Known lung cancer of the right lower lobe

Malignant endobronchial mass in the apical segment of the right upper lobe (B1)

Malignant endobronchial mass in the bronchus intermedius

Successful lymph node sizing and sampling via EBUS-TBNA

Mechanical excision of endobronchial lesions in the bronchus intermedius and right upper lobe

Post-Procedure Diagnosis

Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies

The patient remained stable throughout the procedure and was transferred in good condition to the post-bronchoscopy recovery area for observation until discharge criteria were met.
Preliminary findings were discussed with the patient, and follow-up with the requesting service for final pathology results was recommended."""

# ==========================================
# 3. Entity Extraction Logic
# ==========================================
# List of entities to locate.
# Format: (Label, Search_String, Occurrence_Index)
# Occurrence_Index: 0 = first match, 1 = second, etc.
# If Occurrence_Index is -1, it finds the next instance sequentially from the last cursor.

entities_to_map = [
    ("PROC_METHOD", "Bronchoscopy", 0), # Header
    ("OBS_LESION", "lung cancer", 0),
    ("ANAT_LUNG_LOC", "right lower lobe", 0),
    ("OBS_LESION", "Malignant airway disease", 0),
    ("MEDICATION", "lidocaine", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 0),
    ("MEAS_VOL", "9 mL", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 1),
    ("DEV_INSTRUMENT", "Q180 slim video bronchoscope", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 2),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 3),
    ("DEV_INSTRUMENT", "black rigid bronchial tube", 0),
    ("MEAS_SIZE", "12.0–11.0 mm", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 4),
    ("MEAS_SIZE", "4.0-mm", 0),
    ("DEV_INSTRUMENT", "rigid telescope", 0),
    ("DEV_INSTRUMENT", "T180 therapeutic video bronchoscope", 0),
    ("ANAT_AIRWAY", "tracheobronchial tree", 5),
    ("ANAT_AIRWAY", "Trachea", 0),
    ("ANAT_AIRWAY", "Carina", 0),
    ("ANAT_LUNG_LOC", "Left Lung", 0),
    ("ANAT_LUNG_LOC", "Right Lung", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", ">90% obstruction", 0),
    ("OBS_LESION", "endobronchial mass", 0),
    ("ANAT_LUNG_LOC", "apical segment of the right upper lobe", 0),
    ("ANAT_LUNG_LOC", "B1", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", ">90% obstruction", 1),
    ("OBS_LESION", "endobronchial mass", 1),
    ("ANAT_AIRWAY", "bronchus intermedius", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "successfully traversed", 0),
    ("PROC_METHOD", "endobronchial ultrasound", 0),
    ("PROC_ACTION", "Lymph node sizing and sampling", 0),
    ("PROC_METHOD", "endobronchial ultrasound", 1),
    ("OBS_LESION", "non-small cell lung cancer", 0),
    ("PROC_ACTION", "Transbronchial needle aspiration", 0),
    ("DEV_NEEDLE", "Olympus EBUS-TBNA needle", 0),
    ("ANAT_LN_STATION", "Station 11L", 0),
    ("OBS_ROSE", "adequate tissue", 0),
    ("MEAS_COUNT", "Five needle passes", 0),
    ("ANAT_LN_STATION", "Station 4L", 0),
    ("ANAT_LN_STATION", "Station 2L", 0),
    ("OBS_ROSE", "non-diagnostic tissue", 0),
    ("MEAS_COUNT", "Five needle passes", 1),
    ("ANAT_LN_STATION", "Station 2R", 0),
    ("ANAT_LN_STATION", "Station 4R", 0),
    ("OBS_ROSE", "adequate tissue", 1),
    ("MEAS_COUNT", "Five needle passes", 2),
    ("ANAT_LN_STATION", "Station 7", 0),
    ("OBS_ROSE", "adequate tissue", 2),
    ("MEAS_COUNT", "Five needle passes", 3),
    ("ANAT_LN_STATION", "Stations 11Rs", 0),
    ("ANAT_LN_STATION", "11Ri", 0),
    ("OBS_LESION", "endobronchial tumor", 0),
    ("ANAT_AIRWAY", "bronchus intermedius", 1),
    ("PROC_ACTION", "mechanically excised", 0),
    ("PROC_METHOD", "rigid bronchoscopy", 0),
    ("DEV_INSTRUMENT", "rigid suction", 0),
    ("PROC_ACTION", "tumor debulking", 0),
    ("ANAT_AIRWAY", "right middle lobe bronchus", 0),
    ("OUTCOME_AIRWAY_LUMEN_POST", "patent", 0),
    ("ANAT_AIRWAY", "right lower lobe bronchi", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "occluded", 0),
    ("OBS_LESION", "endobronchial tumor", 1),
    ("ANAT_LUNG_LOC", "apical segment of the right upper lobe", 1),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "occluding", 0),
    ("ANAT_AIRWAY", "right upper lobe bronchus", 0),
    ("DEV_INSTRUMENT", "biopsy forceps", 0),
    ("ANAT_AIRWAY", "anterior", 0),
    ("ANAT_AIRWAY", "posterior segmental bronchi", 0),
    ("ANAT_LUNG_LOC", "right upper lobe", 2),
    ("OUTCOME_AIRWAY_LUMEN_POST", "patent", 1),
    ("ANAT_AIRWAY", "apical segmental bronchus", 0),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "completely occluded", 0),
    ("OUTCOME_COMPLICATION", "No immediate complications", 0),
    ("MEAS_VOL", "5 mL", 0),
    ("OBS_LESION", "lung cancer", 1),
    ("ANAT_LUNG_LOC", "right lower lobe", 1),
    ("OBS_LESION", "Malignant endobronchial mass", 0),
    ("ANAT_LUNG_LOC", "apical segment of the right upper lobe", 2),
    ("ANAT_LUNG_LOC", "B1", 1),
    ("OBS_LESION", "Malignant endobronchial mass", 1),
    ("ANAT_AIRWAY", "bronchus intermedius", 2),
    ("PROC_ACTION", "lymph node sizing and sampling", 0), # in Impression
    ("PROC_METHOD", "EBUS-TBNA", 0),
    ("PROC_ACTION", "Mechanical excision", 0),
    ("OBS_LESION", "endobronchial lesions", 0),
    ("ANAT_AIRWAY", "bronchus intermedius", 3),
    ("ANAT_LUNG_LOC", "right upper lobe", 3),
    ("PROC_METHOD", "flexible bronchoscopy", 0),
    ("PROC_METHOD", "endobronchial ultrasound", 2),
    ("PROC_ACTION", "biopsies", 0),
]

def map_entities(text, entity_list):
    mapped = []
    cursor_map = {} # Tracks last index for specific search terms to handle duplicates

    for label, substr, occurrence in entity_list:
        start_search_idx = 0
        
        # If looking for Nth occurrence
        if occurrence >= 0:
            current_found = -1
            search_idx = 0
            while current_found < occurrence:
                idx = text.find(substr, search_idx)
                if idx == -1:
                    break
                search_idx = idx + 1
                current_found += 1
            
            if current_found == occurrence and idx != -1:
                start = idx
                end = start + len(substr)
                mapped.append({
                    "span_id": f"{label}_{start}",
                    "note_id": NOTE_ID,
                    "label": label,
                    "text": substr,
                    "start": start,
                    "end": end
                })
        else:
            # Sequential search (not used in this specific list but good for robustness)
            pass

    return sorted(mapped, key=lambda x: x['start'])

# ==========================================
# 4. Processing & Output Generation
# ==========================================

def main():
    extracted_entities = map_entities(TEXT, entities_to_map)

    # 4.1 Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in extracted_entities]
    }
    
    ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    with open(ner_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 4.2 Update notes.jsonl
    notes_entry = {
        "id": NOTE_ID,
        "text": TEXT
    }
    notes_file = OUTPUT_DIR / "notes.jsonl"
    with open(notes_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(notes_entry) + "\n")

    # 4.3 Update spans.jsonl
    spans_file = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file, "a", encoding="utf-8") as f:
        for span in extracted_entities:
            f.write(json.dumps(span) + "\n")

    # 4.4 Update stats.json
    # Note: Loading provided stats context to simulate update, 
    # in real scenario would read from file system if available.
    if STATS_FILE.exists():
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Fallback initialization based on provided context
        stats = {
            "total_files": 191, "successful_files": 188, "total_notes": 188,
            "total_spans_raw": 3413, "total_spans_valid": 3404, 
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_entities)
    stats["total_spans_valid"] += len(extracted_entities)

    for span in extracted_entities:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 4.5 Validation & Logging
    alignment_file = ALIGNMENT_LOG
    with open(alignment_file, "a", encoding="utf-8") as f:
        for span in extracted_entities:
            extracted_text = TEXT[span["start"]:span["end"]]
            if extracted_text != span["text"]:
                f.write(f"MISMATCH: {span['span_id']} expected '{span['text']}' got '{extracted_text}'\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_entities)} entities.")

if __name__ == "__main__":
    main()