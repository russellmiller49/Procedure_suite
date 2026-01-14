import json
import re
import os
import datetime
from pathlib import Path

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
NOTE_ID = "note_144"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
# We traverse up 3 levels to reach 'data' based on the assumed structure in the prompt.
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# Raw Text Content (Cleaned of '' tags)
TEXT = """Procedure Name: Bronchoscopy
Indications: Metastatic lung cancer; hemoptysis

Pre-Anesthesia Assessment:

A history and physical examination were performed.
Patient medications and allergies were reviewed. The risks and benefits of the procedure, as well as sedation options and associated risks, were discussed with the patient’s parent.
All questions were answered, and informed consent was obtained. Patient identification and the proposed procedure were verified prior to the procedure by the physician, nurse, and technician in the procedure room.
Mental status examination revealed the patient to be alert and oriented. Airway examination demonstrated a normal oropharyngeal airway.
Respiratory examination was clear to auscultation. Cardiovascular examination revealed regular rate and rhythm without murmurs, S3, or S4.
The ASA physical status classification was III (a patient with severe systemic disease).
After reviewing risks and benefits, the patient was deemed an appropriate candidate to undergo the procedure under general anesthesia.
Immediately prior to administration of medications, the patient was reassessed and found to be appropriate for sedation.
Heart rate, respiratory rate, oxygen saturation, blood pressure, adequacy of ventilation, and response to care were continuously monitored throughout the procedure.
The patient’s physical status was reassessed following completion of the procedure.
Procedure, risks, benefits, and alternatives were again explained to the patient, and informed consent was documented per institutional protocol.
A history and physical examination were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.

Following administration of intravenous medications per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree, the Q180 slim video bronchoscope was introduced through the rigid bronchoscope after removal of the telescope and advanced into the tracheobronchial tree bilaterally.
The T180 therapeutic video bronchoscope was subsequently introduced and advanced into the airways. The procedure was accomplished without difficulty.
Procedure Description:

Left Lung Abnormalities:
A partially obstructing airway abnormality (approximately 40% luminal obstruction) was identified at the entrance to the left lower lobe.
Tumor debulking was performed using an electrocautery snare with successful coagulation.
Upon completion, the left lower lobe entrance was fully patent.
Findings:

Right Lung Abnormalities:
A nearly obstructing airway abnormality (>90% luminal obstruction) was identified at the entrance to the right lower lobe.
Tumor destruction was performed using argon plasma coagulation at 25 watts and 0.3 L/min, in combination with an electrocautery probe and electrocautery snare.
This resulted in successful recanalization.

Upon completion of intervention, both the left lower lobe and right lower lobe entrances were 100% patent.
Residual tumor remained within the anterior and lateral basal segments of the right lower lobe;
this tissue appeared chronic and extended into the peripheral airways and was not amenable to further intervention.
The right lower lobe superior segment, medial basal segment, and posterior segment were fully patent.
Therapeutic aspiration was performed at the conclusion of the procedure to remove retained blood and secretions, with good hemostasis achieved.
Complications: No immediate complications
Estimated Blood Loss: Minimal

Additional Findings:

Metastatic renal cell carcinoma with endobronchial tumors involving the left lower lobe and right lower lobe entrances

Hemoptysis

Partially obstructing (approximately 40%) airway abnormality in the left lower lobe

Nearly obstructing (>90%) airway abnormality in the right lower lobe

No specimens collected

Post-Procedure Diagnosis:

Nearly obstructing airway abnormality of the right lower lobe, status post successful debulking

No specimens collected

Plan:

Follow up with the bronchoscopist in one week

Follow up with the referring physician as previously scheduled"""

# ==========================================
# 2. ENTITY DEFINITIONS
# ==========================================
# Defining entities to extract based on Label_guide_UPDATED.csv
# Format: (Text substring, Label)
# Note: This list targets specific unique phrases or will be processed to find all non-overlapping matches.

TARGET_ENTITIES = [
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("Q180 slim video bronchoscope", "DEV_INSTRUMENT"),
    ("rigid bronchoscope", "DEV_INSTRUMENT"),
    ("T180 therapeutic video bronchoscope", "DEV_INSTRUMENT"),
    ("airways", "ANAT_AIRWAY"),
    ("partially obstructing airway abnormality", "OBS_LESION"),
    ("40% luminal obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("Tumor debulking", "PROC_ACTION"),
    ("electrocautery snare", "DEV_INSTRUMENT"),
    ("coagulation", "PROC_ACTION"),
    ("fully patent", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("nearly obstructing airway abnormality", "OBS_LESION"),
    (">90% luminal obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("Tumor destruction", "PROC_ACTION"),
    ("argon plasma coagulation", "PROC_ACTION"),
    ("25 watts", "MEAS_ENERGY"),
    ("electrocautery probe", "DEV_INSTRUMENT"),
    ("100% patent", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("Residual tumor", "OBS_LESION"),
    ("anterior and lateral basal segments", "ANAT_LUNG_LOC"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("medial basal segment", "ANAT_LUNG_LOC"),
    ("posterior segment", "ANAT_LUNG_LOC"),
    ("Therapeutic aspiration", "PROC_ACTION"),
    ("retained blood", "OBS_FINDING"),
    ("secretions", "OBS_FINDING"),
    ("good hemostasis", "OUTCOME_COMPLICATION"),
    ("No immediate complications", "OUTCOME_COMPLICATION"),
]

# ==========================================
# 3. PROCESSING LOGIC
# ==========================================

def get_spans(text, targets):
    """
    Finds all occurrences of target substrings in the text.
    Returns a list of dicts with label, start, end, and text.
    """
    spans = []
    # To avoid overlapping issues in this simple script, we sort by length (longest first) 
    # and keep track of occupied indices if strictly necessary. 
    # For this dataset generation, we will capture all valid distinct occurrences.
    
    for phrase, label in targets:
        # Use regex to find all matches
        for match in re.finditer(re.escape(phrase), text):
            spans.append({
                "label": label,
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "span_id": f"{label}_{match.start()}"
            })
    
    # Sort by start position
    spans.sort(key=lambda x: x["start"])
    return spans

def update_stats(new_spans):
    """Updates the stats.json file with new counts."""
    if not STATS_PATH.exists():
        print(f"Stats file not found at {STATS_PATH}")
        return

    with open(STATS_PATH, 'r') as f:
        stats = json.load(f)

    # Update global counts
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    # Update label counts
    for span in new_spans:
        label = span["label"]
        stats["label_counts"][label] = stats["label_counts"].get(label, 0) + 1

    with open(STATS_PATH, 'w') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Extract Spans
    extracted_spans = get_spans(TEXT, TARGET_ENTITIES)
    
    # 2. Prepare Data Objects
    ner_entry = {
        "id": NOTE_ID,
        "text": TEXT,
        "entities": [
            {
                "id": span["span_id"],
                "label": span["label"],
                "start_offset": span["start"],
                "end_offset": span["end"]
            }
            for span in extracted_spans
        ]
    }

    note_entry = {
        "id": NOTE_ID,
        "text": TEXT
    }

    span_entries = []
    for span in extracted_spans:
        span_entries.append({
            "span_id": span["span_id"],
            "note_id": NOTE_ID,
            "label": span["label"],
            "text": span["text"],
            "start": span["start"],
            "end": span["end"]
        })

    # 3. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a') as f:
        f.write(json.dumps(ner_entry) + '\n')

    # Append to notes.jsonl
    with open(NOTES_PATH, 'a') as f:
        f.write(json.dumps(note_entry) + '\n')

    # Append to spans.jsonl
    with open(SPANS_PATH, 'a') as f:
        for entry in span_entries:
            f.write(json.dumps(entry) + '\n')

    # 4. Update Stats
    update_stats(extracted_spans)

    # 5. Validate and Log
    with open(LOG_PATH, 'a') as log:
        for span in extracted_spans:
            original_text = TEXT[span["start"]:span["end"]]
            if original_text != span["text"]:
                log.write(f"[{datetime.datetime.now()}] ALIGNMENT ERROR: {NOTE_ID} - Expected '{span['text']}', found '{original_text}' at {span['start']}:{span['end']}\n")

    print(f"Successfully processed {NOTE_ID}. Added {len(extracted_spans)} entities.")

if __name__ == "__main__":
    main()