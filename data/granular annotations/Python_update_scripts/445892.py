import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is running from the correct directory structure.")
    sys.exit(1)

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
# Note 1: 445892_syn_1
# ==========================================
t1 = """Procedure: Bronchoscopy w/ RFA.
- Target: RLL nodule (SCC).
- Guidance: ENB + Radial EBUS.
- Ablation: 105C for 10 min.
- Result: Good ablation zone."""

e1 = [
    {"label": "PROC_ACTION", **get_span(t1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "RFA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(t1, "SCC", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Ablation", 1)},
    {"label": "MEAS_TEMP", **get_span(t1, "105C", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "10 min", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Good ablation zone", 1)}
]
BATCH_DATA.append({"id": "445892_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 445892_syn_2
# ==========================================
t2 = """Operative Report: Under general anesthesia, [REDACTED] ablation of an RLL squamous cell carcinoma. Electromagnetic navigation bronchoscopy (ENB) was used to localize the superior segment lesion. Radial EBUS confirmed the target. A radiofrequency ablation (RFA) catheter was deployed, and treatment was delivered at 105 degrees Celsius for 10 minutes. No immediate complications were observed."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "squamous cell carcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "superior segment", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "radiofrequency ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "RFA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "treatment", 1)},
    {"label": "MEAS_TEMP", **get_span(t2, "105 degrees Celsius", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "10 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "No immediate complications", 1)}
]
BATCH_DATA.append({"id": "445892_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 445892_syn_3
# ==========================================
t3 = """Billing Codes:
- 31641: Destruction of tumor (RFA).
- 31627: Navigation.
- 31654: Radial EBUS.
Note: Diagnosis is SCC. Procedure is therapeutic ablation."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Destruction", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "RFA", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t3, "SCC", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "therapeutic ablation", 1)}
]
BATCH_DATA.append({"id": "445892_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 445892_syn_4
# ==========================================
t4 = """Resident Note:
- Patient: Dennis Jackson.
- Dx: RLL SCC.
- ENB to RLL.
- REBUS confirmed.
- RFA probe placed.
- Burned at 105C x 10m.
- Stable."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "SCC", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 2)},
    {"label": "PROC_METHOD", **get_span(t4, "REBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "RFA probe", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Burned", 1)},
    {"label": "MEAS_TEMP", **get_span(t4, "105C", 1)},
    {"label": "MEAS_TIME", **get_span(t4, "10m", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Stable", 1)}
]
BATCH_DATA.append({"id": "445892_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 445892_syn_5
# ==========================================
t5 = """dennis jackson here for rfa of his lung tumor. used the navigation and the ultrasound to find the rll nodule. cooked it with the rfa probe for 10 mins. everything looks good cxr tomorrow."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "rfa", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lung", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ultrasound", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rll", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "cooked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rfa probe", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "10 mins", 1)}
]
BATCH_DATA.append({"id": "445892_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 445892_syn_6
# ==========================================
t6 = """Bronchoscopy with radiofrequency ablation of a 2.2 cm RLL nodule using ENB and radial EBUS confirmation. The probe was placed, and ablation was performed at 105°C for 10 minutes. The patient tolerated the procedure well."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "radiofrequency ablation", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "2.2 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "probe", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "ablation", 2)},
    {"label": "MEAS_TEMP", **get_span(t6, "105°C", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "10 minutes", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t6, "tolerated the procedure well", 1)}
]
BATCH_DATA.append({"id": "445892_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 445892_syn_7
# ==========================================
t7 = """[Indication] RLL SCC (2.2cm).
[Anesthesia] General.
[Description] ENB (31627) to RLL. REBUS (31654) confirmed. RFA (31641) performed 105C/10min. No bleeding.
[Plan] CXR, DC if stable."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "SCC", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "2.2cm", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 2)},
    {"label": "PROC_METHOD", **get_span(t7, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "RFA", 1)},
    {"label": "MEAS_TEMP", **get_span(t7, "105C", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "10min", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "No bleeding", 1)}
]
BATCH_DATA.append({"id": "445892_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 445892_syn_8
# ==========================================
t8 = """[REDACTED] a bronchoscopy for radiofrequency ablation of his right lower lobe tumor. We used electromagnetic navigation and radial EBUS to precisely locate the cancer. We then inserted the RFA probe and treated the lesion at 105 degrees for 10 minutes. There were no complications."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "radiofrequency ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t8, "cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "RFA probe", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "treated", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lesion", 1)},
    {"label": "MEAS_TEMP", **get_span(t8, "105 degrees", 1)},
    {"label": "MEAS_TIME", **get_span(t8, "10 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "no complications", 1)}
]
BATCH_DATA.append({"id": "445892_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 445892_syn_9
# ==========================================
t9 = """Bronchoscopy with radiofrequency destruction of an RLL nodule using ENB and radial EBUS verification. The lesion was localized and ablated. Treatment parameters were 105°C for 10 minutes."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "radiofrequency destruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "ablated", 1)},
    {"label": "MEAS_TEMP", **get_span(t9, "105°C", 1)},
    {"label": "MEAS_TIME", **get_span(t9, "10 minutes", 1)}
]
BATCH_DATA.append({"id": "445892_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 445892
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Carol Stevens

Dx: RLL nodule 2.2cm, squamous cell CA
Procedure: Bronch w/ RFA

Under GA, bronchoscopy performed. ENB to RLL superior segment. R-EBUS confirmed target. RFA probe placed (RITA 1500X, 2cm tines). Treatment: 105°C x 10min. Good ablation zone. No bleeding, no complications. Extubated, stable.

CXR today. CT tomorrow. D/C if OK. F/U 1mo.

C. Stevens MD"""

e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.2cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "squamous cell CA", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "RFA", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "superior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "R-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "RFA probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "RITA 1500X", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2cm", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Treatment", 1)},
    {"label": "MEAS_TEMP", **get_span(t10, "105°C", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "10min", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Good ablation zone", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no complications", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "stable", 1)}
]
BATCH_DATA.append({"id": "445892", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)