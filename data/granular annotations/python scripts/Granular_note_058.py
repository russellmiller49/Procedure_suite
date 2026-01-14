import openpyxl
from openpyxl.utils import get_column_letter
import re
import json
import datetime
import os

# -------------------------------------------------------------------------
# INPUT DATA
# -------------------------------------------------------------------------
NOTE_ID = "note_058"
SOURCE_FILE = "note_058.txt"
PROCEDURE_DATE = "2026-01-12"  # Inferred from context or left blank
TEMPLATE_PATH = "phase0_golden_registry_labeling_worksheet_anchor_first_therapeutic_pleural.xlsx"
OUTPUT_PATH = f"phase0_extraction_{NOTE_ID}.xlsx"

# Full text from the provided file content
NOTE_TEXT = """NOTE_ID:  note_058 SOURCE_FILE: note_058.txt INDICATION FOR OPERATION:  [REDACTED]is a 88 year old-year-old female who presents with lung nodules.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.
PREOPERATIVE DIAGNOSIS: R91.1 Solitary Lung Nodule
 
POSTOPERATIVE DIAGNOSIS:  R91.1 Solitary Lung Nodule
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31623 Dx bronchoscope/brushing    
31624 Dx bronchoscope/lavage (BAL)    
31628 TBBX single lobe     
31632 TBBX additional lobes  
31629 TBNA single lobe   
31633 TBNA additional lobes   
31626 Fiducial marker placements, single or multiple     
31627 Navigational Bronchoscopy (computer assisted)
77012 Radiology / radiologic guidance for CT guided needle placement (CIOS)
76377 3D rendering with interpretation and reporting of CT, US, Tomo modality (ION Planning Station)
31899NFN BRONCHOSCOPY WITH ENDOBRONCHIAL 
ULTRASOUND (EBUS) OF MEDIASTINAL AND/OR HILAR LYMPH NODES WITHOUT BIOPSY
31654 Radial EBUS for peripheral lesion
31899NFD BRONCHOSCOPY W/ APPLICATION OF TRANEXAMIC ACID
 
 
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure:
This patient required a Transbronchial Cryo biopsies, Robotic Navigation to more than one site, and Radial EBUS performed at multiple locations.
This resulted in >40% increased work due to Technical difficulty of procedure and Physical and mental effort required.
Apply to: 31628 TBBX single lobe     
31629 TBNA single lobe   
31627 Navigational Bronchoscopy (computer assisted).
ANESTHESIA: 
General Anesthesia
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Flexible Therapeutic Bronchoscope
Linear EBUS 
Radial EBUS
Ion Robotic Bronchoscope
 
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
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
vcv	14	375	12	100	10	15
 
Target 1: Lingular nodule
Robotic navigation bronchoscopy was performed with Ion platform.  Partial registration was used.
Ion robotic catheter was used to engage the Superior Segment of Lingula (LB4).
Target lesion is about 1 cm in diameter.   Under navigational guidance the ion robotic catheter was advanced to 1.0 cm away from the planned target.
Radial EBUS was performed to confirm that the location of the nodule is Eccentric.
The following features were noted: Continuous margin  and Absence of linear-discrete air bronchogram.
Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
Cios Spin system was used for evaluation of nodule location.  Low dose spin was performed to acquire CT imaging.
This was passed on to Ion platform system for reconstruction and nodule location.
The 3D images was interpreted on an independent workstation (Ion).
Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location.
I personally interpreted the cone beam CT and 3-D reconstruction.
Transbronchial needle aspiration was performed with 21G Needle through the extended working channel catheter.  Total 4 samples were collected.
Samples sent for Cytology.
 
Transbronchial biopsy was performed with alligator forceps the extended working channel catheter.
Total 1 samples were collected.  Samples sent for Pathology.
 
Transbronchial cryobiopsy was performed with 1.1mm cryoprobe via the extended working channel catheter.
Freeze time of 6 seconds were used.  Total 6 samples were collected.  Samples sent for Pathology.
Transbronchial brushing was performed with Protected cytology brush the extended working channel catheter.  Total 1 samples were collected.
Samples sent for Microbiology (Cultures/Viral/Fungal).
 
Bronchial alveolar lavage was performed the extended working channel catheter.
Instilled 20 cc of NS, suction returned with 10 cc of NS.  Samples sent for Microbiology (Cultures/Viral/Fungal).
Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.
Prior to withdraw of the bronchoscope. 
 
ROSE from ION procedure was noted to be:
Conclusive evidence of malignant neoplasm
 
Prior to withdrawal of the bronchoscope, inspection demonstrated no evidence of bleeding.
Target 2: LUL anterior
Robotic navigation bronchoscopy was performed with Ion platform.  Partial registration was used.
Ion robotic catheter was used to engage the Anterior Segment of LUL (LB3).
Target lesion is about 1 cm in diameter.   Under navigational guidance the ion robotic catheter was advanced to 1.0 cm away from the planned target.
Radial EBUS was performed to confirm that the location of the nodule is Eccentric.
The following features were noted: Continuous margin  and Absence of linear-discrete air bronchogram.
Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
Cios Spin system was used for evaluation of nodule location.  Low dose spin was performed to acquire CT imaging.
This was passed on to Ion platform system for reconstruction and nodule location.
The 3D images was interpreted on an independent workstation (Ion).
Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location.
I personally interpreted the cone beam CT and 3-D reconstruction.
Transbronchial needle aspiration was performed with 21G Needle through the extended working channel catheter.  Total 6 samples were collected.
Samples sent for Cytology.
 
Cryobiopsy was attempted but was technically challenging - unable to penetrate the airway wall to achieve consistent biopsy.
Bronchial alveolar lavage was performed the extended working channel catheter.
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
ROSE from ION procedure was noted to be:
Conclusive evidence of malignant neoplasm
 
Prior to withdrawal of the bronchoscope, inspection demonstrated no evidence of bleeding.
200mg of TXA was placed into LUL to achieve hemostasis. 
 
EBUS-Findings
Indications: Diagnostic
Technique:
All lymph node stations were assessed.
Only those 5 mm or greater in short axis were sampled.
 
Lymph node sizing was performed by EBUS.
Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
4L (lower paratracheal) node
7 (subcarinal) node
10R lymph node
10L lymph node
11Rs lymph node
11Ri lymph node
11L lymph node
 
No immediate complications
 
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
Elastography provided a semi-quantitative classification (Type 1–3), which was used to guide biopsy site selection and sampling strategy.
Lymph Nodes Evaluated:
Site 1: The 4L (lower paratracheal) node was < 10 mm on CT  and Non-Hypermetabolic via PET-CT scan.
The lymph node was photographed. The site was not sampled: Sampling this lymph node was not clinically indicated.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
Site 2: The 7 (subcarinal) node waswas < 10 mm on CT  and Non-Hypermetabolic via PET-CT scan.
The lymph node was photographed. The site was not sampled: Sampling this lymph node was not clinically indicated.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
All other lymph node stations did not have any detectable lymph nodes noted. 
 
 
The patient tolerated the procedure well.
There were no immediate complications.  At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
TBNA, TBCBX, Brush, BAL lingula nodule
TBNA LUL nodule.
 
IMPRESSION/PLAN: [REDACTED]is a 88 year old-year-old female who presents for bronchoscopy for lung nodules.
- f/u in clinic for results"""

# -------------------------------------------------------------------------
# CONFIGURATION & FLAGS
# -------------------------------------------------------------------------
PROCEDURE_FLAGS = {
    # Bronchoscopy
    "diagnostic_bronchoscopy": 1,
    "bal": 1,
    "bronchial_wash": 0,
    "brushings": 1,
    "endobronchial_biopsy": 0,
    "tbna_conventional": 1,
    "linear_ebus": 1,
    "radial_ebus": 1,
    "navigational_bronchoscopy": 1,
    "transbronchial_biopsy": 1,
    "transbronchial_cryobiopsy": 1,
    "therapeutic_aspiration": 1,  # "Successful therapeutic aspiration was performed to clean out..."
    "foreign_body_removal": 0,
    "airway_dilation": 0,
    "airway_stent": 0,
    "thermal_ablation": 0,
    "tumor_debulking_non_thermal": 0,
    "cryotherapy": 0, # Biopsy only
    "blvr": 0,
    "peripheral_ablation": 0,
    "bronchial_thermoplasty": 0,
    "whole_lung_lavage": 0,
    "rigid_bronchoscopy": 0,
    # Pleural
    "thoracentesis": 0,
    "chest_tube": 0,
    "ipc": 0,
    "medical_thoracoscopy": 0,
    "pleurodesis": 0,
    "pleural_biopsy": 0,
    "fibrinolytic_therapy": 0,
}

# -------------------------------------------------------------------------
# DATA EXTRACTION LOGIC
# -------------------------------------------------------------------------

# Helper to build span dicts
def create_span(text, label, norm_val, field, event_id, context="", match_idx=0, negated=False):
    return {
        "text": text,
        "label": label,
        "normalized_value": norm_val,
        "schema_field": field,
        "event_id": event_id,
        "context_prefix": context,
        "match_index": match_idx,
        "is_negated": negated
    }

# Event Definitions
# E1: Airway Clearance (Therapeutic)
# E2: Target 1 - Lingula Nodule
# E3: Target 2 - LUL Anterior
# E4: EBUS Staging

spans = []

# --- Event 1: Therapeutic Aspiration (Mucus) ---
spans.append(create_span("Therapeutic aspiration", "PROC_METHOD", "Therapeutic aspiration", "method", "ev1", "Successful", 0))
spans.append(create_span("Right Mainstem", "ANAT_AIRWAY", "Right Mainstem", "target.anatomy", "ev1"))
spans.append(create_span("Bronchus Intermedius", "ANAT_AIRWAY", "Bronchus Intermedius", "target.anatomy", "ev1"))
spans.append(create_span("Left Mainstem", "ANAT_AIRWAY", "Left Mainstem", "target.anatomy", "ev1"))
spans.append(create_span("clean out", "PROC_ACTION", "clean out", "action", "ev1"))
spans.append(create_span("mucus", "OBS_FINDING", "mucus", "findings", "ev1"))

# --- Event 2: Target 1 (Lingula) ---
spans.append(create_span("Superior Segment of Lingula (LB4)", "ANAT_LUNG_LOC", "Superior Segment of Lingula (LB4)", "target.location.segment", "ev2"))
spans.append(create_span("1 cm", "MEAS_SIZE", "10", "lesion.size_mm", "ev2", "Target lesion is about"))
spans.append(create_span("Radial EBUS", "PROC_METHOD", "Radial EBUS", "method", "ev2", "catheter was advanced to 1.0 cm away"))
spans.append(create_span("Eccentric", "OBS_FINDING", "Eccentric", "findings", "ev2", "location of the nodule is"))
spans.append(create_span("Transbronchial needle aspiration", "PROC_METHOD", "TBNA", "method", "ev2", "I personally interpreted"))
spans.append(create_span("21G Needle", "DEV_NEEDLE", "21G", "devices", "ev2", "needle aspiration was performed with"))
spans.append(create_span("4 samples", "MEAS_COUNT", "4", "specimens", "ev2", "Total"))
spans.append(create_span("Transbronchial biopsy", "PROC_METHOD", "TBBX", "method", "ev2", "Cytology.\n \n"))
spans.append(create_span("alligator forceps", "DEV_INSTRUMENT", "alligator forceps", "devices", "ev2"))
spans.append(create_span("1 samples", "MEAS_COUNT", "1", "specimens", "ev2", "Transbronchial biopsy was performed"))
spans.append(create_span("Transbronchial cryobiopsy", "PROC_METHOD", "Cryobiopsy", "method", "ev2"))
spans.append(create_span("1.1mm cryoprobe", "DEV_INSTRUMENT", "1.1mm cryoprobe", "devices", "ev2"))
spans.append(create_span("6 samples", "MEAS_COUNT", "6", "specimens", "ev2", "Freeze time of 6 seconds"))
spans.append(create_span("Transbronchial brushing", "PROC_METHOD", "Brushing", "method", "ev2"))
spans.append(create_span("Protected cytology brush", "DEV_INSTRUMENT", "Protected cytology brush", "devices", "ev2"))
spans.append(create_span("Bronchial alveolar lavage", "PROC_METHOD", "BAL", "method", "ev2", "Samples sent for Microbiology"))
spans.append(create_span("20 cc", "MEAS_VOL", "20", "measurements", "ev2"))
spans.append(create_span("10 cc", "MEAS_VOL", "10", "measurements", "ev2"))
spans.append(create_span("Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO)", "DEV_INSTRUMENT", "Fiducial marker (0.8x3mm gold CIVCO)", "devices", "ev2"))
spans.append(create_span("Conclusive evidence of malignant neoplasm", "OBS_ROSE", "Malignant", "findings", "ev2", "ROSE from ION procedure was noted to be:"))

# --- Event 3: Target 2 (LUL) ---
spans.append(create_span("Anterior Segment of LUL (LB3)", "ANAT_LUNG_LOC", "Anterior Segment of LUL (LB3)", "target.location.segment", "ev3"))
spans.append(create_span("Radial EBUS", "PROC_METHOD", "Radial EBUS", "method", "ev3", "Target 2: LUL anterior"))
spans.append(create_span("Transbronchial needle aspiration", "PROC_METHOD", "TBNA", "method", "ev3", "Target 2: LUL anterior")) # Searching in Target 2 context
spans.append(create_span("21G Needle", "DEV_NEEDLE", "21G", "devices", "ev3", "catheter.  Total 6 samples"))
spans.append(create_span("6 samples", "MEAS_COUNT", "6", "specimens", "ev3", "needle aspiration was performed"))
spans.append(create_span("Cryobiopsy", "PROC_METHOD", "Cryobiopsy", "method", "ev3", "Samples sent for Cytology.\n \n"))
spans.append(create_span("unable to penetrate", "OBS_FINDING", "unable to penetrate airway", "findings", "ev3"))
spans.append(create_span("Bronchial alveolar lavage", "PROC_METHOD", "BAL", "method", "ev3", "challenging - unable to penetrate"))
spans.append(create_span("60 cc", "MEAS_VOL", "60", "measurements", "ev3"))
spans.append(create_span("15 cc", "MEAS_VOL", "15", "measurements", "ev3"))
spans.append(create_span("Conclusive evidence of malignant neoplasm", "OBS_ROSE", "Malignant", "findings", "ev3", "Target 2"))

# --- Event 4: EBUS Staging ---
spans.append(create_span("EBUS", "PROC_METHOD", "EBUS", "method", "ev4", "Endobronchial ultrasound ("))
spans.append(create_span("4L", "ANAT_LN_STATION", "4L", "target.station", "ev4", "Site 1: The"))
spans.append(create_span("Type 1 elastographic pattern", "OBS_FINDING", "Type 1 (benign)", "findings", "ev4", "target lymph node demonstrated a"))
spans.append(create_span("7", "ANAT_LN_STATION", "7", "target.station", "ev4", "Site 2: The"))
spans.append(create_span("Type 1 elastographic pattern", "OBS_FINDING", "Type 1 (benign)", "findings", "ev4", "Site 2"))

# --- Global Outcomes ---
spans.append(create_span("No immediate complications", "OUTCOME_COMPLICATION", "None", "outcomes.complications", "ev0", "The patient tolerated the procedure well."))

# -------------------------------------------------------------------------
# HYDRATION LOGIC
# -------------------------------------------------------------------------
def hydrate_spans(text, span_list):
    hydrated = []
    text_lower = text.lower()
    
    for s in span_list:
        row = s.copy()
        target = s['text']
        target_lower = target.lower()
        context = s.get('context_prefix', "")
        context_lower = context.lower() if context else ""
        match_idx = s.get('match_index', 0)
        
        start = -1
        end = -1
        status = "ambiguous"
        
        matches = [m.start() for m in re.finditer(re.escape(target), text)]
        
        if len(matches) == 0:
            status = "not_found"
        elif len(matches) == 1:
            start = matches[0]
            end = start + len(target)
            status = "hydrated_unique"
        else:
            # Logic for multiple matches
            found = False
            
            # 1. Try Context
            if context:
                # Find occurrences of context
                ctx_matches = [m.start() for m in re.finditer(re.escape(context), text)]
                if ctx_matches:
                    # For each target match, check if a context match is within N chars preceding
                    for tm in matches:
                        # check window 150 chars before
                        window_start = max(0, tm - 250)
                        window_text = text[window_start:tm]
                        if context in window_text:
                            start = tm
                            end = start + len(target)
                            status = "hydrated_context"
                            found = True
                            break
            
            # 2. If no context or context failed, use match_index
            if not found and match_idx is not None and match_idx < len(matches):
                start = matches[match_idx]
                end = start + len(target)
                status = "hydrated_index"
                found = True
            
            if not found:
                status = f"ambiguous_count={len(matches)}"

        row['start_char'] = start
        row['end_char'] = end
        row['hydration_status'] = status
        row['span_len'] = len(target) if start != -1 else 0
        hydrated.append(row)
        
    return hydrated

# -------------------------------------------------------------------------
# GENERATE EXCEL
# -------------------------------------------------------------------------
def main():
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: Template not found at {TEMPLATE_PATH}")
        return

    wb = openpyxl.load_workbook(TEMPLATE_PATH)
    
    # 1. Note_Text
    ws_text = wb["Note_Text"]
    ws_text.append([NOTE_ID, SOURCE_FILE, NOTE_TEXT])

    # 2. Note_Index
    ws_index = wb["Note_Index"]
    row_meta = [
        SOURCE_FILE, NOTE_ID, "", PROCEDURE_DATE, "", "", "Success", 
        "Robotic bronchoscopy with EBUS, multiple targets, cryobiopsy, fiducials."
    ]
    # Add 30 flags
    flag_keys = [
        "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings", "endobronchial_biopsy", 
        "tbna_conventional", "linear_ebus", "radial_ebus", "navigational_bronchoscopy", 
        "transbronchial_biopsy", "transbronchial_cryobiopsy", "therapeutic_aspiration", 
        "foreign_body_removal", "airway_dilation", "airway_stent", "thermal_ablation", 
        "tumor_debulking_non_thermal", "cryotherapy", "blvr", "peripheral_ablation", 
        "bronchial_thermoplasty", "whole_lung_lavage", "rigid_bronchoscopy", 
        "thoracentesis", "chest_tube", "ipc", "medical_thoracoscopy", "pleurodesis", 
        "pleural_biopsy", "fibrinolytic_therapy"
    ]
    for k in flag_keys:
        row_meta.append(PROCEDURE_FLAGS.get(k, 0))
    ws_index.append(row_meta)

    # 3 & 4. Spans (Anchor and Hydrated)
    ws_anchor = wb["Span_Annotations"]
    ws_hydrated = wb["Span_Hydrated"]
    
    hydrated_data = hydrate_spans(NOTE_TEXT, spans)
    
    # Columns for Span sheets:
    # source_file, note_id, span_id, section_type, context_prefix, span_text, match_index, 
    # start, end, len, label, norm_val, schema_field, event_id, negated, historical, time_anchor, reviewer, comments, status
    
    for idx, h in enumerate(hydrated_data):
        span_id = f"{NOTE_ID}_s{idx+1:03d}"
        row_common = [
            SOURCE_FILE, NOTE_ID, span_id, "Procedure", 
            h.get('context_prefix', ''), h['text'], h.get('match_index', ''),
            "", "", "", # anchors blank start/end/len (len is formula usually, but we leave blank here)
            h['label'], h['normalized_value'], h['schema_field'], h['event_id'], 
            h.get('is_negated', False), False, "", "", "", "needs_hydration"
        ]
        ws_anchor.append(row_common)
        
        # Hydrated row
        row_hyd = list(row_common)
        row_hyd[7] = h['start_char']
        row_hyd[8] = h['end_char']
        row_hyd[9] = h['span_len']
        row_hyd[19] = h['hydration_status']
        ws_hydrated.append(row_hyd)

    # 5. Event_Log
    ws_event = wb["Event_Log"]
    # Events defined: ev1 (Therapeutic), ev2 (Lingula), ev3 (LUL), ev4 (EBUS), ev0 (Outcome)
    
    events_summary = [
        {
            "id": "ev1", "type": "Therapeutic Aspiration", "method": "Therapeutic Aspiration",
            "anatomy": "Right Mainstem, BI, Left Mainstem", "findings": "Mucus cleaned out"
        },
        {
            "id": "ev2", "type": "Diagnostic Bronchoscopy", "method": "Robotic/Ion, Radial EBUS, TBNA, TBBX, Cryo, Brush, BAL, Fiducial",
            "anatomy": "Superior Segment Lingula (LB4)", "devices": "21G Needle, Alligator Forceps, 1.1mm Cryoprobe, Cytology Brush, 0.8x3mm Gold Fiducial",
            "specimens": "TBNA(4), TBBX(1), Cryo(6), Brush(1), BAL", "findings": "Lesion 1cm Eccentric, Malignant ROSE"
        },
        {
            "id": "ev3", "type": "Diagnostic Bronchoscopy", "method": "Robotic/Ion, Radial EBUS, TBNA, Cryo(fail), BAL",
            "anatomy": "Anterior Segment LUL (LB3)", "devices": "21G Needle",
            "specimens": "TBNA(6), BAL", "findings": "Lesion 1cm Eccentric, Malignant ROSE, Cryo failed"
        },
        {
            "id": "ev4", "type": "EBUS Staging", "method": "Linear EBUS", 
            "anatomy": "Stations 4R, 4L, 7, 10R, 10L, 11Rs, 11Ri, 11L",
            "findings": "4L and 7 benign (elastography), others not detectable"
        },
        {
            "id": "ev0", "type": "Outcome", "outcome": "No complications"
        }
    ]
    
    for ev in events_summary:
        # source, note, id, type, method, anat, dev, gauge, station, count, meas, spec, find, hist, rev, comm, sz, mat, lum_pre, lum_post, symp, pl_out, comp
        row = [
            SOURCE_FILE, NOTE_ID, ev["id"], ev.get("type", ""), ev.get("method", ""), 
            ev.get("anatomy", ""), ev.get("devices", ""), "", "", "", "", 
            ev.get("specimens", ""), ev.get("findings", ""), False, "", "",
            "", "", "", "", "", "", ev.get("outcome", "")
        ]
        ws_event.append(row)

    # 6. V3_Procedure_Events
    ws_v3 = wb["V3_Procedure_Events"]
    # Schema: note_id, event_id, type, target_anat_type, lobe, segment, station, lesion_type, size, method, dev_json, meas_json, spec_json, find_json, quote, ...
    
    # Event 1
    ws_v3.append([
        NOTE_ID, "ev1", "Therapeutic Bronchoscopy", "Airway", "", "RMS, BI, LMS", "", 
        "", "", "Therapeutic Aspiration", "", "", "", '{"finding": "mucus"}', "clean out... mucus",
        "", "", "", "", "", "", "", ""
    ])
    # Event 2
    ws_v3.append([
        NOTE_ID, "ev2", "Diagnostic Bronchoscopy", "Lung", "LUL", "Lingula Superior (LB4)", "", 
        "Nodule", "10", "Navigational, Radial EBUS, TBNA, TBBX, Cryo, Brush, BAL, Fiducial", 
        '{"needle": "21G", "forceps": "alligator", "cryoprobe": "1.1mm", "fiducial": "0.8x3mm gold"}',
        '{"bal_in": "20cc", "bal_out": "10cc"}',
        '{"tbna": 4, "tbbx": 1, "cryo": 6, "brush": 1}',
        '{"rose": "Malignant", "ebus": "eccentric"}',
        "Target 1: Lingular nodule... Malignant",
        "", "", "", "", "", "", "", ""
    ])
    # Event 3
    ws_v3.append([
        NOTE_ID, "ev3", "Diagnostic Bronchoscopy", "Lung", "LUL", "Anterior (LB3)", "", 
        "Nodule", "10", "Navigational, Radial EBUS, TBNA, BAL", 
        '{"needle": "21G"}',
        '{"bal_in": "60cc", "bal_out": "15cc"}',
        '{"tbna": 6}',
        '{"rose": "Malignant", "ebus": "eccentric", "cryo_status": "failed"}',
        "Target 2: LUL anterior... Malignant",
        "", "", "", "", "", "", "", ""
    ])
    
    # 7. JSON
    ws_json = wb["V3_Registry_JSON"]
    registry_data = {
        "schema_version": "3.0",
        "note_id": NOTE_ID,
        "procedures": [
            {
                "event_id": "ev1",
                "type": "Therapeutic Bronchoscopy",
                "method": "Aspiration",
                "target": {"anatomy": "Airway"},
                "findings": ["Mucus"]
            },
            {
                "event_id": "ev2",
                "type": "Diagnostic Bronchoscopy",
                "target": {"lobe": "LUL", "segment": "Lingula Superior"},
                "technologies": ["Ion", "Radial EBUS", "Fluoroscopy", "Cone Beam CT"],
                "samples": ["TBNA", "TBBX", "Cryobiopsy", "Brush", "BAL"],
                "implants": ["Fiducial"]
            },
            {
                "event_id": "ev3",
                "type": "Diagnostic Bronchoscopy",
                "target": {"lobe": "LUL", "segment": "Anterior"},
                "technologies": ["Ion", "Radial EBUS"],
                "samples": ["TBNA", "BAL"]
            }
        ],
        "outcomes": {
            "complications": "None"
        }
    }
    ws_json.append([json.dumps(registry_data, indent=2)])

    # Save
    wb.save(OUTPUT_PATH)
    print(f"Successfully generated {OUTPUT_PATH}")

if __name__ == "__main__":
    main()