from pathlib import Path
import json
import os
import datetime

# Configuration
NOTE_ID = "note_154"
RAW_TEXT = """NOTE_ID:  note_154 SOURCE_FILE: note_154.txt Indications: right lower lobe nodule 
Medications: Propofol infusion via anesthesia assistance  
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords were normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal;
there are no endobronchial lesions. We then removed the diagnostic Q190 bronchoscopy and the super-dimension navigational catheter was inserted through the T190 therapeutic bronchoscope and advanced into the airway.
Using navigational map we attempted to advance the 90 degree edge catheter into the proximity of the lesion within the right lower lobe.
Confirmation of placement once at the point of interest with radial ultrasound showed a concentric view within the lesion.
Biopsies were then performed with a variety of instruments to include peripheral needle, triple needle brush and forceps, under fluoroscopic visualization.
After adequate samples were obtained the bronchoscope was removed and the procedure completed
Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc.
Post Procedure Diagnosis:
- Flexible bronchoscopy with successful navigational biopsy of right lower lobe nodule.  
Recommendations
- Await final pathology"""

# Define the entities to extract (Sequential order in text)
# Format: (Text, Label)
ENTITIES_TO_EXTRACT = [
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("nodule", "OBS_LESION"),
    ("Propofol", "MEDICATION"),
    ("General Anesthesia", "PROC_METHOD"),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("diagnostic Q190 bronchoscopy", "DEV_INSTRUMENT"),
    ("super-dimension navigational catheter", "DEV_INSTRUMENT"),
    ("T190 therapeutic bronchoscope", "DEV_INSTRUMENT"),
    ("navigational map", "PROC_METHOD"),
    ("90 degree edge catheter", "DEV_INSTRUMENT"),
    ("lesion", "OBS_LESION"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("radial ultrasound", "PROC_METHOD"),
    ("concentric view", "OBS_LESION"),
    ("lesion", "OBS_LESION"),
    ("Biopsies", "PROC_ACTION"),
    ("peripheral needle", "DEV_NEEDLE"),
    ("triple needle brush", "DEV_INSTRUMENT"),
    ("forceps", "DEV_INSTRUMENT"),
    ("fluoroscopic visualization", "PROC_METHOD"),
    ("No immediate complications", "OUTCOME_COMPLICATION"),
    ("Less than 5 cc", "MEAS_VOL"),
    ("Flexible bronchoscopy", "PROC_METHOD"),
    ("navigational", "PROC_METHOD"),
    ("biopsy", "PROC_ACTION"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("nodule", "OBS_LESION"),
]

# Output setup
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ALIGNMENT_LOG = OUTPUT_DIR / "alignment_warnings.log"

def update_dataset():
    """
    Main function to process the note, calculate offsets, and update JSONL files.
    """
    
    extracted_entities = []
    current_pos = 0
    
    # 1. Calculate Offsets
    for text_span, label in ENTITIES_TO_EXTRACT:
        start_idx = RAW_TEXT.find(text_span, current_pos)
        
        if start_idx == -1:
            log_msg = f"ERROR: Could not find span '{text_span}' after index {current_pos} in note {NOTE_ID}"
            print(log_msg)
            with open(ALIGNMENT_LOG, "a") as log:
                log.write(f"{datetime.datetime.now()}: {log_msg}\n")
            continue
            
        end_idx = start_idx + len(text_span)
        
        # Verify alignment
        extracted_text = RAW_TEXT[start_idx:end_idx]
        if extracted_text != text_span:
            log_msg = f"MISMATCH: Expected '{text_span}', got '{extracted_text}' at {start_idx}:{end_idx}"
            print(log_msg)
            with open(ALIGNMENT_LOG, "a") as log:
                log.write(f"{datetime.datetime.now()}: {log_msg}\n")
            continue

        extracted_entities.append({
            "label": label,
            "start": start_idx,
            "end": end_idx,
            "text": text_span
        })
        
        # Update current_pos to avoid finding the same instance again if it appears later
        current_pos = end_idx

    # 2. Update ner_dataset_all.jsonl
    dataset_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": i,
                "label": e["label"],
                "start_offset": e["start"],
                "end_offset": e["end"]
            }
            for i, e in enumerate(extracted_entities)
        ]
    }
    
    with open(dataset_file, "a") as f:
        f.write(json.dumps(ner_entry) + "\n")
    print(f"Updated {dataset_file}")

    # 3. Update notes.jsonl
    notes_file = OUTPUT_DIR / "notes.jsonl"
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    
    with open(notes_file, "a") as f:
        f.write(json.dumps(note_entry) + "\n")
    print(f"Updated {notes_file}")

    # 4. Update spans.jsonl
    spans_file = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file, "a") as f:
        for ent in extracted_entities:
            span_entry = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "span_text": ent['text'],
                "start_char": ent['start'],
                "end_char": ent['end']
            }
            f.write(json.dumps(span_entry) + "\n")
    print(f"Updated {spans_file}")

    # 5. Update stats.json
    stats_file = OUTPUT_DIR / "stats.json"
    if stats_file.exists():
        with open(stats_file, "r") as f:
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

    # Update counts
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(extracted_entities)
    stats["total_spans_valid"] += len(extracted_entities)

    # Update label counts
    for ent in extracted_entities:
        label = ent['label']
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Updated {stats_file}")

if __name__ == "__main__":
    update_dataset()