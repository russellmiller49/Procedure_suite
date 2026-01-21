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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text: {text[:50]}...")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload (Batch)
# ==========================================
BATCH_DATA = []

# ---------------------------------------------------------------------
# Note 1: 700006_syn_1
# ---------------------------------------------------------------------
t1 = """Dx: Recurrent malignant effusion (Lung CA).
Proc: Tunneled IPC (PleurX) placement.
Steps:
- US guidance.
- Seldinger technique R mid-axillary.
- Subq tunnel created.
- Catheter placed.
- 1500mL drained.
Plan: Home w/ nursing."""

e1 = [
    {"label": "OBS_LESION",      **get_span(t1, "effusion", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t1, "Lung", 1)},
    {"label": "OBS_LESION",      **get_span(t1, "CA", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "Tunneled", 1)},
    {"label": "DEV_CATHETER",    **get_span(t1, "IPC", 1)},
    {"label": "DEV_CATHETER",    **get_span(t1, "PleurX", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "placement", 1)},
    {"label": "PROC_METHOD",     **get_span(t1, "US guidance", 1)},
    {"label": "PROC_METHOD",     **get_span(t1, "Seldinger technique", 1)},
    {"label": "LATERALITY",      **get_span(t1, "R", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t1, "mid-axillary", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "tunnel", 1)},
    {"label": "DEV_CATHETER",    **get_span(t1, "Catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "placed", 1)},
    {"label": "MEAS_VOL",        **get_span(t1, "1500mL", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "drained", 1)},
]
BATCH_DATA.append({"id": "700006_syn_1", "text": t1, "entities": e1})

# ---------------------------------------------------------------------
# Note 2: 700006_syn_2
# ---------------------------------------------------------------------
t2 = """OPERATIVE NOTE: Insertion of indwelling tunneled pleural catheter.
INDICATION: 69-year-old male with metastatic lung adenocarcinoma and recurrent right pleural effusion.
DESCRIPTION: Under ultrasound guidance, the right pleural space was accessed. A subcutaneous tunnel was created, and the PleurX catheter was advanced. 1500 mL of serosanguinous fluid was drained to confirm position and patency. The patient was discharged with home health instructions."""

e2 = [
    {"label": "PROC_ACTION",     **get_span(t2, "Insertion", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "tunneled", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t2, "pleural", 1)},
    {"label": "DEV_CATHETER",    **get_span(t2, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t2, "lung", 1)},
    {"label": "OBS_LESION",      **get_span(t2, "adenocarcinoma", 1)},
    {"label": "LATERALITY",      **get_span(t2, "right", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t2, "pleural", 2)},
    {"label": "OBS_LESION",      **get_span(t2, "effusion", 1)},
    {"label": "PROC_METHOD",     **get_span(t2, "ultrasound guidance", 1)},
    {"label": "LATERALITY",      **get_span(t2, "right", 2)},
    {"label": "ANAT_PLEURA",     **get_span(t2, "pleural space", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "accessed", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "tunnel", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "created", 1)},
    {"label": "DEV_CATHETER",    **get_span(t2, "PleurX catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "advanced", 1)},
    {"label": "MEAS_VOL",        **get_span(t2, "1500 mL", 1)},
    {"label": "OBS_FINDING",     **get_span(t2, "serosanguinous fluid", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "drained", 1)},
]
BATCH_DATA.append({"id": "700006_syn_2", "text": t2, "entities": e2})

# ---------------------------------------------------------------------
# Note 3: 700006_syn_3
# ---------------------------------------------------------------------
t3 = """Code: 32550 (Insertion of tunneled pleural catheter).
Notes: Includes drainage at time of placement. Ultrasound guidance used. Catheter tunneled subcutaneously."""

e3 = [
    {"label": "PROC_ACTION",     **get_span(t3, "Insertion", 1)},
    {"label": "PROC_ACTION",     **get_span(t3, "tunneled", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t3, "pleural", 1)},
    {"label": "DEV_CATHETER",    **get_span(t3, "catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t3, "drainage", 1)},
    {"label": "PROC_ACTION",     **get_span(t3, "placement", 1)},
    {"label": "PROC_METHOD",     **get_span(t3, "Ultrasound guidance", 1)},
    {"label": "DEV_CATHETER",    **get_span(t3, "Catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t3, "tunneled", 2)},
]
BATCH_DATA.append({"id": "700006_syn_3", "text": t3, "entities": e3})

# ---------------------------------------------------------------------
# Note 4: 700006_syn_4
# ---------------------------------------------------------------------
t4 = """Procedure: PleurX Placement
Patient: [REDACTED]
Steps:
1. US check: free flowing fluid.
2. Local anesthetic.
3. Needle access/wire placement.
4. Tunnel created.
5. Catheter inserted/peel-away sheath.
6. Drained 1.5L.
Complications: None."""

e4 = [
    {"label": "DEV_CATHETER",    **get_span(t4, "PleurX", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "Placement", 1)},
    {"label": "PROC_METHOD",     **get_span(t4, "US", 1)},
    {"label": "OBS_FINDING",     **get_span(t4, "free flowing fluid", 1)},
    {"label": "MEDICATION",      **get_span(t4, "Local anesthetic", 1)},
    {"label": "DEV_NEEDLE",      **get_span(t4, "Needle", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "access", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t4, "wire", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "placement", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "Tunnel", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "created", 1)},
    {"label": "DEV_CATHETER",    **get_span(t4, "Catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "inserted", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t4, "peel-away sheath", 1)},
    {"label": "PROC_ACTION",     **get_span(t4, "Drained", 1)},
    {"label": "MEAS_VOL",        **get_span(t4, "1.5L", 1)},
]
BATCH_DATA.append({"id": "700006_syn_4", "text": t4, "entities": e4})

# ---------------------------------------------------------------------
# Note 5: 700006_syn_5
# ---------------------------------------------------------------------
t5 = """Put a PleurX catheter in Mr [REDACTED] today for his cancer fluid. Right side. Used ultrasound to find a good spot. Tunneled it nicely. Drained about a liter and a half of bloody fluid. He tolerated it well. Home health is set up to help him drain it at home."""

e5 = [
    {"label": "DEV_CATHETER",    **get_span(t5, "PleurX catheter", 1)},
    {"label": "OBS_LESION",      **get_span(t5, "cancer", 1)},
    {"label": "OBS_FINDING",     **get_span(t5, "fluid", 1)},
    {"label": "LATERALITY",      **get_span(t5, "Right", 1)},
    {"label": "PROC_METHOD",     **get_span(t5, "ultrasound", 1)},
    {"label": "PROC_ACTION",     **get_span(t5, "Tunneled", 1)},
    {"label": "PROC_ACTION",     **get_span(t5, "Drained", 1)},
    {"label": "MEAS_VOL",        **get_span(t5, "liter and a half", 1)},
    {"label": "OBS_FINDING",     **get_span(t5, "bloody fluid", 1)},
]
BATCH_DATA.append({"id": "700006_syn_5", "text": t5, "entities": e5})

# ---------------------------------------------------------------------
# Note 6: 700006_syn_6
# ---------------------------------------------------------------------
t6 = """Ultrasound-guided placement of right-sided tunneled indwelling pleural catheter (PleurX). 1500 mL serosanguinous fluid drained. Catheter patent. No complications. Discharged with home nursing."""

e6 = [
    {"label": "PROC_METHOD",     **get_span(t6, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION",     **get_span(t6, "placement", 1)},
    {"label": "LATERALITY",      **get_span(t6, "right", 1)},
    {"label": "PROC_ACTION",     **get_span(t6, "tunneled", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t6, "pleural", 1)},
    {"label": "DEV_CATHETER",    **get_span(t6, "catheter", 1)},
    {"label": "DEV_CATHETER",    **get_span(t6, "PleurX", 1)},
    {"label": "MEAS_VOL",        **get_span(t6, "1500 mL", 1)},
    {"label": "OBS_FINDING",     **get_span(t6, "serosanguinous fluid", 1)},
    {"label": "PROC_ACTION",     **get_span(t6, "drained", 1)},
    {"label": "DEV_CATHETER",    **get_span(t6, "Catheter", 1)},
]
BATCH_DATA.append({"id": "700006_syn_6", "text": t6, "entities": e6})

# ---------------------------------------------------------------------
# Note 7: 700006_syn_7
# ---------------------------------------------------------------------
t7 = """[Indication]
Recurrent malignant right pleural effusion.
[Anesthesia]
Local.
[Description]
US-guided insertion of tunneled IPC. 1500 mL drained. Catheter secured.
[Plan]
Home drainage 3x/week."""

e7 = [
    {"label": "OBS_LESION",      **get_span(t7, "malignant", 1)},
    {"label": "LATERALITY",      **get_span(t7, "right", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t7, "pleural", 1)},
    {"label": "OBS_LESION",      **get_span(t7, "effusion", 1)},
    {"label": "PROC_METHOD",     **get_span(t7, "US-guided", 1)},
    {"label": "PROC_ACTION",     **get_span(t7, "insertion", 1)},
    {"label": "PROC_ACTION",     **get_span(t7, "tunneled", 1)},
    {"label": "DEV_CATHETER",    **get_span(t7, "IPC", 1)},
    {"label": "MEAS_VOL",        **get_span(t7, "1500 mL", 1)},
    {"label": "PROC_ACTION",     **get_span(t7, "drained", 1)},
    {"label": "DEV_CATHETER",    **get_span(t7, "Catheter", 1)},
]
BATCH_DATA.append({"id": "700006_syn_7", "text": t7, "entities": e7})

# ---------------------------------------------------------------------
# Note 8: 700006_syn_8
# ---------------------------------------------------------------------
t8 = """To manage [REDACTED] effusion, we placed a tunneled PleurX catheter on the right side. Using ultrasound, we accessed the space and tunneled the catheter subcutaneously to reduce infection risk. We drained 1.5 liters of fluid during the procedure. He will now be able to manage his symptoms at home with intermittent drainage."""

e8 = [
    {"label": "OBS_LESION",      **get_span(t8, "effusion", 1)},
    {"label": "PROC_ACTION",     **get_span(t8, "placed", 1)},
    {"label": "PROC_ACTION",     **get_span(t8, "tunneled", 1)},
    {"label": "DEV_CATHETER",    **get_span(t8, "PleurX catheter", 1)},
    {"label": "LATERALITY",      **get_span(t8, "right", 1)},
    {"label": "PROC_METHOD",     **get_span(t8, "ultrasound", 1)},
    {"label": "PROC_ACTION",     **get_span(t8, "accessed", 1)},
    {"label": "PROC_ACTION",     **get_span(t8, "tunneled", 2)},
    {"label": "DEV_CATHETER",    **get_span(t8, "catheter", 2)},
    {"label": "PROC_ACTION",     **get_span(t8, "drained", 1)},
    {"label": "MEAS_VOL",        **get_span(t8, "1.5 liters", 1)},
    {"label": "OBS_FINDING",     **get_span(t8, "fluid", 1)},
    {"label": "PROC_ACTION",     **get_span(t8, "drainage", 1)},
]
BATCH_DATA.append({"id": "700006_syn_8", "text": t8, "entities": e8})

# ---------------------------------------------------------------------
# Note 9: 700006_syn_9
# ---------------------------------------------------------------------
t9 = """Procedure: Implantation of tunneled pleural drain.
Indication: Malignant dropsy.
Action: The pleural cavity was accessed under sonographic vision. A prosthetic catheter was tunneled and inserted. Fluid was evacuated.
Outcome: Device functional."""

e9 = [
    {"label": "PROC_ACTION",     **get_span(t9, "Implantation", 1)},
    {"label": "PROC_ACTION",     **get_span(t9, "tunneled", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t9, "pleural", 1)},
    {"label": "DEV_CATHETER",    **get_span(t9, "drain", 1)},
    {"label": "OBS_LESION",      **get_span(t9, "Malignant dropsy", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t9, "pleural cavity", 1)},
    {"label": "PROC_ACTION",     **get_span(t9, "accessed", 1)},
    {"label": "PROC_METHOD",     **get_span(t9, "sonographic vision", 1)},
    {"label": "DEV_CATHETER",    **get_span(t9, "prosthetic catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t9, "tunneled", 2)},
    {"label": "PROC_ACTION",     **get_span(t9, "inserted", 1)},
    {"label": "OBS_FINDING",     **get_span(t9, "Fluid", 1)},
    {"label": "PROC_ACTION",     **get_span(t9, "evacuated", 1)},
]
BATCH_DATA.append({"id": "700006_syn_9", "text": t9, "entities": e9})

# ---------------------------------------------------------------------
# Note 10: 700006 (Original)
# ---------------------------------------------------------------------
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
AGE: 69 years
DATE OF PROCEDURE: [REDACTED]
LOCATION: Pleural Procedure Suite

PRE-PROCEDURE DIAGNOSIS: Recurrent right malignant pleural effusion secondary to metastatic lung adenocarcinoma.
POST-PROCEDURE DIAGNOSIS: Same.

PROCEDURE: Ultrasound-guided tunneled indwelling pleural catheter placement (PleurX) with large-volume drainage.

PHYSICIAN: Rachel Green, MD (Interventional Pulmonology)
ASSISTANT: Pulmonary Fellow PGY-6

INDICATION:
69-year-old male with metastatic lung adenocarcinoma and recurrent symptomatic right pleural effusion requiring thoracentesis every 7–10 days. Shared decision-making favored tunneled indwelling pleural catheter placement for symptom control and outpatient management.

PROCEDURE DESCRIPTION:
Pre-procedure ultrasound confirmed a large free-flowing right pleural effusion with no significant loculations. Patient was positioned supine with head of bed elevated.

After time-out, the right lateral chest wall was prepped and draped. Local anesthesia was obtained with 1% lidocaine at the planned entry and exit sites. Under real-time ultrasound guidance, an 18G finder needle was advanced into the pleural space at the right mid-axillary line, 6th intercostal space, with return of serosanguinous fluid.

A guidewire was advanced and serial dilation performed. A subcutaneous tunnel approximately 7 cm in length was created anteriorly, and the PleurX catheter was pulled through the tunnel exiting at the anterior chest wall. The peel-away sheath was then advanced into the pleural space over the guidewire, and the catheter was inserted and the sheath removed.

The catheter was connected to a vacuum drainage bottle; approximately 1,500 mL of serosanguinous fluid was drained slowly with monitoring for chest discomfort and blood pressure changes. The catheter tip position was confirmed by ultrasound. The exit site and entry site were secured with sutures and sterile dressings.

COMPLICATIONS:
No significant pain, hypotension, or re-expansion pulmonary edema occurred. No immediate bleeding or air leak was noted.

DISPOSITION:
The patient was discharged home the same day with home health nursing arranged for drainage three times per week and instructions for signs of infection or catheter malfunction.

IMPRESSION:
Technically successful ultrasound-guided placement of a tunneled right PleurX catheter with large-volume drainage of recurrent malignant effusion."""

e10 = [
    # Diagnosis Header
    {"label": "LATERALITY",      **get_span(t10, "right", 1)},
    {"label": "OBS_LESION",      **get_span(t10, "malignant", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural", 1)},
    {"label": "OBS_LESION",      **get_span(t10, "effusion", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t10, "lung", 1)},
    {"label": "OBS_LESION",      **get_span(t10, "adenocarcinoma", 1)},
    
    # Procedure Header
    {"label": "PROC_METHOD",     **get_span(t10, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "tunneled", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural", 2)},
    {"label": "DEV_CATHETER",    **get_span(t10, "catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "placement", 1)},
    {"label": "DEV_CATHETER",    **get_span(t10, "PleurX", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "drainage", 1)},
    
    # Indication
    {"label": "ANAT_LUNG_LOC",   **get_span(t10, "lung", 2)},
    {"label": "OBS_LESION",      **get_span(t10, "adenocarcinoma", 2)},
    {"label": "LATERALITY",      **get_span(t10, "right", 2)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural", 3)},
    {"label": "OBS_LESION",      **get_span(t10, "effusion", 2)},
    {"label": "PROC_ACTION",     **get_span(t10, "thoracentesis", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "tunneled", 2)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural", 4)},
    {"label": "DEV_CATHETER",    **get_span(t10, "catheter", 2)},
    {"label": "PROC_ACTION",     **get_span(t10, "placement", 2)},
    
    # Description
    {"label": "PROC_METHOD",     **get_span(t10, "ultrasound", 1)},
    {"label": "LATERALITY",      **get_span(t10, "right", 3)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural", 5)},
    {"label": "OBS_LESION",      **get_span(t10, "effusion", 3)},
    {"label": "LATERALITY",      **get_span(t10, "right", 4)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "chest wall", 1)},
    {"label": "MEDICATION",      **get_span(t10, "lidocaine", 1)},
    {"label": "PROC_METHOD",     **get_span(t10, "ultrasound guidance", 1)},
    {"label": "MEAS_SIZE",       **get_span(t10, "18G", 1)},
    {"label": "DEV_NEEDLE",      **get_span(t10, "needle", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural space", 1)},
    {"label": "LATERALITY",      **get_span(t10, "right", 5)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "mid-axillary line", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "6th intercostal space", 1)},
    {"label": "OBS_FINDING",     **get_span(t10, "serosanguinous fluid", 1)},
    
    # Description P2
    {"label": "DEV_INSTRUMENT",  **get_span(t10, "guidewire", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "tunnel", 1)},
    {"label": "MEAS_SIZE",       **get_span(t10, "7 cm", 1)},
    {"label": "DEV_CATHETER",    **get_span(t10, "PleurX catheter", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "tunnel", 2)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "chest wall", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(t10, "peel-away sheath", 1)},
    {"label": "ANAT_PLEURA",     **get_span(t10, "pleural space", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(t10, "guidewire", 2)},
    {"label": "DEV_CATHETER",    **get_span(t10, "catheter", 4)},
    {"label": "PROC_ACTION",     **get_span(t10, "inserted", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t10, "sheath", 2)},
    
    # Description P3
    {"label": "DEV_CATHETER",    **get_span(t10, "catheter", 5)},
    {"label": "MEAS_VOL",        **get_span(t10, "1,500 mL", 1)},
    {"label": "OBS_FINDING",     **get_span(t10, "serosanguinous fluid", 2)},
    {"label": "PROC_ACTION",     **get_span(t10, "drained", 1)},
    {"label": "DEV_CATHETER",    **get_span(t10, "catheter", 6)},
    {"label": "PROC_METHOD",     **get_span(t10, "ultrasound", 2)},

    # Impression
    {"label": "PROC_METHOD",     **get_span(t10, "ultrasound-guided", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "placement", 3)},
    {"label": "PROC_ACTION",     **get_span(t10, "tunneled", 3)},
    {"label": "LATERALITY",      **get_span(t10, "right", 6)},
    {"label": "DEV_CATHETER",    **get_span(t10, "PleurX catheter", 2)},
    {"label": "PROC_ACTION",     **get_span(t10, "drainage", 2)},
    {"label": "OBS_LESION",      **get_span(t10, "malignant effusion", 1)},
]
BATCH_DATA.append({"id": "700006", "text": t10, "entities": e10})


# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)