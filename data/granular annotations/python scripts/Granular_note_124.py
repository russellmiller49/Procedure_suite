import openpyxl
from openpyxl.utils import get_column_letter
import datetime
import json
import re
import os

# -------------------------------------------------------------------------
# INPUT DATA
# -------------------------------------------------------------------------
NOTE_ID = "note_124"
SOURCE_FILE = "note_124.txt"
PROCEDURE_DATE = "2026-01-12" # inferred from context or left blank if unknown
TEMPLATE_PATH = "phase0_golden_registry_labeling_worksheet_anchor_first_therapeutic_pleural.xlsx"
OUTPUT_PATH = f"phase0_extraction_{NOTE_ID}.xlsx"

NOTE_TEXT = """NOTE_ID:  note_124 SOURCE_FILE: note_124.txt Pre-operative diagnosis: RLL consolidation

Post-operative diagnosis: SAA

Procedure: Bronchoscopy with EBUS + TBNA + lung biopsy of RLL

CPT Code(s):
CPT 31653 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed with endobronchial ultrasound (EBUS) guided transtracheal and/or transbronchial sampling 3 or more structures.
CPT 31625 Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with bronchial or endobronchial biopsy(s), single or multiple sites
CPT 31628 Bronchoscopy with fluoroscopic guidance for transbronchial lung biopsy(s), single lobe

Bronchoscopes: Olympus H190, convex EBUS

Anesthesia: General per Anesthesia in addition to 6cc of 1% topical lidocaine

Time out: 1349

Scope in: 1350

Scope out: 1501

Estimated blood loss: 5cc

Fluids administered: None

PROCEDURE:

History and physical has been performed.
The risks and benefits of the procedure were discussed with the patient.
All questions were answered and informed consent was obtained.

Patient identification and proposed procedure were verified by the physician, anesthesia team, nurse, and pulmonary team.
The patient was brought to the operating suite. Under general anesthesia, endotracheal tube was placed by anesthesiologist.
The bronchoscope was introduced through an 8.5 endotracheal tube where lidocaine 1% was instilled onto trachea and airways.
The tracheo-bronchial tree was then examined to at least the first subsegmental level.
The endobronchial scope was then advanced in a similar fashion and mediastinal lymph nodes were identified and measured in a systematic fashion (see measurements below).
Transbronchial needle aspiration was performed at enlarged nodal stations with adequate tissue confirmed by ROSE (see sizes below).
Finally, inspection bronchoscopy was performed. 

The procedure was accomplished without difficulty. The patient tolerated the procedure well without immediate complications.
FINDINGS: The vocal cords are normal and move normally with breathing. The subglottic space is normal.
The trachea is of normal caliber. The carina is sharp.
The tracheobronchial tree of bilateral lungs was examined to at least the first subsegmental level.
All segmentals of the RLL appeared significantly stenotic and with nodular mucosa concerning for malignancy.
Mediastinal and hilar lymph nodes were measured and sampled as below.
Node stations and sizes were as follows:

4L - 5.5mm, 4 passes
4R - 6.0mm
7 - 7.5mm, 8 passes
11Rs - 4.9mm

After nodal sampling was completed, forceps were used to biopsy the RLL.
2 samples were taken from the medial segment, 2 samples were taken from the anterior segment and 2 samples were taken from the superior segment.
SPECIMENS SENT TO THE LABORATORY:
--TBNA of 4L node station
--TBNA of 7 node station
-- Forceps Biopsies of the RLL (6 passes)"""

# -------------------------------------------------------------------------
# EXTRACTION LOGIC & MAPPING
# -------------------------------------------------------------------------

# Procedure Flags (0/1)
PROCEDURE_FLAGS = {
    'diagnostic_bronchoscopy': 1,
    'bal': 0,
    'bronchial_wash': 0,
    'brushings': 0,
    'endobronchial_biopsy': 1, # CPT 31625 + nodular mucosa biopsy implied
    'tbna_conventional': 0,
    'linear_ebus': 1, # Convex EBUS used
    'radial_ebus': 0,
    'navigational_bronchoscopy': 0,
    'transbronchial_biopsy': 1, # CPT 31628 + RLL biopsy
    'transbronchial_cryobiopsy': 0,
    'therapeutic_aspiration': 0,
    'foreign_body_removal': 0,
    'airway_dilation': 0,
    'airway_stent': 0,
    'thermal_ablation': 0,
    'tumor_debulking_non_thermal': 0,
    'cryotherapy': 0,
    'blvr': 0,
    'peripheral_ablation': 0,
    'bronchial_thermoplasty': 0,
    'whole_lung_lavage': 0,
    'rigid_bronchoscopy': 0,
    'thoracentesis': 0,
    'chest_tube': 0,
    'ipc': 0,
    'medical_thoracoscopy': 0,
    'pleurodesis': 0,
    'pleural_biopsy': 0,
    'fibrinolytic_therapy': 0
}

# Annotated Spans (Anchor-First)
# Structure: (span_text, label, normalized_value, schema_field, event_id, context_prefix)
SPANS = [
    # Devices
    ("Olympus H190", "DEV_INSTRUMENT", "Olympus H190", "device.brand", "proc_general", None),
    ("convex EBUS", "DEV_INSTRUMENT", "Convex EBUS", "device.type", "proc_ebus", None),
    
    # Event 1: TBNA 4L
    ("4L", "ANAT_LN_STATION", "4L", "target.station", "evt_tbna_4l", "Node stations and sizes were as follows:\n\n"),
    ("5.5mm", "MEAS_SIZE", "5.5", "lesion.size_mm", "evt_tbna_4l", "4L - "),
    ("4 passes", "MEAS_COUNT", "4", "action.count", "evt_tbna_4l", "4L - 5.5mm, "),
    ("TBNA of 4L", "PROC_METHOD", "TBNA", "method", "evt_tbna_4l", None),

    # Event 2: Measurements 4R
    ("4R", "ANAT_LN_STATION", "4R", "target.station", "evt_ebus_4r", "4 passes\n"),
    ("6.0mm", "MEAS_SIZE", "6.0", "lesion.size_mm", "evt_ebus_4r", "4R - "),
    
    # Event 3: TBNA 7
    ("7", "ANAT_LN_STATION", "7", "target.station", "evt_tbna_7", "4R - 6.0mm\n"),
    ("7.5mm", "MEAS_SIZE", "7.5", "lesion.size_mm", "evt_tbna_7", "7 - "),
    ("8 passes", "MEAS_COUNT", "8", "action.count", "evt_tbna_7", "7 - 7.5mm, "),
    ("TBNA of 7", "PROC_METHOD", "TBNA", "method", "evt_tbna_7", None),

    # Event 4: Measurements 11Rs
    ("11Rs", "ANAT_LN_STATION", "11Rs", "target.station", "evt_ebus_11rs", "8 passes\n"),
    ("4.9mm", "MEAS_SIZE", "4.9", "lesion.size_mm", "evt_ebus_11rs", "11Rs - "),

    # Event 5: RLL Biopsy (TBBX + EBBX context)
    ("forceps", "DEV_INSTRUMENT", "Forceps", "device.type", "evt_bx_rll", "After nodal sampling was completed, "),
    ("biopsy the RLL", "PROC_ACTION", "Biopsy", "method", "evt_bx_rll", None),
    ("RLL", "ANAT_LUNG_LOC", "RLL", "target.location.lobe", "evt_bx_rll", "forceps were used to biopsy the "),
    ("medial segment", "ANAT_LUNG_LOC", "RLL Medial Basal", "target.location.segment", "evt_bx_rll", "2 samples were taken from the "),
    ("anterior segment", "ANAT_LUNG_LOC", "RLL Anterior Basal", "target.location.segment", "evt_bx_rll", "2 samples were taken from the "),
    ("superior segment", "ANAT_LUNG_LOC", "RLL Superior", "target.location.segment", "evt_bx_rll", "2 samples were taken from the "),
    ("6 passes", "MEAS_COUNT", "6", "action.count", "evt_bx_rll", "Forceps Biopsies of the RLL ("),
    
    # Findings
    ("significantly stenotic", "OBS_LESION", "Stenosis", "findings.stenosis", "evt_bx_rll", "appeared "),
    ("nodular mucosa", "OBS_LESION", "Nodular Mucosa", "findings.mucosa", "evt_bx_rll", "and with "),

    # Outcome
    ("without immediate complications", "OUTCOME_COMPLICATION", "None", "outcomes.complications", "proc_general", None),
]

# V3 JSON Event Structures
V3_EVENTS = [
    {
        "note_id": NOTE_ID,
        "event_id": "evt_tbna_4l",
        "type": "TBNA",
        "target": {"station": "4L"},
        "lesion": {"size_mm": 5.5},
        "method": "TBNA",
        "measurements_json": {"passes": 4},
        "specimens_json": ["TBNA of 4L"]
    },
    {
        "note_id": NOTE_ID,
        "event_id": "evt_ebus_4r",
        "type": "EBUS",
        "target": {"station": "4R"},
        "lesion": {"size_mm": 6.0},
        "method": "EBUS"
    },
    {
        "note_id": NOTE_ID,
        "event_id": "evt_tbna_7",
        "type": "TBNA",
        "target": {"station": "7"},
        "lesion": {"size_mm": 7.5},
        "method": "TBNA",
        "measurements_json": {"passes": 8},
        "specimens_json": ["TBNA of 7"]
    },
    {
        "note_id": NOTE_ID,
        "event_id": "evt_ebus_11rs",
        "type": "EBUS",
        "target": {"station": "11Rs"},
        "lesion": {"size_mm": 4.9},
        "method": "EBUS"
    },
    {
        "note_id": NOTE_ID,
        "event_id": "evt_bx_rll",
        "type": "Biopsy",
        "target": {
            "location": {
                "lobe": "RLL",
                "segment": ["Medial", "Anterior", "Superior"]
            }
        },
        "method": "Forceps Biopsy",
        "measurements_json": {"passes": 6},
        "findings_json": ["stenotic", "nodular mucosa"],
        "specimens_json": ["Forceps Biopsies of the RLL"]
    }
]

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------

def hydrate_span(text, span_text, context_prefix=None, match_index=None):
    """
    Finds start/end char offsets for a span.
    Logic:
    1. If count == 1, use that.
    2. If context_prefix provided, search for prefix + span within window.
    3. If match_index provided, pick that occurrence.
    4. Fallback: Ambiguous.
    """
    matches = [m.start() for m in re.finditer(re.escape(span_text), text)]
    
    if not matches:
        return None, None, "not_found"
    
    if len(matches) == 1:
        start = matches[0]
        return start, start + len(span_text), "hydrated_unique"
    
    # Context strategy
    if context_prefix:
        # We look for the prefix relatively close to the span
        for m_start in matches:
            # Check 150 chars before
            window_start = max(0, m_start - 150)
            preceding_text = text[window_start:m_start]
            # Clean newlines for easier matching or just simple check
            if context_prefix.strip() in preceding_text or context_prefix in preceding_text:
                return m_start, m_start + len(span_text), "hydrated_context"
    
    # Match index strategy
    if match_index is not None and 0 <= match_index < len(matches):
        start = matches[match_index]
        return start, start + len(span_text), "hydrated_index"
        
    return None, None, f"ambiguous_count={len(matches)}"

# -------------------------------------------------------------------------
# EXECUTION
# -------------------------------------------------------------------------

def main():
    print(f"Loading template from {TEMPLATE_PATH}...")
    try:
        wb = openpyxl.load_workbook(TEMPLATE_PATH)
    except FileNotFoundError:
        print(f"Error: Template {TEMPLATE_PATH} not found.")
        return

    # 1. Note_Text
    ws_text = wb["Note_Text"]
    # Append row: note_id, source_file, note_text
    ws_text.append([NOTE_ID, SOURCE_FILE, NOTE_TEXT])

    # 2. Note_Index
    ws_index = wb["Note_Index"]
    # Construct flag list in order of header (assuming standard order, or mapping explicitly)
    # We will map explicitly based on known header columns if possible, but strict appending is safer if we trust schema.
    # The prompt lists the flags. We'll iterate the flags dictionary.
    
    header_row = [cell.value for cell in ws_index[1]]
    
    # Basic Metadata
    row_data = {
        "source_file": SOURCE_FILE,
        "note_id": NOTE_ID,
        "status": "extracted",
        "procedure_date": PROCEDURE_DATE
    }
    
    # Merge flags into row_data
    row_data.update(PROCEDURE_FLAGS)
    
    # Build the row list matching headers
    new_row = []
    for col in header_row:
        key = col
        if key in row_data:
            new_row.append(row_data[key])
        else:
            new_row.append(None) # Blank for missing
            
    ws_index.append(new_row)

    # 3. Span_Annotations & 4. Span_Hydrated
    ws_span_raw = wb["Span_Annotations"]
    ws_span_hyd = wb["Span_Hydrated"]
    
    for span_def in SPANS:
        span_text, label, norm_val, field, evt_id, ctx = span_def
        
        # Calculate offsets
        start, end, status = hydrate_span(NOTE_TEXT, span_text, context_prefix=ctx)
        length = len(span_text)
        
        # Common data
        # Headers: source_file, note_id, span_id, section_type, context_prefix, span_text, match_index, start, end, len, label, normalized, schema, event, negated, historical, time, reviewer, comments, status
        
        # Raw (Anchor First - no offsets)
        row_raw = [
            SOURCE_FILE, NOTE_ID, f"span_{os.urandom(4).hex()}", "Procedure", ctx, span_text, 
            None, None, None, length, label, norm_val, field, evt_id, 
            False, False, None, "Auto", None, "needs_hydration"
        ]
        ws_span_raw.append(row_raw)
        
        # Hydrated
        row_hyd = [
            SOURCE_FILE, NOTE_ID, f"span_{os.urandom(4).hex()}", "Procedure", ctx, span_text,
            None, start, end, length, label, norm_val, field, evt_id,
            False, False, None, "Auto", None, status
        ]
        ws_span_hyd.append(row_hyd)

    # 5. Event_Log
    ws_event = wb["Event_Log"]
    # Headers: source_file, note_id, event_id, event_type, method, anatomy_target, device, etc.
    # We will populate based on V3_EVENTS for consistency
    for evt in V3_EVENTS:
        target_str = str(evt.get("target", {}))
        method_str = evt.get("method", "")
        # Flat mapping for major columns
        e_row = [
            SOURCE_FILE, NOTE_ID, evt["event_id"], evt.get("type", ""), method_str,
            target_str, 
            str(evt.get("device", "")), # device
            "", # needle
            "", # stations
            str(evt.get("measurements_json", "")), # counts
            "", # measurements
            str(evt.get("specimens_json", "")),
            str(evt.get("findings_json", "")),
            False, "Auto", "", "", "", 
            "", "", "", "", # outcomes
            "" # complication
        ]
        ws_event.append(e_row)

    # 6. V3_Procedure_Events
    ws_v3 = wb["V3_Procedure_Events"]
    # Headers: note_id, event_id, type, target.anatomy_type, target.location.lobe...
    for evt in V3_EVENTS:
        target = evt.get("target", {})
        loc = target.get("location", {})
        lesion = evt.get("lesion", {})

        seg = loc.get("segment", "")
        if isinstance(seg, list):
            seg = "; ".join(map(str, seg))
        
        v3_row = [
            NOTE_ID, evt["event_id"], evt["type"],
            "Lung/Node", # anatomy_type
            loc.get("lobe", ""), seg, target.get("station", ""),
            "Nodule/Node", # lesion type
            lesion.get("size_mm", ""),
            evt.get("method", ""),
            json.dumps(evt.get("devices_json", {})),
            json.dumps(evt.get("measurements_json", {})),
            json.dumps(evt.get("specimens_json", {})),
            json.dumps(evt.get("findings_json", {})),
            "", # quote
            "", "", "", # stent/cath
            "", "", "", "", "" # outcomes
        ]
        ws_v3.append(v3_row)

    # 7. V3_Registry_JSON
    ws_json = wb["V3_Registry_JSON"]
    # schema_version, note_id, full_json, no_complications
    final_obj = {
        "schema_version": "3.0",
        "note_id": NOTE_ID,
        "procedures": V3_EVENTS,
        "no_immediate_complications": True
    }
    ws_json.append(["3.0", NOTE_ID, json.dumps(final_obj, indent=2), True])

    print(f"Saving to {OUTPUT_PATH}...")
    wb.save(OUTPUT_PATH)
    print("Done.")

if __name__ == "__main__":
    main()