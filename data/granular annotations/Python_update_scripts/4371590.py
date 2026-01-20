import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

# Container for all cases
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
# Note 1: 4371590_syn_1
# ==========================================
id_1 = "4371590_syn_1"
text_1 = """Procedure: Ion Bronchoscopy LLL.
Target: 9mm nodule (LB9).
Nav: Ion, rEBUS (adjacent), CBCT.
Actions:
- TBNA (21G): 6 passes.
- Cryobiopsy (1.7mm): 5 samples.
- Fiducial: 1 gold marker.
- Brush: 2 samples.
- BAL: 60cc.
ROSE: Squamous cell carcinoma.
Complications: None."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 samples", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "1", 3)}, # "1 gold marker"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "gold marker", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "60cc", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4371590_syn_2
# ==========================================
id_2 = "4371590_syn_2"
text_2 = """OPERATIVE REPORT: [REDACTED] bronchoscopy for a solitary 9mm LLL nodule. Navigation to the lateral-basal segment (LB9) was achieved via the Ion system. Despite the small size, rEBUS (adjacent) and CBCT provided confirmation. We obtained diagnostic tissue via TBNA (21G), cryobiopsy (1.7mm), and brushing. A fiducial was placed to guide therapy. BAL was performed. ROSE confirmed squamous cell carcinoma."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lateral-basal segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.7mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "fiducial", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "squamous cell carcinoma", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4371590_syn_3
# ==========================================
id_3 = "4371590_syn_3"
text_3 = """CPT Codes:
- 31626: Fiducial.
- 31629: TBNA.
- 31628: Cryobiopsy.
- 31623: Brush.
- 31624: BAL.
- 31627: Nav.
- 31654: EBUS.
Target: 9mm LLL nodule. ROSE: Positive for malignancy."""

entities_3 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Fiducial", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodule", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "Positive for malignancy", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4371590_syn_4
# ==========================================
id_4 = "4371590_syn_4"
text_4 = """Resident Note
Patient: [REDACTED]
Site: LLL Nodule (9mm)

- GA induced.
- Ion Nav to LB9.
- rEBUS: Adjacent.
- CBCT: Confirmed.
- TBNA x6.
- Cryo x5.
- Fiducial placed.
- Brush x2.
- BAL done.
- ROSE: Squamous cell CA."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "9mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Cryo", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Fiducial", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Squamous cell CA", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4371590_syn_5
# ==========================================
id_5 = "4371590_syn_5"
text_5 = """donald taylor [REDACTED] lll nodule small 9mm used ion robot nav to lb9 radial ebus adjacent cone beam ct confirmed. did tbna 21g cryo 1.7mm brush and wash. placed a fiducial marker. rose came back squamous cell carcinoma. no complications discharge planned."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "9mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ion robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lb9", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial ebus", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "cone beam ct", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "tbna", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "21g", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cryo", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "1.7mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "wash", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no complications", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4371590_syn_6
# ==========================================
id_6 = "4371590_syn_6"
text_6 = """The patient underwent general anesthesia for Ion robotic bronchoscopy of a 9mm LLL nodule. Navigation to the Lateral-Basal segment was confirmed with rEBUS and Cone Beam CT. Biopsies included TBNA, cryobiopsy, and brushing. A fiducial marker was placed. BAL was collected. ROSE was positive for squamous cell carcinoma."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Ion robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Lateral-Basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "cryobiopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "fiducial marker", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "squamous cell carcinoma", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4371590_syn_7
# ==========================================
id_7 = "4371590_syn_7"
text_7 = """[Indication]
9mm LLL nodule.
[Anesthesia]
General.
[Description]
Ion navigation to LB9. Confirmed via rEBUS/CBCT.
Intervention:
- TBNA
- Cryobiopsy
- Fiducial
- Brush
- BAL
[Plan]
Oncology referral."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Fiducial", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4371590_syn_8
# ==========================================
id_8 = "4371590_syn_8"
text_8 = """[REDACTED] a small 9mm nodule in his lower left lung. We used the robotic system to navigate to the lateral-basal segment. We confirmed the location with ultrasound and CT. We took multiple samples using a needle, freezing probe, and brush, and washed the area. We also placed a gold marker. The pathologist confirmed squamous cell carcinoma on site."""

entities_8 = [
    {"label": "MEAS_SIZE", **get_span(text_8, "9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lower left lung", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lateral-basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "CT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "freezing probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "washed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "gold marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "squamous cell carcinoma", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4371590_syn_9
# ==========================================
id_9 = "4371590_syn_9"
text_9 = """Procedure: Robotic bronchoscopic biopsy.
Target: LLL lesion.
Technique: Steered to lateral-basal segment. Validated via multimodality imaging. Sampled via aspiration, cryo-retrieval, and brushing. Lavaged segment. Deployed fiducial. 
Diagnosis: Squamous cell carcinoma."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "bronchoscopic biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "lateral-basal segment", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "cryo-retrieval", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "brushing", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Lavaged", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "Squamous cell carcinoma", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4371590 (Original)
# ==========================================
id_10 = "4371590"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: CDR Patricia Davis, MD
Fellow: Dr. Maria Santos (PGY-6)

Indication: Solitary pulmonary nodule
Target: 9mm nodule in LLL

PROCEDURE:

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings:

The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy are normal; there are no endobronchial lesions.

Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), LUL Lingula Carina (LC1), Bronchus Intermedius, RUL Carina (RC1) from mucus.

CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target. The navigational plan was reviewed and verified. This was then loaded into robotic bronchoscopy platform.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t13\t298\t8\t80\t5\t17

Robotic navigation bronchoscopy was performed with Ion platform. Full registration was used. Registration error: 2.1mm. Ion robotic catheter was used to engage the Lateral-Basal Segment of LLL (LB9). Target lesion is approximately 9mm in diameter. Under navigational guidance the Ion robotic catheter was advanced to 1.8cm away from the planned target.

Radial EBUS was performed to confirm lesion location. rEBUS view: Adjacent. Continuous margin noted.

Needle was advanced into the lesion. Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation. Cios Spin system was used for evaluation of nodule location. Low dose spin was performed to acquire CT imaging. This was passed on to Ion platform system for reconstruction and nodule location. The 3D images were interpreted on an independent workstation (Ion). I personally interpreted the cone beam CT and 3-D reconstruction.

Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location. Vision probe removed for biopsy; catheter position maintained via shape-sensing lock. Repeat imaging confirmed tool-in-lesion.

Transbronchial needle aspiration was performed with 21G Needle through the extended working channel catheter. Total 6 samples were collected. Samples sent for Cytology and Cell block.

Transbronchial cryobiopsy was performed with 1.7mm cryoprobe via the extended working channel catheter. Freeze time of 7 seconds was used. Total 5 samples were collected. Samples sent for Pathology.

Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.

Transbronchial brushing was performed with protected cytology brush through the extended working channel catheter. Total 2 samples were collected. Samples sent for Cytology.

Bronchoalveolar lavage was performed at Lateral-Basal Segment of LLL (LB9). Instilled 60cc of NS, suction returned with 23cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

ROSE Result: Malignant cells id[REDACTED], consistent with squamous cell carcinoma

Vision probe was re-inserted to inspect the airway. No significant bleeding observed. The catheter was retracted. Final airway inspection showed no complications.

The patient tolerated the procedure well without immediate complications.

DISPOSITION: Recovery, then discharge if stable. CXR to rule out pneumothorax.
Follow-up: Results conference in 5-7 days.

Davis, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "aspiration", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LUL Lingula Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LC1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Bronchus Intermedius", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RUL Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RC1", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Robotic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lateral-Basal Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "9mm", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Needle", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "Cone Beam CT", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Cios Spin", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 4)},
    {"label": "PROC_METHOD", **get_span(text_10, "cone beam CT", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 5)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion", 5)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 4)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6 samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.7mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "5 samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Fiducial marker", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "0.8mm x 3mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cytology brush", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "2 samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lateral-Basal Segment", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "60cc", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "23cc", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no complications", 1)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)