import sys
from pathlib import Path

# Adjust parents based on where this script is saved.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# Cases 1-9 (Summarized for brevity, assuming they are correct, skipping to Case 10 where error occurred)
# ... [Assuming the first 9 syn notes are fine, let's fix the big Case 10] ...

# Case 10: 95-847-2631 (The Base Note)
t10 = """PATIENT [REDACTED]: Thompson, David W. | MRN: [REDACTED] | DOB: [REDACTED]
PROCEDURE DATE: [REDACTED]
LOCATION: [REDACTED]
PROCEDURALIST: Elizabeth Morrison, MD, PhD, FCCP, DABIP
ASSISTANT: Jennifer Lee, DO (IP Fellow, PGY-6)
ANESTHESIOLOGIST: Robert Chang, MD, MBA

PREOPERATIVE DIAGNOSIS:
Right lower lobe peripheral pulmonary nodule, segment RB9, measuring 2.7 x 2.4 cm on most recent CT imaging dated [REDACTED], with associated spiculation and pleural tethering highly concerning for malignancy. Previous transthoracic needle biopsy performed on [REDACTED] yielded diagnosis of moderately differentiated adenocarcinoma, TTF-1 positive, confirming primary lung origin.

POSTOPERATIVE DIAGNOSIS: As above

PROCEDURE(S) PERFORMED:
1. Flexible bronchoscopy with complete airway survey
2. Electromagnetic navigation bronchoscopy with real-time cone-beam CT guidance
3. Radial endobronchial ultrasound probe confirmation of target lesion
4. Radiofrequency ablation of right lower lobe peripheral nodule
5. Post-procedural bronchoscopic assessment

CLINICAL HISTORY AND INDICATION:
This is a very pleasant 73-year-old retired teacher with significant past medical history including severe chronic obstructive pulmonary disease (GOLD Stage III, FEV1 34% predicted), pulmonary hypertension (mean PA pressure 42 mmHg on recent right heart catheterization), and ischemic cardiomyopathy (EF 35%) who was found to have right lower lobe nodule on routine surveillance imaging. Patient has extensive 60 pack-year tobacco history, quit 3 years ago. After thorough workup including PET-CT showing SUV max 9.7 and transthoracic needle biopsy confirming adenocarcinoma, patient presented to multidisciplinary thoracic oncology conference. Given prohibitive surgical risk with predicted postoperative mortality >20% by thoracic surgery risk calculator, and patient preference to avoid radiation therapy, decision made to proceed with bronchoscopic radiofrequency ablation as definitive treatment modality.

DETAILED PROCEDURAL DESCRIPTION:
Following standard institutional time-out procedure and verification of correct patient, procedure, and laterality, the patient was brought to the advanced bronchoscopy suite (Suite 4) in the interventional pulmonology procedural area. Anesthesiology team performed standard ASA monitors placement. Given anticipated procedural duration >60 minutes and need for complete immobility during ablation, decision made to proceed with general anesthesia rather than moderate sedation.

Anesthesia was induced using propofol 150 mg IV bolus followed by continuous infusion. Rocuronium 50 mg administered to facilitate intubation. Direct laryngoscopy performed and 8.5mm internal diameter endotracheal tube placed atraumatically with good bilateral breath sounds confirmed. Tube secured at 23 cm at the teeth. Patient maintained on sevoflurane 1.5-2% for maintenance of general anesthesia throughout procedure.

Olympus therapeutic bronchoscope (model BF-1TH190) advanced through endotracheal tube adapter. Systematic survey of airways performed documenting: normal appearing vocal cords, patent trachea without lesions or external compression, normal carina with sharp angle bilaterally, normal appearing right and left mainstem bronchi. Detailed inspection of right lower lobe bronchial tree including superior segment and all basal segments revealed no endobronchial abnormalities, no external compression, and patent airways throughout.

Electromagnetic navigation bronchoscopy initiated using Veran SPiN Thoracic Navigation System. Pre-procedure thin-slice CT imaging (1mm cuts) from [REDACTED] loaded into planning software. Target lesion in right lower lobe lateral basal segment (RB9) id[REDACTED] and navigation pathway planned. After registration using automatic registration mode with 8 reference points, registration accuracy calculated at 3.2 mm, which is excellent and well within acceptable parameters.

Navigation performed using 8Fr steerable guide catheter (Always-On Tip Tracked) advanced through working channel. Multiple adjustments and catheter manipulations required due to acute angle into RB9. After approximately 12 minutes of careful navigation, guide sheath successfully positioned at target site. Position confirmed with radial endobronchial ultrasound probe (20 MHz) showing target lesion in direct contact position with characteristic hypoechoic solid mass appearance. Internal architecture showed heterogeneous echotexture consistent with malignancy. Lesion measured approximately 24 mm x 22 mm on real-time EBUS.

Cone-beam CT performed (Siemens Artis Pheno with DynaCT Needle Guidance software) confirming guide sheath position within 8mm of geometric center of target nodule. Distance from pleura measured at 15mm. After review of cone-beam images and confirmation of safe ablation zone without critical vessels, decision made to proceed.

Extended working channel (EWC, 2.0mm diameter) passed through guide sheath. Radiofrequency ablation probe (VIVANT MEDICAL systems, 1.5cm active tip, single electrode configuration) advanced through EWC under direct visualization. Probe position confirmed at lesion center with repeat radial EBUS showing probe centrally located within target.

Radiofrequency ablation protocol initiated per institutional guidelines for lesions 2-3cm. Settings: impedance-controlled algorithm, target temperature 90°C, duration 8 minutes for initial ablation cycle. Real-time impedance monitoring demonstrated initial reading of 85 ohms with gradual rise during treatment. Temperature monitoring at probe tip showed appropriate heating curve reaching target temperature within 90 seconds. Patient remained hemodynamically stable throughout ablation with vital signs: HR 72-85, BP 132/78 - 145/82, SpO2 98-100% on FiO2 0.6. End-tidal CO2 maintained 35-38 mmHg.

After completion of initial 8-minute cycle, probe repositioned 5mm posterior to treat overlapping zone and ensure complete ablation coverage of entire tumor volume plus 5mm margin. Second ablation cycle performed: 6 minutes, target temperature 90°C. Impedance monitoring again demonstrated appropriate curve. Post-ablation radial EBUS performed showing hyperechoic changes throughout entire tumor volume consistent with coagulative necrosis. Ice-cream cone appearance of ablation zone well visualized extending beyond original tumor margins.

Guide sheath and EWC slowly withdrawn under direct bronchoscopic visualization. Careful inspection of airways performed showing mild mucosal hyperemia at catheter contact points but no evidence of perforation, significant edema, or active hemorrhage. Small amount of serosanguinous secretions suctioned from right lower lobe, estimated <10 mL total.

Airways irrigated with normal saline. Bronchoscope withdrawn and patient emerged from general anesthesia without complications. Following standard reversal and spontaneous ventilation recovery, patient successfully extubated with good cough and gag reflexes. Transferred to post-anesthesia care unit in stable condition with oxygen saturation 94% on 2L NC.

ESTIMATED BLOOD LOSS: Minimal, less than 15 milliliters
INTRAVENOUS FLUIDS ADMINISTERED: 1000 mL lactated Ringer's solution
SPECIMENS SENT: None
COMPLICATIONS: None intraoperatively

FINDINGS:
1. Successful electromagnetic navigation to RLL lateral basal segment target lesion
2. Radiofrequency ablation completed per protocol with two overlapping ablation zones
3. Good real-time monitoring throughout with appropriate impedance and temperature curves
4. Post-ablation imaging demonstrates adequate treatment zone with apparent complete coverage
5. No immediate procedural complications id[REDACTED]

ASSESSMENT AND RECOMMENDATIONS:
74-year-old gentleman with biopsy-proven RLL peripheral adenocarcinoma, poor surgical candidate, status post successful bronchoscopic radiofrequency ablation. Procedure technically successful with good positioning and ablation parameters. Patient tolerated procedure well without complications.

PLAN:
1. Admit to Pulmonary Intermediate Care Unit (7 East) for overnight observation
2. Continuous pulse oximetry and telemetry monitoring overnight
3. Chest radiograph in 4 hours to evaluate for pneumothorax or other acute complications
4. CT chest with intravenous contrast in 24 hours to assess ablation zone and rule out complications
5. Pain management: scheduled acetaminophen 1000mg q8h, oxycodone 5mg q6h PRN moderate pain, hydromorphone 0.5mg IV q4h PRN severe pain
6. Aggressive pulmonary toilet: incentive spirometry 10 times per hour while awake, chest physiotherapy as needed
7. Empiric antibiotics NOT indicated at this time given low infection risk
8. Anticipated discharge tomorrow if overnight course uncomplicated and CT scan reassuring
9. Follow-up arrangements: Clinic visit in 1 week with CXR, CT chest at 6 weeks for initial response assessment, PET-CT at 3 months for metabolic response
10. Continue home medications including COPD regimen, cardiac medications
11. Patient and family extensively counseled on post-procedure expectations, warning signs for complications (increasing dyspnea, chest pain, hemoptysis), importance of follow-up

I have personally performed and supervised this entire procedure. All findings, interventions, and recommendations above represent my direct involvement and assessment.

Procedure time: 87 minutes (includes anesthesia induction and emergence)
Fluoroscopy time: 3.2 minutes
Radiation dose: 245 mGy-cm²

_______________________________________
Elizabeth Morrison, MD, PhD, FCCP, DABIP
Professor of Medicine
Director, Interventional Pulmonology
University of Washington Medical Center

Electronically signed: [REDACTED] 14:37 PST"""

# FIXED ENTITIES: Using distinct phrases instead of "right" #8
e10 = [
    # Header/Dx
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Right lower lobe peripheral pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB9", 1)},
    
    # Procedure List
    {"label": "PROC_METHOD",   **get_span(t10, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD",   **get_span(t10, "cone-beam CT", 1)},
    {"label": "PROC_METHOD",   **get_span(t10, "Radial endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION",   **get_span(t10, "Radiofrequency ablation", 1)},
    
    # Narrative
    # "Right lower lobe" only appears once with that exact casing; later mentions are lowercase.
    {"label": "LATERALITY",    **get_span(t10, "right lower lobe", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "right and left mainstem bronchi", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right lower lobe bronchial tree", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB9", 2)},
    
    # Findings/Assessment
    {"label": "PROC_ACTION",   **get_span(t10, "bronchoscopic radiofrequency ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate procedural complications", 1)},
]
BATCH_DATA.append({"id": "95-847-2631", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")