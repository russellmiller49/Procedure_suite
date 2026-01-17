import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
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
# 3. Data Definitions (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 12245954_syn_1
# ------------------------------------------
t1 = """Indication: Esophageal stent migrated into airway. TE Fistula.
Proc: Rigid Bronch, FB Removal, Y-Stent.
Action: Remnant esophageal stent removed piecemeal (31635). Large TEF exposed. Hybrid Y-stent placed (31631) to cover defect.
Plan: ICU, nebulizers."""

e1 = [
    {"label": "DEV_STENT", **get_span(t1, "Esophageal stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "airway", 1)},
    {"label": "OBS_LESION", **get_span(t1, "TE Fistula", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "FB Removal", 1)},
    {"label": "DEV_STENT", **get_span(t1, "Y-Stent", 1)},
    {"label": "DEV_STENT", **get_span(t1, "esophageal stent", 1)}, # Fixed: occurrence 2 -> 1 (lowercase appears once)
    {"label": "PROC_ACTION", **get_span(t1, "removed", 1)},
    {"label": "OBS_LESION", **get_span(t1, "TEF", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t1, "Hybrid", 1)},
    {"label": "DEV_STENT", **get_span(t1, "Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "placed", 1)},
]
BATCH_DATA.append({"id": "12245954_syn_1", "text": t1, "entities": e1})

# ------------------------------------------
# Case 2: 12245954_syn_2
# ------------------------------------------
t2 = """OPERATIVE REPORT: Rigid Bronchoscopy with Esophageal Stent Extraction and Airway Stenting.
The patient presented with a migrated esophageal stent occluding the left mainstem. Using rigid bronchoscopic techniques and endoscopic scissors, the stent was extracted piecemeal from the trachea. This revealed a significant tracheoesophageal fistula involving the carina. To restore airway patency and seal the fistula, a dynamic Hybrid Y-stent was deployed. The limbs were seated in the mainstems and the tracheal limb secured."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Rigid Bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t2, "Esophageal Stent", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Extraction", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Airway Stenting", 1)},
    {"label": "DEV_STENT", **get_span(t2, "esophageal stent", 1)}, # Fixed: occurrence 2 -> 1 (lowercase appears once)
    {"label": "ANAT_AIRWAY", **get_span(t2, "left mainstem", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rigid bronchoscopic techniques", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "endoscopic scissors", 1)},
    {"label": "DEV_STENT", **get_span(t2, "stent", 3)},
    {"label": "PROC_ACTION", **get_span(t2, "extracted", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "trachea", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tracheoesophageal fistula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "carina", 1)},
    {"label": "OBS_LESION", **get_span(t2, "fistula", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "Hybrid", 1)},
    {"label": "DEV_STENT", **get_span(t2, "Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "mainstems", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "tracheal limb", 1)},
]
BATCH_DATA.append({"id": "12245954_syn_2", "text": t2, "entities": e2})

# ------------------------------------------
# Case 3: 12245954_syn_3
# ------------------------------------------
t3 = """Coding Summary:
- 31635: Removal of foreign body (Migrated esophageal stent fragments removed piecemeal).
- 31631: Placement of tracheal stent (Y-stent placed covering trachea and mainstems).
Medical Necessity: Critical airway obstruction and TE fistula."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Removal of foreign body", 1)},
    {"label": "DEV_STENT", **get_span(t3, "esophageal stent", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "removed", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Placement of tracheal stent", 1)},
    {"label": "DEV_STENT", **get_span(t3, "Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "placed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "mainstems", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "airway obstruction", 1)},
    {"label": "OBS_LESION", **get_span(t3, "TE fistula", 1)},
]
BATCH_DATA.append({"id": "12245954_syn_3", "text": t3, "entities": e3})

# ------------------------------------------
# Case 4: 12245954_syn_4
# ------------------------------------------
t4 = """Procedure: Rigid Bronch Stent Removal/Placement
Pt: [REDACTED]
Steps:
1. Rigid scope inserted.
2. Saw esophageal stent in airway.
3. Cut it out piece by piece (FB removal).
4. Saw huge fistula.
5. Placed Y-stent to cover the hole.
6. Intubated through stent.
Plan: ICU."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Stent Removal", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Placement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid scope", 1)},
    {"label": "DEV_STENT", **get_span(t4, "esophageal stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "airway", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Cut", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "FB removal", 1)},
    {"label": "OBS_LESION", **get_span(t4, "fistula", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Placed", 1)},
    {"label": "DEV_STENT", **get_span(t4, "Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Intubated", 1)},
    {"label": "DEV_STENT", **get_span(t4, "stent", 3)},
]
BATCH_DATA.append({"id": "12245954_syn_4", "text": t4, "entities": e4})

# ------------------------------------------
# Case 5: 12245954_syn_5
# ------------------------------------------
t5 = """op note for jessica mcbee... airway emergency esophageal stent came through the trachea... used the rigid scope to pull the stent out had to cut it into pieces very difficult... huge hole te fistula found... placed a hybrid y stent to cover it up took a few tries but got it seated... intubated through the stent patient stable for now."""

e5 = [
    {"label": "ANAT_AIRWAY", **get_span(t5, "airway", 1)},
    {"label": "DEV_STENT", **get_span(t5, "esophageal stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "pull", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 2)},
    {"label": "PROC_ACTION", **get_span(t5, "cut", 1)},
    {"label": "OBS_LESION", **get_span(t5, "te fistula", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "placed", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t5, "hybrid", 1)},
    {"label": "DEV_STENT", **get_span(t5, "y stent", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "intubated", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 4)},
]
BATCH_DATA.append({"id": "12245954_syn_5", "text": t5, "entities": e5})

# ------------------------------------------
# Case 6: 12245954_syn_6
# ------------------------------------------
t6 = """Rigid bronchoscopy with esophageal stent removal. Dynamic Y (hybrid) Tracheal stent placement. Bronchoscopic intubation. 14mm ventilating rigid bronchoscope was inserted. The stents traversed into the left mainstem causing complete occlusion. Using multiple techniques to include rigid endoscopic scissors, APC, and forceps we slowly removed exposed wires and attempted to transect the stent. The majority of the stents had to be removed in a piecemeal fashion. Large defect at the main carina extending directly into the esophagus. Placed a 13X10X10 mm dynamic Y stent."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t6, "esophageal stent", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "removal", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t6, "hybrid", 1)},
    {"label": "DEV_STENT", **get_span(t6, "Tracheal stent", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "placement", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Bronchoscopic intubation", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid bronchoscope", 1)},
    {"label": "DEV_STENT", **get_span(t6, "stents", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "left mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "occlusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid endoscopic scissors", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "removed", 1)},
    {"label": "DEV_STENT", **get_span(t6, "stent", 3)},
    {"label": "DEV_STENT", **get_span(t6, "stents", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "removed", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "main carina", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Placed", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t6, "13X10X10 mm", 1)},
    {"label": "DEV_STENT", **get_span(t6, "dynamic Y stent", 1)},
]
BATCH_DATA.append({"id": "12245954_syn_6", "text": t6, "entities": e6})

# ------------------------------------------
# Case 7: 12245954_syn_7
# ------------------------------------------
t7 = """[Indication]
Airway obstruction from migrated esophageal stent.
[Anesthesia]
General.
[Description]
Rigid bronchoscopy performed. Esophageal stent fragments removed piecemeal from airway. TE fistula id[REDACTED]. Dynamic Y-stent deployed to cover fistula and maintain patency.
[Plan]
ICU, humidity, check CXR."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "Airway obstruction", 1)},
    {"label": "DEV_STENT", **get_span(t7, "esophageal stent", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t7, "Esophageal stent", 1)}, # Fixed: occurrence 2 -> 1 (Capitalized appears once)
    {"label": "PROC_ACTION", **get_span(t7, "removed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "airway", 2)},
    {"label": "OBS_LESION", **get_span(t7, "TE fistula", 1)},
    {"label": "DEV_STENT", **get_span(t7, "Dynamic Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "deployed", 1)},
    {"label": "OBS_LESION", **get_span(t7, "fistula", 2)},
]
BATCH_DATA.append({"id": "12245954_syn_7", "text": t7, "entities": e7})

# ------------------------------------------
# Case 8: 12245954_syn_8
# ------------------------------------------
t8 = """Jessica required emergency rigid bronchoscopy because her esophageal stent had eroded into her airway, blocking her left lung. We carefully removed the metal stent pieces from her windpipe using heavy scissors and forceps. Once removed, we saw a large hole (fistula) between the airway and esophagus. We placed a silicone Y-shaped stent to cover this hole and keep her breathing passages open."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t8, "esophageal stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "left lung", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "removed", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t8, "metal", 1)},
    {"label": "DEV_STENT", **get_span(t8, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "windpipe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "scissors", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "removed", 2)},
    {"label": "OBS_LESION", **get_span(t8, "fistula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 2)},
    {"label": "PROC_ACTION", **get_span(t8, "placed", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t8, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t8, "Y-shaped stent", 1)},
]
BATCH_DATA.append({"id": "12245954_syn_8", "text": t8, "entities": e8})

# ------------------------------------------
# Case 9: 12245954_syn_9
# ------------------------------------------
t9 = """Procedure: Rigid bronchoscopic foreign body extraction and airway stenting.
Action: Retrieved migrated prosthetic material from the tracheobronchial tree. Deployed a bifurcated silicone stent (Y-stent) to bridge the resultant tracheoesophageal defect.
Result: Airway patency restored."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Rigid bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "foreign body extraction", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "airway stenting", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Retrieved", 1)},
    {"label": "DEV_STENT", **get_span(t9, "prosthetic material", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "tracheobronchial tree", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Deployed", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t9, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t9, "stent", 1)},
    {"label": "DEV_STENT", **get_span(t9, "Y-stent", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tracheoesophageal defect", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "Airway patency restored", 1)},
]
BATCH_DATA.append({"id": "12245954_syn_9", "text": t9, "entities": e9})

# ------------------------------------------
# Case 10: 12245954 (Full Report)
# ------------------------------------------
t10 = """DATE OF PROCEDURE: [REDACTED]
NAME: [REDACTED]RN: [REDACTED]

PREOPERATIVE DIAGNOSIS: 
1.        Esophageal stent migration through distal trachea and left mainstem
2.         Left mainstem occlusion secondary to  esophageal stent
POSTOPERATIVE DIAGNOSIS: 
1.        Tracheoesophageal fistula status post tracheal Y-stent placement
PROCEDURE PERFORMED: 
1.        Rigid bronchoscopy with esophageal stent removal 
2.        Dynamic Y ( hybrid) Tracheal stent placement
3.        Bronchoscopic intubation
SURGEON: Jordan Parks MD
INDICATIONS: left mainstem obstruction secondary to esophageal stent migration
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives. The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room. After administration of sedatives an LMA was inserted and the T190 therapeutic flexible bronchoscope was passed through the vocal cords and into the trachea. Approximately 2 cm proximal to the main carina an esophageal stent was visualized protruding into the airway causing approximately 30% obstruction of the distal trachea. On closer inspection we could visualize both of the patients telescoping esophageal stent. The proximal end of the inner covered stent could be seen with the origin of the lumen approximately 50% into the airway. The outer uncovered stents proximal origin was seen about 5mm into the distal left mainstem. Additionally a large clip attached to the uncovered outer stent could be seen within the airway. The stents traversed into the left mainstem causing complete occlusion which we could not bypass with the flexible bronchoscope. Bronchial lavage was performed to collect purulent secretions from the airway. The flexible bronchoscope and LMA were then removed and a 14mm ventilating rigid bronchoscope was subsequently inserted into the mid trachea and connected to ventilator. Using flexible forceps we were able to detach and remove the clip. We were aware that the outer uncovered stent was embedded into the trachea and could not be removed. However, given that the inner stents proximal lumen was within the airway and that this stent was not known to be fixed to tissue we chose to attempt the remove the stent enblock through the airway. Using the rigid forceps the proximal edge of the stent was grasped and slowly withdrawn. Initially the stent moved easily however after retracting approximately 3cm of the stent sudden resistance was encountered and the proximal edge of the stent fractured. Given that a much longer segment of the stent was now within the trachea causing significant obstruction (which also now made placement of a tracheal stent impossible) we had no choice except to attempt to further extract the stent. The stent however was firmly fixed and retraction resulted in further fracture with multiple exposed sires within the trachea. Advanced GI endoscopy was called and came to the OR. The rigid bronchoscope was removed and an EGD was performed. The proximal edge of the outer uncovered stent  from the esophageal side was embedded and distorted and could not be passed even with the Ultra slim (6mm) gastroscope.  The rigid bronchoscope was reinserted during EGD to better allow us to visualize the communication and attempt to pass a wire in into the esophagus to place an additional stent but the wire would only pass into the airway and this was subsequently aborted leaving us no choice but to continue to remove the esophageal stent piecemeal. Using multiple techniques to include rigid endoscopic scissors, APC, and forceps we slowly removed exposed wires and attempted to transect the stent to allow airway stent placement. This was extremely difficult as more and more unraveling stent was seen. As both stents migrated further into the airway while extracting exposed wires the majority of the stents had to be removed in a piecemeal fashion. Once the stents were removed, with the exception of some small distal wires, the extent of the fistula (which extended during extraction) became completely apparent with the posterior wall of the trachea essentially absent in the lower third with a large defect at the main carina extending directly into the esophagus. We then attempted to place a 15x12x12 hybrid dynamic Y stent into the airway to occlude the fistula by removing the rigid bronchoscope and using glide-scope laryngoscopy visualizing the vocal cords and directly passing the stent, secured with Freitag forceps, into the trachea. Once the stent was within the airway we inserted a  rigid non-ventilating tracheoscope through the vocal cords proximal to the stent. Due to the large defect at the main carina it was extremely difficult to seat the limbs within the bilateral mainstem and despite multiple attempts utilizing rigid forceps, reverse forceps CRE balloons and manipulation with the tip of the flexible bronchoscope we could not adequately seat the stent. The stent was removed and we then attempted to place a smaller 13X10X10 mm dynamic Y with a 5.5cm tracheal limb, a 2cm right sided limb and a 3cm left sided limb using a similar technique and were eventually able to secure the stent in place. Once this was accomplished a 6.5 ETT was inserted into the airway over a bronchoscope and advanced into the proximal limb of the stent and secured in place.   
Complications:  Extension of TE fistula 
Recommendations:
-        Patient to remain on positive pressure ventilation tonight.
-        Please obtain CXR once patient arrives in ICU
-        Please obtain CT chest prior to extubation if possible 
-        Appreciate GI recommendations. 
-        Please contact the interventional pulmonary team if any airway issues occur in this patient. Anesthesia is also aware
-        Patient will require 3 times a day 3% saline nebulizers starting tonight and as long as the patient’s airway stent is in place for mucolytic effect and hydration to prevent stent plugging.
-        If tracheostomy tube needs to be removed and reinserted this must be performed  with direct visualization of the distal tip as it is inserted into the lumen of the tracheostomy tube to prevent kinking or obstruction of the stent by  the tracheostomy tube.
-        Please do not adjust the endotracheal tubes position or attempt suction unless absolutely necessary (tonight).
-        Extubation must be performed with flexible bronchoscope to allow visualization of the stent and using flexible forceps to apply downward pressure on the main carina while retracting the ETT to avoid dislodging of the stent.
-        If invasive ventilatory support is required after ETT removal blind intubation (direct laryngoscopy, glidescope) should be avoided as it can result in dislodgment of the tracheal stent and potential catastrophic airway obstruction.  Intubation should be performed with a 6.5 or smaller ETT with bronchoscopic insertion to visualize the distal tip of the endotracheal tube. The endotracheal tube should be advanced into the tracheal limb of the stent and secured.        
Jordan Parks, MD 
Interventional Pulmonology 
UCLA Medical Center"""

e10 = [
    {"label": "DEV_STENT", **get_span(t10, "Esophageal stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "distal trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "left mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "occlusion", 1)},
    {"label": "DEV_STENT", **get_span(t10, "esophageal stent", 1)}, # Fixed: occurrence 2 -> 1 (First lowercase)
    {"label": "OBS_LESION", **get_span(t10, "Tracheoesophageal fistula", 1)},
    {"label": "DEV_STENT", **get_span(t10, "tracheal Y-stent", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t10, "esophageal stent", 2)}, # Fixed: occurrence 3 -> 2
    {"label": "PROC_ACTION", **get_span(t10, "removal", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "hybrid", 1)},
    {"label": "DEV_STENT", **get_span(t10, "Tracheal stent", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoscopic intubation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "left mainstem", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "obstruction", 1)},
    {"label": "DEV_STENT", **get_span(t10, "esophageal stent", 3)}, # Fixed: occurrence 4 -> 3
    {"label": "DEV_INSTRUMENT", **get_span(t10, "T190 therapeutic flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "DEV_STENT", **get_span(t10, "esophageal stent", 4)}, # Fixed: occurrence 5 -> 4
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "30% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "distal trachea", 2)},
    {"label": "DEV_STENT", **get_span(t10, "esophageal stent", 5)}, # Fixed: occurrence 6 -> 5
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "covered", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 6)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "uncovered", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "distal left mainstem", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "uncovered", 2)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 8)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stents", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "left mainstem", 4)},
    {"label": "OBS_FINDING", **get_span(t10, "occlusion", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible bronchoscope", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchial lavage", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "purulent secretions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 4)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible bronchoscope", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "removed", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "ventilating rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "mid trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "remove", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "uncovered", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 9)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 4)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 10)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 5)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 11)},
    {"label": "PROC_ACTION", **get_span(t10, "remove", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 12)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 6)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid forceps", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 13)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 14)},
    {"label": "MEAS_SIZE", **get_span(t10, "3cm", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 15)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 16)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 17)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 5)},
    {"label": "DEV_STENT", **get_span(t10, "tracheal stent", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "extract", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 19)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 20)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 6)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid bronchoscope", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "removed", 3)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "uncovered", 4)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 21)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid bronchoscope", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 22)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 7)},
    {"label": "PROC_ACTION", **get_span(t10, "remove", 4)},
    {"label": "DEV_STENT", **get_span(t10, "esophageal stent", 6)}, # Fixed: occurrence 7 -> 6
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid endoscopic scissors", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 23)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 24)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 25)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 9)},
    {"label": "DEV_STENT", **get_span(t10, "stents", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "removed", 4)},
    {"label": "DEV_STENT", **get_span(t10, "stents", 4)},
    {"label": "PROC_ACTION", **get_span(t10, "removed", 5)},
    {"label": "OBS_LESION", **get_span(t10, "fistula", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 7)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "place", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(t10, "15x12x12", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "hybrid", 2)},
    {"label": "DEV_STENT", **get_span(t10, "dynamic Y stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 10)},
    {"label": "OBS_LESION", **get_span(t10, "fistula", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "removing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid bronchoscope", 4)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 27)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Freitag forceps", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 8)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 28)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 11)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid non-ventilating tracheoscope", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 29)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 3)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "bilateral mainstem", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid forceps", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "CRE balloons", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible bronchoscope", 4)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 30)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 31)},
    {"label": "PROC_ACTION", **get_span(t10, "removed", 6)},
    {"label": "PROC_ACTION", **get_span(t10, "place", 3)},
    {"label": "DEV_STENT_SIZE", **get_span(t10, "13X10X10 mm", 1)},
    {"label": "DEV_STENT", **get_span(t10, "dynamic Y", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "5.5cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "tracheal limb", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2cm", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "3cm", 2)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 32)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 12)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "bronchoscope", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 33)},
    {"label": "OBS_LESION", **get_span(t10, "TE fistula", 2)},
]
BATCH_DATA.append({"id": "12245954", "text": t10, "entities": e10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)