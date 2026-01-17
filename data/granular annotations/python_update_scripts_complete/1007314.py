import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 1007314
# ==========================================
id_1 = "1007314"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 62yo female here for bronch w EBUS staging and robotic biopsy of a 21.6mm RUL nodule that was ground-glass on CT, bronchus sign was negative, no PET done.

under general we did linear EBUS first using the Fujifilm EB-580S scope with 22g needle and sampled stations 10L x3, 4L x2, 11L x2, ROSE was there and showed Malignant - NSCLC NOS at multiple stations.

then switched to Ion robot and navigated to the RUL anterior (B3) lesion, registration was 1.8mm which is fine, got radial EBUS showing eccentric view and did tool in lesion confirmation with cbct. took 8 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Granuloma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Robert Patel md
ip attending"""

entities_1 = [
    # Segment 1: "bronch w EBUS staging and robotic biopsy"
    {"label": "PROC_METHOD", **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    
    # Segment 2: "21.6mm RUL nodule"
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    
    # Segment 3: "ground-glass"
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    
    # Segment 4: "linear EBUS first using the Fujifilm EB-580S scope"
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S scope", 1)},
    
    # Segment 5: "22g needle"
    {"label": "DEV_NEEDLE", **get_span(text_1, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)}, # "needle" is also a keyword, but usually we prefer the specific size. 
                                                                # However, "needle" is part of the phrase "22g needle". 
                                                                # "22g" maps to DEV_NEEDLE. "needle" is generic.
                                                                # Looking at later "needle passes", "needle" is used alone. 
                                                                # I will stick to "22g" here as the primary definition.
    
    # Segment 6: "sampled stations 10L x3, 4L x2, 11L x2"
    {"label": "PROC_ACTION", **get_span(text_1, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 2)},
    
    # Segment 7: "ROSE ... Malignant - NSCLC NOS"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Segment 8: "Ion robot"
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robot", 1)},
    
    # Segment 9: "RUL anterior (B3) lesion"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    
    # Segment 10: "radial EBUS"
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    
    # Segment 11: "cbct"
    {"label": "PROC_METHOD", **get_span(text_1, "cbct", 1)},
    
    # Segment 12: "8 forceps bx"
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    
    # Segment 13: "4 needle passes"
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)}, # Matches "4" before needle
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)}, # Second occurrence of "needle" in text
    
    # Segment 14: "brushings x2"
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 3)},
    
    # Segment 15: "BAL"
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    
    # Segment 16: "ROSE from the nodule was Granuloma"
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    
    # Segment 17: Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    
    # Segment 18: Specimens
    {"label": "SPECIMEN", **get_span(text_1, "cyto", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical path", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "flow", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "molecular", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)