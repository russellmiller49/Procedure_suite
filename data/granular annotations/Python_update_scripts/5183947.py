import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 5183947_syn_1
# ==========================================
text_1 = """Indication: LLL mass, adenopathy.
Findings: LLL orifice occluded by tumor.
Procedures: EBUS (4R, 4L, 7, 10L, 11L sampled). Endobronchial biopsy LLL. EMN to peripheral LLL (partial).
ROSE: Squamous cell CA in all stations and primary.
Dx: Stage IIIB/C SCC."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "occluded", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "sampled", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Endobronchial biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 3)},
    {"label": "PROC_METHOD", **get_span(text_1, "EMN", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "peripheral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Squamous cell CA", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 5183947_syn_2
# ==========================================
text_2 = """PROCEDURE: Comprehensive staging was performed for a large LLL mass. EBUS-TBNA of stations 4R, 4L, 7, 10L, and 11L confirmed multi-station N2/N3 involvement with squamous cell carcinoma. Airway inspection revealed endobronchial tumor extension obstructing the LLL, which was biopsied directly. Electromagnetic navigation was attempted to sample the peripheral component for molecular adequacy, yielding confirmatory diagnostic tissue."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "11L", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "squamous cell carcinoma", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "Airway", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "endobronchial tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 2)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsied", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Electromagnetic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sample", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "peripheral", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "tissue", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 5183947_syn_3
# ==========================================
text_3 = """Codes: 31653 (EBUS 3+ stations), 31625 (Endobronchial biopsy), 31627 (Nav), 31654 (REBUS), 31628 (Transbronchial biopsy).
Rationale: Extensive EBUS staging. Endobronchial biopsy of visible tumor (31625). Navigation and TBBx of peripheral component (31627, 31628)."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Endobronchial biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Transbronchial biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "Endobronchial biopsy", 2)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "peripheral", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 5183947_syn_4
# ==========================================
text_4 = """Staging Bronchoscopy
Patient: [REDACTED]
Steps:
1. EBUS: Sampled 5 stations. All pos for Squamous.
2. Standard Bronch: Saw tumor in LLL airway. Biopsied (Endobronchial).
3. EMN: Navigated past tumor to distal lung. Biopsied.
Diagnosis: Extensive Squamous Cell CA.
Plan: Chemo/Rad."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Sampled", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Squamous", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Bronch", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "airway", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "EMN", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Navigated", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "distal lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 2)},
    {"label": "OBS_ROSE", **get_span(text_4, "Squamous Cell CA", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 5183947_syn_5
# ==========================================
text_5 = """Carlos has a big LLL mass and nodes everywhere. EBUS showed cancer in 4R 4L 7 10L 11L. Its squamous cell. Looked in the airway and the tumor is blocking the LLL so i took biopsies there too. Then tried to navigate to the far part of the tumor with superdimension to get more tissue. Got good samples. He has stage 3B or maybe 4."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "nodes", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "11L", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "squamous cell", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "airway", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "blocking", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "LLL", 2)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "navigate", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 2)},
    {"label": "SPECIMEN", **get_span(text_5, "tissue", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "samples", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 5183947_syn_6
# ==========================================
text_6 = """Procedures: EBUS-TBNA, Electromagnetic navigation bronchoscopy, Radial EBUS, Transbronchial biopsies, Endobronchial biopsies. Patient is a 59-year-old male with LLL mass. EBUS sampled stations 4R, 4L, 7, 10L, 11L; all positive for squamous cell carcinoma. Airway inspection showed LLL endobronchial tumor, biopsied. EMN used to sample peripheral component. Extensive N2/N3 disease confirmed."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Transbronchial biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Endobronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "11L", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "squamous cell carcinoma", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Airway", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 2)},
    {"label": "OBS_LESION", **get_span(text_6, "endobronchial tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsied", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "EMN", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "sample", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "peripheral", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 5183947_syn_7
# ==========================================
text_7 = """[Indication]
LLL mass, extensive adenopathy.
[Anesthesia]
General.
[Description]
EBUS-TBNA (5 stations). Endobronchial biopsy of LLL tumor. EMN-guided TBBx of peripheral mass. Squamous cell carcinoma confirmed in all sites.
[Plan]
Medical Oncology consult."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Endobronchial biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EMN", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "peripheral", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 2)},
    {"label": "OBS_ROSE", **get_span(text_7, "Squamous cell carcinoma", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 5183947_syn_8
# ==========================================
text_8 = """[REDACTED] a major staging procedure. We found that his lung cancer (squamous cell) has spread to lymph nodes on both sides of his chest. We also found the tumor growing into his airway, which we biopsied. We also navigated deeper into the lung to get more tissue for testing. He has advanced stage disease and will need chemotherapy and radiation."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "staging procedure", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lung cancer", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "squamous cell", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "lymph nodes", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsied", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "tissue", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 5183947_syn_9
# ==========================================
text_9 = """Procedure: Staging EBUS and therapeutic/diagnostic bronchoscopy.
Findings: Contralateral and ipsilateral nodal metastases (Squamous Cell). Endobronchial tumor obstruction.
Intervention: Nodal aspiration, direct endobronchial biopsy, and navigated peripheral sampling.
Outcome: Diagnosis of advanced stage carcinoma established."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodal metastases", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "Squamous Cell", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Endobronchial tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Nodal aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "endobronchial biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "navigated", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
]

BATCH_DATA.append({"id": "5183947_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 5183947
# ==========================================
text_10 = """Patient: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]

Preoperative Diagnosis: Respiratory failure secondary to extrinsic tracheal compression
Postoperative Diagnosis: Extrinsic tracheal compression s/p airway stent placement
Procedure Performed: Rigid bronchoscopy, Silicone Y-stent placement, bronchoscopic intubation

Surgeon: Laura Bennett, MD
Indications: Severe extrinsic tracheal compression
Consent: Consent was obtained from the patient's family prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
Sedation: General Anesthesia

Description of Procedure:
The procedure was performed in the main operating room. Once the patient was sedated, a flexible Q190 Olympus bronchoscope was inserted through the ETT into the trachea and airway inspection was performed. Beginning in the mid trachea, inflammation was seen within the airway walls extending into the bilateral mainstem with approximately 90% obstruction (at maximum) of the tracheal lumen most prominent in the mid trachea with less extensive obstruction extending to approximately 2 cm above the carina. There was no endobronchial tumor.

We subsequently removed the flexible bronchoscope and after administration of paralytics, a 14 mm ventilating rigid bronchoscope was inserted through the mouth into the supraglottic space. The previously placed endotracheal tube was visualized passing through the vocal cords. Under direct visualization, the endotracheal tube was removed and the rigid bronchoscope was inserted through the vocal cords into the mid trachea and connected to ventilator. The Q190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and into the airways.

After measuring the airways, we customized a 16x13x13 silicone Y-stent to a length of 75 mm in the tracheal limb, 15 mm in the right mainstem limb, and 30 mm in the left mainstem limb. The rigid bronchoscope was then advanced into the left mainstem and the stent was deployed. Through the use of rigid forceps and manipulation with the tip of the flexible bronchoscope, we were able to adequately position the limbs within the proper airways, resulting in successful stabilization of the airway.

At this point, inspection was performed to evaluate for any bleeding or other complications and none was seen. The rigid bronchoscope was then removed and an LMA was inserted. A repeat inspection was performed with the flexible bronchoscope and showed the stent well placed with near complete resolution of central airway obstruction. The bronchoscope was then removed and once the patient was awake and protecting airway, the LMA was removed and the procedure was complete.

Post-procedure Diagnosis: Severe extrinsic tracheal compression s/p successful deployment of silicone tracheal Y-stent

Recommendations:
• Transfer to ICU
• Obtain post-procedure CXR
• TID hypertonic nebulizers to avoid mucous impaction and obstruction of stent

Laura Bennett, MD

________________________________________"""

entities_10 = [
    {"label": "OBS_FINDING", **get_span(text_10, "Respiratory failure", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "extrinsic tracheal compression", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Extrinsic tracheal compression", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "airway stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placement", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "Silicone Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placement", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchoscopic intubation", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "extrinsic tracheal compression", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible Q190 Olympus bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "mid trachea", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "inflammation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "bilateral mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "90% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "tracheal", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "mid trachea", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2 cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible bronchoscope", 1)},
    {"label": "MEDICATION", **get_span(text_10, "paralytics", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "ventilating rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "supraglottic space", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "vocal cords", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "vocal cords", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "mid trachea", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Q190 Olympus flexible bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(text_10, "16x13x13", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "silicone Y-stent", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "75 mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "tracheal", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "15 mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right mainstem", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "30 mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem", 2)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible bronchoscope", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 4)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "LMA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible bronchoscope", 3)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "near complete resolution of central airway obstruction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "LMA", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "extrinsic tracheal compression", 3)},
    {"label": "DEV_STENT", **get_span(text_10, "silicone tracheal Y-stent", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "mucous impaction", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "obstruction", 3)},
]

BATCH_DATA.append({"id": "5183947", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)