# Registry self-correction for final_diagnosis_prelim

## Current instruction
Preliminary final diagnosis category Allowed values: Malignancy, Granulomatous, Infectious, Non-diagnostic, Benign, Other. Use null if not documented.

## Suggested updates
### updated_instruction
You are extracting the **preliminary final diagnosis category** for an interventional pulmonology procedure.

1. **Goal**  
   Classify the *overall* preliminary final diagnosis suggested by the procedure note (often implied by indication, pre-/post-op diagnosis, ROSE, or pathology impressions), **not** the indication alone.

2. **Allowed values (exactly one):**  
   - "Malignancy"  
   - "Granulomatous"  
   - "Infectious"  
   - "Non-diagnostic"  
   - "Benign"  
   - "Other"  
   - If you truly cannot determine any of these from the note, output exactly: `null`

3. **How to choose the category**

   **A. Malignancy**  
   Choose **Malignancy** if any of the following are present as the working / preliminary diagnosis, even if final pathology is pending:
   - ROSE / on-site cytology: "malignant", "positive for malignancy", "carcinoma", "adenocarcinoma", "squamous cell carcinoma", "small cell lung cancer", "metastatic carcinoma", "NSCLC", "SCLC", "lymphoma", etc.
   - Pre- or post-operative diagnosis clearly malignant (e.g., "malignant central airway obstruction", "known lung cancer", "small cell lung cancer staging").
   - Airway obstruction or lesion described as clearly malignant or tumor-related ("tumor debulking", "endobronchial tumor", etc.).
   - Staging procedures where an existing cancer diagnosis is explicitly documented (e.g., "Indication: small cell lung cancer staging").
   
   **Do NOT** assign Malignancy based *only* on suspicion or imaging phrases like "suspicious nodule", "concern for malignancy", "mass", or "staging" when no explicit malignant diagnosis or malignant ROSE/cytology is documented.

   **B. Granulomatous**  
   Choose **Granulomatous** if the preliminary diagnosis is granulomatous disease, e.g.:
   - "granulomatous inflammation", "noncaseating granulomas" on ROSE/frozen/rapid read.
   - Working diagnosis of sarcoidosis, granulomatous disease, or similar.

   **C. Infectious**  
   Choose **Infectious** if the preliminary diagnosis is an infection, e.g.:
   - "bacterial pneumonia", "fungal infection", "TB", "mycobacterial infection", "abscess", or ROSE suggesting infection.

   **D. Non-diagnostic**  
   Choose **Non-diagnostic** if the note indicates that no diagnostic material was obtained or the result is nondiagnostic, e.g.:
   - "non-diagnostic", "insufficient material", "no lesional cells identified", "no diagnostic tissue obtained".

   **E. Benign**  
   Choose **Benign** if the preliminary diagnosis is clearly non-malignant and non-infectious, e.g.:
   - "benign", "reactive lymphoid tissue", "benign bronchial mucosa", "benign appearing", benign tumor such as hamartoma, etc.

   **F. Other**  
   Choose **Other** when:
   - The procedure is **not** being done to diagnose malignancy, infection, granulomatous disease, or a clear benign pathologic process, and
   - No diagnostic pathology category from above is stated or implied.
   
   Typical **Other** scenarios:
   - Purely therapeutic / structural procedures: e.g., bronchoscopic lung volume reduction (BLVR), endobronchial valve placement for emphysema, airway inspection for atelectasis, mucus plugging, unexplained collapse, stent placement for non-malignant reasons, etc., when no underlying malignant / infectious / granulomatous / benign pathology is explicitly documented as the diagnosis.
   - Notes that only describe the **procedure** or **indication** (e.g., "emphysema", "airway collapse", "bronchial stenosis") without specifying a malignancy, benign tumor, infection, or granulomatous disease.

4. Special guidance for common patterns and error-prone cases

   - If the note contains **explicit malignant language** (e.g., "small cell lung cancer", "malignant central airway obstruction", ROSE positive for malignancy), choose **Malignancy** even if the procedure also has a therapeutic component.
   - If the note **only** describes imaging suspicion or concern ("suspicious nodule", "clinical question: primary lung cancer vs other"), but **no malignant diagnosis or ROSE result** is given and no other diagnosis category is clear, choose **Other**, not Malignancy.
   - For procedures clearly aimed at **emphysema treatment** (e.g., EBV/BLVR for severe emphysema) without a documented malignancy, infection, granulomatous disease, benign pathology, or nondiagnostic statement, choose **Other**.
   - For airway evaluation where only collapse/obstruction is mentioned and **no cause is given** (no tumor, no malignancy, no infection, etc.), choose **Other**.
   - For staging procedures with **known** cancer documented (e.g., "Pre-op diagnosis: small cell lung cancer"), choose **Malignancy** even if post-op diagnosis is "pending".

5. If you truly cannot map the note to any of the six categories above, output exactly `null`.

Output format: return **only** one of the following strings exactly: `Malignancy`, `Granulomatous`, `Infectious`, `Non-diagnostic`, `Benign`, `Other`, or `null`.

### python_postprocessing_rules
def map_final_diagnosis_prelim(raw: str) -> str:
    """Map raw LLM output to one of the allowed values or 'null'."""
    if raw is None:
        return "null"
    text = str(raw).strip().lower()

    # Direct normalized mapping
    mapping = {
        'malignancy': 'Malignancy',
        'malignant': 'Malignancy',
        'cancer': 'Malignancy',
        'granulomatous': 'Granulomatous',
        'granuloma': 'Granulomatous',
        'infectious': 'Infectious',
        'infection': 'Infectious',
        'non-diagnostic': 'Non-diagnostic',
        'nondiagnostic': 'Non-diagnostic',
        'non diagnostic': 'Non-diagnostic',
        'benign': 'Benign',
        'other': 'Other',
        'null': 'null',
        'none': 'null',
        'unknown': 'null',
        'not documented': 'null'
    }

    # Exact match after stripping
    if text in mapping:
        return mapping[text]

    # Handle common noisy variants
    for key, val in mapping.items():
        if key in text:
            return val

    # If nothing matches, default to null to avoid misclassification
    return 'null'

### comments
Main changes: (1) Expanded instructions to clearly distinguish between *suspicion* of cancer vs *documented malignancy* to prevent over-calling Malignancy in cases like Example 1 and 7. (2) Added explicit guidance that known cancer diagnoses (e.g., 'small cell lung cancer staging', 'malignant central airway obstruction') should be labeled Malignancy even if post-op diagnosis is pending (Examples 4 and 6). (3) Clarified that therapeutic/structural procedures (e.g., BLVR for emphysema, airway collapse evaluation) without a clear pathologic label should be 'Other' (Examples 3, 5, 7, 8). (4) Provided concrete phrase triggers for each category and explicit decision rules for typical error-prone scenarios. (5) Postprocessing now normalizes minor textual variants and defaults to 'null' rather than guessing when the model output is unclear.

