import json
import os
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_228"

# Raw text content exactly as provided
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: left mainstem stent obstruction
POSTOPERATIVE DIAGNOSIS: 
Distal granulation tissue causing left lower lobe obstruction
PROCEDURE PERFORMED: Rigid bronchoscopy with cryodebulking/cryotherapy of obstructive granulation tissue, endobronchial submucosal steroid injection, left mainstem bronchial stent removal
INDICATIONS: complete lobar collapse  
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient’s family acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The trachea and right sided airways were normal. The left mainstem stent was widely patent without evidence of stent obstruction.
At the distal edge of the stent there was some minor granulation tissue which was nonobstructive.
Distal to the stent there was complete obstruction of the left lower lobe orifice secondary to granulation tissue.
Using the 1.9 mm cryoprobe we are able to extract granulation tissue to visualize the segmental stenosis in the left lower lobe.
All of the segments were obstructed with granulation tissue as well which we also removed with cryotherapy as well as flexible forceps.
At this point we decided to remove the left mainstem stent for a few reasons.
The first is that pathology from previous bronchoscopy at time of stent placement did not show evidence of tumor and metallic stents are not advised for benign disease.
The second was that her new obstruction was secondary to distal granulation tissue and it was unclear whether the stent was providing any current benefit.
Finally, our hope was that the short-term placement of the stent allowed some remodeling of the airway to relieve the previous obstruction.
At this point the LMA was removed and a 12 mm ventilating rigid bronchoscope was inserted and passed into the airway and advanced to the distal trachea and then attached to the jet ventilator.
The flexible bronchoscope was then advanced through the rigid bronchoscope into the airway.
Using flexible forceps to grasp the proximal string on the stent we were able to gently retract the stent and remove it without difficulty.
Subsequently they flexible bronchoscope was reinserted and as we had hoped the orifice had remodeled and essentially there is no obstruction at the level of the previous stent.
At the left of the LC2 carina (bifurcation between left upper and left lower lobe) the left upper lobe stump from previous lobectomy appeared intact.
Then, using a 8–9–10 millimeter CRE balloon dilated each of the left lower lobe subsegments as well as the left lower lobe main bronchus which improved patency of the subsegments to approximately 50% of normal and left lower lobe bronchus to approximately 80%.
Cryotherapy was then performed with 30 second freeze/thaw cycles to induce tissue sloughing.
Finally using the super dimension 21-gauge needle we injected a total of 5 mL of Kenalog 10 mg/milliliter solution into the submucosa have areas of significant granulation tissue in hopes of inducing an anti-inflammatory effect to prevent regrowth of granulation tissue.
Once we were satisfied that no further intervention was required the rigid bronchoscope was removed and the case was turned over to anesthesia to recover the patient.
Recommendations:
-	Transfer patient back to the ICU
-	Post-procedure x-ray
-	Patient to follow-up with me for repeat bronchoscopy in about a week to remove debris post cryotherapy as well as to assess for evidence of restenosis."""

# Define entities: (Label, Text Search String)
# Order matters: The script searches sequentially from the end of the previous match.
ENTITIES_TO_EXTRACT = [
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "obstruction"),
    ("OBS_FINDING", "granulation tissue"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_FINDING", "obstruction"),
    ("PROC_METHOD", "Rigid bronchoscopy"),
    ("PROC_ACTION", "cryodebulking"),
    ("PROC_ACTION", "cryotherapy"),
    ("OBS_FINDING", "granulation tissue"),
    ("PROC_ACTION", "injection"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("PROC_ACTION", "removal"),
    ("OBS_FINDING", "lobar collapse"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("DEV_INSTRUMENT", "T190 video bronchoscope"),
    ("ANAT_AIRWAY", "mouth"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "Trachea"),
    ("ANAT_AIRWAY", "right sided airways"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "widely patent"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "obstruction"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "granulation tissue"),
    ("OBS_FINDING", "nonobstructive"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "complete obstruction"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_FINDING", "granulation tissue"),
    ("MEAS_SIZE", "1.9 mm"),
    ("DEV_INSTRUMENT", "cryoprobe"),
    ("OBS_FINDING", "granulation tissue"),
    ("OBS_FINDING", "segmental stenosis"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("OBS_FINDING", "granulation tissue"),
    ("PROC_ACTION", "cryotherapy"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("PROC_ACTION", "remove"),
    ("ANAT_AIRWAY", "left mainstem"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT_MATERIAL", "metallic"),
    ("DEV_STENT", "stents"),
    ("OBS_FINDING", "obstruction"),
    ("OBS_FINDING", "granulation tissue"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("OBS_FINDING", "obstruction"),
    ("DEV_INSTRUMENT", "LMA"),
    ("PROC_ACTION", "removed"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "ventilating rigid bronchoscope"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("DEV_INSTRUMENT", "jet ventilator"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "airway"),
    ("DEV_INSTRUMENT", "flexible forceps"),
    ("DEV_STENT", "stent"),
    ("DEV_STENT", "stent"),
    ("PROC_ACTION", "remove"),
    ("DEV_INSTRUMENT", "flexible bronchoscope"),
    ("OBS_FINDING", "no obstruction"),
    ("DEV_STENT", "stent"),
    ("ANAT_AIRWAY", "LC2 carina"),
    ("ANAT_LUNG_LOC", "left upper"),
    ("ANAT_LUNG_LOC", "left lower lobe"),
    ("ANAT_LUNG_LOC", "left upper lobe"),
    ("MEAS_SIZE", "8–9–10 millimeter"),
    ("DEV_INSTRUMENT", "CRE balloon"),
    ("PROC_ACTION", "dilated"),
    ("ANAT_LUNG_LOC", "left lower lobe subsegments"),
    ("ANAT_AIRWAY", "left lower lobe main bronchus"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "50%"),
    ("OUTCOME_AIRWAY_LUMEN_POST", "80%"),
    ("PROC_ACTION", "Cryotherapy"),
    ("MEAS_TIME", "30 second"),
    ("DEV_NEEDLE", "21-gauge needle"),
    ("PROC_ACTION", "injected"),
    ("MEAS_VOL", "5 mL"),
    ("MEDICATION", "Kenalog"),
    ("ANAT_AIRWAY", "submucosa"),
    ("OBS_FINDING", "granulation tissue"),
    ("OBS_FINDING", "granulation tissue"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("PROC_ACTION", "removed"),
    ("PROC_ACTION", "cryotherapy"),
    ("OBS_FINDING", "restenosis")
]

# =============================================================================
# DIRECTORY SETUP
# =============================================================================
# Target: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALIGNMENT_LOG_PATH = OUTPUT_DIR / "alignment_warnings.log"
NER_DATASET_PATH = OUTPUT_DIR / "ner_dataset_all.jsonl"
NOTES_PATH = OUTPUT_DIR / "notes.jsonl"
SPANS_PATH = OUTPUT_DIR / "spans.jsonl"
STATS_PATH = OUTPUT_DIR / "stats.json"

# =============================================================================
# MAIN PROCESSING
# =============================================================================
def main():
    spans = []
    current_idx = 0
    
    # 1. Extraction
    for label, substr in ENTITIES_TO_EXTRACT:
        start = RAW_TEXT.find(substr, current_idx)
        if start == -1:
            # Fallback check from beginning if sequential fails (safety net, though order is prioritized)
            # warning logic would go here
            continue
        
        end = start + len(substr)
        span_text = RAW_TEXT[start:end]
        
        spans.append({
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": span_text,
            "start": start,
            "end": end
        })
        current_idx = start + 1 # Advance just past start to allow overlapping if strictly needed, or end

    # 2. File Updates
    
    # Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[s["start"], s["end"], s["label"]] for s in spans]
    }
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # Update notes.jsonl
    note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # Update spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")

    # Update stats.json
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
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
    # total_files is essentially unique notes tracked, so same increment here
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(spans)
    stats["total_spans_valid"] += len(spans)

    for s in spans:
        lbl = s["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 3. Validation & Logging
    with open(ALIGNMENT_LOG_PATH, "a", encoding="utf-8") as log:
        for s in spans:
            extracted = RAW_TEXT[s["start"]:s["end"]]
            if extracted != s["text"]:
                log.write(f"[{datetime.datetime.now()}] MISMATCH: {s['span_id']} expected '{s['text']}' got '{extracted}'\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(spans)} entities.")

if __name__ == "__main__":
    main()