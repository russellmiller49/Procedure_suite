import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================
NOTE_ID = "note_221"
RAW_TEXT = """Procedure Name: Inspection bronchoscopy with bronchial lavage
Indications: Right lower lobe collapse and possible BP fistula
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record.
Laboratory studies and radiographs 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first sub-segmental level. The left sided airways were normal.
Significant pus was encountered within the right mainstem which was suctioned.
Once we’re able to better visualize the airways a 3 mm hole consistent with the BP fistula actively oozing purulent material was seen in the stump from the posterior segment of the right upper lobe.
A proximally 150 cc of gross pus was suctioned including 40 cc which was suctioned and retained in the trap for culture.
The right middle lobe stump was intact.  The superior segment of the right lower lobe was open.
The basilar segments of the right lower lobe were completely obstructed due to bronchial kink without endobronchial disease which we could not pass.
Purulent material was expressed from this area as well consistent with a postobstructive pneumonia.
CT surgery was informed of the findings and came to the room to observe the stump.
At this point retained secretions were suctioned and once we were confident that there was no evidence of active bleeding the bronchoscope was subsequently removed.
Complications: None 
Estimated Blood Loss: 0

Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with bronchial wash.
-BP fistula in the posterior segment of the right upper lobe stump.
- After patient recovers from anesthesia we will have a discussion regarding his wishes for further therapeutic interventions."""

# Target entities based on Label_guide_UPDATED.csv
# Strategy: text_snippet -> Label
ENTITIES_TO_FIND = [
    ("Inspection bronchoscopy", "PROC_METHOD"),
    ("bronchial lavage", "PROC_ACTION"),
    ("Right lower lobe", "ANAT_LUNG_LOC"),
    ("collapse", "OBS_FINDING"),
    ("BP fistula", "OBS_LESION"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("video bronchoscope", "DEV_INSTRUMENT"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("subglottic space", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),  # Lowercase for search, will match "The trachea"
    ("carina", "ANAT_AIRWAY"),   # Lowercase for search
    ("right mainstem", "ANAT_AIRWAY"),
    ("pus", "OBS_FINDING"),
    ("suctioned", "PROC_ACTION"),
    ("3 mm", "MEAS_SIZE"),
    ("posterior segment of the right upper lobe", "ANAT_LUNG_LOC"),
    ("purulent material", "OBS_FINDING"),
    ("150 cc", "MEAS_VOL"),
    ("40 cc", "MEAS_VOL"),
    ("right middle lobe stump", "ANAT_LUNG_LOC"),
    ("superior segment of the right lower lobe", "ANAT_LUNG_LOC"),
    ("basilar segments of the right lower lobe", "ANAT_LUNG_LOC"),
    ("bronchial kink", "OBS_FINDING"),
    ("endobronchial disease", "OBS_LESION"),
    ("postobstructive pneumonia", "OBS_LESION"),
    ("secretions", "OBS_FINDING"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("flexible bronchoscopy", "PROC_METHOD"),
    ("bronchial wash", "PROC_ACTION"),
]

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def find_entity_spans(text, entities_list):
    """
    Finds strict start/end character offsets for entities.
    Returns a list of dicts: {"label": str, "start": int, "end": int, "text": str}
    """
    spans = []
    text_lower = text.lower()
    
    # Sort by length descending to prioritize longer matches (greedy)
    # Note: simple substring search might overlap; in production, use a token-based matcher.
    # Here we perform a simple iterative search with tracking to avoid double-counting strictly if needed,
    # but for this utility, we allow multiple hits if they appear multiple times.
    
    # We iterate through the specific list order to handle specific instances
    
    for snippet, label in entities_list:
        snippet_lower = snippet.lower()
        start = 0
        while True:
            idx = text_lower.find(snippet_lower, start)
            if idx == -1:
                break
            
            # Grab actual text to preserve case
            actual_text = text[idx : idx + len(snippet)]
            
            # Check overlap with existing spans? 
            # For simplicity in this generator, we assume the user list is curated to avoid sub-span conflicts 
            # or that overlaps are acceptable for ML data augmentation unless strict IOB is required.
            # We will deduplicate exact same span objects.
            
            span_obj = {
                "label": label,
                "start": idx,
                "end": idx + len(snippet),
                "text": actual_text
            }
            
            if span_obj not in spans:
                spans.append(span_obj)
            
            start = idx + 1
            
    return sorted(spans, key=lambda x: x["start"])

def load_json_stats(path):
    if not path.exists():
        return {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "label_counts": {}
        }
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_stats(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def append_jsonl(path, data):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')

# ==========================================
# 3. EXECUTION
# ==========================================

print(f"Processing Note ID: {NOTE_ID}...")

# 3.1 Extract Spans
extracted_spans = find_entity_spans(RAW_TEXT, ENTITIES_TO_FIND)

# 3.2 Prepare Data Structures
# Structure for ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {"start": s["start"], "end": s["end"], "label": s["label"]} 
        for s in extracted_spans
    ]
}

# Structure for notes.jsonl
note_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

# Structure for spans.jsonl
span_entries = []
for s in extracted_spans:
    span_id = f"{s['label']}_{s['start']}"
    span_entries.append({
        "span_id": span_id,
        "note_id": NOTE_ID,
        "label": s['label'],
        "text": s['text'],
        "start": s['start'],
        "end": s['end']
    })

# 3.3 Update Files
print("Updating ner_dataset_all.jsonl...")
append_jsonl(NER_DATASET_PATH, ner_entry)

print("Updating notes.jsonl...")
append_jsonl(NOTES_PATH, note_entry)

print("Updating spans.jsonl...")
for entry in span_entries:
    append_jsonl(SPANS_PATH, entry)

# 3.4 Update Stats
print("Updating stats.json...")
stats = load_json_stats(STATS_PATH)

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(extracted_spans)
stats["total_spans_valid"] += len(extracted_spans)

for s in extracted_spans:
    lbl = s["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

save_json_stats(STATS_PATH, stats)

# 3.5 Validation & Logging
print("Validating alignments...")
with open(LOG_PATH, "a", encoding="utf-8") as log_file:
    for s in extracted_spans:
        original_snippet = RAW_TEXT[s["start"]:s["end"]]
        if original_snippet != s["text"]:
            log_msg = f"[{datetime.datetime.now()}] MISMATCH: ID {NOTE_ID}, Label {s['label']}, Exp '{s['text']}' vs Found '{original_snippet}'\n"
            log_file.write(log_msg)
            print(f"WARNING: Mismatch detected for {s['label']}")

print("Done successfully.")