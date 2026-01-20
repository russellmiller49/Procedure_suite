import sys
from pathlib import Path

# Set the repository root (assuming script runs from within the repo structure)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the python path to import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 3849571_syn_1
# ==========================================
id_1 = "3849571_syn_1"
text_1 = """Procedure: Nav bronch, radial EBUS, TBNA, forceps biopsy, BAL.
Target: Left lingular lesion.
Findings: Concentric EBUS view. Nav success.
Sampling: TBNA (ROSE+), brush, forceps.
BAL: RUL posterior.
Comp: None. Minimal bleeding."""
entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lingular", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Concentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "ROSE", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "posterior", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 3849571_syn_2
# ==========================================
id_2 = "3849571_syn_2"
text_2 = """PROCEDURE NOTE: Bronchoscopy with multimodal sampling.
INDICATION: Migratory lung nodules.
NARRATIVE: The airway was inspected using a Q190 bronchoscope; anatomy was normal. BAL was performed in the RUL posterior segment. The SuperDimension system was utilized to navigate to a lesion in the left lingula. Position was confirmed with radial EBUS demonstrating a concentric view. We performed TBNA under fluoroscopic guidance (ROSE showed histiocytes/giant cells), followed by triple needle brush and forceps biopsies. Hemostasis was achieved."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodules", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "airway", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "normal", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "posterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "SuperDimension", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "LATERALITY", **get_span(text_2, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopic", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "histiocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "giant cells", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "Hemostasis was achieved", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 3849571_syn_3
# ==========================================
id_3 = "3849571_syn_3"
text_3 = """Billing:
- 31627: Navigation to lingular lesion.
- 31654: Radial EBUS confirmation of lesion.
- 31629: TBNA of lingular lesion.
- 31628: Forceps biopsy of lingular lesion.
- 31624: BAL of RUL (distinct lobe from biopsy)."""
entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "lingular", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "lingular", 2)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "lingular", 3)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 4)},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 3849571_syn_4
# ==========================================
id_4 = "3849571_syn_4"
text_4 = """Resident Note
Pt: [REDACTED]
Attending: Dr. Wright
1. Inspection: Normal.
2. BAL: RUL (180cc).
3. Nav: SuperD to Lingula.
4. REBUS: Concentric.
5. Sampling: TBNA, Brush, Forceps.
6. ROSE: Histiocytes/Giant cells.
7. Finished."""
entities_4 = [
    {"label": "OBS_FINDING", **get_span(text_4, "Normal", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "180cc", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "SuperD", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Forceps", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Histiocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Giant cells", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 3849571_syn_5
# ==========================================
id_5 = "3849571_syn_5"
text_5 = """rachel anderson procedure note. dr wright attending. we did a bronch with navigation and ebus. washed the rul first. then navigated to the lingula lesion. radial probe showed it nicely concentric. stuck it with the needle rose saw giant cells so maybe infection or sarcoid? did brush and forceps too. no bleeding really. patient woke up fine."""
entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ebus", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "washed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rul", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial probe", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rose", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "giant cells", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "infection", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "sarcoid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding really", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 3849571_syn_6
# ==========================================
id_6 = "3849571_syn_6"
text_6 = """Diagnostic bronchoscopy performed for migratory nodules. Airways inspected and found normal. RUL BAL performed. SuperDimension navigation used to access left lingular lesion. Radial EBUS confirmed concentric view. TBNA, brush, and forceps biopsies performed. ROSE suggested inflammatory process (histiocytes/giant cells). No complications."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Airways", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "normal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "SuperDimension", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "navigation", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "lingular", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "inflammatory process", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "histiocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "giant cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 3849571_syn_7
# ==========================================
id_7 = "3849571_syn_7"
text_7 = """[Indication]
Migratory lung nodules.
[Anesthesia]
General.
[Description]
1. BAL RUL.
2. Nav bronch to Lingula.
3. Radial EBUS confirmation.
4. TBNA, Brush, Forceps of Lingula target.
[Plan]
CXR. Pathology pending."""
entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Nav", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Forceps", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "Lingula", 2)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 3849571_syn_8
# ==========================================
id_8 = "3849571_syn_8"
text_8 = """We performed a complex bronchoscopy on [REDACTED] her lung nodules. First, we washed the right upper lobe to check for infection. Then, using electromagnetic navigation, we guided a catheter to the lesion in the left lingula. We double-checked the position with ultrasound, which confirmed we were right in the lesion. We took samples with a needle, a brush, and forceps. The preliminary look at the slides showed cells consistent with inflammation rather than cancer."""
entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "washed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right upper lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "electromagnetic navigation", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    {"label": "LATERALITY", **get_span(text_8, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "forceps", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "inflammation", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 3849571_syn_9
# ==========================================
id_9 = "3849571_syn_9"
text_9 = """Procedure: Guided bronchoscopy (31627), Ultrasound verification (31654), Needle aspiration (31629), Tissue sampling (31628), Bronchial washing (31624).
Target: Lingular nodule.
Findings: Lesion localized via navigation and sonography. Samples obtained via aspiration and forceps. Lavage performed in contralateral lobe."""
entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Ultrasound", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "washing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Lingular", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "sonography", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "contralateral lobe", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 3849571
# ==========================================
id_10 = "3849571"
text_10 = """Patient Name: [REDACTED]
MRN: [REDACTED]
Date of Procedure: [REDACTED]

Proceduralist(s): Thomas Wright, MD, Pulmonologist; Nicole Stevens, MD (Fellow)

Procedure(s) Performed:
• CPT 31629 Flexible bronchoscopy with fluoroscopic transbronchial needle aspiration
• CPT 31627 Bronchoscopy with computer assisted image guided navigation
• CPT 31654 Bronchoscopy with Endobronchial Ultrasound guidance for peripheral lesion
• CPT 31624 Bronchoscopy with bronchial alveolar lavage

Indications: Migratory lung nodules
Medications: General Anesthesia

Procedure, risks, benefits, and alternatives were explained to the patient. All questions were answered and informed consent was documented as per institutional protocol. A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed. A time-out was performed prior to the intervention.

Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the endotracheal tube. The trachea was of normal caliber. The tracheobronchial tree was examined to at least the first sub-segmental level. Bronchial mucosa and anatomy were normal; there were no endobronchial lesions. There were thick non-purulent secretions in multiple airways which were suctioned.

Following inspection, a bronchoalveolar lavage was performed in the posterior segment of the right upper lobe with 180 cc instillation and 70 cc return. The SuperDimension navigational catheter was then inserted through the therapeutic bronchoscope and advanced into the airway. Using the navigational software, we were able to direct the catheter to within 1 cm of the left lingular lesion of interest. Radial ultrasound was then used to confirm location and a concentric view was seen indicating appropriate isolation of the lesion. TBNAs were performed under fluoroscopic observation and on ROSE numerous histiocytes and occasional giant cells were seen. Subsequently, further biopsies were performed with a triple needle brush and forceps biopsies under fluoroscopic observation. After samples were obtained and we were confident that there was no active bleeding, the bronchoscope was removed and the procedure concluded.

Complications: No immediate complications
Estimated Blood Loss: Less than 5 cc

Recommendation:
• CXR to rule out pneumothorax
• Await pathology results

Thomas Wright, MD
Interventional Pulmonary

________________________________________"""
entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "computer assisted image guided navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Endobronchial Ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "peripheral lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoscopy", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchial alveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "tracheobronchial tree", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "normal caliber", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "tracheobronchial tree", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Bronchial mucosa", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "normal", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial lesions", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "thick non-purulent secretions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "airways", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "posterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right upper lobe", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "180 cc", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "70 cc", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "SuperDimension", 1)},
    {"label": "LATERALITY", **get_span(text_10, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lingular", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "concentric view", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNAs", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "histiocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "giant cells", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)