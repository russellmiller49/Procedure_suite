import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 456789_syn_1
# ==========================================
id_1 = "456789_syn_1"
text_1 = """Indication: Bulky adenopathy.
Proc: Thoracoscopy w/ biopsy.
- Single port 6th ICS.
- Flex-rigid scope.
- Biopsied 4R and 7 (5x each).
- 14Fr pigtail."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Bulky adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Single port", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "6th ICS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Flex-rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5x", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "14Fr pigtail", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 456789_syn_2
# ==========================================
id_2 = "456789_syn_2"
text_2 = """PROCEDURE: Thoracoscopic biopsy of mediastinal lymph nodes.
FINDINGS: Bulky adenopathy in the right paratracheal (4R) and subcarinal (7) stations.
DETAILS: Following access via the 6th intercostal space, the mediastinal pleura was incised. Insulated-tip forceps were used to obtain deep tissue biopsies from both stations to rule out lymphoma and sarcoidosis. A 14Fr pigtail catheter was placed for drainage."""
entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "mediastinal lymph nodes", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "Bulky adenopathy", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "mediastinal pleura", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Insulated-tip forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "14Fr pigtail catheter", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 456789_syn_3
# ==========================================
id_3 = "456789_syn_3"
text_3 = """CPT 32606: Thoracoscopy with biopsy of mediastinal space.
Nodes: 4R and 7.
Technique: Single port, flex-rigid scope.
Specimens: 10 cores.
Chest tube: 14Fr pigtail."""
entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Single port", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "flex-rigid scope", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "10", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "cores", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "14Fr pigtail", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 456789_syn_4
# ==========================================
id_4 = "456789_syn_4"
text_4 = """Procedure: Thoracoscopy Biopsy
1. Moderate sedation.
2. Port 6th ICS.
3. Biopsied 4R and 7.
4. Cautery for hemostasis.
5. Pigtail placed."""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "6th ICS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Cautery", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Pigtail", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 456789_syn_5
# ==========================================
id_5 = "456789_syn_5"
text_5 = """[REDACTED] needing biopsy for lymph nodes single port thoracoscopy right side found 4r and 7 nodes huge took good biopsies with the hot forceps pigtail in no pneumo."""
entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "lymph nodes", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "single port thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "hot forceps", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pigtail", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no pneumo", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 456789_syn_6
# ==========================================
id_6 = "456789_syn_6"
text_6 = """Thoracoscopy with mediastinal lymph node biopsy. Single-incision thoracoscopy at 6th ICS MAL. Flex-rigid scope inserted. Mediastinal pleura over station 4R and 7 opened. Multiple deep biopsies obtained using insulated-tip forceps. Station 4R 5 specimens. Station 7 5 specimens. Hemostasis with electrocautery. 14Fr pigtail catheter placed."""
entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Thoracoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "mediastinal lymph node", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Single-incision thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "6th ICS MAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Flex-rigid scope", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "Mediastinal pleura", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "insulated-tip forceps", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 2)},
    {"label": "MEAS_COUNT", **get_span(text_6, "5", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "specimens", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 2)},
    {"label": "MEAS_COUNT", **get_span(text_6, "5", 2)},
    {"label": "SPECIMEN", **get_span(text_6, "specimens", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "electrocautery", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "14Fr pigtail catheter", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 456789_syn_7
# ==========================================
id_7 = "456789_syn_7"
text_7 = """[Indication]
Bulky mediastinal adenopathy.
[Anesthesia]
Moderate Sedation.
[Description]
Single port thoracoscopy. Biopsies of 4R and 7. Pigtail catheter placed.
[Plan]
Obs overnight."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Bulky mediastinal adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Single port thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsies", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Pigtail catheter", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 456789_syn_8
# ==========================================
id_8 = "456789_syn_8"
text_8 = """[REDACTED] a thoracoscopy to biopsy enlarged lymph nodes in his chest. We used a flexible scope through a single incision. We id[REDACTED] large nodes near his windpipe and under the airway split. We took multiple samples from both areas to ensure a good diagnosis. A small pigtail tube was left in place."""
entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "enlarged lymph nodes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "flexible scope", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "single incision", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "large nodes", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "windpipe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway split", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "samples", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "pigtail tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 456789_syn_9
# ==========================================
id_9 = "456789_syn_9"
text_9 = """Diagnosis: Mediastinal lymph node enlargement.
Action: Thoracoscopic tissue sampling.
Details: Access established. Nodes at 4R and 7 harvested. 14Fr catheter inserted."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Mediastinal lymph node enlargement", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tissue sampling", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "14Fr catheter", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 456789
# ==========================================
id_10 = "456789"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Jennifer Walsh

Dx: Bulky mediastinal lymphadenopathy, prior non-diagnostic bronchoscopy
Procedure: Thoracoscopy with mediastinal lymph node biopsy

Hx: 55M with bilateral hilar and mediastinal adenopathy on CT. EBUS-TBNA showed granulomatous inflammation but insufficient tissue for definitive diagnosis. Sarcoidosis vs. lymphoma remains on differential.

Procedure:
Moderate sedation. Right lateral decubitus. Single-incision thoracoscopy at 6th ICS MAL. Flex-rigid scope inserted. Pleural space normal. Mediastinal pleura over station 4R and 7 opened. Multiple deep biopsies obtained using insulated-tip forceps:
- Station 4R: 5 specimens
- Station 7: 5 specimens

Excellent tissue cores obtained. Sent for path, flow, TB workup.

Hemostasis with electrocautery. 14Fr pigtail catheter placed. No pneumothorax on completion imaging.

Patient [REDACTED]. Will admit for observation overnight.

J. Walsh MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Bulky mediastinal lymphadenopathy", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_10, "prior", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Thoracoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal lymph node", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 1)},
    {"label": "LATERALITY", **get_span(text_10, "bilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "hilar", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mediastinal adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Single-incision thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th ICS MAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Flex-rigid scope", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Mediastinal pleura", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "insulated-tip forceps", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "5", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "specimens", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "5", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "specimens", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "cores", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "electrocautery", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "14Fr pigtail catheter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)