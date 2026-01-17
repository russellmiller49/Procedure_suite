import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3404046
# ==========================================
id_1 = "3404046"
text_1 = """BRONCHIAL THERMOPLASTY NOTE
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | Age: 48F
Attending: Dr. Andrew Miller, MD
Location: [REDACTED]

INDICATION: Severe persistent asthma (FEV1 65%, on high-dose ICS/LABA, omalizumab, history of 3 exacerbations past year). Selected for bronchial thermoplasty after multidisciplinary review.

PROCEDURE: Bronchial thermoplasty - Session 2 of 3 (Left Lower Lobe)

ANESTHESIA: Moderate sedation

PROCEDURE DETAILS:
Using the Alair System (Boston Scientific), bronchial thermoplasty performed in the left lower lobe.

Treatment Sites:
- LB6: 15 activations
- LB7: 8 activations
- LB8: 12 activations
- LB9: 14 activations
- LB10: 11 activations

Total activations: 60

Each activation delivered radiofrequency energy at 18.5 watts for 10 seconds at sequential 5mm intervals per standard protocol.

POST-PROCEDURE: Patient observed for 4 hours. Mild transient chest tightness resolved with bronchodilator. No significant adverse events.

PLAN: Session 3 (RLL) in 3 weeks.

Dr. Andrew Miller, MD"""

entities_1 = [
    # Header & Indication
    {"label": "PROC_ACTION", **get_span(text_1, "BRONCHIAL THERMOPLASTY", 1)},
    {"label": "MEDICATION", **get_span(text_1, "ICS/LABA", 1)},
    {"label": "MEDICATION", **get_span(text_1, "omalizumab", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_1, "history of", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial thermoplasty", 1)},
    
    # Procedure Header
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchial thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Left Lower Lobe", 1)},
    
    # Procedure Details
    {"label": "PROC_METHOD", **get_span(text_1, "Alair System", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial thermoplasty", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "left lower lobe", 1)},
    
    # Treatment Sites (Segments & Counts)
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB6", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "15", 1)}, # 15 activations
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 2)},  # 8 activations (ensure not grabbing digit in date or age if present)
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB8", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "12", 1)}, # 12 activations
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB9", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "14", 1)}, # 14 activations
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB10", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "11", 1)}, # 11 activations
    
    # Totals & Settings
    {"label": "MEAS_COUNT", **get_span(text_1, "60", 1)}, # Total activations
    {"label": "MEAS_ENERGY", **get_span(text_1, "18.5 watts", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "10 seconds", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "5mm", 1)},
    
    # Post-Procedure & Plan
    {"label": "CTX_TIME", **get_span(text_1, "4 hours", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_1, "chest tightness", 1)},
    {"label": "MEDICATION", **get_span(text_1, "bronchodilator", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant adverse events", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)