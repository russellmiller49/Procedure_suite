import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[3]
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
# Note 1: 10001_syn_1
# ==========================================
t1 = """Indication: ILD (UIP/NSIP).
Technique: LMA, Flex Bronch, Radial EBUS.
- RLL Basilar segments cleared via REBUS.
- 1.9mm Cryoprobe.
- Site 1: RLL Posterior Basal (5s freeze).
- Site 2: RLL Lateral Basal (5s freeze).
- Fogarty balloon used prophylactically.
- 2 samples (10mm each).
- No pneumothorax."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "ILD", 1)},
    {"label": "OBS_LESION", **get_span(t1, "UIP", 1)},
    {"label": "OBS_LESION", **get_span(t1, "NSIP", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Flex Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL Basilar segments", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "REBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Cryoprobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL Posterior Basal", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "5s", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "freeze", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL Lateral Basal", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "5s", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "freeze", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Fogarty balloon", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2", 2)},
    {"label": "SPECIMEN", **get_span(t1, "samples", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "10mm", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No pneumothorax", 1)},
]
BATCH_DATA.append({"id": "10001_syn_1", "text": t1, "entities": e1})


# ==========================================
# Note 2: 10001_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: The patient presented for diagnostic evaluation of progressive fibrotic interstitial lung disease. Under general anesthesia with a laryngeal mask airway, transbronchial cryobiopsy was performed. Radial EBUS confirmed the absence of significant vasculature in the target zones. A 1.9mm cryoprobe was utilized to obtain biopsies from the RLL posterior basal and lateral basal segments using a 5-second activation time. A Fogarty balloon was deployed immediately post-extraction for prophylactic hemostasis. Two substantial parenchymal specimens were retrieved."""

e2 = [
    {"label": "OBS_LESION", **get_span(t2, "interstitial lung disease", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "laryngeal mask airway", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial cryobiopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "cryoprobe", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RLL posterior basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "lateral basal segments", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "5-second", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Fogarty balloon", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "Two", 1)},
    {"label": "SPECIMEN", **get_span(t2, "specimens", 1)},
]
BATCH_DATA.append({"id": "10001_syn_2", "text": t2, "entities": e2})


# ==========================================
# Note 3: 10001_syn_3
# ==========================================
t3 = """Codes: 31628 (Transbronchial lung biopsy, single lobe), 31654 (Radial EBUS guidance).
Justification:
- Biopsies taken from lung parenchyma (RLL) using cryoprobe supports 31628.
- Radial EBUS utilized to survey biopsy site for safety supports 31654.
- Note: Multiple biopsies in same lobe bundle into single 31628."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Transbronchial lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "lung parenchyma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "cryoprobe", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsy", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsies", 1)},
]
BATCH_DATA.append({"id": "10001_syn_3", "text": t3, "entities": e3})


# ==========================================
# Note 4: 10001_syn_4
# ==========================================
t4 = """Procedure: Cryobiopsy
Pt: [REDACTED]
1. LMA/GA.
2. Radial EBUS check RLL bases.
3. Cryoprobe to RLL Post Basal -> Freeze 5s -> Pull.
4. Balloon up for bleeding control.
5. Repeat in RLL Lat Basal.
6. 2 good chunks.
7. Fluoro/US check neg for pneumo."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL bases", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Cryoprobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL Post Basal", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Freeze", 1)},
    {"label": "MEAS_TIME", **get_span(t4, "5s", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL Lat Basal", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "2", 2)},
    {"label": "SPECIMEN", **get_span(t4, "chunks", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Fluoro", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "US", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "neg for pneumo", 1)},
]
BATCH_DATA.append({"id": "10001_syn_4", "text": t4, "entities": e4})


# ==========================================
# Note 5: 10001_syn_5
# ==========================================
t5 = """Did a cryobiopsy on mr [REDACTED] for his ILD today. Used the LMA and general. Checked with the radial ebus first to make sure no vessels were there. Froze for 5 seconds in the RLL posterior and lateral basal segments. Pulled the whole scope out with the sample. Used the fogarty balloon to stop any bleeding. Got two big pieces of lung. No pneumothorax on the ultrasound after."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "cryobiopsy", 1)},
    {"label": "OBS_LESION", **get_span(t5, "ILD", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "radial ebus", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "5 seconds", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RLL posterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lateral basal segments", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "fogarty balloon", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "two", 1)},
    {"label": "SPECIMEN", **get_span(t5, "pieces of lung", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "No pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ultrasound", 1)},
]
BATCH_DATA.append({"id": "10001_syn_5", "text": t5, "entities": e5})


# ==========================================
# Note 6: 10001_syn_6
# ==========================================
t6 = """Transbronchial cryobiopsy for interstitial lung disease. General anesthesia with LMA. Radial EBUS guidance used. Biopsies obtained from RLL posterior basal and lateral basal segments. 1.9mm probe, 5-second freeze time. Fogarty balloon used for hemostasis. Two specimens obtained. Post-procedure imaging negative for pneumothorax."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Transbronchial cryobiopsy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "interstitial lung disease", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL posterior basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "lateral basal segments", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "probe", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "5-second", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "freeze", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Fogarty balloon", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Two", 1)},
    {"label": "SPECIMEN", **get_span(t6, "specimens", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "negative for pneumothorax", 1)},
]
BATCH_DATA.append({"id": "10001_syn_6", "text": t6, "entities": e6})


# ==========================================
# Note 7: 10001_syn_7
# ==========================================
t7 = """[Indication]
Fibrotic ILD, suspect UIP/NSIP.
[Anesthesia]
General, LMA.
[Description]
Radial EBUS used. 1.9mm Cryoprobe biopsies x2 in RLL (Posterior/Lateral Basal). Freeze time 5s. Fogarty balloon control. Specimens 10mm.
[Plan]
Pathology pending. D/C home."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Fibrotic ILD", 1)},
    {"label": "OBS_LESION", **get_span(t7, "UIP", 1)},
    {"label": "OBS_LESION", **get_span(t7, "NSIP", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Cryoprobe", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x2", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Posterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lateral Basal", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Freeze", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "5s", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Fogarty balloon", 1)},
    {"label": "SPECIMEN", **get_span(t7, "Specimens", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "10mm", 1)},
]
BATCH_DATA.append({"id": "10001_syn_7", "text": t7, "entities": e7})


# ==========================================
# Note 8: 10001_syn_8
# ==========================================
t8 = """We performed a cryobiopsy to evaluate [REDACTED]. After placing an LMA, we used radial EBUS to ensure the biopsy sites in the right lower lobe were safe. We then advanced the cryoprobe and obtained biopsies from the posterior and lateral basal segments, freezing for 5 seconds each time. We used a Fogarty balloon to manage potential bleeding. We retrieved two large lung samples and confirmed there was no pneumothorax before finishing."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lower lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "cryoprobe", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "posterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "lateral basal segments", 1)},
    {"label": "MEAS_TIME", **get_span(t8, "5 seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "Fogarty balloon", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "two", 1)},
    {"label": "SPECIMEN", **get_span(t8, "lung samples", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": "10001_syn_8", "text": t8, "entities": e8})


# ==========================================
# Note 9: 10001_syn_9
# ==========================================
t9 = """Procedure: Transbronchial cryo-sampling of parenchyma.
Context: Pulmonary fibrosis.
Method: Under LMA anesthesia, sonographic clearance was obtained. The cryo-instrument was applied to the RLL basilar segments. Freezing activation yielded two substantial tissue aggregates. Prophylactic balloon occlusion was employed.
Result: Hemostasis secured. Lung intact."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Transbronchial cryo-sampling", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "parenchyma", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Pulmonary fibrosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "sonographic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "cryo-instrument", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RLL basilar segments", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Freezing", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "two", 1)},
    {"label": "SPECIMEN", **get_span(t9, "tissue aggregates", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "balloon", 1)},
]
BATCH_DATA.append({"id": "10001_syn_9", "text": t9, "entities": e9})


# ==========================================
# Note 10: 10001
# ==========================================
t10 = """PROCEDURE: Transbronchial Cryobiopsy for ILD
DATE: [REDACTED]
PATIENT: [REDACTED] (MRN: [REDACTED])

Indication: Progressive fibrotic ILD, UIP vs NSIP pattern.

Technique: LMA placed. Flexible bronchoscopy. 
Radial EBUS used to confirm absence of large vessels in RLL basilar segments. 
Cryoprobe (1.9mm) advanced to RLL Posterior Basal segment. 
Freezing performed x 5 seconds. 
Probe and scope withdrawn en bloc. 
Fogarty balloon inflated for hemostasis (prophylactic).
Specimen: Large lung chunk (10mm) obtained. 
Repeated in RLL Lateral Basal segment x 1.

Total 2 biopsies. Fluoroscopy used.
No pneumothorax on post-op ultrasound."""

e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial Cryobiopsy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "ILD", 1)},
    {"label": "OBS_LESION", **get_span(t10, "fibrotic ILD", 1)},
    {"label": "OBS_LESION", **get_span(t10, "UIP", 1)},
    {"label": "OBS_LESION", **get_span(t10, "NSIP", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "LMA", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL basilar segments", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cryoprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL Posterior Basal segment", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Freezing", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "5 seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Fogarty balloon", 1)},
    {"label": "SPECIMEN", **get_span(t10, "lung chunk", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "10mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL Lateral Basal segment", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "x 1", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsies", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Fluoroscopy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 1)},
]
BATCH_DATA.append({"id": "10001", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
