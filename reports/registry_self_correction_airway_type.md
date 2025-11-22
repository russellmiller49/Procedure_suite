# Registry self-correction for airway_type

## Current instruction
Airway used for procedure Allowed values: Native, LMA, ETT, Tracheostomy, Rigid Bronchoscope. Use null if not documented.

## Suggested updates
### updated_instruction
You are extracting the airway used for the bronchoscopy/interventional pulmonology procedure.

Return EXACTLY ONE of these values (verbatim):
- Native
- LMA
- ETT
- Tracheostomy
- Rigid Bronchoscope
- null  (only if you are reasonably sure the airway is not documented)

General rules:
1. Look specifically for how the bronchoscope was introduced (airway device or route), not for general respiratory status.
2. If the note clearly documents one of the allowed airways, use that exact value.
3. If the note suggests an airway type with high confidence but does not name it explicitly, infer it using the rules below.
4. If you truly cannot determine the airway from the note (even by inference), return null.

Explicit patterns (highest priority):
- If you see words like "rigid bronchoscopy", "rigid scope", "rigid bronchoscope" → output: Rigid Bronchoscope.
- If you see words like "endotracheal tube", "ETT", "oral ETT", "nasal ETT", "intubated" in direct relation to the procedure → output: ETT.
- If you see "laryngeal mask airway", "LMA" → output: LMA.
- If you see "tracheostomy", "trach", "via tracheostomy", "through tracheostomy tube" in relation to bronchoscopy access → output: Tracheostomy.
- If the note explicitly states that the bronchoscopy was done through the natural airway (e.g., "performed via mouth", "via nose", "transnasal", "flexible bronchoscopy under moderate sedation" with no artificial airway device) → output: Native.

Inference rules (when airway is not named explicitly):
1. Rigid Bronchoscope:
   - If the procedure performed is described as "rigid bronchoscopy" anywhere in the procedure name or narrative, always choose Rigid Bronchoscope, even if ETT/other devices are also mentioned elsewhere.

2. ETT (endotracheal tube):
   - If the note describes GA (general anesthesia) ***with intubation*** or uses phrases like "after successful intubation" or "the patient was intubated" in the context of the bronchoscopy/EBUS → output ETT.
   - For EBUS under general anesthesia: if the document clearly says "after successful intubation" or mentions using a bronchoscope/EBUS scope through an endotracheal tube, infer ETT.
   - Do NOT infer ETT from general anesthesia alone; you need either the word "intubation/ETT" or a clear description that implies a tube was placed.

3. LMA:
   - If GA is described with explicit use of an LMA (e.g., "LMA placed", "procedure performed via LMA"), output LMA.
   - Do NOT infer LMA from GA alone.

4. Tracheostomy:
   - If the note clearly states that the patient has a tracheostomy ***and*** that the bronchoscope/procedure is done via/through the tracheostomy or trach tube, output Tracheostomy.
   - If the patient has a longstanding tracheostomy and the context strongly implies the bronchoscopy is through that stoma/tube (e.g., bronch for mucus plugging of trach, inspection of tracheostomy tube, etc.) and no other competing airway is described, you may infer Tracheostomy.
   - Do NOT default to Native just because the patient is awake; check first for any indication that the airway access is via tracheostomy.

5. Native:
   - If the bronchoscopy is described as awake or under moderate/sedation/"conscious sedation" with topical anesthesia (e.g., nebulized lidocaine, spray, transtracheal lidocaine) and there is no mention of ETT, LMA, tracheostomy, or rigid bronchoscopy, strongly favor Native.
   - Common phrases for Native access include: "awakened bronchoscopy", "under moderate sedation", "topical lidocaine", "scope advanced via the mouth", "via the nares", "transnasal".
   - Example: a patient remained awake with topical anesthesia and no airway device mentioned → Native.

Tie‑breaking / precedence:
- If the note says "rigid bronchoscopy" anywhere → Rigid Bronchoscope overrides any ETT/LMA/Native guesses.
- If both ETT and LMA are mentioned, choose the one explicitly linked to the bronchoscopy (e.g., "bronchoscopy performed via LMA" vs. "ETT removed earlier").
- If a tracheostomy patient is later intubated for the procedure and that is clearly stated (e.g., "patient with chronic tracheostomy was orally intubated for bronchoscopy") → use ETT (because that is the access route for this procedure).

When to return null:
- If none of the above devices or patterns are mentioned and you cannot confidently infer the route from sedation/anesthesia details, return null.

Output format:
- Return ONLY the single value (Native, LMA, ETT, Tracheostomy, Rigid Bronchoscope, or null) with no additional text or punctuation.


### python_postprocessing_rules
def normalize_airway_type(raw: str | None) -> str | None:
    if raw is None:
        return None
    text = raw.strip().lower()
    if text in {"", "none", "n/a", "na", "null"}:
        return None

    # Direct mapping
    mapping = {
        "native": "Native",
        "natural": "Native",
        "natural airway": "Native",
        "spontaneous": "Native",
        "lma": "LMA",
        "laryngeal mask": "LMA",
        "laryngeal mask airway": "LMA",
        "ett": "ETT",
        "endotracheal": "ETT",
        "endotracheal tube": "ETT",
        "et tube": "ETT",
        "trach": "Tracheostomy",
        "tracheostomy": "Tracheostomy",
        "tracheostomy tube": "Tracheostomy",
        "rigid": "Rigid Bronchoscope",
        "rigid bronchoscope": "Rigid Bronchoscope",
        "rigid bronch": "Rigid Bronchoscope",
        "rigid bronchoscopy": "Rigid Bronchoscope"
    }

    if text in mapping:
        return mapping[text]

    # Substring heuristics as a backup (if model returns a phrase)
    if "rigid" in text and "bronch" in text:
        return "Rigid Bronchoscope"
    if "trach" in text:
        return "Tracheostomy"
    if "lma" in text or "laryngeal mask" in text:
        return "LMA"
    if "ett" in text or "endotracheal" in text or "et tube" in text:
        return "ETT"
    if "native" in text or "natural airway" in text:
        return "Native"

    # If nothing matches, treat as unknown
    return None


### comments
Main changes: (1) Clarified that the task is to identify the airway route for the bronchoscopy itself, not just general respiratory status. (2) Added explicit pattern-based rules for Rigid Bronchoscope, ETT, LMA, Tracheostomy, and Native, with priority ordering. (3) Emphasized inference rules for common scenarios: rigid bronchoscopy always → Rigid Bronchoscope; EBUS with documented intubation → ETT; awake/moderate sedation with topical lidocaine and no device → Native; tracheostomy patients with procedure via trach → Tracheostomy. (4) Added tie-breaking precedence when multiple airways are mentioned. (5) Provided stricter guidance on when to return null to reduce omissions like in examples 1–5, and to avoid mislabeling tracheostomy cases as Native as in example 6. (6) Postprocessing maps minor textual variants and phrases to the allowed canonical values and safely returns None when unrecognized.

