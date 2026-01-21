import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
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
# Note 1: 1034928_syn_1
# ==========================================
t1 = """Procedure: PleurX IPC placement Rt Hemithorax.
- US guidance used.
- Local anesthetic.
- Seldinger technique: 18G needle -> wire -> dilators -> sheath.
- Catheter tunneled 6cm.
- Fluid: 1200mL serous.
- No complications. CXR pending."""

e1 = [
    {"label": "DEV_CATHETER", **get_span(t1, "PleurX", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "IPC", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "placement", 1)},
    {"label": "LATERALITY", **get_span(t1, "Rt", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "Hemithorax", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Seldinger technique", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "18G needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "wire", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "dilators", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "sheath", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "tunneled", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "6cm", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "1200mL", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "serous", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No complications", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1034928_syn_2
# ==========================================
t2 = """OPERATIVE NARRATIVE: The patient presented with a recurrent, malignant right-sided pleural effusion. Under ultrasound guidance, the pleural space was accessed at the 5th intercostal space. A subcutaneous tunnel was created, and the indwelling pleural catheter was advanced into the pleural cavity. Approximately 1.2 liters of exudative fluid were drained. The catheter was secured, and the patient tolerated the procedure without hemodynamic compromise."""

e2 = [
    {"label": "OBS_LESION", **get_span(t2, "pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(t2, "right-sided", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ultrasound", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "5th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "subcutaneous tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "indwelling pleural catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural cavity", 1)},
    {"label": "MEAS_VOL", **get_span(t2, "1.2 liters", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "exudative", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "catheter", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1034928_syn_3
# ==========================================
t3 = """Service: Insertion of Tunneled Pleural Catheter (32550).
Guidance: Ultrasound (76942) for site selection and safety.
Details: Right hemithorax. Subcutaneous tunneling performed. Cuff positioned appropriately.
Drainage: 1200 mL removed to confirm function.
Status: Successful placement."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Insertion", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "Tunneled Pleural Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Ultrasound", 1)},
    {"label": "LATERALITY", **get_span(t3, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "hemithorax", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Subcutaneous tunneling", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Cuff", 1)},
    {"label": "MEAS_VOL", **get_span(t3, "1200 mL", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "placement", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1034928_syn_4
# ==========================================
t4 = """Resident Note
Procedure: PleurX Placement
Attending: Dr. Green
1. US check - big effusion right side.
2. Local lidocaine.
3. Stick w/ needle, wire down.
4. Tunneled catheter under skin.
5. Peel-away sheath in.
6. Catheter in, drained 1.2L.
7. Stitched up.
Plan: Home health teaching."""

e4 = [
    {"label": "DEV_CATHETER", **get_span(t4, "PleurX", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Placement", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "US", 1)},
    {"label": "OBS_LESION", **get_span(t4, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t4, "right side", 1)},
    {"label": "MEDICATION", **get_span(t4, "lidocaine", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "wire", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Tunneled", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Peel-away sheath", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(t4, "1.2L", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1034928_syn_5
# ==========================================
t5 = """ipc placement note pt patricia johnson. right side effusion recurrent cancer. did the ultrasound marked spot. numbed her up good with lido. put the wire in tunneled the catheter about 6cm. dilated track put sheath in. catheter went in easy drained 1200cc straw fluid. stitched it up dressing on. no issues."""

e5 = [
    {"label": "DEV_CATHETER", **get_span(t5, "ipc", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "placement", 1)},
    {"label": "LATERALITY", **get_span(t5, "right side", 1)},
    {"label": "OBS_LESION", **get_span(t5, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ultrasound", 1)},
    {"label": "MEDICATION", **get_span(t5, "lido", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "wire", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "tunneled", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "6cm", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "sheath", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "catheter", 2)},
    {"label": "PROC_ACTION", **get_span(t5, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "1200cc", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "straw fluid", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1034928_syn_6
# ==========================================
t6 = """Indwelling Tunneled Pleural Catheter Placement was performed on a 74-year-old female with metastatic breast cancer. Ultrasound guidance confirmed a large right pleural effusion. Under local anesthesia, the pleural space was accessed. A subcutaneous tunnel was created. The catheter was inserted and 1200 mL of serous fluid was drained. The procedure was uncomplicated."""

e6 = [
    {"label": "DEV_CATHETER", **get_span(t6, "Indwelling Tunneled Pleural Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Placement", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Ultrasound", 1)},
    {"label": "LATERALITY", **get_span(t6, "right", 1)},
    {"label": "OBS_LESION", **get_span(t6, "pleural effusion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "subcutaneous tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "inserted", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "1200 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "serous", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "drained", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1034928_syn_7
# ==========================================
t7 = """[Indication]
Recurrent malignant pleural effusion, Right.
[Anesthesia]
Local (Lidocaine 1%).
[Description]
US-guided access. Subcutaneous tunnel created. PleurX catheter inserted. 1200mL drained. Cuff positioned. Incisions closed.
[Plan]
Home drainage education."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(t7, "Right", 1)},
    {"label": "MEDICATION", **get_span(t7, "Lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "US", 1)},
    {"label": "ANAT_PLEURA", **get_span(t7, "Subcutaneous tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "inserted", 1)},
    {"label": "MEAS_VOL", **get_span(t7, "1200mL", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "drained", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Cuff", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1034928_syn_8
# ==========================================
t8 = """[REDACTED] to the procedure room for management of her recurrent right pleural effusion. We utilized ultrasound to id[REDACTED] a safe pocket of fluid. After anesthetizing the area, we placed a tunneled PleurX catheter using the standard Seldinger technique. The catheter was tunneled subcutaneously before entering the pleural space. We drained 1200mL of fluid to verify patency. The patient remained stable throughout."""

e8 = [
    {"label": "LATERALITY", **get_span(t8, "right", 1)},
    {"label": "OBS_LESION", **get_span(t8, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "tunneled PleurX catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "tunneled", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "pleural space", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(t8, "1200mL", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1034928_syn_9
# ==========================================
t9 = """Procedure: Implantation of long-term pleural drainage device.
Context: Persistent fluid accumulation due to malignancy.
Technique: Sonographic localization. Creation of subcutaneous tract. Deployment of cuffed catheter into pleural cavity.
Output: 1.2 Liters serous fluid.
Outcome: Successful implantation."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Implantation", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "long-term pleural drainage device", 1)},
    {"label": "OBS_LESION", **get_span(t9, "fluid accumulation", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Sonographic", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "subcutaneous tract", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Deployment", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "cuffed catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "pleural cavity", 1)},
    {"label": "MEAS_VOL", **get_span(t9, "1.2 Liters", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "serous", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "implantation", 1)},
]
BATCH_DATA.append({"id": "1034928_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1034928 (Original)
# ==========================================
t10 = """PATIENT: [REDACTED], 74-year-old Female
MRN: [REDACTED]
INDICATION FOR OPERATION: Ms. [REDACTED] is a 74-year-old female with metastatic breast cancer presenting with recurrent symptomatic right-sided malignant pleural effusion despite two recent therapeutic thoracenteses. The nature, purpose, risks, benefits and alternatives to tunneled pleural catheter placement were discussed with the patient in detail. Patient indicated a wish to proceed and informed consent was signed.
PREOPERATIVE DIAGNOSIS: Recurrent malignant pleural effusion, right
POSTOPERATIVE DIAGNOSIS: Same
PROCEDURE: Indwelling Tunneled Pleural Catheter Placement (CPT 32550)
ATTENDING: Dr. Rachel Green
ASSISTANT: Dr. Paul Anderson, Fellow
Support Staff:

RN: Jennifer Martinez
RT: David Lee

ANESTHESIA: Local anesthesia with Lidocaine 1%
MONITORING: Pulse oximetry, blood pressure
INSTRUMENT: CareFusion PleurX catheter system, ultrasound machine
ESTIMATED BLOOD LOSS: <10 mL
COMPLICATIONS: None
PROCEDURE IN DETAIL:
After timeout, all procedure related images were saved and archived.
PATIENT [REDACTED]: Sitting upright at 60 degrees, right arm elevated
CHEST ULTRASOUND FINDINGS: (Image saved and printed)

Hemithorax: Right
Pleural Effusion Volume: Large
Echogenicity: Anechoic
Loculations: None
Diaphragmatic Motion: Diminished
Lung sliding before procedure: Present
Lung consolidation/atelectasis: Present (compressive atelectasis)
Pleura: Mildly thickened, no nodularity visualized

The right lateral chest was prepped and draped in sterile fashion. Ultrasound guidance was used to id[REDACTED] the optimal insertion site and confirm absence of vital structures.
ANESTHESIA: Lidocaine 1%: 20ml injected at skin, subcutaneous tissue, pleura, and tunnel tract
Entry Site: Right 5th Intercostal Space
Location: [REDACTED]
Procedure Steps:

A finder needle (18G) was used to enter the pleural space in the 5th intercostal space along the midaxillary line under ultrasound guidance. Pleural fluid was easily aspirated (straw-colored fluid). The needle was withdrawn and a 0.038" guidewire was placed into the pleural space through the finder catheter.
Two 5mm skin incisions were made: one at the guidewire entry site and another 5-6cm away anteriorly for the catheter exit site.
The tunneling device was used to tunnel the catheter in the subcutaneous tissue from the exit site to the pleural entry site. Tunnel length: 6cm.
Serial dilation over the guidewire was achieved using 10Fr and 15Fr dilators. The peel-away introducer sheath (16Fr) was placed over the guidewire and advanced into the pleural space.
The guidewire was removed. The PleurX catheter was then inserted through the introducer sheath into the pleural space until all fenestrations were within the pleural cavity (approximately 15cm inserted).
The introducer sheath was peeled away and removed. The pleural entry site incision was closed with a 3-0 absorbable suture (Vicryl).
The catheter cuff was positioned in the subcutaneous tunnel approximately 1cm from the exit site. The catheter was secured to the skin at the exit site using 2-0 nylon sutures.
Sterile dressings were applied (foam and transparent dressing).

Exit site: 5th Intercostal space, anterior axillary line
Initial Drainage:
The PleurX vacuum bottle was attached and drainage initiated.

Fluid Removed: 1200 mL
Appearance: Serous, straw-colored

Pleural Pressures Measured:

Opening: -8 cmH₂O
500ml: -10 cmH₂O
1000ml: -15 cmH₂O
1200ml: -18 cmH₂O (stopped due to chest discomfort)

Drainage device: Initially vacuum bottle, then capped after drainage complete
SPECIMEN(S):

Pleural fluid (cytology, chemistry, cell count)

Post-procedure ultrasound showed reduced effusion volume with no pneumothorax. Post-procedure CXR ordered.
The patient tolerated the procedure well with only mild discomfort during catheter insertion. The attending, Dr. Green, was present throughout the entire procedure.
IMPRESSION/PLAN: Ms. [REDACTED] underwent successful placement of right-sided tunneled pleural catheter for recurrent malignant effusion. Procedure completed without complications. Patient and family educated on catheter care and home drainage protocol. Drainage every other day initially, adjusting based on output. Follow-up appointment in 2 weeks. Home health nursing arranged for first drainage. Patient given written discharge instructions and emergency contact information."""

e10 = [
    {"label": "LATERALITY", **get_span(t10, "right-sided", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignant pleural effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "tunneled pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 1)},
    {"label": "OBS_LESION", **get_span(t10, "pleural effusion", 2)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Indwelling Tunneled Pleural Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Placement", 1)},
    {"label": "MEDICATION", **get_span(t10, "Lidocaine", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "PleurX catheter system", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound machine", 1)},
    {"label": "LATERALITY", **get_span(t10, "Right", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Pleural Effusion", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Lung consolidation", 1)},
    {"label": "OBS_LESION", **get_span(t10, "atelectasis", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Pleura", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound guidance", 1)},
    {"label": "MEDICATION", **get_span(t10, "Lidocaine", 2)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Right 5th Intercostal Space", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "finder needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "18G", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "5th intercostal space", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound guidance", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "straw-colored", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "guidewire", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "finder catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "tunneling device", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "tunnel", 2)},
    {"label": "DEV_CATHETER", **get_span(t10, "catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "6cm", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t10, "10Fr", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t10, "15Fr", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "introducer sheath", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t10, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "PleurX catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural cavity", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "catheter cuff", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "5th Intercostal space", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "1200 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Serous", 1)},
    {"label": "MEAS_PRESS", **get_span(t10, "-8 cmH₂O", 1)},
    {"label": "MEAS_PRESS", **get_span(t10, "-10 cmH₂O", 1)},
    {"label": "MEAS_PRESS", **get_span(t10, "-15 cmH₂O", 1)},
    {"label": "MEAS_PRESS", **get_span(t10, "-18 cmH₂O", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "without complications", 1)},
]
BATCH_DATA.append({"id": "1034928", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)