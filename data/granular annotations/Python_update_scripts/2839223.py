import json

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_idx = -1
    for i in range(occurrence):
        start_idx = text.find(term, start_idx + 1)
        if start_idx == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times.")
    
    return {
        "start": start_idx, 
        "end": start_idx + len(term), 
        "text": term
    }

RAW_TEXT = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Steven Park, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Pentax EB-1990i linear EBUS bronchoscope
   - Needle: 22-gauge FNB/ProCore (FNB/ProCore)
   - STATIONS SAMPLED: 4 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 4L: 2 passes, short axis 18.3mm
     * Station 10R: 4 passes, short axis 14.8mm
     * Station 4R: 4 passes, short axis 20.9mm
     * Station 7: 2 passes, short axis 24.0mm

   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Monarch Robotic Bronchoscopy System (Auris Health (J&J))
   - Registration method: CT-to-body
   - Registration accuracy: 2.0 mm
   - Navigation to peripheral lesion: RUL anterior (B3)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 30.9mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RUL lobe
   - Forceps biopsies obtained: 6 specimens
   - Additional TBNA: 4 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Fluoroscopy
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 08:15 - 09:32 (77 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

[REDACTED], MD
[REDACTED]"""

# Constructing the JSON structure with validated spans
data = {
    "id": "2839223",
    "text": RAW_TEXT,
    "entities": [
        # Metadata
        {"label": "Physician_Name", **get_span(RAW_TEXT, "Steven Park, MD", 1)},
        {"label": "Anesthesia_Type", **get_span(RAW_TEXT, "General anesthesia", 1)},
        {"label": "Total_RVU", **get_span(RAW_TEXT, "18.41", 1)},
        
        # Procedure 1
        {"label": "Procedure_Name", **get_span(RAW_TEXT, "ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
        {"label": "CPT_Code", **get_span(RAW_TEXT, "31653", 1)},
        {"label": "Equipment", **get_span(RAW_TEXT, "Pentax EB-1990i linear EBUS bronchoscope", 1)},
        {"label": "Equipment", **get_span(RAW_TEXT, "22-gauge FNB/ProCore", 1)},
        
        # Procedure 2
        {"label": "Procedure_Name", **get_span(RAW_TEXT, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
        {"label": "CPT_Code", **get_span(RAW_TEXT, "+31627", 1)},
        {"label": "Equipment", **get_span(RAW_TEXT, "Monarch Robotic Bronchoscopy System", 1)},
        {"label": "Target_Anatomy", **get_span(RAW_TEXT, "RUL anterior (B3)", 1)},
        
        # Procedure 3
        {"label": "Procedure_Name", **get_span(RAW_TEXT, "ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION", 1)},
        {"label": "CPT_Code", **get_span(RAW_TEXT, "+31654", 1)},
        {"label": "Equipment", **get_span(RAW_TEXT, "20 MHz radial EBUS miniprobe", 1)},
        
        # Procedure 4
        {"label": "Procedure_Name", **get_span(RAW_TEXT, "TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE", 1)},
        {"label": "CPT_Code", **get_span(RAW_TEXT, "31628", 1)},
        {"label": "Target_Anatomy", **get_span(RAW_TEXT, "RUL lobe", 1)},
        
        # Specimen Types
        {"label": "Specimen_Type", **get_span(RAW_TEXT, "Cytology", 1)},
        {"label": "Specimen_Type", **get_span(RAW_TEXT, "cell block", 1)},
        {"label": "Specimen_Type", **get_span(RAW_TEXT, "flow cytometry", 1)},
        {"label": "Specimen_Type", **get_span(RAW_TEXT, "Surgical pathology", 1)},
        {"label": "Specimen_Type", **get_span(RAW_TEXT, "molecular testing", 1)},
        {"label": "Specimen_Type", **get_span(RAW_TEXT, "Bacterial, fungal, AFB cultures", 1)}
    ]
}

# Verify validity by printing
if __name__ == "__main__":
    print(json.dumps(data, indent=2))