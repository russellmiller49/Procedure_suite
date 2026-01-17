import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

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
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 881204_syn_1
# ==========================================
text_1 = """BT Session 3. RUL and LUL. 62 activations total. No complications."""
entities_1 = [
    {"label": "PROC_ACTION",          **get_span(text_1, "BT", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_1, "LUL", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_1, "62", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
]
BATCH_DATA.append({"id": "881204_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 881204_syn_2
# ==========================================
text_2 = """[REDACTED] third and final session of bronchial thermoplasty. The Alair catheter was systematically deployed in the RUL and LUL. A total of 62 radiofrequency activations were delivered to the distal airways, completing the treatment protocol."""
entities_2 = [
    {"label": "PROC_ACTION",    **get_span(text_2, "bronchial thermoplasty", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_2, "Alair catheter", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "LUL", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_2, "62", 1)},
]
BATCH_DATA.append({"id": "881204_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 881204_syn_3
# ==========================================
text_3 = """CPT 31661: Bronchoscopy with bronchial thermoplasty, 2 or more lobes. RUL (30 activations) and LUL (32 activations) treated in this session."""
entities_3 = [
    {"label": "PROC_ACTION",    **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3, "bronchial thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_3, "RUL", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_3, "30", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_3, "LUL", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_3, "32", 1)},
]
BATCH_DATA.append({"id": "881204_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 881204_syn_4
# ==========================================
text_4 = """Procedure: Bronchial Thermoplasty. Target: RUL/LUL. Steps: 1. GA. 2. Alair catheter checked. 3. RUL treated. 4. LUL treated. 5. Total 62 activations. 6. Extubated."""
entities_4 = [
    {"label": "PROC_ACTION",    **get_span(text_4, "Bronchial Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "LUL", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_4, "Alair catheter", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "LUL", 2)},
    {"label": "MEAS_COUNT",     **get_span(text_4, "62", 1)},
]
BATCH_DATA.append({"id": "881204_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 881204_syn_5
# ==========================================
text_5 = """3rd thermoplasty session for sarah did the upper lobes today rul and lul lots of activations 62 total she did fine no issues with the airway extubated in room."""
entities_5 = [
    {"label": "PROC_ACTION",          **get_span(text_5, "thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_5, "upper lobes", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_5, "rul", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_5, "lul", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_5, "62", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no issues with the airway", 1)},
]
BATCH_DATA.append({"id": "881204_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 881204_syn_6
# ==========================================
text_6 = """Bronchial thermoplasty session 3 performed under general anesthesia. The right upper lobe and left upper lobe were treated with the Alair catheter. A total of 62 activations were delivered. The patient tolerated the procedure well."""
entities_6 = [
    {"label": "PROC_ACTION",          **get_span(text_6, "Bronchial thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_6, "right upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_6, "left upper lobe", 1)},
    {"label": "DEV_CATHETER",         **get_span(text_6, "Alair catheter", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_6, "62", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "patient tolerated the procedure well", 1)},
]
BATCH_DATA.append({"id": "881204_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 881204_syn_7
# ==========================================
text_7 = """[Indication] Asthma. [Anesthesia] General. [Description] BT to RUL/LUL. 62 activations. [Plan] Discharge."""
entities_7 = [
    {"label": "PROC_ACTION",    **get_span(text_7, "BT", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "LUL", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_7, "62", 1)},
]
BATCH_DATA.append({"id": "881204_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 881204_syn_8
# ==========================================
text_8 = """We performed the final thermoplasty session for [REDACTED]. We targeted both upper lobes this time. We delivered a series of activations to the RUL and then the LUL, totaling 62. The patient woke up well."""
entities_8 = [
    {"label": "PROC_ACTION",    **get_span(text_8, "thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_8, "upper lobes", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_8, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_8, "LUL", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_8, "62", 1)},
]
BATCH_DATA.append({"id": "881204_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 881204_syn_9
# ==========================================
text_9 = """Bronchial thermal ablation, session 3. Radiofrequency energy was applied to the RUL and LUL airways. 62 applications were performed."""
entities_9 = [
    {"label": "PROC_ACTION",    **get_span(text_9, "Bronchial thermal ablation", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_9, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_9, "LUL", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_9, "62", 1)},
]
BATCH_DATA.append({"id": "881204_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 881204 (Original)
# ==========================================
text_10 = """PROCEDURE: Bronchial Thermoplasty (Session 3 of 3)
DATE: [REDACTED]
PATIENT: [REDACTED] (MRN: [REDACTED])
PHYSICIAN: Dr. T. Dyson

INDICATION: Severe refractory asthma.

PROCEDURE: 
General anesthesia. ETT #8.0.
Alair Catheter used.
Target: Bilateral Upper Lobes (RUL and LUL).

Right Upper Lobe:
- Apical: 8 activations
- Posterior: 10 activations
- Anterior: 12 activations

Left Upper Lobe:
- Apical-Posterior: 18 activations
- Anterior: 14 activations
- Lingula: Not treated (treated in session 2)

Total activations: 62. 
Patient [REDACTED]. No pneumothorax. Extubated to recovery."""
entities_10 = [
    {"label": "PROC_ACTION",          **get_span(text_10, "Bronchial Thermoplasty", 1)},
    {"label": "DEV_INSTRUMENT",       **get_span(text_10, "ETT", 1)},
    {"label": "MEAS_SIZE",            **get_span(text_10, "8.0", 1)},
    {"label": "DEV_CATHETER",         **get_span(text_10, "Alair Catheter", 1)},
    {"label": "LATERALITY",           **get_span(text_10, "Bilateral", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Upper Lobes", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Right Upper Lobe", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Apical", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_10, "8", 2)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Posterior", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_10, "10", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Anterior", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_10, "12", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Left Upper Lobe", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Apical-Posterior", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_10, "18", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Anterior", 2)},
    {"label": "MEAS_COUNT",           **get_span(text_10, "14", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(text_10, "Lingula", 1)},
    {"label": "MEAS_COUNT",           **get_span(text_10, "62", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No pneumothorax", 1)},
]
BATCH_DATA.append({"id": "881204", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)