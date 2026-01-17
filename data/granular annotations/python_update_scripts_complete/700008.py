import sys
from pathlib import Path

# Set the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to enable imports
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 700008_syn_1
# ==========================================
t1 = """Dx: Loculated malignant effusion.
Proc: US-guided pigtail (12Fr).
Steps:
- US localized pocket.
- Seldinger technique.
- 12Fr pigtail placed.
- 700mL drained.
Plan: Admit to oncology."""

e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "Loculated", 1)},
    {"label": "OBS_LESION", **get_span(t1, "malignant effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US-guided", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "pigtail", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t1, "12Fr", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US", 2)}, # "US localized..."
    {"label": "OBS_LESION", **get_span(t1, "pocket", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t1, "12Fr", 2)},
    {"label": "DEV_CATHETER", **get_span(t1, "pigtail", 2)},
    {"label": "MEAS_VOL", **get_span(t1, "700mL", 1)}
]
BATCH_DATA.append({"id": "700008_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 700008_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Ultrasound-guided placement of small-bore pleural drainage catheter.
INDICATION: 49-year-old male with metastatic renal cell carcinoma and loculated right pleural effusion.
DESCRIPTION: Under ultrasound guidance, a 12 Fr pigtail catheter was inserted into the right pleural space using the Seldinger technique. 700 mL of serosanguinous fluid was drained. The catheter was secured and attached to a drainage system."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "placement", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "small-bore pleural drainage catheter", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "loculated", 1)},
    {"label": "LATERALITY", **get_span(t2, "right", 1)},
    {"label": "OBS_LESION", **get_span(t2, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ultrasound guidance", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t2, "12 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "pigtail catheter", 1)},
    {"label": "LATERALITY", **get_span(t2, "right", 2)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Seldinger technique", 1)},
    {"label": "MEAS_VOL", **get_span(t2, "700 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "serosanguinous fluid", 1)}
]
BATCH_DATA.append({"id": "700008_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 700008_syn_3
# ==========================================
t3 = """Code: 32557 (Pleural drainage with imaging guidance).
Device: 12 Fr pigtail catheter.
Guidance: Ultrasound (real-time).
Note: Separate from thoracentesis codes."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Pleural drainage", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "imaging guidance", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t3, "12 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Ultrasound", 1)}
]
BATCH_DATA.append({"id": "700008_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 700008_syn_4
# ==========================================
t4 = """Procedure: Pigtail Catheter Placement
Patient: [REDACTED]
Steps:
1. US scan: loculated fluid.
2. Local anesthesia.
3. Needle/wire access.
4. Dilated tract.
5. 12Fr pigtail advanced.
6. Drained 700mL.
Complications: None."""

e4 = [
    {"label": "DEV_CATHETER", **get_span(t4, "Pigtail Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Placement", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "US scan", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t4, "fluid", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t4, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(t4, "700mL", 1)}
]
BATCH_DATA.append({"id": "700008_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 700008_syn_5
# ==========================================
t5 = """Placed a pigtail for Mr [REDACTED] today he has those loculated effusions. Right side. Used ultrasound to find the big pocket. Put in a 12 french wire guided. Drained 700cc. Secured it well he's going back to the floor."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "Placed", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "pigtail", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t5, "effusions", 1)},
    {"label": "LATERALITY", **get_span(t5, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(t5, "pocket", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t5, "12 french", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "700cc", 1)}
]
BATCH_DATA.append({"id": "700008_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 700008_syn_6
# ==========================================
t6 = """Ultrasound-guided insertion of 12 Fr pigtail catheter into right pleural space for loculated malignant effusion. 700 mL serosanguinous fluid drained. No pneumothorax. Catheter secured."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "insertion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t6, "12 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "pigtail catheter", 1)},
    {"label": "LATERALITY", **get_span(t6, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t6, "malignant effusion", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "700 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "serosanguinous fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No pneumothorax", 1)}
]
BATCH_DATA.append({"id": "700008_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 700008_syn_7
# ==========================================
t7 = """[Indication]
Loculated right malignant effusion.
[Anesthesia]
Local/Moderate.
[Description]
US-guided placement of 12Fr pigtail catheter. 700 mL drained.
[Plan]
Floor care, daily output monitoring."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "Loculated", 1)},
    {"label": "LATERALITY", **get_span(t7, "right", 1)},
    {"label": "OBS_LESION", **get_span(t7, "malignant effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "US-guided", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "placement", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t7, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(t7, "700 mL", 1)}
]
BATCH_DATA.append({"id": "700008_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 700008_syn_8
# ==========================================
t8 = """We placed a small-bore pigtail catheter for [REDACTED] his loculated effusion. Using ultrasound to guide us, we accessed the fluid pocket and threaded a 12 French catheter over a wire. We drained about 700 mL of fluid. The catheter was secured for ongoing drainage on the ward."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "small-bore pigtail catheter", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t8, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(t8, "fluid pocket", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t8, "12 French", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "catheter", 2)},
    {"label": "MEAS_VOL", **get_span(t8, "700 mL", 1)}
]
BATCH_DATA.append({"id": "700008_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 700008_syn_9
# ==========================================
t9 = """Procedure: Image-guided percutaneous pleural drainage.
Indication: Complex effusion.
Action: A pigtail catheter was introduced under sonographic control. Fluid was evacuated.
Outcome: Catheter in situ."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Image-guided", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "pleural drainage", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Complex", 1)},
    {"label": "OBS_LESION", **get_span(t9, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "sonographic control", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Fluid", 1)}
]
BATCH_DATA.append({"id": "700008_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 700008
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
AGE: 49 years
DATE OF PROCEDURE: [REDACTED]
LOCATION: Interventional Radiology/Pleural Suite

PRE-PROCEDURE DIAGNOSIS: Loculated right malignant pleural effusion, not amenable to simple thoracentesis.
POST-PROCEDURE DIAGNOSIS: Same.

PROCEDURE: Ultrasound-guided placement of small-bore pleural drainage catheter (pigtail) for malignant effusion.

PHYSICIAN: Olivia Harris, MD (Interventional Pulmonology)

INDICATION:
49-year-old male with metastatic renal cell carcinoma and recurrent right pleural effusion. Prior thoracenteses provided temporary relief; current ultrasound demonstrates loculated collections along the posterolateral chest wall. Decision made to place a small-bore pigtail catheter for ongoing drainage.

PROCEDURE DESCRIPTION:
With the patient in the left lateral decubitus position, a comprehensive ultrasound exam localized a large posterolateral fluid pocket without diaphragmatic or lung adhesions. Skin was marked in the mid-axillary line at the level of the 7th intercostal space.

After sterile prep and drape, local anesthesia was obtained with 1% lidocaine. Under real-time ultrasound guidance, an 18G needle was advanced into the collection with return of blood-tinged serous fluid. A 0.035" guidewire was passed and the tract was dilated.

A 12 Fr pigtail catheter was advanced over the wire into the pleural space and the pigtail was formed. The catheter was attached to a closed drainage system and secured with suture and anchoring device.

Approximately 700 mL of serosanguinous fluid drained during the procedure. The patient tolerated the procedure well.

COMPLICATIONS:
No evidence of pneumothorax or bleeding on immediate post-procedure ultrasound. Estimated blood loss < 10 mL.

DISPOSITION:
Patient [REDACTED] the oncology floor with the catheter to continuous drainage and plan for daily monitoring of output and consideration of talc slurry pleurodesis if lung remains expandable.

IMPRESSION:
Successful ultrasound-guided placement of a right pleural pigtail catheter (12 Fr) for ongoing drainage of malignant effusion."""

e10 = [
    {"label": "OBS_FINDING", **get_span(t10, "Loculated", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignant pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "small-bore pleural drainage catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "pigtail", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignant effusion", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "recurrent", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 2)},
    {"label": "OBS_LESION", **get_span(t10, "pleural effusion", 2)},
    {"label": "CTX_HISTORICAL", **get_span(t10, "Prior thoracenteses", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t10, "collections", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "posterolateral chest wall", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "small-bore pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 2)}, 
    {"label": "ANAT_PLEURA", **get_span(t10, "posterolateral", 2)}, 
    {"label": "OBS_LESION", **get_span(t10, "fluid pocket", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "7th intercostal space", 1)},
    {"label": "MEDICATION", **get_span(t10, "1% lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound guidance", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "18G needle", 1)},
    {"label": "OBS_LESION", **get_span(t10, "collection", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "blood-tinged serous fluid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "guidewire", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "12 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "pigtail catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural space", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "700 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "serosanguinous fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No evidence of pneumothorax", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "bleeding", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "10 mL", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 3)}, 
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 2)},
    {"label": "LATERALITY", **get_span(t10, "right", 3)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural", 5)},
    {"label": "DEV_CATHETER", **get_span(t10, "pigtail catheter", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "12 Fr", 2)},
    {"label": "OBS_LESION", **get_span(t10, "malignant effusion", 2)}
]
BATCH_DATA.append({"id": "700008", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
