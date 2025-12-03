# CPT Codes Used in the Coder Module

This document lists all CPT codes used in the Coder module and where they are defined.

## Primary Source Files

The CPT codes are defined and used in several locations:

1. **`modules/coder/constants.py`** - Contains `CPT_DESCRIPTIONS` dictionary with all CPT codes and their descriptions (most comprehensive list)
2. **`configs/coding/ip_cpt_map.yaml`** - Contains CPT code mappings with procedure types and matching logic
3. **`modules/coder/engine.py`** - Contains hardcoded CPT codes in various code-building methods
4. **`modules/coder/rules.py`** - Contains sets of CPT codes grouped by category (surgical, diagnostic, stent, etc.)

## Complete List of CPT Codes

### Diagnostic & Navigation Codes
- **31622** - Diagnostic bronchoscopy
- **31627** - Navigational bronchoscopy (EMN)
- **31624** - Bronchoalveolar lavage (BAL)

### Biopsy & Aspiration Codes
- **31628** - Transbronchial lung biopsy, single lobe
- **+31632** - Additional transbronchial lung biopsy lobe (add-on)
- **31629** - Transbronchial needle aspiration, single lobe
- **+31633** - Additional TBNA lobe (add-on)
- **31645** - Therapeutic aspiration, initial session
- **31646** - Therapeutic aspiration, repeat same stay

### EBUS Codes
- **31652** - Linear EBUS-TBNA 1-2 stations
- **31653** - Linear EBUS-TBNA 3+ stations
- **+31654** - Radial EBUS for peripheral lesion (add-on)

### Stent Codes
- **31631** - Tracheal stent placement
- **31636** - Bronchial stent placement
- **+31637** - Additional major bronchus stent (add-on)
- **31638** - Revision or reposition of tracheal/bronchial stent
- **31635** - Removal of tracheal/bronchial foreign body (stent removal)

### Therapeutic & Dilation Codes
- **31630** - Therapeutic dilation of airway
- **31641** - Bronchoscopy with tumor destruction by ablative energy

### BLVR (Bronchoscopic Lung Volume Reduction) Codes
- **31647** - BLVR initial lobe
- **+31651** - BLVR additional lobe (add-on)

### Assessment Codes
- **31634** - Chartis collateral ventilation assessment

### Pleural Procedure Codes
- **32554** - Thoracentesis (non-imaging guided) - *Note: Used in `engine.py` but not in `constants.py`*
- **32555** - Ultrasound-guided thoracentesis

### Sedation Codes
- **99152** - Moderate sedation (first 15 min)
- **+99153** - Moderate sedation add-on (each additional 15 min)

## Code Categories (from rules.py)

### Surgical Codes Set
Codes that are considered "surgical" and bundle diagnostic codes:
- 31627, 31628, +31632, 31629, +31633, 31630, 31635, 31636, 31652, 31653, +31654, 31638, 31641

### Diagnostic Codes Set
Codes that get bundled when surgical codes are present:
- 31622

### Stent Codes Set
- 31631, 31636, +31637

### Dilation Codes Set
- 31630

### Linear EBUS Codes Set
- 31652, 31653

### Radial EBUS Codes Set
- +31654

### Sedation Codes Set
- 99152, +99153

## File Locations Summary

| File | Purpose | CPT Codes Defined |
|------|---------|-------------------|
| `modules/coder/constants.py` | CPT descriptions dictionary | All 29 codes with descriptions |
| `configs/coding/ip_cpt_map.yaml` | Procedure type mappings | Base codes: 31652, 31622, 31627, 32555, 31631<br>Add-on codes: 31653, 31624, 99152, 99153 |
| `modules/coder/engine.py` | Code generation logic | All codes (hardcoded in methods) |
| `modules/coder/rules.py` | Bundling rules and code sets | Grouped by category |
| `configs/coding/ncci_edits.yaml` | NCCI edit pairs | 31652/31624, 31652/31653, 99152/99153 |

## Notes

- Codes prefixed with `+` are add-on codes (modifier codes)
- The most comprehensive single source is `modules/coder/constants.py` which contains the `CPT_DESCRIPTIONS` dictionary
- **Important**: Code 32554 (non-imaging thoracentesis) is used in `engine.py` but is NOT in `constants.py` - this may be an oversight
- Some codes may be used in logic but not in the constants file - check `engine.py` for all code generation logic
- The golden knowledge base (`ip_golden_knowledge_v2_2.json`) also contains comprehensive coding rules and may reference additional codes

## Quick Reference: Single File with All Codes

**Answer**: The file `modules/coder/constants.py` contains the most comprehensive list in the `CPT_DESCRIPTIONS` dictionary. However, it's missing code 32554 which is used in `engine.py`. For a complete list, you need to check both:
1. `modules/coder/constants.py` - 28 codes with descriptions
2. `modules/coder/engine.py` - Additional code 32554 (line 390)

