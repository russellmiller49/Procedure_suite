import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function to add the case
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1478392_syn_1
# ==========================================
t1 = """Proc: PDT Light Application.
Target: L Mainstem SCC.
Dosimetry: 200 J/cm2, 2.5cm diffuser.
Action: Light delivered 500 sec @ 630nm.
Response: No immediate reaction (expected).
Plan: Light precautions. Debridement in 48h."""
e1 = [
    {"label": "PROC_METHOD", **get_span(t1, "PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Light Application", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "L Mainstem", 1)},
    {"label": "OBS_LESION", **get_span(t1, "SCC", 1)},
    {"label": "MEAS_ENERGY", **get_span(t1, "200 J/cm2", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "2.5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "diffuser", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Light delivered", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "500 sec", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No immediate reaction", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Debridement", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1478392_syn_2
# ==========================================
t2 = """OPERATIVE NOTE: Photodynamic Therapy (Light Activation).
INDICATION: Endobronchial squamous cell carcinoma, Left Mainstem.
PROTOCOL: Photofrin 2mg/kg administered 48h prior. 
PROCEDURE: A 2.5cm cylindrical diffuser was positioned across the tumor bed. Laser light at 630nm was delivered to a total fluence of 200 J/cm2 (Total time 500s). The patient tolerated the light activation phase without hemodynamic instability."""
e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Photodynamic Therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Light Activation", 1)},
    {"label": "OBS_LESION", **get_span(t2, "squamous cell carcinoma", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "Left Mainstem", 1)},
    {"label": "MEDICATION", **get_span(t2, "Photofrin", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "2.5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "cylindrical diffuser", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "MEAS_ENERGY", **get_span(t2, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "500s", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "without hemodynamic instability", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1478392_syn_3
# ==========================================
t3 = """Billing: 31641 (Bronchoscopy with destruction of tumor).
Technique: Photodynamic therapy (PDT).
Specifics: Laser light delivery to photosensitized tissue (Photofrin). Left mainstem bronchus. Non-thermal ablation."""
e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "destruction of tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Photodynamic therapy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Laser light delivery", 1)},
    {"label": "MEDICATION", **get_span(t3, "Photofrin", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Left mainstem bronchus", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "ablation", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1478392_syn_4
# ==========================================
t4 = """Procedure: PDT Light Session.
Steps:
1. 48h post-Photofrin.
2. Bronch to LMS.
3. Measured tumor.
4. Placed fiber.
5. Delivered 200J/cm2 light.
6. Removed scope.
Plan: Strict light precautions."""
e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Light Session", 1)},
    {"label": "MEDICATION", **get_span(t4, "Photofrin", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Bronch", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "fiber", 1)},
    {"label": "MEAS_ENERGY", **get_span(t4, "200J/cm2", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "scope", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1478392_syn_5
# ==========================================
t5 = """pdt light treatment for [REDACTED]... she got the photofrin 2 days ago... went in with the scope left main tumor is there... put the laser fiber in cooked it for 500 seconds... no bleeding patient ok... remind her about the sunlight precautions."""
e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "pdt", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "light treatment", 1)},
    {"label": "MEDICATION", **get_span(t5, "photofrin", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "left main", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "laser fiber", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "500 seconds", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1478392_syn_6
# ==========================================
t6 = """Patient: [REDACTED]. Procedure: Photodynamic therapy - Light Application. Drug: Photofrin (48h prior). Location: Left Mainstem. Laser: 630nm. Dose: 200 J/cm2. Time: 500s. No complications. Plan: Debridement bronchoscopy in 48 hours."""
e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Photodynamic therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Light Application", 1)},
    {"label": "MEDICATION", **get_span(t6, "Photofrin", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "Left Mainstem", 1)},
    {"label": "MEAS_ENERGY", **get_span(t6, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "500s", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Debridement", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "bronchoscopy", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1478392_syn_7
# ==========================================
t7 = """[Indication]
LMS Squamous Cell CA, PDT protocol.
[Anesthesia]
General.
[Description]
Light application. 630nm laser. 2.5cm diffuser. 200 J/cm2 delivered to tumor.
[Plan]
Avoid sunlight 30 days. Return for clean-out."""
e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Squamous Cell CA", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Light application", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "2.5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "diffuser", 1)},
    {"label": "MEAS_ENERGY", **get_span(t7, "200 J/cm2", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1478392_syn_8
# ==========================================
t8 = """[REDACTED] 48 hours after Photofrin injection for light activation. We positioned the diffuser fiber within the left mainstem bronchus tumor. We delivered the calculated light dose of 200 J/cm2. The procedure went smoothly, and she was reminded of strict light precautions upon discharge."""
e8 = [
    {"label": "MEDICATION", **get_span(t8, "Photofrin", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "light activation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "diffuser fiber", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "left mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "MEAS_ENERGY", **get_span(t8, "200 J/cm2", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1478392_syn_9
# ==========================================
t9 = """Photodynamic therapy - laser light application. Flexible bronchoscopy with tumor quantification and documentation. PHOTOSENSITIZER ADMINISTRATION: Agent: Porfimer sodium. Dose: 2 mg/kg IV. Time from photosensitizer to light: 48 hours."""
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Photodynamic therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "light application", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Flexible bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "MEDICATION", **get_span(t9, "Porfimer sodium", 1)},
]
BATCH_DATA.append({"id": "1478392_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1478392
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
    {"label": "PROC_METHOD", **get_span(t10, "Photodynamic Therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Light Application", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Endobronchial squamous cell carcinoma", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "left mainstem bronchus", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Photodynamic therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "light application", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "MEDICATION", **get_span(t10, "Porfimer sodium", 1)},
    {"label": "MEDICATION", **get_span(t10, "Photofrin", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "therapeutic bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cylindrical diffusing fiber", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.5cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right bronchial tree", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left bronchial tree", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "left mainstem bronchus", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left mainstem bronchus", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.8cm", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "0.9cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "plaque-like lesion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "30% luminal narrowing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "cylindrical diffusing fiber", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.5 cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(t10, "200 J/cm²", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "500 seconds", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate edema", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no bleeding", 1)},
    {"label": "OBS_LESION", **get_span(t10, "squamous cell carcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "photodynamic therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "light application", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "debridement bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 3)},
    {"label": "MEDICATION", **get_span(t10, "Dexamethasone", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Debridement", 1)},
    # Second procedure note in same text
    {"label": "PROC_ACTION", **get_span(t10, "EBV Removal", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Zephyr valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "remove valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Right upper lobe", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "valves", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "mucous plugging", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Valve", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB1 apical segment", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "removed", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "mucous plug", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Valve", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB2 posterior segment", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "granulation tissue", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "remove valve", 1)},
    {"label": "MEDICATION", **get_span(t10, "epinephrine", 1)},
    {"label": "MEDICATION", **get_span(t10, "ice saline", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Valve", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB3 anterior segment", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Removed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL segments", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Thick secretions", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no active bleeding", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "Airways now patent", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Zephyr valves", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "mucous plugs", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
]
BATCH_DATA.append({"id": "1478392", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)