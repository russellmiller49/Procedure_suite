import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to verify path if script is run in a different context
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 927364_syn_1
# ==========================================
text_1 = """Dx: Metastatic melanoma.
Findings: Black nodules Trachea, RMS, LMS.
Action: Biopsies x5.
Plan: Palliative/Onc."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x5", 1)},
]
BATCH_DATA.append({"id": "927364_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 927364_syn_2
# ==========================================
text_2 = """PROCEDURE: Bronchoscopy for evaluation of metastatic disease. The airway examination revealed diffuse endobronchial involvement with multiple pigmented, nodular lesions characteristic of metastatic melanoma within the trachea and bilateral mainstem bronchi. Representative biopsies were secured from multiple sites."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodular lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "trachea", 1)},
    {"label": "LATERALITY", **get_span(text_2, "bilateral", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "mainstem bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
]
BATCH_DATA.append({"id": "927364_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 927364_syn_3
# ==========================================
text_3 = """Code: 31625 (Biopsy). Single code covers multiple biopsies of endobronchial lesions (trachea, RMS, LMS) performed during the same session."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "endobronchial lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "LMS", 1)},
]
BATCH_DATA.append({"id": "927364_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 927364_syn_4
# ==========================================
text_4 = """Resident Note
Pt: C. Brown
Dx: Melanoma
1. LMA/GA.
2. Black nodules seen in trachea/bronchi.
3. Biopsied 5 spots.
4. Bleeding mild.
5. Extubated."""

entities_4 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "LMA", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "5", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Bleeding mild", 1)},
]
BATCH_DATA.append({"id": "927364_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 927364_syn_5
# ==========================================
text_5 = """charles brown metastatic melanoma coughing ct showed nodules went in and saw black spots everywhere trachea mainstems took 5 biopsies to confirm bleeding mild referral to palliative and oncology."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "spots", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "mainstems", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "bleeding mild", 1)},
]
BATCH_DATA.append({"id": "927364_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 927364_syn_6
# ==========================================
text_6 = """General anesthesia via LMA was used. Multiple pigmented nodular lesions consistent with metastatic melanoma were observed in the trachea, RMS, and LMS. Five biopsies were obtained. The airways remained patent despite the disease burden."""

entities_6 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "LMA", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodular lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "LMS", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Five", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "airways remained patent", 1)},
]
BATCH_DATA.append({"id": "927364_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 927364_syn_7
# ==========================================
text_7 = """[Indication]
Metastatic melanoma, cough.
[Anesthesia]
General (LMA).
[Description]
Pigmented nodules in central airways. 5 Biopsies taken. Minimal bleeding.
[Plan]
Palliative care, Immunotherapy evaluation."""

entities_7 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "LMA", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "central airways", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": "927364_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 927364_syn_8
# ==========================================
text_8 = """[REDACTED] for metastatic melanoma. We found multiple dark, nodular lesions throughout his windpipe and main airways. We took five biopsies to confirm the diagnosis. He had mild bleeding but is otherwise stable. We are referring him to oncology and palliative care."""

entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "nodular lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "windpipe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "main airways", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "five", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "mild bleeding", 1)},
]
BATCH_DATA.append({"id": "927364_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 927364_syn_9
# ==========================================
text_9 = """Assessment of metastatic burden. Id[REDACTED] pigmented endobronchial nodules. Sampled lesions in trachea and mainstems. Verified metastatic melanoma visually. Referred for systemic therapy."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "endobronchial nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Sampled", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "mainstems", 1)},
]
BATCH_DATA.append({"id": "927364_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 927364
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Jennifer Wu

Dx: Metastatic melanoma, new cough, CT with multiple endobronchial nodules
Procedure: Bronchoscopy with endobronchial biopsy

General anesthesia via LMA for airway protection given bulky disease. Multiple pigmented nodular lesions seen: 3 in trachea, 4 in RMS, 2 in LMS, 2 in BI, consistent with metastatic melanoma. Representative biopsies from trachea (2), RMS (2), LMS (1). Dark pigmented tissue obtained. Minimal bleeding. Airways remain patent despite diffuse disease.

Medical oncology consulted. Immunotherapy to be considered. Palliative care referral. D/C home.

J. Wu, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "endobronchial biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "LMA", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodular lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "BI", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "(2)", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "(2)", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LMS", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "(1)", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Minimal bleeding", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "Airways remain patent", 1)},
]
BATCH_DATA.append({"id": "927364", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)