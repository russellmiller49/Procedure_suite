from pathlib import Path
import json
import os
import datetime

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTE_ID = "note_129"
RAW_TEXT = """NOTE_ID:  note_129 SOURCE_FILE: note_129.txt Procedure Performed:
Right-sided medical thoracoscopy (pleuroscopy) with pleural biopsies, talc pleurodesis, and chest tube insertion

Indication:
Exudative pleural effusion

Medications:
Moderate sedation per anesthesia record

Topical Anesthesia:
Lidocaine 1%, 20 mL

The procedure, including risks, benefits, and alternatives, was explained to the patient. All questions were answered, and informed consent was obtained and documented per institutional protocol. A history and physical examination were performed and updated in the pre-procedure assessment record. Pertinent laboratory studies and imaging were reviewed. A procedural time-out was performed.

The patient was positioned in the left lateral decubitus position on the procedural bed, with pressure points appropriately padded. The right-sided pleural entry site was identified using ultrasound guidance. The patient was sterilely prepped with chlorhexidine gluconate (ChloraPrep) and draped in the usual fashion. The entry site was infiltrated with 20 mL of 1% lidocaine. A 1-cm skin incision was made, and blunt dissection was carried down to the pleural space. Finger sweep revealed pleural adhesions, which were lysed bluntly.

An 8-mm disposable primary port was placed in the right fourth intercostal space at the mid-axillary line. After air entrainment and lung deflation, an Olympus semi-rigid pleuroscope was introduced through the trocar into the pleural cavity. Suction was applied, and approximately 1,600 mL of serosanguinous pleural fluid was removed.

The pleura appeared abnormal, with areas of isolated nodularity and plaques most consistent with pachypleuritis. No significant adhesions were present. Multiple biopsies of abnormal posterior parietal pleura were obtained using forceps. Additionally, a large pleural specimen was obtained using an electrocautery knife. Approximately nine total biopsies were obtained and sent for histopathological examination. Minimal bleeding was observed.

Following biopsies, talc pleurodesis was performed using a combination of talc poudrage and talc slurry, with a total of 5 grams of talc instilled. The primary port was then removed, and a 24-French chest tube was placed through the existing stoma, sutured in place, and connected to a pleuro-vac. The chest tube was dressed and covered with a transparent dressing.

The patient tolerated the procedure well.

A post-procedure chest radiograph demonstrated the chest tube in appropriate position, with the proximal side hole just at the pleural wall and a trace apical pneumothorax.

Complications:
None immediate

Estimated Blood Loss:
10 mL

Post-Procedure Diagnosis:
Pleural effusion

Recommendations:

Admit to inpatient service (planned)

Chest tube to suction; plan for removal once output is <150 mL/day

Pain management following talc pleurodesis, including narcotics as needed

Await pathology results

Inpatient Interventional Pulmonology consult team to follow"""

# Define entities to extract (Sequential occurrence in text)
# (Label, Text Segment)
ENTITIES_TO_EXTRACT = [
    ("LATERALITY", "Right-sided"),
    ("PROC_METHOD", "medical thoracoscopy"),
    ("PROC_METHOD", "pleuroscopy"),
    ("PROC_ACTION", "pleural biopsies"),
    ("PROC_ACTION", "talc pleurodesis"),
    ("PROC_ACTION", "chest tube insertion"),
    ("OBS_LESION", "Exudative pleural effusion"),
    ("MEDICATION", "Lidocaine"),
    ("MEAS_VOL", "20 mL"),
    ("LATERALITY", "left"),
    ("LATERALITY", "right-sided"),
    ("MEDICATION", "chlorhexidine gluconate"),
    ("MEDICATION", "lidocaine"),
    ("MEAS_VOL", "20 mL"), # 2nd occurrence
    ("MEAS_SIZE", "8-mm"),
    ("DEV_INSTRUMENT", "primary port"),
    ("LATERALITY", "right"),
    ("ANAT_PLEURA", "fourth intercostal space"),
    ("DEV_INSTRUMENT", "Olympus semi-rigid pleuroscope"),
    ("MEAS_VOL", "1,600 mL"),
    ("SPECIMEN", "pleural fluid"),
    ("OBS_LESION", "nodularity"),
    ("OBS_LESION", "plaques"),
    ("OBS_LESION", "pachypleuritis"),
    ("PROC_ACTION", "biopsies"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "electrocautery knife"),
    ("PROC_ACTION", "talc pleurodesis"), # 2nd occurrence
    ("PROC_METHOD", "talc poudrage"),
    ("PROC_METHOD", "talc slurry"),
    ("DEV_CATHETER_SIZE", "24-French"),
    ("DEV_CATHETER", "chest tube"),
    ("DEV_DEVICE", "pleuro-vac"),
    ("DEV_CATHETER", "chest tube"), # 2nd occurrence
    ("OUTCOME_COMPLICATION", "pneumothorax"),
    ("MEAS_VOL", "10 mL"),
    ("OBS_LESION", "Pleural effusion")
]

# Calculate spans
spans = []
search_start_index = 0
found_labels = []

for label, text in ENTITIES_TO_EXTRACT:
    start_idx = RAW_TEXT.find(text, search_start_index)
    if start_idx == -1:
        # Retry from beginning if not found (in case of out of order list, though list is ordered)
        # But for this specific note, we assume the list matches the text flow or we search from 0
        # To be safe for repeats (like "20 mL"), we must manage the search index carefully.
        # However, if we miss one because of order, we log it.
        # Let's try searching from 0 if not found, but be careful of duplicates.
        # Actually, let's just stick to the text flow for simplicity and correctness.
        print(f"Warning: Could not find '{text}' after index {search_start_index}")
        continue
    
    end_idx = start_idx + len(text)
    
    # Store span
    span = {
        "start": start_idx,
        "end": end_idx,
        "label": label,
        "text": text
    }
    spans.append(span)
    
    # Construct the granular span object for spans.jsonl
    granular_span = {
        "span_id": f"{label}_{start_idx}",
        "note_id": NOTE_ID,
        "label": label,
        "text": text,
        "start": start_idx,
        "end": end_idx
    }
    
    # Update stats tracking
    found_labels.append(label)
    
    # Move search index forward
    search_start_index = start_idx + 1

# 2. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": spans
}

ner_file_path = OUTPUT_DIR / "ner_dataset_all.jsonl"
with open(ner_file_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 3. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
notes_file_path = OUTPUT_DIR / "notes.jsonl"
with open(notes_file_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# 4. Update spans.jsonl
spans_file_path = OUTPUT_DIR / "spans.jsonl"
with open(spans_file_path, "a", encoding="utf-8") as f:
    for span in spans:
        # Create the object matching the schema: {"span_id":..., "note_id":..., "label":..., "text":..., "start":..., "end":...}
        obj = {
            "span_id": f"{span['label']}_{span['start']}",
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        }
        f.write(json.dumps(obj) + "\n")

# 5. Update stats.json
stats_file_path = OUTPUT_DIR / "stats.json"
if stats_file_path.exists():
    with open(stats_file_path, "r", encoding="utf-8") as f:
        stats_data = json.load(f)
else:
    # Fallback if file doesn't exist (though it should based on instructions)
    stats_data = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "label_counts": {}
    }

# Update counts
stats_data["total_files"] += 1
stats_data["successful_files"] += 1
stats_data["total_notes"] += 1
stats_data["total_spans_raw"] += len(spans)
stats_data["total_spans_valid"] += len(spans)

for label in found_labels:
    if label in stats_data["label_counts"]:
        stats_data["label_counts"][label] += 1
    else:
        stats_data["label_counts"][label] = 1

with open(stats_file_path, "w", encoding="utf-8") as f:
    json.dump(stats_data, f, indent=2)

# 6. Validate & Log (alignment_warnings.log)
log_file_path = OUTPUT_DIR / "alignment_warnings.log"
with open(log_file_path, "a", encoding="utf-8") as f:
    for span in spans:
        extracted_text = RAW_TEXT[span['start']:span['end']]
        if extracted_text != span['text']:
            warning = {
                "note_id": NOTE_ID,
                "label": span['label'],
                "span_text": span['text'],
                "start": span['start'],
                "end": span['end'],
                "issue": f"alignment_error: extracted='{extracted_text}' vs span='{span['text']}'"
            }
            f.write(json.dumps(warning) + "\n")

print(f"Successfully processed {NOTE_ID} and updated all files.")