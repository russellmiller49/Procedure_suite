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

BATCH_DATA = []

# ==========================================
# Note 1: 0847291KK_syn_1
# ==========================================
id_1 = "0847291KK_syn_1"
text_1 = """Indication: Mediastinal LAD.
Proc: EBUS-TBNA.
Stations: 4R, 4L, 7, 11R.
ROSE: Granulomas (Sarcoid).
Specimens: 4.
Complications: None."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "LAD", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granulomas", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Sarcoid", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "Specimens: 4", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 0847291KK_syn_2
# ==========================================
id_2 = "0847291KK_syn_2"
text_2 = """PROCEDURE: Endobronchial Ultrasound-Guided Transbronchial Needle Aspiration (EBUS-TBNA).
INDICATION: Evaluation of mediastinal lymphadenopathy.
FINDINGS: Systematic evaluation of the mediastinum was performed. Lymph nodes at stations 4R, 4L, 7, and 11R were visualized and sampled. Rapid On-Site Evaluation (ROSE) demonstrated non-necrotizing granulomas consistent with sarcoidosis in multiple stations."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Endobronchial Ultrasound-Guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial Needle Aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lymphadenopathy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "non-necrotizing granulomas", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "consistent with sarcoidosis", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 0847291KK_syn_3
# ==========================================
id_3 = "0847291KK_syn_3"
text_3 = """Codes: 31653 (EBUS-TBNA 3 or more stations). Sampled 4R, 4L, 7, 11R (4 distinct stations). Conventional TBNA bundled."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "11R", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 2)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 0847291KK_syn_4
# ==========================================
id_4 = "0847291KK_syn_4"
text_4 = """EBUS Note
Patient: [REDACTED]
1. 4R: 4 passes, granulomas.
2. 4L: 4 passes, sarcoid-like.
3. 7: 4 passes, granulomas.
4. 11R: 3 passes, adequate.
Dx: Sarcoidosis likely."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "granulomas", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_4, "sarcoid-like", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4 passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_4, "granulomas", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "adequate", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 0847291KK_syn_5
# ==========================================
id_5 = "0847291KK_syn_5"
text_5 = """andrew thompson lymph nodes swollen rule out lymphoma sarcoid. did the ebus sampled 4r 4l 7 and 11r. rose guy said looks like granulomas probably sarcoid. took good samples sent for stains. no issues patient went home."""

entities_5 = [
    {"label": "ANAT_LN_STATION", **get_span(text_5, "lymph nodes", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "swollen", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ebus", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4l", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "11r", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "granulomas", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "probably sarcoid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no issues", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 0847291KK_syn_6
# ==========================================
id_6 = "0847291KK_syn_6"
text_6 = """EBUS-TBNA performed for mediastinal staging. Lymph nodes id[REDACTED] and sampled at stations 4R (15mm), 4L (17mm), 7 (22mm), and 11R (10mm). ROSE confirmed adequate cellularity with granulomatous features at all stations. Specimens sent for final pathology and microbiology. Procedure tolerated well."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "15mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "17mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "22mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "10mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "adequate cellularity", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "granulomatous features", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 0847291KK_syn_7
# ==========================================
id_7 = "0847291KK_syn_7"
text_7 = """[Indication]
Mediastinal LAD, r/o sarcoid.
[Anesthesia]
Moderate.
[Description]
EBUS-TBNA stations 4R, 4L, 7, 11R. ROSE: Non-necrotizing granulomas.
[Plan]
Discharge. Follow pathology."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "LAD", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "Non-necrotizing granulomas", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 0847291KK_syn_8
# ==========================================
id_8 = "0847291KK_syn_8"
text_8 = """[REDACTED] EBUS procedure to check the lymph nodes in his chest. We sampled nodes from four different areas: right and left upper chest, center chest, and right lung root. The preliminary results in the room suggest sarcoidosis, as we saw granulomas. We sent the samples for full testing to confirm."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "lymph nodes", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "suggest sarcoidosis", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "granulomas", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 0847291KK_syn_9
# ==========================================
id_9 = "0847291KK_syn_9"
text_9 = """Procedure: Endosonographic lymph node sampling.
Sites: Stations 4R, 4L, 7, 11R.
Method: Transbronchial needle aspiration under ultrasound guidance.
Pathology: Cytology suggests granulomatous inflammation."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Endosonographic", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "11R", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "ultrasound", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 0847291KK
# ==========================================
id_10 = "0847291KK"
text_10 = """***ELECTRONICALLY SIGNED BY: [OPERATOR DE-ID[REDACTED]]***
***COSIGN REQUIRED: NO***

ENCOUNTER: Bronchoscopy Suite Procedure
PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (AGE: 61Y 10M)
ENCOUNTER DATE: [REDACTED] 14:30:00

>>>PROCEDURE CODE: 31622, 31629 (EBUS-TBNA multiple stations)

>>>INDICATION:
Mediastinal lymphadenopathy, etiology unknown; rule out lymphoma vs sarcoidosis vs metastatic disease

>>>ANESTHESIA:
Moderate Sedation
Midazolam 2 MG IV at 14:32
Fentanyl 50 MCG IV at 14:32
Additional Midazolam 1 MG IV at 14:47
Max Ramsay Score: 3
SpO2 Range: 95%-98%
BP Range: 122-138/70-84 MMHG

>>>PROCEDURE NARRATIVE:
EBUS-TBNA performed. Systematic lymph node evaluation completed.

STATION 4R (Size: 15 MM):
- Needle passes: 4
- ROSE result: Granulomatous inflammation, non-necrotizing
- Special stains ordered: AFB, GMS

STATION 4L (Size: 17 MM):
- Needle passes: 4
- ROSE result: Consistent with sarcoidosis

STATION 7 (Size: 22 MM):
- Needle passes: 4
- ROSE result: Non-necrotizing granulomas

STATION 11R (Size: 10 MM):
- Needle passes: 3
- ROSE result: Adequate

Quality Metrics:
- Systematic evaluation: YES
- Photo documentation: YES
- All samples adequate: YES

>>>COMPLICATIONS:
None documented

>>>SPECIMENS COLLECTED:
SPECIMEN-2024-BR-00847: Station 4R (EBUS-TBNA)
SPECIMEN-2024-BR-00848: Station 4L (EBUS-TBNA)
SPECIMEN-2024-BR-00849: Station 7 (EBUS-TBNA)
SPECIMEN-2024-BR-00850: Station 11R (EBUS-TBNA)

>>>PATHOLOGY STATUS: Pending

>>>PATIENT STATUS AT DISCHARGE: Stable, discharged to home

***AUTO-SAVED: [REDACTED] 15:45:23***"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Mediastinal lymphadenopathy", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Midazolam", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "15 MM", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Needle passes: 4", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Granulomatous inflammation, non-necrotizing", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "17 MM", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Needle passes: 4", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "Consistent with sarcoidosis", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "22 MM", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Needle passes: 4", 3)},
    {"label": "OBS_ROSE", **get_span(text_10, "Non-necrotizing granulomas", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "10 MM", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Needle passes: 3", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Adequate", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None documented", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution Logic
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)