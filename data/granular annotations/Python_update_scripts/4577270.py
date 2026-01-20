import sys
from pathlib import Path

# Set up the repository root path
# Assumes this script is run from a subdirectory or the root of the repo
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running from the correct repository context.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Case 1: 4577270_syn_1
# ==========================================
id_1 = "4577270_syn_1"
text_1 = """Indication: Exudative effusion.
Proc: Left Dx Thoracoscopy.
- Findings: Fibrinous adhesions, trapped lung.
- Fluid evacuated.
- Chest tube placed.
- No biopsy mentioned."""

entities_1 = [
    {"label": "OBS_FINDING", **get_span(text_1, "Exudative effusion", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Fibrinous adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "trapped lung", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Case 2: 4577270_syn_2
# ==========================================
id_2 = "4577270_syn_2"
text_2 = """OPERATIVE REPORT: Left diagnostic thoracoscopy. Entry at the 6th intercostal space. Inspection revealed fibrinous adhesions and the appearance of a trapped lung. The parietal, visceral, and diaphragmatic surfaces were visualized within the limits of the adhesions. Fluid was evacuated and a chest tube was placed."""

entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "6th intercostal space", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "fibrinous adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_2, "trapped lung", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragmatic", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "adhesions", 2)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})


# ==========================================
# Case 3: 4577270_syn_3
# ==========================================
id_3 = "4577270_syn_3"
text_3 = """Code: 32601 (Diagnostic).
Side: Left.
Findings: Adhesions, trapped lung.
Action: Visualization and fluid evacuation. Chest tube placement. No biopsy or pleurodesis documented."""

entities_3 = [
    {"label": "LATERALITY", **get_span(text_3, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "Adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_3, "trapped lung", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})


# ==========================================
# Case 4: 4577270_syn_4
# ==========================================
id_4 = "4577270_syn_4"
text_4 = """Left Thoracoscopy
Findings: Trapped lung, adhesions.
Steps: Entry -> Looked around -> Drained fluid -> Tube.
No biopsy. Lung expanded poorly (trapped)."""

entities_4 = [
    {"label": "LATERALITY", **get_span(text_4, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Thoracoscopy", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_4, "Trapped lung", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "adhesions", 1)},
    # "Tube" is generic, but in context implies chest tube. Mapping as DEV_CATHETER.
    {"label": "DEV_CATHETER", **get_span(text_4, "Tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_4, "Lung expanded poorly", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})


# ==========================================
# Case 5: 4577270_syn_5
# ==========================================
id_5 = "4577270_syn_5"
text_5 = """nicholas green left side. diagnostic scope. saw adhesions and trapped lung. drained fluid put tube in. no biopsy just looked."""

entities_5 = [
    {"label": "LATERALITY", **get_span(text_5, "left side", 1)},
    # "scope" as instrument
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_5, "trapped lung", 1)},
    # "tube" implicitly catheter
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})


# ==========================================
# Case 6: 4577270_syn_6
# ==========================================
id_6 = "4577270_syn_6"
text_6 = """Medical Thoracoscopy (Pleuroscopy) - Diagnostic. Single-port entry at 6th intercostal space, mid-axillary line (Left). Findings: Fibrinous adhesions with trapped lung. Parietal, visceral, and diaphragmatic pleura visualized. All remaining fluid evacuated. Chest tube placed."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "6th intercostal space", 1)},
    {"label": "LATERALITY", **get_span(text_6, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Fibrinous adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_6, "trapped lung", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragmatic pleura", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})


# ==========================================
# Case 7: 4577270_syn_7
# ==========================================
id_7 = "4577270_syn_7"
text_7 = """[Indication]
Exudative effusion.
[Description]
Left side. Visualized fibrinous adhesions and trapped lung. Fluid evacuated. Chest tube placed.
[Plan]
Admit. Water seal."""

entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "Exudative effusion", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Left side", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "fibrinous adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_7, "trapped lung", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})


# ==========================================
# Case 8: 4577270_syn_8
# ==========================================
id_8 = "4577270_syn_8"
text_8 = """We looked inside [REDACTED] with the thoracoscope. We found adhesions and what looks like a trapped lung. We drained the fluid and put a chest tube in, but didn't take any biopsies this time."""

entities_8 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "thoracoscope", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_8, "trapped lung", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})


# ==========================================
# Case 9: 4577270_syn_9
# ==========================================
id_9 = "4577270_syn_9"
text_9 = """Procedure: Diagnostic Pleuroscopy.
Side: Left.
Observations: Fibrinous bands and entrapped parenchyma.
Action: Drained effusion. Placed intercostal catheter."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Pleuroscopy", 1)},
    {"label": "LATERALITY", **get_span(text_9, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Fibrinous bands", 1)},
    # "entrapped parenchyma" is synonymous with trapped lung
    {"label": "OUTCOME_PLEURAL", **get_span(text_9, "entrapped parenchyma", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "intercostal catheter", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})


# ==========================================
# Case 10: 4577270
# ==========================================
id_10 = "4577270"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: CDR Patricia Davis, MD

Indication: Cytology-negative exudative effusion
Side: Left

PROCEDURE: Medical Thoracoscopy (Pleuroscopy) - Diagnostic
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted.

FINDINGS: Fibrinous adhesions with trapped lung
Parietal, visceral, and diaphragmatic pleura visualized.
All remaining fluid evacuated under direct visualization.
Chest tube placed. No air leak. Lung expanded.

DISPOSITION: Floor admission, chest tube to water seal.
F/U: Path results in 3-5 days. Tube removal when output <150mL/day.

Davis, MD"""

entities_10 = [
    {"label": "OBS_FINDING", **get_span(text_10, "exudative effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "pleuroscope", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Fibrinous adhesions", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "trapped lung", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "Lung expanded", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)