🩺 Extraction Quality Report: Note 205Score: 55 / 100Status: ❌ FAIL1. Accuracy (Precision)Hallucinations: The JSON extracts the patient's age as "12". This is a critical hallucination derived from the "Cooke 12F pigtail catheter".Mismatch: The JSON states the chest_tube guidance was "Ultrasound". The note indicates the chest tube was placed via Seldinger technique following fluoroscopic imaging showing a pneumothorax. Radial ultrasound was used earlier for the lung lesion, not for the chest tube drainage.2. Completeness (Recall)Missed Procedures: The JSON misses the "Enbobronchial forcep biopsies" performed on the superior segment lesion.Missed Procedures: The JSON misses the "peripheral needle" biopsies performed. Even though they were non-diagnostic on ROSE and aborted due to hypoxia, the procedure was still physically performed.Missed Details: The patient's actual age is missing from the extraction (likely redacted in the header, but extracting "12" from a catheter size is a critical failure).3. Logic & CodingCPT Consistency: CPT 32557 (Pleural drainage with imaging guidance) is applied, but the text lacks explicit mention of real-time imaging during the puncture, only prior/post fluoroscopy.Schema Compliance: The procedures_performed object is missing the forceps and needle biopsies entirely.4. Corrected JSON SnippetJSON    "patient_demographics": {
      "age_years": null,
      "gender": "Female"
    },
    "procedures_performed": {
      "endobronchial_biopsy": {
        "performed": true,
        "tools": ["Forceps"]
      },
      "peripheral_tbna": {
        "performed": true,
        "tools": ["Needle"]
      }
    },
    "pleural_procedures": {
      "chest_tube": {
        "performed": true,
        "action": "Insertion",
        "tube_type": "Pigtail",
        "guidance": "Fluoroscopy"
      }
    }