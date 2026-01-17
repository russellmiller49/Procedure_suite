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
# 2. Helper Functions
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
# 3. Data Definitions
# ==========================================

# ------------------------------------------
# Case 1: 323435523_syn_1
# ------------------------------------------
text_1 = """Study: COMBO-ABLATE.
Site: LUL nodule (3.2cm).
Proc: Cryoablation + Microwave.
Cryo: 2 cycles (-158C).
Microwave: 75W x 7min.
Result: 52mm ablation zone. No complications.
Plan: Protocol follow-up."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "3.2cm", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "Cryoablation", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Microwave", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Cryo", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_1, "2 cycles", 1)},
    {"label": "MEAS_TEMP",     **get_span(text_1, "-158C", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Microwave", 2)},
    {"label": "MEAS_ENERGY",   **get_span(text_1, "75W", 1)},
    {"label": "MEAS_TIME",     **get_span(text_1, "7min", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "52mm", 1)},
    {"label": "OBS_FINDING",   **get_span(text_1, "ablation zone", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_1", "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 323435523_syn_2
# ------------------------------------------
text_2 = """CLINICAL SUMMARY: [REDACTED] per the COMBO-ABLATE protocol for a 3.2 cm LUL adenocarcinoma. The procedure involved sequential application of cryoablation followed by microwave ablation to achieve synergistic tumor destruction. Real-time monitoring confirmed adequate thermal spread and an ablation margin encompassing the lesion."""

entities_2 = [
    {"label": "MEAS_SIZE",     **get_span(text_2, "3.2 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "cryoablation", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "microwave ablation", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "tumor", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "lesion", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_2", "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 323435523_syn_3
# ------------------------------------------
text_3 = """Codes: 31641 (Bronchoscopy with destruction of tumor, initial). 31654 (Radial EBUS guidance). Note: Combined modalities (Cryo + Microwave) on the same lesion constitute a single unit of 31641."""

entities_3 = [
    {"label": "PROC_ACTION",   **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3, "destruction of tumor", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "Cryo", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "Microwave", 1)},
    {"label": "OBS_LESION",    **get_span(text_3, "lesion", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_3", "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 323435523_syn_4
# ------------------------------------------
text_4 = """Research Case: Robert Berg
Target: LUL Apicoposterior
1. Navigated to lesion.
2. Confirmed w/ r-EBUS.
3. Cryo x2 cycles.
4. Wait 15 mins.
5. Microwave 75W 7 mins.
6. Post-op EBUS: big ablation zone.
7. Stable."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL Apicoposterior", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "Navigated", 1)},
    {"label": "OBS_LESION",    **get_span(text_4, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "r-EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "Cryo", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_4, "x2 cycles", 1)},
    {"label": "MEAS_TIME",     **get_span(text_4, "15 mins", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "Microwave", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_4, "75W", 1)},
    {"label": "MEAS_TIME",     **get_span(text_4, "7 mins", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "EBUS", 2)},
    {"label": "OBS_FINDING",   **get_span(text_4, "ablation zone", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_4", "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 323435523_syn_5
# ------------------------------------------
text_5 = """[REDACTED] in the combo study today left upper lobe tumor big one 3cm. we did the cryo freezing first two rounds got a good ice ball. waited the 15 minutes then hit it with the microwave probe 75 watts. cooked it good. total zone looks huge on the ultrasound. patient did fine no issues."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "left upper lobe", 1)},
    {"label": "OBS_LESION",    **get_span(text_5, "tumor", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_5, "3cm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "cryo", 1)},
    {"label": "PROC_ACTION",   **get_span(text_5, "freezing", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_5, "two rounds", 1)},
    {"label": "OBS_FINDING",   **get_span(text_5, "ice ball", 1)},
    {"label": "MEAS_TIME",     **get_span(text_5, "15 minutes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "microwave probe", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_5, "75 watts", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "ultrasound", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no issues", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_5", "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 323435523_syn_6
# ------------------------------------------
text_6 = """Bronchoscopic ablation of LUL neoplasm performed under clinical trial protocol. Guidance achieved via radial EBUS. Dual modality therapy administered: Cryoablation (ProSense) followed by Microwave Ablation (Neuwave). Total procedure time and parameters per protocol. Post-procedure imaging confirmed satisfactory ablation zone. Patient tolerated procedure well."""

entities_6 = [
    {"label": "PROC_ACTION",   **get_span(text_6, "Bronchoscopic ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_6, "neoplasm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "radial EBUS", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "Cryoablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "ProSense", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "Microwave Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Neuwave", 1)},
    {"label": "OBS_FINDING",   **get_span(text_6, "ablation zone", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_6", "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 323435523_syn_7
# ------------------------------------------
text_7 = """[Indication]
LUL Adenocarcinoma, Study Protocol.
[Anesthesia]
General.
[Description]
Navigated to LUL lesion. Confirmed REBUS. Cryoablation performed. 15 min interval. Microwave ablation performed. Margins adequate.
[Plan]
Protocol imaging and follow-up."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_7, "Adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 2)},
    {"label": "OBS_LESION",    **get_span(text_7, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_7, "REBUS", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "Cryoablation", 1)},
    {"label": "MEAS_TIME",     **get_span(text_7, "15 min", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "Microwave ablation", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_7", "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 323435523_syn_8
# ------------------------------------------
text_8 = """[REDACTED] a combination ablation procedure for his lung tumor today. We navigated to the tumor in the left upper lobe and confirmed its location with ultrasound. We first froze the tumor using a cryoprobe, then after a short break, we heated it using a microwave probe. This combination created a large treatment zone that completely covered the tumor."""

entities_8 = [
    {"label": "PROC_ACTION",   **get_span(text_8, "ablation", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 1)},
    {"label": "PROC_METHOD",   **get_span(text_8, "navigated", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe", 1)},
    {"label": "PROC_METHOD",   **get_span(text_8, "ultrasound", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "froze", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "cryoprobe", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "heated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "microwave probe", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 4)},
]
BATCH_DATA.append({"id": "323435523_syn_8", "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 323435523_syn_9
# ------------------------------------------
text_9 = """Procedure: Multimodality tumor destruction.
Target: Left Upper Lobe mass.
Technique: Sequential cryotherapy and microwave energy application.
Verification: Radial endobronchial ultrasound confirmed targeting and treatment effect. 
Outcome: Successful creation of ablation zone."""

entities_9 = [
    {"label": "OBS_LESION",    **get_span(text_9, "tumor", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "destruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Left Upper Lobe", 1)},
    {"label": "OBS_LESION",    **get_span(text_9, "mass", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "cryotherapy", 1)},
    {"label": "PROC_METHOD",   **get_span(text_9, "microwave", 1)},
    {"label": "PROC_METHOD",   **get_span(text_9, "Radial endobronchial ultrasound", 1)},
    {"label": "OBS_FINDING",   **get_span(text_9, "ablation zone", 1)},
]
BATCH_DATA.append({"id": "323435523_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)