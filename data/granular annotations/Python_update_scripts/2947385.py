import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2947385_syn_1
# ==========================================
t1 = """Indication: Lung mass, N2/N3 suspicion.
Procedure: EBUS-TBNA.
Stations: 7, 4R, 10R, 11R.
Findings: Malignancy in 7, 4R. 10R/11R reactive.
Dx: N2 positive NSCLC.
Code: 31653."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Lung mass", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11R", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "reactive", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2947385_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Endobronchial Ultrasound Staging.
INDICATION: Radiographic lymphadenopathy in setting of lung mass.
PROCEDURE: Systematic EBUS survey performed. Transbronchial needle aspiration performed at stations 7, 4R, 10R, and 11R. Cytopathology confirmed adenocarcinoma in mediastinal stations 7 and 4R, confirming N2 disease. Hilar stations were negative."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Endobronchial Ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lung mass", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "stations 7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4R", 2)},
]
BATCH_DATA.append({"id": "2947385_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2947385_syn_3
# ==========================================
t3 = """Code: 31653 (EBUS-TBNA 3 or more stations).
Stations Sampled: 4 total (7, 4R, 10R, 11R).
Findings: Positive for malignancy in mediastinum.
Medical Necessity: Staging for lung cancer treatment planning."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "Positive", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "mediastinum", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lung cancer", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2947385_syn_4
# ==========================================
t4 = """Procedure: EBUS
Patient: [REDACTED]
Steps:
1. Scope in.
2. Sampled 7 (Subcarinal) - Pos.
3. Sampled 4R (Paratracheal) - Pos.
4. Sampled 10R/11R - Neg.
Impression: Stage IIIB (N2 disease).
Plan: Chemo/Rad referral."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "Subcarinal", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Pos", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Sampled", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "Paratracheal", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Pos", 2)},
    {"label": "PROC_ACTION", **get_span(t4, "Sampled", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Neg", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2947385_syn_5
# ==========================================
t5 = """EBUS for Arthur Curry. We looked at all the nodes. Poked 7, 4R, 10R and 11R. The big ones in the middle 7 and 4R have cancer. The others looked okay. So he has N2 disease. Needs oncology."""

e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4R", 2)},
    {"label": "OBS_ROSE", **get_span(t5, "cancer", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2947385_syn_6
# ==========================================
t6 = """Endobronchial ultrasound with transbronchial needle aspiration. Four nodal stations sampled: 7, 4R, 10R, 11R. ROSE confirmed malignancy in stations 7 and 4R. Diagnosis is N2-positive non-small cell lung cancer. Patient tolerated procedure well."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "nodal stations", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 2)},
]
BATCH_DATA.append({"id": "2947385_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2947385_syn_7
# ==========================================
t7 = """[Indication]
Lung cancer staging.
[Anesthesia]
General.
[Description]
EBUS-TBNA x 4 stations (7, 4R, 10R, 11R). Malignancy confirmed in mediastinal nodes.
[Plan]
Multidisciplinary tumor board."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Lung cancer", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "stations", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "Malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "mediastinal nodes", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2947385_syn_8
# ==========================================
t8 = """[REDACTED] staging for his lung cancer. We used the ultrasound scope to sample lymph nodes in four different areas of his chest. Unfortunately, the cancer has spread to the lymph nodes in the mediastinum (N2 nodes), which means surgery isn't the first option. He will likely need chemotherapy and radiation."""

e8 = [
    {"label": "OBS_LESION", **get_span(t8, "lung cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "ultrasound scope", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "sample", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "lymph nodes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "mediastinum", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "N2 nodes", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2947385_syn_9
# ==========================================
t9 = """Procedure: EBUS-guided nodal staging.
Action: Multiple mediastinal and hilar lymph node stations were id[REDACTED] and aspirated (7, 4R, 10R, 11R). 
Result: Cytological confirmation of mediastinal nodal involvement."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "EBUS-guided", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "mediastinal and hilar lymph node stations", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "mediastinal nodal", 1)},
]
BATCH_DATA.append({"id": "2947385_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2947385
# ==========================================
t10 = """[REDACTED]: [REDACTED]arlos MR#: 2947385
Age: 59 | Gender: M Date: [REDACTED]
Physician: Dr. Foster, William (Attending)
Procedure: Endobronchial Ultrasound with Needle Aspiration
Why: Lung mass with lymph nodes - need tissue diagnosis
Sedation: Moderate (Versed + Fentanyl)
What we found:
•	Big lymph node under carina (station 7): 36mm
•	Right side lymph node (station 4R): 23mm
•	Left side lymph node (station 4L): 18mm
•	Other smaller nodes at stations 10R (12mm) and 11R (15mm)
What we did: Used ultrasound bronchoscope to look at lymph nodes. Used needle to get samples.
Station 7 - Did 4 needle passes Quick look by pathologist: CANCER CELLS FOUND (adenocarcinoma type)
Station 4R - Did 3 passes Quick look: Also shows cancer
Station 10R - Did 2 passes
Quick look: Normal lymph node
Station 11R - Did 2 passes Quick look: Normal
Bottom line: Cancer spread to lymph nodes in chest (N2 disease)
No problems during procedure. Patient did fine.
What's next:
•	Cancer doctor appointment
•	More scans needed
•	Treatment plan to be made
Dr. William Foster [REDACTED] 2:15 PM
________________________________________

═══════════════════════════════════════ CENTRAL MEDICAL CENTER PULMONARY PROCEDURE SERVICE ═══════════════════════════════════════
PATIENT [REDACTED]: Baker, Michelle Ann MRN: [REDACTED] DOB: [REDACTED] (Age 49) Gender: Female Date of Service: [REDACTED] Time: 13:30
CLINICAL TEAM Attending Physician: Chang, Margaret MD, FCCP Fellow: Stevens, Brian MD Procedural RN: Thompson, Lisa RN Respiratory Therapist: Garcia, Ramon RRT Cytopathologist: Wu, Steven MD (ROSE interpretation)
═══════════════════════════════════════
PROCEDURE PERFORMED Endobronchial Ultrasound with Transbronchial Needle Aspiration (EBUS-TBNA) CPT Codes: 31652, 31653
CLINICAL INDICATION 49-year-old female, never-smoker, with incidentally discovered mediastinal lymphadenopathy on CT chest performed for chronic cough. Largest node measures 3.8cm in subcarinal region. No known malignancy. PET-CT shows FDG-avid nodes at stations 7, 4R, and 11R. Differential includes sarcoidosis, lymphoma, or metastatic disease from occult primary.
PAST MEDICAL HISTORY
•	Hypertension
•	Hyperlipidemia
•	GERD
•	Asthma (mild intermittent)
MEDICATIONS Home: Lisinopril, atorvastatin, albuterol PRN Held: None (not on anticoagulation)
ALLERGIES: Penicillin (rash)
PRE-PROCEDURE ASSESSMENT
•	ASA Classification: II
•	NPO status: Verified >8 hours
•	IV access: 20-gauge left antecubital
•	Consent: Obtained after detailed discussion of risks (bleeding, infection, pneumothorax, need for additional procedures, failure to obtain diagnosis, adverse reaction to sedation)
MONITORING
•	Pulse oximetry (continuous)
•	Capnography
•	Blood pressure (q3min)
•	ECG (continuous)
SEDATION RECORD 1325 - Glycopyrrolate 0.2mg IV (antisialagogue) 1330 - Midazolam 2mg IV
1332 - Fentanyl 50mcg IV 1335 - Propofol infusion started at 50mcg/kg/min Titrated throughout procedure (max 100mcg/kg/min) Total propofol administered: 245mg 1426 - Sedation discontinued
TOPICAL ANESTHESIA
•	Lidocaine 4% spray to oropharynx (4 applications)
•	Lidocaine 2% via bronchoscope working channel: 18mL total
EQUIPMENT
•	Bronchoscope: Olympus BF-UC180F (Linear EBUS)
•	TBNA Needle: 22-gauge Olympus NA-201SX-4022
•	Ultrasound system: Olympus EU-ME2
═══════════════════════════════════════
PROCEDURE DETAILS
TIME IN: 1330 PROCEDURE START: 1335 PROCEDURE END: 1422 TIME OUT: 1426 TOTAL PROCEDURE TIME: 47 minutes
After adequate sedation achieved and time-out performed, the EBUS bronchoscope was advanced through the oropharynx under direct visualization.
AIRWAY INSPECTION:
•	Oropharynx: Normal
•	Vocal cords: Normal appearance and mobility bilaterally
•	Subglottis: Patent
•	Trachea: Normal caliber, no masses or significant narrowing
•	Carina: Sharp, mobile
•	Main bronchi: Patent bilaterally
SYSTEMATIC MEDIASTINAL ULTRASOUND SURVEY:
Station 1: Not well visualized (typical) Station 2R (Right upper paratracheal): 9mm, maintained normal architecture with central echogenic hilum - NOT SAMPLED Station 2L (Left upper paratracheal): Not visualized
Station 4R (Right lower paratracheal): 23mm x 14mm, oval, maintained hilum, normal vascular pattern Station 4L (Left lower paratracheal): 17mm x 11mm, oval, normal appearance Station 7 (Subcarinal): 38mm x 26mm, MARKEDLY ENLARGED, diffusely hypoechoic, loss of normal hilar architecture, ABNORMAL Station 10R (Right hilar): 19mm x 12mm, round morphology, loss of normal echogenic hilum, ABNORMAL Station 10L (Left hilar): 14mm x 9mm, normal appearance Station 11R (Right interlobar): 21mm x 13mm, hypoechoic, loss of hilum, ABNORMAL Station 11L (Left interlobar): 11mm x 7mm, normal
TRANSBRONCHIAL NEEDLE ASPIRATION:
┌─────────────────────────────────────┐ │ STATION 7 - SUBCARINAL │ └─────────────────────────────────────┘ Dimensions: 38mm x 26mm x 22mm Location: Between RMB and LMB, posterior Elastography: Blue pattern (firm consistency, elastography score 4/5)
Pass 1 (1345):
•	22G needle advanced under real-time ultrasound guidance
•	Penetrated bronchial wall without difficulty
•	22 excursions performed with negative pressure
•	Visible tissue core in needle hub
•	ROSE: ADEQUATE specimen, abundant cellular material
Pass 2 (1348):
•	Additional sampling for confirmation
•	ROSE: NON-NECROTIZING GRANULOMAS id[REDACTED], suggestive of SARCOIDOSIS
Pass 3 (1351):
•	Additional tissue for cell block and flow cytometry
Pass 4 (1354):
•	Specimen for microbiology (AFB smear, culture; fungal culture; bacterial culture)
Complications: None. Minimal bleeding, self-limited.
┌─────────────────────────────────────┐ │ STATION 4R │ └─────────────────────────────────────┘ Dimensions: 23mm x 14mm Location: Right lower paratracheal
Pass 1-3 (1358-1404):
•	Technically successful needle passes
•	ROSE: Granulomatous inflammation consistent with Station 7 findings
┌─────────────────────────────────────┐ │ STATION 10R │ └─────────────────────────────────────┘ Dimensions: 19mm x 12mm
Location: Right hilar region
Pass 1-2 (1407-1410):
•	ROSE: Granulomas present
┌─────────────────────────────────────┐ │ STATION 11R │ └─────────────────────────────────────┘ Dimensions: 21mm x 13mm Location: Right interlobar
Pass 1-2 (1413-1416):
•	ROSE: Reactive lymphoid hyperplasia with scattered granulomas
BRONCHOSCOPE WITHDRAWAL Final inspection of airways showed no evidence of bleeding. Scope withdrawn at 1422.
═══════════════════════════════════════
RAPID ON-SITE EVALUATION (ROSE) Cytopathologist: Dr. Steven Wu
Station 7: ADEQUATE. Non-necrotizing granulomas with multinucleated giant cells. No malignancy. No caseating necrosis. Findings consistent with SARCOIDOSIS. AFB stain negative on preliminary smear.
Station 4R: Similar granulomatous inflammation
Station 10R: Granulomas id[REDACTED]
Station 11R: Reactive hyperplasia with scattered granulomas
═══════════════════════════════════════
SPECIMENS SUBMITTED □ Cytology specimens: Stations 7, 4R, 10R, 11R (4 containers) □ Cell block: Station 7 (1 container) □ Flow cytometry: Station 7 (1 tube, negative for clonal population) □ Microbiology: Station 7
•	AFB smear and culture (1 container)
•	Fungal culture (1 container)
•	Bacterial culture (1 container)
Total specimens: 9 containers
═══════════════════════════════════════
PROCEDURE OUTCOMES
ESTIMATED BLOOD LOSS: <5mL
COMPLICATIONS: None
PATIENT [REDACTED]: Excellent
•	No hypoxemia (SpO2 remained >94% throughout)
•	Hemodynamically stable
•	No arrhythmias
•	Recovered from sedation appropriately
═══════════════════════════════════════
FLUOROSCOPY: Not utilized
IMMEDIATE POST-PROCEDURE CARE
•	Monitored in recovery area
•	Vital signs stable
•	No respiratory distress
•	Diet: NPO x 1 hour, then advanced to regular diet
•	Activity: Ad lib
•	Discharge: To outpatient status after 2-hour observation
═══════════════════════════════════════
DIAGNOSTIC IMPRESSION
2.	Successful EBUS-TBNA with adequate tissue acquisition from multiple mediastinal lymph node stations
3.	ROSE cytology demonstrates NON-NECROTIZING GRANULOMATOUS INFLAMMATION consistent with STAGE II PULMONARY SARCOIDOSIS (bilateral hilar and mediastinal lymphadenopathy)
4.	No evidence of malignancy
5.	Final pathology and culture results pending (5-7 business days)
═══════════════════════════════════════
FOLLOW-UP PLAN
2.	Final pathology review when available (patient portal notification)
3.	Pulmonology clinic follow-up in 2 weeks to review final results and discuss management
4.	Obtain baseline PFTs with DLCO if not recently performed
5.	Consider ophthalmology evaluation (baseline for sarcoid monitoring)
6.	Serum ACE level, calcium level (if not recently checked)
7.	If cultures negative and final pathology confirms sarcoid:
o	Assess for treatment indication based on symptoms
o	If asymptomatic observation vs. treatment decision
o	Prednisone therapy if indicated
8.	Patient educated regarding diagnosis of sarcoidosis, prognosis generally favorable for Stage II disease
9.	Provided written information regarding sarcoidosis
10.	Return precautions reviewed: fever, chest pain, worsening dyspnea, hemoptysis
═══════════════════════════════════════
ATTESTATION
I performed this procedure and was present for all critical portions. The patient was appropriately monitored throughout. This note represents my assessment and plan.
Electronically Signed: Margaret Chang, MD, FCCP Interventional Pulmonology Date/Time: [REDACTED] 14:55
═══════════════════════════════════════
________________________________________"""

e10 = [
    # Top Section (Foster)
    {"label": "PROC_METHOD", **get_span(t10, "Endobronchial Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Needle Aspiration", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Lung mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "lymph nodes", 1)},
    {"label": "MEDICATION", **get_span(t10, "Versed", 1)},
    {"label": "MEDICATION", **get_span(t10, "Fentanyl", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "carina", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "36mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "lymph node", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "23mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "lymph node", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "18mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "stations 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "12mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "11R", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "15mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "ultrasound bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "4", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "CANCER CELLS FOUND", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 10R", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Normal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 11R", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Normal", 1)},
    
    # Bottom Section (Chang)
    {"label": "PROC_METHOD", **get_span(t10, "Endobronchial Ultrasound", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial Needle Aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mediastinal lymphadenopathy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "4R", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "11R", 2)},
    {"label": "MEDICATION", **get_span(t10, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(t10, "Fentanyl", 2)},
    {"label": "MEDICATION", **get_span(t10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(t10, "Lidocaine", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Bronchoscope", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "TBNA Needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22-gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Ultrasound system", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Main bronchi", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 1", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Right upper paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "9mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Left upper paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Right lower paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "23mm x 14mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Left lower paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "17mm x 11mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "38mm x 26mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Right hilar", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "19mm x 12mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Left hilar", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm x 9mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Right interlobar", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "21mm x 13mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 11L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Left interlobar", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "11mm x 7mm", 1)},
    
    # TBNA
    {"label": "ANAT_LN_STATION", **get_span(t10, "STATION 7", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "38mm x 26mm x 22mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RMB", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LMB", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22G", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "ADEQUATE", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "NON-NECROTIZING GRANULOMAS", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "SARCOIDOSIS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "STATION 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "23mm x 14mm", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Granulomatous inflammation", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "STATION 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "19mm x 12mm", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Granulomas", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "STATION 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "21mm x 13mm", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Reactive lymphoid hyperplasia", 1)},
    
    # ROSE Summary
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 7", 3)},
    {"label": "OBS_ROSE", **get_span(t10, "ADEQUATE", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Non-necrotizing granulomas", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "SARCOIDOSIS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 10R", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 11R", 3)},
    {"label": "OBS_ROSE", **get_span(t10, "Reactive hyperplasia", 1)},
    
    # Specimens
    {"label": "ANAT_LN_STATION", **get_span(t10, "Stations 7, 4R, 10R, 11R", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cell block", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 7", 4)},
    
    # Impression
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 4)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "mediastinal lymph node stations", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "NON-NECROTIZING GRANULOMATOUS INFLAMMATION", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "PULMONARY SARCOIDOSIS", 1)},
]
BATCH_DATA.append({"id": "2947385", "text": t10, "entities": e10})

if __name__ == "__main__":
    for c in BATCH_DATA:
        add_case(c['id'], c['text'], c['entities'], REPO_ROOT)