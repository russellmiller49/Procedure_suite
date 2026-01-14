import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================
NOTE_ID = "note_226"
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
# 2. RAW TEXT INPUT
# ==========================================
# Cleaned of tags for processing
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: left mainstem stent obstruction
POSTOPERATIVE DIAGNOSIS: 
Distal granulation tissue causing left lower lobe obstruction
PROCEDURE PERFORMED: flexible bronchoscopy with  cryodebulking/cryotherapy of obstructive granulation tissue, balloon dilatation od airways and endobronchial submucosal steroid injection.
INDICATIONS: complete lobar collapse  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The trachea and right sided airways were normal. The left mainstem stent was widely patent without evidence of obstruction.
At the takeoff of the left lower lobe just beyond surgical stump there was complete obstruction of the left lower lobe orifice secondary to adherent necrotic tissue.
Using the 1.9 mm cryoprobe we are able to extract some of the tissue to visualize the segmental stenosis in the left lower lobe.
We then utilized flexible forceps to slowly debulk the abnormal tissue.
Once we were able to pass the left lower lobe orifice there was continued areas of white necrotic tissue obstruction the superior segment and anteriomedial segments of the left lower lobe and extending to just proximal to the basilar segments.
This tissue was also slowly debulked with the flexible forceps until we were able to achieve relatively preserved luminal diameter.
We then utilized the -9-10 CRE balloon to dilate the left lower lobe orifice and the obstructed sub-segments.
Finally using the Olympus 21-gauge needle we injected a total of 80 mg of Kenalog  solution into the submucosa have areas of significant disease  in hopes of inducing an anti-inflammatory effect to prevent regrowth of inflammatory tissue.
Once we were satisfied that no further intervention was required the flexible bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
Recommendations:
-\tTransfer patient back to ward
-\tWill follow-up with pulmonary for further management on an outpatient basis."""

# ==========================================
# 3. ENTITY DEFINITIONS
# ==========================================
# Manual mapping based on Label_guide_UPDATED.csv
# Format: (Text_Substring, Label)
# Note: The order allows for sequential processing.
entities_to_extract = [
    ("left", "LATERALITY"),
    ("mainstem", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("obstruction", "OBS_FINDING"),
    ("granulation tissue", "OBS_FINDING"),
    ("left", "LATERALITY"),
    ("lower lobe", "ANAT_LUNG_LOC"),
    ("obstruction", "OBS_FINDING"),
    ("flexible bronchoscopy", "PROC_METHOD"),
    ("cryodebulking", "PROC_ACTION"),
    ("cryotherapy", "PROC_ACTION"),
    ("granulation tissue", "OBS_FINDING"),
    ("balloon dilatation", "PROC_ACTION"),
    ("steroid injection", "PROC_ACTION"),
    ("video bronchoscope", "DEV_INSTRUMENT"),
    ("trachea", "ANAT_AIRWAY"),
    ("right sided airways", "ANAT_AIRWAY"),
    ("left", "LATERALITY"),
    ("mainstem", "ANAT_AIRWAY"),
    ("stent", "DEV_STENT"),
    ("widely patent", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("obstruction", "OBS_FINDING"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("surgical stump", "ANAT_AIRWAY"),
    ("complete obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"),
    ("left lower lobe orifice", "ANAT_AIRWAY"),
    ("necrotic tissue", "OBS_FINDING"),
    ("1.9 mm", "MEAS_SIZE"),
    ("cryoprobe", "DEV_INSTRUMENT"),
    ("extract", "PROC_ACTION"),
    ("stenosis", "OBS_FINDING"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("debulk", "PROC_ACTION"),
    ("left lower lobe orifice", "ANAT_AIRWAY"),
    ("necrotic tissue", "OBS_FINDING"),
    ("obstruction", "OBS_FINDING"),
    ("superior segment", "ANAT_LUNG_LOC"),
    ("anteriomedial segments", "ANAT_LUNG_LOC"),
    ("left lower lobe", "ANAT_LUNG_LOC"),
    ("basilar segments", "ANAT_LUNG_LOC"),
    ("debulked", "PROC_ACTION"),
    ("flexible forceps", "DEV_INSTRUMENT"),
    ("preserved luminal diameter", "OUTCOME_AIRWAY_LUMEN_POST"),
    ("9-10", "MEAS_SIZE"),
    ("CRE balloon", "DEV_INSTRUMENT"),
    ("dilate", "PROC_ACTION"),
    ("left lower lobe orifice", "ANAT_AIRWAY"),
    ("21-gauge needle", "DEV_NEEDLE"),
    ("injected", "PROC_ACTION"),
    ("Kenalog", "MEDICATION"),
    ("flexible bronchoscope", "DEV_INSTRUMENT")
]

# ==========================================
# 4. PROCESSING LOGIC
# ==========================================

def calculate_spans(text, entity_list):
    spans = []
    # Use a cursor to scan through text to handle duplicate substrings correctly (chronological order)
    cursor = 0
    
    # We must be careful not to match the same text in the same position multiple times if the list repeats
    # But for this simple extractor, we iterate the list and search from the last cursor.
    # To support non-sequential definitions in the list above, we should ideally search from 0 every time 
    # but track used indices. However, for a single note script, sequential is safer if definitions are ordered.
    # Let's assume the entity_list is roughly in order of appearance or we use a smart find.
    
    # Better approach for robustness: Find all occurrences, map them, then select based on context?
    # Given the constraints, I will implement a robust sequential finder that resets for new unique terms 
    # but advances for repeated terms.
    
    found_indices = set() # Store (start, end) tuples
    
    final_entities = []

    # Helper to find next occurrence ensuring no overlap with existing found entities if possible,
    # or just finding the specific instance intended.
    # Since the input list is "flat", we will iterate and find the *next* available match.
    
    search_start = 0
    
    for term, label in entity_list:
        # Simple case insensitive search could be dangerous, so we use exact case from text if possible.
        # But to be safe against typos in my list vs text, I'll search case-insensitive then grab real text.
        
        start_idx = text.lower().find(term.lower(), search_start)
        
        if start_idx == -1:
            # Try searching from beginning if not found (maybe the list wasn't perfectly ordered)
            start_idx = text.lower().find(term.lower(), 0)
        
        if start_idx != -1:
            end_idx = start_idx + len(term)
            real_text = text[start_idx:end_idx]
            
            # Create span object
            span = {
                "start": start_idx,
                "end": end_idx,
                "label": label,
                "text": real_text
            }
            
            # Check for exact duplicates in this specific list processing (sanity check)
            # We allow same text diff location.
            if (start_idx, end_idx) not in found_indices:
                final_entities.append(span)
                found_indices.add((start_idx, end_idx))
                # Update search_start to avoid finding this exact instance again for the same term
                # We move cursor only if we want strictly sequential. 
                # To be safe: if we found "left" at 10, next search for "left" starts at 14.
                # If we search for "trachea" (which might be earlier), we rely on find(..., 0) fallback above,
                # but that risks re-finding the first "trachea" if there are two.
                # For this specific note, the list above is roughly ordered.
                search_start = end_idx 
            else:
                # If we found an index we already used, we need to find the *next* one.
                # Loop until we find a fresh one
                temp_start = end_idx
                while True:
                    next_start = text.lower().find(term.lower(), temp_start)
                    if next_start == -1: break
                    next_end = next_start + len(term)
                    if (next_start, next_end) not in found_indices:
                        real_text = text[next_start:next_end]
                        span = {
                            "start": next_start,
                            "end": next_end,
                            "label": label,
                            "text": real_text
                        }
                        final_entities.append(span)
                        found_indices.add((next_start, next_end))
                        search_start = next_end
                        break
                    temp_start = next_end

    return final_entities

def update_stats(stats_path, new_labels_count, valid_spans_count):
    if stats_path.exists():
        with open(stats_path, 'r') as f:
            stats = json.load(f)
    else:
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }

    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += valid_spans_count
    stats["total_spans_valid"] += valid_spans_count

    for label, count in new_labels_count.items():
        if label in stats["label_counts"]:
            stats["label_counts"][label] += count
        else:
            stats["label_counts"][label] = count

    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

def main():
    # 1. Calculate Entities
    entities = calculate_spans(RAW_TEXT, entities_to_extract)
    
    # 2. Count Labels for Stats
    label_counts = {}
    for ent in entities:
        lbl = ent['label']
        label_counts[lbl] = label_counts.get(lbl, 0) + 1

    # 3. Prepare Data Lines
    ner_line = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": entities
    }
    
    note_line = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    span_lines = []
    for ent in entities:
        span_id = f"{ent['label']}_{ent['start']}"
        span_lines.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": ent['label'],
            "text": ent['text'],
            "start": ent['start'],
            "end": ent['end']
        })

    # 4. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, 'a') as f:
        f.write(json.dumps(ner_line) + "\n")
        
    # Append to notes.jsonl
    with open(NOTES_PATH, 'a') as f:
        f.write(json.dumps(note_line) + "\n")
        
    # Append to spans.jsonl
    with open(SPANS_PATH, 'a') as f:
        for sl in span_lines:
            f.write(json.dumps(sl) + "\n")

    # 5. Update Stats
    update_stats(STATS_PATH, label_counts, len(entities))

    # 6. Validation Logging
    with open(LOG_PATH, 'a') as log_file:
        for ent in entities:
            # Verify exact text match
            snippet = RAW_TEXT[ent['start']:ent['end']]
            if snippet != ent['text']:
                log_msg = f"WARNING: Alignment mismatch in {NOTE_ID}. Expected '{ent['text']}', got '{snippet}' at {ent['start']}:{ent['end']}\n"
                log_file.write(log_msg)
                print(log_msg)

    print(f"Successfully processed {NOTE_ID} with {len(entities)} entities.")

if __name__ == "__main__":
    main()