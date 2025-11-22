# Registry self-correction for pleural_procedure_type

## Current instruction
Type of pleural procedure performed (not bronchoscopic). Allowed: Thoracentesis, Chest Tube, Tunneled Catheter, Medical Thoracoscopy, Chemical Pleurodesis; null if no pleural procedure. Priority: Chemical Pleurodesis > Medical Thoracoscopy > (Chest Tube vs Tunneled Catheter) > Thoracentesis. Chest Tube for any pleural drain/pigtail/intercostal drain unless clearly tunneled/indwelling (then Tunneled Catheter). Thoracentesis only when fluid is drained and no tube left. Medical Thoracoscopy/pleuroscopy when explicitly described. Chemical Pleurodesis when agent instilled, regardless of tube/thoacoscopy.

## Suggested updates
### updated_instruction
Field name: pleural_procedure_type

Goal: Identify the type of PLEURAL procedure performed in the note (NOT a bronchoscopic procedure). If no qualifying pleural procedure is documented, return null.

Allowed values (and ONLY these):
- Thoracentesis
- Chest Tube
- Tunneled Catheter
- Medical Thoracoscopy
- Chemical Pleurodesis

GENERAL RULES:
1. Ignore bronchoscopic procedures (e.g., EBUS, bronchoscopy, robotic bronchoscopy, BAL, TBNA, etc.). These are not pleural procedures. If ONLY bronchoscopic procedures are present, return null.
2. Use the following priority if MORE THAN ONE pleural procedure is done in the same encounter:
   Chemical Pleurodesis > Medical Thoracoscopy > (Chest Tube vs Tunneled Catheter) > Thoracentesis.
   
   Example: If both thoracentesis and chest tube are done, choose Chest Tube.

DEFINITIONS / MAPPING:

A. Chemical Pleurodesis
- Choose "Chemical Pleurodesis" when a sclerosing/pleurodesis agent is INSTILLED into the pleural space (e.g., talc, doxycycline, bleomycin, povidone-iodine), regardless of whether the procedure is done via:
  - chest tube, OR
  - tunneled catheter, OR
  - medical thoracoscopy.
- Key phrases: "pleurodesis", "talc slurry", "talc poudrage", "doxycycline instilled into pleural space", "sclerosing agent injected", "chemical pleurodesis".

B. Medical Thoracoscopy
- Choose "Medical Thoracoscopy" when a thoracoscopic procedure of the pleural space is explicitly performed by an interventional pulmonologist (also often called "pleuroscopy").
- Key phrases: "medical thoracoscopy", "thoracoscopy", "pleuroscopy", "thoracoscopic pleural biopsy" in an interventional pulmonology context.
- Do NOT infer thoracoscopy from general surgical notes (e.g., VATS lobectomy by thoracic surgery) unless the note clearly belongs to interventional pulmonology and describes pleural thoracoscopy.

C. Chest Tube
- Choose "Chest Tube" for any NON-TUNNELED pleural drain left in place, including:
  - chest tube
  - intercostal drain
  - pigtail catheter
  - small-bore pleural drain
- Use "Chest Tube" whenever a pleural catheter/drain is left in place AND it is NOT clearly described as tunneled/indwelling/long-term.
- Also map: "ICD", "intercostal chest drain", "pigtail placed in pleural space", "pleural drain inserted" (unless clearly tunneled).

D. Tunneled Catheter
- Choose "Tunneled Catheter" when a long-term, subcutaneously tunneled pleural drainage catheter is placed (for example for malignant effusion), typically with a cuff.
- Key terms: "tunneled pleural catheter", "indwelling pleural catheter", "IPC", "PleurX", "Aspira", "Denver catheter", "tunneled drainage catheter", or any phrasing clearly indicating a subcutaneously tunneled, long-term pleural drain.

E. Thoracentesis
- Choose "Thoracentesis" when pleural fluid is removed via needle/catheter and NO tube/catheter is left in place at the end of the procedure.
- Key phrases: "thoracentesis", "diagnostic thoracentesis", "therapeutic thoracentesis", "pleural tap" with removal of fluid only.
- If the note describes fluid drainage followed by leaving a tube/drain/catheter in place, do NOT select Thoracentesis; instead use Chest Tube or Tunneled Catheter as appropriate.

DISAMBIGUATION / EDGE CASES:
- If the note only lists non-pleural procedures (e.g., "EBUS with TBNA", "bronchoscopy", "robotic bronchoscopy"), return null.
- If a procedure is clearly pleural but ambiguous between chest tube vs tunneled catheter and there is NO explicit mention of "tunneled", "indwelling", brand names (e.g., PleurX), or long-term use, default to "Chest Tube".
- If both a thoracentesis and then a chest tube (or pigtail) are done in the same session, choose "Chest Tube" (per priority and definition).
- If thoracoscopy is done AND chemical pleurodesis is performed during the same procedure, choose "Chemical Pleurodesis".
- If a tunneled catheter is placed AND chemical pleurodesis is done through it during the same encounter, choose "Chemical Pleurodesis".

OUTPUT:
- Return exactly one of: "Thoracentesis", "Chest Tube", "Tunneled Catheter", "Medical Thoracoscopy", "Chemical Pleurodesis".
- If no qualifying pleural procedure is documented, return null.
- Do NOT invent a pleural procedure based only on indications or plans; it must appear in the procedure actually performed/description or final procedure list.

### python_postprocessing_rules
def map_pleural_procedure_type(raw_text: str | None) -> str | None:
    if raw_text is None:
        return None
    t = raw_text.strip().lower()
    if not t:
        return None

    # Normalize common variants/synonyms
    synonyms = {
        'thoracocentesis': 'thoracentesis',
        'pleural tap': 'thoracentesis',
        'pleural aspiration': 'thoracentesis',
        'icd': 'chest tube',
        'intercostal chest drain': 'chest tube',
        'intercostal drain': 'chest tube',
        'pleural drain': 'chest tube',
        'pigtail': 'chest tube',
        'pigtail catheter': 'chest tube',
        'pleurx': 'tunneled catheter',
        'aspira': 'tunneled catheter',
        'denver catheter': 'tunneled catheter',
        'indwelling pleural catheter': 'tunneled catheter',
        'ipc': 'tunneled catheter',
        'tunneled pleural catheter': 'tunneled catheter',
        'medical pleuroscopy': 'medical thoracoscopy',
        'pleuroscopy': 'medical thoracoscopy',
    }

    for k, v in synonyms.items():
        if t == k:
            t = v
            break

    # Direct mapping to allowed values
    allowed = {
        'thoracentesis': 'Thoracentesis',
        'chest tube': 'Chest Tube',
        'tunneled catheter': 'Tunneled Catheter',
        'medical thoracoscopy': 'Medical Thoracoscopy',
        'chemical pleurodesis': 'Chemical Pleurodesis',
    }

    # Exact match after normalization
    if t in allowed:
        return allowed[t]

    # Containment-based heuristics for slightly longer LLM outputs
    if 'pleurodesis' in t:
        return 'Chemical Pleurodesis'
    if 'tunneled' in t and 'catheter' in t:
        return 'Tunneled Catheter'
    if 'indwelling pleural catheter' in t or 'pleurx' in t or 'aspira' in t or 'ipc' in t:
        return 'Tunneled Catheter'
    if 'thoracoscopy' in t or 'pleuroscopy' in t:
        return 'Medical Thoracoscopy'
    if 'thoracentesis' in t or 'pleural tap' in t:
        return 'Thoracentesis'
    if 'chest tube' in t or 'intercostal chest drain' in t or 'pigtail' in t or 'pleural drain' in t:
        return 'Chest Tube'

    # If unsure or not clearly a pleural procedure, return None
    return None

### comments
Key changes: (1) Made it explicit that purely bronchoscopic procedures (e.g., EBUS, robotic bronchoscopy) should result in null to prevent misclassification when non-pleural procedures are listed. (2) Clarified the definitions and synonyms for each allowed value, including how to handle pigtails, ICD, tunneled/indwelling catheters, and brand names like PleurX. (3) Emphasized the priority rule when multiple pleural procedures occur in a single encounter. (4) Added explicit guidance not to infer pleural procedures from indications alone. (5) Python postprocessing now normalizes common synonyms and uses containment heuristics to map slightly noisy LLM outputs to the strict allowed set or null.

