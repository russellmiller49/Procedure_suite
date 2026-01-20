import sys
from pathlib import Path

# ==========================================
# Setup: Repo Root & Imports
# ==========================================
try:
    # Adjust this path logic to match your actual repo structure
    # Assuming this script sits in specific folder depth, e.g., root/scripts/processing/
    REPO_ROOT = Path(__file__).resolve().parents[2] 
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for standard structure
    REPO_ROOT = Path(__file__).resolve().parent.parent
    sys.path.append(str(REPO_ROOT))
    try:
        from scripts.add_training_case import add_case
    except ImportError:
        print("Warning: Could not import 'add_case'. Ensure you are in the correct repo.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in the provided text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4726193_syn_1
# ==========================================
id_1 = "4726193_syn_1"
text_1 = """Procedure: Robotic Bronchoscopy (Ion).
Target: RUL nodule (2.8cm).
Nav: Ion system. Auto registration.
Confirmation: Radial EBUS (concentric), Cone Beam CT.
Sampling: Brush, Forceps, Needle.
Comp: None."""
entities_1 = [
    {"label": "PROC_METHOD",       **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION",        **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "2.8cm", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Ion system", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Cone Beam CT", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "Brush", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "Forceps", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_1, "Needle", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4726193_syn_2
# ==========================================
id_2 = "4726193_syn_2"
text_2 = """PROCEDURE NOTE: Robotic-assisted bronchoscopy.
INDICATION: RUL pulmonary nodule (2.8cm), intermediate malignancy risk.
DETAILS: The Intuitive Ion system was utilized. Registration was excellent. The catheter was navigated to the RUL posterior segment target. Radial EBUS confirmed a concentric lesion. Intraprocedural Cone Beam CT (CBCT) verified tool-in-lesion accuracy. Biopsies were taken using brush, forceps, and needle. Samples sent for pathology."""
entities_2 = [
    {"label": "PROC_METHOD",       **get_span(text_2, "Robotic-assisted bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_2, "RUL", 1)},
    {"label": "OBS_LESION",        **get_span(text_2, "pulmonary nodule", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_2, "2.8cm", 1)},
    {"label": "PROC_METHOD",       **get_span(text_2, "Ion system", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_2, "RUL posterior segment", 1)},
    {"label": "PROC_METHOD",       **get_span(text_2, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_2, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION",       **get_span(text_2, "Biopsies", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_2, "brush", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_2, "forceps", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_2, "needle", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4726193_syn_3
# ==========================================
id_3 = "4726193_syn_3"
text_3 = """Billing Codes:
- 31627 (Navigational Bronchoscopy): Ion robotic system used.
- 31654 (Radial EBUS): Confirmation of lesion position.
- 31629/31628: Transbronchial needle aspiration and forceps biopsies performed.
Notes: Cone Beam CT used for verification."""
entities_3 = [
    {"label": "PROC_METHOD",       **get_span(text_3, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD",       **get_span(text_3, "Ion robotic system", 1)},
    {"label": "PROC_METHOD",       **get_span(text_3, "Radial EBUS", 1)},
    {"label": "PROC_ACTION",       **get_span(text_3, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_3, "forceps", 1)},
    {"label": "PROC_ACTION",       **get_span(text_3, "biopsies", 1)},
    {"label": "PROC_METHOD",       **get_span(text_3, "Cone Beam CT", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4726193_syn_4
# ==========================================
id_4 = "4726193_syn_4"
text_4 = """Procedure: Robotic Bronch (Ion)
Pt: [REDACTED]
Attending: Dr. Patel

1. GA/ETT.
2. Ion registration.
3. Nav to RUL.
4. REBUS check: Concentric.
5. CBCT spin: Good position.
6. Biopsy x many.
7. Extubated."""
entities_4 = [
    {"label": "PROC_METHOD",       **get_span(text_4, "Robotic Bronch", 1)},
    {"label": "PROC_METHOD",       **get_span(text_4, "Ion", 1)},
    {"label": "PROC_METHOD",       **get_span(text_4, "Ion", 2)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_4, "RUL", 1)},
    {"label": "PROC_METHOD",       **get_span(text_4, "REBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_4, "CBCT", 1)},
    {"label": "PROC_ACTION",       **get_span(text_4, "Biopsy", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4726193_syn_5
# ==========================================
id_5 = "4726193_syn_5"
text_5 = """gerald thompson robotic bronch case. dr patel attending. used the ion robot. went to the rul nodule. radial ebus showed it good. did a spin with the c-arm to double check. needle brush forceps everything. samples sent. no pneumo on the scan. done."""
entities_5 = [
    {"label": "PROC_METHOD",       **get_span(text_5, "robotic bronch", 1)},
    {"label": "PROC_METHOD",       **get_span(text_5, "ion robot", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_5, "rul", 1)},
    {"label": "OBS_LESION",        **get_span(text_5, "nodule", 1)},
    {"label": "PROC_METHOD",       **get_span(text_5, "radial ebus", 1)},
    {"label": "PROC_METHOD",       **get_span(text_5, "c-arm", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_5, "needle", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_5, "brush", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_5, "forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no pneumo", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4726193_syn_6
# ==========================================
id_6 = "4726193_syn_6"
text_6 = """Robotic-assisted bronchoscopy (Ion) performed for 2.8cm RUL nodule. Navigation to posterior segment successful. Confirmation via Radial EBUS (concentric) and Cone Beam CT. Extensive sampling performed with needle, brush, and forceps. No complications. Estimated blood loss <5mL."""
entities_6 = [
    {"label": "PROC_METHOD",       **get_span(text_6, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD",       **get_span(text_6, "Ion", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_6, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_6, "RUL", 1)},
    {"label": "OBS_LESION",        **get_span(text_6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_6, "posterior segment", 1)},
    {"label": "PROC_METHOD",       **get_span(text_6, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_6, "Cone Beam CT", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_6, "needle", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_6, "brush", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_6, "forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4726193_syn_7
# ==========================================
id_7 = "4726193_syn_7"
text_7 = """[Indication]
2.8cm RUL nodule.
[Anesthesia]
General, 8.0 ETT.
[Description]
Ion Robotic Navigation. Radial EBUS confirmation. Cone Beam CT verification. TBNA/Forceps/Brush biopsies.
[Plan]
Pathology results pending."""
entities_7 = [
    {"label": "MEAS_SIZE",         **get_span(text_7, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_7, "RUL", 1)},
    {"label": "OBS_LESION",        **get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD",       **get_span(text_7, "Ion Robotic Navigation", 1)},
    {"label": "PROC_METHOD",       **get_span(text_7, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_7, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION",       **get_span(text_7, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_7, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_7, "Brush", 1)},
    {"label": "PROC_ACTION",       **get_span(text_7, "biopsies", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4726193_syn_8
# ==========================================
id_8 = "4726193_syn_8"
text_8 = """[REDACTED] a robotic bronchoscopy today for his lung nodule. We used the Ion robot to navigate deep into his right upper lung. We confirmed we were at the right spot using both a mini-ultrasound probe and a 3D CT scan right in the operating room. We took multiple samples using needles and forceps. The procedure went smoothly with no issues."""
entities_8 = [
    {"label": "PROC_METHOD",       **get_span(text_8, "robotic bronchoscopy", 1)},
    {"label": "OBS_LESION",        **get_span(text_8, "lung nodule", 1)},
    {"label": "PROC_METHOD",       **get_span(text_8, "Ion robot", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_8, "right upper lung", 1)},
    {"label": "PROC_METHOD",       **get_span(text_8, "mini-ultrasound probe", 1)},
    {"label": "PROC_METHOD",       **get_span(text_8, "3D CT scan", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_8, "needles", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_8, "forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "no issues", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4726193_syn_9
# ==========================================
id_9 = "4726193_syn_9"
text_9 = """Procedure: Robotic-guided endoscopy (31627), Sonographic confirmation (31654), Tissue sampling (31628/31629).
Target: RUL mass.
Action: Robotic navigation. Multi-modal sampling.
Verification: Cone Beam CT."""
entities_9 = [
    {"label": "PROC_METHOD",       **get_span(text_9, "Robotic-guided endoscopy", 1)},
    {"label": "PROC_METHOD",       **get_span(text_9, "Sonographic confirmation", 1)},
    {"label": "PROC_ACTION",       **get_span(text_9, "Tissue sampling", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_9, "RUL", 1)},
    {"label": "OBS_LESION",        **get_span(text_9, "mass", 1)},
    {"label": "PROC_METHOD",       **get_span(text_9, "Robotic navigation", 1)},
    {"label": "PROC_METHOD",       **get_span(text_9, "Cone Beam CT", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4726193 (Original)
# ==========================================
id_10 = "4726193"
text_10 = """Patient Name: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]

Preoperative Diagnosis: Endotracheal tumor
Postoperative Diagnosis: Endotracheal tumor s/p debulking
Procedure Performed: Rigid bronchoscopy with endoluminal tumor ablation (CPT 31641)

Surgeon: Patricia Lee, MD
Assistant: Marcus Johnson, MD
Indications: Tracheal obstruction
Sedation: General Anesthesia

Description of Procedure:
The procedure was performed in the main operating room. After administration of sedatives and paralytics, the flexible bronchoscope was inserted through the LMA and into the pharynx. We then advanced the bronchoscope into the subglottic space. Approximately 2.5 cm distal to the vocal cords, there were 3 polypoid lesions at the same level blocking about 90% of the airway during exhalation which moved in a ball valve fashion with inhalation, resulting in about 50% obstruction of the airway. Additionally, there were multiple small polypoid (>50) lesions surrounding and distal to the lesion originating from all parts of the airway (anterior trachea, posterior trachea, lateral trachea) which terminated about 1 cm proximal to the main carina. The right-sided and left-sided airways to at least the first sub-segments were uninvolved with no evidence of endobronchial tumor or extrinsic obstruction.

The flexible bronchoscope and LMA were removed and a 10 mm non-ventilating rigid tracheoscope was subsequently inserted into the proximal trachea just proximal to the tumor and connected to ventilator. The T190 Olympus flexible bronchoscope was then introduced through the rigid bronchoscope and the electrocautery snare was used to transect the large polypoid lesions beginning with the 3 proximal obstructive lesions. The lesions, once free from the wall, were easily removed from the airway with suction and collected for pathological assessment. After these lesions were removed, about 10 other lesions in the airway which were anatomically amenable to snare were removed in the same fashion. We then used APC to paint and shave the remaining tumor area on the posterior and lateral trachea walls until we were satisfied that we had achieved adequate luminal recanalization. At the end of the procedure, the trachea was approximately 90% open in comparison to unaffected areas. The rigid bronchoscope was then removed, and the procedure was completed. There were no complications.

Of note, we considered airway stent placement as a barrier effect as the lesions regrew very quickly (<3 months) after the previous bronchoscopic debulking procedure. However, in our discussions with the patient prior to the procedure, he expressed reluctance to have a stent placed due to possible cough associated with the stent and the fact that he only restarted chemotherapy 2 weeks ago. I suspect that these lesions will recur unless he has a profound response to systemic treatment and possible radiation, and if I need to debulk again, I will strongly advocate for placement of a covered tracheal stent.

Recommendations:
• Transfer patient back to ward room
• Await final pathology results
• Will need to speak with oncology regarding other treatment options which might include PDT or brachytherapy

I, Patricia Lee, MD, was present and actively involved in all phases of the procedure.

________________________________________"""
entities_10 = [
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "Endotracheal", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "tumor", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "Endotracheal", 2)},
    {"label": "OBS_LESION",        **get_span(text_10, "tumor", 2)},
    {"label": "PROC_ACTION",       **get_span(text_10, "debulking", 1)},
    {"label": "PROC_METHOD",       **get_span(text_10, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "tumor", 3)},
    {"label": "PROC_ACTION",       **get_span(text_10, "ablation", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "Tracheal", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "obstruction", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "flexible bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "LMA", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "subglottic space", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "polypoid lesions", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "blocking about 90%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "50% obstruction", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "polypoid", 2)},
    {"label": "OBS_LESION",        **get_span(text_10, "lesions", 3)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "anterior trachea", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "posterior trachea", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "lateral trachea", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "main carina", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right-sided", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "left-sided", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "endobronchial tumor", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "extrinsic obstruction", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "flexible bronchoscope", 2)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "LMA", 2)},
    {"label": "MEAS_SIZE",         **get_span(text_10, "10 mm", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "rigid tracheoscope", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "proximal trachea", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "tumor", 5)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "T190 Olympus flexible bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "rigid bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "electrocautery snare", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "transect", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "polypoid lesions", 2)},
    {"label": "OBS_LESION",        **get_span(text_10, "lesions", 6)},
    {"label": "OBS_LESION",        **get_span(text_10, "lesions", 7)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "snare", 2)},
    {"label": "PROC_METHOD",       **get_span(text_10, "APC", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "tumor", 6)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "posterior and lateral trachea walls", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "trachea", 6)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "90% open", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "rigid bronchoscope", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no complications", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "airway stent", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "debulking", 2)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 2)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 3)},
    {"label": "PROC_ACTION",       **get_span(text_10, "debulk", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "covered tracheal stent", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")