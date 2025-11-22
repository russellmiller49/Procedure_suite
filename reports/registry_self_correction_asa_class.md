# Registry self-correction for asa_class

## Current instruction
ASA physical status if explicitly documented. Valid answers are the text as written (e.g., "ASA 3", "ASA III", "ASA 2E"). Do not infer from comorbidities or vitals. If multiple ASA values, choose the one clearly tied to this procedure or the last mentioned if ambiguous. If not documented, return null.

## Suggested updates
### updated_instruction
Extract the ASA physical status **only if it is explicitly documented as an ASA classification.**

1. **What to capture**  
   - Capture the text exactly as written when it clearly denotes an ASA physical status, such as:
     - "ASA 1", "ASA 2", "ASA 3", "ASA 4", "ASA 5", "ASA 6"  
     - "ASA I", "ASA II", "ASA III", "ASA IV", "ASA V", "ASA VI"  
     - With or without emergency suffixes, e.g., "ASA 3E", "ASA III E", "ASA 2 (emergent)", "ASA IIIE"  
   - Include any surrounding text that is part of the ASA phrase itself (e.g., "ASA III - severe systemic disease").

2. **Where it may appear**  
   - Pre-op / Anesthesia assessment sections, pre-procedure checklist, or anesthesia record.  
   - Phrases like "ASA classification", "ASA status", "ASA physical status", or simply "ASA" followed by a class.

3. **What NOT to capture**  
   - Do **not** infer ASA from comorbidities, vitals, sedation level, Ramsay scores, procedure type, or general clinical severity.  
   - Do **not** treat any of the following as ASA:  
     - Sedation scores or scales (e.g., "Ramsay 2", "Ramsay scale 3", "RASS -1").  
     - Anesthesia modality only (e.g., "general anesthesia", "moderate sedation", "MAC").  
     - Procedural or study scales (e.g., "Mallampati 3", "NYHA III", "GCS 15").  
   - If the note only mentions that anesthesia was provided, doses of medications, or sedation level, and **never mentions `ASA` or `American Society of Anesthesiologists` or `physical status`**, then return null.

4. **Multiple ASA values**  
   - If more than one ASA class is documented, choose:  
     - The one explicitly tied to this procedure (e.g., "ASA III for today's bronchoscopy").  
     - If none are clearly tied, use the **last** ASA value mentioned in the note.  

5. **Formatting of the answer**  
   - Return exactly the ASA phrase as written (e.g., "ASA 3", "ASA III", "ASA 3E").  
   - If no explicit ASA physical status is documented anywhere in the note, return **null** (not "N/A", not "unknown").

6. **Ambiguous / partial mentions**  
   - If the note contains only headers or templates like "ASA:" with no value, treat this as not documented → return null.  
   - If "ASA" appears but is clearly part of another term (e.g., part of a word, dictation artifact) and not followed by a recognizable class, ignore it and return null unless a valid ASA class is also present.


### python_postprocessing_rules
def normalize_asa(raw: str | None) -> str | None:
    """Post-process raw LLM output for asa_class.

    Rules:
    - Strip whitespace.
    - Treat empty strings, 'null', 'none', 'n/a', 'unknown' as None.
    - Otherwise return the string unchanged (any text is allowed as long as the model followed instructions).
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "":
        return None
    lowered = text.lower()
    if lowered in {"null", "none", "n/a", "na", "unknown", "not documented"}:
        return None
    return text

### comments
The main change is to stress that ASA must be explicitly documented as an ASA physical status (using the word 'ASA' or 'ASA physical status') and that sedation levels (e.g., Ramsay scores), anesthesia type, or clinical severity must not be interpreted as ASA. This directly targets the observed errors where the model likely inferred a class (ASA 3) from context or sedation details. The postprocessing is intentionally minimal, only normalizing null-like responses, because the field allows any text value as long as it is a true ASA entry per the updated instructions.

