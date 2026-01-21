import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Note 1: 177493_syn_1
# ------------------------------------------
t1 = """Indication: BI malignancy, pneumonia.
Anesthesia: GA, ETT.
Findings: BI 80% obstructed.
Procedure: 6F catheter placed past tumor. Fluoro confirm. Dummy check.
Plan: 6Gy x 4 weekly. Admit/Obs."""

e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "BI", 1)},
    {"label": "OBS_LESION", **get_span(t1, "malignancy", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "pneumonia", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "BI", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "80% obstructed", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t1, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(t1, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Fluoro", 1)},
    {"label": "MEAS_ENERGY", **get_span(t1, "6Gy", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 1)},
]
BATCH_DATA.append({"id": "177493_syn_1", "text": t1, "entities": e1})

# ------------------------------------------
# Note 2: 177493_syn_2
# ------------------------------------------
t2 = """CLINICAL SUMMARY: [REDACTED], an 80-year-old female with NSCLC involving the bronchus intermedius (BI), underwent bronchoscopic catheter placement for palliative HDR brachytherapy. The BI was 80% obstructed by an infiltrative mass. Under general anesthesia, a 6-French afterloading catheter was positioned trans-bronchially. Verification via fluoroscopy ensured the catheter extended sufficiently distal to the 3.0 cm lesion. The patient was transferred for the first of four weekly fractions."""

e2 = [
    {"label": "OBS_LESION", **get_span(t2, "NSCLC", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "bronchus intermedius", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "BI", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "bronchoscopic", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "BI", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "80% obstructed", 1)},
    {"label": "OBS_LESION", **get_span(t2, "infiltrative mass", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t2, "6-French", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "afterloading catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "fluoroscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "catheter", 3)},
    {"label": "MEAS_SIZE", **get_span(t2, "3.0 cm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
]
BATCH_DATA.append({"id": "177493_syn_2", "text": t2, "entities": e2})

# ------------------------------------------
# Note 3: 177493_syn_3
# ------------------------------------------
t3 = """Service: Therapeutic Bronchoscopy (31643).
Site: Bronchus Intermedius.
Material: 6F afterloading catheter.
Dosimetry: 6.0 Gy prescribed at 1.0 cm.
Verification: Fluoroscopy used to confirm catheter 2 cm distal to lesion.
Note: Patient intubated (GA) due to respiratory status."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Bronchus Intermedius", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t3, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "afterloading catheter", 1)},
    {"label": "MEAS_ENERGY", **get_span(t3, "6.0 Gy", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "1.0 cm", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Fluoroscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "catheter", 2)},
    {"label": "MEAS_SIZE", **get_span(t3, "2 cm", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lesion", 1)},
]
BATCH_DATA.append({"id": "177493_syn_3", "text": t3, "entities": e3})

# ------------------------------------------
# Note 4: 177493_syn_4
# ------------------------------------------
t4 = """Resident Procedure Note
Pt: M. Jones
Staff: Dr. Washington
Steps:
1. GA induced, ETT check.
2. Scope to BI.
3. Tumor visualized (large, 3cm).
4. 6F cath placed.
5. Fluoro verification.
6. Secure and transport.
Plan: Session 1/4."""

e4 = [
    {"label": "DEV_INSTRUMENT", **get_span(t4, "ETT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "BI", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "3cm", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t4, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "cath", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Fluoro", 1)},
]
BATCH_DATA.append({"id": "177493_syn_4", "text": t4, "entities": e4})

# ------------------------------------------
# Note 5: 177493_syn_5
# ------------------------------------------
t5 = """procedure note for [REDACTED] 80yo female with the bi tumor shes got pneumonia too so we did ga with ett scope went in saw the tumor blocking the bi pretty bad like 80 percent put the 6f catheter through the scope checked it with the c-arm looks good taped it shes going for 6gy radiation now will do this weekly"""

e5 = [
    {"label": "ANAT_AIRWAY", **get_span(t5, "bi", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "pneumonia", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "ett", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "scope", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "bi", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "80 percent", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t5, "6f", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "scope", 2)},
    {"label": "PROC_METHOD", **get_span(t5, "c-arm", 1)}, # Mapped as procedure/tech used (Fluoroscopy machine)
    {"label": "MEAS_ENERGY", **get_span(t5, "6gy", 1)},
]
BATCH_DATA.append({"id": "177493_syn_5", "text": t5, "entities": e5})

# ------------------------------------------
# Note 6: 177493_syn_6
# ------------------------------------------
t6 = """Bronchoscopy performed for placement of HDR brachytherapy catheter in an 80-year-old female with malignant obstruction of the bronchus intermedius. General anesthesia was utilized. The tumor was visualized and a 6F afterloading catheter was advanced through the working channel to a position distal to the lesion. Fluoroscopic confirmation was obtained. The patient proceeded to receive 6.0 Gy as the first of four planned fractions."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Bronchoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(t6, "obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "bronchus intermedius", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t6, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "afterloading catheter", 1)},
    {"label": "OBS_LESION", **get_span(t6, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Fluoroscopic", 1)},
    {"label": "MEAS_ENERGY", **get_span(t6, "6.0 Gy", 1)},
]
BATCH_DATA.append({"id": "177493_syn_6", "text": t6, "entities": e6})

# ------------------------------------------
# Note 7: 177493_syn_7
# ------------------------------------------
t7 = """[Indication]
Malignant BI obstruction, post-obstructive pneumonia.
[Anesthesia]
General, ETT.
[Description]
Scope advanced to BI. 6F catheter placed across 3.0 cm tumor. Fluoroscopic verification of tip position. Dummy source check complete.
[Plan]
6.0 Gy session 1/4. Monitor respiratory status."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "BI", 1)},
    {"label": "OBS_LESION", **get_span(t7, "obstruction", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "pneumonia", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "ETT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "BI", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t7, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "3.0 cm", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Fluoroscopic", 1)},
    {"label": "MEAS_ENERGY", **get_span(t7, "6.0 Gy", 1)},
]
BATCH_DATA.append({"id": "177493_syn_7", "text": t7, "entities": e7})

# ------------------------------------------
# Note 8: 177493_syn_8
# ------------------------------------------
t8 = """[REDACTED] to the OR for brachytherapy catheter placement to treat her bronchus intermedius tumor. Because of her pneumonia and age, we used general anesthesia. We found the tumor causing significant blockage. We carefully guided a 6F catheter past the narrowing. We used the fluoroscope to make sure it was in the right spot before taping it down. She is scheduled for four weekly sessions starting today."""

e8 = [
    {"label": "DEV_CATHETER", **get_span(t8, "catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "bronchus intermedius", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "pneumonia", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t8, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "catheter", 2)},
    {"label": "PROC_METHOD", **get_span(t8, "fluoroscope", 1)},
]
BATCH_DATA.append({"id": "177493_syn_8", "text": t8, "entities": e8})

# ------------------------------------------
# Note 9: 177493_syn_9
# ------------------------------------------
t9 = """Indication: Neoplastic blockage of BI.
Operation: Bronchoscopy with lodging of brachytherapy conduit.
Observations: 3 cm growth in Bronchus Intermedius. 6F tube inserted via working channel. Placement corroborated via fluoroscopy. 6 Gy dose scheduled. Patient to return weekly."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "blockage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "BI", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "conduit", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "3 cm", 1)},
    {"label": "OBS_LESION", **get_span(t9, "growth", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "Bronchus Intermedius", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t9, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "tube", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "fluoroscopy", 1)},
    {"label": "MEAS_ENERGY", **get_span(t9, "6 Gy", 1)},
]
BATCH_DATA.append({"id": "177493_syn_9", "text": t9, "entities": e9})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)