import json
import os
import datetime
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_205"

# Raw text from the input file
RAW_TEXT = """Indications: Diagnosis and staging of presumed lung cancer
Medications: General Anesthesia,
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.

Following intravenous medications and intubation by anesthesia, the T190 video bronchoscope was introduced through the ETT and advanced to the tracheobronchial tree.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
At the carina for the superior segment of the left lower lobe was a mucosal irregularity concerning for endobronchial tumor.
Otherwise bronchial mucosa and anatomy were normal without other endobronchial lesions.
Enbobronchial forcep biopsies were performed of the superior segment lesion with minimal bleeding.
The Covidien superDimension locatable guide was then inserted through the working channel and registration was performed.
The Edge 180 degree extended working channel was then attached to the bronchoscope.
Using navigational map we attempted to advance into the proximity of the lesion within the left lower lobe lesion.
Confirmation of placement once at the point of interest with radial ultrasound showed a concentric view within the lesion.
Biopsies were then performed with peripheral needle with on ROSE were non-diagnostic.
Due to intermittent hypoxia and rising peak pressures decision was made to abort peripheral biopsies and BAL of the anterior segment of the left lower lobe was performed with 90cc instillation and 25cc return.
Repeat fluoroscopic imaging showed large left sided pneumothorax. 
The left axillary area was the prepped in a sterile fashion.
A Yueh centesis needle was advanced into the pleural space.
Air was easily aspirated and the catheter was advanced into the space and needle withdrawn.
A guidewire was inserted through the catheter. A small skin incision was made at the wire site and a two-step dilatation of pleural tract was then performed via Seldinger technique.
The Cooke 12F pigtail catheter was then inserted with its trocar in place over the wire.
The trocar was subsequently removed with the wire. The catheter was subsequently connected to the pleurovac and the catheter sutured into place.
Repeat fluoroscopic imaging showed pig tail in place and complete lung re-expansion.
The patient was subsequently intubated and admitted to the IM service for chest tube management.
Recommendations:
1.\tAdmit to IM service for CT management
2.\tAwait pathology and microbiological assessment from biopsy specimens and lavage
3.\tWe will follow on the inpatinet service and provide further recs regarding CT management."""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"


# ==========================================
# ENTITY EXTRACTION LOGIC
# ==========================================
# Dictionary of target phrases and their corresponding strict labels from Label_guide_UPDATED.csv
# This approach ensures exact matching.
target_entities = [
    # Anatomy
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("anterior segment", "ANAT_LUNG_LOC"),
    ("left", "LATERALITY"),
    ("axillary area", "ANAT_PLEURA"),  # Chest wall
    ("pleural space", "ANAT_PLEURA"),
    
    # Devices & Tools
    ("T190 video bronchoscope", "DEV_INSTRUMENT"),
    ("forcep", "DEV_INSTRUMENT"),
    ("superDimension locatable guide", "DEV_INSTRUMENT"),
    ("Edge 180 degree extended working channel", "DEV_INSTRUMENT"),
    ("peripheral needle", "DEV_NEEDLE"),
    ("Yueh centesis needle", "DEV_NEEDLE"),
    ("12F", "DEV_CATHETER_SIZE"),  # Specific size phrase
    ("pigtail catheter", "DEV_CATHETER"),
    ("pleurovac", "DEV_CATHETER"),
    ("pig tail", "DEV_CATHETER"),
    ("chest tube", "DEV_CATHETER"),
    ("catheter", "DEV_CATHETER"),

    # Procedures & Methods
    ("navigational map", "PROC_METHOD"),
    ("radial ultrasound", "PROC_METHOD"),
    ("fluoroscopic imaging", "PROC_METHOD"),
    ("Seldinger technique", "PROC_METHOD"),
    ("biopsies", "PROC_ACTION"),
    ("BAL", "PROC_ACTION"),
    ("lavage", "PROC_ACTION"),
    
    # Observations & Findings
    ("endobronchial tumor", "OBS_LESION"),
    ("mucosal irregularity", "OBS_FINDING"),
    ("lesion", "OBS_LESION"),
    ("pneumothorax", "OBS_FINDING"), # Finding during procedure
    ("non-diagnostic", "OBS_ROSE"),
    ("complete lung re-expansion", "OUTCOME_PLEURAL"),
    
    # Measurements
    ("90cc", "MEAS_VOL"),
    ("25cc", "MEAS_VOL"),
]

def find_spans(text, targets):
    """
    Finds all non-overlapping occurrences of target phrases in the text.
    Returns a list of dicts: {"label": str, "start": int, "end": int, "text": str}
    """
    found_spans = []
    
    # Sort targets by length (descending) to prioritize longer phrases (e.g., "left lower lobe" over "left")
    sorted_targets = sorted(targets, key=lambda x: len(x[0]), reverse=True)
    
    # Keep track of occupied indices to prevent overlap
    occupied_indices = set()
    
    for phrase, label in sorted_targets:
        # Regex escape the phrase to handle special chars like parens
        pattern = re.escape(phrase)
        
        # Iterate over all matches
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            
            # Check for overlap
            is_overlap = any(i in occupied_indices for i in range(start, end))
            
            if not is_overlap:
                # Add to results
                found_spans.append({
                    "label": label,
                    "start": start,
                    "end": end,
                    "text": text[start:end] # Use actual text to preserve casing
                })
                
                # Mark indices as occupied
                for i in range(start, end):
                    occupied_indices.add(i)
                    
    # Sort by start position
    found_spans.sort(key=lambda x: x["start"])
    return found_spans

# Perform Extraction
entities = find_spans(RAW_TEXT, target_entities)


# ==========================================
# FILE UPDATE OPERATIONS
# ==========================================

def append_jsonl(path, data):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

def update_stats(new_label_counts, span_count):
    if not STATS_PATH.exists():
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    else:
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)
            
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += span_count
    stats["total_spans_valid"] += span_count # Assuming all extracted are valid
    
    for label, count in new_label_counts.items():
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + count
        
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def log_warning(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().isoformat()
        f.write(f"[{timestamp}] {message}\n")


# 1. Update ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {"start": e["start"], "end": e["end"], "label": e["label"]}
        for e in entities
    ]
}
append_jsonl(NER_DATASET_PATH, ner_entry)

# 2. Update notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
append_jsonl(NOTES_PATH, note_entry)

# 3. Update spans.jsonl & Calculate Stats
label_counts = {}
for e in entities:
    # Schema: {"span_id": "Label_Offset", "note_id": NOTE_ID, "label": "...", "text": "...", "start": ..., "end": ...}
    span_id = f"{e['label']}_{e['start']}"
    
    span_entry = {
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": e["label"],
        "text": e["text"],
        "start": e["start"],
        "end": e["end"]
    }
    append_jsonl(SPANS_PATH, span_entry)
    
    # Validation
    if RAW_TEXT[e["start"]:e["end"]] != e["text"]:
        log_warning(f"Mismatch in Note {NOTE_ID}: Span '{e['text']}' indices {e['start']}-{e['end']} do not match raw text.")

    # Stats aggregation
    label_counts[e["label"]] = label_counts.get(e["label"], 0) + 1

# 4. Update Stats
update_stats(label_counts, len(entities))

print(f"Successfully processed {NOTE_ID}.")
print(f"Extracted {len(entities)} entities.")
print(f"Output directory: {OUTPUT_DIR}")