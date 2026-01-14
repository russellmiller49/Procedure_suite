import json
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_190"
NOTE_CONTENT = """Indications: Mediastinal adenopathy and lung mass
Procedure Performed: EBUS bronchoscopy single station.
Pre-operative diagnosis: Lung mass 
Post-operative diagnosis: malignant mediastinal adenopathy, new onset A. fib 
Medications: General Anesthesia,
Procedure, risks, benefits, and alternatives were explained to the patient.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea is of normal caliber. The carina is sharp. Blood was seen within the right main-stem and gently suctioned.
The tracheobronchial tree was examined to at least the first sub-segmental level.
Obvious sub-mucosal infiltration of tumor was seen through the bronchus intermedius extending into the right middle lobe.
The right upper lobe was obstructed from combination extrinsic compression and sub-mucosal infiltration.
Blood was seen slowly oozing from the right upper lobe. The right lower lobe bronchial mucosa and anatomy were normal;
without endobronchial lesions. The left sided airways had normal bronchial mucosa and anatomy; without endobronchial lesions.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
Ultrasound was utilized to identify and measure the 4R lymph node which was a conglomerate of nodes extending into the station 10R .
Sampling by transbronchial needle aspiration was performed  with the Olympus EBUS-TBNA 22 gauge needle.
Rapid onsite evaluation read as malignancy. All samples were sent for routine cytology.
Near the end of the procedure the patient became significantly tachycardic and hypotensive with new onset A. fib with RVR.
The EBUS bronchoscope was removed and the Q190 video bronchoscope was re-inserted and blood was suctioned from the airway.
The bronchoscope was removed and procedure completed. Cardiology was called to the bedside and decision was made for bedside cardioversion which was successful in terminating the rhythm for a short period however she subsequently returned to atrial flutter but with a more controlled rate.
After awakening the patient had difficulty with oxygen saturation for a few minutes and we reintroduced the bronchoscope through the nasal passage to evaluate for evidence of active bleeding within the airway, none was seen.
The patient was then transferred to the ICU for observation status post cardioversion in good condition.
Complications: Intraoperative atrial fibrillation with RVR
Estimated Blood Loss: 10 cc.
Post Procedure Diagnosis:
- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
-New onset atrial fibrillation
Recommendations
- Will await final pathology results
- We’ll discuss with radiation oncology early treatment to right upper lobe given active hemoptysis."""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"
LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# ENTITY EXTRACTION LOGIC
# ==========================================
# Entity definitions based on Label_guide_UPDATED.csv and text analysis
# List of (Text_Substring, Label, Occurrence_Index)
# Occurrence_Index=0 means first found, 1 means second, etc.
# If Occurrence_Index is -1, it finds ALL non-overlapping occurrences.
entities_to_map = [
    # Indications
    ("adenopathy", "OBS_LESION", 0),
    ("lung", "ANAT_LUNG_LOC", 0),
    ("mass", "OBS_LESION", 0),
    
    # Procedure Performed
    ("EBUS bronchoscopy", "PROC_METHOD", 0),
    
    # Diagnosis
    ("Lung", "ANAT_LUNG_LOC", 1), # Pre-op
    ("mass", "OBS_LESION", 1),    # Pre-op
    ("adenopathy", "OBS_LESION", 1), # Post-op
    
    # Procedure Body
    ("upper airway", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 0),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT", 0),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 1),
    
    # Findings
    ("laryngeal mask airway", "DEV_INSTRUMENT", 1),
    ("vocal cords", "ANAT_AIRWAY", 0),
    ("subglottic space", "ANAT_AIRWAY", 0),
    ("trachea", "ANAT_AIRWAY", 0),
    ("carina", "ANAT_AIRWAY", 0),
    ("right main-stem", "ANAT_AIRWAY", 0),
    ("tracheobronchial tree", "ANAT_AIRWAY", 2),
    
    ("infiltration", "OBS_LESION", 0),
    ("tumor", "OBS_LESION", 0),
    ("bronchus intermedius", "ANAT_AIRWAY", 0),
    ("right middle lobe", "ANAT_LUNG_LOC", 0),
    
    ("right upper lobe", "ANAT_LUNG_LOC", 0),
    ("compression", "OBS_FINDING", 0),
    ("infiltration", "OBS_LESION", 1), # sub-mucosal infiltration
    
    ("right upper lobe", "ANAT_LUNG_LOC", 1), # oozing from
    ("oozing", "OBS_FINDING", 0),
    ("right lower lobe", "ANAT_LUNG_LOC", 0),
    ("endobronchial lesions", "OBS_LESION", 0),
    ("left", "LATERALITY", 0),
    ("airways", "ANAT_AIRWAY", 0), # left sided airways
    ("endobronchial lesions", "OBS_LESION", 1),
    
    # EBUS section
    ("video bronchoscope", "DEV_INSTRUMENT", 1),
    ("UC180F convex probe EBUS bronchoscope", "DEV_INSTRUMENT", 0),
    ("laryngeal mask airway", "DEV_INSTRUMENT", 2),
    ("tracheobronchial tree", "ANAT_AIRWAY", 3),
    
    ("4R", "ANAT_LN_STATION", 0),
    ("station 10R", "ANAT_LN_STATION", 0),
    
    ("transbronchial needle aspiration", "PROC_ACTION", 0),
    ("Olympus EBUS-TBNA", "DEV_INSTRUMENT", 0),
    ("22 gauge", "DEV_NEEDLE", 0),
    
    ("malignancy", "OBS_ROSE", 0),
    
    # Complications/Events
    ("tachycardic", "OBS_FINDING", 0),
    ("hypotensive", "OBS_FINDING", 0),
    ("A. fib", "OBS_FINDING", 1), # New onset in text
    ("RVR", "OBS_FINDING", 0),
    
    ("EBUS bronchoscope", "DEV_INSTRUMENT", 1),
    ("Q190 video bronchoscope", "DEV_INSTRUMENT", 1),
    ("airway", "ANAT_AIRWAY", 5), # suctioned from airway
    
    ("bronchoscope", "DEV_INSTRUMENT", 4), # removed
    ("bedside cardioversion", "PROC_ACTION", 0),
    ("atrial flutter", "OBS_FINDING", 0),
    
    ("bronchoscope", "DEV_INSTRUMENT", 5), # reintroduced
    ("active bleeding", "OBS_FINDING", 0),
    ("airway", "ANAT_AIRWAY", 6), # bleeding within airway
    
    # Complications Section
    ("Intraoperative atrial fibrillation with RVR", "OUTCOME_COMPLICATION", 0),
    ("10 cc", "MEAS_VOL", 0),
    
    # Post Procedure
    ("flexible bronchoscopy", "PROC_METHOD", 0),
    ("endobronchial ultrasound", "PROC_METHOD", 0), # guided
    ("biopsies", "PROC_ACTION", 0),
    
    ("right upper lobe", "ANAT_LUNG_LOC", 2), # recs
    ("hemoptysis", "OBS_FINDING", 0)
]

def find_spans(text, entities):
    found_spans = []
    
    # Sort entities to handle overlaps or order issues? 
    # Logic: find index of Nth occurrence
    
    for text_str, label, occurrence in entities:
        # Find all start indices of text_str
        matches = [m.start() for m in re.finditer(re.escape(text_str), text)]
        
        if not matches:
            print(f"WARNING: '{text_str}' not found in text.")
            continue
            
        if occurrence >= len(matches):
            print(f"WARNING: Occurrence {occurrence} of '{text_str}' requested, but only {len(matches)} found.")
            continue
            
        start_idx = matches[occurrence]
        end_idx = start_idx + len(text_str)
        
        found_spans.append({
            "span_id": f"{label}_{start_idx}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text_str,
            "start": start_idx,
            "end": end_idx
        })
        
    # Sort by start index
    found_spans.sort(key=lambda x: x['start'])
    return found_spans

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    # 1. Extract Spans
    spans = find_spans(NOTE_CONTENT, entities_to_map)
    
    # 2. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": NOTE_CONTENT,
        "entities": [
            {
                "id": s["span_id"],
                "label": s["label"],
                "start_offset": s["start"],
                "end_offset": s["end"]
            }
            for s in spans
        ]
    }
    
    with open(NER_DATASET_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # 3. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": NOTE_CONTENT
    }
    
    with open(NOTES_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # 4. Update spans.jsonl
    with open(SPANS_PATH, 'a', encoding='utf-8') as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")
            
    # 5. Validation & Logging
    warnings = []
    for span in spans:
        extracted = NOTE_CONTENT[span['start']:span['end']]
        if extracted != span['text']:
            warnings.append(f"Mismatch in {NOTE_ID}: Expected '{span['text']}', got '{extracted}' at {span['start']}-{span['end']}")
            
    if warnings:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            for w in warnings:
                f.write(w + "\n")
    
    # 6. Update stats.json
    try:
        with open(STATS_PATH, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            
        stats['total_files'] += 1
        stats['total_notes'] += 1
        stats['total_spans_raw'] += len(spans)
        stats['total_spans_valid'] += len(spans)
        
        # Update label counts
        for span in spans:
            lbl = span['label']
            if lbl in stats['label_counts']:
                stats['label_counts'][lbl] += 1
            else:
                stats['label_counts'][lbl] = 1
                
        with open(STATS_PATH, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
            
    except Exception as e:
        print(f"Error updating stats.json: {e}")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(spans)} entities.")

if __name__ == "__main__":
    main()