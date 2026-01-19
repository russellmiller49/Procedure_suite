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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Case 1: 45678912_syn_1
# ==========================================
text_1 = """Procedure: Bronchoscopy w/ EBV.
Indication: LLL Emphysema.
Action: Airway inspected. LLL target. 
Intervention: Placed 3 Zephyr valves (LB6, LB8, LB9-10). 
Result: Good seal. Complete occlusion.
Plan: CXR, Admit."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "DEV_VALVE", **get_span(text_1, "EBV", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)},
    {"label": "DEV_VALVE", **get_span(text_1, "Zephyr", 1)},
    {"label": "DEV_VALVE", **get_span(text_1, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB8", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB9-10", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CXR", 1)},
]
BATCH_DATA.append({"id": "45678912_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Case 2: 45678912_syn_2
# ==========================================
text_2 = """HISTORY: The patient, a 72-year-old female with severe heterogeneous emphysema predominantly affecting the left lower lobe, presented for bronchoscopic lung volume reduction.
PROCEDURE: Under moderate sedation, the flexible bronchoscope was introduced. The upper airways were unremarkable. Upon inspection of the LLL, severe emphysematous changes were noted. Endobronchial valves were deployed into the target segments: LB6 (4.0mm), LB8 (4.0mm), and LB9-10 (5.5mm). 
OUTCOME: Complete lobar occlusion was visually confirmed with excellent valve seating. There were no immediate complications."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "bronchoscopic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "flexible bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 1)},
    {"label": "DEV_VALVE", **get_span(text_2, "Endobronchial valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB6", 1)},
    {"label": "DEV_VALVE", **get_span(text_2, "4.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB8", 1)},
    {"label": "DEV_VALVE", **get_span(text_2, "4.0mm", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB9-10", 1)},
    {"label": "DEV_VALVE", **get_span(text_2, "5.5mm", 1)},
]
BATCH_DATA.append({"id": "45678912_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Case 3: 45678912_syn_3
# ==========================================
text_3 = """Service: Bronchoscopy with placement of bronchial valves (31647).
Target: Left Lower Lobe (Initial Lobe).
Technique: Flexible bronchoscope inserted. Target segments LB6, LB8, and LB9-10 id[REDACTED]. Delivery catheter used to place 4.0mm and 5.5mm valves. 
Verification: Complete occlusion verified visually. 
Medical Necessity: Treatment of severe heterogeneous emphysema."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "DEV_VALVE", **get_span(text_3, "bronchial valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Left Lower Lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Flexible bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LB6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LB8", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LB9-10", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Delivery catheter", 1)},
    {"label": "DEV_VALVE", **get_span(text_3, "4.0mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_3, "5.5mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_3, "valves", 2)},
]
BATCH_DATA.append({"id": "45678912_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Case 4: 45678912_syn_4
# ==========================================
text_4 = """Procedure Note
Attending: Dr. Park
Resident: [REDACTED]
Patient: [REDACTED]
Procedure Steps:
1. Moderate sedation induced.
2. Scope inserted via oral route.
3. Anatomy reviewed; LLL targeted.
4. Valves placed in LB6, LB8, LB9-10.
5. Good seal confirmed.
Plan: Admit for observation."""

entities_4 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "DEV_VALVE", **get_span(text_4, "Valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB8", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB9-10", 1)},
]
BATCH_DATA.append({"id": "45678912_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Case 5: 45678912_syn_5
# ==========================================
text_5 = """procedure note ebv placement patient maria rodriguez 72yo we did the bronch today for the emphysema lll mainly. used moderate sedation versed fentanyl. went in normal upper airways lll looked bad emphysema. put valves in lb6 lb8 and the 9-10 segment. 4.0 and 5.5 sizes. looks like a good seal occlusion is complete no issues. chest xray next and admit thanks."""

entities_5 = [
    {"label": "DEV_VALVE", **get_span(text_5, "ebv", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lll", 1)},
    {"label": "MEDICATION", **get_span(text_5, "versed", 1)},
    {"label": "MEDICATION", **get_span(text_5, "fentanyl", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lll", 2)},
    {"label": "DEV_VALVE", **get_span(text_5, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lb6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lb8", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "9-10 segment", 1)},
    {"label": "DEV_VALVE", **get_span(text_5, "4.0", 1)},
    {"label": "DEV_VALVE", **get_span(text_5, "5.5", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "chest xray", 1)},
]
BATCH_DATA.append({"id": "45678912_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Case 6: 45678912_syn_6
# ==========================================
text_6 = """The patient, a 72-year-old female with severe heterogeneous emphysema, underwent flexible bronchoscopy with EBV placement. Moderate sedation was used. Access was oropharyngeal. Findings included normal upper airways and severe emphysematous changes in the LLL. Interventions consisted of placing a 4.0mm EBV in LB6, a 4.0mm EBV in LB8, and a 5.5mm EBV in LB9-10. All showed a good seal. The outcome was successful complete LLL occlusion with no complications. Post-op plan includes CXR and admission for observation."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "EBV", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "4.0mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "EBV", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB6", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "4.0mm", 2)},
    {"label": "DEV_VALVE", **get_span(text_6, "EBV", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB8", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "5.5mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "EBV", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB9-10", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 2)},
    {"label": "PROC_METHOD", **get_span(text_6, "CXR", 1)},
]
BATCH_DATA.append({"id": "45678912_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Case 7: 45678912_syn_7
# ==========================================
text_7 = """[Indication]
Severe heterogeneous emphysema, LLL predominant.
[Anesthesia]
Moderate (Versed/Fentanyl).
[Description]
FB performed. LLL targeted. Valves placed in LB6, LB8, LB9-10. Good seal and complete occlusion achieved.
[Plan]
CXR, admit for observation."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Versed", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Fentanyl", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "FB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 2)},
    {"label": "DEV_VALVE", **get_span(text_7, "Valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB8", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB9-10", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "CXR", 1)},
]
BATCH_DATA.append({"id": "45678912_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Case 8: 45678912_syn_8
# ==========================================
text_8 = """We brought [REDACTED] procedure room for her scheduled valve placement. After achieving moderate sedation, we advanced the bronchoscope. The left lower lobe showed significant disease. We proceeded to place valves in the LB6, LB8, and LB9-10 segments. We were able to confirm a good seal on all valves, resulting in complete occlusion of the lobe. She tolerated the procedure well."""

entities_8 = [
    {"label": "DEV_VALVE", **get_span(text_8, "valve", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left lower lobe", 1)},
    {"label": "DEV_VALVE", **get_span(text_8, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "LB6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "LB8", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "LB9-10", 1)},
    {"label": "DEV_VALVE", **get_span(text_8, "valves", 2)},
]
BATCH_DATA.append({"id": "45678912_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Case 9: 45678912_syn_9
# ==========================================
text_9 = """Operation: FB with EBV implantation.
Dx: Severe heterogeneous emphysema.
Findings: LLL severe changes.
Actions: Implantation of 4.0mm EBV in LB6, 4.0mm in LB8, and 5.5mm in LB9-10. Complete obstruction achieved.
Result: Successful LLL isolation, no adverse events."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "FB", 1)},
    {"label": "DEV_VALVE", **get_span(text_9, "EBV", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "DEV_VALVE", **get_span(text_9, "4.0mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_9, "EBV", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB6", 1)},
    {"label": "DEV_VALVE", **get_span(text_9, "4.0mm", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB8", 1)},
    {"label": "DEV_VALVE", **get_span(text_9, "5.5mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB9-10", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 2)},
]
BATCH_DATA.append({"id": "45678912_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Case 10: 45678912
# ==========================================
text_10 = """PROCEDURE NOTE: EBV PLACEMENT
Date: [REDACTED]  
Patient: [REDACTED] | DOB: [REDACTED] | Age: 72 | MRN: [REDACTED]
Institution: [REDACTED]
Physician: James Park, MD

Dx: Severe heterogeneous emphysema, LLL predominant

Procedure: FB with EBV placement
Sedation: Moderate (Versed/Fentanyl)
Access: Oropharyngeal

Findings:
- Normal upper airways
- LLL: Severe emphysematous changes
- Target segments: LB6, LB8-10

Interventions:
LB6: 4.0mm EBV - good seal
LB8: 4.0mm EBV - good seal  
LB9-10: 5.5mm EBV - good seal

Outcome: Successful complete LLL occlusion, no complications
Post-op: CXR, admit for observation

James Park, MD
UCSF Interventional Pulmonology"""

entities_10 = [
    {"label": "DEV_VALVE", **get_span(text_10, "EBV", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "FB", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "EBV", 2)},
    {"label": "MEDICATION", **get_span(text_10, "Versed", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB8-10", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB6", 2)},
    {"label": "DEV_VALVE", **get_span(text_10, "4.0mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "EBV", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB8", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "4.0mm", 2)},
    {"label": "DEV_VALVE", **get_span(text_10, "EBV", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9-10", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "5.5mm", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "EBV", 5)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "CXR", 1)},
]
BATCH_DATA.append({"id": "45678912", "text": text_10, "entities": entities_10})


# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)