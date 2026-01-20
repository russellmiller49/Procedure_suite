import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 4777235
# ==========================================
id_1 = "4777235"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Joshua Bennett, a 50-year-old female patient, presented to Regional Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Eric Johnson, MD, with Priya Sharma assisting.

The clinical indication for this procedure was peripheral lung nodule with suspicious mediastinal nodes. Preprocedural imaging had demonstrated a 19.4 millimeter solid pulmonary nodule located in the RUL lobe, specifically within the anterior (B3) segment. The lesion exhibited a positive bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 6.7. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 54 pack-years as a former smoker. The American Society of Anesthesiologists physical status classification was 2.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 09:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC180F bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 10R, a heterogeneous lymph node was id[REDACTED] measuring 21.2 millimeters in short axis and 29.3 millimeters in long axis. The node appeared oval in shape. Using the 19-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma. At station 2L, a homogeneous lymph node was id[REDACTED] measuring 8.8 millimeters in short axis and 22.9 millimeters in long axis. The node appeared round in shape. Using the 19-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported atypical cells. At station 11L, a heterogeneous lymph node was id[REDACTED] measuring 13.8 millimeters in short axis and 31.1 millimeters in long axis. The node appeared irregular in shape. Using the 19-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes, no malignancy.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Monarch robotic bronchoscopy system, manufactured by Auris Health (J&J), was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.5 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RUL anterior (B3). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a concentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using augmented fluoroscopy.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 6 specimens. Transbronchial needle aspiration was performed with 3 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported granuloma. Finally, bronchoalveolar lavage was performed from the RUL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 11:41, for a total procedure time of 131 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Eric Johnson, MD
Interventional Pulmonology"""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinal staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    
    # Paragraph 2
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "suspicious mediastinal nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3) segment", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hypermetabolic activity", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "staging", 2)},
    
    # Paragraph 4
    {"label": "MEDICATION", **get_span(text_1, "general anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "intubated", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 millimeter", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "09:30", 1)},
    
    # Paragraph 5
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinal lymph node evaluation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "airway inspection", 1)},
    
    # Paragraph 6 - Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "heterogeneous lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.2 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.3 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 2)}, # "classification was 2" is 1st
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},
    
    # Paragraph 6 - Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "homogeneous lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.9 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},
    
    # Paragraph 6 - Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "heterogeneous lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.1 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)}, # "B3" contains 3, "09:30" contains 3, "29.3" contains 3. Careful.
    # Checking "3" occurrences:
    # "B3" -> 1
    # "29.3" -> 2
    # "13.8" -> 3 (index 3 of digit '3'?) No, get_span finds exact string "3 ".
    # text_1.find("3") might hit "B3", "09:30".
    # Term is "3".
    # 1. "(B3)"
    # 2. "29.3"
    # 3. "09:30"
    # 4. "13.8"
    # 5. "31.1"
    # 6. "3 aspiration passes" <- Target
    # Let's target "3 aspiration" and offset length of "3"? No, helper function isn't that flexible.
    # Safe approach: `MEAS_COUNT` usually on the digit.
    # Let's verify manually. 
    # "3" in "(B3)"
    # "3" in "29.3"
    # "3" in "09:30"
    # "3" in "13.8"
    # "3" in "31.1"
    # "3" in "3 aspiration" -> 6th occurrence.
    # This is risky. Let's assume strict exact match of string "3".
    # Better to capture "3 aspiration passes" as count? No, guide says "Integer counts".
    # Using `get_span(text_1, "3", 6)` is brittle.
    # Alternative: The text says "3 aspiration passes".
    # I will assume "3" is the term.
    # Occ 1: B3 (index ~500)
    # Occ 2: 29.3 (index ~1100)
    # Occ 3: 09:30 (index ~950 - Wait, 09:30 is before station 10R).
    # Occ 4: 13.8 (index ~1400)
    # Occ 5: 31.1 (index ~1420)
    # Occ 6: "3 aspiration passes" (index ~1500).
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 6)}, 
    
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},
    
    # Paragraph 7
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinal staging", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lesion sampling", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CT-to-body", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.5 millimeters", 1)},
    
    # Paragraph 8
    {"label": "DEV_CATHETER", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "bronchial tree", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial endobronchial ultrasound probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "augmented fluoroscopy", 1)},
    
    # Paragraph 9
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 2)}, # "6.7" is 1st.
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 7)}, # Next "3" after the previous one.
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    
    # Paragraph 10
    {"label": "CTX_TIME", **get_span(text_1, "11:41", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "131 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "less than ten milliliters", 1)},
    
    # Paragraph 12 (Summary)
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinal staging", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lesion tissue diagnosis", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)