import json
import os
import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
NOTE_ID = "note_063"
SCRIPT_VERSION = "1.0"

# Raw content from note_063.txt
# (Preserving exact whitespace/newlines is critical for offset alignment)
RAW_TEXT = """NOTE_ID:  note_063 SOURCE_FILE: note_063.txt INDICATION FOR OPERATION:  [REDACTED]is a 68 year old-year-old male who presents with airway stenosis.
PREOPERATIVE DIAGNOSIS: J98.09 Other diseases of bronchus, not elsewhere classified
POSTOPERATIVE DIAGNOSIS:  J98.09 Other diseases of bronchus, not elsewhere classified
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)    
31625 Endobronchial Biopsy(s)
31630 Balloon dilation
31636 Dilate and bronchial stent initial bronchus
31640 Bronchoscopy with excision 
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
31635 Foreign body removal
 
22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required) and 50 Bilateral Procedures (Procedure done on both 
sides of the body)
 
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure (22 Modifier):
This patient required multiple forms of bronchoscopy (flexible and rigid).
The patient required both mechanical excision and APC ablation of granulation tissue.
Patient required stent placement and dilation in the left mainstem bronchus, but also required multiple balloon dilations at other discrete locations (left upper lobe, and left lower lobe) and on the opposite side (right mainstem bronchus).
This resulted in >100% increased work due to Increased intensity, Time, Technical difficulty of procedure, and Physical and mental effort required.
Apply to: 
31630 Balloon dilation
31636 Dilate and bronchial stent initial bronchus
31640 Bronchoscopy with excision .
Unusual Procedure (50 Modifier):
31630 Balloon dilation
 
 
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Rigid Bronchoscope
Flexible Therapeutic Bronchoscope
 
ESTIMATED BLOOD LOSS:   Minimum
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Initial Airway Inspection Findings:
 
The laryngeal mask airway is in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.
Larynx: Normal.
Vocal Cords: Normal without mass/lesions
Trachea: Normal.
Main Carina: Somewhat splayed
Right Lung Proximal Airways: Stenosis noted about the anastamosis site/suture line. Normal anatomic branching to segmental level.
No evidence of mass, lesions, bleeding or other endobronchial pathology.
Left Lung Proximal Airways: Proximal stenosis noted at the LMSB.
Metallic stent in the LMSB had migrated distally somewhat, leaving a stenotic and highly malacic ~1cm section of the LMSB proximal to the stent.
Lobar airways and distal had normal anatomic branching to segmental level.
No evidence of mass, lesions, bleeding or other endobronchial pathology.
Mucosa: Granulation tissue at main carina, LMSB, and RMSB.
Otherwise normal.
Secretions: Thick tenacious mucus within the LMSB stent. Othwerwise, moderate, thin, and clear throughout.
LMSB STENOSIS:  Overlying granulation tissue and proximal end of LMSB also highly malacic.
RMSB STENOSIS
 
 
VIEW THROUGH STENT AT OUTSET OF PROCEDURE
 
 
Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius , Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus.
Endobronchial biopsy was performed at the left mainstem bronchus.  Lesion was successfully removed.  Samples sent for Pathology.
Granulation tissue causing stenosis at the proximal LMSB was treated with the following modalities:
Modality	Tools	Setting/Mode	Duration	Results
Mechanical	Pulmonary forceps	N/A	N/A	Good granulation tissue destruction/removal
APC	Straightfire probe	Forced coag, Effect 2	1-2 second applications	Good granulation tissue destruction and hemostasis
 
Bronchial alveolar lavage was performed at Anteromedial Segment of LLL (Lb7/8).
Instilled 60 cc of NS, suction returned with 20 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
After induction of muscle relaxants, tooth or gum protector was placed.
The black ventilating bronchoscope rigid barrel was introduced through the mouth and advanced in the midline while keeping the alignment with the axis of the trachea and minimizing pressure to the teeth.
The vocal cords were identified and the rigid bronchoscope was advanced carefully while minimizing contact with them.
Once the rigid bronchoscope was positioned at the distal-trachea, jet ventilation was initiated and chest wall movement was confirmed.
Foreign body removal was performed:  The patient's existing MicroTech 10mm x 40mm stent was grasped with the pulmonary forcpes and removed en bloc with the flexible bronchoscope through the rigid barrel.
Balloon dilation was performed at Left Mainstem.  10/11/12 Elation balloon was used to perform dilation to 12 mm at the Left Mainstem.
Total 1 inflations with dilation time of 60 seconds each.
The following stent (Bonastent, 10mm x 50mm) was placed in the Left Mainstem bronchus.
Balloon dilation was performed at Left Mainstem through the stent to expand and appropriately seat the stent.
10/11/12 Elation balloon was used to perform dilation to 12 mm at the Left Mainstem.
Total 4 inflations with dilation time of 30 seconds each.
 
Balloon dilation was performed at the left lower lobe take-off.
10/11/12 Elation balloon was used to perform dilation to 12 mm at the left lower lobe take-off.
Total 1 inflations with dilation time of 30 seconds each.
Balloon dilation was performed at the left upper lobe take-off.
10/11/12 Elation balloon was used to perform dilation to 10 mm at the left upper lobe take-off.
Total 1 inflations with dilation time of 30 seconds each.
 
Balloon dilation was performed at Right Mainstem.
8/9/10 Elation balloon was used to perform dilation to 10 mm at the Right Mainstem.
Total 1 inflations with dilation time of 60 seconds each.
VIEW OF STENT AT THE END OF THE CASE
 
 
 
 
 
The rigid bronchoscope was extubated and an LMA replaced by the anesthesia team.
Lidocaine was applied to the vocal cords.
 
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
--LLL BAL (cell count, micro, cyto)
--LMSB endobronchial forceps biopsies (path)
--Left mainstem stent (path)
 
IMPRESSION/PLAN: [REDACTED]is a 68 year old-year-old male who presents for bronchoscopy for evaluation of airway stenosis.
Patient was noted to have distal migration of his existing stent with proximal LMSB stenosis.
The patient's stent was removed, balloon dilation was performed, and a Bonastent 10mm x 50mm stent was re-placed in the LMSB.
The right mainstem bronchus was also dilated. Patient tolerated the procedure well and there were no immediate complications.
--Follow-up BAL and path results
--Continue stent hydration therapy regimen
--Repeat bronchoscopy in approximately 4 weeks for re-evaluation"""

# Ordered list of entities to extract. 
# Order matters: text search resumes after the previous find to handle duplicates.
ENTITIES_TO_EXTRACT = [
    {"label": "OBS_LESION", "text": "airway stenosis"},
    {"label": "PROC_ACTION", "text": "Therapeutic aspiration"},
    {"label": "PROC_ACTION", "text": "lavage (BAL)"},
    {"label": "PROC_ACTION", "text": "Endobronchial Biopsy(s)"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "DEV_STENT", "text": "bronchial stent"},
    {"label": "PROC_ACTION", "text": "Bronchoscopy with excision"},
    {"label": "PROC_ACTION", "text": "Destruction"},
    {"label": "OBS_LESION", "text": "stenosis"},
    {"label": "PROC_ACTION", "text": "excision"},
    {"label": "PROC_ACTION", "text": "Foreign body removal"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"},
    {"label": "PROC_ACTION", "text": "mechanical excision"},
    {"label": "PROC_ACTION", "text": "APC ablation"},
    {"label": "OBS_LESION", "text": "granulation tissue"},
    {"label": "PROC_ACTION", "text": "stent placement"},
    {"label": "PROC_ACTION", "text": "dilation"},
    {"label": "ANAT_AIRWAY", "text": "left mainstem bronchus"},
    {"label": "PROC_ACTION", "text": "balloon dilations"},
    {"label": "ANAT_LUNG_LOC", "text": "left upper lobe"},
    {"label": "ANAT_LUNG_LOC", "text": "left lower lobe"},
    {"label": "ANAT_AIRWAY", "text": "right mainstem bronchus"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "DEV_STENT", "text": "bronchial stent"},
    {"label": "PROC_ACTION", "text": "Bronchoscopy with excision"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "DEV_INSTRUMENT", "text": "Rigid Bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "Flexible Therapeutic Bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "laryngeal mask airway"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"},
    {"label": "ANAT_AIRWAY", "text": "Trachea"},
    {"label": "ANAT_AIRWAY", "text": "Main Carina"},
    {"label": "ANAT_AIRWAY", "text": "Right Lung Proximal Airways"},
    {"label": "OBS_LESION", "text": "Stenosis"},
    {"label": "ANAT_AIRWAY", "text": "Left Lung Proximal Airways"},
    {"label": "OBS_LESION", "text": "stenosis"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "DEV_STENT_MATERIAL", "text": "Metallic"}, # Maps to stent.type/material
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "OBS_LESION", "text": "stenotic"},
    {"label": "OBS_LESION", "text": "malacic"},
    {"label": "MEAS_SIZE", "text": "~1cm"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "OBS_LESION", "text": "Granulation tissue"},
    {"label": "ANAT_AIRWAY", "text": "main carina"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "ANAT_AIRWAY", "text": "RMSB"},
    {"label": "OBS_FINDING", "text": "Thick tenacious mucus"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "OBS_LESION", "text": "STENOSIS"},
    {"label": "OBS_LESION", "text": "Granulation tissue"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "OBS_LESION", "text": "malacic"},
    {"label": "ANAT_AIRWAY", "text": "RMSB"},
    {"label": "OBS_LESION", "text": "STENOSIS"},
    {"label": "PROC_ACTION", "text": "therapeutic aspiration"},
    {"label": "ANAT_AIRWAY", "text": "Trachea"},
    {"label": "ANAT_AIRWAY", "text": "Right Mainstem"},
    {"label": "ANAT_AIRWAY", "text": "Bronchus Intermedius"},
    {"label": "ANAT_AIRWAY", "text": "Left Mainstem"},
    {"label": "ANAT_AIRWAY", "text": "Carina"},
    {"label": "ANAT_AIRWAY", "text": "RUL Carina"},
    {"label": "ANAT_AIRWAY", "text": "RML Carina"},
    {"label": "ANAT_AIRWAY", "text": "LUL Lingula Carina"},
    {"label": "ANAT_AIRWAY", "text": "Left Carina"},
    {"label": "OBS_FINDING", "text": "mucus"},
    {"label": "PROC_ACTION", "text": "Endobronchial biopsy"},
    {"label": "ANAT_AIRWAY", "text": "left mainstem bronchus"},
    {"label": "OBS_LESION", "text": "Lesion"},
    {"label": "OBS_LESION", "text": "Granulation tissue"},
    {"label": "OBS_LESION", "text": "stenosis"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "DEV_INSTRUMENT", "text": "Pulmonary forceps"},
    {"label": "OBS_LESION", "text": "granulation tissue"},
    {"label": "PROC_METHOD", "text": "APC"},
    {"label": "DEV_INSTRUMENT", "text": "Straightfire probe"},
    {"label": "MEAS_TIME", "text": "1-2 second"},
    {"label": "OBS_LESION", "text": "granulation tissue"},
    {"label": "PROC_ACTION", "text": "Bronchial alveolar lavage"},
    {"label": "ANAT_LUNG_LOC", "text": "Anteromedial Segment of LLL"},
    {"label": "ANAT_LUNG_LOC", "text": "Lb7/8"},
    {"label": "MEAS_VOL", "text": "60 cc"},
    {"label": "MEAS_VOL", "text": "20 cc"},
    {"label": "MEDICATION", "text": "muscle relaxants"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"}, # "black ventilating bronchoscope rigid barrel" is clearer, but "rigid bronchoscope" in next sentence
    {"label": "ANAT_AIRWAY", "text": "trachea"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "distal-trachea"},
    {"label": "PROC_ACTION", "text": "Foreign body removal"},
    {"label": "DEV_STENT_MATERIAL", "text": "MicroTech"},
    {"label": "DEV_STENT_SIZE", "text": "10mm x 40mm"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "DEV_INSTRUMENT", "text": "pulmonary forcpes"},
    {"label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "ANAT_AIRWAY", "text": "Left Mainstem"},
    {"label": "DEV_INSTRUMENT", "text": "Elation balloon"},
    {"label": "PROC_ACTION", "text": "dilation"},
    {"label": "MEAS_AIRWAY_DIAM", "text": "12 mm"},
    {"label": "ANAT_AIRWAY", "text": "Left Mainstem"},
    {"label": "MEAS_TIME", "text": "60 seconds"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "DEV_STENT_MATERIAL", "text": "Bonastent"},
    {"label": "DEV_STENT_SIZE", "text": "10mm x 50mm"},
    {"label": "PROC_ACTION", "text": "placed"},
    {"label": "ANAT_AIRWAY", "text": "Left Mainstem bronchus"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "ANAT_AIRWAY", "text": "Left Mainstem"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "DEV_INSTRUMENT", "text": "Elation balloon"},
    {"label": "PROC_ACTION", "text": "dilation"},
    {"label": "MEAS_AIRWAY_DIAM", "text": "12 mm"},
    {"label": "ANAT_AIRWAY", "text": "Left Mainstem"},
    {"label": "MEAS_TIME", "text": "30 seconds"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "ANAT_LUNG_LOC", "text": "left lower lobe"},
    {"label": "DEV_INSTRUMENT", "text": "Elation balloon"},
    {"label": "PROC_ACTION", "text": "dilation"},
    {"label": "MEAS_AIRWAY_DIAM", "text": "12 mm"},
    {"label": "ANAT_LUNG_LOC", "text": "left lower lobe"},
    {"label": "MEAS_TIME", "text": "30 seconds"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "ANAT_LUNG_LOC", "text": "left upper lobe"},
    {"label": "DEV_INSTRUMENT", "text": "Elation balloon"},
    {"label": "PROC_ACTION", "text": "dilation"},
    {"label": "MEAS_AIRWAY_DIAM", "text": "10 mm"},
    {"label": "ANAT_LUNG_LOC", "text": "left upper lobe"},
    {"label": "MEAS_TIME", "text": "30 seconds"},
    {"label": "PROC_ACTION", "text": "Balloon dilation"},
    {"label": "ANAT_AIRWAY", "text": "Right Mainstem"},
    {"label": "DEV_INSTRUMENT", "text": "Elation balloon"},
    {"label": "PROC_ACTION", "text": "dilation"},
    {"label": "MEAS_AIRWAY_DIAM", "text": "10 mm"},
    {"label": "ANAT_AIRWAY", "text": "Right Mainstem"},
    {"label": "MEAS_TIME", "text": "60 seconds"},
    {"label": "DEV_STENT", "text": "STENT"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "LMA"},
    {"label": "MEDICATION", "text": "Lidocaine"},
    {"label": "OUTCOME_COMPLICATION", "text": "no immediate complications"},
    {"label": "ANAT_LUNG_LOC", "text": "LLL"},
    {"label": "PROC_ACTION", "text": "BAL"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "PROC_ACTION", "text": "biopsies"},
    {"label": "ANAT_AIRWAY", "text": "Left mainstem"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"},
    {"label": "OBS_LESION", "text": "airway stenosis"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "OBS_LESION", "text": "stenosis"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "PROC_ACTION", "text": "removed"},
    {"label": "PROC_ACTION", "text": "balloon dilation"},
    {"label": "DEV_STENT_MATERIAL", "text": "Bonastent"},
    {"label": "DEV_STENT_SIZE", "text": "10mm x 50mm"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "ANAT_AIRWAY", "text": "LMSB"},
    {"label": "ANAT_AIRWAY", "text": "right mainstem bronchus"},
    {"label": "PROC_ACTION", "text": "dilated"},
    {"label": "OUTCOME_COMPLICATION", "text": "no immediate complications"},
    {"label": "PROC_ACTION", "text": "BAL"},
    {"label": "DEV_STENT", "text": "stent"},
    {"label": "PROC_ACTION", "text": "bronchoscopy"}
]

def generate_paths():
    """Sets up the output directory structure."""
    # Script location: data/granular annotations/Python_update_scripts/
    # Target location: data/ml_training/granular_ner/
    output_dir = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def process_note(output_dir):
    """Processes the note, extracts entities, and updates JSON/JSONL files."""
    
    # 1. Calculate Offsets
    entities_with_offsets = []
    current_search_index = 0
    
    for entity in ENTITIES_TO_EXTRACT:
        start = RAW_TEXT.find(entity["text"], current_search_index)
        
        if start == -1:
            # Fallback: search from beginning if we messed up strict ordering, 
            # though this risks mapping to the wrong instance.
            # In strict pipeline, we might want to log this as error.
            start = RAW_TEXT.find(entity["text"])
            
        if start != -1:
            end = start + len(entity["text"])
            
            # Validation
            extracted = RAW_TEXT[start:end]
            if extracted != entity["text"]:
                print(f"CRITICAL ERROR: Mismatch {entity['text']} vs {extracted}")
                continue
            
            entities_with_offsets.append({
                "start": start,
                "end": end,
                "label": entity["label"],
                "text": entity["text"]
            })
            
            # Update search cursor to end of this entity
            current_search_index = end
        else:
            with open(output_dir / "alignment_warnings.log", "a") as f:
                f.write(f"[{datetime.datetime.now()}] Could not find entity: '{entity['text']}' in NOTE_ID: {NOTE_ID}\n")

    # 2. Prepare JSON Lines
    
    # ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "id": i,
                "label": e["label"],
                "start_offset": e["start"],
                "end_offset": e["end"]
            }
            for i, e in enumerate(entities_with_offsets)
        ]
    }
    
    # notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # spans.jsonl
    span_entries = []
    for e in entities_with_offsets:
        span_id = f"{e['label']}_{e['start']}"
        span_entries.append({
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        })

    # 3. Write Files
    
    # Append to ner_dataset_all.jsonl
    with open(output_dir / "ner_dataset_all.jsonl", "a") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Append to notes.jsonl
    with open(output_dir / "notes.jsonl", "a") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Append to spans.jsonl
    with open(output_dir / "spans.jsonl", "a") as f:
        for span in span_entries:
            f.write(json.dumps(span) + "\n")
            
    # 4. Update Stats
    stats_path = output_dir / "stats.json"
    
    if stats_path.exists():
        with open(stats_path, "r") as f:
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
    # Assuming one note per file in this context, or file count increments generally
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(entities_with_offsets)
    stats["total_spans_valid"] += len(entities_with_offsets)
    
    for e in entities_with_offsets:
        lbl = e["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities_with_offsets)} entities.")

if __name__ == "__main__":
    out_dir = generate_paths()
    process_note(out_dir)