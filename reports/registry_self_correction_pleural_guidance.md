# Registry self-correction for pleural_guidance

## Current instruction
Imaging guidance for pleural procedures only (thoracentesis, chest tube/pigtail, tunneled pleural catheter, medical thoracoscopy, pleural drain/biopsy). Allowed: Ultrasound, CT, Blind; null if no pleural procedure or guidance not documented. Ultrasound only when pleural procedure is ultrasound-guided; ignore EBUS/rebus/bronchial ultrasound. CT only when pleural procedure performed under CT/CT-fluoro. Blind when no imaging or for medical thoracoscopy/pleuroscopy without imaging guidance. Do not set from non-pleural procedures or prior diagnostic imaging alone.

## Suggested updates
### updated_instruction
Field: pleural_guidance

Goal: Identify the type of imaging guidance used **specifically for pleural procedures** in the note.

Valid outputs (exactly one or null):
- "Ultrasound"
- "CT"
- "Blind"
- null  (if no pleural procedure or no guidance documented)

1) Only consider **pleural procedures**:
   Count as pleural procedures:
   - Thoracentesis
   - Chest tube or pigtail catheter placement (for pleural fluid/air)
   - Tunneled pleural catheter (e.g., PleurX)
   - Medical thoracoscopy / pleuroscopy
   - Pleural drain placement
   - Pleural biopsy (percutaneous or via medical thoracoscopy)

   Do **NOT** set this field from procedures that are **not pleural**, such as:
   - Bronchoscopy, robotic bronchoscopy (e.g., Ion)
   - EBUS / radial EBUS / bronchial ultrasound
   - BAL, endobronchial or transbronchial biopsies
   - Mediastinal / hilar / parenchymal lung biopsies done via bronchoscopy

   If the note only describes non-pleural procedures (e.g., EBUS with TBNA for lymph nodes), output **null**.

2) How to choose the value for pleural procedures:
   - "Ultrasound":
       Use **only** when the pleural procedure is explicitly described as ultrasound-guided (e.g., "ultrasound-guided thoracentesis", "bedside ultrasound was used to localize pleural fluid before pigtail placement").
       Ignore any mention of **EBUS**, **radial/bronchial ultrasound**, or other ultrasound that is not used to guide a pleural procedure.

   - "CT":
       Use when the pleural procedure is performed under **CT** or **CT-fluoroscopy** guidance (e.g., "CT-guided chest tube placement", "CT-fluoro-guided pleural drain").
       Do **not** choose CT just because the patient had prior diagnostic CT imaging; it must guide the actual pleural procedure.

   - "Blind":
       Use when a pleural procedure is performed **without imaging guidance** (i.e., landmark-based), OR for **medical thoracoscopy/pleuroscopy** that is not documented as using ultrasound or CT for guidance.

3) Multiple pleural procedures in one note:
   - If **any** pleural procedure is done with ultrasound guidance, set to "Ultrasound".
   - Else, if **any** pleural procedure is done with CT guidance, set to "CT".
   - Else, if pleural procedures are done without imaging guidance (or only with thoracoscopy/pleuroscopy visualization), set to "Blind".

4) When to output null:
   - No pleural procedure is documented in the note (e.g., EBUS/TBNA only for nodal staging, bronchoscopy only).
   - A pleural procedure is done, but **no imaging guidance is mentioned** and it is **not** clearly blind (e.g., unclear whether they used imaging or not) – in such ambiguous cases, default to **Blind** if the procedure is bedside/landmark-style; otherwise, if the type of guidance truly cannot be inferred at all, you may use null.
   - References only to prior diagnostic imaging (CT chest, PET-CT, ultrasound) without describing an actual pleural procedure under that imaging.

5) Ignore these when deciding pleural_guidance:
   - Any ultrasound used only for airway, lymph node, or parenchymal lung targets (EBUS, radial EBUS, bronchial ultrasound).
   - Imaging used only for diagnosis or staging (e.g., PET-CT, CT chest) without a pleural procedure performed under that imaging.

Examples:
- Note: "EBUS with TBNA of 10R and 4L lymph nodes. No thoracentesis performed." ➜ pleural_guidance = null
- Note: "Ultrasound-guided right thoracentesis performed at bedside." ➜ pleural_guidance = "Ultrasound"
- Note: "CT-guided placement of 12F pigtail catheter into right pleural effusion." ➜ pleural_guidance = "CT"
- Note: "Left chest tube placed in the mid-axillary line using anatomical landmarks. No ultrasound was available." ➜ pleural_guidance = "Blind"
- Note: "Medical thoracoscopy with pleural biopsies; no mention of ultrasound or CT guidance." ➜ pleural_guidance = "Blind"
- Note: "Bronchoscopy with EBUS-guided TBNA of 4R and 7." (no pleural procedure) ➜ pleural_guidance = null
- Note: "Robotic bronchoscopy with radial ultrasound for RLL nodule biopsy; no pleural procedures." ➜ pleural_guidance = null

### python_postprocessing_rules
def map_pleural_guidance(raw: str) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip().lower()
    if text in {"", "none", "null", "n/a", "na"}:
        return None

    # Normalize common variants
    if "ultrasound" in text or "u/s" in text or "us-guided" in text:
        return "Ultrasound"
    if "ct" in text:
        # avoid mis-mapping if text is clearly negating CT guidance
        if any(neg in text for neg in ["no ct", "without ct", "ct not used"]):
            pass
        else:
            return "CT"
    if "blind" in text or "landmark" in text:
        return "Blind"

    # Direct exact mapping for already-clean values
    if text == "ultrasound":
        return "Ultrasound"
    if text == "ct":
        return "CT"
    if text == "blind":
        return "Blind"

    # Fallback: unknown or unexpected → None (leave null)
    return None

### comments
Main change is to emphasize that pleural_guidance must only come from pleural procedures and not from EBUS/bronchoscopy or other non-pleural imaging. The instructions now explicitly list included vs excluded procedures and repeatedly call out that EBUS/bronchial ultrasound must be ignored, which addresses the error where 'Ultrasound' was predicted from an EBUS-only note. Also clarified precedence when multiple pleural procedures exist and added concrete examples around common borderline cases. The postprocessing keeps only the three allowed values and maps unexpected/ambiguous outputs to null.

