import sys
import os
import json
import re
from datetime import datetime
import openpyxl
from openpyxl.utils import get_column_letter

# -------------------------------------------------------------------------
# INPUT DATA & CONFIGURATION
# -------------------------------------------------------------------------
NOTE_ID = "note_084"
SOURCE_FILE = "note_084.txt"
TEMPLATE_PATH = "phase0_golden_registry_labeling_worksheet_anchor_first_therapeutic_pleural.xlsx"
OUTPUT_PATH = f"phase0_extraction_{NOTE_ID}.xlsx"

NOTE_TEXT = """NOTE_ID:  note_084 SOURCE_FILE: note_084.txt INDICATION FOR OPERATION:  [REDACTED]is a 74 year old-year-old female who presents with ILD.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
PREOPERATIVE DIAGNOSIS: Interstitial Lung Disease
POSTOPERATIVE DIAGNOSIS:  Interstitial Lung Disease
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31622 Dx bronchoscope/cell washing          
31624 Dx bronchoscope/lavage (BAL)    
31628 TBBX single lobe     
31654 Radial EBUS for peripheral lesion
D/C 31899NFK BRONCHOSCOPY, RIGID OR FLEXIBLE, INCLUDING FLUOROSCOPIC GUIDANCE AND OCCLUSION BALLOON, WHEN PERFORMED;
WITH BRONCHIAL, ENDOBRONCHIAL, OR TRANSBRONCHIAL CRYOBIOPSY(S), SINGLE LOBE
22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure:
This patient required a Transbronchial Cryo biopsies.
This resulted in >60% increased work due to Increased intensity, Time, Technical difficulty of procedure, Severity of patient's condition, and Physical and mental effort required.
Apply to: 31628 TBBX single lobe     Pt with significant bleeding after biopsy that required blocker placement and attempt to clot blood.
She continued to bleed and required admission to the ICU. Total time with blocker inflation was 24 minutes.
ANESTHESIA: 
General Anesthesia
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENT : 
Flexible Therapeutic Bronchoscope
Radial EBUS
ESTIMATED BLOOD LOSS:   50 cc but continued bleeding
COMPLICATIONS:    Bleeding requiring endobronchial blocker
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
PATIENT POSITION: .supine
Initial Airway Inspection Findings:
The patient was sedated by anesthesia.
Next the bronchoscope was used to fiberoptically intubate the patient with a size 7 Ardnt blocker along side the ETT.
The vocal cords are normal instructure and function. After atraumatic intubation the loop of the endobronchial blocker was moved to the RLL lateral subsegment
Evaluation of the airway was performed.
There were no endobronchial lesions and the mucosa was normal.
Bronchial alveolar lavage was performed at Medial Segment of RML (RB5).
Instilled 40 cc of NS, suction returned with 25 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
Radial EBUS was performed to confirm there were no enlarged blood vessels in the segment of the RLL lateral segment.
Transbronchial biopsy was performed with alligator forceps at Lateral-basal Segment of RLL (RB9).  Total 1 samples were collected.
Samples sent for Pathology. There was no bleeding after this biopsy
Transbronchial biopsy was performed with 1.7 mm cryoprobe with a 4 second freeze.
The scope and the cryoprobe were removed together at Lateral-basal Segment of RLL (RB9).  Total 1 samples were collected.
Samples sent for Pathology. Immediately after removal of the bronchoscope the balloon on the blocker was inflated with 3 cc.
The balloon was left inflated for a total of 2 minutes. At the time of deflation there was continued bleeding.
A total of 1000 mg of TXA, 2 mg epi, 5 cc iced saline were given through the end of the inflated blocker.
Additional isolation time of 5 minutes, followed by additional 10 minutes followed by another 10 minutes.
The ETT is at 21 cm at the front teeth and the blocker is at 29 cm at the front teeth.
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was transferred to the ICU for continued care.
SPECIMEN(S): 
BAL RML 
TBBX right lower lobe
cryoTBBx right lower lobe
IMPRESSION/PLAN: [REDACTED]is a 74 year old-year-old female who presents for bronchoscopy for ILD.
[ ] transfer to ICU
[ ] repeat bronchoscopy in ICU"""

# -------------------------------------------------------------------------
# PROCEDURE FLAGS
# -------------------------------------------------------------------------
PROCEDURE_FLAGS = {
    "diagnostic_bronchoscopy": 1,
    "bal": 1,
    "bronchial_wash": 1,
    "brushings": 0,
    "endobronchial_biopsy": 0,
    "tbna_conventional": 0,
    "linear_ebus": 0,
    "radial_ebus": 1,
    "navigational_bronchoscopy": 0,
    "transbronchial_biopsy": 1,
    "transbronchial_cryobiopsy": 1,
    "therapeutic_aspiration": 1, # Code 31645 present
    "foreign_body_removal": 0,
    "airway_dilation": 0,
    "airway_stent": 0,
    "thermal_ablation": 0,
    "tumor_debulking_non_thermal": 0,
    "cryotherapy": 0,
    "blvr": 0,
    "peripheral_ablation": 0,
    "bronchial_thermoplasty": 0,
    "whole_lung_lavage": 0,
    "rigid_bronchoscopy": 0,
    "thoracentesis": 0,
    "chest_tube": 0,
    "ipc": 0,
    "medical_thoracoscopy": 0,
    "pleurodesis": 0,
    "pleural_biopsy": 0,
    "fibrinolytic_therapy": 0
}

# -------------------------------------------------------------------------
# ANCHOR-FIRST SPANS
# -------------------------------------------------------------------------
# Format: (span_text, label, normalized_value, event_id, context_prefix)
SPANS = [
    # Event 1: BAL RML
    ("Bronchial alveolar lavage", "PROC_METHOD", "BAL", "evt1", "mucosa was normal."),
    ("Medial Segment of RML (RB5)", "ANAT_LUNG_LOC", "RML Medial Segment", "evt1", "performed at "),
    ("Instilled 40 cc", "MEAS_VOL", "40", "evt1", None),
    ("returned with 25 cc", "MEAS_VOL", "25", "evt1", None),
    
    # Event 2: Radial EBUS
    ("Radial EBUS", "PROC_METHOD", "Radial EBUS", "evt2", "Cytology.\n"),
    ("RLL lateral segment", "ANAT_LUNG_LOC", "RLL Lateral Segment", "evt2", "segment of the "),
    ("no enlarged blood vessels", "OBS_LESION", "normal", "evt2", None),

    # Event 3: TBBX Forceps
    ("Transbronchial biopsy", "PROC_METHOD", "Transbronchial Biopsy", "evt3", "enlarged blood vessels"),
    ("alligator forceps", "DEV_INSTRUMENT", "Alligator Forceps", "evt3", None),
    ("Lateral-basal Segment of RLL (RB9)", "ANAT_LUNG_LOC", "RLL Lateral Basal Segment", "evt3", "forceps at "),
    ("Total 1 samples", "MEAS_COUNT", "1", "evt3", "Segment of RLL (RB9).  "),

    # Event 4: TBBX Cryo
    # Note: Text says "Transbronchial biopsy was performed with 1.7 mm cryoprobe"
    ("Transbronchial biopsy", "PROC_METHOD", "Transbronchial Cryobiopsy", "evt4", "after this biopsy\n"),
    ("1.7 mm cryoprobe", "DEV_INSTRUMENT", "Cryoprobe", "evt4", None),
    ("1.7 mm", "DEV_CATHETER_SIZE", "1.7mm", "evt4", "performed with "),
    ("4 second freeze", "PROC_ACTION", "Freeze 4s", "evt4", None),
    ("Lateral-basal Segment of RLL (RB9)", "ANAT_LUNG_LOC", "RLL Lateral Basal Segment", "evt4", "removed together at "),
    ("Total 1 samples", "MEAS_COUNT", "1", "evt4", "Segment of RLL (RB9).  "),

    # Complication (Linked to Event 4 - Cryo, as it happened immediately after)
    ("continued bleeding", "OUTCOME_COMPLICATION", "Bleeding", "evt4", "deflation there was "),
    ("Bleeding requiring endobronchial blocker", "OUTCOME_COMPLICATION", "Bleeding requiring blocker", "evt4", "COMPLICATIONS:    "),
    ("transferred to the ICU", "OUTCOME_COMPLICATION", "ICU Admission", "evt4", "operation, the patient was "),
    ("Ardnt blocker", "DEV_INSTRUMENT", "Arndt Blocker", "evt4", None),
    ("1000 mg of TXA", "PROC_ACTION", "Administer TXA", "evt4", None)
]

# -------------------------------------------------------------------------
# EVENT MAPPING
# -------------------------------------------------------------------------
EVENTS = [
    {
        "event_id": "evt1",
        "type": "bronchial_lavage",
        "method": "BAL",
        "target": {"anatomy_type": "segment", "location": {"lobe": "RML", "segment": "Medial"}},
        "measurements_json": {"instilled": "40 cc", "return": "25 cc"},
        "specimens_json": ["Cell Count", "Microbiology", "Cytology"]
    },
    {
        "event_id": "evt2",
        "type": "radial_ebus",
        "method": "Radial EBUS",
        "target": {"anatomy_type": "segment", "location": {"lobe": "RLL", "segment": "Lateral"}},
        "findings_json": ["No enlarged blood vessels"]
    },
    {
        "event_id": "evt3",
        "type": "transbronchial_biopsy",
        "method": "Forceps",
        "target": {"anatomy_type": "segment", "location": {"lobe": "RLL", "segment": "Lateral Basal"}},
        "devices_json": ["Alligator forceps"],
        "counts": "1 sample"
    },
    {
        "event_id": "evt4",
        "type": "transbronchial_cryobiopsy",
        "method": "Cryoprobe",
        "target": {"anatomy_type": "segment", "location": {"lobe": "RLL", "segment": "Lateral Basal"}},
        "devices_json": ["1.7 mm cryoprobe", "Arndt blocker"],
        "counts": "1 sample",
        "outcomes": {
            "complications": "Bleeding requiring blocker, ICU transfer"
        }
    }
]

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------
def get_offsets(text, span_text, context_prefix=None):
    """
    Finds start/end/match_index for a span.
    Logic:
    1. If context_prefix provided, search for prefix + window + span.
    2. Else if unique, use it.
    3. Else ambiguous.
    """
    if not span_text:
        return None, None, None, "error_empty"
    
    # Escape for regex
    esc_span = re.escape(span_text)
    
    matches = [m for m in re.finditer(esc_span, text)]
    
    if not matches:
        return None, None, None, "not_found"
    
    # Context Match
    if context_prefix:
        esc_ctx = re.escape(context_prefix)
        # Look for context within N chars before span
        for i, m in enumerate(matches):
            start = m.start()
            window_start = max(0, start - 150)
            pre_text = text[window_start:start]
            if context_prefix in pre_text:
                return start, m.end(), i + 1, "hydrated_context"
    
    # Unique Match
    if len(matches) == 1:
        return matches[0].start(), matches[0].end(), 1, "hydrated_unique"
    
    # Fallback: ambiguous
    return None, None, None, f"ambiguous_count={len(matches)}"

# -------------------------------------------------------------------------
# MAIN GENERATION
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
    # Headers should already exist. Row structure: 
    # source_file, note_id, encounter, date, site, reviewer, status, notes, flags...
    row_meta = [SOURCE_FILE, NOTE_ID, "", "", "", "", "Complete", ""]
    
    # Map flags strictly to the template columns if possible, but here we assume strict ordering isn't guaranteed
    # so we'll construct the list based on known flag definitions in script
    # For this snippet, we assume the user knows the template columns match keys or we append known dict keys.
    # We will just append the dict values in order of the keys defined in PROCEDURE_FLAGS.
    flag_values = list(PROCEDURE_FLAGS.values())
    ws_index.append(row_meta + flag_values)

    # 3. Span_Annotations (Anchor First - No Offsets) & 4. Span_Hydrated
    ws_anno = wb["Span_Annotations"]
    ws_hydra = wb["Span_Hydrated"]
    
    # Columns: source, note_id, span_id, section, context, span_text, match_index, start, end, len, label, norm, schema, event, negated, historical, time, reviewer, comments, status
    
    span_counter = 1
    for span_def in SPANS:
        txt, label, norm, evt, ctx = span_def
        span_id = f"span_{span_counter:03d}"
        
        # Calculate hydration
        start, end, midx, status = get_offsets(NOTE_TEXT, txt, ctx)
        span_len = len(txt)
        
        # Common row data
        # Note: start/end blank in Anno, filled in Hydra
        row_base = [
            SOURCE_FILE, NOTE_ID, span_id, "Procedure", ctx, txt, midx
        ]
        
        row_meta_tail = [
            span_len, label, norm, "", evt, 
            "FALSE", "FALSE", "", "", "", status
        ]
        
        # Write to Annotations (start/end blank)
        ws_anno.append(row_base + ["", ""] + row_meta_tail)
        
        # Write to Hydrated (start/end filled if found)
        s_val = start if start is not None else ""
        e_val = end if end is not None else ""
        ws_hydra.append(row_base + [s_val, e_val] + row_meta_tail)
        
        span_counter += 1

    # 5. Event_Log
    ws_event = wb["Event_Log"]
    for evt in EVENTS:
        # Flatten simple dict to row
        # Columns: src, note, event_id, type, method, anatomy, device, gauge, station, count, meas, spec, find, hist, rev, comm, dev_size, dev_mat, out_lumen_pre, out_lumen_post, out_symp, out_pleural, out_comp
        
        tgt = evt.get("target", {})
        loc_str = f"{tgt.get('location',{}).get('lobe','')} {tgt.get('location',{}).get('segment','')}"
        
        row = [
            SOURCE_FILE, NOTE_ID, evt["event_id"], evt["type"], evt.get("method",""),
            loc_str, 
            json.dumps(evt.get("devices_json",[])), 
            "", "", 
            evt.get("counts",""), 
            json.dumps(evt.get("measurements_json",{})), 
            json.dumps(evt.get("specimens_json",[])), 
            json.dumps(evt.get("findings_json",[])),
            "FALSE", "", "",
            "", "", # dev size/mat
            "", "", "", "", # outcomes airway/pleural
            evt.get("outcomes",{}).get("complications","")
        ]
        ws_event.append(row)

    # 6. V3_Procedure_Events
    ws_v3 = wb["V3_Procedure_Events"]
    for evt in EVENTS:
        tgt = evt.get("target", {})
        loc = tgt.get("location", {})
        
        # Columns: note, event_id, type, anat_type, lobe, seg, station, les_type, les_size, method, dev_json, meas_json, spec_json, find_json, quote, stent_size, stent_mat, cath_size, lum_pre, lum_post, symp, pleural, comp
        row = [
            NOTE_ID, evt["event_id"], evt["type"],
            tgt.get("anatomy_type",""), loc.get("lobe",""), loc.get("segment",""), "",
            "", "", # lesion
            evt.get("method",""),
            json.dumps(evt.get("devices_json",[])),
            json.dumps(evt.get("measurements_json",{})),
            json.dumps(evt.get("specimens_json",[])),
            json.dumps(evt.get("findings_json",[])),
            "", # quote
            "", "", "", # stent/cath
            "", "", "", "", # outcomes
            evt.get("outcomes",{}).get("complications","")
        ]
        ws_v3.append(row)

    # 7. V3_Registry_JSON
    ws_json = wb["V3_Registry_JSON"]
    
    # Construct JSON object
    registry_obj = {
        "schema_version": "3.0",
        "note_id": NOTE_ID,
        "no_immediate_complications": False, # Explicitly False due to bleeding
        "procedures": EVENTS
    }
    
    ws_json.append([json.dumps(registry_obj, indent=2)])

    # Save
    wb.save(OUTPUT_PATH)
    print(f"Successfully generated {OUTPUT_PATH}")

if __name__ == "__main__":
    main()