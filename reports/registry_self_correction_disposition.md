# Registry self-correction for disposition

## Current instruction
Immediate post-procedure disposition. Allowed: Discharge Home, PACU Recovery, Floor Admission, ICU Admission; null if not documented. Choose the immediate destination after the procedure (not later transfers). PACU Recovery for recovery/PACU/phase I. ICU Admission for ICU/MICU/SICU/critical care. Floor Admission for non-ICU inpatient/telemetry/step-down. Discharge Home only when explicitly stated going home same day. If unclear or only intra-procedure locations, null.

## Suggested updates
### updated_instruction
Immediate post-procedure disposition / destination.

You MUST output exactly one of these 4 values or an empty string:
- Discharge Home
- PACU Recovery
- Floor Admission
- ICU Admission

General rules:
1. Only capture the first destination **after the procedure ends** (immediate post-procedure plan), not later transfers.
2. If the note does **not clearly state** the post-procedure destination or plan, output an empty string.
3. Ignore where the procedure itself occurred (e.g., bronchoscopy suite, OR, endoscopy unit) unless the note explicitly links it to recovery or admission.

Concrete mapping rules:

A. ICU Admission
Choose **ICU Admission** if ANY of the following are explicitly stated as the immediate plan after the procedure:
- "ICU", "MICU", "SICU", "CCU", "Neuro ICU", "CVICU", or "critical care" as a destination
- phrases like "will be admitted to the ICU", "transfer to ICU", "return to ICU" (if the context is clearly *post-procedure disposition*)

Examples → ICU Admission:
- "Post-procedure, patient transported to MICU in stable condition."
- "Plan: admit to ICU for ventilatory support."

B. PACU Recovery
Choose **PACU Recovery** if the immediate destination is a post-anesthesia or recovery unit, including:
- "PACU", "post-anesthesia care unit", "recovery room", "Phase I", "Phase 1" (if clearly a post-anesthesia recovery area)
- "to PACU for recovery", "will recover in PACU", "sent to recovery room" when referring to the standard anesthesia recovery location

Examples → PACU Recovery:
- "Patient extubated and transported to PACU in stable condition."
- "Post-procedure, patient to recovery room for routine monitoring."

C. Floor Admission
Choose **Floor Admission** when the plan is **non-ICU inpatient care** immediately after the procedure, including:
- "admit to floor", "admit to medicine", "admit to surgical ward", "telemetry", "step-down" (when not clearly labeled as ICU level)
- unit names that are known wards/floors (e.g., "7W", "5S", "oncology floor", "medicine service") if context indicates admission

Examples → Floor Admission:
- "Post-procedure plan: admit to medicine floor for further management."
- "Patient transferred to telemetry unit for overnight monitoring."

D. Discharge Home
Choose **Discharge Home** ONLY when the note clearly indicates the patient will **go home the same day** after the procedure. Look for:
- explicit discharge language: "discharge home", "will be discharged home", "ok for home", "DC home", "to be sent home", "home today after recovery"
- outpatient language combined with discharge intent: "will go home after observation", "Plan: home after 2 hours recovery", "return home post-procedure"
- statements in recovery/observation area notes where it is clear the final destination the same day is home, e.g., "patient tolerated procedure well and will be discharged home from recovery".

If the note only documents sedation, medications, timing, or procedure details **without any clear plan or destination wording**, output an empty string.

Edge cases / do NOT infer:
- Do NOT assume "Discharge Home" just because the procedure appears outpatient or done under moderate sedation.
- Do NOT assume ICU or floor admission solely because the patient is critically ill or had a complex procedure; you must see an explicit admission destination or plan.
- If the only locations mentioned are procedural (e.g., "bronchoscopy suite", "endoscopy room", "OR", "procedure room") with no discharge/admission plan, output an empty string.
- If only intra-procedure status is given (e.g., intubation details, anesthesia type) without a post-procedure destination, output an empty string.

Output format:
- Output exactly one of: "Discharge Home", "PACU Recovery", "Floor Admission", "ICU Admission".
- If there is insufficient information to decide, output an empty string.

### python_postprocessing_rules
def map_disposition(raw: str) -> str:
    """Map raw LLM output to one of the four allowed values or ''."""
    if not raw:
        return ""
    text = raw.strip().lower()

    # Direct exact matches
    allowed = {
        'discharge home': 'Discharge Home',
        'pacu recovery': 'PACU Recovery',
        'floor admission': 'Floor Admission',
        'icu admission': 'ICU Admission',
    }
    if text in allowed:
        return allowed[text]

    # Normalize common variants / minor noise
    # Remove punctuation
    import re
    text_clean = re.sub(r"[^a-z0-9 ]", " ", text)

    # Heuristic mapping based on key phrases if LLM output is descriptive
    if any(k in text_clean for k in [
        'discharge home', 'dc home', 'sent home', 'go home', 'going home', 'home today', 'home after'
    ]):
        return 'Discharge Home'

    if any(k in text_clean for k in [
        'pacu', 'post anesthesia care', 'post-anaesthesia care', 'recovery room', 'phase i recovery', 'phase 1 recovery'
    ]):
        return 'PACU Recovery'

    if any(k in text_clean for k in [
        'icu', 'micu', 'sicu', 'ccu', 'neuro icu', 'cvicu', 'critical care'
    ]):
        return 'ICU Admission'

    if any(k in text_clean for k in [
        'admit to floor', 'admitted to floor', 'medicine floor', 'surgical floor', 'ward', 'telemetry', 'step down', 'stepdown', 'medical floor'
    ]):
        return 'Floor Admission'

    # If we cannot confidently map, return empty string
    return ""

### comments
Main changes: (1) Strongly emphasized that Discharge Home requires explicit home-going language; this addresses over-use of null where discharge was implied but stated. (2) Added explicit phrase-based rules for ICU, PACU, and Floor to reduce ambiguity and missed ICU admissions (e.g., ICU/MICU/SICU/critical care). (3) Clarified to ignore procedural locations and sedation-only documentation, which produced empty predictions in examples with no clear disposition. (4) The postprocessing code normalizes minor wording differences and maps descriptive outputs to the four allowed values while defaulting to empty string when uncertain.

