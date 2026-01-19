import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# Key: 2938475_syn_1
text_2938475_syn_1 = 'Procedure: Ion Nav Bronch + Fiducials.\nTarget: LLL mass (3.8cm).\nAction: Navigated to lesion. r-EBUS eccentric. Biopsied x5. Placed 3 fiducial markers.\nResult: Markers visible on fluoro.\nPlan: Refer for SBRT.'
entities_2938475_syn_1 = [
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_1, 'Ion Nav Bronch', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_1, 'LLL', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_1, 'mass', 1)},
    {'label': 'MEAS_SIZE', **get_span(text_2938475_syn_1, '3.8cm', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_1, 'Navigated', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_1, 'lesion', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_1, 'r-EBUS', 1)},
    {'label': 'OBS_FINDING', **get_span(text_2938475_syn_1, 'eccentric', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_1, 'Biopsied', 1)},
    {'label': 'MEAS_COUNT', **get_span(text_2938475_syn_1, 'x5', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_1, 'Placed', 1)},
    {'label': 'MEAS_COUNT', **get_span(text_2938475_syn_1, '3', 2)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_1, 'fiducial markers', 1)},
    {'label': 'OUTCOME_COMPLICATION', **get_span(text_2938475_syn_1, 'Markers visible on fluoro', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_1, 'SBRT', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_1', 'text': text_2938475_syn_1, 'entities': entities_2938475_syn_1})

# Key: 2938475_syn_2
text_2938475_syn_2 = 'OPERATIVE NOTE: The patient presented for fiducial placement to facilitate stereotactic body radiation therapy (SBRT). The Ion robotic system was utilized to navigate to the left lower lobe mass. Following histologic confirmation via transbronchial biopsy (CPT 31628), four gold fiducial markers were deployed within and around the tumor volume (CPT 31626). Fluoroscopy confirmed appropriate spacing and stability of the markers.'
entities_2938475_syn_2 = [
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_2, 'placement', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_2, 'stereotactic body radiation therapy', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_2, 'SBRT', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_2, 'Ion robotic system', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_2, 'navigate', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_2, 'left lower lobe', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_2, 'mass', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_2, 'transbronchial biopsy', 1)},
    {'label': 'MEAS_COUNT', **get_span(text_2938475_syn_2, 'four', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_2, 'gold fiducial markers', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_2, 'deployed', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_2, 'tumor', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_2, 'confirmed', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_2, 'markers', 2)},
]
BATCH_DATA.append({'id': '2938475_syn_2', 'text': text_2938475_syn_2, 'entities': entities_2938475_syn_2})

# Key: 2938475_syn_3
text_2938475_syn_3 = 'Coding:\n- 31627 (Navigation)\n- 31626 (Fiducial markers): Primary intent for SBRT guidance.\n- 31628 (Biopsy): Tissue confirmation.\n- 31654 (REBUS): Localization.\nTarget: LLL Mass.'
entities_2938475_syn_3 = [
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_3, 'markers', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_3, 'SBRT', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_3, 'Biopsy', 1)},
    {'label': 'SPECIMEN', **get_span(text_2938475_syn_3, 'Tissue', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_3, 'REBUS', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_3, 'LLL', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_3', 'text': text_2938475_syn_3, 'entities': entities_2938475_syn_3})

# Key: 2938475_syn_4
text_2938475_syn_4 = 'Procedure: Ion + Fiducials\nResident: Dr. Mitchell\nPatient: [REDACTED]\nSteps:\n1. Navigated to LLL mass with Robot.\n2. Confirmed with rEBUS.\n3. Took biopsies.\n4. Dropped fiducials for Rad Onc.\n5. Fluoro showed good placement.'
entities_2938475_syn_4 = [
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_4, 'Ion', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_4, 'Navigated', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_4, 'LLL', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_4, 'mass', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_4, 'rEBUS', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_4, 'fiducials', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_4, 'placement', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_4', 'text': text_2938475_syn_4, 'entities': entities_2938475_syn_4})

# Key: 2938475_syn_5
text_2938475_syn_5 = 'Mr [REDACTED] is here for markers. He has that LLL mass. We used the robot to get there. Biopsied it first to be sure then put in the gold markers for the radiation doctors. Put in four of them. Looks good on the screen. No pneumothorax.'
entities_2938475_syn_5 = [
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_5, 'markers', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_5, 'LLL', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_5, 'mass', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_5, 'Biopsied', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_5, 'gold markers', 1)},
    {'label': 'MEAS_COUNT', **get_span(text_2938475_syn_5, 'four', 1)},
    {'label': 'OUTCOME_COMPLICATION', **get_span(text_2938475_syn_5, 'No pneumothorax', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_5', 'text': text_2938475_syn_5, 'entities': entities_2938475_syn_5})

# Key: 2938475_syn_6
text_2938475_syn_6 = 'Robotic navigational bronchoscopy with fiducial placement. The Ion system was used to access a left lower lobe mass. Radial EBUS confirmed lesion location. Transbronchial biopsies were obtained. Subsequently, fiducial markers were deployed into the lesion under fluoroscopic guidance to assist with future radiation therapy. Post-procedure imaging ruled out pneumothorax.'
entities_2938475_syn_6 = [
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_6, 'bronchoscopy', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_6, 'placement', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_6, 'Ion', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_6, 'left lower lobe', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_6, 'mass', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_6, 'Radial EBUS', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_6, 'confirmed', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_6, 'lesion', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_6, 'Transbronchial biopsies', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_6, 'obtained', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_6, 'fiducial markers', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_6, 'deployed', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_6, 'lesion', 2)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_6, 'fluoroscopic', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_6, 'radiation therapy', 1)},
    {'label': 'OUTCOME_COMPLICATION', **get_span(text_2938475_syn_6, 'ruled out pneumothorax', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_6', 'text': text_2938475_syn_6, 'entities': entities_2938475_syn_6})

# Key: 2938475_syn_7
text_2938475_syn_7 = '[Indication]\nLLL mass, need tissue and markers for SBRT.\n[Anesthesia]\nGeneral.\n[Description]\nIon navigation to LLL. Biopsy performed. Fiducial markers (x4) placed. Position confirmed.\n[Plan]\nRadiation Oncology follow-up.'
entities_2938475_syn_7 = [
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_7, 'LLL', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_7, 'mass', 1)},
    {'label': 'SPECIMEN', **get_span(text_2938475_syn_7, 'tissue', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_7, 'markers', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_7, 'SBRT', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_7, 'Ion navigation', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_7, 'LLL', 2)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_7, 'Biopsy', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_7, 'markers', 2)},
    {'label': 'MEAS_COUNT', **get_span(text_2938475_syn_7, 'x4', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_7, 'placed', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_7, 'confirmed', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_7, 'Radiation Oncology', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_7', 'text': text_2938475_syn_7, 'entities': entities_2938475_syn_7})

# Key: 2938475_syn_8
text_2938475_syn_8 = 'We performed a procedure on [REDACTED] him for radiation therapy. Using the robotic bronchoscope, we navigated to the tumor in his left lower lung. We took a sample to confirm the diagnosis and then placed several small gold markers, or fiducials, directly into the tumor. These will act as targets for the radiation machine to treat the cancer precisely.'
entities_2938475_syn_8 = [
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_8, 'radiation therapy', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_8, 'robotic bronchoscope', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_8, 'navigate', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_8, 'tumor', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_8, 'left lower lung', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_8, 'took', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_8, 'sample', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_8, 'placed', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_8, 'gold markers', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_8, 'fiducials', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_8, 'tumor', 2)},
]
BATCH_DATA.append({'id': '2938475_syn_8', 'text': text_2938475_syn_8, 'entities': entities_2938475_syn_8})

# Key: 2938475_syn_9
text_2938475_syn_9 = 'Procedure: Robotic-assisted guidance with implantation of radiotherapy markers.\nAction: The LLL lesion was reached. Tissue was sampled. Metallic markers were deposited within the target volume.\nOutcome: Markers authenticated via fluoroscopy.'
entities_2938475_syn_9 = [
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_9, 'implantation', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_9, 'radiotherapy markers', 1)},
    {'label': 'ANAT_LUNG_LOC', **get_span(text_2938475_syn_9, 'LLL', 1)},
    {'label': 'OBS_LESION', **get_span(text_2938475_syn_9, 'lesion', 1)},
    {'label': 'SPECIMEN', **get_span(text_2938475_syn_9, 'Tissue', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_9, 'sampled', 1)},
    {'label': 'DEV_INSTRUMENT', **get_span(text_2938475_syn_9, 'Metallic markers', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_9, 'deposited', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475_syn_9, 'authenticate', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475_syn_9, 'fluoroscopy', 1)},
]
BATCH_DATA.append({'id': '2938475_syn_9', 'text': text_2938475_syn_9, 'entities': entities_2938475_syn_9})

# Key: 2938475
text_2938475 = 'Patient: [REDACTED] | DOB: [REDACTED] | MRN: [REDACTED]\nProcedure Date: [REDACTED]\nOperator: David Wong, MD | Assistant: Sarah Mitchell, MD (Fellow)\nRN: Jennifer Adams | RT: Michael Torres\n\nPREOP DX: Left lower lobe mass, 3.8 cm\nPOSTOP DX: Same\nPROCEDURE: Ion robotic bronchoscopy, radial EBUS, transbronchial biopsy, fiducial placement\n\nCPT: 31627, 31654, 31628, 31626'
entities_2938475 = [
    {'label': 'OBS_LESION', **get_span(text_2938475, 'mass', 1)},
    {'label': 'MEAS_SIZE', **get_span(text_2938475, '3.8 cm', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475, 'Ion robotic bronchoscopy', 1)},
    {'label': 'PROC_METHOD', **get_span(text_2938475, 'radial EBUS', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475, 'transbronchial biopsy', 1)},
    {'label': 'PROC_ACTION', **get_span(text_2938475, 'placement', 1)},
]
BATCH_DATA.append({'id': '2938475', 'text': text_2938475, 'entities': entities_2938475})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)