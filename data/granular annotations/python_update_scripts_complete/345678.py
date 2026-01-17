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
# Note 1: 345678_syn_1
# ==========================================
text_1 = """Indication: Post. mediastinal mass (Schwannoma).
Proc: VATS excision.
- 3 ports.
- Mass at T6-T7.
- Dissected from nerve root.
- Nerve transected.
- Specimen extracted.
- 28Fr tube."""

entities_1 = [
    {"label": "ANAT_PLEURA", **get_span(text_1, "Post. mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Schwannoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "excision", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Mass", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "tube", 1)},
]
BATCH_DATA.append({"id": "345678_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 345678_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: Video-assisted thoracoscopic resection of posterior mediastinal neurogenic tumor.
FINDINGS: A 3.5 cm encapsulated schwannoma arising from the intercostal nerve at the T6-T7 level.
TECHNIQUE: A standard three-port VATS approach was utilized. The parietal pleura overlying the mass was incised. The tumor was dissected from the intercostal nerve of origin, which was transected to ensuring clear margins. The specimen was removed intact."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Video-assisted thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "resection", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "posterior mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "neurogenic tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "3.5 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "schwannoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "VATS", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
]
BATCH_DATA.append({"id": "345678_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 345678_syn_3
# ==========================================
text_3 = """CPT 32662: VATS excision of mediastinal tumor.
Location: Posterior mediastinum.
Pathology: Schwannoma.
Details: Dissection from spine/nerve root, complete excision, extraction."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "excision", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "Posterior mediastinum", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Schwannoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "excision", 2)},
]
BATCH_DATA.append({"id": "345678_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 345678_syn_4
# ==========================================
text_4 = """Procedure: VATS Posterior Mediastinal Mass Excision
1. Position: LLD.
2. Ports placed.
3. Mass id[REDACTED] T6-T7.
4. Pleura opened.
5. Tumor dissected off nerve.
6. Extracted.
7. Chest tube."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "VATS", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "Posterior Mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Excision", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Mass", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "Pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Tumor", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "345678_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 345678_syn_5
# ==========================================
text_5 = """Linda Petrova with the nerve tumor in the back chest vats 3 ports found the mass at t6 t7 dissected it out cut the nerve pulled it out in a bag checked for leaks none chest tube in."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "nerve tumor", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "back chest", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "vats", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "bag", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345678_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 345678_syn_6
# ==========================================
text_6 = """Video-assisted thoracoscopic excision of posterior mediastinal tumor. 3.5cm encapsulated mass arising from posterior mediastinum at T6-T7 level consistent with nerve sheath tumor. Overlying pleura incised. Tumor carefully dissected from intercostal nerve using bipolar cautery and blunt dissection. Nerve of origin transected proximally and distally with clear margins. Specimen placed in retrieval bag and extracted."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Video-assisted thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "excision", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "posterior mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "3.5cm", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "posterior mediastinum", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nerve sheath tumor", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "Tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "bipolar cautery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "retrieval bag", 1)},
]
BATCH_DATA.append({"id": "345678_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 345678_syn_7
# ==========================================
text_7 = """[Indication]
Posterior mediastinal mass (Schwannoma).
[Anesthesia]
General, DLT.
[Description]
3-port VATS. Mass dissected from T6-T7 intercostal nerve. Nerve transected. Mass removed.
[Plan]
Admit, monitor for CSF leak (none seen)."""

entities_7 = [
    {"label": "ANAT_PLEURA", **get_span(text_7, "Posterior mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Schwannoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "VATS", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Mass", 2)},
]
BATCH_DATA.append({"id": "345678_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 345678_syn_8
# ==========================================
text_8 = """[REDACTED] a tumor on a nerve near her spine. We used video-assisted surgery to remove it. Through three small ports, we located the mass and carefully separated it from the nerve, which had to be cut to remove the tumor completely. We checked to make sure there was no fluid leaking from the spine area and then closed up, leaving a chest tube."""

entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "video-assisted surgery", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345678_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 345678_syn_9
# ==========================================
text_9 = """Diagnosis: Posterior mediastinal nerve sheath neoplasm.
Action: Thoracoscopic ablation of mediastinal lesion.
Details: Lesion isolated at T6-T7. Separated from neural origin. Complete extraction performed. Drain placed."""

entities_9 = [
    {"label": "ANAT_PLEURA", **get_span(text_9, "Posterior mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nerve sheath neoplasm", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "ablation", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Lesion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Drain", 1)},
]
BATCH_DATA.append({"id": "345678_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 345678
# ==========================================
text_10 = """OPERATIVE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]

Attending Surgeon: Dr. Richard Chang, MD
First Assistant: Dr. Amy Liu, MD (Fellow)
Anesthesia: Dr. James Morrison, MD

Preop Dx: Right posterior mediastinal mass, neurogenic tumor suspected
Postop Dx: Posterior mediastinal schwannoma, completely excised

Procedure: Video-assisted thoracoscopic excision of posterior mediastinal tumor

Operative Details:

After induction of general anesthesia with double-lumen intubation, patient positioned in left lateral decubitus. Right chest prepared. Single-lung ventilation initiated.

Port placement:
- 12mm camera port at 7th ICS, posterior axillary line
- 5mm instrument port at 5th ICS, mid-axillary line  
- 5mm instrument port at 9th ICS, posterior axillary line

Inspection revealed 3.5cm encapsulated mass arising from posterior mediastinum at T6-T7 level, consistent with nerve sheath tumor. Overlying pleura incised. Tumor carefully dissected from intercostal nerve using bipolar cautery and blunt dissection. Nerve of origin transected proximally and distally with clear margins. Specimen placed in retrieval bag and extracted through enlarged camera port incision.

No CSF leak id[REDACTED]. Hemostasis achieved. 28Fr chest tube placed. Lung fully re-expanded. Wound closed.

Specimen: 3.7 x 3.2 x 2.8 cm encapsulated tumor to pathology.

EBL: 50mL
Complications: None

R. Chang, MD"""

entities_10 = [
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "posterior mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "neurogenic tumor", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Posterior mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "schwannoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Video-assisted thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "excision", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "posterior mediastinal", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 2)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "3.5cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "posterior mediastinum", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nerve sheath tumor", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "bipolar cautery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "retrieval bag", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "Lung fully re-expanded", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "3.7 x 3.2 x 2.8 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 4)},
    {"label": "MEAS_VOL", **get_span(text_10, "50mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
]
BATCH_DATA.append({"id": "345678", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)