import openpyxl
from openpyxl.utils import get_column_letter
import json
import re
import os

# -------------------------------------------------------------------------
# INPUT DATA
# -------------------------------------------------------------------------
NOTE_ID = "note_032"
SOURCE_FILE = "note_032.txt"
PROCEDURE_DATE = "2026-01-12" # Inferred from prompt context, usually blank if unknown
NOTE_TEXT = """NOTE_ID:  note_032 SOURCE_FILE: note_032.txt INDICATION FOR OPERATION:  [REDACTED]is a 73 year old-year-old male who presents with lung mass, multiple lung nodules, mediastinal/hilar lymphadenopathy, and LLL lobar atelectasis.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient or surrogate in detail.
Patient or surrogate indicated a wish to proceed with surgery and informed consent was signed.
PREOPERATIVE DIAGNOSIS: R91.8 Other nonspecific abnormal finding of lung field.
POSTOPERATIVE DIAGNOSIS:  R91.8 Other nonspecific abnormal finding of lung field.
PROCEDURE:  
31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS)
31645 Therapeutic aspiration initial episode
31622 Dx bronchoscope/cell washing          
31623 Dx bronchoscope/brushing    
31624 Dx bronchoscope/lavage (BAL)    
31625 Endobronchial Biopsy(s)
31628 TBBX single lobe     
31629 TBNA single lobe   
31626 Fiducial marker placements, single or multiple     
31627 Navigational Bronchoscopy (computer assisted)
77012 Radiology / radiologic guidance for CT guided needle placement (CIOS)
76377 3D rendering with interpretation and reporting of CT, US, Tomo modality (ION Planning Station)
31654 Radial EBUS 
for peripheral lesion
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
31632 TBBX additional lobes  
31633 TBNA additional lobes   
31653 EBUS sampling 3 or more nodes
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets 
76983 Ultrasound Elastography, Additional Target 2
 
22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)
 
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure (22 MODIFIER):
This patient required Transbronchial Cryo biopsies at different locations (2 different locations), Robotic Navigation to more 
than one site (2 different sites - LEFT upper lobe and RIGHT middle lobe), CT-guided needle placement at different locations (2 different locations), Multiple Bronchoalveolar lavages in different locations (3 different locations), Brushings at multiple locations (2 different locations), and Radial EBUS performed at multiple locations (2 different locations).
The patient required endobronchial biopsies at two different/discrete locations and endobronchial destruction of tumor by method other than excision at two different/discrete locations.
The patient required ultrasound elastrography evaluation of 5 different/discrete lymph node sites, with the images/interpretation used for intraprocedural decision-making;
this also extended the time necessary for the EBUS procedure.
This resulted in >100% increased work due to Increased intensity, Time, Technical difficulty of procedure, Severity of patient's condition, and Physical and mental effort required.
Apply to:      
31623 Dx bronchoscope/brushing    
31624 Dx bronchoscope/lavage (BAL)    
31625 Endobronchial Biopsy(s)
31628 TBBX single lobe
31627 Navigational Bronchoscopy (computer assisted)
77012 Radiology / radiologic guidance for CT guided needle placement (CIOS)
31654 Radial EBUS for peripheral lesion
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
31632 TBBX additional lobes   
31653 EBUS sampling 3 or more nodes
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets 
 
ANESTHESIA: General Anesthesia
 
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an 
independent trained observer that was present throughout the entire procedure.
INSTRUMENT(S): 
Flexible Therapeutic Bronchoscope
Linear EBUS 
Radial EBUS
Ion Robotic Bronchoscope
 
PROCEDURE IN DETAIL:
A timeout was performed (confirming the patient's name, procedure type, and procedure location).
After the successful induction of anesthesia, anesthesia placed an ETT.
Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
VCV	14	450	12	70	10	17
 
The Flexible Therapeutic Bronchoscope was advanced for airway examination.
Endobronchial topical lidocaine applied to the main carina, right carina 1, and left carina 2.
 
Initial Airway Examination Findings:
Trachea: Distal 1/3 normal.
Thin bloody secretions in the distal trachea.
Main Carina: Sharp
Right Lung Proximal Airways:  Bloody secretions and scattered mild blood clot burden within the right-sided airways, particularly the RML and RLL.
Normal anatomic branching to the first subsegmental level - except there was no RB7, which is a normal variant.
No right-sided endobronchial tumor.  No right-sided source of bleeding.  No evidence of mass, lesions, other endobronchial pathology.
Left Lung Proximal Airways:  Moderate blood secretions and large clot burden within the left-sided airways, including complete obstruction of the LLL bronchus due to clot.
Endobronchial tumor was not initially seen; however, later in the case when the clot was aspirated out, endobronchial tumor was noted protruding from the LLL basilar anteromedial (LB7/8) segment and LLL superior segment (LB6) and causing complete obstruction of these airways.
After therapeutic aspiration of clot, the LLL lateral (LB9) and posterior (LB10) segments appeared patent.  No LUL endobronchial tumor identified.
LUL with normal anatomic branching to the first subsegmental level.  Source of bleeding, appeared to be from the LLL.
No active bleeding from LUL identified.
Mucosa: Friable with patches of erythema.
Secretions: Moderate blood secretions and blood clot, most notably in the left-sided airways, but also mild amount in the right-sided airways.
All secretions were suctioned to clear (therapeutic aspiration).
 
Successful therapeutic aspiration was performed to clean out the distal trachea, right mainstem bronchus, right upper lobe, bronchus intermedius, right middle lobe, right lower lobe, left mainstem bronchus, left upper lobe, left lower lobe from mucus, blood, and blood clots.
The Flexible Therapeutic Bronchoscope was removed and the robotic-assisted navigational platform was set-up and the Ion robotic bronchoscope catheter advanced.
Left upper lobe LB1/LB2 mass:
 
CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target.
The navigational plan was reviewed and verified.  This was then loaded into robotic bronchoscopy platform.
Robotic navigation bronchoscopy was performed with Intuitive Ion platform.  Partial registration was used.
The Ion robotic catheter was used to engage the Apical-Posterior Segment of LUL (LB1/2).
Target lesion is about 7.4 cm in diameter.   Under navigational guidance the Ion robotic catheter was advanced to 0.5 cm away from the planned target.
Radial EBUS was performed in attempt to identify location of lesion, which showed Concentric pattern with the following features noted: Continuous margin  and Absence of linear-discrete air bronchogram.
Transbronchial needle was advanced.  Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
Cios Spin system was used for evaluation of nodule location.  Low dose spin was performed to acquire 3D volume.
This was passed on to Ion platform system for 3D reconstruction and nodule location.
The newly acquired nodule location demonstrated the robotic catheter was in appropriate position. Cone beam CT confirmed tool-in-lesion.
I personally interpreted the cone beam CT and 3-D reconstruction.
Transbronchial needle aspiration was performed with 21G Needle and 23G Needle through the Ion extended working channel catheter.
Total 8 sample(s) were collected.  Samples sent for Cytology, Flow cytometry, and cultures.
Radial EBUS was performed in attempt to identify location of lesion, which showed Concentric pattern with the following features noted: Continuous margin  and Absence of linear-discrete air bronchogram.
Transbronchial cryobiopsy was performed with the 1.1 mm cryoprobe via the extended working channel catheter.
Freeze time of 6 seconds were used.  Total 10 sample(s) were collected.  Samples sent for Pathology.
ROSE from ION procedure was noted to be:  TBNA with atypical cells, large naked nuclei, cryo-biopsies with cells possibly more consistent with atypical histiocytes.
Not definitive for RCC.  Additional sampling recommended (which was performed, but no change in ROSE interpretation).
Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.
Transbronchial brushing was performed with Protected cytology brush via the extended working channel catheter.  Total 1 sample(s) were collected.
Samples sent for Cytology.
 
Mini Bronchial alveolar lavage was performed via the extended working channel catheter.
Instilled 10 cc of NS, suction returned with 5 cc of BAL fluid.  Samples sent for Cytology.
The robotic extended working channel catheter was withdrawn.
 
The Flexible Therapeutic Bronchoscope was readvanced. Moderate bleeding suctioned to clear.
Bronchial alveolar lavage was performed at Apical-Posterior Segment of LUL (LB1/2).
Instilled 40 cc of NS, suction returned with 15 cc of BAL fluid.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology. 
 
Secretions, residual saline, and mild blood suctioned to clear.
Right middle lobe RB4 nodule:
 
CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target.
The navigational plan was reviewed and verified.  This was then loaded into robotic bronchoscopy platform.
Robotic navigation bronchoscopy was performed with Intuitive Ion platform.  Partial registration was repeated and used.
The Ion robotic catheter was used to engage the Lateral Segment of RML (RB4).
Target lesion is about 2.3 cm in diameter.   Under navigational guidance the Ion robotic catheter was advanced to 0.5 cm away from the planned target.
Radial EBUS was performed in attempt to identify location of lesion, which showed Eccentric pattern with the following features noted: Continuous margin  and Absence of linear-discrete air bronchogram.
Transbronchial needle was advanced.  Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
Cios Spin system was used for evaluation of nodule location.  Low dose spin was performed to acquire 3D volume.
This was passed on to Ion platform system for 3D reconstruction and nodule location.
The newly acquired nodule location demonstrated the robotic catheter was in appropriate position..  Cone beam CT confirmed tool-in-lesion.
I personally interpreted the cone beam CT and 3-D reconstruction.
Transbronchial needle aspiration was performed with new 21G Needle and 23G Needle through the Ion extended working channel catheter.
Total 7 sample(s) were collected.  Samples sent for Cytology and Cultures.
Radial EBUS was performed in attempt to identify location of lesion, which showed Concentric pattern with the following features noted: Continuous margin  and Absence of linear-discrete air bronchogram.
Transbronchial cryobiopsy was performed with the 1.1 mm cryoprobe via the extended working channel catheter.
Freeze time of 6 seconds were used.  Total 6 sample(s) were collected.  Samples sent for Pathology.
ROSE from ION procedure was noted to be:  Macrophages, Lymphocytes, Bronchial cells
 
Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.
However, this fiducial marker appeared to fall out and did not enter the nodule.
Transbronchial brushing was performed with Protected cytology brush via the extended working channel catheter.  Total 1 sample(s) were collected.
Samples sent for Cytology.
 
Mini Bronchial alveolar lavage was performed via the extended working channel catheter.
Instilled 10 cc of NS, suction returned with 5 cc of NS.  Samples sent for Micro/Cultures.
The robotic extended working channel catheter was withdrawn.  
 
Post-biopsy fluoroscopy images negative for pneumothorax bilaterally.
The Flexible Therapeutic Bronchoscope was readvanced. Mild bleeding suctioned to clear.
Bronchial alveolar lavage was performed at Lateral Segment of RML (RB4).
Instilled 60 cc of NS, suction returned with 60 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology. 
 
Secretions, residual saline, and mild blood suctioned to clear.
Therapeutic aspiration of clot from the LLL confirmed endobronchial tumor within multiple LLL segmental airways - this tumor was friable and easily bled.
The Flexible Therapeutic Bronchoscope was withdrawn and the endobronchial ultrasound-capable (EBUS) bronchoscope was introduced with the following findings:
 
EBUS-Findings
Indications: Diagnostic and Staging
Technique:
All lymph node stations were assessed.
Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 25-gauge Needle and 21-gauge Needle.
Lymph Nodes/Sites Inspected: 
4R (lower paratracheal) node - see ultrasound elastography details below.
4L (lower paratracheal) node - Endobronchial ultrasound (EBUS) elastography mode was performed on this lymph node to assess its stiffness and tissue characteristics, and to identify different densities in this target lymph node.
Semi-qualitivative analysis of this lymph node demonstrated a Type 1 elastograpic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
The elastography interpretation was separate from the typical interpretation of linear EBUS ultrasound images.
Along with the lymph node size, the elastographic pattern information/interpretation was used to make the decision to not perform transbronchial sampling of this lymph node.
This image was store and archived. 
7 (subcarinal)  - ultrasound elastography details below.
11Rs lymph node - see ultrasound elastography details below.
11Ri lymph node - see ultrasound elastography details below.
Due to friable/bleeding endobronchial tumor in the LLL, EBUS assessment of 11L was not performed.
Overall EBUS TBNA ROSE Diagnosis:  Many histiocytes, some lymphocytes
 
Lymph Nodes Sampled:
Site 1: The 11Ri lymph node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed.
Elastography:  Endobronchial ultrasound (EBUS) elastography mode was performed to assess lymph node stiffness and tissue characteristics, and to identify different densities in this target lymph node.
Semi-qualitivative analysis of this lymph node demonstrated a Type 1 elastograpic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
Despite the benign appearance, TBNA was performed to confirm the absence of malignancy and to obtain cytology for diagnostic completeness.
The elastography interpretation was separate from the typical interpretation of linear EBUS ultrasound images.
Along with the lymph node size, the elastographic pattern interpretation was used to make the decision to perform transbronchial sampling of this lymph node and where to guide/location sampling within the lymph node.
This image was store and archived.  
Sampling:  The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Sample sent for cytology.
Preliminary ROSE Cytology was reported as adequate and Lymphocytes, Histiocytes. Final results are pending.
Site 2: The 11Rs lymph node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed.
Elastography:  Endobronchial ultrasound (EBUS) elastography mode was performed to assess lymph node stiffness and tissue characteristics, and to identify different densities in this target lymph node.
Semi-qualitivative analysis of this lymph node demonstrated a Type 2 elastographic pattern with mixed soft (green/yellow) and stiff (blue) regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
The elastography interpretation was separate from the typical interpretation of linear EBUS ultrasound images.
Along with the lymph node size, the elastographic pattern interpretation was used to make the decision to perform transbronchial sampling of this lymph node and where to guide/location sampling within the lymph node.
This image was store and archived.  
Sampling:  The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Sample sent for cytology.
Preliminary ROSE Cytology was reported as adequate and Lymphocytes, Histiocytes. Final results are pending.
Site 3: The 4R (lower paratracheal) node was => 10 mm on CT and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed.
Elastography:  Endobronchial ultrasound (EBUS) elastography mode was performed to assess lymph node stiffness and tissue characteristics, and to identify different densities in this target lymph node.
Semi-qualitivative analysis of this lymph node demonstrated a Type 2 elastographic pattern with mixed soft (green/yellow) and stiff (blue) regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
The elastography interpretation was separate from the typical interpretation of linear EBUS ultrasound images.
Along with the lymph node size, the elastographic pattern interpretation was used to make the decision to perform transbronchial sampling of this lymph node and where to guide/location sampling within the lymph node.
This image was store and archived.  
Sampling:  The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Sample sent for cytology.
Preliminary ROSE Cytology was reported as adequate and Many histiocytes, some lymphocytes. Final results are pending.
Site 4: The 7 (subcarinal) node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable.
The lymph node was photographed.
Elastography:  Endobronchial ultrasound (EBUS) elastography mode was performed to assess lymph node stiffness and tissue characteristics, and to identify different densities in this target lymph node.
Semi-qualitivative analysis of this lymph node demonstrated a Type 2 elastographic pattern with mixed soft (green/yellow) and stiff (blue) regions.
Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.
The elastography interpretation was separate from the typical interpretation of linear EBUS ultrasound images.
Along with the lymph node size, the elastographic pattern interpretation was used to make the decision to perform transbronchial sampling of this lymph node and where to guide/location sampling within the lymph node.
This image was store and archived.  
Sampling:  The site was sampled.. 4 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.
Sample sent for cytology.
Preliminary ROSE Cytology was reported as adequate and Lymphocytes, Histiocytes. Final results are pending.
The EBUS bronchoscope was withdrawn and the Flexible Therapeutic Bronchoscope readvanced.  
 
Moderate bloody secretions and blood clot suctioned to clear.
Endobronchial biopsy with cryoprobe was performed at left lower lobe basilar anteromedial segment (LB7/8).  Lesion was successfully removed.
Samples sent for Pathology - combined with the LLL LB6 tumor.
Endobronchial biopsy with cryoprobe was performed at left lower lobe superior segment (LB6).  Lesion was successfully removed.
Samples sent for Pathology - combined with the LLL LB7/8 tumor.
ROSE from endobronchial tumor touch-prep was noted to be:  Atypical cells, large naked nuclei.
Endobronchial obstruction due to discrete endobronchial tumor at left lower lobe basilar anteromedial segment (LB7/8) was treated with the following modalities:
Modality	Tools	Setting/Mode	Duration	Results
Cryotherapy	1.1mm cryoprobe	Cryo	8-12 seconds	Cryoprobe used to resect with cryotherapy portions of the endobronchial tumor obstructing the LLL basilar anteromedial segment (LB7/8).
This modality debulked some of the tumor, but it became apparent that the tumor was extensive in this segmental airways and the obstruction from the tumor could not be relieved.
APC	1.5mm Pulmonary axial 'straight-fire' probe	forcedAPC, 0.5 LPM, Effect 2	1-5 second pulses	Successful coagulation/devitalization of tumor obstructing the left lower lobe basilar anteromedial segment (LB7/8) - leading to partial ablation of the endobronchial tumors (although these segments remain fully obstructed) and resolution of bleeding from the site.
Endobronchial obstruction due to discrete endobronchial tumor at left lower lobe superior segment (LB6) was treated with the following modalities:
Modality	Tools	Setting/Mode	Duration	Results
Cryotherapy	1.1mm cryoprobe	Cryo	8-12 seconds	Cryoprobe used to resect with cryotherapy portions of the endobronchial tumor obstructing the LLL superior segment segment (LB6).
This modality debulked some of the tumor, but it became apparent that the tumor was extensive in this segmental airways and the obstruction from the tumor could not be relieved.
APC	1.5mm Pulmonary axial 'straight-fire' probe	forcedAPC, 0.5 LPM, Effect 2	1-5 second pulses	Successful coagulation/devitalization of tumor obstructing the left lower lobe superior segment (LB6) - leading to partial ablation of the endobronchial tumors (although these segments remain fully obstructed) and resolution of bleeding from the site.
The endobronchial tumors were friable even with minimal scope/suction trauma and persistently oozed blood, but never in a large amount.
There was Nashville Grade 2 bleeding from the endobronchial tumors during tumor destruction and debulking.
Bleeding controlled with suction, cold saline flushes, and endobronchial epinephrine 0.2mg.
Still had mild oozing, particularly from the LB6 endobronchial tumor, which ultimately resolved with APC ablation/coagulation of the visible endobronchial tumors.
Prior to treatment, the left lower lobe basilar anteromedial segment (LB7/8) airway was note to be 0% patent.
After treatment, the airway was 0% patent.  
Prior to treatment, the left lower lobe superior segment (LB6) airway was note to be 0% patent.
After treatment, the airway was 0% patent. 
Prior to treatment, the left lower lobe truncus basalis and LB9-10 airways were was note to be 0% patent.
After extraction of clot and nearby tumor, these airways were 100% patent.
Residual secretions, saline, and minimal blood was suctioned to clear (therapeutic aspiration).  Inspection demonstrated no evidence of active bleeding.
Bronchoscope was removed.
 
The patient tolerated the procedure well.  There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
ESTIMATED BLOOD LOSS:   Moderate
COMPLICATIONS:     None
"""

TEMPLATE_PATH = "phase0_golden_registry_labeling_worksheet_anchor_first_therapeutic_pleural.xlsx"
OUTPUT_PATH = f"phase0_extraction_{NOTE_ID}.xlsx"

# -------------------------------------------------------------------------
# CONSTANTS & CONFIG
# -------------------------------------------------------------------------
HEADERS_NOTE_TEXT = ["note_id", "source_file", "note_text"]
HEADERS_NOTE_INDEX = [
    "source_file", "note_id", "encounter_id", "procedure_date", "site", "reviewer", "status", "free_text_notes",
    "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings", "endobronchial_biopsy", "tbna_conventional",
    "linear_ebus", "radial_ebus", "navigational_bronchoscopy", "transbronchial_biopsy", "transbronchial_cryobiopsy",
    "therapeutic_aspiration", "foreign_body_removal", "airway_dilation", "airway_stent", "thermal_ablation",
    "tumor_debulking_non_thermal", "cryotherapy", "blvr", "peripheral_ablation", "bronchial_thermoplasty",
    "whole_lung_lavage", "rigid_bronchoscopy",
    "thoracentesis", "chest_tube", "ipc", "medical_thoracoscopy", "pleurodesis", "pleural_biopsy", "fibrinolytic_therapy"
]
HEADERS_SPAN = [
    "source_file", "note_id", "span_id", "section_type", "context_prefix", "span_text", "match_index",
    "start_char", "end_char", "span_len", "label", "normalized_value", "schema_field", "event_id",
    "is_negated", "is_historical", "time_anchor", "reviewer", "comments", "hydration_status"
]
HEADERS_EVENT_LOG = [
    "source_file", "note_id", "event_id", "event_type", "method", "anatomy_target", "device", "needle_gauge",
    "stations", "counts", "measurements", "specimens", "findings", "is_historical", "reviewer", "comments",
    "device_size", "device_material",
    "outcome_airway_lumen_pre", "outcome_airway_lumen_post", "outcome_symptoms", "outcome_pleural", "outcome_complication"
]
HEADERS_V3_EVENTS = [
    "note_id", "event_id", "type",
    "target.anatomy_type", "target.location.lobe", "target.location.segment", "target.station",
    "lesion.type", "lesion.size_mm",
    "method", "devices_json", "measurements_json", "specimens_json", "findings_json", "evidence_quote",
    "stent.size", "stent.material_or_brand", "catheter.size_fr",
    "outcomes.airway.lumen_pre", "outcomes.airway.lumen_post",
    "outcomes.symptoms", "outcomes.pleural", "outcomes.complications"
]

# -------------------------------------------------------------------------
# EXTRACTION LOGIC
# -------------------------------------------------------------------------
def generate_extraction(write_workbook: bool = True):
    wb = None
    ws_index = None
    if write_workbook:
        wb = openpyxl.load_workbook(TEMPLATE_PATH)
        ws_text = wb["Note_Text"]
        ws_text.append([NOTE_ID, SOURCE_FILE, NOTE_TEXT])
        ws_index = wb["Note_Index"]
    # Map flags based on analysis
    flags = {
        "diagnostic_bronchoscopy": 1,
        "bal": 1,
        "bronchial_wash": 0, # Note uses Therapeutic aspiration or BAL
        "brushings": 1,
        "endobronchial_biopsy": 1, # Cryo of LLL tumor
        "tbna_conventional": 1,
        "linear_ebus": 1,
        "radial_ebus": 1,
        "navigational_bronchoscopy": 1,
        "transbronchial_biopsy": 1, # TBBX codes and Cryo parenchymal
        "transbronchial_cryobiopsy": 1,
        "therapeutic_aspiration": 1,
        "foreign_body_removal": 0,
        "airway_dilation": 0,
        "airway_stent": 0,
        "thermal_ablation": 1, # APC
        "tumor_debulking_non_thermal": 1, # Cryo extraction
        "cryotherapy": 1,
        "blvr": 0,
        "peripheral_ablation": 0,
        "bronchial_thermoplasty": 0,
        "whole_lung_lavage": 0,
        "rigid_bronchoscopy": 0,
        "thoracentesis": 0,
        "chest_tube": 0,
        "ipc": 0,
        "medical_thoracoscopy": 0,
        "pleurodesis": 0,
        "pleural_biopsy": 0,
        "fibrinolytic_therapy": 0
    }
    
    row_data = [SOURCE_FILE, NOTE_ID, "", PROCEDURE_DATE, "", "", "Extraction Done", ""]
    # Append flag values in order
    flag_keys = HEADERS_NOTE_INDEX[8:]
    for key in flag_keys:
        row_data.append(flags.get(key, 0))
    if write_workbook and ws_index is not None:
        ws_index.append(row_data)

    # 4. Prepare Spans & Events
    spans = []
    events = []
    
    # --- Event Definitions ---
    
    # Event 1: Global/Multi-site Therapeutic Aspiration (Clots)
    events.append({
        "event_id": "EVT_01", "type": "therapeutic", "method": "therapeutic_aspiration",
        "anatomy": "tracheobronchial tree", "findings": "clots removed"
    })
    spans.extend([
        {"text": "Therapeutic aspiration", "label": "PROC_METHOD", "norm": "therapeutic_aspiration", "evt": "EVT_01", "ctx": "Successful therapeutic aspiration"},
        {"text": "distal trachea", "label": "ANAT_AIRWAY", "norm": "trachea", "evt": "EVT_01", "ctx": "clean out the"},
        {"text": "left lower lobe", "label": "ANAT_AIRWAY", "norm": "LLL", "evt": "EVT_01", "ctx": "left upper lobe,"},
        {"text": "blood clots", "label": "OBS_LESION", "norm": "blood_clot", "evt": "EVT_01", "ctx": "mucus, blood, and"}
    ])

    # Event 2: LUL Mass (LB1/LB2) - Nav/Radial/TBNA/Cryo/Fiducial/Brush/Mini-BAL
    events.append({
        "event_id": "EVT_02", "type": "diagnostic", "method": "navigational_bronchoscopy",
        "anatomy": "LUL", "lobe": "LUL", "segment": "LB1+LB2", "lesion_size": "74",
        "findings": "Concentric EBUS, Atypical cells"
    })
    spans.extend([
        {"text": "Apical-Posterior Segment of LUL (LB1/2)", "label": "ANAT_LUNG_LOC", "norm": "LUL_apicoposterior", "evt": "EVT_02", "ctx": "engage the"},
        {"text": "7.4 cm", "label": "MEAS_SIZE", "norm": "74", "evt": "EVT_02", "ctx": "Target lesion is about"},
        {"text": "Radial EBUS", "label": "PROC_METHOD", "norm": "radial_ebus", "evt": "EVT_02", "ctx": "target.\nRadial EBUS"},
        {"text": "Concentric pattern", "label": "OBS_ROSE", "norm": "concentric_view", "evt": "EVT_02", "ctx": "showed Concentric pattern"},
        {"text": "Transbronchial needle aspiration", "label": "PROC_METHOD", "norm": "tbna", "evt": "EVT_02", "ctx": "reconstruction.\nTransbronchial needle aspiration"},
        {"text": "21G Needle", "label": "DEV_NEEDLE", "norm": "21G", "evt": "EVT_02", "ctx": "performed with 21G Needle"},
        {"text": "23G Needle", "label": "DEV_NEEDLE", "norm": "23G", "evt": "EVT_02", "ctx": "Needle and 23G Needle"},
        {"text": "Transbronchial cryobiopsy", "label": "PROC_METHOD", "norm": "transbronchial_cryobiopsy", "evt": "EVT_02", "ctx": "catheter.\nTransbronchial cryobiopsy"},
        {"text": "1.1 mm cryoprobe", "label": "DEV_INSTRUMENT", "norm": "cryoprobe_1.1mm", "evt": "EVT_02", "ctx": "with the 1.1 mm cryoprobe"},
        {"text": "Fiducial marker", "label": "PROC_METHOD", "norm": "fiducial_placement", "evt": "EVT_02", "ctx": "interpretation).\nFiducial marker"},
        {"text": "Protected cytology brush", "label": "DEV_INSTRUMENT", "norm": "cytology_brush", "evt": "EVT_02", "ctx": "performed with Protected cytology brush"},
        {"text": "Mini Bronchial alveolar lavage", "label": "PROC_METHOD", "norm": "mini_bal", "evt": "EVT_02", "ctx": "Cytology.\n\nMini Bronchial alveolar lavage"}
    ])

    # Event 3: LUL BAL (Separate)
    events.append({
        "event_id": "EVT_03", "type": "diagnostic", "method": "bal",
        "anatomy": "LUL", "lobe": "LUL", "segment": "LB1+LB2"
    })
    spans.extend([
        {"text": "Bronchial alveolar lavage", "label": "PROC_METHOD", "norm": "bal", "evt": "EVT_03", "ctx": "suctioned to clear.\nBronchial alveolar lavage"},
        {"text": "Apical-Posterior Segment of LUL (LB1/2)", "label": "ANAT_LUNG_LOC", "norm": "LUL_apicoposterior", "evt": "EVT_03", "ctx": "performed at Apical-Posterior Segment"},
        {"text": "Instilled 40 cc", "label": "PROC_ACTION", "norm": "instilled_40ml", "evt": "EVT_03", "ctx": "Apical-Posterior Segment of LUL (LB1/2).\nInstilled 40 cc"}
    ])

    # Event 4: RML Nodule (RB4) - Nav/Radial/TBNA/Cryo/Fiducial(Fail)/Brush/Mini-BAL
    events.append({
        "event_id": "EVT_04", "type": "diagnostic", "method": "navigational_bronchoscopy",
        "anatomy": "RML", "lobe": "RML", "segment": "RB4", "lesion_size": "23",
        "findings": "Eccentric EBUS, Macrophages"
    })
    spans.extend([
        {"text": "Lateral Segment of RML (RB4)", "label": "ANAT_LUNG_LOC", "norm": "RML_lateral", "evt": "EVT_04", "ctx": "engage the Lateral Segment"},
        {"text": "2.3 cm", "label": "MEAS_SIZE", "norm": "23", "evt": "EVT_04", "ctx": "Target lesion is about"},
        {"text": "Radial EBUS", "label": "PROC_METHOD", "norm": "radial_ebus", "evt": "EVT_04", "ctx": "target.\nRadial EBUS"},
        {"text": "Eccentric pattern", "label": "OBS_ROSE", "norm": "eccentric_view", "evt": "EVT_04", "ctx": "showed Eccentric pattern"},
        {"text": "Transbronchial needle aspiration", "label": "PROC_METHOD", "norm": "tbna", "evt": "EVT_04", "ctx": "reconstruction.\nTransbronchial needle aspiration"},
        {"text": "Transbronchial cryobiopsy", "label": "PROC_METHOD", "norm": "transbronchial_cryobiopsy", "evt": "EVT_04", "ctx": "air bronchogram.\nTransbronchial cryobiopsy"},
        {"text": "Fiducial marker", "label": "PROC_METHOD", "norm": "fiducial_placement", "evt": "EVT_04", "ctx": "Bronchial cells\n\nFiducial marker"},
        {"text": "Transbronchial brushing", "label": "PROC_METHOD", "norm": "brushing", "evt": "EVT_04", "ctx": "not enter the nodule.\nTransbronchial brushing"},
        {"text": "Mini Bronchial alveolar lavage", "label": "PROC_METHOD", "norm": "mini_bal", "evt": "EVT_04", "ctx": "Cytology.\n\nMini Bronchial alveolar lavage"}
    ])

    # Event 5: RML BAL (Separate)
    events.append({
        "event_id": "EVT_05", "type": "diagnostic", "method": "bal",
        "anatomy": "RML", "lobe": "RML", "segment": "RB4"
    })
    spans.extend([
        {"text": "Bronchial alveolar lavage", "label": "PROC_METHOD", "norm": "bal", "evt": "EVT_05", "ctx": "suctioned to clear.\nBronchial alveolar lavage"},
        {"text": "Lateral Segment of RML (RB4)", "label": "ANAT_LUNG_LOC", "norm": "RML_lateral", "evt": "EVT_05", "ctx": "performed at Lateral Segment"},
        {"text": "Instilled 60 cc", "label": "PROC_ACTION", "norm": "instilled_60ml", "evt": "EVT_05", "ctx": "Lateral Segment of RML (RB4).\nInstilled 60 cc"}
    ])

    # Event 6: EBUS 11Ri
    events.append({
        "event_id": "EVT_06", "type": "diagnostic", "method": "linear_ebus",
        "anatomy": "11Ri", "station": "11Ri"
    })
    spans.extend([
        {"text": "11Ri lymph node", "label": "ANAT_LN_STATION", "norm": "11Ri", "evt": "EVT_06", "ctx": "Site 1: The 11Ri lymph node"},
        {"text": "Type 1 elastograpic pattern", "label": "OBS_LESION", "norm": "elastography_type_1", "evt": "EVT_06", "ctx": "demonstrated a Type 1 elastograpic pattern"},
        {"text": "transbronchial biopsies", "label": "PROC_METHOD", "norm": "tbna", "evt": "EVT_06", "ctx": "ultrasound guided transbronchial biopsies"}
    ])

    # Event 7: EBUS 11Rs
    events.append({
        "event_id": "EVT_07", "type": "diagnostic", "method": "linear_ebus",
        "anatomy": "11Rs", "station": "11Rs"
    })
    spans.extend([
        {"text": "11Rs lymph node", "label": "ANAT_LN_STATION", "norm": "11Rs", "evt": "EVT_07", "ctx": "Site 2: The 11Rs lymph node"},
        {"text": "Type 2 elastographic pattern", "label": "OBS_LESION", "norm": "elastography_type_2", "evt": "EVT_07", "ctx": "demonstrated a Type 2 elastographic pattern"},
        {"text": "TBNA", "label": "PROC_METHOD", "norm": "tbna", "evt": "EVT_07", "ctx": "indeterminate appearance, TBNA"}
    ])

    # Event 8: EBUS 4R
    events.append({
        "event_id": "EVT_08", "type": "diagnostic", "method": "linear_ebus",
        "anatomy": "4R", "station": "4R"
    })
    spans.extend([
        {"text": "4R (lower paratracheal) node", "label": "ANAT_LN_STATION", "norm": "4R", "evt": "EVT_08", "ctx": "Site 3: The 4R (lower paratracheal)"},
        {"text": "TBNA", "label": "PROC_METHOD", "norm": "tbna", "evt": "EVT_08", "ctx": "appearance, TBNA was directed"}
    ])

    # Event 9: EBUS 7
    events.append({
        "event_id": "EVT_09", "type": "diagnostic", "method": "linear_ebus",
        "anatomy": "7", "station": "7"
    })
    spans.extend([
        {"text": "7 (subcarinal) node", "label": "ANAT_LN_STATION", "norm": "7", "evt": "EVT_09", "ctx": "Site 4: The 7 (subcarinal)"},
        {"text": "TBNA", "label": "PROC_METHOD", "norm": "tbna", "evt": "EVT_09", "ctx": "indeterminate appearance, TBNA"}
    ])

    # Event 10: LLL LB7/8 Tumor Debulking
    events.append({
        "event_id": "EVT_10", "type": "therapeutic", "method": "tumor_debulking_non_thermal",
        "anatomy": "LLL LB7/8", "lobe": "LLL", "segment": "LB7+LB8",
        "lumen_pre": "0", "lumen_post": "0"
    })
    spans.extend([
        {"text": "Endobronchial biopsy with cryoprobe", "label": "PROC_METHOD", "norm": "endobronchial_biopsy", "evt": "EVT_10", "ctx": "Endobronchial biopsy with cryoprobe was performed at left lower lobe basilar"},
        {"text": "left lower lobe basilar anteromedial segment (LB7/8)", "label": "ANAT_LUNG_LOC", "norm": "LLL_anteromedial_basal", "evt": "EVT_10", "ctx": "cryoprobe was performed at"},
        {"text": "Cryotherapy", "label": "PROC_METHOD", "norm": "cryotherapy", "evt": "EVT_10", "ctx": "Modality\tTools\tSetting/Mode\tDuration\tResults\nCryotherapy"},
        {"text": "1.1mm cryoprobe", "label": "DEV_INSTRUMENT", "norm": "cryoprobe_1.1mm", "evt": "EVT_10", "ctx": "Cryotherapy\t1.1mm cryoprobe"},
        {"text": "APC", "label": "PROC_METHOD", "norm": "apc", "evt": "EVT_10", "ctx": "relieved.\nAPC"},
        {"text": "0% patent", "label": "OUTCOME_AIRWAY_LUMEN_PRE", "norm": "0", "evt": "EVT_10", "ctx": "LB7/8) airway was note to be 0% patent"},
        {"text": "0% patent", "label": "OUTCOME_AIRWAY_LUMEN_POST", "norm": "0", "evt": "EVT_10", "ctx": "After treatment, the airway was 0% patent"}
    ])

    # Event 11: LLL LB6 Tumor Debulking
    events.append({
        "event_id": "EVT_11", "type": "therapeutic", "method": "tumor_debulking_non_thermal",
        "anatomy": "LLL LB6", "lobe": "LLL", "segment": "LB6",
        "lumen_pre": "0", "lumen_post": "0"
    })
    spans.extend([
        {"text": "Endobronchial biopsy with cryoprobe", "label": "PROC_METHOD", "norm": "endobronchial_biopsy", "evt": "EVT_11", "ctx": "tumor.\nEndobronchial biopsy with cryoprobe was performed at left lower lobe superior"},
        {"text": "left lower lobe superior segment (LB6)", "label": "ANAT_LUNG_LOC", "norm": "LLL_superior", "evt": "EVT_11", "ctx": "performed at left lower lobe superior segment"},
        {"text": "Cryotherapy", "label": "PROC_METHOD", "norm": "cryotherapy", "evt": "EVT_11", "ctx": "Modality\tTools\tSetting/Mode\tDuration\tResults\nCryotherapy"},
        {"text": "APC", "label": "PROC_METHOD", "norm": "apc", "evt": "EVT_11", "ctx": "relieved.\nAPC"},
        {"text": "0% patent", "label": "OUTCOME_AIRWAY_LUMEN_PRE", "norm": "0", "evt": "EVT_11", "ctx": "LB6) airway was note to be 0% patent"},
        {"text": "0% patent", "label": "OUTCOME_AIRWAY_LUMEN_POST", "norm": "0", "evt": "EVT_11", "ctx": "After treatment, the airway was 0% patent"}
    ])

    # Event 12: LLL Clot/Tumor Clearance (LB9-10)
    events.append({
        "event_id": "EVT_12", "type": "therapeutic", "method": "therapeutic_aspiration",
        "anatomy": "LLL LB9-10", "lobe": "LLL", "segment": "LB9+LB10",
        "lumen_pre": "0", "lumen_post": "100"
    })
    spans.extend([
        {"text": "LB9-10 airways", "label": "ANAT_LUNG_LOC", "norm": "LLL_basal", "evt": "EVT_12", "ctx": "truncus basalis and"},
        {"text": "0% patent", "label": "OUTCOME_AIRWAY_LUMEN_PRE", "norm": "0", "evt": "EVT_12", "ctx": "airways were was note to be 0% patent"},
        {"text": "100% patent", "label": "OUTCOME_AIRWAY_LUMEN_POST", "norm": "100", "evt": "EVT_12", "ctx": "airways were 100% patent"}
    ])
    
    # Event 13: Complications
    events.append({
        "event_id": "EVT_13", "type": "outcome", "method": "n/a", "anatomy": "n/a"
    })
    spans.append({"text": "No immediate complications", "label": "OUTCOME_COMPLICATION", "norm": "none", "evt": "EVT_13", "ctx": "procedure well.  There were"})

    if not write_workbook:
        return flags, spans, events

    # --- Processing Spans (Hydration) ---
    ws_span = wb["Span_Annotations"]
    ws_hydrated = wb["Span_Hydrated"]
    
    # Add headers to both
    ws_span.append(HEADERS_SPAN)
    ws_hydrated.append(HEADERS_SPAN)
    
    # Helper for finding text
    def find_matches(text, substring):
        return [m.start() for m in re.finditer(re.escape(substring), text)]

    span_id_counter = 1
    
    for s in spans:
        span_text = s["text"]
        context = s.get("ctx", "")
        label = s["label"]
        norm = s["norm"]
        event_id = s.get("evt", "")
        
        matches = find_matches(NOTE_TEXT, span_text)
        
        start_char = ""
        end_char = ""
        hydration_status = "unresolved"
        match_index = 0
        
        if len(matches) == 1:
            start_char = matches[0]
            end_char = start_char + len(span_text)
            hydration_status = "hydrated_unique"
            match_index = 1
        elif len(matches) > 1 and context:
            # Context window check (preceding 120 chars)
            best_match = -1
            for i, m_start in enumerate(matches):
                window_start = max(0, m_start - 120)
                preceding_text = NOTE_TEXT[window_start:m_start]
                if context in preceding_text or context in NOTE_TEXT[max(0, m_start - len(context) - 20):m_start + 20]:
                    best_match = m_start
                    match_index = i + 1
                    break
            
            if best_match != -1:
                start_char = best_match
                end_char = start_char + len(span_text)
                hydration_status = "hydrated_context"
            else:
                hydration_status = f"ambiguous_count={len(matches)}"
        else:
            hydration_status = f"ambiguous_count={len(matches)}"
            
        # Write Anchor Row (No offsets)
        span_id = f"SPAN_{span_id_counter:03d}"
        span_len = f'=LEN(F{span_id_counter + 1})'
        
        row_anchor = [
            SOURCE_FILE, NOTE_ID, span_id, "Procedure", context, span_text, match_index,
            "", "", span_len, label, norm, "", event_id,
            0, 0, "", "", "", "needs_hydration"
        ]
        ws_span.append(row_anchor)
        
        # Write Hydrated Row
        row_hydrated = [
            SOURCE_FILE, NOTE_ID, span_id, "Procedure", context, span_text, match_index,
            start_char, end_char, len(span_text), label, norm, "", event_id,
            0, 0, "", "", "", hydration_status
        ]
        ws_hydrated.append(row_hydrated)
        
        span_id_counter += 1

    # 5. Populate Event Log
    ws_event = wb["Event_Log"]
    ws_event.append(HEADERS_EVENT_LOG)
    
    # Map internal event dicts to log rows
    for e in events:
        evt_id = e["event_id"]
        if evt_id == "EVT_13": continue # Outcome only
        
        # Defaults
        anatomy = e.get("anatomy", "")
        method = e.get("method", "")
        outcome_pre = e.get("lumen_pre", "")
        outcome_post = e.get("lumen_post", "")
        
        row = [
            SOURCE_FILE, NOTE_ID, evt_id, e["type"], method, anatomy,
            "", "", "", "", "", "", e.get("findings", ""),
            0, "", "", "", "",
            outcome_pre, outcome_post, "", "", ""
        ]
        # Check specific complication logic
        if evt_id == "EVT_13":
            # Already handled skip, but logic would go here
            pass
            
        ws_event.append(row)
        
    # Add complication row separately to event log? 
    # The template implies one row per event. 
    # I'll just append a specific outcome row for the complication.
    ws_event.append([
        SOURCE_FILE, NOTE_ID, "EVT_13", "outcome", "", "", "", "", "", "", "", "", "", 
        0, "", "", "", "", "", "", "", "", "None"
    ])

    # 6. Populate V3_Procedure_Events
    ws_v3 = wb["V3_Procedure_Events"]
    ws_v3.append(HEADERS_V3_EVENTS)
    
    registry_procedures = []
    
    for e in events:
        if e["event_id"] == "EVT_13": continue
        
        # Construct JSON objects
        proc_obj = {
            "event_id": e["event_id"],
            "type": e["type"],
            "target": {
                "anatomy_type": "airway" if "LB" in e.get("segment", "") or "RB" in e.get("segment", "") else "lymph_node" if "station" in e else "lung",
                "location": {
                    "lobe": e.get("lobe", ""),
                    "segment": e.get("segment", "")
                },
                "station": e.get("station", "")
            },
            "lesion": {
                "size_mm": e.get("lesion_size", "")
            },
            "method": e["method"],
            "outcomes": {
                "airway": {
                    "lumen_pre": e.get("lumen_pre", ""),
                    "lumen_post": e.get("lumen_post", "")
                }
            }
        }
        
        registry_procedures.append(proc_obj)
        
        row = [
            NOTE_ID, e["event_id"], e["type"],
            proc_obj["target"]["anatomy_type"], e.get("lobe", ""), e.get("segment", ""), e.get("station", ""),
            "", e.get("lesion_size", ""),
            e["method"], "[]", "[]", "[]", "[]", "",
            "", "", "",
            e.get("lumen_pre", ""), e.get("lumen_post", ""),
            "", "", ""
        ]
        ws_v3.append(row)

    # 7. V3_Registry_JSON
    ws_json = wb["V3_Registry_JSON"]
    ws_json.append(["schema_version", "note_id", "json_output", "no_immediate_complications"])
    
    final_json = {
        "schema_version": "3.0",
        "note_id": NOTE_ID,
        "procedures": registry_procedures,
        "no_immediate_complications": True
    }
    
    ws_json.append(["3.0", NOTE_ID, json.dumps(final_json, indent=2), True])

    # Save
    wb.save(OUTPUT_PATH)
    print(f"Generated {OUTPUT_PATH}")

def extract_data():
    return generate_extraction(write_workbook=False)


if __name__ == "__main__":
    generate_extraction()
