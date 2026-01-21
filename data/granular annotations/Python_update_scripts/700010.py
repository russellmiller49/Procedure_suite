import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure your environment is set up such that this import works, 
# or adjust the path logic as needed for your specific repo structure.
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        tuple: (start_index, end_index)
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return start, start + len(term)

# ==========================================
# Note 1: 700010_syn_1
# ==========================================
t1 = "Proc: EBUS (Stn 7) + EM Nav (LLL nodule).\nFindings:\n- EBUS: Stn 7 benign.\n- Nav: LLL lesion, 4 bx taken.\nComp: None.\nPlan: D/C, wait for path."
e1 = [
    {"label": "PROC_METHOD", "span": get_span(t1, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t1, "Stn 7", 1)},
    {"label": "PROC_METHOD", "span": get_span(t1, "EM Nav", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t1, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t1, "nodule", 1)},
    {"label": "PROC_METHOD", "span": get_span(t1, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(t1, "Stn 7", 2)},
    {"label": "OBS_ROSE", "span": get_span(t1, "benign", 1)},
    {"label": "PROC_METHOD", "span": get_span(t1, "Nav", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t1, "LLL", 2)},
    {"label": "OBS_LESION", "span": get_span(t1, "lesion", 1)},
    {"label": "MEAS_COUNT", "span": get_span(t1, "4", 1)},
    {"label": "PROC_ACTION", "span": get_span(t1, "bx", 1)},
]
BATCH_DATA.append({"id": "700010_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 700010_syn_2
# ==========================================
t2 = "PROCEDURE: Flexible bronchoscopy with EBUS-TBNA and electromagnetic navigation.\nINDICATION: 64M with LLL nodule and subcarinal lymphadenopathy.\nDETAILS: EBUS-TBNA of station 7 was performed; ROSE was negative for malignancy. Electromagnetic navigation was then utilized to reach the LLL superior segment nodule. Transbronchial biopsies were obtained under fluoroscopic guidance."
e2 = [
    {"label": "PROC_METHOD", "span": get_span(t2, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", "span": get_span(t2, "EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(t2, "TBNA", 1)},
    {"label": "PROC_METHOD", "span": get_span(t2, "electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t2, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t2, "nodule", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t2, "subcarinal", 1)},
    {"label": "PROC_METHOD", "span": get_span(t2, "EBUS", 2)},
    {"label": "PROC_ACTION", "span": get_span(t2, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(t2, "station 7", 1)},
    {"label": "OBS_ROSE", "span": get_span(t2, "negative", 1)},
    {"label": "PROC_METHOD", "span": get_span(t2, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t2, "LLL superior segment", 1)},
    {"label": "OBS_LESION", "span": get_span(t2, "nodule", 2)},
    {"label": "PROC_ACTION", "span": get_span(t2, "Transbronchial biopsies", 1)},
    {"label": "PROC_METHOD", "span": get_span(t2, "fluoroscopic", 1)},
]
BATCH_DATA.append({"id": "700010_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 700010_syn_3
# ==========================================
t3 = "Codes:\n- 31652: EBUS 1 station (Stn 7).\n- 31627: Navigational guidance.\n- 31628: TBLB single lobe (LLL).\nNote: Only one nodal station sampled, so 31652 is correct (not 31653)."
e3 = [
    {"label": "PROC_METHOD", "span": get_span(t3, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t3, "Stn 7", 1)},
    {"label": "PROC_METHOD", "span": get_span(t3, "Navigational guidance", 1)},
    {"label": "PROC_ACTION", "span": get_span(t3, "TBLB", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t3, "LLL", 1)},
]
BATCH_DATA.append({"id": "700010_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 700010_syn_4
# ==========================================
t4 = "Procedure: EBUS + Nav TBLB\nPatient: [REDACTED]\nSteps:\n1. EBUS Stn 7: 3 passes.\n2. Nav set up. Targeted LLL nodule.\n3. TBLB x4.\n4. Fluoro check.\nBenign ROSE on node. Biopsies sent."
e4 = [
    {"label": "PROC_METHOD", "span": get_span(t4, "EBUS", 1)},
    {"label": "PROC_METHOD", "span": get_span(t4, "Nav", 1)},
    {"label": "PROC_ACTION", "span": get_span(t4, "TBLB", 1)},
    {"label": "PROC_METHOD", "span": get_span(t4, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(t4, "Stn 7", 1)},
    {"label": "MEAS_COUNT", "span": get_span(t4, "3 passes", 1)},
    {"label": "PROC_METHOD", "span": get_span(t4, "Nav", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t4, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t4, "nodule", 1)},
    {"label": "PROC_ACTION", "span": get_span(t4, "TBLB", 2)},
    {"label": "MEAS_COUNT", "span": get_span(t4, "4", 2)}, # "x4" and "4." appear. The text has "TBLB x4." and "4. Fluoro". This targets "4" in "x4".
    {"label": "PROC_METHOD", "span": get_span(t4, "Fluoro", 1)},
    {"label": "OBS_ROSE", "span": get_span(t4, "Benign", 1)},
    {"label": "PROC_ACTION", "span": get_span(t4, "Biopsies", 1)},
]
BATCH_DATA.append({"id": "700010_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 700010_syn_5
# ==========================================
t5 = "Mr [REDACTED] here for the LLL nodule. Checked the subcarinal node first with EBUS it looked benign but we sampled it anyway. Then used the navigation to get out to the lung lesion. Took 4 biopsies. No bleeding. Extubated fine."
e5 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(t5, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t5, "nodule", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t5, "subcarinal node", 1)},
    {"label": "PROC_METHOD", "span": get_span(t5, "EBUS", 1)},
    {"label": "OBS_ROSE", "span": get_span(t5, "benign", 1)},
    {"label": "PROC_ACTION", "span": get_span(t5, "sampled", 1)},
    {"label": "PROC_METHOD", "span": get_span(t5, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t5, "lung", 1)},
    {"label": "OBS_LESION", "span": get_span(t5, "lesion", 1)},
    {"label": "MEAS_COUNT", "span": get_span(t5, "4", 1)},
    {"label": "PROC_ACTION", "span": get_span(t5, "biopsies", 1)},
]
BATCH_DATA.append({"id": "700010_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 700010_syn_6
# ==========================================
t6 = "EBUS-TBNA of station 7 (benign on ROSE) followed by electromagnetic navigational bronchoscopy to LLL superior segment nodule. Transbronchial biopsies obtained. No complications."
e6 = [
    {"label": "PROC_METHOD", "span": get_span(t6, "EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(t6, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t6, "station 7", 1)},
    {"label": "OBS_ROSE", "span": get_span(t6, "benign", 1)},
    {"label": "PROC_METHOD", "span": get_span(t6, "electromagnetic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t6, "LLL superior segment", 1)},
    {"label": "OBS_LESION", "span": get_span(t6, "nodule", 1)},
    {"label": "PROC_ACTION", "span": get_span(t6, "Transbronchial biopsies", 1)},
]
BATCH_DATA.append({"id": "700010_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 700010_syn_7
# ==========================================
t7 = "[Indication]\nLLL nodule, station 7 lymphadenopathy.\n[Anesthesia]\nGeneral.\n[Description]\nEBUS-TBNA station 7. EM navigation to LLL nodule. Transbronchial biopsies.\n[Plan]\nOutpatient follow-up."
e7 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(t7, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t7, "nodule", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t7, "station 7", 1)},
    {"label": "PROC_METHOD", "span": get_span(t7, "EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(t7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t7, "station 7", 2)},
    {"label": "PROC_METHOD", "span": get_span(t7, "EM navigation", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t7, "LLL", 2)},
    {"label": "OBS_LESION", "span": get_span(t7, "nodule", 2)},
    {"label": "PROC_ACTION", "span": get_span(t7, "Transbronchial biopsies", 1)},
]
BATCH_DATA.append({"id": "700010_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 700010_syn_8
# ==========================================
t8 = "We performed a bronchoscopy on [REDACTED] his LLL nodule and a nearby lymph node. The EBUS sample of the lymph node (station 7) appeared benign. We then navigated to the lung nodule using the electromagnetic system and took four biopsies to determine its nature."
e8 = [
    {"label": "PROC_METHOD", "span": get_span(t8, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t8, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t8, "nodule", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t8, "lymph node", 1)},
    {"label": "PROC_METHOD", "span": get_span(t8, "EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(t8, "sample", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t8, "lymph node", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(t8, "station 7", 1)},
    {"label": "OBS_ROSE", "span": get_span(t8, "benign", 1)},
    {"label": "PROC_METHOD", "span": get_span(t8, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t8, "lung", 1)},
    {"label": "OBS_LESION", "span": get_span(t8, "nodule", 2)},
    {"label": "PROC_METHOD", "span": get_span(t8, "electromagnetic system", 1)},
    {"label": "MEAS_COUNT", "span": get_span(t8, "four", 1)},
    {"label": "PROC_ACTION", "span": get_span(t8, "biopsies", 1)},
]
BATCH_DATA.append({"id": "700010_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 700010_syn_9
# ==========================================
t9 = "Procedure: Sonographic nodal sampling and guided lung biopsy.\nTarget: Station 7 and LLL lesion.\nAction: The subcarinal node was aspirated. The lung nodule was localized via navigation and biopsied.\nOutcome: Samples to pathology."
e9 = [
    {"label": "PROC_METHOD", "span": get_span(t9, "Sonographic", 1)},
    {"label": "PROC_ACTION", "span": get_span(t9, "sampling", 1)},
    {"label": "PROC_METHOD", "span": get_span(t9, "guided", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t9, "lung", 1)},
    {"label": "PROC_ACTION", "span": get_span(t9, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t9, "Station 7", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t9, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t9, "lesion", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t9, "subcarinal node", 1)},
    {"label": "PROC_ACTION", "span": get_span(t9, "aspirated", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t9, "lung", 2)},
    {"label": "OBS_LESION", "span": get_span(t9, "nodule", 1)},
    {"label": "PROC_METHOD", "span": get_span(t9, "navigation", 1)},
    {"label": "PROC_ACTION", "span": get_span(t9, "biopsied", 1)},
]
BATCH_DATA.append({"id": "700010_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 700010
# ==========================================
t10 = "PATIENT: [REDACTED]\nMRN: [REDACTED]\nDOB: [REDACTED] (64 years)\nDATE OF SERVICE: [REDACTED]\nLOCATION: Bronchoscopy Suite\n\nPROCEDURES:\n1. Flexible bronchoscopy with transbronchial lung biopsy (TBLB), left lower lobe.\n2. Electromagnetic navigational bronchoscopy to left lower lobe lesion.\n3. Linear EBUS-TBNA of station 7.\n\nOPERATOR: Karen Lee, MD (Interventional Pulmonology)\n\nINDICATION:\n64-year-old male with a 2.0 cm left lower lobe superior segment nodule and mildly enlarged subcarinal lymph node (station 7). PET shows moderate uptake in both sites. Combined nodal and parenchymal sampling requested.\n\nPROCEDURE SUMMARY:\nUnder general anesthesia via ETT, a flexible bronchoscope was passed to the segmental bronchi. No endobronchial tumor was seen.\n\nEBUS-TBNA (station 7):\nA convex EBUS scope was used to sample a 1.4 cm subcarinal node. Three passes were performed with a 22G needle. ROSE was adequate with benign-appearing lymphocytes.\n\nEM NAVIGATION + TBLB (LLL superior segment):\nAn EM navigation system was used to register the pre-procedure CT. The lesion in the LLL superior segment was targeted; registration error ~3 mm. The scope was advanced to the LLL superior segment, and navigation confirmed proximity to the lesion. Fluoroscopy confirmed the biopsy forceps at the lesion margin. Four transbronchial biopsies were obtained; specimens were sent for histology and molecular studies.\n\nNo significant bleeding or hypoxia occurred. The patient was extubated and transferred to PACU in stable condition.\n\nIMPRESSION:\nCombined EM-navigated transbronchial biopsies of LLL lesion and single-station EBUS-TBNA of station 7 for staging."
e10 = [
    {"label": "PROC_METHOD", "span": get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", "span": get_span(t10, "transbronchial lung biopsy", 1)},
    {"label": "PROC_ACTION", "span": get_span(t10, "TBLB", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "left lower lobe", 1)},
    {"label": "PROC_METHOD", "span": get_span(t10, "Electromagnetic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "left lower lobe", 2)},
    {"label": "OBS_LESION", "span": get_span(t10, "lesion", 1)},
    {"label": "PROC_METHOD", "span": get_span(t10, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(t10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t10, "station 7", 1)},
    {"label": "MEAS_SIZE", "span": get_span(t10, "2.0 cm", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "left lower lobe superior segment", 1)},
    {"label": "OBS_LESION", "span": get_span(t10, "nodule", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t10, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t10, "station 7", 2)},
    {"label": "PROC_ACTION", "span": get_span(t10, "sampling", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(t10, "flexible bronchoscope", 1)},
    {"label": "PROC_METHOD", "span": get_span(t10, "EBUS", 2)},
    {"label": "PROC_ACTION", "span": get_span(t10, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(t10, "station 7", 3)},
    {"label": "DEV_INSTRUMENT", "span": get_span(t10, "convex EBUS scope", 1)},
    {"label": "MEAS_SIZE", "span": get_span(t10, "1.4 cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(t10, "subcarinal node", 1)},
    {"label": "MEAS_COUNT", "span": get_span(t10, "Three passes", 1)},
    {"label": "DEV_NEEDLE", "span": get_span(t10, "22G", 1)},
    {"label": "OBS_ROSE", "span": get_span(t10, "benign-appearing lymphocytes", 1)},
    {"label": "PROC_METHOD", "span": get_span(t10, "EM NAVIGATION", 1)},
    {"label": "PROC_ACTION", "span": get_span(t10, "TBLB", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "LLL superior segment", 1)},
    {"label": "PROC_METHOD", "span": get_span(t10, "EM navigation system", 1)},
    {"label": "OBS_LESION", "span": get_span(t10, "lesion", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "LLL superior segment", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "LLL superior segment", 3)},
    {"label": "PROC_METHOD", "span": get_span(t10, "navigation", 1)},
    {"label": "OBS_LESION", "span": get_span(t10, "lesion", 3)},
    {"label": "PROC_METHOD", "span": get_span(t10, "Fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(t10, "biopsy forceps", 1)},
    {"label": "OBS_LESION", "span": get_span(t10, "lesion", 4)},
    {"label": "MEAS_COUNT", "span": get_span(t10, "Four", 1)},
    {"label": "PROC_ACTION", "span": get_span(t10, "transbronchial biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", "span": get_span(t10, "No significant bleeding", 1)},
    {"label": "PROC_METHOD", "span": get_span(t10, "EM-navigated", 1)},
    {"label": "PROC_ACTION", "span": get_span(t10, "transbronchial biopsies", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(t10, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(t10, "lesion", 5)},
    {"label": "PROC_METHOD", "span": get_span(t10, "EBUS", 4)},
    {"label": "PROC_ACTION", "span": get_span(t10, "TBNA", 3)},
    {"label": "ANAT_LN_STATION", "span": get_span(t10, "station 7", 4)},
]
BATCH_DATA.append({"id": "700010", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)