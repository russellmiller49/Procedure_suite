import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    """
    def find_nth(haystack, needle, n):
        start = -1
        for _ in range(n):
            start = haystack.find(needle, start + 1)
            if start == -1:
                return -1
        return start

    start_index = find_nth(text, term, occurrence)
    if start_index == -1:
        start_index = find_nth(text.lower(), term.lower(), occurrence)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")

    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Note 1: 2025-IP-9847_syn_1
# ==========================================
t1 = """Indication: LLL nodule, 2.6cm, PET+. Surgically ineligible.
Procedure: Flexible bronchoscopy, EMN (Veran), Radial EBUS, Cryoablation.
Target: LLL lateral basal segment.
Action: Navigated to lesion. Confirmed w/ REBUS (concentric). Cryoprobe inserted. 3 cycles freeze/thaw performed (-165C). Ice ball visualized.
Complications: None.
Plan: Admit, CXR, CT in 24h."""

e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "2.6cm", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EMN", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Veran", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "lateral basal segment", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "REBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)},
    {"label": "MEAS_TEMP", **get_span(t1, "-165C", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CXR", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CT", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2025-IP-9847_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: Bronchoscopic Cryoablation of Peripheral Pulmonary Malignancy.
The patient, a 70-year-old female with significant comorbidities precluding surgical resection, underwent palliative ablation of a PET-avid left lower lobe nodule. Under general anesthesia, the airway was secured. Utilizing electromagnetic navigation (Veran SPiN) and radial endobronchial ultrasound confirmation, the target lesion in the lateral basal segment was localized. A cryoablation probe was advanced into the tumor core. A modified protocol utilizing three freeze-thaw cycles was executed to ensure adequate tumoricidal effect given the lesion diameter (>2.5cm). Post-procedural imaging via radial EBUS confirmed a hyperechoic ablation zone extending beyond the tumor margins."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Cryoablation", 1)},
    {"label": "OBS_LESION", **get_span(t2, "Peripheral Pulmonary Malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Veran SPiN", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial endobronchial ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "lateral basal segment", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "cryoablation probe", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "three", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 2)},
    {"label": "MEAS_SIZE", **get_span(t2, ">2.5cm", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 2)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2025-IP-9847_syn_3
# ==========================================
t3 = """CPT Justification:
31641: Bronchoscopy with destruction of tumor. 
- Technique: Cryoablation (Erbecryo system).
- Target: LLL peripheral nodule (Malignant).
- Effort: 3 freeze-thaw cycles performed to destroy tumor tissue.
- Guidance: EMN and Radial EBUS used for localization (integral to successful placement of ablation probe)."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "destruction of tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Cryoablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Erbecryo system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Malignant", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "3", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(t3, "EMN", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "ablation probe", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2025-IP-9847_syn_4
# ==========================================
t4 = """Procedure Note - Pulmonary
Patient: [REDACTED]
Attending: Dr. Zhang

Steps:
1. Time out. GA induced. 8.0 ETT placed.
2. Scope passed. Airways patent.
3. Veran navigation to LLL lateral basal nodule.
4. Radial EBUS confirmed lesion (26mm).
5. Cryoprobe placed. 3 freeze cycles performed.
6. No bleeding. Extubated.

Plan: Admit for obs."""

e4 = [
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Scope", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Veran", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "lateral basal", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "26mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "3", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2025-IP-9847_syn_5
# ==========================================
t5 = """cryo ablation procedure for Lucia Morales today for that LLL cancer shes not a surgery candidate. used general anesthesia intubated. used the veran system to get out there took a while cause of the angle. radial ebus confirmed it solid mass. stuck the cryo probe in froze it three times just to be sure cause its big. saw the ice ball on fluoro looks good. no bleeding really pulled everything out woke her up sent to pacu."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "cryo ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "veran system", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "radial ebus", 1)},
    {"label": "OBS_LESION", **get_span(t5, "solid mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "cryo probe", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "three", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "fluoro", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2025-IP-9847_syn_6
# ==========================================
t6 = """Flexible bronchoscopy with electromagnetic navigation and cryoablation of left lower lobe peripheral pulmonary nodule. Patient is a 70-year-old woman with extensive medical comorbidities. General anesthesia induced. Electromagnetic navigation bronchoscopy commenced using Veran SPiN Planning and Navigation System. Target lesion in left lower lobe lateral basal segment id[REDACTED]. Radial EBUS probe advanced through EWC. Cryoablation probe introduced. Three freeze-thaw cycles performed. Post-ablation radial EBUS repeated showing marked hyperechoic changes. No hemorrhage. Patient reversed from anesthesia."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "electromagnetic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Veran SPiN Planning and Navigation System", 1)},
    {"label": "OBS_LESION", **get_span(t6, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "left lower lobe", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "EWC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Cryoablation probe", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Three", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "radial EBUS", 2)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2025-IP-9847_syn_7
# ==========================================
t7 = """[Indication]
LLL Nodule (Adenocarcinoma), Medically Inoperable.
[Anesthesia]
General, ETT.
[Description]
Navigation to LLL lateral basal segment (Veran). Radial EBUS confirmation. Cryoablation performed (3 cycles: 6min/6min/5min). Ice ball confirmed via fluoroscopy and REBUS. No complications.
[Plan]
Admit, Telemetry, post-op CT."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Nodule", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Veran", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Cryoablation", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "3", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "6min", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "6min", 2)},
    {"label": "MEAS_TIME", **get_span(t7, "5min", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "REBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "CT", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2025-IP-9847_syn_8
# ==========================================
t8 = """[REDACTED] for treatment of her left lung cancer. Because surgery wasn't safe for her, we proceeded with a bronchoscopic ablation. After she was asleep, we used a navigation system to guide a catheter out to the tumor in the lower part of her left lung. We double-checked the position with ultrasound. Then, we inserted a freezing probe right into the tumor and ran three cycles of extreme cold to destroy the cancer cells. Everything went smoothly, and she woke up well."""

e8 = [
    {"label": "LATERALITY", **get_span(t8, "left", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lung cancer", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "bronchoscopic ablation", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "navigation system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "lower part", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "left lung", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "freezing probe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "MEAS_COUNT", **get_span(t8, "three", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2025-IP-9847_syn_9
# ==========================================
t9 = """Operation: Bronchoscopy with tumor destruction.
Technique: Cryotherapy.
Action: The LLL lateral basal tumor was localized via electromagnetic guidance. The cryoprobe was positioned centrally. Three cycles of freezing were administered to ablate the tissue. 
Outcome: Successful destruction of target lesion with adequate margins."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Cryotherapy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "lateral basal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(t9, "electromagnetic guidance", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "Three", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2025-IP-9847
# ==========================================
t10 = """PATIENT NAME: [REDACTED]
MEDICAL RECORD [REDACTED]: 2025-IP-9847
DATE OF BIRTH: [REDACTED] (Age 70 years)
PROCEDURE DATE: [REDACTED]
INSTITUTION: [REDACTED]
ATTENDING PHYSICIAN: Kevin Zhang, MD, FCCP, DABIP
FELLOWS: Dr. Lisa Nguyen (PGY-6), Dr. Thomas Wright (PGY-5)
ANESTHESIA PROVIDER: Dr. Susan Mitchell, MD

PREOPERATIVE DIAGNOSIS:
Left lower lobe pulmonary nodule, 2.6 cm, lateral basal segment, highly suspicious for primary lung cancer based on PET-avid characteristics (SUV 11.2) and growth on serial imaging (1.8 cm six months prior). Transbronchial biopsy via radial EBUS on [REDACTED] yielded adenocarcinoma with TTF-1 positivity.

POSTOPERATIVE DIAGNOSIS: Same as preoperative

OPERATION PERFORMED:
Flexible bronchoscopy with electromagnetic navigation and cryoablation of left lower lobe peripheral pulmonary nodule

CLINICAL SCENARIO:
Patient is a 70-year-old woman with extensive medical comorbidities including severe emphysema (FEV1 32% predicted, DLCO 38% predicted), obesity (BMI 38), diabetes mellitus type 2 with complications including diabetic nephropathy (CKD stage 3b, baseline Cr 1.8), and history of pulmonary embolism on chronic anticoagulation with apixaban. Cardiopulmonary exercise testing demonstrated VO2 max of 11 mL/kg/min. Thoracic surgery evaluation concluded operative mortality risk >25% and declined surgical candidacy. Discussed at multidisciplinary tumor board with medical oncology, radiation oncology, thoracic surgery, and interventional pulmonology. Given patient preference for minimally invasive approach and contraindications to SBRT (previous radiation to left chest for breast cancer), bronchoscopic ablation recommended as optimal treatment strategy.

DESCRIPTION OF PROCEDURE:
After obtaining informed consent and completing universal protocol time-out, patient brought to IP suite. Standard ASA monitors applied. Pre-procedure antibiotics NOT administered per institutional protocol for ablation procedures. 

General anesthesia induced by anesthesiology team. Oral endotracheal intubation performed using 8.0 mm inner diameter tube with video laryngoscope assistance. Tube positioned at 21 cm at incisors. Bilateral breath sounds confirmed. 

Olympus therapeutic videobronchoscope (BF-P290) introduced through endotracheal tube. Comprehensive inspection of airways performed and documented:
- Normal supraglottic structures
- Trachea: patent, no masses or compression, mild tracheomalacia
- Carina: sharp, mobile
- Right bronchial tree: normal segmental anatomy
- Left bronchial tree: normal upper lobe segments; lower lobe segments patent, no endobronchial abnormalities visualized

Electromagnetic navigation bronchoscopy commenced using Veran SPiN Planning and Navigation System. Pre-loaded CT scan from [REDACTED] with 1mm slice thickness utilized for planning. Target lesion in left lower lobe lateral basal segment id[REDACTED] at 2.6 x 2.4 cm. Virtual bronchoscopy pathway created and navigation pathway optimized.

Registration performed using automated CT-to-body registration with 6 fiducial points. Registration error: 2.8mm (acceptable, <4mm threshold). 

Steerable guide sheath (8.0 Fr) with always-on tip tracking advanced through working channel. Navigation to target required approximately 15 minutes with multiple adjustments due to peripheral location and acute branching angles. Extended working channel passed through guide sheath.

Radial EBUS probe (20 MHz) advanced through EWC. Multiple radial planes examined showing solid, hypoechoic mass in direct contact position with probe centered within lesion. Lesion characteristics: heterogeneous internal echogenicity, irregular borders, size 26 x 23 mm consistent with imaging and expected tumor characteristics.

Fluoroscopic confirmation performed showing guide sheath in appropriate peripheral location, approximately 3cm from pleural surface. Cone-beam CT would have been ideal but unavailable due to C-arm equipment malfunction (documented in safety report).

Cryoablation probe introduced (erbecryo 2 system, 2.4mm diameter probe with 3cm freeze zone). Probe advanced through EWC to center of lesion based on prior radial EBUS measurements. Due to technical considerations of lesion size >2.5cm, decision made to perform THREE freeze-thaw cycles rather than standard two cycles to ensure adequate margins:

Cycle 1: 
- Freeze time: 6 minutes
- Temperature at probe tip: -165°C (monitor displayed continuous temperature throughout)
- Passive thaw: 4 minutes (until temperature >-20°C)

Cycle 2:
- Freeze time: 6 minutes  
- Temperature: -167°C
- Passive thaw: 4 minutes

Cycle 3:
- Freeze time: 5 minutes
- Temperature: -163°C
- Active thaw: 2 minutes using helium warming (to expedite procedure completion given >90 min elapsed time)

Throughout ablation cycles, patient monitored closely. Vital signs stable: HR 68-78 bpm, BP 128-142/72-85 mmHg, SpO2 97-99% on FiO2 0.5. No arrhythmias noted on continuous ECG monitoring. Ice ball formation visualized fluoroscopically during freeze cycles with appropriate coverage of target region and safety margin.

Post-ablation radial EBUS repeated showing marked hyperechoic changes throughout tumor volume consistent with ice crystal formation and cellular destruction. Ablation zone appeared to extend approximately 5mm beyond original tumor margins in all directions - adequate for oncologic treatment.

Cryoprobe removed slowly. Guide sheath withdrawn under direct visualization with sequential airway inspection. Findings:
- Mild mucosal blanching at peripheral contact points (expected, transient)
- No hemorrhage
- No airway perforation
- Small amount of blood-tinged secretions suctioned (<5 mL estimated)

Complete re-examination of left bronchial tree performed post-procedure showing patent airways without evidence of significant edema or injury. 

Bronchoscope withdrawn. Patient reversed from anesthesia per standard protocol. Extubation successful with adequate respiratory drive and airway protective reflexes. Transferred to PACU in stable condition with SpO2 95% on 3L nasal cannula.

FINDINGS:
1. Successful navigation to LLL lateral basal segment target
2. Cryoablation performed per modified protocol (3 cycles for larger lesion)
3. Adequate ablation zone achieved based on post-procedure EBUS
4. No procedural complications

SPECIMENS: None

ESTIMATED BLOOD LOSS: <10 mL

INTRAVENOUS FLUIDS: 850 mL lactated Ringer's solution

COMPLICATIONS: None intraoperatively

DRAINS/TUBES: None placed

POST-PROCEDURE ORDERS:
1. Admit to Pulmonary PCU (4 West) for monitoring
2. Continuous telemetry and pulse oximetry
3. Chest X-ray portable in 4 hours to evaluate for pneumothorax/complications
4. CT chest with IV contrast at 24 hours for baseline post-ablation imaging
5. Pain management: acetaminophen 1000mg PO q8h scheduled, oxycodone 5-10mg PO q4h PRN moderate pain, morphine 2-4mg IV q3h PRN severe pain
6. Resume apixaban 24 hours post-procedure (held for 48 hours pre-procedure)
7. Continue home medications including insulin regimen
8. Incentive spirometry 10x/hour while awake
9. Ambulation with assistance as tolerated
10. Diet as tolerated
11. DVT prophylaxis: sequential compression devices (no pharmacologic prophylaxis until anticoagulation resumed)

FOLLOW-UP PLAN:
- Anticipated discharge POD 1 if uncomplicated course
- Clinic appointment in 1 week with chest X-ray
- CT chest at 6 weeks for initial response assessment (expect central low attenuation with peripheral rim enhancement on post-ablation changes)
- PET-CT at 3 months for metabolic response evaluation
- Continued surveillance per NCCN guidelines with CT every 3-6 months for 2 years, then annually

DISCUSSION WITH PATIENT/FAMILY:
Extensive post-procedure discussion held with patient and daughter (healthcare proxy). Explained technical success of procedure, expected post-procedure course, and importance of close follow-up. Reviewed warning signs requiring immediate attention: severe chest pain, shortness of breath, hemoptysis, fever. Questions answered. Patient and family expressed understanding and satisfaction with care.

Total procedure time: 94 minutes
Fluoroscopy time: 4.7 minutes  
Radiation dose: 287 mGy-cm²

ATTESTATION: I was present for and personally performed the key components of this procedure including navigation, targeting, ablation, and post-procedure assessment.

___________________________________________
Kevin Zhang, MD, FCCP, DABIP
Associate Professor of Medicine
Director of Advanced Bronchoscopy Fellowship
Division of Pulmonary, Allergy, and Critical Care Medicine
Stanford University School of Medicine

Co-signed by:
Lisa Nguyen, MD (Pulmonary/Critical Care Fellow, PGY-6)

Procedure dictated: [REDACTED] 16:45
Transcribed: [REDACTED] 17:20
Electronically authenticated: [REDACTED] 18:05"""

e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(t10, "pulmonary nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.6 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "lateral basal segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lung cancer", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t10, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "electromagnetic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(t10, "pulmonary nodule", 2)},
    {"label": "OBS_LESION", **get_span(t10, "pulmonary embolism", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchoscopic ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "videobronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right bronchial tree", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left bronchial tree", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Veran SPiN Planning and Navigation System", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Target lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "left lower lobe", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "lateral basal segment", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.6 x 2.4 cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "guide sheath", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Extended working channel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "guide sheath", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "probe", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "EWC", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "26 x 23 mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Fluoroscopic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "guide sheath", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "Cone-beam CT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cryoablation probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "erbecryo 2 system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "probe", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "EWC", 2)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "radial EBUS", 2)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 4)},
    {"label": "MEAS_SIZE", **get_span(t10, ">2.5cm", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "THREE", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "freeze-thaw cycles", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "6 minutes", 1)},
    {"label": "MEAS_TEMP", **get_span(t10, "-165°C", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "4 minutes", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "6 minutes", 2)},
    {"label": "MEAS_TEMP", **get_span(t10, "-167°C", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "4 minutes", 2)},
    {"label": "MEAS_TIME", **get_span(t10, "5 minutes", 1)},
    {"label": "MEAS_TEMP", **get_span(t10, "-163°C", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "2 minutes", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "radial EBUS", 3)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 3)},
    {"label": "OBS_FINDING", **get_span(t10, "ice crystal formation", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 4)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cryoprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Guide sheath", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "hemorrhage", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "left bronchial tree", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "lateral basal segment", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "Cryoablation", 2)},
    {"label": "MEAS_COUNT", **get_span(t10, "3", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 2)},
    {"label": "MEAS_TIME", **get_span(t10, "94 minutes", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "4.7 minutes", 1)}
]
BATCH_DATA.append({"id": "2025-IP-9847", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)
