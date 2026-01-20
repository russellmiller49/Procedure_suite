import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# Assuming saved in: data/granular_annotations/Python_update_scripts/
# Parents[3] is the Repo Root.
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

BATCH_DATA = []

# ==========================================
# Note 1: 4168297_syn_1
# ==========================================
id_1 = "4168297_syn_1"
text_1 = """Procedure: Rt PleurX Catheter Placement.
Indication: Malignant pleural effusion.
US: Free flowing fluid.
Steps: Local. Tunnel 7.5cm. Seldinger technique. 15.5Fr catheter. 1550mL drained.
Comp: None. CXR confirms placement."""

entities_1 = [
    {"label": "LATERALITY",         **get_span(text_1, "Rt", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "PleurX", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "Catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "Placement", 1)},
    {"label": "OBS_LESION",         **get_span(text_1, "Malignant pleural effusion", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "US", 1)},
    {"label": "OBS_FINDING",        **get_span(text_1, "Free flowing fluid", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "Tunnel", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "7.5cm", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_1, "15.5Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "catheter", 1)},
    {"label": "MEAS_VOL",           **get_span(text_1, "1550mL", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "drained", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "CXR", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4168297_syn_2
# ==========================================
id_2 = "4168297_syn_2"
text_2 = """OPERATIVE REPORT: Tunneled Pleural Catheter Insertion.
INDICATION: Recurrent malignant pleural effusion (Adenocarcinoma).
DESCRIPTION: Under ultrasound guidance, the right pleural space was id[REDACTED]. A subcutaneous tunnel was created. Using the Seldinger technique, a 15.5 Fr PleurX indwelling pleural catheter was inserted. The cuff was positioned within the tunnel. 1,550 mL of clear yellow fluid was drained. Post-procedure imaging confirmed appropriate positioning and lung re-expansion."""

entities_2 = [
    {"label": "DEV_CATHETER",       **get_span(text_2, "Tunneled Pleural Catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_2, "Insertion", 1)},
    {"label": "OBS_LESION",         **get_span(text_2, "malignant pleural effusion", 1)},
    {"label": "OBS_LESION",         **get_span(text_2, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD",        **get_span(text_2, "ultrasound", 1)},
    {"label": "LATERALITY",         **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_2, "pleural space", 1)},
    {"label": "PROC_ACTION",        **get_span(text_2, "tunnel", 1)},
    {"label": "PROC_METHOD",        **get_span(text_2, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_2, "15.5 Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_2, "PleurX", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_2, "indwelling pleural catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_2, "inserted", 1)},
    {"label": "MEAS_VOL",           **get_span(text_2, "1,550 mL", 1)},
    {"label": "OBS_FINDING",        **get_span(text_2, "clear yellow fluid", 1)},
    {"label": "PROC_ACTION",        **get_span(text_2, "drained", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_2, "lung re-expansion", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4168297_syn_3
# ==========================================
id_3 = "4168297_syn_3"
text_3 = """CPT 32550: Insertion of indwelling tunneled pleural catheter.
Guidance: Ultrasound used for site selection and wire placement.
Device: 15.5 Fr PleurX.
Drainage: 1550 mL.
Site: [REDACTED]"""

entities_3 = [
    {"label": "PROC_ACTION",        **get_span(text_3, "Insertion", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_3, "indwelling tunneled pleural catheter", 1)},
    {"label": "PROC_METHOD",        **get_span(text_3, "Ultrasound", 1)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_3, "15.5 Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_3, "PleurX", 1)},
    {"label": "MEAS_VOL",           **get_span(text_3, "1550 mL", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4168297_syn_4
# ==========================================
id_4 = "4168297_syn_4"
text_4 = """Procedure: IPC Placement
Patient: [REDACTED]
Attending: Dr. Reyes

1. US scan: Large Rt effusion.
2. Prep/Drape/Local.
3. Tunnel created.
4. Catheter inserted over wire.
5. Fluid drained (1.5L).
6. Teaching done with patient."""

entities_4 = [
    {"label": "DEV_CATHETER",       **get_span(text_4, "IPC", 1)},
    {"label": "PROC_ACTION",        **get_span(text_4, "Placement", 1)},
    {"label": "PROC_METHOD",        **get_span(text_4, "US", 1)},
    {"label": "LATERALITY",         **get_span(text_4, "Rt", 1)},
    {"label": "OBS_LESION",         **get_span(text_4, "effusion", 1)},
    {"label": "PROC_ACTION",        **get_span(text_4, "Tunnel", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_4, "Catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_4, "inserted", 1)},
    {"label": "PROC_ACTION",        **get_span(text_4, "drained", 1)},
    {"label": "MEAS_VOL",           **get_span(text_4, "1.5L", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4168297_syn_5
# ==========================================
id_5 = "4168297_syn_5"
text_5 = """[REDACTED] needed a pleurx for her cancer fluid. right side. dr reyes doing it. we scanned it big effusion. numbed her up made the tunnel put the catheter in. drained about a liter and a half of yellow fluid. she felt way better. taught her how to use the bottles. xray looked good."""

entities_5 = [
    {"label": "DEV_CATHETER",       **get_span(text_5, "pleurx", 1)},
    {"label": "OBS_LESION",         **get_span(text_5, "cancer", 1)},
    {"label": "OBS_FINDING",        **get_span(text_5, "fluid", 1)},
    {"label": "LATERALITY",         **get_span(text_5, "right", 1)},
    {"label": "OBS_LESION",         **get_span(text_5, "effusion", 1)},
    {"label": "PROC_ACTION",        **get_span(text_5, "tunnel", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_5, "catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_5, "drained", 1)},
    {"label": "MEAS_VOL",           **get_span(text_5, "liter and a half", 1)},
    {"label": "OBS_FINDING",        **get_span(text_5, "yellow fluid", 1)},
    {"label": "PROC_METHOD",        **get_span(text_5, "xray", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4168297_syn_6
# ==========================================
id_6 = "4168297_syn_6"
text_6 = """Ultrasound-guided placement of right indwelling pleural catheter (PleurX) performed for malignant effusion. 15.5 Fr catheter tunneled and inserted without difficulty. 1,550 mL fluid drained. Post-procedure CXR showed good position and re-expansion. Patient educated on home drainage."""

entities_6 = [
    {"label": "PROC_METHOD",        **get_span(text_6, "Ultrasound", 1)},
    {"label": "PROC_ACTION",        **get_span(text_6, "placement", 1)},
    {"label": "LATERALITY",         **get_span(text_6, "right", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_6, "indwelling pleural catheter", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_6, "PleurX", 1)},
    {"label": "OBS_LESION",         **get_span(text_6, "malignant effusion", 1)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_6, "15.5 Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_6, "catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_6, "tunneled", 1)},
    {"label": "PROC_ACTION",        **get_span(text_6, "inserted", 1)},
    {"label": "MEAS_VOL",           **get_span(text_6, "1,550 mL", 1)},
    {"label": "OBS_FINDING",        **get_span(text_6, "fluid", 1)},
    {"label": "PROC_ACTION",        **get_span(text_6, "drained", 1)},
    {"label": "PROC_METHOD",        **get_span(text_6, "CXR", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_6, "re-expansion", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4168297_syn_7
# ==========================================
id_7 = "4168297_syn_7"
text_7 = """[Indication]
Recurrent malignant pleural effusion (Rt).
[Anesthesia]
Local (Lidocaine).
[Description]
US guidance. Tunnel created. PleurX catheter inserted. 1550mL drained.
[Plan]
Drain Q2 days. Home health setup."""

entities_7 = [
    {"label": "OBS_LESION",         **get_span(text_7, "malignant pleural effusion", 1)},
    {"label": "LATERALITY",         **get_span(text_7, "Rt", 1)},
    {"label": "MEDICATION",         **get_span(text_7, "Lidocaine", 1)},
    {"label": "PROC_METHOD",        **get_span(text_7, "US", 1)},
    {"label": "PROC_ACTION",        **get_span(text_7, "Tunnel", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_7, "PleurX", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_7, "catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_7, "inserted", 1)},
    {"label": "MEAS_VOL",           **get_span(text_7, "1550mL", 1)},
    {"label": "PROC_ACTION",        **get_span(text_7, "drained", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4168297_syn_8
# ==========================================
id_8 = "4168297_syn_8"
text_8 = """[REDACTED] suffering from fluid buildup due to her lung cancer. To help manage this at home, we placed a PleurX catheter today. We used ultrasound to find the best spot on her right side. We numbed the area, created a tunnel under the skin, and inserted the drainage tube into the pleural space. We drained over a liter of fluid immediately, which helped her breathing significantly. We taught her and her husband how to use the drainage kits at home."""

entities_8 = [
    {"label": "OBS_LESION",         **get_span(text_8, "fluid buildup", 1)},
    {"label": "OBS_LESION",         **get_span(text_8, "lung cancer", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_8, "PleurX", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_8, "catheter", 1)},
    {"label": "PROC_METHOD",        **get_span(text_8, "ultrasound", 1)},
    {"label": "LATERALITY",         **get_span(text_8, "right", 1)},
    {"label": "PROC_ACTION",        **get_span(text_8, "tunnel", 1)},
    {"label": "PROC_ACTION",        **get_span(text_8, "inserted", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_8, "drainage tube", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_8, "pleural space", 1)},
    {"label": "PROC_ACTION",        **get_span(text_8, "drained", 1)},
    {"label": "MEAS_VOL",           **get_span(text_8, "liter", 1)},
    {"label": "OBS_FINDING",        **get_span(text_8, "fluid", 2)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4168297_syn_9
# ==========================================
id_9 = "4168297_syn_9"
text_9 = """Procedure: Implantation of tunneled pleural drainage system (32550).
Context: Malignant hydrothorax.
Action: Sonographic localization. Catheter tunneled and deployed into pleural cavity. Effusion evacuated (1550mL).
Outcome: Symptomatic relief. Device functional."""

entities_9 = [
    {"label": "PROC_ACTION",        **get_span(text_9, "Implantation", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_9, "tunneled pleural drainage system", 1)},
    {"label": "OBS_LESION",         **get_span(text_9, "Malignant hydrothorax", 1)},
    {"label": "PROC_METHOD",        **get_span(text_9, "Sonographic", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_9, "Catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "tunneled", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "deployed", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_9, "pleural cavity", 1)},
    {"label": "OBS_LESION",         **get_span(text_9, "Effusion", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "evacuated", 1)},
    {"label": "MEAS_VOL",           **get_span(text_9, "1550mL", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4168297
# ==========================================
id_10 = "4168297"
text_10 = """**PATIENT INFORMATION:**
- Name: Jennifer Kim
- MRN: [REDACTED]
- DOB: [REDACTED]
- Date of Procedure: [REDACTED]
- Procedure Time: 10:00-10:55

**INSTITUTION:[REDACTED]

**ATTENDING PHYSICIAN:** Dr. Monica Reyes, MD (Interventional Pulmonology)  
**ASSISTANT:** Sarah Chen, PA-C

**INDICATION:**
48-year-old female with stage IV non-small cell lung cancer (adenocarcinoma) and symptomatic recurrent right malignant pleural effusion. Patient receiving immunotherapy, desires to minimize clinic visits and maintain active lifestyle.

**PRE-PROCEDURE:**
- Comprehensive informed consent obtained
- Patient educated on catheter management, drainage technique, and infection prevention
- Timeout performed with entire procedural team
- Ultrasound examination: Large right pleural effusion, maximum depth 9.8 cm, free-flowing, no loculations
- Recent CT chest (5 days ago): No evidence of trapped lung, appropriate candidate for pleurodesis
- Labs: WBC 5.2K, Platelets 198K (decreased from baseline due to recent chemo)
- Vital signs: BP 118/68, HR 76, SpO2 93% on RA

**PROCEDURE DETAILS:**
- Patient positioned in left lateral decubitus, comfortable positioning with pillows
- Right lateral chest, 5th intercostal space, mid-axillary line id[REDACTED]
- Site marked with ultrasound guidance, safe window confirmed
- Chlorhexidine prep, sterile drape placement
- Local anesthesia: 18 mL 1% lidocaine along planned tract
- Small 1 cm incision with #11 blade
- Tunneling performed to anterior chest wall (tunnel length 7.5 cm)
- Tunneling device used to create tract
- Guidewire placed under direct ultrasound visualization
- 15.5 French PleurX catheter advanced over wire smoothly
- Catheter tip positioned and confirmed to be coiled in pleural space
- Safety suture placed, cuff in appropriate subcutaneous position
- Valve connector attached
- Initial drainage via vacuum bottles: 1,550 mL clear yellow fluid
- Drainage well tolerated, no re-expansion symptoms
- Post-drainage ultrasound: minimal residual fluid, good lung expansion

**CATHETER SPECIFICATIONS:**
- Type: PleurX drainage catheter system
- French Size: 15.5 Fr
- Tunnel length: 7.5 cm

**SPECIMENS SENT:**
- Pleural fluid cytology (initial drainage specimen)

**POST-PROCEDURE:**
- Procedure completed successfully
- Post-procedure chest X-ray: IPC in excellent position, near-complete drainage of effusion, no pneumothorax
- Sterile dressing applied per protocol
- Comprehensive teaching session with patient and spouse (1.5 hours)
- Patient demonstrated proper drainage technique with return demonstration
- Home health referral placed for first week support
- Written instructions and video resources provided
- Emergency contact information given
- Drainage supplies dispensed (vacuum bottles, dressing supplies)
- Vital signs: BP 116/66, HR 72, SpO2 97% on RA
- Patient very pleased with symptomatic relief

**COMPLICATIONS:** None

**DRAINAGE SCHEDULE:** Every other day initially, will reassess based on output volumes

**ASSESSMENT:** Successful ultrasound-guided placement of right indwelling pleural catheter for management of recurrent malignant pleural effusion. Excellent initial drainage with good lung expansion. Reasonable expectation for spontaneous pleurodesis given no trapped lung and good lung expansion.

**PLAN:**
- Drainage every other day initially
- Record all drainage volumes in provided log
- Home health visits first week for catheter assessment and drainage assistance
- Monitor for signs of spontaneous pleurodesis (decreasing volumes to <50 mL per drainage session)
- Report fever, increasing redness/drainage at site, catheter malfunction, or worsening dyspnea
- Follow-up clinic visit in 3 weeks
- Continue immunotherapy as scheduled (cleared by oncology)
- If pleurodesis achieved (minimal drainage x 2 consecutive drainages), schedule catheter removal
- Patient given 24/7 contact number for concerns"""

entities_10 = [
    {"label": "CTX_TIME",           **get_span(text_10, "10:00-10:55", 1)},
    {"label": "OBS_LESION",         **get_span(text_10, "non-small cell lung cancer", 1)},
    {"label": "OBS_LESION",         **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "LATERALITY",         **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION",         **get_span(text_10, "malignant pleural effusion", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "Ultrasound", 1)},
    {"label": "LATERALITY",         **get_span(text_10, "right", 2)},
    {"label": "OBS_LESION",         **get_span(text_10, "pleural effusion", 2)},
    {"label": "MEAS_SIZE",          **get_span(text_10, "9.8 cm", 1)},
    {"label": "OBS_FINDING",        **get_span(text_10, "free-flowing", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "CT chest", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_10, "Right lateral chest", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_10, "5th intercostal space", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_10, "mid-axillary line", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "ultrasound", 2)},
    {"label": "MEDICATION",         **get_span(text_10, "lidocaine", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_10, "1 cm", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "#11 blade", 1)},
    {"label": "PROC_ACTION",        **get_span(text_10, "Tunneling", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_10, "anterior chest wall", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_10, "7.5 cm", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "Tunneling device", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "Guidewire", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "ultrasound", 3)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_10, "15.5 French", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "PleurX", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "catheter", 2)},
    {"label": "ANAT_PLEURA",        **get_span(text_10, "pleural space", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "suture", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "Valve connector", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "vacuum bottles", 1)},
    {"label": "MEAS_VOL",           **get_span(text_10, "1,550 mL", 1)},
    {"label": "OBS_FINDING",        **get_span(text_10, "clear yellow fluid", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "ultrasound", 4)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_10, "good lung expansion", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "PleurX drainage catheter system", 1)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_10, "15.5 Fr", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_10, "7.5 cm", 2)},
    {"label": "SPECIMEN",           **get_span(text_10, "Pleural fluid", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "chest X-ray", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "IPC", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_10, "near-complete drainage", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no pneumothorax", 1)},
    {"label": "PROC_ACTION",        **get_span(text_10, "placement", 2)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "indwelling pleural catheter", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_10, "good lung expansion", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)