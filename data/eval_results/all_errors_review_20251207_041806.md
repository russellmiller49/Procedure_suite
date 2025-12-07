# All Errors Error Review Report

Generated: 2025-12-07T04:18:06.827191

## Summary

- Total errors reviewed: **20**
- Cases where ML alone was correct: 0
- Cases where ML had partial overlap: 14

### Errors by Difficulty

- high_confidence: 20

### Errors by Fallback Reason

- other: 20

### Common False Positives (LLM suggested but shouldn't have)

- 31627: 2 occurrences
- 31653: 2 occurrences
- 32650: 2 occurrences
- 31636: 2 occurrences
- 31628: 1 occurrences
- 31641: 1 occurrences
- 32550: 1 occurrences

### Common False Negatives (LLM missed)

- 31652: 5 occurrences
- 31628: 3 occurrences
- 31625: 2 occurrences
- 31623: 2 occurrences
- 31624: 2 occurrences
- 31653: 1 occurrences
- 32560: 1 occurrences
- 31631: 1 occurrences
- 31638: 1 occurrences
- 31640: 1 occurrences

---

## Cases for Review

### Case 1 (idx=0, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31652, 31653`
- Predicted: `31653`
- ML-only: `31653`

- ⚠️ False Negatives: `31652`

**Note Preview:**
```
║ ║ 11L │ 19x13mm │ Hypoechoic │ YES │ MALIGNANT║ ╚══════════════════════════════════════════════════════════════╝
TRANSBRONCHIAL NEEDLE ASPIRATION - DETAILED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 2 (idx=5, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31627, 31628, 31653, 31654`
- Predicted: `31627, 31628, 31654`
- ML-only: `31627, 31628, 31654`

- ⚠️ False Negatives: `31653`

**Note Preview:**
```
Patient: Daniels, Corey || MRN: 700004
Service: Interventional Pulmonology
Date: 10/02/2025
Facility: Northside Academic Medical Center
Attending: Sarah Chen, MD

INDICATION: RLL peripheral nodule (2.
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 3 (idx=21, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31625, 31653`
- Predicted: `31653`
- ML-only: `31653`

- ⚠️ False Negatives: `31625`

**Note Preview:**
```
Patient: Jennifer Wang | ID: RR-3847-P | Birth Date: 06/28/1963
Date of Service: 10/22/2024 | Time: 10:30 AM

Chief Indication: RUL mass with mediastinal LAD, diagnostic + staging

HPI: 61F, 35 pack-y
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 4 (idx=22, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31628, 31629, 31654`
- Predicted: `31627, 31628, 31629, 31654`
- ML-only: `31627, 31628, 31629, 31654`

- ❌ False Positives: `31627`

**Note Preview:**
```
Patient: Mark Thompson | MRN# TK-9472 | Born: 09/03/1964

INDICATION: RLL 21mm solid nodule with clear bronchus sign on CT, PET SUV 4.8

ANESTHESIA: Moderate sedation, midazolam 3mg + fentanyl 75mcg
R
```

**Recommendation:** LLM hallucinated codes. Review prompt constraints for these codes.

---

### Case 5 (idx=27, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31623, 31624, 31627, 31628, 31652, 31654`
- Predicted: `31627, 31628, 31653, 31654`
- ML-only: `31627, 31628, 31653, 31654`

- ❌ False Positives: `31653`
- ⚠️ False Negatives: `31623, 31624, 31652`

**Note Preview:**
```
**Procedure Documentation**
Memorial Regional Medical Center

Date: 02/14/2025
Patient: Chen, Michelle Y., 71F, MRN 4829301
Providers: Attending - Dr. James Mitchell | Fellow - Dr. Rebecca Torres
Anes
```

**Recommendation:** Mixed errors. Manual review needed.

---

### Case 6 (idx=38, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31623, 31627, 31629, 31654`
- Predicted: `31627, 31628, 31629, 31654`
- ML-only: `31627, 31628, 31654`

- ❌ False Positives: `31628`
- ⚠️ False Negatives: `31623`

**Note Preview:**
```
Patient: ___Lisa Anderson___ MRN: ___BB-8472-K___ DOB: ___03/19/1961___

Indication: ___Peripheral LLL nodule 19mm, PET+___

SEDATION [check one]:
☐ Local only
☑ Moderate sedation: Midazolam ___3___ m
```

**Recommendation:** Mixed errors. Manual review needed.

---

### Case 7 (idx=40, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31647, 31652`
- Predicted: `31647`
- ML-only: `31647`

- ⚠️ False Negatives: `31652`

**Note Preview:**
```
Interventional Pulmonology Procedure Note
Procedure: Bronchoscopic lung volume reduction with Zephyr endobronchial valves to left upper lobe.
Patient: Karen Young, 68-year-old female with severe emphy
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 8 (idx=49, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `32609`
- Predicted: `32609, 32650`
- ML-only: `32609, 32650`

- ❌ False Positives: `32650`

**Note Preview:**
```
Pt: White, Karen || MRN: 7516219 || DOB: 4/27/1944
Date: 07/29/2025 || Location: Cedars-Sinai Medical Center, Los Angeles, CA
Attending: CDR Patricia Davis, MD

Indication: Persistent effusion despite
```

**Recommendation:** LLM hallucinated codes. Review prompt constraints for these codes.

---

### Case 9 (idx=50, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `32609`
- Predicted: `32609, 32650`
- ML-only: `32609, 32650`

- ❌ False Positives: `32650`

**Note Preview:**
```
Pt: Rivera, Susan || MRN: 3217688 || DOB: 10/25/1949
Date: 11/11/2025 || Location: UCSF Medical Center, San Francisco, CA
Attending: Dr. Sarah Williams
Fellow: Dr. Maria Santos (PGY-6)

Indication: Cy
```

**Recommendation:** LLM hallucinated codes. Review prompt constraints for these codes.

---

### Case 10 (idx=67, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31625, 31653`
- Predicted: `31653`
- ML-only: `31653`

- ⚠️ False Negatives: `31625`

**Note Preview:**
```
NAME: PATRICIA ANDERSON / ID#: MR-K8374 / D.O.B: 02/17/1957

INDICATION: RUL endobronchial lesion causing post-obstructive pneumonia + mediastinal LAD

ANESTHESIA: General via ETT, maintained on sevof
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 11 (idx=72, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31624, 31653`
- Predicted: `31653`
- ML-only: `31653`

- ⚠️ False Negatives: `31624`

**Note Preview:**
```
PATIENT: 71-year-old female with suspected stage III lung cancer.

INDICATION: PET-avid mediastinal and hilar adenopathy (stations 4R, 7, and 11R) requiring comprehensive EBUS staging.

PROCEDURE: Lin
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 12 (idx=75, test_holdout)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31628, 31653`
- Predicted: `31653`
- ML-only: `31653`

- ⚠️ False Negatives: `31628`

**Note Preview:**
```
Pt: Christopher Lee
Medical Record Number: KJ-7482-N
Date of Birth: 10/18/1955

COMPLEX INDICATION: Mediastinal lymphadenopathy + LLL peripheral infiltrate (? ILD vs malignancy)

GENERAL ANESTHESIA: E
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 13 (idx=0, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31652`
- Predicted: `31653`
- ML-only: `31653`

- ❌ False Positives: `31653`
- ⚠️ False Negatives: `31652`

**Note Preview:**
```
Patient: Sanders, Lucille | 59F | MRN 8801001
Date of Procedure: 11/14/2024
Attending: Brian Cho, MD

PRE-OP DIAGNOSIS:
Right upper lobe lung mass, suspected non-small cell lung cancer

POST-OP DIAGNO
```

**Recommendation:** Mixed errors. Manual review needed.

---

### Case 14 (idx=2, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31627, 31628, 31652, 31654`
- Predicted: `31627, 31628, 31654`
- ML-only: `31627, 31628, 31654`

- ⚠️ False Negatives: `31652`

**Note Preview:**
```
Patient: Nguyen, Tina | 50F | MRN 8801003
Date of Procedure: 11/21/2024
Attending: Michael Hart, MD

PRE-OP DIAGNOSIS:
PET-avid 2.1 cm LLL peripheral nodule and mildly enlarged 11L/7 nodes

POST-OP DI
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 15 (idx=5, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31631`
- Predicted: `31631, 31636, 31641`
- ML-only: `31636`

- ❌ False Positives: `31636, 31641`

**Note Preview:**
```
Patient: Alvarez, Maria | 63F | MRN 8801006
Date of Procedure: 11/29/2024
Attending: David Chen, MD

PRE-OP DIAGNOSIS:
Malignant right mainstem bronchus obstruction from squamous cell carcinoma

POST-
```

**Recommendation:** LLM hallucinated codes. Review prompt constraints for these codes.

---

### Case 16 (idx=8, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `32560`
- Predicted: `32550`
- ML-only: `32550`

- ❌ False Positives: `32550`
- ⚠️ False Negatives: `32560`

**Note Preview:**
```
Patient: Smith, Carolyn | 69F | MRN 8801009
Date of Procedure: 12/04/2024
Attending: Jason Moore, MD

PRE-OP DIAGNOSIS:
Recurrent malignant right pleural effusion with existing PleurX catheter

POST-O
```

**Recommendation:** Mixed errors. Manual review needed.

---

### Case 17 (idx=10, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31631, 31638, 31640, 31641`
- Predicted: `31636`
- ML-only: `31636`

- ❌ False Positives: `31636`
- ⚠️ False Negatives: `31631, 31638, 31640, 31641`

**Note Preview:**
```
OPERATIVE REPORT: COMPLEX AIRWAY INTERVENTION

Patient: Octavia Butler (MRN: 772194)
Date: 12/12/2025
Attending: Dr. V. Frankenstein

**Indication:** 65F with adenoid cystic carcinoma of the trachea. 
```

**Recommendation:** Mixed errors. Manual review needed.

---

### Case 18 (idx=14, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31628, 31632, 31654`
- Predicted: `31654`
- ML-only: ``

- ⚠️ False Negatives: `31628, 31632`

**Note Preview:**
```
PROCEDURE: Transbronchial Cryobiopsy for ILD
DATE: 10/31/2025
PATIENT: Bruce Wayne (MRN: 10001)

Indication: Progressive fibrotic ILD, UIP vs NSIP pattern.

Technique: LMA placed. Flexible bronchoscop
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 19 (idx=15, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `32551, 32561`
- Predicted: `32551`
- ML-only: `32551`

- ⚠️ False Negatives: `32561`

**Note Preview:**
```
PROCEDURE NOTE: PLEURAL INTERVENTION CONVERSION

**Patient:** James Howlett (MRN: 991823)
**Date:** 10/31/2025
**Provider:** Dr. C. Xavier

**Indication:** 55M with fevers and large right pleural effu
```

**Recommendation:** LLM missed codes. Consider adding to training data or improving prompt.

---

### Case 20 (idx=19, edge_cases)

**Difficulty:** high_confidence

**Fallback Reason:** N/A

**Codes:**
- Gold: `31628, 31641, 31654`
- Predicted: `31627, 31641, 31654`
- ML-only: ``

- ❌ False Positives: `31627`
- ⚠️ False Negatives: `31628`

**Note Preview:**
```
Procedure: Cryo-Ablation vs Biopsy
Date: 09/09/2025

**Scenario:** RLL endobronchial mass (Squamous cell).

**Intervention:**
Cryoprobe applied to the mass. Frozen for 10 seconds. 
Probe and scope wit
```

**Recommendation:** Mixed errors. Manual review needed.

---

