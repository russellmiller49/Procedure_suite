from pathlib import Path
import json
import os
import datetime

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTE_ID = "note_173"
RAW_TEXT = """NOTE_ID:  note_173 SOURCE_FILE: note_173.txt Procedure Name: Peripheral bronchoscopy with radial EBUS localization.
Indications: Pulmonary nodule requiring diagnosis
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient. All questions were answered and informed consent was documented as per institutional protocol. A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed. A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree. The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal. The trachea was of normal caliber. The carina was sharp. The tracheobronchial tree was examined to at least the first subsegmental level without endobronchial lesions visualized. Anatomy was normal with exception of what appears to be a fused anterior segment of left upper lobe with lingula. The video bronchoscope was then removed and the T190 Therapeutic video bronchoscope was inserted into the airway.  A sheath catheter was advanced through the working channel into the segment of suspicion. A radial US was advanced through the sheath and concentric view of lesion was seen. Using fluoroscopy, transbronchial needle biopsies were performed. ROSE was consistent with malignancy. We then performed 6 bronchoscopic lung biopsies in the same area under fluoroscopic visualization with forceps.   
We then removed the therapeutic scope and re0inserted the Q190 videoscope. After cleaning of blood and debris no active bleeding and none was identified. Fluoroscopy was then used to scan for evidence of pneumothorax which was not seen. The bronchoscope was removed and the procedure completed. 

Complications: 	
-None 
Estimated Blood Loss:  5 cc
Recommendations:
- post-procedure CXR
- Await biopsy results 
- Discharge home once criteria met.

"""

# Define entities to extract
# Order matters for find() with start index updates
entities_to_find = [
    {"label": "PROC_METHOD", "text": "Peripheral bronchoscopy"},
    {"label": "PROC_METHOD", "text": "radial EBUS"},
    {"label": "OBS_LESION", "text": "Pulmonary nodule"},
    {"label": "MEDICATION", "text": "Propofol"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "DEV_INSTRUMENT", "text": "Q190 video bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "laryngeal mask airway"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "DEV_INSTRUMENT", "text": "laryngeal mask airway"},
    {"label": "ANAT_AIRWAY", "text": "vocal cords"},
    {"label": "ANAT_AIRWAY", "text": "subglottic space"},
    {"label": "ANAT_AIRWAY", "text": "trachea"},
    {"label": "ANAT_AIRWAY", "text": "carina"},
    {"label": "ANAT_AIRWAY", "text": "tracheobronchial tree"},
    {"label": "ANAT_LUNG_LOC", "text": "anterior segment of left upper lobe"},
    {"label": "ANAT_LUNG_LOC", "text": "lingula"},
    {"label": "DEV_INSTRUMENT", "text": "T190 Therapeutic video bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "sheath catheter"},
    {"label": "PROC_METHOD", "text": "radial US"},
    {"label": "OBS_LESION", "text": "concentric view"},
    {"label": "PROC_METHOD", "text": "fluoroscopy"},
    {"label": "PROC_ACTION", "text": "transbronchial needle biopsies"},
    {"label": "OBS_ROSE", "text": "malignancy"},
    {"label": "MEAS_COUNT", "text": "6"},
    {"label": "PROC_ACTION", "text": "bronchoscopic lung biopsies"},
    {"label": "PROC_METHOD", "text": "fluoroscopic visualization"},
    {"label": "DEV_INSTRUMENT", "text": "forceps"},
    {"label": "DEV_INSTRUMENT", "text": "Q190 videoscope"},
    {"label": "OBS_FINDING", "text": "active bleeding"},
    {"label": "PROC_METHOD", "text": "Fluoroscopy"},
    {"label": "OUTCOME_COMPLICATION", "text": "None"},
    {"label": "MEAS_VOL", "text": "5 cc"}
]

def update_pipeline():
    # 1. Calculate Indices
    extracted_entities = []
    search_start_index = 0
    
    # We must be careful not to skip occurrences if the order in list doesn't match text order
    # However, for simplicity and accuracy, we will search from the beginning for each, 
    # but to handle duplicates (like 'tracheobronchial tree'), we need a more robust approach.
    # Approach: Iterate through the text, finding entities. To handle duplicates correctly 
    # based on the list order provided above (which roughly follows text order), we will 
    # maintain a cursor.
    
    current_cursor = 0
    
    for item in entities_to_find:
        start = RAW_TEXT.find(item["text"], current_cursor)
        if start == -1:
            # Fallback to search from beginning if not found after cursor (unsorted list case)
            start = RAW_TEXT.find(item["text"])
        
        if start != -1:
            end = start + len(item["text"])
            extracted_entities.append({
                "label": item["label"],
                "text": item["text"],
                "start": start,
                "end": end
            })
            # Update cursor to avoid finding the same instance if intended to find the next
            # But only if we are confident the list is ordered. 
            # Given the analysis, the list is roughly ordered.
            current_cursor = start + 1
        else:
            print(f"Warning: Entity '{item['text']}' not found in text.")

    # 2. Update ner_dataset_all.jsonl
    ner_data = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": extracted_entities
    }
    
    ner_file_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
    with open(ner_file_path, "a") as f:
        f.write(json.dumps(ner_data) + "\n")
    
    # 3. Update notes.jsonl
    notes_data = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    notes_file_path = OUTPUT_DIR / "notes.jsonl"
    with open(notes_file_path, "a") as f:
        f.write(json.dumps(notes_data) + "\n")

    # 4. Update spans.jsonl
    spans_file_path = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file_path, "a") as f:
        for ent in extracted_entities:
            span_record = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "span_text": ent['text'],
                "start_char": ent['start'],
                "end_char": ent['end']
            }
            f.write(json.dumps(span_record) + "\n")

    # 5. Update stats.json
    stats_file_path = OUTPUT_DIR / "stats.json"
    if stats_file_path.exists():
        with open(stats_file_path, "r") as f:
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
    
    for ent in extracted_entities:
        label = ent["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(stats_file_path, "w") as f:
        json.dump(stats, f, indent=2)

    # 6. Validate & Log
    log_file_path = OUTPUT_DIR / "alignment_warnings.log"
    with open(log_file_path, "a") as f:
        for ent in extracted_entities:
            sliced_text = RAW_TEXT[ent["start"]:ent["end"]]
            if sliced_text != ent["text"]:
                error_msg = {
                    "note_id": NOTE_ID,
                    "label": ent["label"],
                    "span_text": ent["text"],
                    "start": ent["start"],
                    "end": ent["end"],
                    "issue": f"alignment_error: extracted='{sliced_text}' vs span='{ent['text']}'"
                }
                f.write(json.dumps(error_msg) + "\n")

if __name__ == "__main__":
    update_pipeline()