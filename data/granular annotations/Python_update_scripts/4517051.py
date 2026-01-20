import sys
from pathlib import Path

# Set up repository root (assuming script is run from within the repo or one level deep)
# Adjust if necessary to point to the correct root containing 'scripts'
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add to path to import utility
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 4517051
# ==========================================
id_1 = "4517051"
text_1 = """BRONCHOSCOPY NOTE
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | Age: 45M
Attending: Dr. Nancy Adams, MD
Location: [REDACTED]

INDICATION: Immunocompromised patient (AML s/p allo-HSCT day +45) with new bilateral infiltrates on CT, febrile, hypoxic. BAL for infectious workup.

PROCEDURE: Flexible bronchoscopy with BAL

ANESTHESIA: Moderate sedation (intubated in MICU, FiO2 60%)

PROCEDURE: Bronchoscope advanced via ETT. Airways examined:
- Diffuse mucosal edema and erythema throughout
- Scant mucopurulent secretions
- No endobronchial lesions

BAL performed in RML (area of maximal infiltrate on CT):
- Instilled 150mL sterile saline in 3 aliquots
- Returned 60mL slightly cloudy fluid
- Sent for: Cell count, bacterial/fungal/viral cultures, PCP DFA, CMV PCR, galactomannan, respiratory viral panel, cytology

SPECIMENS: BAL fluid - comprehensive infectious workup

COMPLICATIONS: Transient desaturation to 88% during procedure, resolved with increased FiO2

IMPRESSION: BAL obtained for infectious workup in immunocompromised host. Await results.

Dr. Nancy Adams, MD"""

entities_1 = [
    # Indication Section
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "infiltrates", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    
    # Procedure Header
    {"label": "PROC_METHOD", **get_span(text_1, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},
    
    # Procedure Body
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "edema", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "erythema", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "secretions", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesions", 1)},
    
    # BAL / Intervention Details
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "infiltrate", 1)}, # singular form here
    {"label": "MEAS_VOL", **get_span(text_1, "150mL", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)}, # "3 aliquots"
    {"label": "MEAS_VOL", **get_span(text_1, "60mL", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)}, # "cloudy fluid"
    
    # Specimens Section
    {"label": "SPECIMEN", **get_span(text_1, "BAL fluid", 1)},
    
    # Complications
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_1, "desaturation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "resolved", 1)},
    
    # Impression
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 4)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Processing complete.")