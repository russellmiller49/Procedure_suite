import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 882041_syn_1
# ------------------------------------------
id_1 = "882041_syn_1"
text_1 = """Indication: Mediastinal LAD.
Proc: EBUS-TBNA.
Stations: 7, 11R.
ROSE: Granulomas.
Result: 2 stations sampled.
Plan: D/C."""
entities_1 = [
    {"label": "OBS_LESION",      **get_span(text_1, "LAD", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Granulomas", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "sampled", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 882041_syn_2
# ------------------------------------------
id_2 = "882041_syn_2"
text_2 = """PROCEDURE: Endobronchial Ultrasound-Guided Transbronchial Needle Aspiration.
FINDINGS: The mediastinum was systematically staged. Enlarged lymph nodes were id[REDACTED] at stations 7 (subcarinal) and 11R (right interlobar). TBNA was performed at both stations under real-time ultrasound guidance. Cytopathology suggests a granulomatous process consistent with sarcoidosis."""
entities_2 = [
    {"label": "PROC_METHOD",     **get_span(text_2, "Endobronchial Ultrasound-Guided", 1)},
    {"label": "PROC_ACTION",     **get_span(text_2, "Transbronchial Needle Aspiration", 1)},
    {"label": "OBS_LESION",      **get_span(text_2, "Enlarged lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "right interlobar", 1)},
    {"label": "PROC_ACTION",     **get_span(text_2, "TBNA", 1)},
    {"label": "PROC_METHOD",     **get_span(text_2, "ultrasound", 1)},
    {"label": "OBS_ROSE",        **get_span(text_2, "granulomatous process", 1)},
    {"label": "OBS_LESION",      **get_span(text_2, "sarcoidosis", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 882041_syn_3
# ------------------------------------------
id_3 = "882041_syn_3"
text_3 = """Code: 31652 (EBUS-TBNA, 1-2 stations).
Specifics: Sampled Station 7 and Station 11R (Total 2 stations). This qualifies for the base EBUS code 31652, not the multiple station code 31653."""
entities_3 = [
    {"label": "PROC_METHOD",     **get_span(text_3, "EBUS-TBNA", 1)},
    {"label": "PROC_ACTION",     **get_span(text_3, "Sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 11R", 1)},
    {"label": "PROC_METHOD",     **get_span(text_3, "EBUS", 2)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 882041_syn_4
# ------------------------------------------
id_4 = "882041_syn_4"
text_4 = """EBUS Note
Patient: [REDACTED]
1. ETT 8.0.
2. EBUS scope in.
3. Station 7: 4 passes -> Granulomas.
4. Station 11R: 3 passes -> Granulomas.
5. No other nodes sampled.
6. Pt stable."""
entities_4 = [
    {"label": "PROC_METHOD",     **get_span(text_4, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_4, "EBUS scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 7", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_4, "4 passes", 1)},
    {"label": "OBS_ROSE",        **get_span(text_4, "Granulomas", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 11R", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_4, "3 passes", 1)},
    {"label": "OBS_ROSE",        **get_span(text_4, "Granulomas", 2)},
    {"label": "PROC_ACTION",     **get_span(text_4, "sampled", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 882041_syn_5
# ------------------------------------------
id_5 = "882041_syn_5"
text_5 = """linda reyes for ebus checking for sarcoid. lymph nodes looked big at 7 and 11r. poked them with the needle got good samples rose said granulomas. didn't see anything else weird. patient woke up fine going home."""
entities_5 = [
    {"label": "PROC_METHOD",     **get_span(text_5, "ebus", 1)},
    {"label": "OBS_LESION",      **get_span(text_5, "sarcoid", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "lymph nodes", 1)},
    {"label": "OBS_FINDING",      **get_span(text_5, "big", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "11r", 1)},
    {"label": "PROC_ACTION",     **get_span(text_5, "poked", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_5, "needle", 1)},
    {"label": "OBS_ROSE",        **get_span(text_5, "granulomas", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 882041_syn_6
# ------------------------------------------
id_6 = "882041_syn_6"
text_6 = """Linear EBUS bronchoscopy performed for mediastinal staging. Lymph nodes at station 7 and 11R were id[REDACTED] and sampled via transbronchial needle aspiration. Rapid on-site evaluation showed granulomatous inflammation. No complications occurred."""
entities_6 = [
    {"label": "PROC_METHOD",     **get_span(text_6, "Linear EBUS bronchoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "11R", 1)},
    {"label": "PROC_ACTION",     **get_span(text_6, "sampled", 1)},
    {"label": "PROC_ACTION",     **get_span(text_6, "transbronchial needle aspiration", 1)},
    {"label": "OBS_ROSE",        **get_span(text_6, "granulomatous inflammation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 882041_syn_7
# ------------------------------------------
id_7 = "882041_syn_7"
text_7 = """[Indication]
Mediastinal adenopathy, ?Sarcoid.
[Anesthesia]
General.
[Description]
EBUS-TBNA Stations 7 & 11R. ROSE: Granulomas.
[Plan]
Discharge. Follow-up ILD clinic."""
entities_7 = [
    {"label": "OBS_LESION",      **get_span(text_7, "Mediastinal adenopathy", 1)},
    {"label": "OBS_LESION",      **get_span(text_7, "Sarcoid", 1)},
    {"label": "PROC_METHOD",     **get_span(text_7, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "11R", 1)},
    {"label": "OBS_ROSE",        **get_span(text_7, "Granulomas", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 882041_syn_8
# ------------------------------------------
id_8 = "882041_syn_8"
text_8 = """Dr. Cole performed an EBUS procedure on [REDACTED] her swollen lymph nodes. We used a special ultrasound scope to guide a needle into nodes in the center of her chest and the right side. The preliminary results show granulomas, which points towards sarcoidosis. We sampled two areas total."""
entities_8 = [
    {"label": "PROC_METHOD",     **get_span(text_8, "EBUS", 1)},
    {"label": "OBS_LESION",      **get_span(text_8, "swollen lymph nodes", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_8, "ultrasound scope", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_8, "needle", 1)},
    {"label": "OBS_ROSE",        **get_span(text_8, "granulomas", 1)},
    {"label": "OBS_LESION",      **get_span(text_8, "sarcoidosis", 1)},
    {"label": "PROC_ACTION",     **get_span(text_8, "sampled", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 882041_syn_9
# ------------------------------------------
id_9 = "882041_syn_9"
text_9 = """Procedure: Endosonographic nodal sampling.
Technique: Transbronchial needle aspiration under linear ultrasound guidance.
Targets: Subcarinal and right interlobar nodes.
Pathology: Granulomatous inflammation detected."""
entities_9 = [
    {"label": "PROC_METHOD",     **get_span(text_9, "Endosonographic", 1)},
    {"label": "PROC_ACTION",     **get_span(text_9, "nodal sampling", 1)},
    {"label": "PROC_ACTION",     **get_span(text_9, "Transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD",     **get_span(text_9, "linear ultrasound guidance", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "right interlobar nodes", 1)},
    {"label": "OBS_ROSE",        **get_span(text_9, "Granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 882041
# ------------------------------------------
id_10 = "882041"
text_10 = """PATIENT: [REDACTED] | 61F | MRN [REDACTED]
DATE OF PROCEDURE: [REDACTED]
PROCEDURE: Flexible bronchoscopy with endobronchial ultrasound–guided transbronchial needle aspiration (EBUS-TBNA) of mediastinal and hilar lymph nodes (CPT 31652)
INDICATION: Mediastinal adenopathy on PET-CT in patient with suspected sarcoidosis.

ATTENDING: Dr. Benjamin Cole
ANESTHESIA: General anesthesia with 8.0 ETT

PROCEDURE SUMMARY:
After induction of general anesthesia, a linear EBUS bronchoscope was introduced through the ETT. Systematic ultrasound survey of mediastinal and hilar lymph node stations was performed.

Stations sampled:
- Station 7 (subcarinal), short axis 1.8 cm – 4 passes with 22G needle
- Station 11R (right interlobar), short axis 1.2 cm – 3 passes with 22G needle

Rapid on-site cytology suggested non-caseating granulomas. No peripheral lesions were targeted. No radial EBUS, navigation or transbronchial lung biopsies were performed.

There was no endobronchial mass and no significant bleeding. All EBUS images were saved to PACS.

COMPLICATIONS: None. Estimated blood loss <10 mL.
DISPOSITION: Extubated in the OR, discharged from PACU to home with follow up in ILD clinic."""
entities_10 = [
    {"label": "PROC_ACTION",     **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD",     **get_span(text_10, "endobronchial ultrasound–guided", 1)},
    {"label": "PROC_ACTION",     **get_span(text_10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD",     **get_span(text_10, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal and hilar lymph nodes", 1)},
    {"label": "OBS_LESION",      **get_span(text_10, "Mediastinal adenopathy", 1)},
    {"label": "OBS_LESION",      **get_span(text_10, "sarcoidosis", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_10, "linear EBUS bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal and hilar lymph node stations", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_10, "1.8 cm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "4 passes", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_10, "22G needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "right interlobar", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_10, "1.2 cm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "3 passes", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_10, "22G needle", 2)},
    {"label": "OBS_ROSE",        **get_span(text_10, "non-caseating granulomas", 1)},
    {"label": "PROC_METHOD",     **get_span(text_10, "radial EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(text_10, "transbronchial lung biopsies", 1)},
    {"label": "OBS_LESION",      **get_span(text_10, "endobronchial mass", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)