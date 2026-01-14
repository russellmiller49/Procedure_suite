from pathlib import Path
import json
import os
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_174"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Raw Text Content (Verbatim from source)
RAW_TEXT = """Procedure Name: EBUS bronchoscopy
Indications: Pulmonary nodule requiring diagnosis/staging.
Medications: Propofol infusion via anesthesia assistance  
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention. 
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level without endobronchial lesions visualized.
Anatomy was normal with exception of what appears to be a fused anterior segment of left upper lobe with lingula.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) was only met in station station 4R.
Sampling by transbronchial needle aspiration was performed using an Olympus EBUSTBNA 22 gauge needle.
Further details regarding nodal size and number of samples are included in the EBUS procedural sheet in AHLTA.
All samples were sent for routine cytology. Onsite path evaluation did not identify malignancy.
The bronchoscope was then removed and the P190 ultrathin video bronchoscope was inserted into the airway and based on anatomical knowledge advanced into the left upper lobe to the area of known nodule within the anterior segment and an eccentric view of the lesion was identified with the radial EBUS.
Biopsies were then performed with a variety of instruments to include peripheral needle forceps and brush.
After adequate samples were obtained the bronchoscope was removed. ROSE did not identify malignancy on preliminary samples.
The bronchoscope was then removed and the P190 re-inserted into the airways.
DECAMP research samples were then performed with brushing within the right upper lobe, right middle lobe and transbronchial biopsies in the RUL, RML and LUL.
We ten observed for evidence of active bleeding and none was identified. The bronchoscope was removed and the procedure completed.
Complications: 	
-None 
Estimated Blood Loss:  10 cc.
Recommendations:
- Transfer to PACU
- Await biopsy results 
- Discharge home once criteria met."""

# Entity Definitions: (Label, Text_Snippet, Occurrence_Index_If_Repeated)
# Occurrence index 0 = first match, 1 = second match, etc.
# If no index provided, logic assumes sequential order from previous match end.
ENTITIES_SEQUENTIAL = [
    ("PROC_METHOD", "EBUS"),
    ("OBS_LESION", "nodule"),
    ("MEDICATION", "Propofol"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "trachea"),
    ("ANAT_AIRWAY", "carina"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("OBS_LESION", "lesions"),
    ("ANAT_LUNG_LOC", "anterior segment"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("ANAT_LUNG_LOC", "lingula"),
    ("DEV_INSTRUMENT", "UC180F convex probe EBUS bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_LN_STATION", "hilar"),
    ("ANAT_LN_STATION", "mediastinal"),
    ("MEAS_SIZE", "5mm"),
    ("ANAT_LN_STATION", "station 4R"),
    ("PROC_ACTION", "transbronchial needle aspiration"),
    ("DEV_NEEDLE", "22 gauge"),
    ("SPECIMEN", "samples"), # "All samples were sent..."
    ("OBS_ROSE", "malignancy"),
    ("DEV_INSTRUMENT", "P190 ultrathin video bronchoscope"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("OBS_LESION", "nodule"),
    ("ANAT_LUNG_LOC", "anterior segment"),
    ("PROC_METHOD", "radial EBUS"),
    ("PROC_ACTION", "Biopsies"),
    ("DEV_INSTRUMENT", "forceps"),
    ("DEV_INSTRUMENT", "brush"),
    ("SPECIMEN", "samples"), # "After adequate samples..."
    ("OBS_ROSE", "malignancy"), # "ROSE did not identify malignancy"
    ("DEV_INSTRUMENT", "P190"),
    ("SPECIMEN", "samples"), # "DECAMP research samples"
    ("PROC_ACTION", "brushing"),
    ("ANAT_LUNG_LOC", "right upper lobe"),
    ("ANAT_LUNG_LOC", "right middle lobe"),
    ("PROC_ACTION", "transbronchial biopsies"),
    ("ANAT_LUNG_LOC", "RUL"),
    ("ANAT_LUNG_LOC", "RML"),
    ("ANAT_LUNG_LOC", "LUL"),
    ("OBS_FINDING", "active bleeding"),
    ("OUTCOME_COMPLICATION", "None"),
    ("MEAS_VOL", "10 cc")
]

# ==========================================
# PROCESSING LOGIC
# ==========================================

def update_pipeline():
    print(f"Processing {NOTE_ID}...")
    
    # 1. Calculate Offsets
    entities_with_offsets = []
    cursor = 0
    alignment_issues = []

    for label, substr in ENTITIES_SEQUENTIAL:
        start_idx = RAW_TEXT.find(substr, cursor)
        if start_idx == -1:
            # Fallback: search from beginning if not found sequentially (should not happen if ordered)
            # This handles cases where human ordering might be slightly off in the list
            start_idx = RAW_TEXT.find(substr)
            if start_idx == -1:
                print(f"CRITICAL ERROR: Could not find substring '{substr}' in text.")
                continue
        
        end_idx = start_idx + len(substr)
        
        # Verify
        extracted = RAW_TEXT[start_idx:end_idx]
        if extracted != substr:
            alignment_issues.append(f"Mismatch: Expected '{substr}', got '{extracted}' at {start_idx}")
        
        entities_with_offsets.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": substr,
            "start": start_idx,
            "end": end_idx
        })
        
        # Move cursor to avoid re-matching the same instance
        cursor = start_idx + 1

    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities_with_offsets
    }
    
    ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    with open(ner_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 3. Update notes.jsonl
    notes_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    notes_file = OUTPUT_DIR / "notes.jsonl"
    with open(notes_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(notes_entry) + "\n")

    # 4. Update spans.jsonl
    spans_file = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file, "a", encoding="utf-8") as f:
        for span in entities_with_offsets:
            f.write(json.dumps(span) + "\n")

    # 5. Update stats.json
    stats_file = OUTPUT_DIR / "stats.json"
    if stats_file.exists():
        with open(stats_file, "r", encoding="utf-8") as f:
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
    stats["total_files"] += 1 # Assuming 1 note per file context
    stats["total_spans_raw"] += len(entities_with_offsets)
    stats["total_spans_valid"] += len(entities_with_offsets)

    for span in entities_with_offsets:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 6. Log Warnings
    if alignment_issues:
        log_file = OUTPUT_DIR / "alignment_warnings.log"
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().isoformat()
            f.write(f"[{timestamp}] {NOTE_ID} Issues:\n")
            for issue in alignment_issues:
                f.write(f"  - {issue}\n")

    print(f"Successfully processed {NOTE_ID} with {len(entities_with_offsets)} entities.")

if __name__ == "__main__":
    update_pipeline()