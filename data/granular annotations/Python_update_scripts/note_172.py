import json
import re
import os
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. Configuration & Path Setup
# ------------------------------------------------------------------------------
NOTE_ID = "note_172"
SCRIPT_DIR = Path(__file__).resolve()
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = SCRIPT_DIR.parents[2] / "ml_training" / "granular_ner"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_JSONL_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_JSONL_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ------------------------------------------------------------------------------
# 2. Raw Text & Entity Definition
# ------------------------------------------------------------------------------
# Raw text reconstructed from the input, stripping source tags.
RAW_TEXT = (
    "Indications: Left upper lobe nodule \n"
    "Medications: Propofol infusion via anesthesia assistance  \n"
    "Procedure, risks, benefits, and alternatives were explained to the patient.\n"
    "All questions were answered and informed consent was documented as per institutional protocol.\n"
    "A history and physical were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.\n"
    "A time-out was performed prior to the intervention. \n"
    "Following intravenous medications as per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree the Q190 video bronchoscope was introduced through the mouth.\n"
    "The vocal cords appeared normal. The subglottic space was normal. The trachea is of normal caliber. The carina was sharp.\n"
    "All left and right sided airways were normal without endobronchial disease.\n"
    "The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.\n"
    "A systematic hilar and mediastinal lymph node survey was carried out.\n"
    "Sampling criteria (5mm short axis diameter) were met in station 7 and 11L.\n"
    "Sampling by transbronchial needle aspiration was performed in these lymph nodes using an Olympus Vizishot  EBUS TBNA 19 gauge needle.\n"
    "All samples were sent for routine cytology. We then tried to visualize the FDG avid station 5 lymph node seen on PET CT through the pulmonary artery but were unable to clearly visualize the node and thus could not sample from the mainstem approach (transvascular).\n"
    "We then removed the EBUS bronchoscopy. At this point the patient had lost her IV access and developed laryngospasm prompting us to bronchoscopically intubate the patient with a size 8.5 ETT which was easily passed through the vocal cords and into the lower trachea before being secured in place.\n"
    "The Q190 bronchscope was then advanced, using anatomical knowledge,  into the proximal left upper lobe adjacent to the station 5 lymph node and utilizing radial EBUS attempted to sample this node through an airway approach with a transbronchial needle approach.\n"
    "ROSE was unrevealing and we subsequently the super-dimension navigational catheter was inserted through the therapeutic bronchoscope and advanced into the airway.\n"
    "Using navigational map we advanced the 180 degree edge catheter into the proximity of the lesion within the left upper lobe.\n"
    "Confirmation of placement was attempted once we were in the vicinity of the point of interest with radial ultrasound.\n"
    "The lesion however could not be adequately visualized. Multiple attempts to navigate to the lesion were unfruitful and we subsequently completed the procedure without attempting to sample the left upper lobe peripheral lesion.\n"
    "Complications: No immediate complications\n"
    "Estimated Blood Loss: Less than 5 cc.\n"
    "Post Procedure Diagnosis:\n"
    "- Negative Staging EBUS on preliminary evaluation \n"
    "- Flexible bronchoscopy with unsuccessful electromagnetic navigation to the left upper nodule\n"
    "- Await final pathology  \n"
    "- Discharge once post-op criteria met"
)

# Entities based on Label_guide_UPDATED.csv
# Order matches occurrence in text to allow sequential searching.
ENTITIES_TO_EXTRACT = [
    ("Left upper lobe", "ANAT_LUNG_LOC"),
    ("nodule", "OBS_LESION"),
    ("Propofol", "MEDICATION"),
    ("upper airway", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("airways", "ANAT_AIRWAY"),
    ("video bronchoscope", "DEV_INSTRUMENT"),
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("hilar", "ANAT_LN_STATION"),
    ("mediastinal", "ANAT_LN_STATION"),
    ("station 7", "ANAT_LN_STATION"),
    ("11L", "ANAT_LN_STATION"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("19 gauge", "DEV_NEEDLE"),
    ("station 5", "ANAT_LN_STATION"),
    ("EBUS", "PROC_METHOD"),  # In "EBUS bronchoscopy"
    ("laryngospasm", "OUTCOME_COMPLICATION"),
    ("intubate", "PROC_ACTION"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("lower trachea", "ANAT_AIRWAY"),
    ("Q190 bronchscope", "DEV_INSTRUMENT"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("station 5", "ANAT_LN_STATION"),
    ("radial EBUS", "PROC_METHOD"),
    ("unrevealing", "OBS_ROSE"),
    ("super-dimension navigational catheter", "DEV_INSTRUMENT"),
    ("airway", "ANAT_AIRWAY"),
    ("180 degree edge catheter", "DEV_INSTRUMENT"),
    ("lesion", "OBS_LESION"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("radial ultrasound", "PROC_METHOD"),
    ("lesion", "OBS_LESION"),
    ("lesion", "OBS_LESION"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("lesion", "OBS_LESION"),
    ("No immediate complications", "OUTCOME_COMPLICATION"),
    ("Less than 5 cc", "MEAS_VOL"),
    ("EBUS", "PROC_METHOD"),
    ("Flexible bronchoscopy", "PROC_ACTION"),
    ("electromagnetic navigation", "PROC_METHOD"),
    ("left upper", "ANAT_LUNG_LOC"),
    ("nodule", "OBS_LESION")
]

# ------------------------------------------------------------------------------
# 3. Processing Logic
# ------------------------------------------------------------------------------

def extract_entities_sequentially(text, entity_list):
    """
    Finds entities in the text sequentially to handle repeated terms correctly.
    """
    results = []
    current_index = 0
    
    for term, label in entity_list:
        # Search for the term starting from the current_index
        start = text.find(term, current_index)
        
        if start == -1:
            # Fallback: if not found (e.g. minor typo in manual list), log a warning
            print(f"WARNING: Could not find '{term}' after index {current_index}")
            continue
            
        end = start + len(term)
        
        span_obj = {
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": term,
            "start": start,
            "end": end
        }
        results.append(span_obj)
        
        # Move index forward, but allow overlapping starts if strictly necessary 
        # (though mostly we move past). For safety, move just past start to allow 
        # tight packing, or past end. Here we move to end to avoid sub-match confusion.
        current_index = end 

    return results

def update_stats(stats_path, new_entities):
    """
    Updates the stats.json file with new counts.
    """
    if stats_path.exists():
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "label_counts": {}
        }

    # Global counters
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(new_entities)
    stats["total_spans_valid"] += len(new_entities)

    # Label counts
    for ent in new_entities:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def append_jsonl(path, data):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + "\n")

# ------------------------------------------------------------------------------
# 4. Main Execution
# ------------------------------------------------------------------------------

def main():
    # A. Extract Entities
    extracted_spans = extract_entities_sequentially(RAW_TEXT, ENTITIES_TO_EXTRACT)

    # B. Prepare Records
    # 1. For ner_dataset_all.jsonl
    ner_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_spans
    }

    # 2. For notes.jsonl
    note_record = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # C. Write to Files
    print(f"Updating {NER_DATASET_PATH}...")
    append_jsonl(NER_DATASET_PATH, ner_record)

    print(f"Updating {NOTES_JSONL_PATH}...")
    append_jsonl(NOTES_JSONL_PATH, note_record)

    print(f"Updating {SPANS_JSONL_PATH}...")
    for span in extracted_spans:
        append_jsonl(SPANS_JSONL_PATH, span)

    # D. Update Stats
    print(f"Updating {STATS_PATH}...")
    update_stats(STATS_PATH, extracted_spans)

    # E. Validation
    with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
        for span in extracted_spans:
            s, e = span["start"], span["end"]
            sliced_text = RAW_TEXT[s:e]
            if sliced_text != span["text"]:
                error_msg = f"ALIGNMENT ERROR {NOTE_ID}: Expected '{span['text']}', found '{sliced_text}' at [{s}:{e}]"
                print(error_msg)
                log_file.write(error_msg + "\n")

    print(f"Successfully processed {NOTE_ID} with {len(extracted_spans)} entities.")

if __name__ == "__main__":
    main()