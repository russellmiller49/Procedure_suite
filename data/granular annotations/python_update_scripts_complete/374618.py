import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure 'scripts.add_training_case' is in your python path
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a case-sensitive term.
    
    Args:
        text (str): The text to search within.
        term (str): The exact substring to find.
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 374618_syn_1
# ==========================================
t1 = """Dx: HIV, KS.
Findings: Violaceous plaques Trachea, RMS, LMS.
Procedure: Biopsies RMS x2, LMS x2. BAL LLL.
Plan: ART optimization."""
e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Violaceous plaques", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "RMS", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "x2", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "LMS", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "x2", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL", 1)},
]
BATCH_DATA.append({"id": "374618_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 374618_syn_2
# ==========================================
t2 = """CLINICAL SUMMARY: Patient with HIV (CD4 120) and suspected pulmonary Kaposi sarcoma. Endoscopic examination revealed multiple characteristic violaceous, raised plaques distributed throughout the trachea and mainstem bronchi. Diagnostic biopsies were obtained from the right and left mainstems. A bronchial wash was performed in the LLL to rule out opportunistic infection (PCP)."""
e2 = [
    {"label": "OBS_LESION", **get_span(t2, "violaceous, raised plaques", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "mainstem bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "LATERALITY", **get_span(t2, "right", 1)},
    {"label": "LATERALITY", **get_span(t2, "left", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "mainstems", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "bronchial wash", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LLL", 1)},
]
BATCH_DATA.append({"id": "374618_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 374618_syn_3
# ==========================================
t3 = """Coding: 31625 (Biopsy). Multiple biopsies taken from separate sites (RMS, LMS) map to single CPT 31625. 31622 (Wash) is bundled. Indication is diagnosis of endobronchial lesions in immunocompromised host."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Wash", 1)},
    {"label": "OBS_LESION", **get_span(t3, "endobronchial lesions", 1)},
]
BATCH_DATA.append({"id": "374618_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 374618_syn_4
# ==========================================
t4 = """Resident Note
Pt: T. Nguyen
Findings: Purple lesions everywhere (Trachea, RMS, LMS).
Action:
- Biopsy RMS x2
- Biopsy LMS x2
- Wash LLL (PCP check)
 bleeding mild."""
e4 = [
    {"label": "OBS_LESION", **get_span(t4, "Purple lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "RMS", 2)},
    {"label": "MEAS_COUNT", **get_span(t4, "x2", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "LMS", 2)},
    {"label": "MEAS_COUNT", **get_span(t4, "x2", 2)},
    {"label": "PROC_ACTION", **get_span(t4, "Wash", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LLL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "bleeding mild", 1)},
]
BATCH_DATA.append({"id": "374618_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 374618_syn_5
# ==========================================
t5 = """[REDACTED] positive checking for ks saw purple spots all over trachea and mainstems took biopsies from right and left sides also washed the lll for pcp check bleeding wasn't bad oncology and id to follow up."""
e5 = [
    {"label": "OBS_LESION", **get_span(t5, "purple spots", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "mainstems", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "LATERALITY", **get_span(t5, "right", 1)},
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "washed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lll", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "bleeding wasn't bad", 1)},
]
BATCH_DATA.append({"id": "374618_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 374618_syn_6
# ==========================================
t6 = """Moderate sedation with propofol was used. Multiple violaceous raised plaques consistent with Kaposi sarcoma were noted in the trachea and bilateral mainstems. Biopsies were taken from the RMS and LMS. A bronchial wash was performed in the LLL. The patient tolerated the procedure well."""
e6 = [
    {"label": "MEDICATION", **get_span(t6, "propofol", 1)},
    {"label": "OBS_LESION", **get_span(t6, "violaceous raised plaques", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "trachea", 1)},
    {"label": "LATERALITY", **get_span(t6, "bilateral", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "mainstems", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "bronchial wash", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LLL", 1)},
]
BATCH_DATA.append({"id": "374618_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 374618_syn_7
# ==========================================
t7 = """[Indication]
HIV+, pulmonary lesions.
[Anesthesia]
Propofol infusion.
[Description]
Violaceous plaques id[REDACTED]. Biopsies: RMS, LMS. Wash: LLL. Minimal bleeding.
[Plan]
ID/Oncology follow-up. ART optimization."""
e7 = [
    {"label": "OBS_LESION", **get_span(t7, "pulmonary lesions", 1)},
    {"label": "MEDICATION", **get_span(t7, "Propofol", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Violaceous plaques", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Wash", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LLL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": "374618_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 374618_syn_8
# ==========================================
t8 = """[REDACTED] a bronchoscopy due to his history of HIV and lung lesions. We saw purple plaques typical of Kaposi sarcoma in his windpipe and main airways. We biopsied lesions on both the right and left sides and did a wash in the lower lung to check for infections. He is discharged to follow up with his specialists."""
e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lung lesions", 1)},
    {"label": "OBS_LESION", **get_span(t8, "purple plaques", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "windpipe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "main airways", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsied", 1)},
    {"label": "LATERALITY", **get_span(t8, "right", 1)},
    {"label": "LATERALITY", **get_span(t8, "left", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "wash", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "lower lung", 1)},
]
BATCH_DATA.append({"id": "374618_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 374618_syn_9
# ==========================================
t9 = """Assessment for Kaposi sarcoma. Executed bronchoscopy. Observed violaceous plaques. Sampled tissue from bilateral mainstems. Lavaged LLL for infectious etiology. Minimal hemorrhage."""
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "violaceous plaques", 1)},
    {"label": "LATERALITY", **get_span(t9, "bilateral", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "mainstems", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Lavaged", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LLL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "Minimal hemorrhage", 1)},
]
BATCH_DATA.append({"id": "374618_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 374618
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Elizabeth Foster

Dx: HIV+ (CD4 120), multiple pulmonary Kaposi sarcoma lesions
Procedure: Bronchoscopy with endobronchial biopsy, bronchial wash

Moderate sedation with propofol infusion. Standard bronchoscopy. Multiple violaceous raised plaques noted: 2 in trachea, 3 in RMS, 2 in LMS, consistent with endobronchial KS. Representative biopsies taken from RMS (2) and LMS (2) lesions. Minimal bleeding. Bronchial wash from LLL for PCP rule-out.

Patient [REDACTED]. ID and oncology aware. D/C with close outpatient f/u. ART optimization planned.

E. Foster, MD"""
e10 = [
    {"label": "OBS_LESION", **get_span(t10, "pulmonary Kaposi sarcoma lesions", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "endobronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchial wash", 1)},
    {"label": "MEDICATION", **get_span(t10, "propofol", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Standard bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "violaceous raised plaques", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RMS", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 3)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(t10, "endobronchial KS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RMS", 2)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 4)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LMS", 2)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 5)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Minimal bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchial wash", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL", 1)},
]
BATCH_DATA.append({"id": "374618", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)