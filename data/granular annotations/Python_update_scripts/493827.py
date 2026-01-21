import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Case 1: 493827_syn_1
# ==========================================
text_1 = """Dx: Sarcoidosis susp.
Proc: EBBx x6, BAL RML.
Findings: Cobblestoning main carina/mainstems.
Action: Biopsies taken (Carina, RMS, LMS). BAL RML 100mL instilled, 55mL return.
Complications: None."""

entities_1 = [
    {"label": "PROC_ACTION", **get_span(text_1, "EBBx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Cobblestoning", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "mainstems", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)},
    {"label": "MEAS_VOL", **get_span(text_1, "100mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "55mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": "493827_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 493827_syn_2
# ==========================================
text_2 = """PROCEDURE: Fiberoptic bronchoscopy with endobronchial biopsy and bronchoalveolar lavage.
FINDINGS: The bronchial mucosa exhibited diffuse nodularity and a 'cobblestone' appearance characteristic of granulomatous disease, particularly at the carina and mainstem bronchi. Six biopsies were harvested from these sites. Subsequently, a bronchoalveolar lavage was conducted in the right middle lobe yielding clear fluid.
IMPRESSION: Findings consistent with sarcoidosis."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Fiberoptic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "endobronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoalveolar lavage", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "nodularity", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "cobblestone", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "mainstem bronchi", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Six", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoalveolar lavage", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right middle lobe", 1)},
]
BATCH_DATA.append({"id": "493827_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 493827_syn_3
# ==========================================
text_3 = """Code Selection:
- 31625: Endobronchial biopsies (multiple sites: Carina, RMS, LMS).
- 31624: Bronchoalveolar lavage (RML).
Justification: Biopsies taken from central airways for tissue diagnosis. Lavage performed in a separate lobe (RML) for cellular differential. Modifier XS/59 applicable due to separate sites."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Endobronchial biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RML", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "central airways", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RML", 2)},
]
BATCH_DATA.append({"id": "493827_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 493827_syn_4
# ==========================================
text_4 = """Resident Procedure Note
Patient: S. Martinez
Steps:
1. Scope passed. Mucosa looked like cobblestones.
2. Biopsies taken: 3 from carina, 2 RMS, 1 LMS.
3. BAL done in RML. 100cc in, 55cc out.
4. Patient tolerated well.
Plan: Clinic f/u 2 weeks."""

entities_4 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "cobblestones", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "3", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "carina", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "2", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "RMS", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RML", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "100cc", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "55cc", 1)},
]
BATCH_DATA.append({"id": "493827_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 493827_syn_5
# ==========================================
text_5 = """sofia martinez bronchoscopy for sarcoidosis suspicion saw cobblestoning everywhere typical sarcoid look took 6 biopsies total from carina and mainstems bleeding was minimal also did a bal in the rml clear fluid back patient fine sending home."""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "cobblestoning", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "mainstems", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "bleeding was minimal", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rml", 1)},
]
BATCH_DATA.append({"id": "493827_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 493827_syn_6
# ==========================================
text_6 = """Moderate sedation was achieved. The scope was advanced, revealing diffuse mucosal nodularity and cobblestoning at the main carina and bilateral mainstem bronchi. Six endobronchial biopsies were obtained from the carina, RMS, and LMS. A BAL was performed in the RML with 55mL return. The procedure was uncomplicated."""

entities_6 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "nodularity", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "cobblestoning", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "bilateral mainstem bronchi", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Six", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "endobronchial biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "carina", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RML", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "55mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "uncomplicated", 1)},
]
BATCH_DATA.append({"id": "493827_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 493827_syn_7
# ==========================================
text_7 = """[Indication]
Bilateral hilar adenopathy, rule out sarcoidosis.
[Anesthesia]
Moderate sedation.
[Description]
Cobblestone mucosa observed. 6 Endobronchial biopsies obtained. BAL performed in RML. Minimal bleeding.
[Plan]
Outpatient follow-up. PFTs pending pathology."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Bilateral hilar adenopathy", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Cobblestone", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Endobronchial biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RML", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": "493827_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 493827_syn_8
# ==========================================
text_8 = """[REDACTED] a bronchoscopy to investigate suspected sarcoidosis. We observed the classic cobblestone appearance of the mucosa in the central airways. To confirm the diagnosis, we took six biopsies from the carina and mainstem bronchi. We also performed a lavage in the right middle lobe. She tolerated the procedure well with minimal bleeding."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "cobblestone", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "central airways", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "six", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "mainstem bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right middle lobe", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "minimal bleeding", 1)},
]
BATCH_DATA.append({"id": "493827_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 493827_syn_9
# ==========================================
text_9 = """Evaluation for sarcoidosis. Executed bronchoscopy with tissue sampling and lavage. Noted mucosal irregularities. Harvested 6 specimens from central airways. Performed washing of RML. No obstructions noted."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tissue sampling", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "lavage", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "mucosal irregularities", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "6", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "specimens", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "central airways", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "washing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RML", 1)},
]
BATCH_DATA.append({"id": "493827_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 493827
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Michael Thornton

Dx: Bilateral hilar adenopathy, suspected sarcoidosis
Procedure: Bronchoscopy with endobronchial biopsy, BAL

Moderate sedation achieved. Olympus BF-P190 scope advanced. Diffuse mucosal nodularity and cobblestoning noted at main carina, bilateral mainstem bronchi. Classic sarcoid appearance. 6 endobronchial biopsies taken (3 carina, 2 RMS, 1 LMS). Minimal bleeding. BAL performed at RML (100mL instilled, 55mL returned, clear). No endobronchial obstruction. Procedure uneventful.

Plan: Await pathology for non-caseating granulomas. PFTs if confirmed. F/U pulm clinic 2 weeks.

M. Thornton, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Bilateral hilar adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "endobronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Olympus BF-P190", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "nodularity", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "cobblestoning", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "bilateral mainstem bronchi", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "endobronchial biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "2", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LMS", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Minimal bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "BAL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "100mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "55mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Procedure uneventful", 1)},
]
BATCH_DATA.append({"id": "493827", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)