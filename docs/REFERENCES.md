# CPT Codes Reference

This document provides a quick reference for the core Interventional Pulmonology CPT codes supported by the system. 

> **Note**: The authoritative source for logic and RVUs is `data/knowledge/ip_coding_billing.v2_7.json`.

## Bronchoscopy Family

### Diagnostic
- **31622**: Diagnostic bronchoscopy
- **31623**: Brushing / Protected Brush
- **31624**: Bronchoalveolar Lavage (BAL)
- **31625**: Endobronchial Biopsy (EBBx)
- **31628**: Transbronchial Lung Biopsy (TBLB) - Single Lobe
- **31629**: Transbronchial Needle Aspiration (TBNA) - Initial

### EBUS (Endobronchial Ultrasound)
- **31652**: Linear EBUS (1-2 nodal stations)
- **31653**: Linear EBUS (3+ nodal stations)
- **+31654**: Radial EBUS (Peripheral lesion) - *Add-on*

### Therapeutic / Interventional
- **31630**: Tracheal/Bronchial Dilation
- **31631**: Tracheal Stent placement
- **31634**: Balloon occlusion (Chartis)
- **31635**: Foreign body removal
- **31636**: Bronchial Stent placement (Initial)
- **+31637**: Bronchial Stent (Each additional)
- **31638**: Stent revision
- **31640**: Tumor excision
- **31641**: Tumor destruction / Relief of stenosis
- **31643**: Catheter placement (e.g., fiducials) - *Note: Often 31626 used for fiducials*
- **31645**: Therapeutic aspiration (Initial)
- **31646**: Therapeutic aspiration (Subsequent)
- **31647**: Endobronchial Valve (BLVR) - Initial Lobe
- **31648**: Valve Removal - Initial
- **+31649**: Valve Removal - Addl
- **+31651**: Valve Placement - Addl Lobe
- **31660**: Bronchial Thermoplasty (1 lobe)
- **31661**: Bronchial Thermoplasty (2+ lobes)

### Navigation
- **+31627**: Electromagnetic Navigation (EMN) / Computer-assisted guidance - *Add-on*

---

## Pleural Family

### Thoracentesis
- **32554**: Thoracentesis (No imaging)
- **32555**: Thoracentesis (With imaging)

### Chest Tubes & Catheters
- **32550**: Tunneled Pleural Catheter (IPC) Insertion
- **32551**: Tube Thoracostomy (Chest Tube)
- **32552**: IPC Removal
- **32556**: Pleural Drainage Catheter (Pigtail) - No imaging
- **32557**: Pleural Drainage Catheter (Pigtail) - With imaging

### Thoracoscopy (Medical)
- **32601**: Diagnostic Thoracoscopy
- **32604**: Thoracoscopy with Pericardial Biopsy
- **32606**: Thoracoscopy with Mediastinal Biopsy
- **32607**: Thoracoscopy with Wedge Resection
- **32608**: Thoracoscopy with Wedge (Bilat)
- **32609**: Thoracoscopy with Pleural Biopsy

### Pleurodesis
- **32560**: Chemical Pleurodesis (Instillation)
- **32650**: Thoracoscopy with Pleurodesis

---

## Evaluation & Management (E/M)

### Inpatient
- **99221-99223**: Initial Hospital Care
- **99231-99233**: Subsequent Hospital Care
- **99238-99239**: Discharge Day Management

### Outpatient / Consult
- **99202-99205**: New Patient
- **99211-99215**: Established Patient

### Critical Care
- **99291**: Critical Care (First 30-74 min)
- **+99292**: Critical Care (Addl 30 min)

---

## NCCI & Bundling Logic

The system enforces NCCI edits automatically. Common rules:

1. **Diagnostic Bundling**: `31622` (Diagnostic) is bundled into almost all surgical bronchoscopy codes (e.g., 31628, 31629) performed in the same session.
2. **Biopsy Hierarchy**: `31625` (EBBx) is often distinct from `31628` (TBLB) and `31629` (TBNA), but pay attention to "same lesion" vs "different lesion" logic.
3. **Navigation**: `+31627` is an add-on and must accompany a primary bronchoscopy code (31622+).
4. **Sedation**: `99152` (Moderate sedation) cannot be billed if General Anesthesia is used.

*For specific edit pairs, see `data/knowledge/ip_coding_billing.v2_7.json`.*
