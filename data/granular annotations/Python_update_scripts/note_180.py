from pathlib import Path
import json
import os
import datetime

# =============================================================================
# 1. Configuration & Path Setup
# =============================================================================

NOTE_ID = "note_179"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
FILE_NER_DATASET = OUTPUT_DIR / "ner_dataset_all.jsonl"
FILE_NOTES = OUTPUT_DIR / "notes.jsonl"
FILE_SPANS = OUTPUT_DIR / "spans.jsonl"
FILE_STATS = OUTPUT_DIR / "stats.json"
FILE_LOG = OUTPUT_DIR / "alignment_warnings.log"

# =============================================================================
# 2. Raw Text & Entity Definition
# =============================================================================

RAW_TEXT = """Indications: Hilar cyst aspiration 
Procedure: EBUS bronchoscopy – single station
Medications: General Anesthesia
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway initially was not well positioned but after replacement with larger LMA seated in good position.
The vocal cords appeared normal. The subglottic space was normal. The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.
Bronchial mucosa and anatomy were normal with the exception of partial extrinsic compression of the left upper lobe bronchus distal to the lingual and most obvious in the apical segment;
there are no endobronchial lesions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The scope was advanced into the proximal left upper lobe and a 45mm heterogeneous cyst with multiple septations was seen just distal to the left PA.
Sampling by transbronchial needle aspiration was performed with the Olympus 19G Visioshot EBUS-TBNA needle.
Material was thick which could not be grossly  aspirated through the needle with attached suction.
Samples showed thick coagulated bloody material on multiple needle passes consistent with old blood.
Rapid onsite pathological evaluation showed heme and multiple foamy macrophages.
Samples and fluid were sent for both culture and routine cytology.
Following completion of EBUS bronchoscopy, the Q190 video bronchoscope was then re-inserted and after suctioning blood and secretions there was no evidence of active bleeding and the bronchoscope was subsequently removed.
Complications: No immediate complications
Post-operative diagnosis: Hemorrhagic Hilar cyst
Estimated Blood Loss: 10cc
Recommendations:
- Transferred patient to post-procedural monitoring 
- 10 day course of Augmentin to reduced likelihood of infection of capsulated cystic space.
- Will await final pathology results
- Repeat CT in 3-4 weeks or earlier if fevers, persistent/worsening chest pain, hemoptysis or other symptoms concerning for infection or cyst rupture.
- Will likely require unroofing and resection with thoracic surgery"""

# Helper to locate spans dynamically to ensure accuracy
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# Entity Extraction (Mapped to Label_guide_UPDATED.csv)
entities_raw = [
    # "Indications: Hilar cyst aspiration"
    {"label": "ANAT_LN_STATION", **get_span(RAW_TEXT, "Hilar", 1)},
    {"label": "OBS_LESION",      **get_span(RAW_TEXT, "cyst", 1)},
    {"label": "PROC_ACTION",     **get_span(RAW_TEXT, "aspiration", 1)},
    
    # "Procedure: EBUS bronchoscopy"
    {"label": "PROC_METHOD",     **get_span(RAW_TEXT, "EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(RAW_TEXT, "bronchoscopy", 1)},
    
    # Body Paragraph 1
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "Q190 video bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "laryngeal mask airway", 1)},
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "tracheobronchial tree", 2)}, # 1st is in 'anesthesia to...', 2nd is 'advanced to'
    
    # Body Paragraph 2
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "laryngeal mask airway", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "LMA", 1)},
    
    # Body Paragraph 3 (Anatomy check)
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "vocal cords", 1)},
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "subglottic space", 1)},
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "trachea", 1)},
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "carina", 1)},
    
    # Body Paragraph 4
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "tracheobronchial tree", 3)},
    
    # Body Paragraph 5
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "left upper lobe bronchus", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(RAW_TEXT, "lingual", 1)}, # Typo in note for Lingula
    {"label": "ANAT_LUNG_LOC",   **get_span(RAW_TEXT, "apical segment", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "video bronchoscope", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "UC180F convex probe EBUS bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "laryngeal mask airway", 3)},
    {"label": "ANAT_AIRWAY",     **get_span(RAW_TEXT, "tracheobronchial tree", 4)},
    
    # Body Paragraph 6 (The scope was advanced...)
    {"label": "ANAT_LUNG_LOC",   **get_span(RAW_TEXT, "proximal left upper lobe", 1)},
    {"label": "MEAS_SIZE",       **get_span(RAW_TEXT, "45mm", 1)},
    {"label": "OBS_LESION",      **get_span(RAW_TEXT, "cyst", 2)},
    
    # Body Paragraph 7 (Sampling...)
    {"label": "PROC_ACTION",     **get_span(RAW_TEXT, "transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE",      **get_span(RAW_TEXT, "19G", 1)},
    
    # Body Paragraph 9 (Samples showed...)
    {"label": "OBS_FINDING",     **get_span(RAW_TEXT, "thick coagulated bloody material", 1)},
    
    # Body Paragraph 10 (Rapid onsite...)
    {"label": "OBS_ROSE",        **get_span(RAW_TEXT, "heme", 1)},
    {"label": "OBS_ROSE",        **get_span(RAW_TEXT, "foamy macrophages", 1)},
    
    # Body Paragraph 12 (Following completion...)
    {"label": "PROC_METHOD",     **get_span(RAW_TEXT, "EBUS", 3)},
    {"label": "PROC_ACTION",     **get_span(RAW_TEXT, "bronchoscopy", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(RAW_TEXT, "Q190 video bronchoscope", 2)},
    {"label": "OBS_FINDING",     **get_span(RAW_TEXT, "bleeding", 1)},
    
    # Complications/Diagnosis
    {"label": "OUTCOME_COMPLICATION", **get_span(RAW_TEXT, "No immediate complications", 1)},
    {"label": "ANAT_LN_STATION", **get_span(RAW_TEXT, "Hilar", 2)},
    {"label": "OBS_LESION",      **get_span(RAW_TEXT, "cyst", 3)},
    {"label": "MEAS_VOL",        **get_span(RAW_TEXT, "10cc", 1)},
    
    # Recommendations
    {"label": "MEDICATION",      **get_span(RAW_TEXT, "Augmentin", 1)},
]

# Sort entities by start position
entities_sorted = sorted(entities_raw, key=lambda x: x['start'])

# =============================================================================
# 3. Execution & Updates
# =============================================================================

def update_files():
    # 1. Update ner_dataset_all.jsonl
    with open(FILE_NER_DATASET, 'a', encoding='utf-8') as f:
        record = {
            "id": NOTE_ID,
            "text": RAW_TEXT,
            "entities": entities_sorted
        }
        f.write(json.dumps(record) + "\n")

    # 2. Update notes.jsonl
    with open(FILE_NOTES, 'a', encoding='utf-8') as f:
        note_record = {"id": NOTE_ID, "text": RAW_TEXT}
        f.write(json.dumps(note_record) + "\n")

    # 3. Update spans.jsonl
    with open(FILE_SPANS, 'a', encoding='utf-8') as f:
        for ent in entities_sorted:
            span_record = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": NOTE_ID,
                "label": ent['label'],
                "text": ent['text'],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_record) + "\n")

    # 4. Update stats.json
    if FILE_STATS.exists():
        with open(FILE_STATS, 'r', encoding='utf-8') as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file for this batch
    stats["total_spans_raw"] += len(entities_sorted)
    stats["total_spans_valid"] += len(entities_sorted)

    for ent in entities_sorted:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(FILE_STATS, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

    # 5. Validation & Logging
    with open(FILE_LOG, 'a', encoding='utf-8') as log:
        for ent in entities_sorted:
            extracted_text = RAW_TEXT[ent['start']:ent['end']]
            if extracted_text != ent['text']:
                log_entry = f"[{datetime.datetime.now()}] MISMATCH: {NOTE_ID} - Label {ent['label']} expected '{ent['text']}' but got '{extracted_text}' at indices {ent['start']}:{ent['end']}\n"
                log.write(log_entry)

    print(f"Successfully processed {NOTE_ID}. Stats updated.")

if __name__ == "__main__":
    update_files()