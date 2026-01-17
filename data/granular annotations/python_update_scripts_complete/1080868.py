import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running within the directory structure of the project
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the system path to allow importing the utility function
sys.path.append(str(REPO_ROOT))

# Import the utility function to add the case to the training set
from scripts.add_training_case import add_case

# Define the container for the batch data
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    
    Args:
        text (str): The text to search within.
        term (str): The term to find.
        occurrence (int): The specific occurrence to find (1-based index).
        
    Returns:
        dict: A dictionary containing 'start' and 'end' indices.
    """
    start_index = -1
    current_occurrence = 0
    
    while current_occurrence < occurrence:
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
        current_occurrence += 1
        
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 1080868
# ==========================================
id_1 = "1080868"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: CDR Patricia Davis, MD

Indication: Malignant pleural effusion - NSCLC
Side: Right

PROCEDURE: Tunneled Pleural Catheter Insertion
Informed consent obtained. Timeout performed.
Patient positioned lateral decubitus, Right side up.
Preprocedure ultrasound confirmed large free-flowing effusion.
Site [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Rocket tunneled pleural catheter kit used.
Subcutaneous tunnel created. Pleural space entered with Seldinger technique.
Catheter advanced and position confirmed. 2055mL serosanguinous fluid drained.
Catheter secured with sutures. Sterile dressing applied.
CXR obtained - catheter in good position, lung re-expanded.

DISPOSITION: Home with drainage supplies. Teaching provided.
F/U: Clinic 1-2 weeks, drain PRN for symptoms.

Davis, MD"""

entities_1 = [
    # Indication: Malignant pleural effusion - NSCLC
    {"label": "OBS_LESION", **get_span(text_1, "Malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    
    # Side: Right
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},
    
    # PROCEDURE: Tunneled Pleural Catheter Insertion
    {"label": "DEV_CATHETER", **get_span(text_1, "Tunneled Pleural Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Insertion", 1)},
    
    # Patient positioned lateral decubitus, Right side up.
    {"label": "LATERALITY", **get_span(text_1, "Right", 2)},
    
    # Preprocedure ultrasound confirmed large free-flowing effusion.
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 2)}, # (2nd occurrence, 1st is in Indication line)
    
    # Local anesthesia with 1% lidocaine.
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    
    # Rocket tunneled pleural catheter kit used.
    {"label": "DEV_CATHETER", **get_span(text_1, "Rocket tunneled pleural catheter", 1)},
    
    # Pleural space entered with Seldinger technique.
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleural space", 1)},
    
    # Catheter advanced and position confirmed. 2055mL serosanguinous fluid drained.
    # Note: 1st "Catheter" is in the procedure title. This is the 2nd capitalized instance.
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)},
    {"label": "MEAS_VOL", **get_span(text_1, "2055mL", 1)},
    
    # Catheter secured with sutures.
    # Note: This is the 3rd capitalized instance.
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 3)},
    
    # CXR obtained - catheter in good position, lung re-expanded.
    # Note: 1st lowercase "catheter" is in "Rocket tunneled...". This is the 2nd lowercase instance.
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 2)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "lung re-expanded", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)