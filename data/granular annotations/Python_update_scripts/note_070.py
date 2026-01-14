import json
import os
import datetime
from pathlib import Path

# ==========================================
# 1. Configuration & Path Setup
# ==========================================
NOTE_ID = "note_070"

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
# 2. Raw Text Data
# ==========================================
RAW_TEXT = """NOTE_ID:  note_070 SOURCE_FILE: note_070.txt INDICATION FOR OPERATION:  [REDACTED] is a 51 year old-year-old female who presents with lung nodule.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
PREOPERATIVE DIAGNOSIS: R91.1 Solitary Lung Nodule
 
POSTOPERATIVE DIAGNOSIS:  R91.1 Solitary Lung Nodule
 
PROCEDURE:  
31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS)
31645 Therapeutic aspiration initial episode
31623 Dx bronchoscope/brushing    
31624 Dx bronchoscope/lavage (BAL)    
31628 TBBX single lobe     
31629 TBNA single lobe   
31626 Fiducial marker placements, single or multiple     
31627 Navigational Bronchoscopy (computer assisted)
77012 Radiology / radiologic guidance for CT guided needle placement (CIOS)
76377 3D rendering with interpretation and reporting of CT, US, Tomo modality (ION Planning Station)
31652 EBUS sampling 1 or 
2 nodes
31654 Radial EBUS for peripheral lesion
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets 
76983 Ultrasound Elastography, Additional Target 2
31630 Balloon dilation
 
22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)
 
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure:
This patient required a Transbronchial Cryo biopsies.
This resulted in >40% increased work due to Technical difficulty of procedure and Physical and mental effort required.
Apply to: 31628 TBBX single lobe. 
 
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Linear EBUS 
Radial EBUS
Ion Robotic Bronchoscope
Disposable Bronchoscope
 
ESTIMATED BLOOD LOSS:   None
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: . 
 
Initial Airway Inspection Findings:
 
CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target.
The navigational plan was reviewed and verified.  This was then loaded into robotic bronchoscopy platform.
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius , and Left Mainstem from mucus.
Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
vcv\t14\t400\t12\t100\t10\t15
 
Robotic navigation bronchoscopy was performed with Ion platform.  Partial registration was used.
Ion robotic catheter was used to engage the Anterior Segment of RUL (RB3).
Target lesion is about 1 cm in diameter.   
 
Significant difficulties were encountered during the navigation due to a small carina.
5mmx20mm mustang balloon was used to dilate the distal airway under direct fluoro-guidance with Omnipaque 240 as inflation agent.
After dilation, the robotic bronchoscope was easily navigated to the distal nodule under navigational guidance the ion robotic catheter was advanced to 1.0 cm away from the planned target.
Radial EBUS was performed to confirm that the location of the nodule is Eccentric.
The following features were noted: Continuous margin .
 
Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
Cios Spin system was used for evaluation of nodule location.  Low dose spin was performed to acquire CT imaging.
This was passed on to Ion platform system for reconstruction and nodule location.
The 3D images was interpreted on an independent workstation (Ion).
Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location.
I personally interpreted the cone beam CT and 3-D reconstruction.
Transbronchial needle aspiration was performed with 21G Needle through the extended working channel catheter.  Total 6 samples were collected.
Samples sent for Cytology.
 
Transbronchial biopsy was performed with alligator forceps the extended working channel catheter.
Total 2 samples were collected.  Samples sent for Pathology.
 
Transbronchial cryobiopsy was performed with 1.1mm cryoprobe via the extended working channel catheter.
Freeze time of 6 seconds were used.  Total 6 samples were collected.  Samples sent for Pathology.
Transbronchial brushing was performed with Protected cytology brush the extended working channel catheter.  Total 1 samples were collected.
Samples sent for Microbiology (Cultures/Viral/Fungal).
 
Bronchial alveolar lavage was performed the extended working channel catheter.
Instilled 40 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.
Prior to withdraw of the bronchoscope. 
 
ROSE from ION procedure was noted to be:
Conclusive evidence of malignant neoplasm
 
Prior to withdrawal of the bronchoscope, inspection demonstrated no evidence of bleeding.
EBUS-Findings
Indications: Diagnostic and Staging
Technique:
All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle.
Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
4L (lower paratracheal) node
7 (subcarinal) node
11Rs lymph node
11L lymph node
 
No immediate complications
 
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
Elastography provided a semi-quantitative classification (Type 1–3), which was used to guide biopsy site selection and sampling strategy.
Lymph Nodes Evaluated:
Site 1: The 11L lymph node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed. The site was not sampled: Sampling this lymph node was not clinically indicated.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
Site 2: The 7 (subcarinal) node was => 10 mm on CT and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed. The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
Site 3: The 4R (lower paratracheal) node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed. The site was not sampled: Sampling this lymph node was not clinically indicated.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
Site 4: The 11Rs lymph node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed. The site was not sampled: Sampling this lymph node was not clinically indicated.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
TBCBX, TBBX, TBNA, Brush, BAL RUL lung nodule
TBNA station 7 
 
IMPRESSION/PLAN: [REDACTED] is a 51 year old-year-old female who presents for bronchoscopy for lung nodule.
- f/u results in clinic
- f/u cxr"""

# ==========================================
# 3. Entity Extraction Config
# ==========================================
# Define entities to extract (text_substring, label)
# Order matters: first occurrence found will be consumed, but logic handles repeats.
entities_to_extract = [
    # Diagnosis/Lesions
    ("lung nodule", "OBS_LESION"),
    ("Solitary Lung Nodule", "OBS_LESION"),
    ("Solitary Lung Nodule", "OBS_LESION"), # Second instance
    ("Target lesion", "OBS_LESION"),
    ("distal nodule", "OBS_LESION"),
    ("malignant neoplasm", "OBS_ROSE"),
    
    # Anatomy - Airway
    ("Right Mainstem", "ANAT_AIRWAY"),
    ("Bronchus Intermedius", "ANAT_AIRWAY"),
    ("Left Mainstem", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    
    # Anatomy - Lung/Loc
    ("Anterior Segment of RUL (RB3)", "ANAT_LUNG_LOC"),
    ("RUL", "ANAT_LUNG_LOC"), # In specimen
    
    # Anatomy - Lymph Nodes (Stations)
    ("4R", "ANAT_LN_STATION"),
    ("lower paratracheal", "ANAT_LN_STATION"),
    ("4L", "ANAT_LN_STATION"),
    ("lower paratracheal", "ANAT_LN_STATION"), # Second instance
    ("7", "ANAT_LN_STATION"),
    ("subcarinal", "ANAT_LN_STATION"),
    ("11Rs", "ANAT_LN_STATION"),
    ("11L", "ANAT_LN_STATION"),
    # Repeated in detail section
    ("11L", "ANAT_LN_STATION"),
    ("7", "ANAT_LN_STATION"),
    ("subcarinal", "ANAT_LN_STATION"),
    ("4R", "ANAT_LN_STATION"),
    ("lower paratracheal", "ANAT_LN_STATION"),
    ("11Rs", "ANAT_LN_STATION"),
    ("station 7", "ANAT_LN_STATION"),
    
    # Procedures / Methods
    ("Bronchoscopy", "PROC_ACTION"),
    ("Therapeutic aspiration", "PROC_ACTION"),
    ("Fiducial marker placements", "PROC_ACTION"),
    ("Navigational Bronchoscopy", "PROC_METHOD"),
    ("CT guided", "PROC_METHOD"),
    ("EBUS sampling", "PROC_ACTION"),
    ("Radial EBUS", "PROC_METHOD"),
    ("Radial EBUS", "PROC_METHOD"), # Second mention
    ("Balloon dilation", "PROC_ACTION"),
    ("Transbronchial Cryo biopsies", "PROC_ACTION"),
    ("Robotic navigation bronchoscopy", "PROC_METHOD"),
    ("Ion platform", "PROC_METHOD"),
    ("therapeutic aspiration", "PROC_ACTION"),
    ("Cone Beam CT", "PROC_METHOD"),
    ("Cios Spin system", "PROC_METHOD"),
    ("Transbronchial needle aspiration", "PROC_ACTION"),
    ("Transbronchial biopsy", "PROC_ACTION"),
    ("Transbronchial cryobiopsy", "PROC_ACTION"),
    ("Transbronchial brushing", "PROC_ACTION"),
    ("Bronchial alveolar lavage", "PROC_ACTION"),
    ("sampling by transbronchial needle aspiration", "PROC_ACTION"),
    ("endobronchial ultrasound guided transbronchial biopsies", "PROC_ACTION"),
    ("TBNA", "PROC_ACTION"),
    
    # Devices / Instruments
    ("Linear EBUS", "DEV_INSTRUMENT"),
    ("Radial EBUS", "DEV_INSTRUMENT"),
    ("Ion Robotic Bronchoscope", "DEV_INSTRUMENT"),
    ("Disposable Bronchoscope", "DEV_INSTRUMENT"),
    ("mustang balloon", "DEV_INSTRUMENT"),
    ("robotic bronchoscope", "DEV_INSTRUMENT"),
    ("21G Needle", "DEV_NEEDLE"),
    ("alligator forceps", "DEV_INSTRUMENT"),
    ("cryoprobe", "DEV_INSTRUMENT"),
    ("Protected cytology brush", "DEV_INSTRUMENT"),
    ("Fiducial marker", "DEV_INSTRUMENT"),
    ("22-gauge Needle", "DEV_NEEDLE"),
    
    # Measurements
    ("1 cm", "MEAS_SIZE"),
    ("5mmx20mm", "MEAS_SIZE"),
    ("1.0 cm", "MEAS_SIZE"),
    ("1.1mm", "MEAS_SIZE"),
    ("6 seconds", "MEAS_TIME"),
    ("40 cc", "MEAS_VOL"),
    ("15 cc", "MEAS_VOL"),
    ("0.8mm x 3mm", "MEAS_SIZE"),
    ("5 mm", "MEAS_SIZE"),
    ("10 mm", "MEAS_SIZE"),
    ("10 mm", "MEAS_SIZE"),
    ("10 mm", "MEAS_SIZE"),
    ("10 mm", "MEAS_SIZE"),

    # Findings/Obs
    ("mucus", "OBS_FINDING"),
    ("Eccentric", "OBS_FINDING"),
    ("Continuous margin", "OBS_FINDING"),
    ("Type 1 elastographic pattern", "OBS_FINDING"),
    ("Type 2 elastographic pattern", "OBS_FINDING"),
    ("heterogeneous", "OBS_FINDING"),
    ("Type 1 elastographic pattern", "OBS_FINDING"), # Repeat
    ("Type 1 elastographic pattern", "OBS_FINDING"), # Repeat
    
    # Medications
    ("Omnipaque 240", "MEDICATION"),
    ("General Anesthesia", "MEDICATION"),
]

# ==========================================
# 4. Processing Logic
# ==========================================

def get_entities_with_offsets(text, entity_list):
    """
    Finds exact offsets for entities in text.
    Handles multiple occurrences by updating a cursor.
    """
    valid_entities = []
    # Sort entities by length (descending) to avoid partial matching issues if overlaps occur, 
    # though strict sequential finding usually works best for medical notes.
    # However, strict sequential finding requires exact order in list. 
    # Instead, we track used ranges to avoid overlap.
    
    # We will simply find ALL occurrences of each string, then dedup and sort by start index.
    # This captures the entities_to_extract list intent without needing perfect order in the list.
    
    found_spans = []
    
    for substr, label in entity_list:
        search_start = 0
        while True:
            start = text.find(substr, search_start)
            if start == -1:
                break
            end = start + len(substr)
            
            # Check for overlaps with already found spans
            is_overlap = False
            for exist_start, exist_end, _ in found_spans:
                if (start < exist_end and end > exist_start):
                    is_overlap = True
                    break
            
            if not is_overlap:
                found_spans.append((start, end, label))
                valid_entities.append({
                    "span_id": f"{label}_{start}",
                    "note_id": NOTE_ID,
                    "label": label,
                    "text": substr,
                    "start": start,
                    "end": end
                })
            
            search_start = end # Move past this occurrence
            
    # Sort by start offset
    valid_entities.sort(key=lambda x: x["start"])
    return valid_entities

def update_stats(new_entities):
    """
    Updates the global stats.json file.
    """
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
    stats["total_files"] += 1 # Assuming 1 note per file for this script
    stats["total_spans_raw"] += len(new_entities)
    stats["total_spans_valid"] += len(new_entities)
    
    for entity in new_entities:
        lbl = entity["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
        
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

def main():
    # 1. Extract Entities
    entities = get_entities_with_offsets(RAW_TEXT, entities_to_extract)
    
    # 2. Prepare Data Structures
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [[e["start"], e["end"], e["label"]] for e in entities]
    }
    
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    # 3. Write to Files
    
    # Append to ner_dataset_all.jsonl
    with open(NER_DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    # Append to notes.jsonl
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")
        
    # Append to spans.jsonl
    with open(SPANS_PATH, "a", encoding="utf-8") as f:
        for entity in entities:
            f.write(json.dumps(entity) + "\n")
            
    # 4. Update Stats
    update_stats(entities)
    
    # 5. Validation & Logging
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        for entity in entities:
            extracted_text = RAW_TEXT[entity["start"]:entity["end"]]
            if extracted_text != entity["text"]:
                log_msg = f"MISMATCH {datetime.datetime.now()}: Note {NOTE_ID}, Label {entity['label']}. Expected '{entity['text']}', found '{extracted_text}' at {entity['start']}:{entity['end']}\n"
                log_file.write(log_msg)
    
    print(f"Successfully processed {NOTE_ID}. Extracted {len(entities)} entities.")

if __name__ == "__main__":
    main()