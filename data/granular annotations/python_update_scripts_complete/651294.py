import sys
from pathlib import Path

# Set the root directory (assuming this script is inside a subdirectory of the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

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
    
    return start, start + len(term)

# ==========================================
# Note 1: 651294_syn_1
# ==========================================
t1 = """Indication: LLL lesion, ?recurrence.
Findings: Polypoid lesion LB6, 50% obstructed. Necrotic.
Procedure: 5 biopsies taken. APC (40W) used for hemostasis.
Disp: Home. Onc f/u."""
e1 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t1, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t1, "lesion", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t1, "recurrence", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t1, "Polypoid lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t1, "LB6", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(t1, "50% obstructed", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t1, "Necrotic", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t1, "5", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "biopsies", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t1, "APC", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(t1, "40W", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "hemostasis", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 651294_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: The patient, with a history of NSCLC, presented with a new LLL lesion. Bronchoscopy revealed a necrotic, polypoid mass partially obstructing the LB6 orifice. Five biopsy specimens were obtained for histopathologic and molecular analysis. Hemostasis was achieved utilizing Argon Plasma Coagulation (APC) applied to the biopsy bed."""
e2 = [
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(t2, "history of NSCLC", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t2, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t2, "lesion", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t2, "Bronchoscopy", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t2, "necrotic", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t2, "polypoid mass", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t2, "LB6", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t2, "Five", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "biopsy", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t2, "specimens", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "Hemostasis", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t2, "Argon Plasma Coagulation", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t2, "APC", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 651294_syn_3
# ==========================================
t3 = """CPT 31625 (Biopsy). Note on APC: Argon Plasma Coagulation was utilized solely for control of procedure-induced hemorrhage (hemostasis), not for tumor destruction. Therefore, CPT 31641 is not reported. Service billed is biopsy of the LLL lesion."""
e3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "Biopsy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t3, "APC", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t3, "Argon Plasma Coagulation", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t3, "procedure-induced hemorrhage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "hemostasis", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "tumor destruction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "biopsy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t3, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t3, "lesion", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 651294_syn_4
# ==========================================
t4 = """Fellow Note
Pt: M. Thompson
Procedure: Bronch w/ Biopsy
1. LMA placed.
2. Scope to LLL.
3. Lesion at LB6 biopsied x5.
4. Bleeding noted -> APC applied for control.
5. Extubated stable."""
e4 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t4, "Bronch", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "Biopsy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "Scope", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t4, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t4, "Lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t4, "LB6", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "biopsied", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t4, "x5", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t4, "Bleeding", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t4, "APC", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 651294_syn_5
# ==========================================
t5 = """marcus thompson biopsy of lll mass looks like recurrence necrotic tissue at lb6 took 5 samples started bleeding a bit so we used the apc to burn it stop the bleeding airway open enough extubated fine."""
e5 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "biopsy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t5, "lll", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t5, "mass", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t5, "recurrence", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t5, "necrotic tissue", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t5, "lb6", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t5, "5", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t5, "samples", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t5, "bleeding", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t5, "apc", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "burn", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t5, "stop the bleeding", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t5, "airway", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 651294_syn_6
# ==========================================
t6 = """General anesthesia was administered via LMA. A therapeutic scope was used to id[REDACTED] a polypoid, necrotic lesion at the LB6 origin causing 50% obstruction. Five biopsies were taken. Moderate bleeding necessitated the use of APC (40W) for hemostasis. The patient was extubated and recovered in PACU."""
e6 = [
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t6, "therapeutic scope", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t6, "polypoid, necrotic lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t6, "LB6", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(t6, "50% obstruction", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t6, "Five", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "biopsies", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t6, "bleeding", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t6, "APC", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(t6, "40W", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "hemostasis", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 651294_syn_7
# ==========================================
t7 = """[Indication]
Suspected NSCLC recurrence, LLL lesion.
[Anesthesia]
General (LMA).
[Description]
LB6 mass biopsied 5 times. Moderate bleeding controlled with APC. Airway patent.
[Plan]
Oncology follow-up."""
e7 = [
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(t7, "NSCLC recurrence", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t7, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t7, "lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t7, "LB6", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t7, "mass", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "biopsied", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t7, "5", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t7, "bleeding controlled", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t7, "APC", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t7, "Airway", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 651294_syn_8
# ==========================================
t8 = """[REDACTED] a bronchoscopy to evaluate a suspicious lesion in his left lower lobe. We found a necrotic mass blocking about half of the LB6 segment. We took five biopsy samples. Because of moderate bleeding afterwards, we used Argon Plasma Coagulation to cauterize the area and stop the bleeding. He is discharged to follow up with oncology."""
e8 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t8, "bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t8, "lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t8, "left lower lobe", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t8, "necrotic mass", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(t8, "blocking about half", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t8, "LB6", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t8, "five", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "biopsy", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t8, "samples", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t8, "bleeding", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t8, "Argon Plasma Coagulation", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "cauterize", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t8, "stop the bleeding", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 651294_syn_9
# ==========================================
t9 = """Assessment of LLL mass. Conducted bronchoscopy with sampling. Id[REDACTED] necrotic blockage at LB6. Collected 5 tissue specimens. Applied thermal energy (APC) for coagulation. Extubated successfully."""
e9 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t9, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t9, "mass", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t9, "bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "sampling", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t9, "necrotic", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t9, "blockage", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t9, "LB6", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t9, "5", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t9, "tissue specimens", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t9, "thermal energy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t9, "APC", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "coagulation", 1)))},
]
BATCH_DATA.append({"id": "651294_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 651294
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Amanda Williams, Fellow: Dr. James Park (PGY-5)

Dx: LLL endobronchial lesion, known NSCLC s/p chemo, ? recurrence
Procedure: Flex bronch with endobronchial biopsy

General anesthesia via LMA. Olympus therapeutic scope used. Prior radiation changes noted at LUL. New polypoid lesion at LB6 origin, 50% obstruction. Appears necrotic with surface ulceration. 5 endobronchial biopsies obtained. APC applied (40W, 0.8L/min) for hemostasis after moderate bleeding. Airways otherwise patent. Scope withdrawn, LMA removed, patient extubated.

Stable in PACU. CXR post-procedure unremarkable. D/C to home. Oncology f/u with results.

A. Williams, MD / J. Park, MD"""
e10 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "LLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "endobronchial lesion", 1)))},
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(t10, "known NSCLC", 1)))},
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(t10, "s/p chemo", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "Flex bronch", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "endobronchial biopsy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Olympus therapeutic scope", 1)))},
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(t10, "Prior radiation changes", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "LUL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "polypoid lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "LB6", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(t10, "50% obstruction", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "necrotic", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "surface ulceration", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "5", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "endobronchial biopsies", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "APC", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(t10, "40W", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "hemostasis", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t10, "bleeding", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "Airways", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Scope", 1)))},
]
BATCH_DATA.append({"id": "651294", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)