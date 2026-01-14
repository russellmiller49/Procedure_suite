import json
import os
import re
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_247"

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
# 2. Raw Text Data
# ==========================================
RAW_TEXT = """INDICATION FOR OPERATION:  Timothy Grace is a 56 year old-year-old male with cystic fibrosis who presents with a cavitary lesion in right lower lobe.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT : Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form / provided consent over the phone.
The consent was witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS: R91.1 Solitary Lung Nodule
POSTOPERATIVE DIAGNOSIS:  R91.1 Solitary Lung Nodule
PROCEDURE:  
31624 Dx bronchoscope/lavage (BAL)    
31625 Endobronchial Biopsy(s)
  
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Flexible Hybrid (Pediatric) Bronchoscope
ESTIMATED BLOOD LOSS:   Moderate
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After successful induction of anesthesia, a timeout was performed to confirm the patient’s identity, the procedure, and the location.
Following administration of intravenous medications and topical anesthesia to the upper airway, a P190 hybrid video bronchoscope was introduced through the endotracheal tube.
The trachea appeared normal. The bronchoscope was advanced to the main carina, which was noted to have a sharp angle.
The scope was then directed into the left mainstem bronchus, allowing visualization of all segments and subsegments of the left upper lobe, lingula, and lower lobe;
no abnormalities were identified on the left side. The bronchoscope was withdrawn to the trachea and advanced into the right mainstem bronchus.
All segments and subsegments of the right upper, middle, and lower lobes were examined.
Purulent material was observed emanating from the superior segment of the right lower lobe.
The bronchoscope was wedged in this segment, and a bronchoalveolar lavage was performed using 60 cc of instilled saline, yielding 20 cc of return fluid.
During the lavage, a cavity was visualized in the superior segment of the right lower lobe containing a well-demarcated soft tissue mass with a granular texture, consistent with a mycetoma.
The right airway anatomy was notable for fusion of the apical and posterior segments in the right upper lobe;
aside from the cavity, no additional masses or lesions were identified.
After thorough inspection, multiple forceps biopsies were obtained from the mass within the cavity.
Moderate bleeding ensued and was effectively managed with 4 cc of epinephrine, 30 cc of iced saline, and wedging of the scope in the affected segment, which successfully controlled the hemorrhage.
The bronchoscope was removed, and the procedure was completed without further incident.
The patient tolerated the procedure well, with no immediate complications.
At the conclusion, he was extubated in the operating room and transferred to the post-anesthesia care unit (PACU) in stable condition.
SPECIMEN(S): 
BAL from right lower lobe: Sent for respiratory and fungal cultures, AFB, cytology, and galactomannan.
Right lower lobe forceps biopsy: Sent for pathology and culture.
IMPRESSION/PLAN: Timothy Grace is a 56 year old-year-old male who underwent bronchoscopy for evaluation of a cavitary lesion in the right lower lobe.
•	Transfer to PACU
•	Obtain chest X-ray
•	Discharge home once cleared by PACU
•	Await pathology results."""

# ==========================================
# 3. Entity Definitions
# ==========================================
# We define entities with strict order or specific unique text to ensure correct mapping.
# Format: (Label, Text_Segment)
# Note: For repeated terms, the extraction logic below handles sequential finding.

targets = [
    # Indication
    ("OBS_LESION", "cavitary lesion"),
    ("ANAT_LUNG_LOC", "right lower lobe"), # 1st
    
    # Header/Consent
    ("PROC_ACTION", "Bronchoscopy"),
    
    # Pre/Post Op
    ("OBS_LESION", "Solitary Lung Nodule"), # Pre
    ("OBS_LESION", "Solitary Lung Nodule"), # Post
    
    # Procedure Header
    ("PROC_ACTION", "lavage"),
    ("PROC_ACTION", "Endobronchial Biopsy(s)"),
    
    # Instrument
    ("DEV_INSTRUMENT", "Flexible Hybrid (Pediatric) Bronchoscope"),
    
    # Procedure Detail
    ("DEV_INSTRUMENT", "P190 hybrid video bronchoscope"),
    ("ANAT_AIRWAY", "trachea"), # 1st
    ("ANAT_AIRWAY", "main carina"),
    ("ANAT_AIRWAY", "left mainstem bronchus"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_LUNG_LOC", "lingula"),
    ("ANAT_LUNG_LOC", "lower lobe"), # Left lower
    ("ANAT_AIRWAY", "trachea"), # 2nd
    ("ANAT_AIRWAY", "right mainstem bronchus"),
    ("ANAT_LUNG_LOC", "right upper"),
    ("ANAT_LUNG_LOC", "middle"),
    ("ANAT_LUNG_LOC", "lower lobes"), # Right lower context
    ("OBS_FINDING", "Purulent material"),
    ("ANAT_LUNG_LOC", "superior segment"), # 1st
    ("ANAT_LUNG_LOC", "right lower lobe"), # 2nd (emanating from)
    ("PROC_ACTION", "bronchoalveolar lavage"),
    ("MEAS_VOL", "60 cc"), # Note: specialized space character in source text
    ("MEAS_VOL", "20 cc"),
    ("OBS_LESION", "cavity"), # 1st
    ("ANAT_LUNG_LOC", "superior segment"), # 2nd
    ("ANAT_LUNG_LOC", "right lower lobe"), # 3rd (containing)
    ("OBS_LESION", "soft tissue mass"),
    ("OBS_LESION", "mycetoma"),
    ("ANAT_LUNG_LOC", "apical and posterior segments"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("OBS_LESION", "cavity"), # 2nd
    ("DEV_INSTRUMENT", "forceps"),
    ("PROC_ACTION", "biopsies"),
    ("OBS_LESION", "mass"),
    ("OBS_LESION", "cavity"), # 3rd
    ("OBS_FINDING", "bleeding"),
    ("MEAS_VOL", "4 cc"),
    ("MEDICATION", "epinephrine"),
    ("MEAS_VOL", "30 cc"),
    ("MEDICATION", "iced saline"),
    ("OBS_FINDING", "hemorrhage"),
    
    # Specimen
    ("SPECIMEN", "BAL"),
    ("ANAT_LUNG_LOC", "right lower lobe"), # 4th (Specimen header)
    ("ANAT_LUNG_LOC", "Right lower lobe"), # 5th (Specimen header)
    ("DEV_INSTRUMENT", "forceps"), # In "forceps biopsy"
    
    # Impression
    ("PROC_ACTION", "bronchoscopy"),
    ("OBS_LESION", "cavitary lesion"),
    ("ANAT_LUNG_LOC", "right lower lobe") # 6th
]

# Normalizing the specialized space if necessary, but finding exact match is safer.
# The source text has "60 cc" (U+202F Narrow No-Break Space) likely. 
# We will iterate and find matches sequentially to handle the order.

# ==========================================
# 4. Extraction Logic
# ==========================================

found_entities = []
search_start_index = 0

for label, text_snippet in targets:
    # Find next occurrence of text_snippet starting from search_start_index
    match_index = RAW_TEXT.find(text_snippet, search_start_index)
    
    if match_index == -1:
        # Fallback: try replacing narrow no-break space with normal space if failed
        alt_snippet = text_snippet.replace('\u202f', ' ')
        match_index = RAW_TEXT.find(alt_snippet, search_start_index)
        
        if match_index == -1:
             print(f"Warning: Could not find entity '{text_snippet}' after index {search_start_index}")
             continue
        else:
            # Update snippet to what was actually found for length calc
            text_snippet = alt_snippet

    start = match_index
    end = start + len(text_snippet)
    
    found_entities.append({
        "label": label,
        "text": text_snippet,
        "start": start,
        "end": end
    })
    
    # Advance search index to avoid re-finding the same instance
    # We move just past this entity
    search_start_index = start + 1

# ==========================================
# 5. Output Generation
# ==========================================

# Prepare data for ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [[e["start"], e["end"], e["label"]] for e in found_entities]
}

# Prepare data for notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

# Prepare data for spans.jsonl
span_entries = []
for e in found_entities:
    span_id = f"{e['label']}_{e['start']}"
    span_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": e["label"],
        "text": e["text"],
        "start": e["start"],
        "end": e["end"]
    })

# Write to files
with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

with open(NOTES_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

with open(SPANS_PATH, "a", encoding="utf-8") as f:
    for span in span_entries:
        f.write(json.dumps(span) + "\n")

# ==========================================
# 6. Update Stats
# ==========================================
if STATS_PATH.exists():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
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
# Assuming 1 file per note in this workflow
stats["total_files"] += 1
stats["total_spans_raw"] += len(found_entities)
stats["total_spans_valid"] += len(found_entities)

for e in found_entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# ==========================================
# 7. Validation & Logging
# ==========================================
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for e in found_entities:
        extracted = RAW_TEXT[e["start"]:e["end"]]
        if extracted != e["text"]:
            log_msg = f"[{datetime.datetime.now()}] MISMATCH in {NOTE_ID}: Label {e['label']} indices {e['start']}-{e['end']} extract '{extracted}' != expected '{e['text']}'\n"
            log_file.write(log_msg)

print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")