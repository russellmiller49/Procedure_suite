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
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return start_index, start_index + len(term)

# ==========================================
# Note 1: 1589403_syn_1
# ==========================================
t1 = """Procedure: Valve Removal RUL.
- Indication: Recurrent pneumonia.
- Findings: 3 valves in place, mucus plugging.
- Action: All 3 removed via forceps.
- Result: Airways patent, secretions cleared.
- Plan: Discharge."""

e1 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "Valve Removal", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t1, "RUL", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t1, "3", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t1, "valves", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t1, "mucus plugging", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t1, "3", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "removed", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t1, "forceps", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t1, "Airways", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(t1, "patent", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t1, "secretions", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1589403_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: The patient presented for removal of endobronchial valves due to infectious complications. Under general anesthesia, the Right Upper Lobe was interrogated. Three Zephyr valves were id[REDACTED]. Each valve was sequentially grasped and retrieved without incident. Significant mucous plugging distal to the valves was aspirated. The airway was patent at the conclusion of the procedure."""

e2 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "removal", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t2, "endobronchial valves", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t2, "Right Upper Lobe", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t2, "Three", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t2, "Zephyr valves", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t2, "valve", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t2, "mucous plugging", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t2, "valves", 3)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t2, "airway", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(t2, "patent", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1589403_syn_3
# ==========================================
t3 = """Codes: 31648 (Valve removal). Site: [REDACTED]"""

e3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "Valve removal", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1589403_syn_4
# ==========================================
t4 = """Resident Note: Valve Removal
1. Pt with RUL valves + pneumonia.
2. Bronch down.
3. Pulled 3 valves from RUL using forceps.
4. Suctioned a lot of mucus.
5. No bleeding.
Plan: Antibiotics, follow up."""

e4 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "Valve Removal", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t4, "RUL", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t4, "valves", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t4, "Bronch", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t4, "3", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t4, "valves", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t4, "RUL", 2)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "Suctioned", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t4, "mucus", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t4, "No bleeding", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1589403_syn_5
# ==========================================
t5 = """taking out valves for michael torres. he keeps getting pneumonia. went in saw the three valves in the rul. pulled them out one by one. tons of junk behind them suctioned it all out. airway looks open now. done."""

e5 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "taking out", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t5, "valves", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t5, "three", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t5, "valves", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t5, "rul", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t5, "junk", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "suctioned", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t5, "airway", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(t5, "open", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1589403_syn_6
# ==========================================
t6 = """Bronchoscopic removal of endobronchial valves was performed. Indication was recurrent pneumonia. Three Zephyr valves were removed from the RUL using retrieval forceps. Mucous plugging was cleared. The patient tolerated the procedure well."""

e6 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t6, "Bronchoscopic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "removal", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t6, "endobronchial valves", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t6, "Three", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t6, "Zephyr valves", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "removed", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t6, "RUL", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t6, "retrieval forceps", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t6, "Mucous plugging", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1589403_syn_7
# ==========================================
t7 = """[Indication]
Infected BLVR / Pneumonia.
[Anesthesia]
General.
[Description]
Removal of 3 Zephyr valves from RUL. Airway clearance of mucus.
[Plan]
Observation, antibiotics."""

e7 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "Removal", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t7, "3", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t7, "Zephyr valves", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t7, "RUL", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t7, "Airway", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "clearance", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t7, "mucus", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1589403_syn_8
# ==========================================
t8 = """[REDACTED] of his lung volume reduction valves due to recurrent infections. We went in bronchoscopically and removed all three valves from the right upper lobe. There was a lot of mucus trapped behind them, which we cleared out. The procedure was successful and should help clear up his infection."""

e8 = [
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t8, "lung volume reduction valves", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t8, "bronchoscopically", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "removed", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t8, "three", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t8, "valves", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t8, "right upper lobe", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t8, "mucus", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1589403_syn_9
# ==========================================
t9 = """Procedure: Extraction of bronchial prostheses.
Reason: Post-obstructive infection.
Action: Retrieval of 3 valves. Aspiration of retained secretions.
Result: Restoration of lobar ventilation."""

e9 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "Extraction", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t9, "bronchial prostheses", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "Retrieval", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t9, "3", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t9, "valves", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "Aspiration", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t9, "secretions", 1)))}
]
BATCH_DATA.append({"id": "1589403_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1589403
# ==========================================
t10 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
Photodynamic Therapy - Light Application Session
FieldValuePatient NameAnderson, MargaretAge/Sex71/FMRN1478392Date of ServiceOctober 12, 2024Procedure Date/TimeStart: 08:15, End: 09:45Attending PhysicianDr. Raymond Chen, MDAssistantDr. Lisa Martinez, Fellow
PREOPERATIVE DIAGNOSIS
Endobronchial squamous cell carcinoma, left mainstem bronchus, early stage (T1aN0M0), patient declined surgery
POSTOPERATIVE DIAGNOSIS
Same
PROCEDURES PERFORMED

Photodynamic therapy - laser light application (CPT code: verify)
Flexible bronchoscopy with tumor measurement and documentation

PHOTOSENSITIZER ADMINISTRATION

Agent: Porfimer sodium (Photofrin®)
Dose: 2 mg/kg IV
Total dose administered: 138 mg (patient weight 69 kg)
Administration date/time: [REDACTED] at 14:00 hours
Time from photosensitizer to light: 48 hours (optimal window: 40-50 hours)

ANESTHESIA
General anesthesia with endotracheal intubation (8.0mm ETT)
Anesthesia team: Dr. William Park (attending), Samantha Lee CRNA
MONITORING
Standard ASA monitors plus:

Continuous pulse oximetry
End-tidal CO2
Arterial line (right radial)

EQUIPMENT

Olympus BF-1T180 therapeutic bronchoscope
Cylindrical diffusing fiber (2.5cm length, 400 micron core diameter)
Diode laser system: 630nm wavelength
Light dosimetry calculation performed pre-procedure

DETAILED PROCEDURE NARRATIVE
The patient was [REDACTED] the endoscopy suite. After successful induction of general anesthesia and orotracheal intubation, a time-out was performed verifying correct patient, procedure, and photosensitizer administration timing.
Initial Bronchoscopic Survey:
The bronchoscope was introduced through the endotracheal tube. Systematic examination revealed:

Upper airways: Normal
Trachea: Patent, no lesions
Carina: Sharp, normal
Right bronchial tree: Entirely normal, no endobronchial lesions
Left bronchial tree: Endobronchial tumor visible in left mainstem bronchus

Tumor Characteristics (Pre-PDT measurements):

Location: Left mainstem bronchus, 2cm distal to carina on medial wall
Size: 1.8cm (longitudinal) × 0.9cm (circumferential extent)
Morphology: Flat, slightly raised plaque-like lesion
Color: Pink-red with areas of white keratinization
Surface: Irregular, slightly friable appearance
Obstruction: Approximately 30% luminal narrowing
Distal airways: LUL and LLL fully patent

Photodynamic Therapy Light Delivery:
Laser safety protocols confirmed (room signage, protective eyewear, fire safety measures in place). The cylindrical diffusing fiber was introduced through the working channel of the bronchoscope. The fiber was positioned to center the tumor within the treatment field. Distance measurements confirmed using bronchoscope markings.
Treatment Parameters:

Wavelength: 630 nm (red laser light, optimal for Photofrin activation)
Power output: 400 mW/cm of diffuser length
Diffuser length: 2.5 cm
Total power: 1000 mW (1.0 W)
Light dose (fluence): 200 J/cm² of diffuser surface
Treatment time: 500 seconds (8 minutes 20 seconds)
Calculation: 200 J/cm² ÷ 0.4 W/cm = 500 seconds

Light was continuously delivered for the calculated duration. During light application:

Laser energy meter verified consistent power output
No visible tissue changes during light delivery (expected)
No charring or thermal effects observed (confirming non-thermal mechanism)
Patient [REDACTED] throughout
No arrhythmias or desaturations

Post-Treatment Assessment:
Immediately following light delivery, the treated area appeared essentially unchanged (expected for PDT). No immediate edema, no bleeding. The fiber was removed and the bronchoscope withdrawn.
Light Precautions Review:
Post-procedure, the following light precautions were reviewed with patient and family:

Strict avoidance of direct sunlight and bright indoor lights for 30 days minimum
Wear protective clothing, wide-brimmed hat, gloves when outdoors
Gradual re-exposure to normal light starting day 30 with skin testing
Emergency contact information provided
Written instructions given

The patient tolerated the procedure well. Extubated in the OR without difficulty. Transferred to PACU in stable condition.
SPECIMENS
None (non-excisional therapy)
ASSESSMENT AND PLAN
This 71-year-old female with early-stage endobronchial squamous cell carcinoma (biopsy-proven [REDACTED]) underwent photodynamic therapy light application session without complications.
Timeline for Follow-up Bronchoscopy:

Scheduled debridement bronchoscopy: [REDACTED] (48 hours post-light)
Anticipated findings: Necrotic tumor debris requiring mechanical removal
Will assess treatment response and obtain biopsies from treatment bed

Ongoing Management:

Continue light precautions (patient education reinforced)
Monitor for post-PDT complications: airway edema, photosensitivity reactions
Dexamethasone 4mg PO BID x 5 days (reduce airway inflammation)
PPI therapy (reduce risk of esophageal photosensitivity)
Debridement session in 2 days

Long-term surveillance:
Bronchoscopic surveillance at 1, 3, 6, and 12 months post-treatment per protocol.
Procedure Note - EBV Removal
Patient [REDACTED] 59M MRN [REDACTED], [REDACTED], Dr. Amanda Foster attending
Indication: Patient had Zephyr valves placed in RUL 6 months ago for emphysema. Developed recurrent pneumonias and productive cough. Decision made to remove valves.
Patient [REDACTED] OR under general anesthesia with 8.5 ETT. Bronchoscope introduced. Right upper lobe examined - all three valves visible and in good position but significant mucous plugging noted distal to valves.
Valve 1 (RB1 apical segment): Grasped with retrieval forceps, removed without difficulty. Some mucous plug came out with valve.
Valve 2 (RB2 posterior segment): This one had granulation tissue at the rim. Used forceps to remove valve, small amount bleeding from granulation tissue controlled with epinephrine and ice saline.
Valve 3 (RB3 anterior segment): Removed easily with forceps.
After valve removal the RUL segments were suctioned extensively. Thick secretions cleared. Mucosa was edematous but no active bleeding. Airways now patent.
Left lung examined - normal. Patient tolerated well, extubated, transferred to recovery.
Specimens: 3 Zephyr valves (not sent to pathology per protocol, retained for documentation), mucous plugs sent for culture.
Follow up: CXR in AM. Likely improved ventilation to RUL now. Patient understands FEV1 may decrease as we've reversed the lung volume reduction effect but pneumonia risk should improve. Will see in clinic 2 weeks."""

e10 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "Photodynamic Therapy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "Endobronchial squamous cell carcinoma", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "left mainstem bronchus", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "Photodynamic therapy", 1)))}, # Fixed: 'Photodynamic therapy' (case-sensitive) only appears once
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "Flexible bronchoscopy", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(t10, "Porfimer sodium", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(t10, "Photofrin", 1)))},
    {"label": "CTX_TIME", **dict(zip(["start", "end"], get_span(t10, "14:00", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "8.0mm", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "ETT", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "BF-1T180", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "therapeutic bronchoscope", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Cylindrical diffusing fiber", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "2.5cm", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "400 micron", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Diode laser system", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "630nm", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "bronchoscope", 2)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "Trachea", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(t10, "Patent", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "Carina", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "Right bronchial tree", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "Left bronchial tree", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "Endobronchial tumor", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "left mainstem bronchus", 2)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "1.8cm", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "0.9cm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "LUL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "LLL", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(t10, "fully patent", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "630 nm", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "2.5 cm", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(t10, "200 J/cm²", 1)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(t10, "500 seconds", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "squamous cell carcinoma", 2)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(t10, "Dexamethasone", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t10, "Zephyr valves", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RUL", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "8.5 ETT", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Bronchoscope", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "Right upper lobe", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "three", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t10, "valves", 2)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "mucous plugging", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t10, "Valve 1", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RB1", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "apical segment", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "retrieval forceps", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "mucous plug", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t10, "Valve 2", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RB2", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "posterior segment", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "forceps", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(t10, "epinephrine", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t10, "Valve 3", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RB3", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "anterior segment", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "forceps", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RUL", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "suctioned", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "secretions", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "edematous", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "Airways", 1)))}, # Fixed: 'Airways' (Capital A) appears once
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(t10, "patent", 2)))}, # Fixed: 'patent' (lower p) appears twice
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "3", 1)))},
    {"label": "DEV_VALVE", **dict(zip(["start", "end"], get_span(t10, "Zephyr valves", 2)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "mucous plugs", 1)))}
]
BATCH_DATA.append({"id": "1589403", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)