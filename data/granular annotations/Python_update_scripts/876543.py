import sys
from pathlib import Path

# Set up the repository root directory
# (Assuming this script is run from within the repository structure)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is in the correct directory structure.")
    sys.exit(1)

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
# Note 1: 876543_syn_1
# ==========================================
text_1 = """Indication: Severe asthma.
Procedure: Bronchial Thermoplasty (Session 1/3).
- GA/ETT.
- Alair catheter.
- Treated RLL segments (Posterior, Lateral, Anterior, Medial, Superior).
- 59 activations total.
- No bleeding.
Plan: Discharge. Next session in 3 weeks."""

entities_1 = [
    {"label": "OBS_LESION",      **get_span(text_1, "Severe asthma", 1)},     # Indication
    {"label": "PROC_ACTION",     **get_span(text_1, "Bronchial Thermoplasty", 1)}, # Specific intervention
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Alair catheter", 1)},    # Transient tool/device
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "RLL", 1)},               # Lobes
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "Posterior", 1)},         # Segments
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "Lateral", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "Anterior", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "Medial", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "Superior", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "59", 1)},                # Integer count
    {"label": "OBS_FINDING",     **get_span(text_1, "bleeding", 1)}           # General finding
]
BATCH_DATA.append({"id": "876543_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 876543_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: The patient presented for the initial session of Bronchial Thermoplasty for refractory severe asthma. Under general anesthesia, the Alair system was deployed. Systematic treatment of the right lower lobe was undertaken. Radiofrequency energy was delivered to the distal airways of all basal segments and the superior segment, totaling 59 activations. The bronchial mucosa appeared blanched consistent with effective treatment. The patient tolerated the procedure well without bronchospasm."""

entities_2 = [
    {"label": "PROC_ACTION",     **get_span(text_2, "Bronchial Thermoplasty", 1)},
    {"label": "OBS_LESION",      **get_span(text_2, "severe asthma", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_2, "Alair system", 1)},      # Device
    {"label": "ANAT_LUNG_LOC",   **get_span(text_2, "right lower lobe", 1)},  # 
    {"label": "ANAT_LUNG_LOC",   **get_span(text_2, "basal segments", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_2, "superior segment", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_2, "59", 1)},
    {"label": "OBS_FINDING",     **get_span(text_2, "blanched", 1)},          # Finding
    {"label": "OBS_FINDING",     **get_span(text_2, "bronchospasm", 1)}
]
BATCH_DATA.append({"id": "876543_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 876543_syn_3
# ==========================================
text_3 = """Code: 31660 (Bronchial Thermoplasty, one lobe).
Target: Right Lower Lobe (RLL).
Details:
- Initial session.
- System: Alair.
- Activations: 59 total across RLL segments.
- Scope: Diagnostic bronchoscopy included."""

entities_3 = [
    {"label": "PROC_ACTION",     **get_span(text_3, "Bronchial Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_3, "Right Lower Lobe", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_3, "RLL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_3, "Alair", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_3, "59", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_3, "RLL", 2)},
    {"label": "PROC_ACTION",     **get_span(text_3, "Diagnostic bronchoscopy", 1)} # 
]
BATCH_DATA.append({"id": "876543_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 876543_syn_4
# ==========================================
text_4 = """Procedure: Thermoplasty RLL
Patient: [REDACTED]
Steps:
1. GA / Tube.
2. Airway check.
3. Alair catheter used.
4. Zapped RLL segments (59 times total).
5. Checked for bleeding - none.
6. Woke patient up.
Plan: Home."""

entities_4 = [
    {"label": "PROC_ACTION",     **get_span(text_4, "Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_4, "RLL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_4, "Alair catheter", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_4, "RLL", 2)},
    {"label": "MEAS_COUNT",      **get_span(text_4, "59", 1)},
    {"label": "OBS_FINDING",     **get_span(text_4, "bleeding", 1)}
]
BATCH_DATA.append({"id": "876543_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 876543_syn_5
# ==========================================
text_5 = """Thermoplasty session 1 for Lisa Simpson. Severe asthma. Did the RLL today. General anesthesia. Used the Alair probe. Did about 59 activations in the lower lobe. Went fine no bleeding. Patient stable."""

entities_5 = [
    {"label": "PROC_ACTION",     **get_span(text_5, "Thermoplasty", 1)},
    {"label": "OBS_LESION",      **get_span(text_5, "Severe asthma", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_5, "RLL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_5, "Alair probe", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_5, "59", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_5, "lower lobe", 1)},
    {"label": "OBS_FINDING",     **get_span(text_5, "bleeding", 1)}
]
BATCH_DATA.append({"id": "876543_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 876543_syn_6
# ==========================================
text_6 = """Bronchoscopy with bronchial thermoplasty. Patient 8F (Adult size/context). Severe asthma. General anesthesia. RLL treated. 59 activations delivered to basal and superior segments. Alair system used. Complications none. Extubated. Stable."""

entities_6 = [
    {"label": "PROC_ACTION",     **get_span(text_6, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",     **get_span(text_6, "bronchial thermoplasty", 1)},
    {"label": "OBS_LESION",      **get_span(text_6, "Severe asthma", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_6, "RLL", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_6, "59", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_6, "basal", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_6, "superior segments", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_6, "Alair system", 1)}
]
BATCH_DATA.append({"id": "876543_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 876543_syn_7
# ==========================================
text_7 = """[Indication]
Severe refractory asthma.
[Anesthesia]
General, ETT.
[Description]
Bronchial thermoplasty of RLL performed. 59 activations delivered via Alair catheter. Mucosa blanched. No bleeding.
[Plan]
Discharge, Session 2 in 3 weeks."""

entities_7 = [
    {"label": "OBS_LESION",      **get_span(text_7, "Severe refractory asthma", 1)},
    {"label": "PROC_ACTION",     **get_span(text_7, "Bronchial thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_7, "RLL", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_7, "59", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_7, "Alair catheter", 1)},
    {"label": "OBS_FINDING",     **get_span(text_7, "blanched", 1)},
    {"label": "OBS_FINDING",     **get_span(text_7, "bleeding", 1)}
]
BATCH_DATA.append({"id": "876543_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 876543_syn_8
# ==========================================
text_8 = """Lisa came in for her first bronchial thermoplasty treatment for severe asthma. We focused on the right lower lobe today. Under anesthesia, we used a special catheter to deliver heat energy to the airway walls, completing 59 activations. This helps reduce the smooth muscle mass. She woke up fine with no issues."""

entities_8 = [
    {"label": "PROC_ACTION",     **get_span(text_8, "bronchial thermoplasty", 1)},
    {"label": "OBS_LESION",      **get_span(text_8, "severe asthma", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_8, "right lower lobe", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_8, "catheter", 1)}, # Context implies device used
    {"label": "MEAS_COUNT",      **get_span(text_8, "59", 1)}
]
BATCH_DATA.append({"id": "876543_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 876543_syn_9
# ==========================================
text_9 = """Procedure: Endobronchial radiofrequency ablation (Thermoplasty).
Action: The RLL was targeted. Thermal energy was applied to the bronchial walls via the Alair device. 59 applications were administered. Mucosal reaction was observed.
Result: Treatment of RLL completed."""

entities_9 = [
    {"label": "PROC_ACTION",     **get_span(text_9, "Endobronchial radiofrequency ablation", 1)},
    {"label": "PROC_ACTION",     **get_span(text_9, "Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_9, "RLL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_9, "Alair device", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_9, "59", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_9, "RLL", 2)}
]
BATCH_DATA.append({"id": "876543_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 876543 (Main)
# ==========================================
text_10 = """Bronchoscopy Note - Thermoplasty Session 1

Patient: [REDACTED] | MRN: [REDACTED] | Date: [REDACTED]
Provider: Dr. Hibbert

**History:** Severe persistent asthma refractory to biologics. Presenting for first session of Bronchial Thermoplasty (RLL).

**Procedure:**
- General Anesthesia/ETT.
- Alair catheter introduced.
- RLL basal segments treated systematically.
- **Activations:**
  - Right Posterior Basal: 14 activations
  - Right Lateral Basal: 12 activations
  - Right Anterior Basal: 10 activations
  - Right Medial Basal: 8 activations
  - Right Superior Segment: 15 activations
- Total Activations: 59.
- No significant bleeding or mucosal injury observed.

**Post-Op:** Stable. Extubated. Observe for bronchospasm."""

entities_10 = [
    {"label": "PROC_ACTION",     **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",     **get_span(text_10, "Thermoplasty", 1)},
    {"label": "OBS_LESION",      **get_span(text_10, "Severe persistent asthma", 1)},
    {"label": "PROC_ACTION",     **get_span(text_10, "Bronchial Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "RLL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_10, "Alair catheter", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "basal segments", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "Right Posterior Basal", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "14", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "Right Lateral Basal", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "12", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "Right Anterior Basal", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "10", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "Right Medial Basal", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "8", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_10, "Right Superior Segment", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "15", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_10, "59", 1)},
    {"label": "OBS_FINDING",     **get_span(text_10, "bleeding", 1)},
    {"label": "OBS_FINDING",     **get_span(text_10, "mucosal injury", 1)},
    {"label": "OBS_FINDING",     **get_span(text_10, "bronchospasm", 1)}
]
BATCH_DATA.append({"id": "876543", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)