# Registry self-correction for sedation_type

## Current instruction
Extract sedation/anesthesia level for the procedure. Allowed: Moderate, Deep, General, Local, Monitored Anesthesia Care; null if not documented. Prefer explicit labels (e.g., "moderate sedation", "general anesthesia", "local anesthesia", "MAC/monitored anesthesia care"). If intubated/ventilated or "general anesthesia/GA" → General. If anesthesia-managed MAC without ETT and no explicit general → Deep (project convention). If explicit deep sedation → Deep. Moderate/conscious sedation when typical midazolam/fentanyl given by procedural team without anesthesia provider. Local only when local anesthetic is used and note states no systemic sedatives. If unclear, null.

## Suggested updates
### updated_instruction
Extract the sedation/anesthesia level for the procedure as ONE of the following:
- Moderate
- Deep
- General
- Local
- Monitored Anesthesia Care
If not documented or cannot be inferred using the rules below, return null.

GENERAL PRIORITY RULES
1. If the note has an explicit label that matches an allowed value (e.g., "moderate sedation", "deep sedation", "general anesthesia", "local anesthesia", "MAC" / "monitored anesthesia care"), use that label.
2. If there is an explicit mention of an anesthesia provider/team (e.g., "Anesthesia: Dr X", "CRNA", "anesthesiologist", "anesthesia team", "anesthesia managed"), **do not** label the case as Moderate just because midazolam/fentanyl were used; follow the rules for General vs Deep vs MAC below.
3. If there are conflicting clues, prefer the more intense level (General > Deep > MAC > Moderate > Local).

DEFINITIONS / MAPPING RULES

A. GENERAL
Return **General** if ANY of the following are present:
- Explicit phrases like: "general anesthesia", "GA", "under general", "general endotracheal anesthesia".
- Documentation of endotracheal tube or general anesthetic context, e.g.: "intubated", "endotracheal tube", "ETT", "LMA" with an anesthesia provider and no statement that it was MAC only, or phrases such as "after successful intubation and adequate depth of anesthesia".
- Rigid bronchoscopy, robotic bronchoscopy, or other major airway interventions (e.g., "rigid bronchoscopy", "tumor debulking", large airway stent placement) **with anesthesia team involvement** and no clear contrary statement (these are almost always under general; project convention: classify as General).
- If the gold standard for a similar context is known to be general (e.g., EBUS/rigid/robotic with anesthesia team and induction/intubation language), follow that pattern.

B. MONITORED ANESTHESIA CARE vs DEEP
Use this project convention:
- If the note states **"MAC" or "monitored anesthesia care"** and there is **no** endotracheal intubation / ventilation and **no explicit general anesthesia**, classify as **Deep** (project convention: anesthesia-managed MAC without ETT = Deep).
- If anesthesia is clearly managing a propofol-based infusion or deep sedation (e.g., "propofol drip/infusion" given by anesthesia, "anesthesia provided sedation"), with **no ETT and no explicit general**, classify as **Deep**.
- If the provider explicitly calls the technique "monitored anesthesia care" and you are not asked to apply the deep-sedation convention, you may output **Monitored Anesthesia Care**; however, if project documentation states that MAC should be treated as Deep, then output **Deep**. (If in doubt for this task, use Deep for MAC, as above.)

C. DEEP (without explicit MAC wording)
Return **Deep** if ANY of the following:
- Explicit phrases: "deep sedation", "deeply sedated".
- Anesthesia service manages continuous or high-dose IV sedatives (often with propofol) and the level is described as deep or implies minimal responsiveness, **without** documentation of intubation or general anesthesia.

D. MODERATE
Return **Moderate** when:
- The note explicitly says "moderate sedation", "conscious sedation", or "procedural sedation" without an anesthesia team being the primary operator of sedation.
- Typical moderate sedation pattern: midazolam (Versed) and/or fentanyl (or similar benzodiazepine/opioid combinations) are given by the procedural team (pulmonologist, nurse) and there is **no anesthesia provider/team mentioned**.
- Patient remains responsive, can follow commands, or similar wording of moderate level, and there is no ETT or general anesthesia.
- Propofol may be present in small bolus doses **without** an anesthesia provider and without indication of deep or general; if described as "conscious/moderate" or typical bedside sedation, classify as Moderate.
- Audio-recorded notes describing the patient as sedated but responsive, with Ramsay score around 2–3 and no anesthesia team, are typically Moderate, even if only midazolam/fentanyl are explicitly named.

IMPORTANT: Do **NOT** default to Moderate solely because midazolam/fentanyl are given if there is a clearly documented anesthesia provider or intubation, since that usually indicates General or Deep.

E. LOCAL
Return **Local** only if ALL are true:
- Only topical/local anesthetics are documented (e.g., lidocaine to airway/skin, nebulized or sprayed lidocaine), and
- The note **explicitly** indicates no systemic sedatives/analgesics were given (e.g., "no IV sedation", "local anesthesia only", "patient remained awake with topical anesthesia only"), or clearly states the patient remained fully awake and unsedated (e.g., Ramsay 1–2 with explicit statement that no sedatives were administered), and
- There is no mention of midazolam, fentanyl, propofol, dexmedetomidine, or other systemic sedatives/analgesics.

If a note describes topical/local anesthesia and the patient is awake (e.g., "Ramsay 1–2") but does **not** clearly say that **no systemic sedatives were given**, and there is no medication list, classify as **Moderate** rather than Local (project convention to avoid under-calling sedation in ambiguous cases).

F. NULL
Return null if:
- No sedation/anesthesia information is documented, and
- Sedation level cannot be reasonably inferred from the type of procedure and context using the above rules.

EXAMPLES (HOW TO HANDLE CASES SIMILAR TO RECENT ERRORS)
- Example 1: EBUS + robotic with "Anesthesia: Dr. Andrew Kim (CRNA supervision)" → **General** (major airway procedure with anesthesia team; assume general unless clearly MAC only).
- Example 2: EBUS with midazolam, fentanyl, *propofol drip* and likely anesthesia team involvement → treat as anesthesia-managed, high-intensity sedation; by project convention, if not explicitly general but deep-level propofol infusion, classify as **Deep**. If there is also intubation/GA language, classify as **General**.
- Example 3: If the procedure is a standard flexible bronchoscopy or EBUS, done in endoscopy/bronchoscopy lab, with IV midazolam/fentanyl by procedural team and no anesthesia provider noted → **Moderate**.
- Example 4: Rigid bronchoscopy with tumor debulking and stent placement, anesthesia involved/OR setting (even if truncated documentation) → **General** (rigid bronchoscopy is almost always done under general).
- Example 5: "Anesthesia: General anesthesia provided by anesthesia team" and mention of intubation → **General**.
- Example 6: Topical lidocaine, patient remained awake, Ramsay 1–2, **BUT** no explicit statement that no systemic sedatives were given → classify as **Moderate** (do not call this Local unless note clearly says no systemic sedatives).

Output exactly one of: Moderate, Deep, General, Local, Monitored Anesthesia Care, or null.

### python_postprocessing_rules
def normalize_sedation_type(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    text = raw_value.strip().lower()
    if not text:
        return None

    # Direct matches
    mapping = {
        'moderate': 'Moderate',
        'moderate sedation': 'Moderate',
        'conscious sedation': 'Moderate',
        'procedural sedation': 'Moderate',
        'deep': 'Deep',
        'deep sedation': 'Deep',
        'general': 'General',
        'general anesthesia': 'General',
        'ga': 'General',
        'local': 'Local',
        'local anesthesia': 'Local',
        'monitored anesthesia care': 'Monitored Anesthesia Care',
        'mac': 'Monitored Anesthesia Care'
    }

    if text in mapping:
        return mapping[text]

    # Containment / fuzzy logic
    if 'general' in text or 'ga' == text:
        return 'General'

    if 'monitored anesthesia care' in text or text == 'mac' or ' mac ' in text:
        return 'Monitored Anesthesia Care'

    if 'deep' in text:
        return 'Deep'

    if 'moderate' in text or 'conscious sedation' in text or 'procedural sedation' in text:
        return 'Moderate'

    if 'local' in text and 'anesth' in text:
        return 'Local'

    # As a safety: if the model returns any of the allowed values with extra spaces/case
    for allowed in ['Moderate', 'Deep', 'General', 'Local', 'Monitored Anesthesia Care']:
        if allowed.lower() == text:
            return allowed

    return None

### comments
Changes focus on (1) making General the default for rigid/robotic/major airway procedures with anesthesia team or intubation; (2) clarifying that anesthesia-managed MAC/propofol without ETT should be labeled Deep by project convention; (3) preventing mislabeling as Local when only topical anesthesia and low Ramsay are mentioned but absence of systemic sedatives is not explicit—these are now treated as Moderate; (4) emphasizing that presence of an anesthesia provider should block automatic classification as Moderate based solely on midazolam/fentanyl. Also added explicit example-based guidance tied to the error cases and made post-processing robust to small textual variations while strictly mapping to allowed values.

