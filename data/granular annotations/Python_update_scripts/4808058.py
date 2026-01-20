import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running within the repo structure or allows relative pathing
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve().parent

# Add scripts directory to path to import utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The term to search for.
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4808058
# ==========================================
t1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Christopher Brown

Indication: Malignant pleural effusion - unknown primary
Side: Right

PROCEDURE: Tunneled Pleural Catheter Insertion
Informed consent obtained. Timeout performed.
Patient positioned lateral decubitus, Right side up.
Preprocedure ultrasound confirmed large free-flowing effusion.
Site [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Aspira tunneled pleural catheter kit used.
Subcutaneous tunnel created. Pleural space entered with Seldinger technique.
Catheter advanced and position confirmed. 1905mL straw-colored fluid drained.
Catheter secured with sutures. Sterile dressing applied.
CXR obtained - catheter in good position, lung re-expanded.

DISPOSITION: Home with drainage supplies. Teaching provided.
F/U: Clinic 1-2 weeks, drain PRN for symptoms.

Brown, MD"""

e1 = [
    # [cite_start]Indication: Malignant pleural effusion [cite: 11]
    {"label": "OBS_LESION", **get_span(t1, "effusion", 1)},
    
    # [cite_start]Side: Right [cite: 4]
    {"label": "LATERALITY", **get_span(t1, "Right", 1)},
    
    # [cite_start]PROCEDURE: Tunneled Pleural Catheter [cite: 6]
    {"label": "DEV_CATHETER", **get_span(t1, "Tunneled Pleural Catheter", 1)},
    
    # [cite_start]Patient positioned lateral decubitus, Right side up [cite: 4]
    {"label": "LATERALITY", **get_span(t1, "Right", 2)},
    
    # [cite_start]Preprocedure ultrasound [cite: 10]
    {"label": "PROC_METHOD", **get_span(t1, "ultrasound", 1)},
    
    # [cite_start]confirmed large free-flowing effusion [cite: 11]
    {"label": "OBS_LESION", **get_span(t1, "effusion", 2)},
    
    # [cite_start]Local anesthesia with 1% lidocaine [cite: 21]
    {"label": "MEDICATION", **get_span(t1, "lidocaine", 1)},
    
    # [cite_start]Aspira tunneled pleural catheter [cite: 6]
    {"label": "DEV_CATHETER", **get_span(t1, "Aspira", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "tunneled pleural catheter", 1)},
    
    # [cite_start]Pleural space entered [cite: 3]
    {"label": "ANAT_PLEURA", **get_span(t1, "Pleural space", 1)},
    
    # [cite_start]with Seldinger technique [cite: 10]
    {"label": "PROC_METHOD", **get_span(t1, "Seldinger technique", 1)},
    
    # [cite_start]Catheter advanced [cite: 6]
    {"label": "DEV_CATHETER", **get_span(t1, "Catheter", 1)},
    
    # [cite_start]1905mL straw-colored fluid drained [cite: 8, 22]
    {"label": "MEAS_VOL", **get_span(t1, "1905mL", 1)},
    {"label": "SPECIMEN", **get_span(t1, "fluid", 1)},
    
    # [cite_start]Catheter secured [cite: 6]
    {"label": "DEV_CATHETER", **get_span(t1, "Catheter", 2)},
    
    # [cite_start]CXR obtained [cite: 10]
    {"label": "PROC_METHOD", **get_span(t1, "CXR", 1)},
    
    # [cite_start]catheter in good position [cite: 6]
    {"label": "DEV_CATHETER", **get_span(t1, "catheter", 1)},
    
    # [cite_start]lung re-expanded [cite: 16]
    {"label": "OUTCOME_PLEURAL", **get_span(t1, "lung re-expanded", 1)}
]

BATCH_DATA.append({"id": "4808058", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)