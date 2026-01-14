from pathlib import Path
import json
import os
import re

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_222"
# Note: The input text below has been cleaned of the '' tags 
# commonly found in RAG outputs to represent the raw medical text.
RAW_TEXT = """NOTE_ID:  note_222 SOURCE_FILE: note_222.txt PREOPERATIVE DIAGNOSIS: Diffuse parenchymal lung disease
POSTOPERATIVE DIAGNOSIS: Diffuse parenchymal lung disease 

PROCEDURE PERFORMED: Rigid bronchoscopy with transbronchial cryobiopsy

INDICATIONS: Diffuse parenchymal lung disease

Consent was obtained from the patient prior to the procedure after explaining in lay terms the indications, details of the procedure, and potential risks and alternatives.
The patient acknowledged and provided consent. 

Sedation: General Anesthesia

DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
After receiving analgesia and paralytics, the patient was mask-bagged and once preoxygenated, an 8.0 endotracheal tube was inserted bronchoscopically using an Olympus T180 therapeutic bronchoscope with an Arent enbobronchial blocker attached to the bronchoscope externally.
The blocker was then advanced into the right lower lobe, and the endotracheal tube was advanced over the bronchoscope into the mid trachea and attached to the ventilator.
After an unremarkable inspection bronchoscopy, the 2.4 mm reusable ERBE cryoprobe was inserted through the past the balloon into the right lower lobe anterior segment under fluoroscopic guidance.
Once the pleural margin was reached, the probe was withdrawn approximately 1 cm, and the cryoprobe was activated for 4 seconds.
The flexible bronchoscope and cryoprobe were then removed en-bloc, and the endobronchial blocker balloon was immediately inflated after removal.
One specimen was obtained from the cryoprobe, the flexible bronchoscope was reinserted, and the balloon was slowly deflated to assess for distal bleeding.
No blood was noted, and this was repeated for a total of 5 biopsies.
Cryobiopsies were then performed in the lateral segment of the right lower lobe using the same technique.
After the second biopsy, significant blood was encountered when the balloon was deflated.
The balloon was reinflated for 5 minutes to protect against blood soiling the airways, and 20cc of iced saline was instilled through the blocker to promote hemostasis.
The balloon was released again, and bleeding was noted to have stopped.
One more biopsy was completed in the segment for a total of 3. Once it was confirmed that there was no active bleeding, the flexible bronchoscope was removed.
Following the completion of the procedure, fluoroscopic evaluation of the pleura was performed to assess for pneumothorax, and a moderate right-sided pneumothorax was visualized.
The right lateral chest wall was marked, prepped, and draped in the usual sterile fashion.
1% Lidocaine was used to anesthetize the skin down to the rib and along the proposed insertion path for the tube.
A 20-gauge Yueh-centesis needle with a syringe attached was inserted into the pleural space under fluoroscopic visualization, with aspiration of air to verify placement.
The needle was then removed, and the catheter was left in place.
A guide wire was advanced into the pleural space through the catheter, and the catheter was then withdrawn.
A 0.5cm incision was made through the skin, and the subcutaneous tissues were dilated.
The 14Fr Wayne pigtail chest drain was inserted into the pleural space. The drain was immediately connected to a Pleur-evac.
Adequate placement was confirmed by air leak and fluoroscopy. The tube was sutured in place, and a dressing was applied.
At this point, the endotracheal tube was removed, and the procedure was completed.
Estimated Blood Loss: 10cc
Complications: Pneumothorax requiring chest tube insertion

Assessment and Plan:
- Successful lung cryobiopsy complicated by pneumothorax requiring pigtail insertion
- CXR pending
- Admit to Internal medicine for chest tube management
- Await pathological evaluation of tissue"""

# Output directories
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = Path("stats.json") # Assumes stats.json is in current working dir for update
ALIGNMENT_LOG = Path("alignment_warnings.log")

# =============================================================================
# ENTITY EXTRACTION LOGIC
# =============================================================================
# Helper to find exact spans.
# We store (Label, Text_Snippet, Occurrence_Index) to handle duplicates.
# Occurrence_Index 0 = first match, 1 = second match, etc.

entities_to_find = [
    ("OBS_LESION", "Diffuse parenchymal lung disease", 0), # Pre-op
    ("OBS_LESION", "Diffuse parenchymal lung disease", 1), # Post-op
    ("PROC_METHOD", "Rigid bronchoscopy", 0),
    ("PROC_ACTION", "transbronchial cryobiopsy", 0),
    ("OBS_LESION", "Diffuse parenchymal lung disease", 2), # Indications
    ("DEV_INSTRUMENT", "Olympus T180 therapeutic bronchoscope", 0),
    ("DEV_INSTRUMENT", "enbobronchial blocker", 0),
    ("DEV_INSTRUMENT", "blocker", 0), # "The blocker was then advanced"
    ("ANAT_LUNG_LOC", "right lower lobe", 0),
    ("ANAT_AIRWAY", "mid trachea", 0),
    ("PROC_ACTION", "inspection bronchoscopy", 0),
    ("MEAS_SIZE", "2.4 mm", 0),
    ("DEV_INSTRUMENT", "cryoprobe", 0),
    ("DEV_INSTRUMENT", "balloon", 0), # "...past the balloon"
    ("ANAT_LUNG_LOC", "right lower lobe anterior segment", 0),
    ("PROC_METHOD", "fluoroscopic guidance", 0),
    ("ANAT_PLEURA", "pleural margin", 0),
    ("DEV_INSTRUMENT", "probe", 0),
    ("DEV_INSTRUMENT", "cryoprobe", 1), # "...and the cryoprobe was activated"
    ("MEAS_TIME", "4 seconds", 0),
    ("DEV_INSTRUMENT", "flexible bronchoscope", 0),
    ("DEV_INSTRUMENT", "cryoprobe", 2), # "...and cryoprobe were then removed"
    ("DEV_INSTRUMENT", "endobronchial blocker", 1), # "...endobronchial blocker balloon"
    ("DEV_INSTRUMENT", "balloon", 1), # "...blocker balloon was immediately"
    ("MEAS_COUNT", "One", 0),
    ("SPECIMEN", "specimen", 0),
    ("DEV_INSTRUMENT", "cryoprobe", 3), # "...from the cryoprobe"
    ("DEV_INSTRUMENT", "flexible bronchoscope", 1),
    ("DEV_INSTRUMENT", "balloon", 2), # "...and the balloon was slowly"
    ("OBS_FINDING", "bleeding", 0),
    ("OBS_FINDING", "blood", 0), # "No blood was noted"
    ("MEAS_COUNT", "5", 0),
    ("PROC_ACTION", "biopsies", 0),
    ("PROC_ACTION", "Cryobiopsies", 0),
    ("ANAT_LUNG_LOC", "lateral segment of the right lower lobe", 0),
    ("PROC_ACTION", "biopsy", 0),
    ("OBS_FINDING", "blood", 1), # "significant blood"
    ("DEV_INSTRUMENT", "balloon", 3), # "...when the balloon was deflated"
    ("DEV_INSTRUMENT", "balloon", 4), # "The balloon was reinflated"
    ("MEAS_TIME", "5 minutes", 0),
    ("OBS_FINDING", "blood", 2), # "...protect against blood soiling"
    ("ANAT_AIRWAY", "airways", 0),
    ("MEAS_VOL", "20cc", 0),
    ("DEV_INSTRUMENT", "blocker", 1), # "...through the blocker"
    ("DEV_INSTRUMENT", "balloon", 5), # "The balloon was released"
    ("OBS_FINDING", "bleeding", 1), # "...and bleeding was noted"
    ("MEAS_COUNT", "One", 1),
    ("PROC_ACTION", "biopsy", 1),
    ("MEAS_COUNT", "3", 0),
    ("OBS_FINDING", "bleeding", 2), # "active bleeding"
    ("DEV_INSTRUMENT", "flexible bronchoscope", 2),
    ("PROC_METHOD", "fluoroscopic evaluation", 0),
    ("ANAT_PLEURA", "pleura", 0),
    ("OBS_LESION", "pneumothorax", 0), # "...assess for pneumothorax"
    ("OBS_LESION", "pneumothorax", 1), # "...pneumothorax was visualized"
    ("LATERALITY", "right", 1), # "The right lateral..." - Skip 0 (right lower lobe)
    ("ANAT_PLEURA", "chest wall", 0),
    ("MEDICATION", "Lidocaine", 0),
    ("DEV_NEEDLE", "20-gauge Yueh-centesis needle", 0),
    ("ANAT_PLEURA", "pleural space", 0),
    ("PROC_METHOD", "fluoroscopic visualization", 0),
    ("PROC_ACTION", "aspiration", 0),
    ("DEV_NEEDLE", "needle", 0), # "The needle was then removed"
    ("DEV_CATHETER", "catheter", 0), # "...and the catheter was left"
    ("DEV_INSTRUMENT", "guide wire", 0),
    ("ANAT_PLEURA", "pleural space", 1),
    ("DEV_CATHETER", "catheter", 1), # "...through the catheter"
    ("DEV_CATHETER", "catheter", 2), # "...and the catheter was then"
    ("MEAS_SIZE", "0.5cm", 0),
    ("PROC_ACTION", "incision", 0),
    ("DEV_CATHETER_SIZE", "14Fr", 0),
    ("DEV_CATHETER", "Wayne pigtail chest drain", 0),
    ("ANAT_PLEURA", "pleural space", 2),
    ("DEV_CATHETER", "drain", 0), # "The drain was immediately..."
    ("PROC_METHOD", "fluoroscopy", 0),
    ("DEV_CATHETER", "tube", 0), # "The tube was sutured"
    ("MEAS_VOL", "10cc", 0),
    ("OUTCOME_COMPLICATION", "Pneumothorax requiring chest tube insertion", 0),
    ("PROC_ACTION", "cryobiopsy", 1), # "Successful lung cryobiopsy"
    ("OUTCOME_COMPLICATION", "pneumothorax requiring pigtail insertion", 0),
]

# Refined Logic to handle entity extraction
final_spans = []
search_start = 0

# We process entity definitions to find their precise offsets
# We must be careful not to consume duplicates in wrong order.
# The list above is roughly chronological which helps.

processed_entities = []

# This simple finder will search from the beginning of text each time
# but skip N occurrences as defined in the tuple (text, N).
for label, text, occ_idx in entities_to_find:
    current_idx = -1
    search_pos = 0
    found_start = -1
    found_end = -1
    
    # Find the Nth occurrence
    for i in range(occ_idx + 1):
        found_start = RAW_TEXT.find(text, search_pos)
        if found_start == -1:
            break
        search_pos = found_start + 1
        current_idx = i
        
    if current_idx == occ_idx and found_start != -1:
        found_end = found_start + len(text)
        final_spans.append({
            "span_id": f"{label}_{found_start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text,
            "start": found_start,
            "end": found_end
        })
    else:
        print(f"WARNING: Could not find occurrence {occ_idx} of '{text}'")

# Sort spans by start index
final_spans = sorted(final_spans, key=lambda x: x["start"])

# =============================================================================
# FILE GENERATION
# =============================================================================

# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": final_spans
}

ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
with open(ner_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# 2. Update notes.jsonl
notes_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
notes_file = OUTPUT_DIR / "notes.jsonl"
with open(notes_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(notes_entry) + "\n")

# 3. Update spans.jsonl
spans_file = OUTPUT_DIR / "spans.jsonl"
with open(spans_file, "a", encoding="utf-8") as f:
    for span in final_spans:
        f.write(json.dumps(span) + "\n")

# 4. Update stats.json
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
    
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(final_spans)
    stats["total_spans_valid"] += len(final_spans)
    
    # Update label counts
    for span in final_spans:
        lbl = span["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1
            
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

# 5. Validation & Logging
with open(ALIGNMENT_LOG, "a", encoding="utf-8") as log:
    for span in final_spans:
        extracted = RAW_TEXT[span["start"]:span["end"]]
        if extracted != span["text"]:
            log.write(f"MISMATCH in {NOTE_ID}: {span['label']} expected '{span['text']}' but got '{extracted}' at {span['start']}\n")

print(f"Successfully processed {NOTE_ID} with {len(final_spans)} entities.")