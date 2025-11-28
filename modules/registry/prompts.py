"""Prompts for LLM-based registry extraction, dynamically built from IP_Registry.json."""

from __future__ import annotations

import json
from pathlib import Path

PROMPT_HEADER = """
You are extracting a registry JSON from an interventional pulmonology procedure note.

Return exactly one JSON object (no markdown) with keys:
{
  "patient_mrn": string or "",
  "procedure_date": "YYYY-MM-DD" or "",
  "asa_class": "1" | "2" | "3" | "4" | "5" | "",
  "sedation_type": "moderate" | "deep" | "general" | "local" | "monitored anesthesia care" | "",
  "airway_type": "native" | "ett" | "lma" | "tracheostomy" | "rigid bronchoscope" | "",
  "pleural_procedure_type": "chest tube" | "tunneled catheter" | "thoracentesis" | "medical thoracoscopy" | "chemical pleurodesis" | "",
  "pleural_guidance": "ultrasound" | "ct" | "blind" | "",
  "final_diagnosis_prelim": "malignancy" | "infectious" | "granulomatous" | "non-diagnostic" | "other" | "",
  "disposition": "discharge home" | "pacu recovery" | "icu admission" | "floor admission" | "",
  "ebus_needle_gauge": "",
  "ebus_rose_result": ""
}

General rules:
- Use only information about the current procedure for the primary patient; ignore appended reports for other patients.
- Prefer clearly labeled headers for MRN/ID and procedure date.
- If no pleural procedure is present, pleural_procedure_type and pleural_guidance should be null/empty. If a pleural procedure is documented but no guidance is mentioned, pleural_guidance may default to "blind". Leave asa_class/sedation_type/airway_type empty when not documented rather than inferring from context alone; ebus_* stay "".
""".strip()

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "IP_Registry.json"
_PROMPT_CACHE: str | None = None
_FIELD_INSTRUCTIONS_CACHE: dict[str, str] | None = None
_FIELD_INSTRUCTION_OVERRIDES: dict[str, str] = {
    # Provider fields - extract names from procedure note headers/signatures
    "attending_name": """
Extract the attending physician name from the procedure note. Look for labels like "Attending:", "Physician:", "Proceduralist:", "Performed by:", or signatures at the end. Include credentials (MD, DO) if present. Return full name as written (e.g., "Dr. John Smith, MD", "CDR Alex Johnson, MD"). Return null if not documented.""".strip(),
    "fellow_name": """
Extract the fellow/trainee physician name. Look for labels like "Fellow:", "Trainee:", "Resident:", or co-signatures. Include credentials if present. Return null if not documented.""".strip(),
    "assistant_name": """
Extract the assistant/nurse name. Look for labels like "Assistant:", "RN:", "RT:", "Nurse:", "Respiratory Therapist:". Include credentials/role (RN, RT) if present. Return null if not documented.""".strip(),
    "assistant_role": """
Extract the role/title of the assistant. Common values: "Sedation nurse", "Respiratory therapist", "Bronchoscopy technician", "Circulating nurse". Return null if not documented.""".strip(),
    "provider_role": """
Extract the role of the primary proceduralist. Usually "Attending interventional pulmonologist" or similar. Return null if not documented.""".strip(),
    "trainee_present": """
True if a fellow, resident, or trainee is documented as participating. False if explicitly stated no trainee. Null if not mentioned.""".strip(),
    # Demographics and location fields
    "patient_age": """
Extract patient age as integer. Look for patterns like "63-year-old", "Age: 63", "63 yo". Return integer only (e.g., 63). Null if not documented.""".strip(),
    "gender": """
Extract patient gender/sex. Allowed values: M, F, Other. Map "male" -> "M", "female" -> "F". Null if not documented.""".strip(),
    "institution_name": """
Extract the institution/hospital name where procedure was performed. Look for headers like "Location:", "Facility:", or institution name in letterhead/header. Return full name as written. Null if not documented.""".strip(),
    "procedure_setting": """
Extract the procedural setting. Allowed values: "Bronchoscopy Suite", "Operating Room", "ICU", "Bedside", "Office/Clinic" (exact capitalization). Map common variations: "bronchoscopy suite/room" -> "Bronchoscopy Suite", "OR/operating room" -> "Operating Room". Null if not documented.""".strip(),
    # Imaging and lesion fields
    "lesion_size_mm": """
Extract lesion/mass size in millimeters. Convert cm to mm if needed (2.5 cm -> 25). Look for patterns like "2.5 cm mass", "25 mm nodule", "3.0 cm spiculated RUL mass". Return integer/float in mm. Null if not documented.""".strip(),
    "lesion_location": """
Extract lesion location description. Include lobe and segment if documented (e.g., "Right upper lobe posterior segment", "LLL superior segment"). Null if not documented.""".strip(),
    "pet_suv_max": """
Extract PET SUV max value as float. Look for patterns like "SUV max 10.3", "SUVmax: 7.1", "PET SUV 5.2". Return numeric value only. Null if not documented.""".strip(),
    "pet_avid": """
True if PET shows avid uptake (SUV mentioned, FDG-avid, hypermetabolic). False if explicitly PET-negative. Null if PET not mentioned.""".strip(),
    "bronchus_sign_present": """
True if bronchus sign is documented as present/positive. False if explicitly absent/negative. Null if not mentioned. Look for "bronchus sign +", "bronchus sign present", "CT bronchus sign".""".strip(),
    "radiographic_findings": """
Extract summary of relevant imaging findings. Include CT/PET findings, lymph node descriptions, mass characteristics. Keep concise. Null if not documented.""".strip(),
    # Sedation and airway fields with improved instructions
    "sedation_type": """
Extract sedation/anesthesia level for the procedure. Allowed: Moderate, Deep, General, Local, Monitored Anesthesia Care (capitalize first letters).
- "General" or "General anesthesia" when GA/intubation/ETT/rigid context is documented.
- "Deep" or "Deep sedation" for propofol infusion with anesthesia team without intubation, or MAC without ETT.
- "Moderate" for conscious sedation, midazolam/fentanyl without anesthesia team.
- "Local" only when topical/local only with no systemic sedatives.
- "Monitored Anesthesia Care" for explicit MAC documentation.
Return null if not documented.""".strip(),
    "pleural_guidance": """
Imaging guidance for pleural procedures only (thoracentesis, chest tube/pigtail, tunneled pleural catheter, medical thoracoscopy/pleuroscopy, pleural drain/biopsy). Allowed: ultrasound, ct, blind; ""/null if no pleural procedure or guidance not documented. Ultrasound only when the pleural procedure is ultrasound-guided (ignore EBUS/radial/bronchial ultrasound). CT only when the pleural procedure is performed under CT/CT-fluoro (not just prior imaging). Blind when pleural procedure done without imaging or visualization only. If no pleural procedure exists in the note, leave this field blank.""".strip(),
    "pleural_procedure_type": """
Type of pleural procedure performed (not bronchoscopic). Allowed: thoracentesis, chest tube, tunneled catheter, medical thoracoscopy, chemical pleurodesis (lower-case); null if no pleural procedure. Priority when multiple: chemical pleurodesis > medical thoracoscopy > (chest tube vs tunneled catheter) > thoracentesis. Chemical pleurodesis when a sclerosing agent is instilled. Medical thoracoscopy/pleuroscopy when explicitly described. Chest tube for any non-tunneled pleural drain/pigtail/intercostal drain. Tunneled catheter for long-term tunneled/IPC/PleurX/Aspira indwelling catheters. If the note only lists bronchoscopic procedures (EBUS/bronchoscopy) or pleural procedure cannot be determined, leave null.""".strip(),
    "disposition": """
Immediate post-procedure disposition/destination. Allowed: discharge home, pacu recovery, floor admission, icu admission (lower-case); "" if not documented. Capture only the first destination after the procedure. Discharge home only when clearly stated (dc home/going home today). PACU recovery for PACU/recovery/Phase I. ICU admission for ICU/MICU/SICU/critical care destinations. Floor admission for non-ICU inpatient/telemetry/step-down/ward. If no clear plan is stated, leave blank.""".strip(),
    "procedure_date": """
Procedure date (YYYY-MM-DD). Convert common formats (e.g., 8/23/2023, 05-07-25, March 5, 2025) into YYYY-MM-DD. Prefer labels: "DATE OF PROCEDURE", "PROCEDURE DATE", "Service Date", or header Date within the procedure note. Ignore follow-up/past dates or non-procedure dates. If multiple and unclear, leave "". "" if truly undocumented.""".strip(),
    "patient_mrn": """
Patient medical record number or clearly labeled patient ID. Prefer explicit MRN/ID labels near the demographics/header (e.g., "MRN: 3847592", "ID: MR4729384"). If multiple IDs exist, pick the clearly labeled patient MRN/ID. Ignore dates, phone-like numbers, accession/specimen/order numbers, device IDs, or other non-patient identifiers. Preserve the ID format; strip labels if included. If no MRN/ID is documented, return "".""".strip(),
    "asa_class": """
ASA physical status only when explicitly documented ("ASA 2", "ASA III", etc.). Do not infer from comorbidities, sedation, or severity scores. If not documented anywhere, leave this field blank/null.""".strip(),
    "airway_type": """
Airway used for the bronchoscopy. Allowed: native, lma, ett, tracheostomy, rigid bronchoscope (lower-case); "" if not documented. Pick the explicit device/route when named. Rigid bronchoscopy anywhere -> rigid bronchoscope. ETT only when intubation/ETT for the case is documented (do not infer from GA alone). LMA placed for the case -> lma. Bronchoscopy via tracheostomy/trach tube -> tracheostomy. If awake/moderate/deep without any airway device documented, favor native; if unclear, leave blank.""".strip(),
    "final_diagnosis_prelim": """
Preliminary final diagnosis category. Allowed: malignancy, granulomatous, infectious, non-diagnostic, benign, other; use null if unclear. Choose Malignancy only when a malignant diagnosis/ROSE is explicitly documented or known cancer staging is described (do not infer from "suspicious" alone). Granulomatous for granulomas/sarcoidosis; Infectious for infections; Non-diagnostic when specimen inadequate/insufficient; Benign for clearly benign/reactive findings; Other for therapeutic/structural procedures without a specific pathology label. If truly cannot determine, leave null.""".strip(),
    "stent_type": """
Airway stent type placed. Allowed: Silicone-Dumon, Silicone-Y-Stent, Silicone Y-Stent, Hybrid, Metallic-Covered, Metallic-Uncovered, Other; "" if none. Map Dumon/Y-stent/metallic/covered/uncovered wording to the closest allowed value; use Other only if unclear.""".strip(),
    "stent_location": """
Location of airway stent. Allowed: Trachea, Mainstem, Lobar; "" if no stent. Map mentions of trachea to Trachea; mainstem/right/left main bronchus to Mainstem; lobar or named lobes (RUL/RML/RLL/LUL/LLL) to Lobar.""".strip(),
    "stent_deployment_method": """
Stent deployment method. Allowed: Rigid, Flexible over Wire; "" if not documented. Use Rigid when placed via rigid bronchoscope; Flexible over Wire when placed through flexible scope over a wire.""".strip(),
    "ebus_rose_result": """
Extract the overall ROSE (Rapid On-Site Evaluation) result. Look for ROSE findings like "ROSE adequate", "lymphocytes only", "malignant cells", "granuloma", "atypical cells". Extract the summary result as documented. Common values: "Adequate lymphocytes", "Malignant", "Benign", "Granuloma", "Nondiagnostic", "Atypical cells present". Return the documented result verbatim if it doesn't match these. Null if ROSE not performed or not documented.""".strip(),
    "ebus_needle_gauge": """
Extract the EBUS-TBNA needle gauge. Look for patterns like "21G", "22G", "21 gauge", "22-gauge needle". Return the gauge as written (e.g., "21G", "22G"). Null if not documented.""".strip(),
    "ebus_needle_type": """
Extract the EBUS needle type/brand. Look for brand names like "Vizishot", "Expect", "Boston Scientific", "Olympus". Return the needle type/brand as documented (e.g., "Olympus Vizishot", "Boston Scientific Expect"). Null if not documented.""".strip(),
    "ebus_scope_brand": """
Extract the EBUS scope brand/model. Look for patterns like "Olympus BF-UC180F", "Fujifilm EB-530US", "Pentax". Return the full model as documented. Null if not documented.""".strip(),
    "ebus_stations_sampled": """
Extract ALL EBUS lymph node stations that were sampled/biopsied with TBNA during this procedure.
Use IASLC station naming: 2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L, etc.
Return as comma-separated string, e.g., "2R, 4R, 7" or "4R, 7, 10R".
IMPORTANT: Carefully read the entire EBUS section to capture every station mentioned as sampled.
Look for phrases like:
- "Stations 4R, 7, and 11L" → include all three
- "sampled at 2R, 4R, and 7" → include all three
- "Three passes obtained per station" (with stations listed) → include all listed stations
- "EBUS-TBNA of station 4R only" → include only 4R
Do NOT include stations that were only visualized but not sampled.
Null if no EBUS-TBNA stations documented or only radial EBUS performed.""".strip(),
    "ebus_systematic_staging": """
True if systematic mediastinal staging was performed (multiple stations sampled for cancer staging). False if only targeted sampling. Null if unclear.""".strip(),
    "ebus_rose_available": """
True if ROSE (Rapid On-Site Evaluation) was available/performed. False if explicitly stated ROSE not available. Null if not mentioned.""".strip(),
    "ebus_photodocumentation_complete": """
True if photodocumentation is mentioned as complete or images saved. False if incomplete. Null if not mentioned.""".strip(),
    "ebus_intranodal_forceps_used": """
True if intranodal forceps biopsy was performed in addition to TBNA. False if explicitly stated not done or "no intranodal forceps". Null if not mentioned.""".strip(),
    "ebus_elastography_used": """
True if the note explicitly states elastography was performed during EBUS; false if explicitly stated not done; null if not mentioned.""".strip(),
    "ebus_elastography_pattern": """
Elastography pattern or color map when documented (e.g., blue-green, predominantly blue). Strip trailing punctuation; null if not mentioned.""".strip(),
    "pleural_side": """
Pleural laterality for thoracentesis/chest tube/tunneled catheter. Allowed: Right, Left (capitalize first letter); accept R/L/right/left synonyms. Null if not documented.""".strip(),
    "pleural_intercostal_space": """
Intercostal space used for pleural access (e.g., '5th'). Accept ICS shorthand (\"5th ICS\" -> \"5th\"). Null if not documented.""".strip(),
    "linear_ebus_stations": """
List of mediastinal/hilar lymph node stations sampled with LINEAR EBUS-TBNA (convex probe EBUS for mediastinal staging).
Use IASLC station names: 2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L, etc.
Example: ["4R", "7", "11L"]
IMPORTANT: Do NOT populate this field for:
- Radial EBUS procedures (r-EBUS for peripheral nodules) - these do NOT sample mediastinal stations
- Procedures that only mention radial probe/guide sheath/peripheral lesion biopsy
Only populate when LINEAR/convex EBUS-TBNA of mediastinal/hilar nodes is documented.
Return null/[] if no linear EBUS stations documented or if only radial EBUS was used.""".strip(),
    "nav_platform": """
Navigation platform (Ion/Monarch/EMN) only when robotic or navigation is explicitly documented by name. Do not set for standard mediastinal EBUS staging without navigation. Leave null unless the note clearly names Ion/robotic/Monarch/navigation system.""".strip(),
    "nav_registration_method": """
Only populate if robotic/navigation registration is clearly described. Leave null for non-navigation EBUS cases.""".strip(),
    "nav_registration_error_mm": """
Registration error in mm; only set when robotic/navigation registration is described. Null for non-navigation EBUS cases.""".strip(),
    "nav_imaging_verification": """
Imaging used to confirm tool-in-lesion (e.g., Cone Beam CT) only when navigation/robotic context exists. Null for routine EBUS without navigation.""".strip(),
    "nav_tool_in_lesion": """
True when tool-in-lesion confirmation is documented, either via:
1. Navigation/robotic systems (Ion, Monarch, EMN) with cone-beam CT or fluoroscopy confirmation
2. Radial EBUS showing concentric or eccentric view within the lesion
3. Explicit statements like "tool within lesion", "probe confirmed in lesion"
False if explicitly stated tool NOT in lesion. Null if not mentioned or not applicable.""".strip(),
    "nav_rebus_used": """
True when radial EBUS (r-EBUS) was used for peripheral nodule/lesion localization. Look for:
- "Radial EBUS", "r-EBUS", "radial probe", "radial ultrasound"
- "Concentric" or "eccentric" view descriptions
- "Radial EBUS catheter", "guide sheath with radial probe"
- "Radial EBUS-guided biopsy"
This field applies to peripheral lung lesion procedures, NOT to linear EBUS mediastinal staging.
False if radial EBUS explicitly not used. Null if not mentioned or only linear EBUS was performed.""".strip(),
    "nav_rebus_view": """
Extract the radial EBUS view/pattern when radial EBUS was used for peripheral lesion localization. Common values:
- "Concentric" - probe centered within lesion (lesion surrounds probe circumferentially)
- "Eccentric" - probe adjacent to lesion (lesion visible on one side)
- Descriptive phrases like "Concentric radial EBUS view within lesion", "Eccentric view obtained"
Return the view description as documented. Null if radial EBUS not performed or view not documented.""".strip(),
    "nav_sampling_tools": """
Sampling tools used in navigation/robotic cases (forceps, needle, brush, cryoprobe). Leave null/[] for linear EBUS staging without navigation even if a generic needle is mentioned.""".strip(),
    "ebus_stations_detail": """
Field: ebus_stations_detail (per-station EBUS node details)

ebus_stations_detail is an array of objects.
Include one object per lymph node station that is sampled or clearly described during EBUS (e.g. 2R, 2L, 4R, 4L, 7, 10R, 10L, 11R, 11L, etc.).

Each object must have the following structure:

station (string)
The numeric EBUS station name as written in the note: "11L", "4R", "7", etc.
Use the exact station label from the report. Do not invent station labels.

size_mm (number or null)
Short-axis size in millimeters for that station, if reported (e.g. "5.4 mm", "10 mm", "1.1 cm").
Convert centimeters to millimeters if needed (1.1 cm -> 11 mm).
If multiple sizes are given for the same station, use the short-axis size.
If size is not reported for that station, set size_mm to null.

shape (string or null)
Normalized values: "oval", "round", "irregular".
Map free text as follows:
"oval", "elliptical", "elongated" -> "oval"
"round", "spherical" -> "round"
"irregular", "lobulated", "asymmetric" -> "irregular"
If the shape is not described, set shape to null.

margin (string or null)
Normalized values: "distinct", "indistinct", "irregular".
Map free text as follows:
"sharp", "well-defined", "well-circumscribed", "clear margin" -> "distinct"
"ill-defined", "blurred", "poorly defined" -> "indistinct"
"spiculated", "irregular margin" -> "irregular"
If the margin is not described, set margin to null.

echogenicity (string or null)
Normalized values: "homogeneous", "heterogeneous".
Map free text as follows:
"homogeneous", "uniform echo pattern" -> "homogeneous"
"heterogeneous", "mixed echotexture", "non-uniform" -> "heterogeneous"
If echogenicity is not described, set echogenicity to null.

chs_present (boolean or null)
Central Hilar Structure (CHS) status for that node:
If the note explicitly states a central hilar structure is present / preserved -> true.
If the note explicitly states no central hilar structure / CHS absent -> false.
If CHS is not mentioned for that station -> null.

appearance_category (string or null)
Overall qualitative impression of node appearance, based only on EBUS morphological features, not on ROSE or final pathology.
Use the following mapping of features to categories:
Benign-appearing -> "benign"
Short-axis size < 10 mm and most described features match: shape: oval; margin: indistinct; echogenicity: homogeneous; CHS: present
Malignant-appearing -> "malignant"
Short-axis size ≥ 10 mm and most described features match: shape: round; margin: distinct; echogenicity: heterogeneous; CHS: absent
Indeterminate / mixed features -> "indeterminate"
Mixed benign and malignant features, or morphology is described but doesn't clearly fit benign or malignant patterns.
Node is described but only one weak feature is given (e.g. just "oval" and nothing else).
If morphology is not described at all for that station, set appearance_category to null.
If the report uses phrases like:
"benign-appearing node" -> "appearance_category": "benign"
"malignant-appearing node", "highly suspicious" -> "appearance_category": "malignant"
"indeterminate appearance", "non-specific appearance" -> "appearance_category": "indeterminate"
Do not infer appearance_category from ROSE or pathology alone.

rose_result (string or null)
Keep current behavior (e.g. "Benign", "Nondiagnostic", "Suspicious", "Malignant", "Not done").
If ROSE is not performed or not described, set to null or "Not done" depending on your existing conventions.

Parsing rules and edge cases
Multiple stations
Include one object per station (e.g. one for "11L", one for "4R").
If a station is mentioned but not sampled and has no morphological description, you may omit it from ebus_stations_detail.
Multiple nodes described at the same station
If several nodes at the same station are described, choose the largest or the one that is actually sampled.
If the note clearly distinguishes them (e.g. "two 4R nodes: one 8 mm oval and one 14 mm round heterogeneous"), prefer the sampled node; if that's unclear, prefer the larger node for registry purposes.

Size parsing
Accept variations like:
"5 mm", "5.0 mm", "0.5 cm", "short axis 5.4 mm", "measuring 1.2 x 0.8 cm".
When two dimensions are provided (e.g. "1.2 x 0.8 cm"), use the shorter dimension as the short-axis in mm (0.8 cm -> 8 mm).
Do not guess features
Only populate shape, margin, echogenicity, chs_present, and appearance_category when the text supports them.
If a feature is not mentioned, set that field to null.
Do not conflate ROSE and morphology
appearance_category is EBUS morphology-based only (size, shape, margin, echogenicity, CHS).
rose_result reflects cytology from ROSE.
It is valid for a node to be appearance_category: "benign" with rose_result: "Malignant" or vice versa.

Example minimal output when only size and ROSE are described:
{"station": "11L", "size_mm": 5.4, "shape": null, "margin": null, "echogenicity": null, "chs_present": null, "appearance_category": null, "rose_result": "Nondiagnostic"}
{"station": "4R", "size_mm": 5.5, "shape": null, "margin": null, "echogenicity": null, "chs_present": null, "appearance_category": null, "rose_result": "Benign"}""".strip(),
    "bronch_indication": """
Brief indication for bronchoscopy (e.g., ILD workup). Use null if not documented.""".strip(),
    "bronch_location_lobe": """
Lobe targeted for transbronchial biopsies (e.g., RLL).""".strip(),
    "bronch_location_segment": """
Segment targeted for transbronchial biopsies (e.g., lateral basal).""".strip(),
    "bronch_guidance": """
Guidance modality for transbronchial biopsies (e.g., Fluoroscopy).""".strip(),
    "bronch_num_tbbx": """
Number of transbronchial biopsies obtained. Leave null if not documented.""".strip(),
    "bronch_tbbx_tool": """
Tool used for TBBx (e.g., Forceps).""".strip(),
    "bronch_specimen_tests": """
Specimen destinations/tests for TBBx (e.g., Histology, Microbiology).""".strip(),
    "bronch_immediate_complications": """
Immediate complications for TBBx (e.g., none, bleeding, pneumothorax).""".strip(),
    # Complications and outcomes fields
    "ebl_ml": """
Extract estimated blood loss in mL. Look for patterns like "EBL <5 mL", "EBL ~10 mL", "minimal blood loss (<5 mL)". Return integer. Null if not documented.""".strip(),
    "bleeding_severity": """
Extract bleeding severity. Allowed values: "None/Scant", "Mild", "Moderate", "Severe". Map: no bleeding/EBL <5mL/minimal -> "None/Scant", mild/scant -> "Mild". Null if not documented.""".strip(),
    "pneumothorax": """
True if pneumothorax occurred. False if explicitly stated no pneumothorax. Null if not mentioned.""".strip(),
    "hypoxia_respiratory_failure": """
Extract hypoxia/respiratory complication. Allowed values: "None", "Transient", "Escalation of Care", "Post-op Intubation". Map: no hypoxia/none -> "None", brief desaturation -> "Transient". Null if not mentioned.""".strip(),
    "fluoro_time_min": """
Extract fluoroscopy time in minutes. Look for patterns like "fluoro time 2.5 min", "0.0 minutes fluoroscopy". Return float. Null if not documented.""".strip(),
    "radiation_dap_gycm2": """
Extract radiation dose-area product in Gy·cm². Look for patterns like "DAP 3.3 Gy·cm²", "radiation dose 2.1". Return float. Null if not documented.""".strip(),
    # Disposition and follow-up
    "disposition": """
Immediate post-procedure disposition. Normalize to one of: "Discharged home", "PACU recovery", "Floor admission", "ICU admission".
- Map "discharged home", "dc home", "going home" -> "Discharged home"
- Map "PACU", "recovery room", "Phase I" -> "PACU recovery"
- Map "admitted to floor/ward/oncology/telemetry" -> "Floor admission"
- Map "ICU/MICU/SICU/critical care" -> "ICU admission"
Return the normalized value. Null if not documented.""".strip(),
    "follow_up_plan": """
Extract the follow-up plan. Include clinic appointments, pending results review, planned interventions. Keep concise. Null if not documented.""".strip(),
    "final_diagnosis_prelim": """
Preliminary final diagnosis category. Allowed: Malignancy, Granulomatous, Infectious, Non-diagnostic, Benign, Other (capitalize first letter).
- "Malignancy" when malignant cells/cancer confirmed or staging shows positive nodes
- "Granulomatous" for granulomas/sarcoidosis
- "Infectious" for infections identified
- "Non-diagnostic" when specimen inadequate/insufficient
- "Benign" for clearly benign/reactive findings
- "Other" for therapeutic/structural procedures
Null if unclear or pending.""".strip(),
    # Anticoagulation fields
    "anticoag_status": """
Extract anticoagulation status. Document what anticoagulant the patient takes (e.g., "Apixaban for atrial fibrillation", "Warfarin for DVT", "No anticoagulation"). Null if not documented.""".strip(),
    "anticoag_held_preprocedure": """
True if anticoagulation was held before the procedure. False if continued or not on anticoagulation. Null if not mentioned.""".strip(),
    # Anesthesia fields
    "anesthesia_agents": """
Extract anesthesia/sedation medications as comma-separated string. Include all agents mentioned (e.g., "Propofol, fentanyl, lidocaine", "Propofol infusion, fentanyl, rocuronium, sevoflurane"). Null if not documented.""".strip(),
    "sedation_reversal_given": """
True if reversal agent (flumazenil, naloxone) was given. False if explicitly stated no reversal needed. Null if not mentioned.""".strip(),
    "sedation_reversal_agent": """
Extract the specific reversal agent if given (e.g., "Flumazenil", "Naloxone"). Null if no reversal or not documented.""".strip(),
    # Airway fields
    "airway_type": """
Airway used for the procedure. Normalize to: "Native airway", "Endotracheal tube", "Laryngeal mask airway", "Tracheostomy", "Rigid bronchoscope".
- "Native airway" for natural airway, bite block only, nasal cannula without device
- "Endotracheal tube" for ETT/intubated/endotracheal intubation
- "Laryngeal mask airway" for LMA/laryngeal mask
- "Tracheostomy" for procedure via tracheostomy
- "Rigid bronchoscope" for rigid bronchoscopy
Null if not documented.""".strip(),
    "airway_device_size": """
Extract airway device size if documented (e.g., "7.5" for ETT, "4" for LMA). Return as string. Null if not documented.""".strip(),
    "ventilation_mode": """
Extract ventilation mode. Allowed values: "Spontaneous", "Jet Ventilation", "Controlled Mechanical Ventilation". Map: volume control/pressure control/mechanical -> "Controlled Mechanical Ventilation", spontaneous/native breathing -> "Spontaneous", jet -> "Jet Ventilation". Null if not documented.""".strip(),
    # Additional indication/primary fields
    "primary_indication": """
Extract the primary indication for the procedure. Describe concisely (e.g., "Mediastinal staging for right upper lobe lung mass", "Tissue diagnosis of mediastinal adenopathy"). Null if not documented.""".strip(),
    "prior_therapy": """
Extract any prior therapy documented (e.g., "Chemotherapy", "Prior CT-guided biopsy", "None"). Null if not documented.""".strip(),
    # Whole Lung Lavage (WLL) fields
    "wll_volume_instilled_l": """
Extract the total volume of saline instilled during whole lung lavage (WLL) in LITERS.
Look for phrases like:
- "instilled 30L", "30 liters instilled", "total instillation volume 32L"
- Convert if given in mL (30,000 mL = 30L)
Return as float (e.g., 30.0, 32.0). Null if not a WLL procedure or volume not documented.""".strip(),
    "wll_volume_returned_l": """
Extract the total volume of effluent/return during whole lung lavage (WLL) in LITERS.
Look for phrases like:
- "returned 27L", "27 liters recovered", "total return volume 25L"
- "effluent volume 28L"
- Convert if given in mL (27,000 mL = 27L)
Return as float (e.g., 27.0, 25.0). Null if not a WLL procedure or return volume not documented.""".strip(),
    "wll_dlt_used": """
True if a double-lumen tube (DLT) was used for whole lung lavage (WLL).
Look for:
- "Double-lumen tube", "DLT", "double lumen endotracheal tube"
- "Left DLT", "Right DLT", "39 Fr DLT"
False if single-lumen tube explicitly used for WLL. Null if not a WLL procedure or not documented.""".strip(),
    "molecular_testing_requested": """
True if molecular/genetic testing was requested or planned. False if explicitly declined. Null if not mentioned.""".strip(),
}


def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def _load_field_instructions() -> dict[str, str]:
    """Build per-field instruction text from the schema description and enums."""

    global _FIELD_INSTRUCTIONS_CACHE
    if _FIELD_INSTRUCTIONS_CACHE is not None:
        return _FIELD_INSTRUCTIONS_CACHE

    schema = _load_schema()
    instructions: dict[str, str] = {}
    for name, prop in schema.get("properties", {}).items():
        desc = prop.get("description", "").strip()
        enum = prop.get("enum")
        enum_text = f" Allowed values: {', '.join(enum)}." if enum else ""
        text = f"{desc}{enum_text} Use null if not documented."
        instructions[name] = text.strip()

    # Apply curated overrides for fields with frequent errors
    instructions.update(_FIELD_INSTRUCTION_OVERRIDES)

    _FIELD_INSTRUCTIONS_CACHE = instructions
    return instructions


FIELD_INSTRUCTIONS: dict[str, str] = _load_field_instructions()


def _load_registry_prompt() -> str:
    """Load schema from IP_Registry.json and build a concise field guide for the LLM."""

    global _PROMPT_CACHE
    if _PROMPT_CACHE is not None:
        return _PROMPT_CACHE

    instructions = _load_field_instructions()
    lines = ["Return JSON with the following fields (use null if missing):"]
    for name, text in instructions.items():
        lines.append(f'- "{name}": {text}')

    _PROMPT_CACHE = f"{PROMPT_HEADER}\n\n" + "\n".join(lines)
    return _PROMPT_CACHE


def build_registry_prompt(note_text: str) -> str:
    prompt_text = _load_registry_prompt()
    return f"{prompt_text}\n\nProcedure Note:\n{note_text}\nJSON:"


__all__ = ["build_registry_prompt", "FIELD_INSTRUCTIONS"]
