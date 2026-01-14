import json
import os
import re
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
NOTE_ID = "note_042"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATS_FILE = Path(__file__).resolve().parents[2] / "stats.json" 
# Assuming stats.json is in the root of the data folder or similar relative path. 
# Adjusting to look in the same directory as the Label_guide/stats uploaded if needed, 
# but based on prompt "repo-ready", I'll assume standard relative path.
# If stats.json was uploaded, it might be local. I will assume it's in the parent of output or local.
# For this script, I will try to locate it relative to the script or default to current dir.
STATS_FILE_PATH = Path("stats.json")

# =============================================================================
# INPUT DATA
# =============================================================================
RAW_TEXT = """NOTE_ID:  note_042 SOURCE_FILE: note_042.txt INDICATION FOR OPERATION:  68 year old-year-old female with respiratory failure.
PREOPERATIVE DIAGNOSIS: J96.90 Respiratory Failure
 
POSTOPERATIVE DIAGNOSIS:  J96.90 Respiratory Failure
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)    
31600 Incision of windpipe (perc trach)
43246 Esophagogastroduodenoscopy, flexible, transoral;
with directed placement of percutaneous gastrostomy tube
76536 Ultrasound of Neck
 
ANESTHESIA: 
99152 Moderate sedation: initial 15 minutes
99153 Moderate sedation: each additional 15 minutes 
 
Procedure performed under moderate sedation.
The following medications were provided:
Versed             4 mg
Fentanyl          100 mcg
Etomidate20mg
Rocuronium43mg
 
Physician/patient face-to-face anesthesia start time:   1513
 
Physician/patient face-to-face anesthesia stop time:   1700
 
Total moderate sedation time was 107 minutes.
Patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.
Sedation was administered by ICU RN. 
 
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Flexible Therapeutic Bronchoscope
 
ESTIMATED BLOOD LOSS:   Minimum
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: Supine
 
Initial Airway Inspection Findings:
 
The endotracheal tube is in good position.
Pharynx: Not assessed due to bronchoscopy introduction through ETT.
Larynx: Not assessed due to bronchoscopy introduction through ETT.
Vocal Cords: Not assessed due to bronchoscopy introduction through ETT.
Trachea: Distal 1/3 normal.
Main Carina: Sharp
Right Lung Proximal Airways: Normal anatomic branching to segmental level.
No evidence of mass, lesions, bleeding or other endobronchial pathology.
Left Lung Proximal Airways: Normal anatomic branching to segmental level.
No evidence of mass, lesions, bleeding or other endobronchial pathology.
Mucosa: Normal.
Secretions: Copious thick and thin light-yellow mucus/secretions throughout.
Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius , Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus.
Bronchial alveolar lavage was performed at Lateral Segment of RML (RB4) and Medial Segment of RML (RB5).
Instilled 40 cc of NS, suction returned with 25 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
===========================================
 
NECK ULTRASOUND OF PROPOSED TRACHEOSTOMY INSERTION SITE
 
 
The bronchoscope was retracted into the ETT tube and the ET tube retracted into the subglottic space under direct visualization.
The inferior border of the cricoid along with the proximal tracheal rings were visualized.
Next, the anterior neck was prepped and draped in the usual sterile fashion.
Lidocaine 1% 3ml ml was injected into the anterior neck.
A 1 cm incision was made horizontallywith a #10 blade down through the subcutaneous tissue, just inferior to the cricoid cartilage.
The introducer needle and passed between the 1st and 2nd tracheal rings and into the trachea under direct visualization.
Next, a J-wire was passed through the catheter, also visualized with the bronchoscope.
The site was then dilated using the 14Fr introducing dilator passed over the wire.
The 14 Fr dilator was then removed from the guide wire and an 8 Fr guiding catheter placed over the guide wire until the safety ridge on the guiding catheter was at skin level.
The tissue dilator was placed over the guiding catheter until the positioning mark was visualized via the bronchoscope.
The tissue dilator was then removed leaving the guiding catheter and guide wire assembly in place, all under direct visualization bronchoscopically.
Finally a Portex 7.0mm cuffed tracheostomy tube with appropriate dilator was introduced over the guiding catheter into the trachea under direct visualization.
The dilator, guiding catheter, and J-wire were then removed and the tracheostomy tube left in place.
This was confirmed to be in good position bronchoscopically.  The Endotracheal tube was then removed and the ventilator connected to the tracheostomy tube.
Surgicel was placed preemptively around the tracheostomy site to reduce bleeding.
A Lyofoam drain sponge was placed under the tracheostomy tube prior to suturing into place.
The patient tolerated the procedure well.  There were no complications. The staff physician was present throughout the entire procedure.
===========================================
 
Under sterile prep and draping, the abdomen was evaluated and 2 cm below the costal margin on the left, the likely point of insertion was identified.
Ultrasound was used and hepatic tissue was identified just under the standard/traditional PEG insertion site.
TRADITIONAL INSERTION SITE
 
 
As such, a new more lateral insertion site was chosen and no hepatic tissue was identified on ultrasound.
PROPOSED INSERTION SITE
 
 
The scope was introduced through the mouth without difficulty and with continuous insufflation, the stomach was reached within 10 seconds.
Then, the point of digital pressure was identified in the stomach and transillumination was accomplished successfully and without any doubts.
At this point, a 1cm incision was carried out in the skin and a 14ga angiocath was introduced.
Using modified Seldinger technique, the angiocath was advanced and a wire was introduced.
Using pull through technique, the guide wire was pulled through the mouth and linked to the 20Fr PEG catheter in usual fashion.
Thereafter, the wire was pulled through the abdominal wall and the PEG tube positioned correctly with the bumper at 1.5 cm.
The remaining air was suctioned out and complete apposition of the stomach and esophagus was seen. There were no complications.
The total procedural time was 20 minutes.
 
INSTRUCTIONS:
PEG can be used for medications 6 hrs post procedure (@2200)
PEG (or NG tube) can be used for feeds 6 hrs post procedure (@2200).
No enteral feeding prior.
OK to restart systemic anticoagulation @2200, if needed.
 
The patient tolerated the procedure well.
There were no immediate complications.  At the conclusion of the operation, the patient was in stable condition.
SPECIMEN(S): 
--RML BAL (cell count, cyto, micro)
 
IMPRESSION/PLAN: [REDACTED]is a 68 year old-year-old female who presents for tracheostomy and PEG tube placement.
--Post-procedure CXR
--Anticipate suture removal in 7 days (~12/29/2025)
--Anticipate trach change in 10 days (~1/1/2026)
--PEG can be used for medications and tube feeds at 2200 on 12/22/2025
--If required to place gauze underneath the skin bumper, please use only 1 thin layer and change as needed, as this can lead to tension on the gastric cuff and result in complication.
--Please call the Interventional pulmonary fellow on call should there be any issues with the PEG."""

# Target Entities to Find (Order matters for sequential search to avoid overlap issues if any,
# though we will use exact text matching from the provided list).
# Format: (Label, Text Fragment)
TARGET_ENTITIES = [
    # Header/Diagnosis
    ("OBS_FINDING", "respiratory failure"), # Lowercase to match text if needed, but text has mixed.
    ("OBS_FINDING", "Respiratory Failure"),
    # Procedure List
    ("PROC_ACTION", "Therapeutic aspiration"),
    ("PROC_METHOD", "bronchoscope"),
    ("PROC_ACTION", "lavage"),
    ("PROC_ACTION", "Incision"),
    ("PROC_ACTION", "Esophagogastroduodenoscopy"),
    ("DEV_CATHETER", "percutaneous gastrostomy tube"),
    ("PROC_METHOD", "Ultrasound"),
    # Meds
    ("MEDICATION", "Versed"),
    ("MEDICATION", "Fentanyl"),
    ("MEDICATION", "Etomidate"),
    ("MEDICATION", "Rocuronium"),
    ("CTX_TIME", "107 minutes"),
    # Instruments/Anatomy
    ("DEV_INSTRUMENT", "Flexible Therapeutic Bronchoscope"),
    ("OUTCOME_COMPLICATION", "None"),
    ("ANAT_AIRWAY", "Trachea"),
    ("ANAT_AIRWAY", "Main Carina"),
    ("ANAT_AIRWAY", "Right Lung Proximal Airways"),
    ("ANAT_AIRWAY", "Left Lung Proximal Airways"),
    ("OBS_FINDING", "mucus"),
    ("OBS_FINDING", "secretions"),
    ("PROC_ACTION", "therapeutic aspiration"),
    ("ANAT_AIRWAY", "Right Mainstem"),
    ("ANAT_AIRWAY", "Bronchus Intermedius"),
    ("ANAT_AIRWAY", "Left Mainstem"),
    ("ANAT_AIRWAY", "Carina"),
    ("ANAT_AIRWAY", "RUL Carina"),
    ("ANAT_AIRWAY", "RC1"),
    ("ANAT_AIRWAY", "RML Carina"),
    ("ANAT_AIRWAY", "RC2"),
    ("ANAT_AIRWAY", "LUL Lingula Carina"),
    ("ANAT_AIRWAY", "Lc1"),
    ("ANAT_AIRWAY", "Left Carina"),
    ("ANAT_AIRWAY", "LC2"),
    ("PROC_ACTION", "Bronchial alveolar lavage"),
    ("ANAT_LUNG_LOC", "Lateral Segment of RML"),
    ("ANAT_LUNG_LOC", "RB4"),
    ("ANAT_LUNG_LOC", "Medial Segment of RML"),
    ("ANAT_LUNG_LOC", "RB5"),
    ("MEAS_VOL", "40 cc"),
    ("MEAS_VOL", "25 cc"),
    # Trach Details
    ("ANAT_AIRWAY", "subglottic space"),
    ("ANAT_AIRWAY", "cricoid"),
    ("ANAT_AIRWAY", "proximal tracheal rings"),
    ("MEDICATION", "Lidocaine"),
    ("MEAS_VOL", "3ml"),
    ("MEAS_SIZE", "1 cm"),
    ("DEV_INSTRUMENT", "#10 blade"),
    ("DEV_NEEDLE", "introducer needle"),
    ("ANAT_AIRWAY", "tracheal rings"),
    ("DEV_INSTRUMENT", "J-wire"),
    ("DEV_CATHETER_SIZE", "14Fr"),
    ("DEV_INSTRUMENT", "introducing dilator"),
    ("DEV_CATHETER_SIZE", "8 Fr"),
    ("DEV_CATHETER", "guiding catheter"),
    ("DEV_INSTRUMENT", "tissue dilator"),
    ("DEV_CATHETER", "Portex 7.0mm cuffed tracheostomy tube"),
    ("DEV_INSTRUMENT", "dilator"),
    ("DEV_CATHETER", "tracheostomy tube"),
    ("DEV_CATHETER", "Lyofoam drain sponge"),
    # PEG Details
    ("MEAS_SIZE", "2 cm"),
    ("PROC_METHOD", "transillumination"),
    ("DEV_NEEDLE", "14ga"),
    ("DEV_CATHETER", "angiocath"),
    ("PROC_METHOD", "Seldinger technique"),
    ("DEV_CATHETER_SIZE", "20Fr"),
    ("DEV_CATHETER", "PEG catheter"),
    ("DEV_CATHETER", "PEG tube"),
    ("MEAS_SIZE", "1.5 cm"),
    ("CTX_TIME", "20 minutes"),
    ("OUTCOME_COMPLICATION", "no immediate complications")
]

# =============================================================================
# LOGIC
# =============================================================================

def extract_entities(text, entity_list):
    """
    Finds strict text matches in the raw text and returns a list of dictionaries.
    Handles multiple occurrences by scanning the text.
    """
    spans = []
    # Sort by length descending to capture "Respiratory Failure" before "Failure" if ambiguous
    # though strict exact match avoids most issues.
    sorted_entities = sorted(entity_list, key=lambda x: len(x[1]), reverse=True)
    
    # We use a set to track (start, end) to avoid overlapping exact duplicates if any
    # (though in this specific data, overlaps shouldn't occur with the chosen list).
    occupied_indices = set()
    
    entities_found = []

    # Simple approach: find all occurrences of each string
    for label, substr in sorted_entities:
        # Using regex to find all start indices
        # Escape special chars in substr
        pattern = re.escape(substr)
        for match in re.finditer(pattern, text):
            start = match.start()
            end = match.end()
            
            # check overlap
            is_overlap = any(i in occupied_indices for i in range(start, end))
            if not is_overlap:
                entities_found.append({
                    "span_id": f"{label}_{start}",
                    "note_id": NOTE_ID,
                    "label": label,
                    "text": substr,
                    "start": start,
                    "end": end
                })
                # mark indices
                for i in range(start, end):
                    occupied_indices.add(i)
    
    # Sort by start position
    entities_found.sort(key=lambda x: x["start"])
    return entities_found

def main():
    # 1. Extract Entities
    entities = extract_entities(RAW_TEXT, TARGET_ENTITIES)
    
    # 2. Prepare JSONL Data
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # 3. File Operations
    
    # A. Update ner_dataset_all.jsonl
    ner_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    with open(ner_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # B. Update notes.jsonl
    notes_file = OUTPUT_DIR / "notes.jsonl"
    with open(notes_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # C. Update spans.jsonl
    spans_file = OUTPUT_DIR / "spans.jsonl"
    with open(spans_file, "a", encoding="utf-8") as f:
        for ent in entities:
            f.write(json.dumps(ent) + "\n")
            
    # D. Update stats.json
    # Try to load existing, else initialize
    if os.path.exists("stats.json"):
        with open("stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        # Fallback structure if file not found
        stats = {
            "total_files": 0, "successful_files": 0, "total_notes": 0,
            "total_spans_raw": 0, "total_spans_valid": 0,
            "alignment_warnings": 0, "alignment_errors": 0,
            "label_counts": {}
        }
        
    stats["total_files"] += 1
    stats["successful_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities)
    stats["total_spans_valid"] += len(entities)
    
    for ent in entities:
        lbl = ent["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    # E. Validation Log
    log_file = OUTPUT_DIR / "alignment_warnings.log"
    with open(log_file, "a", encoding="utf-8") as f:
        for ent in entities:
            extracted = RAW_TEXT[ent["start"]:ent["end"]]
            if extracted != ent["text"]:
                f.write(f"MISMATCH: {ent['span_id']} expected '{ent['text']}' got '{extracted}'\n")

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    main()