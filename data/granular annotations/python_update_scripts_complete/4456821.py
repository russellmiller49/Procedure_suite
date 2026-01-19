import sys
from pathlib import Path

# Set the repository root (assuming script is run from a subfolder or root)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Could not import 'add_case'. Ensure you are running this from the correct repository structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
            
    if start == -1:
        # Fallback to prevent hard crashes during generation, though strict matching is preferred
        print(f"WARNING: Term '{term}' not found (occurrence {occurrence}).")
        return {"start": 0, "end": 0}
        
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4456821_syn_1
# ==========================================
id_1 = "4456821_syn_1"
text_1 = """Procedure: Therapeutic Thoracentesis.
Indication: Hepatic hydrothorax (Rt).
US: 6.5cm pocket.
Action: 8Fr catheter inserted. 800mL removed. Stopped early (re-expansion concern).
Comp: None.
Plan: Diuretics. TIPS eval."""

entities_1 = [
    {"label": "PROC_ACTION", **get_span(text_1, "Therapeutic Thoracentesis", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Hepatic hydrothorax", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Rt", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "6.5cm", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "8Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "800mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4456821_syn_2
# ==========================================
id_2 = "4456821_syn_2"
text_2 = """PROCEDURE NOTE: Ultrasound-Guided Thoracentesis.
INDICATION: Recurrent right hepatic hydrothorax in patient with cirrhosis (MELD 18).
DESCRIPTION: The right hemithorax was scanned, id[REDACTED] a safe pocket. Under local anesthesia, an 8-French catheter was introduced. 800 mL of clear transudative fluid was removed. Drainage was terminated at 800 mL to prevent re-expansion pulmonary edema and hypotension in this high-risk patient. Post-procedure ultrasound ruled out pneumothorax."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Thoracentesis", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "hepatic hydrothorax", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "right hemithorax", 1)},
    {"label": "MEDICATION", **get_span(text_2, "local anesthesia", 1)}, # Often mapped to medication category if specific drug not named but class is specific enough
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "8-French", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "800 mL", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "fluid", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "800 mL", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "ultrasound", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "ruled out pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4456821_syn_3
# ==========================================
id_3 = "4456821_syn_3"
text_3 = """CPT 32555: Thoracentesis with imaging guidance.
Guidance: Ultrasound used to mark site and guide needle.
Volume: 800 mL.
Complexity: Patient coagulopathic (Plt 68K, INR 1.7), careful technique required."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ultrasound", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "needle", 1)}, # Generic needle often mapped here
    {"label": "MEAS_VOL", **get_span(text_3, "800 mL", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4456821_syn_4
# ==========================================
id_4 = "4456821_syn_4"
text_4 = """Procedure: Thoracentesis
Pt: [REDACTED]
Attending: Dr. Nguyen

1. Pre-proc US: Rt effusion.
2. Local anesthetic.
3. Catheter placed.
4. Drained 800cc yellow fluid.
5. Stopped to be safe.
6. Pt breathing better."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 1)},
    {"label": "LATERALITY", **get_span(text_4, "Rt", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "800cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "yellow", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "fluid", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4456821_syn_5
# ==========================================
id_5 = "4456821_syn_5"
text_5 = """james rodriguez liver patient with fluid on the lung. dr nguyen supervising. did a tap on the right side. ultrasound looked good. put the catheter in drained about 800cc. didn't want to take too much cause his liver is bad. fluid looked clear. sent for culture. he felt better."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "tap", 1)}, # Colloquial for thoracentesis
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "800cc", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 2)},
    {"label": "OBS_FINDING", **get_span(text_5, "clear", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4456821_syn_6
# ==========================================
id_6 = "4456821_syn_6"
text_6 = """Therapeutic thoracentesis performed for right hepatic hydrothorax. Ultrasound guidance used. 800 mL clear transudative fluid removed. Procedure terminated to minimize risk of re-expansion edema/bleeding given coagulopathy. Patient tolerated well. No pneumothorax on post-procedure ultrasound."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Therapeutic thoracentesis", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "hepatic hydrothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "800 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "clear", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "ultrasound", 2)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4456821_syn_7
# ==========================================
id_7 = "4456821_syn_7"
text_7 = """[Indication]
Rt hepatic hydrothorax, dyspnea.
[Anesthesia]
Local.
[Description]
US guidance. 8Fr catheter. 800mL drained. Clear/yellow.
[Plan]
Continue diuretics. Sodium restriction."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "Rt", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "hepatic hydrothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "US", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "8Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "800mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Clear/yellow", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4456821_syn_8
# ==========================================
id_8 = "4456821_syn_8"
text_8 = """[REDACTED] drained from his right lung due to his liver condition. We performed a thoracentesis using ultrasound to guide us safely. We removed 800 mL of fluid, which looked like typical liver-related fluid. We decided not to take more to avoid complications like bleeding or shock, given his delicate condition. He reported feeling much better afterwards."""

entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "800 mL", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 2)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4456821_syn_9
# ==========================================
id_9 = "4456821_syn_9"
text_9 = """Procedure: Pleural aspiration (32555).
Context: Hepatic hydrothorax.
Action: Sonographically guided puncture. 800mL effusion evacuated.
Outcome: Respiratory relief. No adverse events."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Pleural aspiration", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Hepatic hydrothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Sonographically", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "800mL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "effusion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No adverse events", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4456821
# ==========================================
id_10 = "4456821"
text_10 = """Patient: [REDACTED] | MRN: [REDACTED] | Age: 58 | Sex: F Date: [REDACTED] | Time: 10:30 AM Provider: Lee, Jonathan MD (Attending) | Patel, Rahul MD (Fellow)
PROCEDURE: EBUS-TBNA (CPT 31652, 31653)
INDICATION: Mediastinal and hilar lymphadenopathy, r/o lymphoma vs sarcoidosis vs malignancy. Patient with constitutional symptoms including fevers, night sweats, 20lb weight loss over 3 months.
INFORMED CONSENT: Risks, benefits, alternatives discussed. Patient verbalized understanding. Written consent obtained.
PREPROCEDURE ASSESSMENT:
•\tASA Class: II
•\tNPO Status: Confirmed >8 hours
•\tIV Access: 20G left forearm
•\tAllergies: NKDA
•\tCurrent Medications: Lisinopril, metformin
•\tAnticoagulation: None
MONITORING: Standard ASA monitors plus capnography
SEDATION: 0915 - Midazolam 2mg IV 0917 - Fentanyl 75mcg IV
0920 - Propofol infusion initiated 50mcg/kg/min, titrated to effect (max 125mcg/kg/min) Total Propofol: 285mg
TOPICAL ANESTHESIA: Lidocaine 4% spray to oropharynx x3 applications Lidocaine 2% instilled via working channel: 15mL total
BRONCHOSCOPE: Fujifilm EB-530US (Ultrasound capable)
==PROCEDURE DESCRIPTION==
EBUS bronchoscope introduced via oral route. Vocal cords visualized, normal mobility. Trachea without masses or significant narrowing. Carina sharp.
ULTRASOUND SURVEY FINDINGS:
RIGHT PARATRACHEAL (2R): 9mm, normal hilum - NOT SAMPLED RIGHT LOWER PARATRACHEAL (4R): 31mm x 18mm, hypoechoic, loss of hilum LEFT LOWER PARATRACHEAL (4L): 27mm x 15mm, heterogeneous echotexture
SUBCARINAL (7): 45mm x 28mm, MARKEDLY ENLARGED, diffusely hypoechoic RIGHT HILAR (10R): 14mm, mildly prominent LEFT HILAR (10L): 22mm, round, abnormal architecture RIGHT INTERLOBAR (11R): 18mm
SAMPLING PERFORMED:
[STATION 7 - SUBCARINAL] Dimensions: 45 x 28mm | Position: Between LMB and RMB Pass 1 (0932): 22G needle, suction applied, 20 excursions, excellent tissue visible ROSE: Adequate specimen, large atypical lymphoid cells, recommend flow cytometry Pass 2 (0934): Additional material for flow cytometry Pass 3 (0936): Cell block preparation
Pass 4 (0938): Microbiology specimen sent for cultures Complications: None, minimal bleeding controlled with suction
[STATION 4R] Dimensions: 31 x 18mm Pass 1-3 (0942-0946): ROSE: Atypical lymphoid proliferation, similar to Station 7
[STATION 10L]
Dimensions: 22 x 14mm Pass 1-2 (0949-0951): ROSE: Lymphoid cells present, flow recommended
[STATION 11R] Dimensions: 18 x 11mm Pass 1-2 (0953-0955): ROSE: Benign reactive lymphoid tissue
Bronchoscope withdrawn at 0958. Total procedure time: 43 minutes.
SPECIMENS SUBMITTED:
•\tCytology: Stations 7, 4R, 10L, 11R
•\tFlow cytometry: Stations 7, 4R, 10L
•\tCell block: Station 7
•\tMicrobiology: Station 7 (AFB, fungal, bacterial cultures)
ESTIMATED BLOOD LOSS: <10mL
COMPLICATIONS: None
PATIENT [REDACTED]: Good, no desaturation episodes, hemodynamically stable throughout
POST-PROCEDURE:
•\tMonitoring in recovery area
•\tDiet: NPO x 2hrs then advance as tolerated
•\tActivity: Bedrest x 2hrs
•\tF/U: Results discussed when final path available
IMPRESSION: Successful EBUS-TBNA with sampling of multiple mediastinal lymph node stations. ROSE cytology demonstrates atypical lymphoid proliferation concerning for lymphoma. Flow cytometry and final pathology pending for definitive diagnosis.
RECOMMENDATIONS:
4.\tHematology/Oncology consultation
5.\tPET-CT for staging once diagnosis confirmed
6.\tFollow up in IP clinic in 1 week for pathology review
________________________________________
Jonathan Lee, MD Interventional Pulmonology Date/Time: [REDACTED] 11:15 Electronically Signed
________________________________________"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lymphadenopathy", 1)},
    
    # Sedation & Meds
    {"label": "MEDICATION", **get_span(text_10, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Lidocaine", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Lidocaine", 2)},

    # Scope/Method
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 2)},
    
    # Anatomy Survey
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Carina", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "9mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "31mm x 18mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "27mm x 15mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "45mm x 28mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "22mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "18mm", 1)},

    # Sampling 7
    {"label": "ANAT_LN_STATION", **get_span(text_10, "STATION 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "SUBCARINAL", 2)}, # 1st was in survey
    {"label": "MEAS_SIZE", **get_span(text_10, "45 x 28mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LMB", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMB", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0932", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "20 excursions", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "large atypical lymphoid cells", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0934", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0936", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0938", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Microbiology specimen", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 2)}, # 1st 'None' was anticoags

    # Sampling 4R
    {"label": "ANAT_LN_STATION", **get_span(text_10, "STATION 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "31 x 18mm", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0942", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Atypical lymphoid proliferation", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 2)}, # Reference

    # Sampling 10L
    {"label": "ANAT_LN_STATION", **get_span(text_10, "STATION 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "22 x 14mm", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0949", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Lymphoid cells", 1)},

    # Sampling 11R
    {"label": "ANAT_LN_STATION", **get_span(text_10, "STATION 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "18 x 11mm", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "0953", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Benign reactive lymphoid tissue", 1)},

    # Post
    {"label": "CTX_TIME", **get_span(text_10, "0958", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "43 minutes", 1)},
    
    # Specimens List
    {"label": "SPECIMEN", **get_span(text_10, "Cytology", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "10L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "11R", 2)},
    
    {"label": "SPECIMEN", **get_span(text_10, "Flow cytometry", 1)},
    # Skipping stations repetition here to avoid clutter, focus on key extractions

    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 3)},

    {"label": "SPECIMEN", **get_span(text_10, "Microbiology", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 4)},

    # Impression/Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 3)}, # Complications section
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "atypical lymphoid proliferation", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")