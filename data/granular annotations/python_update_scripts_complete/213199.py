import sys
from pathlib import Path

# Set up the repository root path (adjust depth as needed for your environment)
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 213199_syn_1
# ==========================================
text_1 = """Pre-op: Recurrent RUL SCC. Plan: HDR brachy.
Anesthesia: Mod sed.
Procedure: Scope passed. Tumor RUL 75% occlusion. 5F catheter placed 2cm distal to lesion. Fluoro confirm. Dummy check done. Rx length 4.5cm.
Plan: Transport to RadOnc for 10Gy. f/u 4-6wks."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "SCC", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "Tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "75% occlusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "catheter", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "2cm", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Fluoro", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "4.5cm", 1)}
]
BATCH_DATA.append({"id": "213199_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 213199_syn_2
# ==========================================
text_2 = """HISTORY: [REDACTED], a 72-year-old gentleman with recurrent endobronchial squamous cell carcinoma, presented for high-dose-rate (HDR) brachytherapy. The lesion in the right upper lobe (RUL) bronchus demonstrated significant obstruction.
PROCEDURE: Under moderate sedation, flexible bronchoscopy id[REDACTED] an infiltrative tumor. A 5-French flexible catheter was navigated through the working channel, extending 2 cm distal to the tumor margin. Fluoroscopic verification ensured optimal positioning for the 4.5 cm treatment length. The patient was transferred to Radiation Oncology for the administration of 10.0 Gy."""

entities_2 = [
    {"label": "OBS_LESION",    **get_span(text_2, "squamous cell carcinoma", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_2, "bronchus", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "catheter", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_2, "2 cm", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "tumor", 2)},
    {"label": "PROC_METHOD",   **get_span(text_2, "Fluoroscopic", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_2, "4.5 cm", 1)}
]
BATCH_DATA.append({"id": "213199_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 213199_syn_3
# ==========================================
text_3 = """Procedure: Bronchoscopy with catheter placement (CPT 31643).
Indication: RUL Obstruction/Malignancy.
Device: 5F flexible brachytherapy catheter.
Technique: Transnasal approach. Catheter advanced past RUL tumor (2.5 cm length). Distal placement verified via Fluoroscopy (included). Catheter secured.
Plan: HDR delivery 10 Gy (Session 3).
Medical Necessity: Palliation of symptomatic airway obstruction."""

entities_3 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_3, "Malignancy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "catheter", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 2)},
    {"label": "OBS_LESION",    **get_span(text_3, "tumor", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_3, "2.5 cm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "Fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Catheter", 2)}
]
BATCH_DATA.append({"id": "213199_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 213199_syn_4
# ==========================================
text_4 = """Resident Note
Patient: J. Brown, 72M.
Procedure: Brachytherapy Catheter Placement.
Attending: Dr. O'Brien.
Steps:
1. Time out/Sedation.
2. Airway inspection: RUL tumor 75% blocked.
3. 5F catheter placed past lesion.
4. Fluoro confirmation of position.
5. Secured at nose.
Plan: RadOnc for tx."""

entities_4 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_4, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "75% blocked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "catheter", 1)},
    {"label": "OBS_LESION",    **get_span(text_4, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "Fluoro", 1)}
]
BATCH_DATA.append({"id": "213199_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 213199_syn_5
# ==========================================
text_5 = """patient [REDACTED] here for brachytherapy session 3 for his rul cancer we used moderate sedation scope went in fine saw the tumor blocking the rul bronchus put the 5f catheter in past it checked with fluoro looks good taped it to his nose sending him to radiation now no complications thanks"""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rul", 1)},
    {"label": "OBS_LESION",    **get_span(text_5, "cancer", 1)},
    {"label": "OBS_LESION",    **get_span(text_5, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rul", 2)},
    {"label": "ANAT_AIRWAY",   **get_span(text_5, "bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "catheter", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "fluoro", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no complications", 1)}
]
BATCH_DATA.append({"id": "213199_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 213199_syn_6
# ==========================================
text_6 = """The patient is a 72-year-old male with recurrent squamous cell carcinoma of the RUL presenting for brachytherapy catheter placement. Under moderate sedation, the airway was inspected revealing the known tumor. A 5F flexible catheter was introduced and advanced 2 cm beyond the distal margin of the lesion. Position was verified with fluoroscopy. The catheter was secured, and the patient was transported to Radiation Oncology for delivery of 10.0 Gy. No complications occurred."""

entities_6 = [
    {"label": "OBS_LESION",    **get_span(text_6, "squamous cell carcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "catheter", 1)},
    {"label": "OBS_LESION",    **get_span(text_6, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "catheter", 2)},
    {"label": "MEAS_SIZE",     **get_span(text_6, "2 cm", 1)},
    {"label": "OBS_LESION",    **get_span(text_6, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "catheter", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)}
]
BATCH_DATA.append({"id": "213199_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 213199_syn_7
# ==========================================
text_7 = """[Indication]
Recurrent endobronchial SCC, RUL obstruction.
[Anesthesia]
Moderate sedation.
[Description]
Bronchoscopy performed. 5F catheter inserted past RUL tumor. Position confirmed via fluoroscopy. Treatment length 4.5 cm. Catheter secured.
[Plan]
Deliver 10.0 Gy. F/u bronchoscopy 4-6 weeks."""

entities_7 = [
    {"label": "OBS_LESION",    **get_span(text_7, "SCC", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 2)},
    {"label": "OBS_LESION",    **get_span(text_7, "tumor", 1)},
    {"label": "PROC_METHOD",   **get_span(text_7, "fluoroscopy", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_7, "4.5 cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Catheter", 1)}
]
BATCH_DATA.append({"id": "213199_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 213199_syn_8
# ==========================================
text_8 = """We brought [REDACTED] bronchoscopy suite for his scheduled brachytherapy session. After inducing moderate sedation, we inserted the scope transnasally. We visualized the infiltrative tumor at the RUL bronchus causing significant obstruction. We then passed a 5F catheter through the scope, placing it carefully past the tumor. We used fluoroscopy to confirm the tip was 2 cm distal to the lesion. Once satisfied, we taped the catheter and sent him for radiation treatment."""

entities_8 = [
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RUL", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_8, "bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "catheter", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 2)},
    {"label": "PROC_METHOD",   **get_span(text_8, "fluoroscopy", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_8, "2 cm", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "catheter", 2)}
]
BATCH_DATA.append({"id": "213199_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 213199_syn_9
# ==========================================
text_9 = """Dx: Recurrent RUL carcinoma.
Proc: Bronchoscopy with insertion of radioelement catheter.
Details: Scope introduced. RUL mass id[REDACTED]. 5F tube deployed beyond the blockage. Location authenticated via imaging. Device anchored. Patient moved to oncology for irradiation (10 Gy). No issues."""

entities_9 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_9, "carcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 2)},
    {"label": "OBS_LESION",    **get_span(text_9, "mass", 1)}
]
BATCH_DATA.append({"id": "213199_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)