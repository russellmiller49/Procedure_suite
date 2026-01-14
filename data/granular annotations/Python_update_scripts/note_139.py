import json
import os
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# 1. Configuration & Data Definition
# ==========================================

NOTE_ID = "note_139"

# The raw text from the provided file
RAW_TEXT = """Procedure Name: Bronchoscopy
Indications: Multiple pulmonary nodules
Medications: Per anesthesia record

Pre-Procedure

Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered, and informed consent was documented per institutional protocol.
A history and physical examination were performed and updated in the preprocedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.

Following intravenous medications per the anesthesia record and topical anesthesia to the upper airway and tracheobronchial tree, the T180 therapeutic video bronchoscope was introduced through the mouth via laryngeal mask airway and advanced into the tracheobronchial tree.
The Q180 slim video bronchoscope was subsequently introduced via the same route.
Procedure Description / Findings

Post-radiation changes were noted involving the vocal cords and aryepiglottic folds.
Papillomatous lesions were identified involving the right mainstem bronchus and bronchus intermedius.
Abnormal mucosa was noted along the anterolateral aspect of the upper trachea, predominantly on the left side, with post-treatment changes extending to the mid-trachea.
No clear papillomatous growth was identified in the distal airways.
The patient is status post prior endotracheal biopsies at abnormal papillomatous lesions involving the superior segment stump, proximal bronchus intermedius, and distal bronchus intermedius.
The patient is also status post intratracheal injection of cidofovir (75 mg in 15 mL) at these sites.
Right Lung Abnormalities

A small, barely obstructing (less than 10% luminal obstruction) 8–10 mm polypoid lesion was identified proximally in the bronchus intermedius and in the superior segment of the right lower lobe (B6).
Narrow-band imaging was used for airway examination and demonstrated dotted abnormal vascular patterns in the proximal and distal bronchus intermedius.
These lesions were biopsied.

Complications

No immediate complications.

Estimated Blood Loss

Minimal.
Post-Procedure Diagnosis

Endobronchial papillomatous lesions, status post biopsy

Recommendations

Follow up in clinic in 3 months.
Attending Participation

I was present and participated throughout the entire procedure, including non-key portions."""

# Entities identified based on Label_guide_UPDATED.csv
# Format: (Text_Snippet, Label)
# Note: This list targets specific occurrences. The script searches for these strings.
TARGET_ENTITIES = [
    ("Multiple pulmonary nodules", "OBS_LESION"),
    ("upper airway", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("T180 therapeutic video bronchoscope", "DEV_INSTRUMENT"),
    ("Q180 slim video bronchoscope", "DEV_INSTRUMENT"),
    ("Post-radiation changes", "OBS_FINDING"),
    ("vocal cords", "ANAT_AIRWAY"),
    ("aryepiglottic folds", "ANAT_AIRWAY"),
    ("Papillomatous lesions", "OBS_LESION"),
    ("right mainstem bronchus", "ANAT_AIRWAY"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("Abnormal mucosa", "OBS_FINDING"),
    ("upper trachea", "ANAT_AIRWAY"),
    ("post-treatment changes", "OBS_FINDING"),
    ("mid-trachea", "ANAT_AIRWAY"),
    ("biopsies", "PROC_ACTION"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("injection", "PROC_ACTION"),
    ("cidofovir", "MEDICATION"),
    ("8–10 mm", "MEAS_SIZE"),
    ("polypoid lesion", "OBS_LESION"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("B6", "ANAT_LUNG_LOC"),
    ("Narrow-band imaging", "PROC_METHOD"),
    ("abnormal vascular patterns", "OBS_FINDING"),
    ("biopsied", "PROC_ACTION"),
    ("Endobronchial papillomatous lesions", "OBS_LESION"),
]

# ==========================================
# 2. Path Setup
# ==========================================

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 3. Processing & Extraction Logic
# ==========================================

def find_spans(text, targets):
    """
    Finds strict character offsets for target entities.
    Handles multiple occurrences by finding all and filtering if needed, 
    but here we map all unique exact matches found in the text 
    to populate the training set comprehensively.
    """
    spans = []
    found_indices = set()
    
    for substring, label in targets:
        # Escape special regex characters in the substring (like parens)
        pattern = re.escape(substring)
        for match in re.finditer(pattern, text):
            start = match.start()
            end = match.end()
            
            # Create a unique key for this span location
            span_key = (start, end)
            
            # Avoid duplicate spans if the list has duplicates or overlaps
            if span_key not in found_indices:
                spans.append({
                    "span_id": f"{label}_{start}",
                    "note_id": NOTE_ID,
                    "label": label,
                    "text": substring,
                    "start": start,
                    "end": end
                })
                found_indices.add(span_key)
                
    # Sort spans by start index
    spans.sort(key=lambda x: x['start'])
    return spans

def load_json_stats(path):
    if not path.exists():
        return {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_stats(path, stats):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

# ==========================================
# 4. Execution
# ==========================================

if __name__ == "__main__":
    # A. Calculate Spans
    extracted_spans = find_spans(RAW_TEXT, TARGET_ENTITIES)
    
    # B. Prepare NER Dataset Entry (Doccano/spaCy friendly format)
    # entities list format: [start, end, label]
    ner_entities = [[s['start'], s['end'], s['label']] for s in extracted_spans]
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": ner_entities
    }

    # C. Prepare Note Entry
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }

    # D. Write to Files
    
    # 1. Update ner_dataset_all.jsonl
    with open(NER_DATASET_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 2. Update notes.jsonl
    with open(NOTES_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")

    # 3. Update spans.jsonl
    with open(SPANS_FILE, 'a', encoding='utf-8') as f:
        for span in extracted_spans:
            f.write(json.dumps(span) + "\n")

    # E. Update Stats
    stats = load_json_stats(STATS_FILE)
    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += len(extracted_spans)
    stats["total_spans_valid"] += len(extracted_spans) # Assuming all passed valid checks
    
    for span in extracted_spans:
        lbl = span['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    save_json_stats(STATS_FILE, stats)

    # F. Validation & Logging
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        for span in extracted_spans:
            # Verify offset integrity
            snippet_in_text = RAW_TEXT[span['start']:span['end']]
            if snippet_in_text != span['text']:
                log.write(f"[{datetime.now()}] MISMATCH: ID {span['span_id']} expected '{span['text']}' but found '{snippet_in_text}'\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(extracted_spans)} entities.")
    print(f"Stats updated at {STATS_FILE}")