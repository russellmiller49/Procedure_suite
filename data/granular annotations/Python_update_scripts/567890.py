import sys
import os
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from within the repository structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the system path to allow importing the utility
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the script is running in the correct environment/directory structure.")
    sys.exit(1)

# ==========================================
# Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found required number of times
            
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Data Payload
# ==========================================
BATCH_DATA = []

# -----------------------------------------------------------------------------
# Case 1: 567890_syn_1
# -----------------------------------------------------------------------------
text_1 = """Dx: Loculated MPE (NSCLC).
Proc: IPC fibrinolysis Day 1.
- 10mg tPA / 5mg DNase.
- 2hr dwell w/ repositioning.
- Drained 850mL straw fluid.
- SpO2 improved 89->94%."""

entities_1 = [
    {"label": "OBS_FINDING", **get_span(text_1, "Loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "MPE", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "IPC", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "fibrinolysis", 1)},
    {"label": "MEDICATION", **get_span(text_1, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_1, "DNase", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "2hr", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "repositioning", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "850mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "straw", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_1, "SpO2 improved", 1)},
]
BATCH_DATA.append({"id": "567890_syn_1", "text": text_1, "entities": entities_1})

# -----------------------------------------------------------------------------
# Case 2: 567890_syn_2
# -----------------------------------------------------------------------------
text_2 = """PROCEDURE: Intrapleural fibrinolytic therapy via indwelling pleural catheter.
INDICATION: Recurrent loculated malignant pleural effusion secondary to Stage IV NSCLC.
DESCRIPTION: A solution of 10 mg tPA and 5 mg DNase was instilled into the pleural space via the PleurX catheter. The patient was repositioned during the two-hour dwell time to ensure distribution. Subsequent drainage yielded 850 mL of fluid, resulting in symptomatic improvement and increased oxygen saturation."""

entities_2 = [
    {"label": "ANAT_PLEURA", **get_span(text_2, "Intrapleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "fibrinolytic therapy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "indwelling pleural catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "NSCLC", 1)},
    {"label": "MEDICATION", **get_span(text_2, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_2, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "instilled", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "repositioned", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "two-hour", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "drainage", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "850 mL", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_2, "symptomatic improvement", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_2, "increased oxygen saturation", 1)},
]
BATCH_DATA.append({"id": "567890_syn_2", "text": text_2, "entities": entities_2})

# -----------------------------------------------------------------------------
# Case 3: 567890_syn_3
# -----------------------------------------------------------------------------
text_3 = """CPT 32561. Instillation of fibrinolytic.
Catheter: Left IPC.
Dose: 10mg tPA / 5mg DNase.
Volume Drained: 850mL.
Medical Necessity: Symptomatic loculated MPE."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(text_3, "fibrinolytic", 1)},
    {"label": "LATERALITY", **get_span(text_3, "Left", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "IPC", 1)},
    {"label": "MEDICATION", **get_span(text_3, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_3, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "850mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "MPE", 1)},
]
BATCH_DATA.append({"id": "567890_syn_3", "text": text_3, "entities": entities_3})

# -----------------------------------------------------------------------------
# Case 4: 567890_syn_4
# -----------------------------------------------------------------------------
text_4 = """Procedure: IPC Lytic Instillation
1. Prep and flush.
2. Instill tPA/DNase.
3. Clamp 2h, rotate patient.
4. Drain.
Output 850mL. Breathing improved."""

entities_4 = [
    {"label": "DEV_CATHETER", **get_span(text_4, "IPC", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Instillation", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "flush", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Instill", 1)},
    {"label": "MEDICATION", **get_span(text_4, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_4, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Clamp", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "2h", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "rotate", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drain", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "850mL", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_4, "Breathing improved", 1)},
]
BATCH_DATA.append({"id": "567890_syn_4", "text": text_4, "entities": entities_4})

# -----------------------------------------------------------------------------
# Case 5: 567890_syn_5
# -----------------------------------------------------------------------------
text_5 = """Jennifer Walsh lung cancer patient with the pleurx that stopped draining we put in tpa and dnase today clamped it moved her around a bit after two hours got out huge amount 850ml she feels way better sats up."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "lung cancer", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pleurx", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "draining", 1)},
    {"label": "MEDICATION", **get_span(text_5, "tpa", 1)},
    {"label": "MEDICATION", **get_span(text_5, "dnase", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "clamped", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "moved her around", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "two hours", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "850ml", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "feels way better", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "sats up", 1)},
]
BATCH_DATA.append({"id": "567890_syn_5", "text": text_5, "entities": entities_5})

# -----------------------------------------------------------------------------
# Case 6: 567890_syn_6
# -----------------------------------------------------------------------------
text_6 = """Stage IV NSCLC with recurrent loculated left MPE. Fibrinolytic instillation via IPC Day 1. Catheter flushed patent. Instilled 10mg tPA + 5mg DNase in 100mL NS. Catheter clamped. Patient repositioned side-to-side over 2hr dwell period. Drained 850mL straw-colored fluid after unclamping. No complications."""

entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "NSCLC", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "loculated", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "MPE", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Fibrinolytic instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "IPC", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "flushed", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "patent", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_6, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_6, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "100mL", 1)},
    {"label": "MEDICATION", **get_span(text_6, "NS", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "clamped", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "repositioned", 1)},
    {"label": "MEAS_TIME", **get_span(text_6, "2hr", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "850mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "straw-colored", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": "567890_syn_6", "text": text_6, "entities": entities_6})

# -----------------------------------------------------------------------------
# Case 7: 567890_syn_7
# -----------------------------------------------------------------------------
text_7 = """[Indication]
Loculated malignant pleural effusion (NSCLC).
[Anesthesia]
None.
[Description]
Instilled 10mg tPA/5mg DNase via IPC. 2 hour dwell. Drained 850mL.
[Plan]
Daily x 3 days."""

entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "Loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "NSCLC", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_7, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_7, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "IPC", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "2 hour", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "850mL", 1)},
]
BATCH_DATA.append({"id": "567890_syn_7", "text": text_7, "entities": entities_7})

# -----------------------------------------------------------------------------
# Case 8: 567890_syn_8
# -----------------------------------------------------------------------------
text_8 = """[REDACTED] a malignant effusion that wasn't draining due to loculations. We treated this by injecting tPA and DNase into her PleurX catheter. We asked her to move side-to-side while the tube was clamped for two hours to spread the medicine. This was very effective, draining 850mL of fluid and significantly improving her oxygen levels and breathing."""

entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "malignant effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "injecting", 1)},
    {"label": "MEDICATION", **get_span(text_8, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_8, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "move side-to-side", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "clamped", 1)},
    {"label": "MEAS_TIME", **get_span(text_8, "two hours", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "draining", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "850mL", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "improving her oxygen levels", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "breathing", 1)},
]
BATCH_DATA.append({"id": "567890_syn_8", "text": text_8, "entities": entities_8})

# -----------------------------------------------------------------------------
# Case 9: 567890_syn_9
# -----------------------------------------------------------------------------
text_9 = """Diagnosis: Septated malignant fluid collection.
Action: Administered lytic therapy via indwelling catheter.
Details: 10mg alteplase and 5mg dornase alfa injected. Catheter occluded for 2 hours with patient rotation. Released to drain 850mL. Respiratory status improved."""

entities_9 = [
    {"label": "OBS_FINDING", **get_span(text_9, "Septated", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "malignant fluid collection", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "lytic therapy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "indwelling catheter", 1)},
    {"label": "MEDICATION", **get_span(text_9, "alteplase", 1)},
    {"label": "MEDICATION", **get_span(text_9, "dornase alfa", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "injected", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "occluded", 1)},
    {"label": "MEAS_TIME", **get_span(text_9, "2 hours", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "rotation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drain", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "850mL", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_9, "Respiratory status improved", 1)},
]
BATCH_DATA.append({"id": "567890_syn_9", "text": text_9, "entities": entities_9})

# -----------------------------------------------------------------------------
# Case 10: 567890
# -----------------------------------------------------------------------------
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Robert Lee

Dx: Stage IV NSCLC with recurrent loculated left MPE
Procedure: Fibrinolytic instillation via IPC, Day 1

Hx: 70F with NSCLC, left PleurX in place x 3 months. Recent US shows multiple new septations with decreased output despite symptomatic dyspnea and recurrent effusion on imaging.

Procedure:
Patient [REDACTED]. PleurX site cleaned. Catheter flushed - patent.
Instilled 10mg tPA + 5mg DNase in 100mL NS.
Catheter clamped. Patient repositioned side-to-side over 2hr dwell period.
Drained 850mL straw-colored fluid after unclamping.

No complications. Patient reports improved breathing. SpO2 94% on RA vs 89% pre-procedure.

Continue daily x 3 days, f/u in clinic 1 week.

R. Lee MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "NSCLC", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "loculated", 1)},
    {"label": "LATERALITY", **get_span(text_10, "left", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "MPE", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Fibrinolytic instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "IPC", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "NSCLC", 2)},
    {"label": "LATERALITY", **get_span(text_10, "left", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "PleurX", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "septations", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "dyspnea", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "PleurX", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "flushed", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "patent", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_10, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_10, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "100mL", 1)},
    {"label": "MEDICATION", **get_span(text_10, "NS", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "clamped", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "repositioned", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "2hr", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "850mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "straw-colored", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "improved breathing", 1)},
]
BATCH_DATA.append({"id": "567890", "text": text_10, "entities": entities_10})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)