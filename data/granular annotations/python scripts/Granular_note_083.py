import openpyxl
from openpyxl.utils import get_column_letter
import json
import re
import os

# -------------------------------------------------------------------------
# INPUT DATA
# -------------------------------------------------------------------------
NOTE_ID = "note_083"
SOURCE_FILE = "note_083.txt"
PROCEDURE_DATE = "2026-01-12" # inferred or blank
NOTE_TEXT = """NOTE_ID:  note_083 SOURCE_FILE: note_083.txt INDICATION FOR OPERATION:  [REDACTED]is a 68 year old-year-old female who presents with bronchial stenosis.
PREOPERATIVE DIAGNOSIS: J98.09 Other diseases of bronchus, not elsewhere classified
POSTOPERATIVE DIAGNOSIS:  J98.09 Other diseases of bronchus, not elsewhere classified
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)    
31625 Endobronchial Biopsy(s)
31654 Radial EBUS for peripheral lesion
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
31635 Foreign body removal
22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure:
This patient required a extensive mechanical excision of endobronchial tissue to salvage 
the airway as well as two separate stent placement given abarrent anatomy.
This resulted in >80% increased work due to Technical difficulty of procedure and Physical and mental effort required.
Apply to: 31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy).
Pt with complex airway with significant stenosis of the LMSB and complete occlusion of the LLL bronchus that required multiple attempts and 
 ANESTHESIA: 
General Anesthesia
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Disposable Bronchoscope
ESTIMATED BLOOD LOSS:   Minimum
COMPLICATIONS:    None
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: 
Initial Airway Inspection Findings:
An iGel was placed by anesthesia after adequate sedation.
Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Trachea (Distal 1/3), Left Mainstem, Carina, LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus and mucus plug.
The stent was partially occluded with thick yellow,green mucus
The LUL bronchus was approximately 3-4 mm and the LLL bronchus could not be visualized.
Saline was instilled without visualization of the LLL.  
Endobronchial tumor was noted and required extensive excision and mechanical debridement.
(Alligator forceps) and 1.7 cryoprobe with 30 second freeze cycles to vascular occlusion and then cryotherapy for further debulking of the LUL ostium.
It appeared that the LMSB stent migrated distally and appeared to be covering the LMSB
Using forceps the proximal end of the microtech stent was grasped and then removed on en bloc with the bronchoscope.
The foreign body removal was difficult due to significant inflammation.
After removal the LMSB mucosa was ragged, irregular and there was dynamic collapse.
The LLL bronchus could not be visualized and the LC2 was difficult to delineate along the inferior portion.
The area of firm and unable to use multiple aliquots the LLL airway could not be identified.
Due to complex anatomy a jag wire was placed in the Lingula and the radial EBUS was utilized to identify vasculature and airways but the LLL was still unable to be identified.
Bronchial alveolar lavage was performed at Superior Segment of Lingula (LB4).
Instilled 40 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S): 
- LUL BAL - cell count, culture and cytology
- LMSB EBBx - pathology 
IMPRESSION/PLAN: [REDACTED]is a 68 year old-year-old female who presents for bronchoscopy for bronchial stenosis.
Very odd presentation of cicatrization and benign stenosis of the LMSB without evidence of residual malignancy.
Very challenging anatomy of the airway and stenosis. Continues to have robust inflammatory response and no additional stents were placed.
- admit overnight
- start abx to treat MSSA, add prednisone 20 mg and obtain CT chest with contrast
- NPO after midnight for bronchoscopy [REDACTED]"""

TEMPLATE_PATH = "phase0_golden_registry_labeling_worksheet_anchor_first_therapeutic_pleural.xlsx"
OUTPUT_PATH = f"phase0_extraction_{NOTE_ID}.xlsx"

# -------------------------------------------------------------------------
# PROCEDURE FLAGS
# -------------------------------------------------------------------------
# Based on the text, we determine the flags:
# - Therapeutic aspiration: "Successful therapeutic aspiration was performed"
# - Foreign body removal: "foreign body removal", "stent was... removed"
# - Endobronchial Biopsy: "Endobronchial Biopsy(s)", "LMSB EBBx"
# - BAL: "Bronchial alveolar lavage was performed"
# - Radial EBUS: "Radial EBUS for peripheral lesion"
# - Cryotherapy: "cryotherapy for further debulking"
# - Tumor debulking (non-thermal): "mechanical excision", "Alligator forceps"
# - Airway stent: Note says "no additional stents were placed" (though one was removed). Keep 0.
# - Transbronchial Biopsy: Not explicitly mentioned (EBBx is endobronchial).
# - Rigid: Not mentioned (Disposable Bronchoscope used).

FLAGS = {
    "diagnostic_bronchoscopy": 1, # Implied base
    "bal": 1,
    "bronchial_wash": 0,
    "brushings": 0,
    "endobronchial_biopsy": 1,
    "tbna_conventional": 0,
    "linear_ebus": 0,
    "radial_ebus": 1,
    "navigational_bronchoscopy": 0,
    "transbronchial_biopsy": 0,
    "transbronchial_cryobiopsy": 0,
    "therapeutic_aspiration": 1,
    "foreign_body_removal": 1,
    "airway_dilation": 0,
    "airway_stent": 0, # Removal only
    "thermal_ablation": 0,
    "tumor_debulking_non_thermal": 1, # Mechanical debridement with forceps
    "cryotherapy": 1,
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
    "fibrinolytic_therapy": 0
}

# -------------------------------------------------------------------------
# SPAN ANNOTATIONS
# -------------------------------------------------------------------------
# Structure: (span_text, label, normalized_value, schema_field, event_id, context_prefix)
# Events:
# E1: Therapeutic Aspiration
# E2: Stent Removal (Foreign Body)
# E3: Tumor/Stenosis Mgmt (Cryo/Forceps)
# E4: Radial EBUS
# E5: BAL
# E6: General/Outcomes

SPANS = [
    # E1: Therapeutic Aspiration
    ("Therapeutic aspiration", "PROC_METHOD", "Therapeutic Aspiration", "procedure.method", "E1", "Successful "),
    ("Trachea", "ANAT_AIRWAY", "Trachea", "target.anatomy", "E1", "clean out the "),
    ("Left Mainstem", "ANAT_AIRWAY", "Left Mainstem Bronchus", "target.anatomy", "E1", "Distal 1/3), "),
    ("Carina", "ANAT_AIRWAY", "Carina", "target.anatomy", "E1", "Left Mainstem, "),
    ("LUL Lingula Carina", "ANAT_AIRWAY", "LUL Lingula Carina", "target.anatomy", "E1", None),
    ("mucus", "OBS_FINDING", "Mucus", "findings.finding", "E1", "LC2) from "),
    
    # E2: Stent Removal (Foreign Body)
    ("LMSB", "ANAT_AIRWAY", "Left Mainstem Bronchus", "target.anatomy", "E2", "stent migrated distally and appeared to be covering the "),
    ("stent", "DEV_STENT", "Stent", "device.type", "E2", "LMSB "),
    ("Microtech", "DEV_STENT_MATERIAL", "Microtech", "device.material", "E2", None), # Brand treated as material/type for granular
    ("forceps", "DEV_INSTRUMENT", "Forceps", "device.type", "E2", "Using "),
    ("removed", "PROC_ACTION", "Removal", "procedure.action", "E2", "grasped and then "),
    ("foreign body removal", "PROC_METHOD", "Foreign Body Removal", "procedure.method", "E2", "The "),
    
    # E3: Tumor/Stenosis Mgmt
    ("Endobronchial tumor", "OBS_LESION", "Endobronchial Tumor", "lesion.type", "E3", None),
    ("extensive excision", "PROC_ACTION", "Excision", "procedure.action", "E3", "required "),
    ("mechanical debridement", "PROC_METHOD", "Mechanical Debridement", "procedure.method", "E3", "excision and "),
    ("Alligator forceps", "DEV_INSTRUMENT", "Alligator Forceps", "device.type", "E3", None),
    ("1.7 cryoprobe", "DEV_INSTRUMENT", "Cryoprobe 1.7mm", "device.type", "E3", None),
    ("cryotherapy", "PROC_METHOD", "Cryotherapy", "procedure.method", "E3", "occlusion and then "),
    ("LUL ostium", "ANAT_AIRWAY", "LUL Ostium", "target.anatomy", "E3", "debulking of the "),
    
    # E4: Radial EBUS
    ("Radial EBUS", "PROC_METHOD", "Radial EBUS", "procedure.method", "E4", "31654 "),
    ("Lingula", "ANAT_AIRWAY", "Lingula", "target.anatomy", "E4", "wire was placed in the "),
    ("jag wire", "DEV_INSTRUMENT", "Jag Wire", "device.type", "E4", "anatomy a "),
    ("radial EBUS", "DEV_INSTRUMENT", "Radial EBUS Probe", "device.type", "E4", "Lingula and the "),
    
    # E5: BAL
    ("Bronchial alveolar lavage", "PROC_METHOD", "Bronchoalveolar Lavage", "procedure.method", "E5", None),
    ("Superior Segment of Lingula", "ANAT_AIRWAY", "Lingula Superior Segment", "target.anatomy", "E5", "performed at "),
    ("40 cc", "MEAS_VOL", "40", "measurements.volume", "E5", "Instilled "),
    ("15 cc", "MEAS_VOL", "15", "measurements.volume", "E5", "returned with "),
    
    # E6: General/Outcomes
    ("None", "OUTCOME_COMPLICATION", "None", "outcomes.complications", "E6", "COMPLICATIONS:    "),
    ("Disposable Bronchoscope", "DEV_INSTRUMENT", "Disposable Bronchoscope", "device.type", "E6", None),
]

# -------------------------------------------------------------------------
# CLASSES & FUNCTIONS
# -------------------------------------------------------------------------

class Phase0Generator:
    def __init__(self, note_text):
        self.note_text = note_text
        self.wb = openpyxl.load_workbook(TEMPLATE_PATH)
        self.span_data = [] # To store hydrated spans for sheets
        
    def generate(self):
        self.populate_note_text()
        self.populate_note_index()
        self.populate_spans_and_hydrate()
        self.populate_event_log()
        self.populate_v3_procedure_events()
        self.populate_v3_registry_json()
        self.wb.save(OUTPUT_PATH)
        print(f"Generated {OUTPUT_PATH}")

    def populate_note_text(self):
        ws = self.wb['Note_Text']
        ws.append([NOTE_ID, SOURCE_FILE, self.note_text])

    def populate_note_index(self):
        ws = self.wb['Note_Index']
        # Metadata row
        row = [SOURCE_FILE, NOTE_ID, "", PROCEDURE_DATE, "", "", "Success", ""]
        # Add flags
        flag_keys = list(FLAGS.keys())
        for key in flag_keys:
            row.append(FLAGS[key])
        ws.append(row)

    def populate_spans_and_hydrate(self):
        # Anchor sheet
        ws_anchor = self.wb['Span_Annotations']
        # Hydrated sheet
        ws_hydrated = self.wb['Span_Hydrated']
        
        for idx, (span_text, label, norm_val, schema, event_id, ctx) in enumerate(SPANS):
            span_id = f"span_{idx+1:03d}"
            
            # Anchor Row (Start/End blank)
            anchor_row = [
                SOURCE_FILE, NOTE_ID, span_id, "Procedure",
                ctx, span_text, "", # match_index blank
                "", "", "", # start, end, len blank
                label, norm_val, schema, event_id,
                "FALSE", "FALSE", "", "", "", "needs_hydration"
            ]
            ws_anchor.append(anchor_row)
            
            # Hydrate
            start, end, status = self.find_offset(span_text, ctx)
            length = ""
            if isinstance(start, int):
                length = end - start
            
            hydrated_row = [
                SOURCE_FILE, NOTE_ID, span_id, "Procedure",
                ctx, span_text, "",
                start, end, length,
                label, norm_val, schema, event_id,
                "FALSE", "FALSE", "", "", "", status
            ]
            ws_hydrated.append(hydrated_row)
            
            # Store for usage in other sheets
            self.span_data.append({
                "span_id": span_id,
                "text": span_text,
                "label": label,
                "norm": norm_val,
                "event_id": event_id
            })

    def find_offset(self, span_text, context_prefix):
        # Simple hydration logic
        # 1. Exact match count
        matches = [m.start() for m in re.finditer(re.escape(span_text), self.note_text)]
        
        if len(matches) == 0:
            return "", "", "not_found"
        
        if len(matches) == 1:
            return matches[0], matches[0] + len(span_text), "hydrated_unique"
            
        # Context match
        if context_prefix:
            for m in matches:
                # Look back 120 chars
                window_start = max(0, m - 120)
                window_text = self.note_text[window_start:m]
                if context_prefix in window_text:
                    return m, m + len(span_text), "hydrated_prefix_window"
        
        # Default to first if ambiguous (simplification for this task)
        return matches[0], matches[0] + len(span_text), f"ambiguous_count={len(matches)}"

    def populate_event_log(self):
        ws = self.wb['Event_Log']
        # Group by event_id
        events = {}
        for s in self.span_data:
            eid = s['event_id']
            if eid not in events:
                events[eid] = {
                    "method": [], "anatomy": [], "device": [], 
                    "specimens": [], "findings": [], "measurements": [],
                    "outcomes": {}
                }
            
            if s['label'] == "PROC_METHOD": events[eid]["method"].append(s['norm'])
            elif s['label'] == "ANAT_AIRWAY": events[eid]["anatomy"].append(s['norm'])
            elif s['label'] in ["DEV_STENT", "DEV_INSTRUMENT", "DEV_CATHETER"]: events[eid]["device"].append(s['norm'])
            elif s['label'] == "OBS_FINDING": events[eid]["findings"].append(s['norm'])
            elif s['label'] == "MEAS_VOL": events[eid]["measurements"].append(s['norm'])
            elif s['label'] == "OUTCOME_COMPLICATION": events[eid]["outcomes"]["complication"] = s['norm']
            elif s['label'] == "OBS_LESION": events[eid]["findings"].append(s['norm'])
            elif s['label'] == "PROC_ACTION": events[eid]["findings"].append(s['norm']) # Use findings for actions in simple log

        for eid, data in events.items():
            row = [
                SOURCE_FILE, NOTE_ID, eid, "Procedure",
                ", ".join(set(data["method"])),
                ", ".join(set(data["anatomy"])),
                ", ".join(set(data["device"])),
                "", "", "", # Gauge, stations, counts
                ", ".join(set(data["measurements"])),
                ", ".join(set(data["specimens"])),
                ", ".join(set(data["findings"])),
                "FALSE", "", "", "", "", # Historical, reviewer, comments, size, material
                "", "", "", "", # Outcomes airway/pleural
                data["outcomes"].get("complication", "")
            ]
            ws.append(row)

    def populate_v3_procedure_events(self):
        ws = self.wb['V3_Procedure_Events']
        # Same event groupings
        # Just map columns roughly
        for eid in sorted(set(s['event_id'] for s in self.span_data)):
             # Re-gather data specific to this event
             methods = [s['norm'] for s in self.span_data if s['event_id'] == eid and s['label'] == 'PROC_METHOD']
             anatomy = [s['norm'] for s in self.span_data if s['event_id'] == eid and s['label'].startswith('ANAT')]
             devices = [s['norm'] for s in self.span_data if s['event_id'] == eid and s['label'].startswith('DEV')]
             
             row = [
                 NOTE_ID, eid, "Procedure",
                 ", ".join(anatomy), "", "", "", # Target anatomy broken down
                 "", "", # Lesion
                 ", ".join(methods),
                 json.dumps(devices),
                 "", "", "", "", # meas, spec, find, quote
                 "", "", "", # stent props
                 "", "", "", "", "" # Outcomes
             ]
             ws.append(row)

    def populate_v3_registry_json(self):
        ws = self.wb['V3_Registry_JSON']
        data = {
            "schema_version": "3.0",
            "note_id": NOTE_ID,
            "procedures": [],
            "no_immediate_complications": True # Based on text
        }
        ws.append([json.dumps(data, indent=2)])

# -------------------------------------------------------------------------
# EXECUTION
# -------------------------------------------------------------------------
if __name__ == "__main__":
    generator = Phase0Generator(NOTE_TEXT)
    generator.generate()