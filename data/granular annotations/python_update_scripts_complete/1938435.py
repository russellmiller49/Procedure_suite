import sys
from pathlib import Path

# Set up the repository root (assuming this script is in specific subfolder, adjust as needed or use absolute path)
# Using the standard pattern provided in instructions
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the scripts directory to sys.path to import the utility
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
# Note 1: 1938435_syn_1
# ==========================================
id_1 = "1938435_syn_1"
text_1 = """Target: 28mm LUL nodule (PET-avid).
Nav: Galaxy electromagnetic. TiLT correction 1.0cm.
Tools: rEBUS (eccentric), 22G TBNA, Cytology Brush, BAL, Fiducial.
ROSE: Suspicious (necrotic/atypical).
Plan: Outpatient discharge."""

entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "28mm")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL")},
    {"label": "OBS_LESION", **get_span(text_1, "nodule")},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy electromagnetic")},
    {"label": "PROC_METHOD", **get_span(text_1, "TiLT")},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.0cm")},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS")},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G")},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA")},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology Brush")},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL")},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious")},
    {"label": "OBS_ROSE", **get_span(text_1, "necrotic")},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical")},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1938435_syn_2
# ==========================================
id_2 = "1938435_syn_2"
text_2 = """A 51-year-old male presented with a hypermetabolic LUL mass. Diagnostic bronchoscopy was performed utilizing the Galaxy robotic system. Registration accuracy was 3.7mm. Intraoperative C-arm tomosynthesis (TiLT) id[REDACTED] a 1.0cm target divergence. Following alignment, the lesion was sampled via multidimensional approach: TBNA, brushing, and lavage. A fiducial was deployed for potential SBRT."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LUL")},
    {"label": "OBS_LESION", **get_span(text_2, "mass")},
    {"label": "PROC_METHOD", **get_span(text_2, "Galaxy robotic system")},
    {"label": "MEAS_SIZE", **get_span(text_2, "3.7mm")},
    {"label": "PROC_METHOD", **get_span(text_2, "TiLT")},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.0cm")},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA")},
    {"label": "PROC_ACTION", **get_span(text_2, "lavage")},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1938435_syn_3
# ==========================================
id_3 = "1938435_syn_3"
text_3 = """Coding Summary:
31627 (Nav) + 31654 (EBUS) + 31629 (TBNA) + 31623 (Brush) + 31624 (BAL) + 31626 (Marker).
Documentation supports use of Galaxy navigation and TiLT+ verification for LUL target. Multiple distinct sampling tools utilized."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Nav")},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS")},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA")},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Brush")},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL")},
    {"label": "PROC_METHOD", **get_span(text_3, "Galaxy navigation")},
    {"label": "PROC_METHOD", **get_span(text_3, "TiLT+")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL")},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1938435_syn_4
# ==========================================
id_4 = "1938435_syn_4"
text_4 = """Procedure: LUL biopsy (Galaxy)
Steps:
- ETT.
- Nav to LB3.
- TiLT sweep: 1.0cm shift.
- rEBUS: Eccentric.
- TBNA x8.
- Brush x1.
- BAL.
- Marker placed.
ROSE: Atypical cells."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL")},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsy")},
    {"label": "PROC_METHOD", **get_span(text_4, "Galaxy")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB3")},
    {"label": "PROC_METHOD", **get_span(text_4, "TiLT")},
    {"label": "MEAS_SIZE", **get_span(text_4, "1.0cm")},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS")},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA")},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Brush")},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL")},
    {"label": "OBS_ROSE", **get_span(text_4, "Atypical cells")},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1938435_syn_5
# ==========================================
id_5 = "1938435_syn_5"
text_5 = """james has a pet avid nodule lul. we did the galaxy bronch today. registration ok. tilt showed the nodule was 1cm off from the ct so we fixed that. did needles brushes and a wash. also dropped a seed for radiation. rose guy said it looks weird necrotic. no issues."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lul")},
    {"label": "PROC_METHOD", **get_span(text_5, "galaxy bronch")},
    {"label": "PROC_METHOD", **get_span(text_5, "tilt")},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 2)},
    {"label": "MEAS_SIZE", **get_span(text_5, "1cm")},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brushes")},
    {"label": "OBS_ROSE", **get_span(text_5, "necrotic")},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1938435_syn_6
# ==========================================
id_6 = "1938435_syn_6"
text_6 = """PET-avid lung nodule 28mm in LUL. General anesthesia. Noah Galaxy bronchoscope used. Navigated to LB3. TiLT+ sweep revealed 1.0cm divergence. Corrected. rEBUS eccentric. TBNA 22G, Cytology brush, BAL, and Gold fiducial placement performed. ROSE necrotic debris with rare atypical cells. Discharged stable."""

entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "nodule")},
    {"label": "MEAS_SIZE", **get_span(text_6, "28mm")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL")},
    {"label": "PROC_METHOD", **get_span(text_6, "Noah Galaxy bronchoscope")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB3")},
    {"label": "PROC_METHOD", **get_span(text_6, "TiLT+")},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.0cm")},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS")},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA")},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22G")},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Cytology brush")},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL")},
    {"label": "OBS_ROSE", **get_span(text_6, "necrotic debris")},
    {"label": "OBS_ROSE", **get_span(text_6, "atypical cells")},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1938435_syn_7
# ==========================================
id_7 = "1938435_syn_7"
text_7 = """[Indication]
PET-avid nodule, 28mm LUL.
[Anesthesia]
General.
[Description]
Galaxy Nav to LB3. TiLT correction (1.0cm). rEBUS eccentric. TBNA, Brush, BAL performed. Fiducial placed.
[Plan]
Results in 5-7 days."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "nodule")},
    {"label": "MEAS_SIZE", **get_span(text_7, "28mm")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL")},
    {"label": "PROC_METHOD", **get_span(text_7, "Galaxy Nav")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB3")},
    {"label": "PROC_METHOD", **get_span(text_7, "TiLT")},
    {"label": "MEAS_SIZE", **get_span(text_7, "1.0cm")},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS")},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA")},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush")},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL")},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1938435_syn_8
# ==========================================
id_8 = "1938435_syn_8"
text_8 = """We went after a 28mm spot in the left upper lobe today. Using the Galaxy robot, we got close and used the TiLT spin to fine-tune our position, correcting a 1cm error. We threw the kitchen sink at it—needle biopsies, brushing, and a wash. We also left a gold marker behind just in case he needs radiation later. The preliminary slides look suspicious."""

entities_8 = [
    {"label": "MEAS_SIZE", **get_span(text_8, "28mm")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe")},
    {"label": "PROC_METHOD", **get_span(text_8, "Galaxy robot")},
    {"label": "PROC_METHOD", **get_span(text_8, "TiLT")},
    {"label": "MEAS_SIZE", **get_span(text_8, "1cm")},
    {"label": "PROC_ACTION", **get_span(text_8, "needle biopsies")},
    {"label": "PROC_ACTION", **get_span(text_8, "brushing")},
    {"label": "OBS_ROSE", **get_span(text_8, "suspicious")},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1938435_syn_9
# ==========================================
id_9 = "1938435_syn_9"
text_9 = """Indication: PET-avid mass.
Operation: Galaxy navigation to LUL. TiLT+ adjusted for 1.0cm divergence. Lesion localized with rEBUS. Sampled via TBNA and brush. Lavaged. Marker implanted. ROSE: Atypical."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "mass")},
    {"label": "PROC_METHOD", **get_span(text_9, "Galaxy navigation")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL")},
    {"label": "PROC_METHOD", **get_span(text_9, "TiLT+")},
    {"label": "MEAS_SIZE", **get_span(text_9, "1.0cm")},
    {"label": "PROC_METHOD", **get_span(text_9, "rEBUS")},
    {"label": "PROC_ACTION", **get_span(text_9, "TBNA")},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "brush")},
    {"label": "PROC_ACTION", **get_span(text_9, "Lavaged")},
    {"label": "OBS_ROSE", **get_span(text_9, "Atypical")},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1938435
# ==========================================
id_10 = "1938435"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: 8/7/1974
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez
Fellow: Dr. Maria Santos (PGY-6)

Indication: PET-avid lung nodule
Target: 28mm nodule in LUL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t13\t350\t8\t100\t5\t22

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the LUL (LB3) based on the pre-operative CT navigational plan. Registration accuracy: 3.7mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 1.0cm divergence between the pre-op CT target and the actual lesion location due to respiratory motion.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Eccentric.

Transbronchial needle aspiration performed with 22G needle. 8 passes obtained. Samples sent for Cytology and Cell block.

Cytology brushings obtained. Samples sent for Cytology.

Bronchoalveolar lavage performed at target segment. 60mL instilled, 19mL return. Sent for Cytology and Culture.

Gold fiducial marker placed under TiLT-augmented fluoroscopic guidance for SBRT planning.

ROSE Result: Necrotic debris with rare atypical cells

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Rodriguez, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "28mm")},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea")},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina")},
    {"label": "PROC_METHOD", **get_span(text_10, "Noah Galaxy bronchoscope")},
    {"label": "PROC_METHOD", **get_span(text_10, "electromagnetic field generator")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB3")},
    {"label": "MEAS_SIZE", **get_span(text_10, "3.7mm")},
    {"label": "PROC_METHOD", **get_span(text_10, "Tool-in-Lesion Tomosynthesis (TiLT+)")},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.0cm")},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration")},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G")},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoalveolar lavage")},
    {"label": "MEAS_VOL", **get_span(text_10, "60mL")},
    {"label": "MEAS_VOL", **get_span(text_10, "19mL")},
    {"label": "OBS_ROSE", **get_span(text_10, "Necrotic debris")},
    {"label": "OBS_ROSE", **get_span(text_10, "atypical cells")},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)