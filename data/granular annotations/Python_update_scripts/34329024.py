import sys
from pathlib import Path

# Set up the repository root path to import utilities
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
    
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 34329024_syn_1
# ==========================================
text_1 = """Indication: R Pleural Effusion.
Proc: Med Thoracoscopy + IPC.
Findings: Carcinomatosis. 1600cc fluid.
Action: Biopsy x12. 15.5Fr IPC placed/tunneled.
Result: Lung re-expanded. Minimal bleed."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Pleural Effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Med Thoracoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "IPC", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Carcinomatosis", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "1600cc", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x12", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "15.5Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "IPC", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "tunneled", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "Lung re-expanded", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Minimal bleed", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 34329024_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Medical Thoracoscopy and Indwelling Pleural Catheter Placement.
CLINICAL SUMMARY: Right-sided exudative effusion. 
FINDINGS: 1.6L serosanguinous fluid drained. Diffuse parietal and visceral nodules consistent with carcinomatosis. 
INTERVENTION: Twelve biopsies were taken. A PleurX catheter was tunneled and inserted under direct visualization. Post-procedure imaging confirmed catheter position."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Medical Thoracoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "Indwelling Pleural Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Placement", 1)},
    {"label": "LATERALITY", **get_span(text_2, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "exudative effusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "1.6L", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "serosanguinous fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "drained", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "visceral", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "carcinomatosis", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "taken", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "PleurX", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "tunneled", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "inserted", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 2)},
]
BATCH_DATA.append({"id": "34329024_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 34329024_syn_3
# ==========================================
text_3 = """Codes: 32601 (Dx Thoracoscopy), 32550 (IPC placement).
Rationale: Diagnostic inspection and biopsy of pleural carcinomatosis followed by placement of a tunneled catheter for long-term drainage.
Pathology: Pleural nodules biopsied."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Dx Thoracoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "IPC", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "placement", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "inspection", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "carcinomatosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "placement", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "tunneled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "drainage", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "Pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsied", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 34329024_syn_4
# ==========================================
text_4 = """Procedure: Pleuroscopy & PleurX.
Steps:
1. Lateral decubitus.
2. Trocar placement.
3. Fluid drainage (1600cc).
4. Biopsies of nodules (x12).
5. PleurX catheter tunneled and placed.
6. Closure.
No complications."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Pleuroscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "PleurX", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Trocar", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "placement", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "drainage", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "1600cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x12", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "tunneled", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "placed", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No complications", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 34329024_syn_5
# ==========================================
text_5 = """thoracoscopy for maizie booth... drained 1600cc fluid... saw cancer nodules everywhere took 12 biopsies... put in a pleurx catheter for drainage... tunnel looks good... sent tissue to lab."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "1600cc", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pleurx catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drainage", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "tissue", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 34329024_syn_6
# ==========================================
text_6 = """Pt: [REDACTED]. Proc: Medical Thoracoscopy, IPC placement. Findings: 1600cc fluid, diffuse nodules. Action: Biopsy x12, IPC (15.5Fr) placed. Outcome: Lung re-expanded, catheter functional. Plan: Path f/u, catheter teaching."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Medical Thoracoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "IPC", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "placement", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "1600cc", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x12", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "IPC", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "15.5Fr", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "placed", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_6, "Lung re-expanded", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 34329024_syn_7
# ==========================================
text_7 = """[Indication]
Right pleural effusion, suspect malignancy.
[Anesthesia]
Moderate/Local.
[Description]
Thoracoscopic entry. 1600cc drained. Multiple biopsies of nodules. Indwelling pleural catheter placed and tunneled.
[Plan]
Discharge, catheter care education."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Thoracoscopic", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "1600cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "drained", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Indwelling pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "placed", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "tunneled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "catheter", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 34329024_syn_8
# ==========================================
text_8 = """[REDACTED] a medical thoracoscopy to investigate her pleural effusion. We drained 1.6 liters of fluid and found extensive nodules, which were biopsied. To manage the recurrent fluid, we placed a tunneled pleural catheter. She tolerated the procedure well."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "pleural effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "1.6 liters", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsied", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 2)},
    {"label": "PROC_ACTION", **get_span(text_8, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "tunneled pleural catheter", 1)},
]
BATCH_DATA.append({"id": "34329024_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 34329024_syn_9
# ==========================================
text_9 = """Intervention: Medical Thoracoscopy with implantation of tunneled drainage catheter. Subject: Maizie Booth. Findings: Extensive carcinomatosis. Action: Twelve tissue samples procured. Tunneled catheter deployed for chronic drainage."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "implantation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tunneled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "drainage catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "carcinomatosis", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Twelve", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "tissue samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "procured", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Tunneled catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "deployed", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drainage", 2)},
]
BATCH_DATA.append({"id": "34329024_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 34329024
# ==========================================
text_10 = """Proceduralist(s): Daniel Larson MD
Procedure Name: Medical Thoracoscopy (pleuroscopy)
Patient Name: [REDACTED]
Patient [REDACTED]: [REDACTED]
Indications: Right sided Pleural effusion
Medications: As per anesthesia record
Procedure, risks, benefits, and alternatives were explained to the patient. All questions were answered and informed consent was documented as per institutional protocol. A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed. A time-out was performed prior to the intervention. The patient was placed on the standard procedural bed in the left lateral decubitus position and sites of compression were well padded. The pleural entry site was id[REDACTED] by means of the ultrasound. The patient was sterilely prepped with chlorhexidine gluconate (Chloraprep) and draped in the usual fashion. The entry sites was infiltrated with a 10mL solution of 1% lidocaine. Following instillation of subcutaneous lidocaine a 1.5 cm subcutaneous incision was made and gentle dissection was performed until the pleural space was entered.  An 8 mm disposable primary port was then placed on the left side at the 6th anterior axillary line. After allowing air entrainment and lung deflation, suction was applied through the port to remove pleural fluid with removal of approximately 1600cc of serosanguinous fluid. The rigid pleuroscopy telescope was then introduced through the trocar and advanced into the pleural space. The pleura was had diffuse carcinomatosis with multiple hard white pleural nodules covering the parietal and visceral pleura.  No adhesions were present Biopsies of the abnormal areas in the parietal pleura posteriorly were performed with forceps and sent for histopathological and microbiological examination with approximately 12 total biopsies taken. There was minimal bleeding associated with the biopsies. After residual bleeding had subsided, the pleuroscopy telescope was then removed and a 15.5 pleural catheter was placed into the pleural space through the primary port with tunneling anteriorly.
Complications: None
The patient tolerated the procedural well.
Post-procedure chest radiograph showed mild post-procedural subcutaneous air with full lung re-expansion and IPC in place
Estimated Blood Loss: 15cc
Post Procedure Diagnosis: Pleural effusion 
Recommendation:
Will await pathology and microbiological studies
Patient [REDACTED] pleural catheter draining and will next week for initial drainage.
Jordan Parks, MD 
Pulmonology Medicine
UCLA Medical Center"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "pleuroscopy", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Pleural effusion", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 1)},
    {"label": "MEDICATION", **get_span(text_10, "chlorhexidine gluconate", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Chloraprep", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.5 cm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "dissection", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural space", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "entered", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "8 mm", 1)},
    {"label": "LATERALITY", **get_span(text_10, "left", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th anterior axillary line", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "suction", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "remove", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "pleural fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "removal", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "1600cc", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "serosanguinous fluid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "pleuroscopy telescope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "trocar", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural space", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "carcinomatosis", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleura", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "minimal bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "pleuroscopy telescope", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "15.5", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placed", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural space", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "tunneling", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "full lung re-expansion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "IPC", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "15cc", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Pleural effusion", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "pleural catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "drainage", 1)},
]
BATCH_DATA.append({"id": "34329024", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)