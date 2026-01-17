import sys
from pathlib import Path

# Set up the repository root directory
# (Assumes this script is running from within the repository or a subfolder)
try:
    REPO_ROOT = Path(__file__).resolve().parents[1]  # Adjust parent count if needed
except NameError:
    REPO_ROOT = Path('.').resolve()

# Import the utility function
# Ensure 'scripts' is a python package or in python path
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    :param text: The raw text string.
    :param term: The substring to search for (case-sensitive).
    :param occurrence: The 1-based index of the occurrence to find.
    :return: A tuple (start_index, end_index) or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Occurrence not found
    return start, start + len(term)

# ==========================================
# Note 1: 659521_syn_1
# ==========================================
text_1 = """Dx: Early stage RUL SCC.
Anesthesia: Mod Sed.
Proc: Washings. 5F poly cath placed. Fluoro verified.
Plan: 6Gy x 4. Curative intent."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RUL", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_1, "SCC", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_1, "Washings", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_1, "Fluoro", 1)))},
    {"label": "MEAS_ENERGY",   **dict(zip(["start", "end"], get_span(text_1, "6Gy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 659521_syn_2
# ==========================================
text_2 = """CLINICAL RECORD: [REDACTED], a 74-year-old male with roentgenographically occult squamous cell carcinoma of the RUL (B3), presented for curative-intent brachytherapy. Flexible bronchoscopy under moderate sedation revealed the 0.8 cm lesion. A 5-French polyethylene catheter was placed across the tumor bed. Fluoroscopic verification confirmed appropriate positioning. The patient was transferred for the first of four fractions."""

entities_2 = [
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_2, "squamous cell carcinoma", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "RUL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "B3", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_2, "lesion", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_2, "tumor", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_2, "Fluoroscopic", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 659521_syn_3
# ==========================================
text_3 = """Service: 31643 (Cath placement).
Bundle: 31622 (Washings - included).
Target: RUL B3 Segment.
Device: 5F Polyethylene Catheter.
Guidance: Fluoroscopy.
Intent: Curative (Early stage)."""

entities_3 = [
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_3, "Washings", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_3, "RUL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_3, "B3 Segment", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_3, "Fluoroscopy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 659521_syn_4
# ==========================================
text_4 = """Resident Note
Pt: C. White
Procedure: Brachy Cath #1
Steps:
1. Mod sed.
2. Scope RUL B3.
3. Washings.
4. 5F cath placed.
5. Fluoro check.
Plan: 6Gy today."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_4, "RUL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_4, "B3", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_4, "Washings", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_4, "Fluoro", 1)))},
    {"label": "MEAS_ENERGY",   **dict(zip(["start", "end"], get_span(text_4, "6Gy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 659521_syn_5
# ==========================================
text_5 = """charles white here for his early lung cancer treatment rul b3 segment we did the scope with sedation took some washings then put the 5f catheter in checked it with fluoro taped it up he goes for 6gy radiation now"""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_5, "rul", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_5, "b3 segment", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_5, "washings", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_5, "fluoro", 1)))},
    {"label": "MEAS_ENERGY",   **dict(zip(["start", "end"], get_span(text_5, "6gy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 659521_syn_6
# ==========================================
text_6 = """Bronchoscopy for brachytherapy catheter placement. Patient has early-stage RUL SCC. Moderate sedation. 5F polyethylene catheter placed in RUL B3. Fluoroscopic confirmation. Washings obtained. Patient sent for radiation therapy session 1 of 4."""

entities_6 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "RUL", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_6, "SCC", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "RUL", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "B3", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_6, "Fluoroscopic", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_6, "Washings", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 659521_syn_7
# ==========================================
text_7 = """[Indication]
Occult RUL SCC (B3).
[Anesthesia]
Moderate sedation.
[Description]
Lesion visualized. Washings taken. 5F catheter inserted. Position verified with fluoroscopy.
[Plan]
6.0 Gy fraction 1. Weekly sessions."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_7, "RUL", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_7, "SCC", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_7, "B3", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_7, "Lesion", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_7, "Washings", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_7, "fluoroscopy", 1)))},
    {"label": "MEAS_ENERGY",   **dict(zip(["start", "end"], get_span(text_7, "6.0 Gy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 659521_syn_8
# ==========================================
text_8 = """[REDACTED] a very early stage cancer in his right upper lobe. We are treating it with brachytherapy. Today was session one. We sedated him, checked the airway, and took some washings. Then we put a 5F catheter right past the small tumor in the B3 segment. Fluoroscopy confirmed it was perfect. He's getting 6 Gy today."""

entities_8 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "right upper lobe", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_8, "washings", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_8, "tumor", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "B3 segment", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_8, "Fluoroscopy", 1)))},
    {"label": "MEAS_ENERGY",   **dict(zip(["start", "end"], get_span(text_8, "6 Gy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 659521_syn_9
# ==========================================
text_9 = """Dx: Occult RUL carcinoma.
Proc: Scope with positioning of brachytherapy line.
Details: 5F polyethylene tube inserted into B3. Location validated via fluoroscopy. Washings collected. Curative 6 Gy dose planned."""

entities_9 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_9, "RUL", 1)))},
    {"label": "OBS_LESION",    **dict(zip(["start", "end"], get_span(text_9, "carcinoma", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_9, "B3", 1)))},
    {"label": "PROC_METHOD",   **dict(zip(["start", "end"], get_span(text_9, "fluoroscopy", 1)))},
    {"label": "PROC_ACTION",   **dict(zip(["start", "end"], get_span(text_9, "Washings", 1)))},
    {"label": "MEAS_ENERGY",   **dict(zip(["start", "end"], get_span(text_9, "6 Gy", 1)))},
]
BATCH_DATA.append({"id": "659521_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)