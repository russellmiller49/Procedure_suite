import openpyxl
from openpyxl.utils import get_column_letter
import json
import re
import os

# -------------------------------------------------------------------------
# INPUT DATA
# -------------------------------------------------------------------------
NOTE_ID = "note_063"
SOURCE_FILE = "note_063.txt"
PROCEDURE_DATE = "2020-01-20" # Arbitrary valid date as placeholder
TEMPLATE_PATH = "phase0_golden_registry_labeling_worksheet_anchor_first_therapeutic_pleural.xlsx"
OUTPUT_PATH = f"phase0_extraction_{NOTE_ID}.xlsx"

NOTE_TEXT = """NOTE_ID:  note_063 SOURCE_FILE: note_063.txt INDICATION FOR OPERATION:  [REDACTED]is a 68 year old-year-old male who presents with airway stenosis.
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

# -------------------------------------------------------------------------
# CONFIGURATION & CLASSES
# -------------------------------------------------------------------------

class ProcedureFlag:
    def __init__(self, key, value=0):
        self.key = key
        self.value = value

class SpanAnnotation:
    def __init__(self, span_text, label, normalized_value, schema_field, event_id=None, context_prefix=None, match_index=0, is_historical="No"):
        self.span_text = span_text
        self.label = label
        self.normalized_value = normalized_value
        self.schema_field = schema_field
        self.event_id = event_id
        self.context_prefix = context_prefix
        self.match_index = match_index
        self.is_historical = is_historical

class EventLog:
    def __init__(self, event_id, event_type, method=None, anatomy_target=None, device=None, measurements=None, specimens=None, findings=None, outcome_complication=None, device_size=None, device_material=None):
        self.event_id = event_id
        self.event_type = event_type
        self.method = method
        self.anatomy_target = anatomy_target
        self.device = device
        self.measurements = measurements
        self.specimens = specimens
        self.findings = findings
        self.outcome_complication = outcome_complication
        self.device_size = device_size
        self.device_material = device_material

# -------------------------------------------------------------------------
# EXTRACTION LOGIC
# -------------------------------------------------------------------------

def extract_data():
    # 1. Flags
    flags = {
        "diagnostic_bronchoscopy": 1,
        "bal": 1,
        "bronchial_wash": 0,
        "brushings": 0,
        "endobronchial_biopsy": 1,
        "tbna_conventional": 0,
        "linear_ebus": 0,
        "radial_ebus": 0,
        "navigational_bronchoscopy": 0,
        "transbronchial_biopsy": 0,
        "transbronchial_cryobiopsy": 0,
        "therapeutic_aspiration": 1,
        "foreign_body_removal": 1,
        "airway_dilation": 1,
        "airway_stent": 1,
        "thermal_ablation": 1,
        "tumor_debulking_non_thermal": 1,
        "cryotherapy": 0,
        "blvr": 0,
        "peripheral_ablation": 0,
        "bronchial_thermoplasty": 0,
        "whole_lung_lavage": 0,
        "rigid_bronchoscopy": 1,
        "thoracentesis": 0,
        "chest_tube": 0,
        "ipc": 0,
        "medical_thoracoscopy": 0,
        "pleurodesis": 0,
        "pleural_biopsy": 0,
        "fibrinolytic_therapy": 0
    }
    
    # 2. Events & Spans
    spans = []
    events = []
    
    # -- Procedure: General Rigid
    spans.append(SpanAnnotation("Rigid Bronchoscope", "PROC_METHOD", "Rigid Bronchoscopy", "Procedure", "evt1", context_prefix="INSTRUMENT : \n"))
    
    # -- Event 2: Therapeutic Aspiration
    # "Successful therapeutic aspiration was performed to clean out the Trachea..."
    ev2 = "evt2"
    spans.append(SpanAnnotation("therapeutic aspiration", "PROC_METHOD", "Therapeutic Aspiration", "Procedure", ev2, context_prefix="Successful "))
    spans.append(SpanAnnotation("Trachea (Distal 1/3)", "ANAT_AIRWAY", "Trachea", "Target", ev2))
    spans.append(SpanAnnotation("Right Mainstem", "ANAT_AIRWAY", "RMSB", "Target", ev2, context_prefix="Trachea (Distal 1/3), "))
    spans.append(SpanAnnotation("Left Mainstem", "ANAT_AIRWAY", "LMSB", "Target", ev2, context_prefix="Bronchus Intermedius , "))
    spans.append(SpanAnnotation("mucus", "OBS_FINDING", "Mucus", "Findings", ev2, context_prefix="Left Carina (LC2) from "))
    events.append(EventLog(ev2, "Therapeutic Aspiration", method="Therapeutic Aspiration", anatomy_target="Trachea, LMSB, RMSB", findings="Mucus"))

    # -- Event 3: Endobronchial Biopsy
    # "Endobronchial biopsy was performed at the left mainstem bronchus."
    ev3 = "evt3"
    spans.append(SpanAnnotation("Endobronchial biopsy", "PROC_METHOD", "Endobronchial Biopsy", "Procedure", ev3))
    spans.append(SpanAnnotation("left mainstem bronchus", "ANAT_AIRWAY", "LMSB", "Target", ev3, context_prefix="Endobronchial biopsy was performed at the "))
    spans.append(SpanAnnotation("Lesion", "OBS_LESION", "Lesion", "Findings", ev3, context_prefix="performed at the left mainstem bronchus.  "))
    events.append(EventLog(ev3, "Endobronchial Biopsy", method="Endobronchial Biopsy", anatomy_target="LMSB", findings="Lesion"))

    # -- Event 4: Granulation Removal (Mechanical)
    ev4 = "evt4"
    spans.append(SpanAnnotation("Granulation tissue", "OBS_LESION", "Granulation Tissue", "Findings", ev4, context_prefix="LMSB STENOSIS:  Overlying "))
    spans.append(SpanAnnotation("proximal LMSB", "ANAT_AIRWAY", "LMSB", "Target", ev4, context_prefix="Granulation tissue causing stenosis at the "))
    spans.append(SpanAnnotation("Mechanical", "PROC_METHOD", "Mechanical Debulking", "Procedure", ev4, context_prefix="Results\n"))
    spans.append(SpanAnnotation("Pulmonary forceps", "DEV_INSTRUMENT", "Forceps", "Device", ev4, context_prefix="Mechanical\t"))
    events.append(EventLog(ev4, "Debulking", method="Mechanical", anatomy_target="LMSB", device="Pulmonary forceps", findings="Granulation tissue"))

    # -- Event 5: Granulation Removal (APC)
    ev5 = "evt5"
    spans.append(SpanAnnotation("APC", "PROC_METHOD", "APC", "Procedure", ev5, context_prefix="tissue destruction/removal\n"))
    spans.append(SpanAnnotation("Straightfire probe", "DEV_INSTRUMENT", "APC Probe", "Device", ev5))
    spans.append(SpanAnnotation("Forced coag", "PROC_ACTION", "Forced Coagulation", "Settings", ev5))
    events.append(EventLog(ev5, "Thermal Ablation", method="APC", anatomy_target="LMSB", device="Straightfire probe"))

    # -- Event 6: BAL
    ev6 = "evt6"
    spans.append(SpanAnnotation("Bronchial alveolar lavage", "PROC_METHOD", "BAL", "Procedure", ev6))
    spans.append(SpanAnnotation("Anteromedial Segment of LLL", "ANAT_LUNG_LOC", "LLL Anteromedial Segment", "Target", ev6))
    spans.append(SpanAnnotation("60 cc", "MEAS_VOL", "60 cc", "Measurements", ev6, context_prefix="Instilled "))
    spans.append(SpanAnnotation("20 cc", "MEAS_VOL", "20 cc", "Measurements", ev6, context_prefix="suction returned with "))
    events.append(EventLog(ev6, "BAL", method="BAL", anatomy_target="LLL Anteromedial Segment", measurements="Instilled 60cc, Return 20cc"))

    # -- Event 7: Foreign Body Removal (Stent)
    ev7 = "evt7"
    spans.append(SpanAnnotation("Foreign body removal", "PROC_METHOD", "Foreign Body Removal", "Procedure", ev7, context_prefix="Foreign body removal was performed:  "))
    spans.append(SpanAnnotation("MicroTech 10mm x 40mm stent", "DEV_STENT", "MicroTech Stent", "Device", ev7, context_prefix="The patient's existing "))
    spans.append(SpanAnnotation("pulmonary forcpes", "DEV_INSTRUMENT", "Forceps", "Device", ev7, context_prefix="grasped with the "))
    events.append(EventLog(ev7, "Foreign Body Removal", method="Foreign Body Removal", device="MicroTech Stent", anatomy_target="LMSB"))

    # -- Event 8: Balloon Dilation (LMSB 1)
    ev8 = "evt8"
    spans.append(SpanAnnotation("Balloon dilation", "PROC_METHOD", "Balloon Dilation", "Procedure", ev8, context_prefix="through the rigid barrel.\n"))
    spans.append(SpanAnnotation("Left Mainstem", "ANAT_AIRWAY", "LMSB", "Target", ev8, context_prefix="Balloon dilation was performed at "))
    spans.append(SpanAnnotation("10/11/12 Elation balloon", "DEV_INSTRUMENT", "Elation Balloon", "Device", ev8, context_prefix="Left Mainstem.  "))
    spans.append(SpanAnnotation("12 mm", "MEAS_AIRWAY_DIAM", "12 mm", "Measurements", ev8, context_prefix="perform dilation to "))
    spans.append(SpanAnnotation("60 seconds", "CTX_TIME", "60 seconds", "Time", ev8, context_prefix="dilation time of "))
    events.append(EventLog(ev8, "Airway Dilation", method="Balloon Dilation", anatomy_target="LMSB", measurements="12mm", device="Elation Balloon"))

    # -- Event 9: Stent Placement
    ev9 = "evt9"
    spans.append(SpanAnnotation("Bonastent, 10mm x 50mm", "DEV_STENT", "Bonastent", "Device", ev9))
    spans.append(SpanAnnotation("Left Mainstem bronchus", "ANAT_AIRWAY", "LMSB", "Target", ev9, context_prefix="placed in the "))
    spans.append(SpanAnnotation("10mm x 50mm", "DEV_STENT_SIZE", "10mm x 50mm", "Device Size", ev9, context_prefix="Bonastent, "))
    events.append(EventLog(ev9, "Airway Stent", method="Stent Placement", anatomy_target="LMSB", device="Bonastent", device_size="10mm x 50mm"))

    # -- Event 10: Balloon Dilation (LMSB Post-Stent)
    ev10 = "evt10"
    spans.append(SpanAnnotation("Balloon dilation", "PROC_METHOD", "Balloon Dilation", "Procedure", ev10, context_prefix="seat the stent.\n"))
    spans.append(SpanAnnotation("Left Mainstem", "ANAT_AIRWAY", "LMSB", "Target", ev10, context_prefix="Balloon dilation was performed at ", match_index=1)) # 2nd occurrence
    spans.append(SpanAnnotation("through the stent", "PROC_METHOD", "Through Stent", "Method", ev10))
    spans.append(SpanAnnotation("12 mm", "MEAS_AIRWAY_DIAM", "12 mm", "Measurements", ev10, context_prefix="dilation to ", match_index=1))
    spans.append(SpanAnnotation("30 seconds", "CTX_TIME", "30 seconds", "Time", ev10, context_prefix="dilation time of ", match_index=0)) # First occurrence of 30 sec
    events.append(EventLog(ev10, "Airway Dilation", method="Balloon Dilation", anatomy_target="LMSB", measurements="12mm"))

    # -- Event 11: Balloon Dilation (LLL)
    ev11 = "evt11"
    spans.append(SpanAnnotation("Balloon dilation", "PROC_METHOD", "Balloon Dilation", "Procedure", ev11, context_prefix="Balloon dilation was performed at the left lower lobe"))
    spans.append(SpanAnnotation("left lower lobe take-off", "ANAT_LUNG_LOC", "LLL Take-off", "Target", ev11))
    spans.append(SpanAnnotation("12 mm", "MEAS_AIRWAY_DIAM", "12 mm", "Measurements", ev11, context_prefix="dilation to ", match_index=2))
    spans.append(SpanAnnotation("30 seconds", "CTX_TIME", "30 seconds", "Time", ev11, context_prefix="dilation time of ", match_index=1))
    events.append(EventLog(ev11, "Airway Dilation", method="Balloon Dilation", anatomy_target="LLL", measurements="12mm"))

    # -- Event 12: Balloon Dilation (LUL)
    ev12 = "evt12"
    spans.append(SpanAnnotation("Balloon dilation", "PROC_METHOD", "Balloon Dilation", "Procedure", ev12, context_prefix="Balloon dilation was performed at the left upper lobe"))
    spans.append(SpanAnnotation("left upper lobe take-off", "ANAT_LUNG_LOC", "LUL Take-off", "Target", ev12))
    spans.append(SpanAnnotation("10 mm", "MEAS_AIRWAY_DIAM", "10 mm", "Measurements", ev12, context_prefix="dilation to ", match_index=0))
    spans.append(SpanAnnotation("30 seconds", "CTX_TIME", "30 seconds", "Time", ev12, context_prefix="dilation time of ", match_index=2))
    events.append(EventLog(ev12, "Airway Dilation", method="Balloon Dilation", anatomy_target="LUL", measurements="10mm"))

    # -- Event 13: Balloon Dilation (RMSB)
    ev13 = "evt13"
    spans.append(SpanAnnotation("Balloon dilation", "PROC_METHOD", "Balloon Dilation", "Procedure", ev13, context_prefix="Balloon dilation was performed at Right Mainstem"))
    spans.append(SpanAnnotation("Right Mainstem", "ANAT_AIRWAY", "RMSB", "Target", ev13, context_prefix="dilation to 10 mm at the "))
    spans.append(SpanAnnotation("8/9/10 Elation balloon", "DEV_INSTRUMENT", "Elation Balloon", "Device", ev13))
    spans.append(SpanAnnotation("10 mm", "MEAS_AIRWAY_DIAM", "10 mm", "Measurements", ev13, context_prefix="dilation to ", match_index=1))
    spans.append(SpanAnnotation("60 seconds", "CTX_TIME", "60 seconds", "Time", ev13, context_prefix="dilation time of ", match_index=1))
    events.append(EventLog(ev13, "Airway Dilation", method="Balloon Dilation", anatomy_target="RMSB", measurements="10mm"))

    # -- Outcome
    ev_out = "evt_out"
    spans.append(SpanAnnotation("No immediate complications", "OUTCOME_COMPLICATION", "None", "Outcome", ev_out))
    events.append(EventLog(ev_out, "Outcome", outcome_complication="None"))

    return flags, spans, events

# -------------------------------------------------------------------------
# GENERATION FUNCTIONS
# -------------------------------------------------------------------------

def calculate_offsets(note_text, span_text, context_prefix, match_index):
    # Normalize
    text_lower = note_text.lower()
    span_lower = span_text.lower()
    prefix_lower = context_prefix.lower() if context_prefix else None
    
    start_indices = [m.start() for m in re.finditer(re.escape(span_lower), text_lower)]
    
    if not start_indices:
        return None, None, "not_found"
    
    # 1. Unique Match
    if len(start_indices) == 1:
        return start_indices[0], start_indices[0] + len(span_text), "hydrated_unique"
    
    # 2. Context Match
    if prefix_lower:
        best_idx = None
        for idx in start_indices:
            window_start = max(0, idx - 120)
            window = text_lower[window_start:idx]
            if prefix_lower in window:
                best_idx = idx
                break
        if best_idx is not None:
            return best_idx, best_idx + len(span_text), "hydrated_prefix_window"

    # 3. Index Match
    if 0 <= match_index < len(start_indices):
        idx = start_indices[match_index]
        return idx, idx + len(span_text), "hydrated_match_index"
    
    return None, None, f"ambiguous_count={len(start_indices)}"

def create_workbook():
    wb = openpyxl.load_workbook(TEMPLATE_PATH)
    
    # Get Data
    flags, spans, events = extract_data()
    
    # 1. Note_Text
    ws_text = wb["Note_Text"]
    ws_text.append([NOTE_ID, SOURCE_FILE, NOTE_TEXT])
    
    # 2. Note_Index
    ws_index = wb["Note_Index"]
    row_idx = [
        SOURCE_FILE, NOTE_ID, "", PROCEDURE_DATE, "", "", "Extraction Done", ""
    ]
    # Add flags in order
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
        val = flags.get(k, 0)
        row_idx.append(val)
    ws_index.append(row_idx)
    
    # 3. Span_Annotations (Anchor First) & 4. Span_Hydrated
    ws_span = wb["Span_Annotations"]
    ws_hydrated = wb["Span_Hydrated"]
    
    for s in spans:
        # Base row
        row = [
            SOURCE_FILE, NOTE_ID, f"span_{len(ws_span['A'])}", "Procedure",
            s.context_prefix, s.span_text, s.match_index, 
            "", "", f"=LEN(F{len(ws_span['A'])+1})", # Formula for len
            s.label, s.normalized_value, s.schema_field, s.event_id,
            "No", s.is_historical, "No", "GPT", "", "needs_hydration"
        ]
        ws_span.append(row)
        
        # Calculate offsets
        start, end, status = calculate_offsets(NOTE_TEXT, s.span_text, s.context_prefix, s.match_index)
        
        row_hyd = list(row)
        row_hyd[7] = start
        row_hyd[8] = end
        row_hyd[9] = (end - start) if start is not None else 0
        row_hyd[19] = status
        ws_hydrated.append(row_hyd)

    # 5. Event_Log
    ws_event = wb["Event_Log"]
    for e in events:
        row = [
            SOURCE_FILE, NOTE_ID, e.event_id, e.event_type, e.method,
            e.anatomy_target, e.device, "", "", "", e.measurements,
            e.specimens, e.findings, "No", "GPT", "",
            e.device_size, e.device_material, 
            "", "", "", "", e.outcome_complication
        ]
        ws_event.append(row)

    # 6. V3_Procedure_Events & 7. JSON
    ws_v3 = wb["V3_Procedure_Events"]
    ws_json = wb["V3_Registry_JSON"]
    
    registry_data = {
        "schema_version": "3.0",
        "note_id": NOTE_ID,
        "no_immediate_complications": True, # Based on extraction
        "procedures": []
    }
    
    for e in events:
        if e.event_id == "evt_out": continue
        
        # Construct V3 Record
        v3_record = {
            "event_id": e.event_id,
            "type": e.event_type,
            "target": {"anatomy_type": "Airway" if "Airway" in e.event_type or "Stent" in e.event_type or "Dilat" in e.event_type else "Lung", "location": {"lobe": "", "segment": ""}, "station": ""},
            "lesion": {"type": "", "size_mm": None},
            "method": e.method,
            "devices": [{"name": e.device, "size": e.device_size}] if e.device else [],
            "measurements": [{"value": e.measurements}] if e.measurements else [],
            "findings": [{"description": e.findings}] if e.findings else []
        }
        
        #