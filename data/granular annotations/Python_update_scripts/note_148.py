import json
import os
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_148"

# Raw text from the provided file
TEXT = """Procedure: Fiberoptic bronchoscopy
Anesthesia Type: Previously tracheostomized and sedated
Indication: Hypoxemia
Consent: Emergent
Time-Out: Performed
Pre-Procedure Diagnosis: Emergent
Post-Procedure Diagnosis: Emergent
Medications: Patient previously sedated

Procedure Description

The Olympus Q190 video bronchoscope was introduced through the tracheostomy tube and advanced into the tracheobronchial tree.
A complete airway inspection was performed to at least the first subsegmental airways.
The right-sided airways were unremarkable, with only mildly edematous mucosa and clear secretions.
The left-sided airways were similar, with the exception of purulent secretions pooling in the superior segment of the left lower lobe.
The remaining airways were patent without significant central mucus plugging.
The bronchoscope was wedged into the superior segment of the left lower lobe, and bronchoalveolar lavage was performed with 60 mL of instilled saline and 20 mL of return.
The bronchoscope was then withdrawn, and the procedure was completed.
Estimated Blood Loss: None
Complications: None
Specimens Sent: Bronchoalveolar lavage, left lower lobe
Implants: None

Follow-Up: Continue ICU-level care"""

# =============================================================================
# ENTITY EXTRACTION (Manual Annotation based on Label_guide_UPDATED.csv)
# =============================================================================
# Helper function to find distinct occurrences
def get_span(text, search_str, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(search_str, start + 1)
        if start == -1:
            raise ValueError(f"Substring '{search_str}' (occ {occurrence}) not found.")
    return start, start + len(search_str), search_str

# List of target entities to extract
# Format: (search_string, label, occurrence_index)
targets = [
    ("Fiberoptic bronchoscopy", "PROC_ACTION", 1),
    ("tracheobronchial tree", "ANAT_AIRWAY", 1),
    ("first subsegmental airways", "ANAT_AIRWAY", 1),
    ("right-sided airways", "ANAT_AIRWAY", 1),
    ("edematous mucosa", "OBS_FINDING", 1),
    ("clear secretions", "OBS_FINDING", 1),
    ("left-sided airways", "ANAT_AIRWAY", 1),
    ("purulent secretions", "OBS_FINDING", 1),
    ("superior segment of the left lower lobe", "ANAT_LUNG_LOC", 1),
    ("central mucus plugging", "OBS_FINDING", 1),
    ("superior segment of the left lower lobe", "ANAT_LUNG_LOC", 2),
    ("bronchoalveolar lavage", "PROC_ACTION", 1), # In procedure description
    ("60 mL", "MEAS_VOL", 1),
    ("20 mL", "MEAS_VOL", 1),
    ("Bronchoalveolar lavage", "SPECIMEN", 1), # In Specimens Sent
    ("left lower lobe", "ANAT_LUNG_LOC", 3) # In Specimens Sent
]

entities = []
for search_str, label, occ in targets:
    s, e, t = get_span(TEXT, search_str, occ)
    entities.append({
        "label": label,
        "start": s,
        "end": e,
        "text": t
    })

# Sort entities by start position
entities.sort(key=lambda x: x["start"])

# =============================================================================
# PATH SETUP
# =============================================================================
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# EXECUTION
# =============================================================================

def update_ner_dataset():
    """Appends the labeled note to ner_dataset_all.jsonl"""
    entry = {
        "id": NOTE_ID,
        "text": TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_notes():
    """Appends the raw note to notes.jsonl"""
    entry = {
        "id": NOTE_ID,
        "text": TEXT
    }
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_spans():
    """Appends individual spans to spans.jsonl"""
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for e in entities:
            span_entry = {
                "span_id": f"{e['label']}_{e['start']}",
                "note_id": NOTE_ID,
                "label": e["label"],
                "text": e["text"],
                "start": e["start"],
                "end": e["end"]
            }
            f.write(json.dumps(span_entry) + "\n")

def update_stats():
    """Updates the global statistics file"""
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
    stats["total_files"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)

    for e in entities:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def validate_alignment():
    """Checks string alignment and logs warnings"""
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        for e in entities:
            extracted = TEXT[e["start"]:e["end"]]
            if extracted != e["text"]:
                msg = f"[{datetime.datetime.now()}] MISMATCH {NOTE_ID}: Expected '{e['text']}' but found '{extracted}' at {e['start']}:{e['end']}\n"
                log.write(msg)

if __name__ == "__main__":
    try:
        update_ner_dataset()
        update_notes()
        update_spans()
        update_stats()
        validate_alignment()
        print(f"Successfully processed {NOTE_ID} and updated datasets in {OUTPUT_DIR}")
    except Exception as e:
        print(f"Error processing {NOTE_ID}: {e}")