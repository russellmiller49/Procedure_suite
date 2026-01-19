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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 2145069_syn_1
# ------------------------------------------
text_1 = """Indication: Pneumonia, non-resolving.
Sedation: Mod sed.
Procedure: Scope via nose. Airways patent. No endobronchial lesions.
Action: BAL LLL. 100cc in, 80cc return.
Plan: Cultures pending. Continue Abx."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Pneumonia", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "endobronchial lesions", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "100cc", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "80cc", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_1", "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 2145069_syn_2
# ------------------------------------------
text_2 = """PROCEDURE: Diagnostic flexible bronchoscopy with bronchoalveolar lavage.
INDICATION: 82-year-old female with persistent right-sided infiltrates despite antibiotic therapy.
FINDINGS: The tracheobronchial tree was systematically inspected. No endobronchial masses, mucosal irregularities, or foreign bodies were visualized. Thick secretions were noted diffusely. A bronchoalveolar lavage was performed in the left lower lobe (target segment) yielding turbid fluid which was submitted for microbiological analysis."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoalveolar lavage", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "infiltrates", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "tracheobronchial tree", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "endobronchial masses", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "mucosal irregularities", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoalveolar lavage", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left lower lobe", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "turbid fluid", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_2", "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 2145069_syn_3
# ------------------------------------------
text_3 = """Service: Bronchoscopy with BAL (31624).
Medical Necessity: Non-resolving pneumonia (J18.9).
Details: Scope advanced to LLL. 100mL saline instilled in aliquots. 80mL aspirated. Specimen sent for quantitative culture. No biopsy performed (excludes 31628/31625). Diagnostic inspection (31622) included."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "pneumonia", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LLL", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "100mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "80mL", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "Specimen", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_3", "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 2145069_syn_4
# ------------------------------------------
text_4 = """Resident Note
Patient: [REDACTED]
Pre-op Dx: Pneumonia
Steps:
1. Vitals stable. Lidocaine spray.
2. Scope inserted nare.
3. Inspection: Normal anatomy, some secretions.
4. BAL LLL: Good return.
5. Scope out.
Plan: Wait for culture results."""

entities_4 = [
    {"label": "OBS_LESION", **get_span(text_4, "Pneumonia", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Lidocaine", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 2)},
]
BATCH_DATA.append({"id": "2145069_syn_4", "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 2145069_syn_5
# ------------------------------------------
text_5 = """Bronchoscopy for Estelle Getty she has pneumonia that wont go away. used moderate sedation versed and fentanyl. looked around airways look okay just lots of secretions. washed the LLL collected fluid for culture. patient tolerated it fine no o2 desats."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "pneumonia", 1)},
    {"label": "MEDICATION", **get_span(text_5, "versed", 1)},
    {"label": "MEDICATION", **get_span(text_5, "fentanyl", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "airways", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "washed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "LLL", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_5", "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 2145069_syn_6
# ------------------------------------------
text_6 = """Diagnostic flexible bronchoscopy with bronchoalveolar lavage. Indication was non-resolving pneumonia. Upper airway and vocal cords normal. Trachea and main carina normal. Bilateral bronchial trees patent. Purulent secretions noted. BAL performed in LLL. Fluid sent for bacterial, fungal, and AFB culture. Patient stable."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoalveolar lavage", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "pneumonia", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Upper airway", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "vocal cords", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "bronchial trees", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Purulent secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "Fluid", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_6", "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 2145069_syn_7
# ------------------------------------------
text_7 = """[Indication]
Refractory Pneumonia.
[Anesthesia]
Moderate Sedation.
[Description]
Flexible bronchoscopy. Airway inspection negative for mass/lesion. BAL performed LLL. Samples sent for micro.
[Plan]
Adjust antibiotics based on culture."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Pneumonia", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Flexible bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Airway", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "SPECIMEN", **get_span(text_7, "Samples", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_7", "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 2145069_syn_8
# ------------------------------------------
text_8 = """We performed a bronchoscopy on [REDACTED] investigate her persistent pneumonia. After numbing the nose and throat, the scope was passed easily. We didn't see any tumors or blockages, just some thick mucus. We washed the left lower lobe with saline and collected the fluid to check for specific bacteria. She did great during the procedure."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "pneumonia", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumors", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "blockages", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "mucus", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "washed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left lower lobe", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_8", "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 2145069_syn_9
# ------------------------------------------
text_9 = """Procedure: Flexible bronchoscopy with lung washing.
Context: Persistent pulmonary infiltrate.
Action: The bronchial tree was examined. No obstructions were observed. The LLL was lavaged with saline. Effluent was collected for analysis.
Result: Specimen acquired for microbiology."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "lung washing", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "pulmonary infiltrate", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "bronchial tree", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "obstructions", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "lavaged", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "Effluent", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "Specimen", 1)},
]
BATCH_DATA.append({"id": "2145069_syn_9", "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 2145069 (Real Note)
# ------------------------------------------
text_10 = """OPERATIVE REPORT - DETAILED NARRATIVE
PART 1: AIRWAY INTERVENTION (07:45 - 10:15)
Patient [REDACTED] hybrid OR suite. After successful induction of general anesthesia, formal time-out performed with all team members present. Confirmed:

Correct patient (ID [REDACTED], verbal confirmation)
Procedures planned (airway intervention, pericardial window, pleural catheter)
Positioning (supine throughout)
Antibiotic prophylaxis (Cefazolin 2g IV given)
Steroid coverage (Dexamethasone 10mg IV given)
Blood products available (2 units PRBCs typed and crossed)

Initial orotracheal intubation performed by anesthesia with video laryngoscopy - 8.0mm ETT placed without difficulty. Position confirmed at 21cm at teeth with end-tidal CO2 and bilateral breath sounds. However, significantly diminished breath sounds on right side noted.
Initial Flexible Bronchoscopy Survey:
Olympus BF-1T180 therapeutic bronchoscope introduced through ETT. Findings:

Supraglottic structures: Normal, no lesions
Vocal cords: Mobile bilaterally, no masses
Subglottis: Normal caliber, no stenosis
Trachea: Patent, mild mucosal erythema, no significant secretions
Carina: Widened, evidence of external compression from adenopathy
Left main bronchus: Patent, some extrinsic compression but adequate luminal diameter
LUL, Lingula, LLL: All segments visualized and patent
Right main bronchus: CRITICAL FINDING - Near-complete obstruction beginning 1cm from carina. Large fungating tumor mass arising from anterior and lateral walls, extending 4cm distally. Approximately 90% obstruction. Friable, hemorrhagic appearance. Unable to pass bronchoscope beyond lesion. No visualization of RUL, RML, or RLL orifices.

Decision: Proceed with rigid bronchoscopy for tumor debridement and airway restoration.
Rigid Bronchoscopy Phase:
Patient re-positioned with shoulder roll for neck extension. The 8.0mm ETT was removed. A Storz 13mm rigid bronchoscope (Model #8580C) was carefully introduced through the oral cavity under direct visualization using Weerda laryngoscope.
Ventilation strategy: High-frequency jet ventilation (HFJV) via rigid scope side arm. Ventilator settings: Frequency 150/min, Driving pressure 2.0 bar, FiO2 1.0, I:E ratio 1:1.5. Good chest rise and end-tidal CO2 waveform confirmed adequate ventilation.
The rigid scope was advanced through the vocal cords under direct visualization. The trachea was traversed without difficulty. The tumor mass in right mainstem bronchus was encountered.
Mechanical Debridement:
Using the beveled edge of the rigid bronchoscope as a core, the tumor was mechanically debrided with careful forward pressure and rotating motion. Multiple passes were required. Tumor tissue was extremely friable with significant bleeding encountered.
Estimated tumor volume removed via coring: Approximately 20-25 cubic centimeters of tumor tissue
Hemostasis Measures:
As expected, bleeding was brisk during debulking. The following measures were employed:

Iced saline lavage: 500mL total of iced normal saline instilled in 50-100mL aliquots, allowed to dwell 30-60 seconds, then suctioned. This provided temporary hemostasis.
Topical epinephrine: 1:10,000 concentration, total 30mL instilled in divided doses to tumor bed. Significant reduction in bleeding achieved.
Tranexamic acid: 1 gram in 100mL NS instilled topically (in addition to 1g IV given by anesthesia systemically). Further improvement in hemostasis.

After approximately 30 minutes of mechanical debridement and hemostatic measures, adequate visualization of distal airways was achieved. The RUL, RML, and RLL orifices could be visualized, though tumor bulk remained on the airway walls.
Electrocautery:
Flexible bronchoscope (Olympus) passed through rigid barrel. Electrocautery probe advanced through working channel. Residual tumor tissue was cauterized using monopolar cautery at 40 watts in coagulation mode. FiO2 was reduced to 0.4 during cautery per safety protocol.
Treatment areas: Anterior wall, lateral wall, and carina region of right mainstem bronchus
Treatment time: Approximately 8 minutes total cautery time
Effect: Tumor base cauterized, some reduction in tumor bulk, improved hemostasis
Argon Plasma Coagulation:
APC probe (ERBE VIO system) advanced through flexible scope. Settings: 40 watts, Argon flow 1.5 L/min, Pulsed mode.
Treatment: Circumferential APC application to all visible tumor tissue in right mainstem bronchus. Particular attention to areas of residual bleeding.
Duration: 6 minutes active APC time
Result: Excellent hemostasis achieved, visible coagulation effect on tumor surface
Assessment after debridement:
Right mainstem bronchus now approximately 50% patent (improved from <10% pre-treatment). However, significant residual tumor bulk and malacia noted.
Balloon Dilation:
Boston Scientific CRE balloon catheter (12mm x 4cm) advanced over guidewire to stenotic segment under fluoroscopic guidance.
Inflation sequence:

First inflation: 12mm diameter x 60 seconds
Second inflation: 12mm diameter x 60 seconds
Third inflation: 14mm diameter x 90 seconds (maximum size)

Fluoroscopy showed excellent balloon expansion across entire stenotic segment. Upon deflation, improved luminal diameter appreciated.
Post-dilation assessment: Right mainstem bronchus now approximately 60-65% patent. However, given residual tumor bulk, malacia, and risk of rapid re-obstruction, decision made to place stent.
Stent Placement:
After discussion with anesthesia regarding patient stability (patient remained stable throughout), proceeded with metallic stent placement.
Stent selected: Boston Scientific Ultraflex covered metallic stent, 14mm diameter x 60mm length
Deployment technique:

Stent advanced over guidewire under combined bronchoscopic and fluoroscopic guidance
Positioned to span from 0.5cm distal to carina to mid-right mainstem bronchus
Fluoroscopic confirmation of position in AP and lateral views
Slow, controlled deployment under direct visualization
Post-deployment balloon dilation of stent (12mm balloon) to ensure full stent expansion

Post-stent assessment:
Flexible bronchoscope passed through rigid scope and into stent lumen.
Findings:

Stent well-positioned, no migration
Excellent apposition to airway walls
RUL orifice: Fully visible through stent side mesh, patent
RML orifice: Visible and patent
RLL orifice: Visible and patent
All segments of right lung now visualized for first time
Significant amount of retained secretions in distal airways (expected due to chronic obstruction)

Therapeutic Aspiration:
Extensive suctioning and aspiration performed in all segments of right lung. Thick, purulent-appearing secretions removed from:

Right upper lobe: Approximately 30mL
Right middle lobe: Approximately 20mL
Right lower lobe: Approximately 40mL

Total secretions removed: ~90mL. Samples sent for culture.
Final Airway Inspection:

Trachea: Normal
Left bronchial tree: Unchanged, patent
Right main stem: Patent through stent, estimated 85-90% luminal patency (compared to pre-procedure ~10%)
RUL, RML, RLL: All now patent with significant improvement in ventilation
Minimal residual bleeding, hemostasis excellent

Rigid bronchoscope removed. Patient re-intubated with 8.0mm ETT. Confirmation of ETT position with bronchoscopy and capnography. Bilateral breath sounds now audible (marked improvement in right-sided ventilation compared to pre-procedure).
Airway Intervention Completed: 10:15 AM
Estimated blood loss during airway phase: 200mL
Specimens obtained: Tumor tissue (pathology), secretions (microbiology)

PART 2: PERICARDIAL WINDOW (10:30 - 11:15)
Patient [REDACTED] arms tucked. Subxiphoid area prepped and draped in sterile fashion by cardiothoracic surgery team. Interventional pulmonology team assisted.
TEE probe inserted by anesthesia showed moderate-large circumferential pericardial effusion with RV diastolic collapse.
Surgical technique (performed by CT surgery, Dr. Harrison):

Subxiphoid incision, approximately 4cm
Dissection carried down to pericardium
Pericardium opened, approximately 4cm x 3cm window created
Rush of 400mL of serosanguineous fluid
Pericardial biopsy obtained (sent for pathology and cytology)
No active bleeding from pericardial surface
19Fr Blake drain left in pericardial space
Drain secured to skin, connected to bulb suction

TEE post-drainage: Complete resolution of pericardial effusion, no RV collapse, improved cardiac output.

PART 3: PLEURAL CATHETER PLACEMENT (11:20 - 11:45)
With patient still under general anesthesia, attention turned to right pleural effusion.
Ultrasound examination (performed by IP team):

Right hemithorax with moderate-large pleural effusion
Estimated volume: 1000-1200mL
Anechoic fluid, no loculations
Compressed right lung (though now ventilating via stent)

PleurX catheter placement:
Standard tunneled technique as previously described. Entry site: [REDACTED]
Initial drainage: 850mL of serosanguineous fluid removed (stopped at patient request earlier - she was waking up and uncomfortable).
Chest tube secured with 2-0 nylon sutures. Occlusive dressing applied.

PROCEDURE CONCLUSION
All procedures completed successfully. Total operative time: 4 hours 15 minutes.
Patient [REDACTED] Conclusion:

Hemodynamically stable (MAP 78, HR 82)
Improved oxygen saturation: 96% on FiO2 0.5 (compared to pre-procedure 88% on FiO2 1.0)
TEE shows improved cardiac function
Bilateral breath sounds now audible

Patient [REDACTED] for transport to ICU given length of procedure and concern for post-obstructive pulmonary edema.
Specimens Sent:

Endobronchial tumor (histology)
Bronchial secretions (bacterial, fungal, AFB cultures)
Pericardial tissue (histology, cytology)
Pericardial fluid (cytology, chemistry)
Pleural fluid (cytology, chemistry, cell count)

Estimated Total Blood Loss: 250mL
Fluids Given: 2000mL crystalloid
UOP: 400mL
Complications: None intraoperatively

POSTOPERATIVE DISPOSITION & PLAN
Immediate (ICU):

Extubate when fully awake and following commands (anticipated within 2-4 hours)
Chest X-ray immediately post-procedure and daily x3 days
Monitor pericardial drain output
Pleural catheter to drain q3 days initially
Continue broad-spectrum antibiotics (started on Pip-Tazo for post-obstructive pneumonia)
DVT prophylaxis with heparin SQ
PPI for stress ulcer prophylaxis
Aggressive pulmonary toilet and incentive spirometry

Short-term (Inpatient, 3-5 days):

Remove pericardial drain when output <50mL/day
Transition to floor when stable
Continue PleurX catheter drainage
Pain control
Physical therapy for reconditioning

Medium-term (1-2 weeks):

Discharge with home health for PleurX catheter management
Follow-up in IP clinic at 2 weeks with chest X-ray
Discuss with oncology regarding re-initiation of systemic therapy now that dyspnea improved

Long-term:

Surveillance bronchoscopy at 6-8 weeks to assess stent
Monitor for stent-related complications (migration, granulation, tumor in-growth)
May need stent revision/exchange
PleurX catheter to remain until auto-pleurodesis occurs or end of life


ASSESSMENT & PROGNOSIS
[REDACTED] critical, multi-system involvement of metastatic lung cancer causing:

Near-complete right mainstem bronchus obstruction → Successfully addressed with tumor debridement and stent
Cardiac tamponade physiology → Successfully addressed with pericardial window
Large pleural effusion → Successfully palliated with PleurX catheter

All procedures were technically successful without intra-operative complications. The patient now has:

Restored right lung ventilation (dramatic improvement from pre-procedure state)
Resolution of cardiac compromise
Control of pleural effusion

Prognosis: Given stage IV disease, prognosis remains guarded with likely survival measured in months. However, these palliative interventions should significantly improve quality of life by reducing dyspnea and allowing potential resumption of systemic therapy.
The patient and family understand this is palliative care aimed at symptom control rather than cure. They expressed gratitude for the interventions and understanding of the goals of care.

ATTENDING PHYSICIAN STATEMENT
I, David Kim, MD, was present and actively participating throughout the entire procedure. I performed the critical portions of the airway intervention including tumor debridement, cautery, stent placement, and final bronchoscopic assessment. I supervised Dr. Foster throughout the pleural catheter placement. I assisted the cardiothoracic surgery team during pericardial window creation.
The procedure was medically necessary, technically indicated, and appropriately performed. Informed consent was obtained. The patient tolerated the procedure without immediate complications.
Electronically Signed: David Kim, MD - [REDACTED] 13:05
BRONCHOSCOPY [REDACTED]
Jackson Mary 82F #2145069
Indication pneumonia not improving on abx, r/o endobronchial lesion
Moderate sedation versed 2mg fent 75mcg
Scope thru nose, lidocaine spray used
Findings:
Nose/pharynx ok
Cords move normal
Trachea normal
R side all patent no lesions
L side all patent no lesions
Diffuse thick yellow secretions throughout both lungs
BAL done LLL 100cc in 80cc out
Sputum cultures sent
No lesions seen
Post bronch CXR no PTX
Impression: No endobronchial cause for pneumonia, likely bacterial pneumonitis, cultures pending
Plan: Continue abx, f/u cultures, repeat CXR 48h
Dr. Smith"""

entities_10 = [
    {"label": "MEDICATION", **get_span(text_10, "Cefazolin", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Dexamethasone", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Flexible Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Supraglottic structures", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Vocal cords", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Subglottis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "erythema", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left main bronchus", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right main bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "tumor debridement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "mechanical debridement", 1)},
    {"label": "MEDICATION", **get_span(text_10, "epinephrine", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Tranexamic acid", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "30 minutes", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Electrocautery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Flexible bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "cauterized", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_10, "40 watts", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "8 minutes", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "APC", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_10, "40 watts", 2)},
    {"label": "MEAS_TIME", **get_span(text_10, "6 minutes", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Balloon Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "12mm", 3)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "covered metallic stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_10, "14mm diameter x 60mm length", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Aspiration", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right middle lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right lower lobe", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "30mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "20mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "40mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "90mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "Tumor tissue", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "pericardial effusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "400mL", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Blake drain", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "19Fr", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "1000-1200mL", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "PleurX catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "850mL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pneumonia", 2)},
    {"label": "MEDICATION", **get_span(text_10, "versed", 1)},
    {"label": "MEDICATION", **get_span(text_10, "fent", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 5)},
    {"label": "PROC_ACTION", **get_span(text_10, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "100cc", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "80cc", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Sputum", 1)},
]
BATCH_DATA.append({"id": "2145069", "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)