import sys
from pathlib import Path

# Set the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure this script is run from a location where 'scripts' is a sibling or in python path
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search.
        term (str): The term to find.
        occurrence (int): The 1-based occurrence number.
        
    Returns:
        dict: A dictionary containing 'start' and 'end' indices.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1701625_syn_1
# ==========================================
id_1 = "1701625_syn_1"
t1 = """Indication: ILD diagnosis.
Proc: Cryobiopsy RLL.
Steps: REBUS checked path. Cryoprobe 2.4mm. 5 samples taken (6s freeze). Blocker used for hemostasis.
Result: Adequate tissue. No PTX."""
e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "ILD", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "REBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Cryoprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "2.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "6s", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Blocker", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No PTX", 1)},
]
BATCH_DATA.append({"id": id_1, "text": t1, "entities": e1})

# ==========================================
# Note 2: 1701625_syn_2
# ==========================================
id_2 = "1701625_syn_2"
t2 = """PROCEDURE: Transbronchial cryobiopsy for interstitial lung disease.
TECHNIQUE: The bronchoscope was advanced to the right lower lobe. Radial EBUS was utilized to ensure a vessel-free biopsy path. The cryoprobe was positioned, and five transbronchial biopsies were obtained using a 6-second freeze time. Prophylactic balloon occlusion (Arndt blocker) was used after each biopsy to ensure hemostasis."""
e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Transbronchial cryobiopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "interstitial lung disease", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "right lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "five", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial biopsies", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "6-second", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "balloon", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Arndt blocker", 1)},
]
BATCH_DATA.append({"id": id_2, "text": t2, "entities": e2})

# ==========================================
# Note 3: 1701625_syn_3
# ==========================================
id_3 = "1701625_syn_3"
t3 = """Codes: 31628 (Transbronchial lung biopsy, single lobe), 31654 (Radial EBUS).
Details: Cryoprobe used for parenchymal sampling of RLL. Radial EBUS used for guidance/safety. Endobronchial blocker used for bleed control."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Transbronchial lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Cryoprobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Endobronchial blocker", 1)},
]
BATCH_DATA.append({"id": id_3, "text": t3, "entities": e3})

# ==========================================
# Note 4: 1701625_syn_4
# ==========================================
id_4 = "1701625_syn_4"
t4 = """Procedure: Cryobiopsy.
Steps:
1. GA/ETT.
2. Nav to RLL.
3. REBUS check.
4. Cryo activation x5.
5. Balloon blocker up.
Samples sent for histopath."""
e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "REBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon blocker", 1)},
]
BATCH_DATA.append({"id": id_4, "text": t4, "entities": e4})

# ==========================================
# Note 5: 1701625_syn_5
# ==========================================
id_5 = "1701625_syn_5"
t5 = """bronch for ild... went to the rll used the radial ebus to check for vessels... took 5 cryo biopsies with the freezer... used the balloon to stop bleeding worked well... samples look good size... cxr clear."""
e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bronch", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "ild", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rll", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "radial ebus", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "cryo biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "balloon", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "cxr clear", 1)},
]
BATCH_DATA.append({"id": id_5, "text": t5, "entities": e5})

# ==========================================
# Note 6: 1701625_syn_6
# ==========================================
id_6 = "1701625_syn_6"
t6 = """PT: [REDACTED], K. DX: ILD. PROC: Bronch w/ transbronchial cryobiopsy RLL. REBUS to RLL lateral basal. 2.4mm cryoprobe. Freeze 6sec x 5 samples. Arndt blocker utilized. Samples 5-8mm. Minimal bleeding. No PTX. IMP: Successful cryobx."""
e6 = [
    {"label": "OBS_FINDING", **get_span(t6, "ILD", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "transbronchial cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "REBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL lateral basal", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "2.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "cryoprobe", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "6sec", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Arndt blocker", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "5-8mm", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "Minimal bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No PTX", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "cryobx", 1)},
]
BATCH_DATA.append({"id": id_6, "text": t6, "entities": e6})

# ==========================================
# Note 7: 1701625_syn_7
# ==========================================
id_7 = "1701625_syn_7"
t7 = """[Indication]
ILD, tissue dx needed.
[Anesthesia]
General.
[Description]
RLL targeted. REBUS guidance. Cryobiopsy x5. Hemostasis w/ blocker. No complications.
[Plan]
Pathology pending."""
e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "ILD", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Cryobiopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "blocker", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "No complications", 1)},
]
BATCH_DATA.append({"id": id_7, "text": t7, "entities": e7})

# ==========================================
# Note 8: 1701625_syn_8
# ==========================================
id_8 = "1701625_syn_8"
t8 = """[REDACTED] a cryobiopsy to evaluate her interstitial lung disease. We targeted the right lower lobe, using radial EBUS to ensure safety. Five large biopsies were taken using the cryoprobe. Bleeding was controlled with a balloon blocker. Post-procedure imaging ruled out pneumothorax."""
e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "cryobiopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "interstitial lung disease", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "Five", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "cryoprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "balloon blocker", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "ruled out pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_8, "text": t8, "entities": e8})

# ==========================================
# Note 9: 1701625_syn_9
# ==========================================
id_9 = "1701625_syn_9"
t9 = """DX: ILD, UIP pattern on imaging, needs tissue dx. PROC: Bronch w/ transbronchial cryobiopsy RLL (CPT 31632). MEDS: Propofol, fent, roc for intubation. SCOPE FINDINGS: Airways clear, no endo lesions."""
e9 = [
    {"label": "OBS_FINDING", **get_span(t9, "ILD", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "UIP pattern", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "transbronchial cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RLL", 1)},
    {"label": "MEDICATION", **get_span(t9, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(t9, "fent", 1)},
    {"label": "MEDICATION", **get_span(t9, "roc", 1)},
]
BATCH_DATA.append({"id": id_9, "text": t9, "entities": e9})

# ==========================================
# Note 10: 1701625
# ==========================================
id_10 = "1701625"
t10 = """PT: [REDACTED], K | 64F | #1701625
DT: [REDACTED]
MD: R. Johnson
DX: ILD, UIP pattern on imaging, needs tissue dx
PROC: Bronch w/ transbronchial cryobiopsy RLL (CPT 31632)
MEDS: Propofol, fent, roc for intubation
SCOPE FINDINGS:
Airways clear, no endo lesions
TECHNIQUE:

REBUS to RLL lateral basal - no vessels in path
2.4mm cryoprobe advanced to target area
Freeze 6sec x 5 samples total
Arndt blocker inflated 8cc RLL after each, held 3min each time
Samples good size (5-8mm each)
Minimal bleeding, all stopped with blocker

SAMPLES:

5 cryo specimens → histology (ILD protocol)

COMP: None, no PTX on fluoro
DISPO: Extubate, recovery, CXR, d/c if CXR clear
IMP: Successful cryobx. Await path. F/u 1wk."""
e10 = [
    {"label": "OBS_FINDING", **get_span(t10, "ILD", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "UIP pattern", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "transbronchial cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 1)},
    {"label": "MEDICATION", **get_span(t10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(t10, "fent", 1)},
    {"label": "MEDICATION", **get_span(t10, "roc", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "REBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL lateral basal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "cryoprobe", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "6sec", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Arndt blocker", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 3)},
    {"label": "MEAS_TIME", **get_span(t10, "3min", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "5-8mm", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Minimal bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "blocker", 2)},
    {"label": "MEAS_COUNT", **get_span(t10, "5", 2)},
    {"label": "SPECIMEN", **get_span(t10, "cryo specimens", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no PTX", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "cryobx", 1)},
]
BATCH_DATA.append({"id": id_10, "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)