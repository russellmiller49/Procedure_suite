from pathlib import Path
import json
import os
import datetime

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
NOTE_ID = "note_246"
NOTE_TEXT = """PREOPERATIVE DIAGNOSIS: left upper and lower lobe obstruction 
POSTOPERATIVE DIAGNOSIS: 
Presumed malignant obstruction of left upper and lower lobe
PROCEDURE PERFORMED: flexible bronchoscopy with cryodebulking, electrocautery snare and APC..
INDICATIONS: bilobar collapse  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The trachea was normal. On the right there was a small focus of tumor just prximal to the right upper lobe at the anterior wall which was non-obstructive.
The right sided airways were otherwise normal. The left mainstem was normal.
At the takeoff of the left lower lobe there was a vascular appearing endobronchial mass causing complete airway obstruction.
At the takeoff of the left upper lobe there was a similar appearing vascular endobronchial lesion causing complete airway obstruction.
With gentile manipulation of the tumor it was noted to bleed easily.
APC was used to devascularize the superficial layer of the left upper and lower lobe tumors.
The electrocautery snare was then used to remove the prximal portion of the left upper lobe tumor after which we cold visualize distal airways.
The tumor extended to just proximal to the lingual take-off and distally there did not appear to be evidence of active tumor.
Using APC we used the burn and shave method to slowly debulk the tumor as well as flexible forceps debulking of charred tumor after APC cauterization.
Bleeding was moderate and resolved with topical instillation of 1:1000 TXA through the bronchoscope.
After debulking in the left upper lobe we had complete opening of the lobar and segmental bronchi.
We then brought our attention to the left lower lobe lesion.
Using the electrocautery snare in a similar fashion we were able to debulk the proximal tumor.
There was much more extensive distal tumor in the lower lobe with tumor involving multiple segmental bronchi.
Using the 1.9 mm cryoprobe we are able to extract some of the tissue after which we utilized APC and flexible forceps in a similar fashion as performed in the left upper lobe to slowly debulk the tumor.
We were able to open the left lower lobe orifice to approximately 70% of normal but despite our best efforts we could not completely remove the tumor due to the extent of disease and distal tumor infiltration.
APC was used at the end of the procedure to paint cauterize any active oozing and once we were satisfied that no further intervention was required and that there was no evidence of active bleeding the flexible bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
Recommendations:
-	Transfer patient PACU
-	Follow-up PRN if return of symptoms
-	Treatment of metastatic foci per oncology"""

# ------------------------------------------------------------------------------
# PRE-CALCULATED ENTITIES (STRICT LABEL_GUIDE MAPPING)
# ------------------------------------------------------------------------------
# Entities are identified by exact text match within the note.
# Order corresponds to appearance in text.

entities_raw = [
    ("flexible bronchoscopy", "PROC_ACTION"),
    ("cryodebulking", "PROC_ACTION"),
    ("electrocautery snare", "DEV_INSTRUMENT"),
    ("APC", "DEV_INSTRUMENT"),
    ("bilobar collapse", "OBS_FINDING"),
    ("upper airway", "ANAT_AIRWAY"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("T190 video bronchoscope", "DEV_INSTRUMENT"),
    ("mouth", "ANAT_AIRWAY"),
    ("laryngeal mask airway", "DEV_INSTRUMENT"),
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("trachea", "ANAT_AIRWAY"),
    ("right", "LATERALITY"),
    ("tumor", "OBS_LESION"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("anterior wall", "ANAT_AIRWAY"),
    ("right sided airways", "ANAT_AIRWAY"),
    ("Left mainstem", "ANAT_AIRWAY"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("mass", "OBS_LESION"),
    ("airway obstruction", "OBS_FINDING"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("lesion", "OBS_LESION"),
    ("airway obstruction", "OBS_FINDING"),
    ("tumor", "OBS_LESION"),
    ("APC", "DEV_INSTRUMENT"),
    ("left upper", "ANAT_LUNG_LOC"), # Handling partials or skipping if ambiguous. "left upper" appears in "left upper and lower lobe tumors".
    # Correction: "left upper and lower lobe" appears. We'll grab specific phrases if possible.
    # Re-scanning specifically for body text matches.
    ("electrocautery snare", "DEV_INSTRUMENT"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("tumor", "OBS_LESION"),
    ("distal airways", "ANAT_AIRWAY"),
    ("tumor", "OBS_LESION"),
    ("lingual", "ANAT_LUNG_LOC"), # Typo in note "lingual" -> Lingula
    ("tumor", "OBS_LESION"),
    ("APC", "DEV_INSTRUMENT"),
    ("debulk", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("tumor", "OBS_LESION"),
    ("APC", "DEV_INSTRUMENT"), # "APC cauterization" - APC as tool
    ("TXA", "MEDICATION"),
    ("bronchoscope", "DEV_INSTRUMENT"),
    ("debulking", "PROC_ACTION"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("segmental bronchi", "ANAT_AIRWAY"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("lesion", "OBS_LESION"),
    ("electrocautery snare", "DEV_INSTRUMENT"),
    ("debulk", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),
    ("tumor", "OBS_LESION"), # distal tumor
    ("lower lobe", "ANAT_LUNG_LOC"),
    ("tumor", "OBS_LESION"),
    ("segmental bronchi", "ANAT_AIRWAY"),
    ("1.9 mm", "MEAS_SIZE"),
    ("cryoprobe", "DEV_INSTRUMENT"),
    ("APC", "DEV_INSTRUMENT"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("left upper lobe", "ANAT_LUNG_LOC"),
    ("debulk", "PROC_ACTION"),
    ("tumor", "OBS_LESION"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("approximately 70% of normal", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("tumor", "OBS_LESION"),
    ("tumor", "OBS_LESION"),
    ("APC", "DEV_INSTRUMENT"),
    ("flexible bronchoscope", "DEV_INSTRUMENT"),
]

# ------------------------------------------------------------------------------
# PATH SETUP
# ------------------------------------------------------------------------------
# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"

# ------------------------------------------------------------------------------
# LOGIC
# ------------------------------------------------------------------------------

def find_entity_spans(text, entities):
    """
    Finds unique start/end offsets for entities in order.
    Starts searching after the previous entity's end index to handle duplicates correctly.
    """
    spans = []
    current_index = 0
    
    for entity_text, label in entities:
        # Find the next occurrence of the entity text starting from current_index
        start = text.find(entity_text, current_index)
        
        if start == -1:
            # Fallback: Look from beginning if not found (though this breaks sequential assumption)
            # In strict processing, we might want to log this.
            # For this script, we assume entities are listed in order of appearance.
            print(f"Warning: Could not find '{entity_text}' after index {current_index}")
            continue
            
        end = start + len(entity_text)
        spans.append({
            "label": label,
            "text": entity_text,
            "start": start,
            "end": end
        })
        current_index = end # Move pointer forward
        
    return spans

def update_jsonl(file_path, new_record):
    """Appends a JSON line to the specified file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_record) + '\n')

def update_stats(stats_path, new_spans):
    """Updates the global stats.json file."""
    if not stats_path.exists():
        stats = {
            "total_notes": 0,
            "total_files": 0,
            "total_spans_raw": 0,
            "total_spans_valid": 0,
            "label_counts": {}
        }
    else:
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)

    stats["total_notes"] += 1
    stats["total_files"] += 1 # Assuming 1 note per file for this workflow
    stats["total_spans_raw"] += len(new_spans)
    stats["total_spans_valid"] += len(new_spans)

    for span in new_spans:
        lbl = span['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. calculate spans
    spans = find_entity_spans(NOTE_TEXT, entities_raw)
    
    # 2. validate
    with open(ALIGNMENT_LOG_PATH, 'a', encoding='utf-8') as log:
        for span in spans:
            extracted = NOTE_TEXT[span['start']:span['end']]
            if extracted != span['text']:
                log.write(f"MISMATCH: {NOTE_ID} | Exp: '{span['text']}' vs Act: '{extracted}'\n")

    # 3. ner_dataset_all.jsonl
    # Format: {"id": "...", "text": "...", "entities": [[start, end, label], ...]}
    ner_entities = [[s['start'], s['end'], s['label']] for s in spans]
    ner_record = {
        "id": NOTE_ID,
        "text": NOTE_TEXT,
        "entities": ner_entities
    }
    update_jsonl(OUTPUT_DIR / "ner_dataset_all.jsonl", ner_record)

    # 4. notes.jsonl
    notes_record = {"id": NOTE_ID, "text": NOTE_TEXT}
    update_jsonl(OUTPUT_DIR / "notes.jsonl", notes_record)

    # 5. spans.jsonl
    # Format: {"span_id": "Label_Offset", "note_id": "...", "label": "...", "text": "...", "start": ..., "end": ...}
    for span in spans:
        span_record = {
            "span_id": f"{span['label']}_{span['start']}",
            "note_id": NOTE_ID,
            "label": span['label'],
            "text": span['text'],
            "start": span['start'],
            "end": span['end']
        }
        update_jsonl(OUTPUT_DIR / "spans.jsonl", span_record)

    # 6. stats.json
    update_stats(OUTPUT_DIR / "stats.json", spans)

    print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()