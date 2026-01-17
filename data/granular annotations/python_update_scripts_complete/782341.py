import sys
from pathlib import Path

# Adjust this path if your repository structure is different
# We assume the script is run from a subfolder or root where 'scripts' is accessible
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly in a different structure
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns: {"start": int, "end": int} or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found enough times
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 782341_syn_1
# ==========================================
t1 = """Procedure: Bronchoscopy w/ EBBx
Target: RUL mass (RB1).
Action: Scope passed. Exophytic mass ID'd. 4 biopsies taken with cold forceps. Moderate bleeding -> Cold saline. Hemostasis achieved.
Plan: Path f/u."""

e1 = [
    {"label": "PROC_ACTION", **get_span(t1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "EBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB1", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Scope", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Exophytic", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "cold forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(t1, "Cold saline", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Hemostasis", 1)}
]
BATCH_DATA.append({"id": "782341_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 782341_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: The patient was brought to the bronchoscopy suite for evaluation of a right upper lobe endobronchial abnormality suggestive of neoplasia. Upon endoscopic visualization, a polypoid, friable tissue mass was observed nearly obstructing the RB1 segment. Utilizing standard cold forceps, four biopsies were procured to ensure adequate histopathologic characterization. Hemostasis was secured via lavage with cold saline."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t2, "endobronchial abnormality", 1)},
    {"label": "OBS_LESION", **get_span(t2, "neoplasia", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "polypoid", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "friable", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB1", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "cold forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "four", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "Hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "lavage", 1)},
    {"label": "MEDICATION", **get_span(t2, "cold saline", 1)}
]
BATCH_DATA.append({"id": "782341_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 782341_syn_3
# ==========================================
t3 = """CPT 31625: Bronchoscopy with endobronchial biopsy.
Procedure Note: Flexible bronchoscope introduced. Anatomical inspection revealed 6.0mm scope used to access RUL. A specific lesion at the RB1 orifice was id[REDACTED]. Forceps were utilized to obtain 4 distinct tissue samples (endobronchial biopsies). Bleeding was managed with cold saline irrigation. No additional fluoroscopy or needle aspiration required."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "endobronchial biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Flexible bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RB1", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "4", 1)},
    {"label": "SPECIMEN", **get_span(t3, "tissue samples", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "endobronchial biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t3, "Bleeding", 1)},
    {"label": "MEDICATION", **get_span(t3, "cold saline", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "irrigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "needle aspiration", 1)}
]
BATCH_DATA.append({"id": "782341_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 782341_syn_4
# ==========================================
t4 = """Procedure Note
Resident: Dr. Chen
Patient: [REDACTED]
Indication: RUL Mass
Steps:
1. Moderate sedation initiated.
2. Scope inserted orally.
3. Airway inspection: Mass at RB1.
4. Biopsy: 4 samples taken from RUL mass.
5. Hemostasis: Cold saline used.
6. Scope withdrawn.
Plan: Follow pathology."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Scope", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Mass", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB1", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "4", 1)},
    {"label": "SPECIMEN", **get_span(t4, "samples", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t4, "mass", 1)}, # Fixed: "mass" (lowercase) appears only once in t4
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "Hemostasis", 1)},
    {"label": "MEDICATION", **get_span(t4, "Cold saline", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Scope", 2)}
]
BATCH_DATA.append({"id": "782341_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 782341_syn_5
# ==========================================
t5 = """pt [REDACTED] harrison here for bronchoscopy found that rul mass looked like cancer red and friable at rb1 took four biopsies bleeding was moderate so we used cold saline to stop it washings sent too patient did fine going home 5 days for path results."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rul", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "red", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "friable", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rb1", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "four", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(t5, "cold saline", 1)},
    {"label": "SPECIMEN", **get_span(t5, "washings", 1)},
    {"label": "CTX_TIME", **get_span(t5, "5 days", 1)}
]
BATCH_DATA.append({"id": "782341_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 782341_syn_6
# ==========================================
t6 = """Under moderate sedation, a flexible bronchoscope was introduced. The airways were inspected. A pink-red, friable, exophytic mass was id[REDACTED] at the RB1 orifice, causing near-complete occlusion. Four endobronchial biopsies were obtained using cold forceps. Moderate bleeding occurred and was controlled with cold saline irrigation. Bronchial washings were collected. The patient tolerated the procedure well."""

e6 = [
    {"label": "DEV_INSTRUMENT", **get_span(t6, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "airways", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "pink-red", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "friable", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "exophytic", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RB1", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Four", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "endobronchial biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "cold forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(t6, "cold saline", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "irrigation", 1)},
    {"label": "SPECIMEN", **get_span(t6, "Bronchial washings", 1)}
]
BATCH_DATA.append({"id": "782341_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 782341_syn_7
# ==========================================
t7 = """[Indication]
RUL endobronchial mass on CT, suspected malignancy.
[Anesthesia]
Moderate sedation (Midazolam/Fentanyl).
[Description]
Scope inserted. Exophytic mass found at RB1. 4 biopsies taken. Bleeding controlled with cold saline.
[Plan]
Discharge home. Pathology follow-up."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "endobronchial mass", 1)},
    {"label": "MEDICATION", **get_span(t7, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(t7, "Fentanyl", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Scope", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Exophytic", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB1", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Bleeding", 1)},
    {"label": "MEDICATION", **get_span(t7, "cold saline", 1)}
]
BATCH_DATA.append({"id": "782341_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 782341_syn_8
# ==========================================
t8 = """The patient, [REDACTED], presented for a bronchoscopy due to a suspected RUL mass. After achieving moderate sedation, we advanced the scope and id[REDACTED] a polypoid mass occluding the RB1 segment. We proceeded to take four biopsies using cold forceps. There was some moderate bleeding, which we successfully managed with cold saline. The patient remained stable throughout."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "scope", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "polypoid", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "RB1", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "four", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "cold forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(t8, "cold saline", 1)}
]
BATCH_DATA.append({"id": "782341_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 782341_syn_9
# ==========================================
t9 = """Diagnosed RUL endobronchial mass. Performed bronchoscopy with sampling. Under sedation, inspected airways. Spotted exophytic mass at RB1. Harvested 4 tissue samples with forceps. Controlled hemorrhage with saline. Collected washings. Patient tolerated intervention."""

e9 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "endobronchial mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "airways", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "exophytic", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RB1", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "4", 1)},
    {"label": "SPECIMEN", **get_span(t9, "tissue samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "hemorrhage", 1)},
    {"label": "MEDICATION", **get_span(t9, "saline", 1)},
    {"label": "SPECIMEN", **get_span(t9, "washings", 1)}
]
BATCH_DATA.append({"id": "782341_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 782341
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Rebecca Chen

Dx: RUL endobronchial mass seen on CT, suspected lung cancer
Procedure: Bronchoscopy with endobronchial biopsy

Under moderate sedation (midazolam 4mg, fentanyl 100mcg IV), flexible bronchoscopy performed via oral route with 6.0mm Olympus scope. Airways inspected systematically. Exophytic polypoid mass id[REDACTED] at RB1 orifice, near-completely occluding the segment. Pink-red, friable appearance. 4 endobronchial biopsies obtained with cold forceps. Moderate bleeding controlled with cold saline irrigation. Bronchial washings sent. No other airway abnormalities. Patient tolerated procedure well.

Post-procedure: Stable, SpO2 96% on 2L NC. D/C home with path f/u in 5 days.

R. Chen, MD"""

e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "endobronchial mass", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lung cancer", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "endobronchial biopsy", 1)},
    {"label": "MEDICATION", **get_span(t10, "midazolam", 1)},
    {"label": "MEDICATION", **get_span(t10, "fentanyl", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "flexible bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Olympus scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Airways", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Exophytic", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "polypoid", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB1", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Pink-red", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "friable", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "endobronchial biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "cold forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "bleeding", 1)}, # Fixed: "bleeding" (lowercase) in t10
    {"label": "MEDICATION", **get_span(t10, "cold saline", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "irrigation", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Bronchial washings", 1)},
    {"label": "CTX_TIME", **get_span(t10, "5 days", 1)}
]
BATCH_DATA.append({"id": "782341", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)