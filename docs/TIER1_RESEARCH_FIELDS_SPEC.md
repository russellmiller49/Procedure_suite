# Tier 1 Research Fields (Registry V3) — Field Spec

This document is the single source of truth for **Tier 1 research-grade fields** added to the v3 `RegistryRecord` (extraction-first pipeline).

**Non-negotiables**
- **Evidence-first:** any populated Tier 1 field must have an evidence span (`record.evidence[...]`) so the UI can highlight it and integrity checks can keep it.
- **Narrative > templates/checkboxes:** deterministic derivations should prefer active-voice narrative over templated “none” statements.
- **Tools ≠ intent:** do not infer high-impact claims from equipment lists alone.

## Fields

### 1) CT bronchus sign
- **Path:** `registry.clinical_context.bronchus_sign`
- **Type:** `"Positive" | "Negative" | "Not assessed"`
- **Derivation (explicit-only):**
  - Deterministic regex extracts polarity when “bronchus sign … positive/negative/present/absent” is documented.
  - Treat explicit “air bronchogram present/absent” as bronchus sign positive/negative.
  - Do not infer from lesion location, navigation system, or rEBUS findings.
- **Evidence key:** `clinical_context.bronchus_sign` (span should include the polarity statement)

### 2) ECOG / Zubrod performance status
- **Paths:**
  - `registry.clinical_context.ecog_score` (preferred when a single integer)
  - `registry.clinical_context.ecog_text` (fallback for ranges like `"0-1"`)
- **Types:**
  - `ecog_score`: `int | null` (0–4)
  - `ecog_text`: `str | null`
- **Derivation (explicit-only):**
  - Extract only when “ECOG …” or “Zubrod …” is explicitly documented.
  - Do **not** coerce a range (e.g., `"0-1"`) into a single score; store it in `ecog_text`.
- **Evidence keys:**
  - `clinical_context.ecog_score`
  - `clinical_context.ecog_text`

### 3) Radial EBUS view / probe position
- **Path:** `registry.procedures_performed.radial_ebus.probe_position`
- **Type:** `"Concentric" | "Eccentric" | "Adjacent" | "Not visualized" | null`
- **Derivation:**
  - Primary: extracted by the engine (when available).
  - Backstop: deterministic regex near “radial EBUS / rEBUS …” phrases.
  - Do not infer from the presence of a radial probe mention alone; keep `probe_position=null` if the view is not described.
- **Evidence key:** `procedures_performed.radial_ebus.probe_position`

### 4) Lymphocyte adequacy per EBUS station
- **Path:** `registry.granular_data.linear_ebus_stations_detail[].lymphocytes_present`
- **Type:** `bool | null` (`null` = not assessable from the note)
- **Derivation (explicit-only, station-scoped):**
  - `true` when ROSE/pathology language indicates lymphocytes/lymphoid tissue is present/adequate/seen.
  - `false` when language indicates no/scant/rare lymphocytes, “blood only”, or explicitly non-diagnostic due to inadequate lymphoid material.
  - Leave `null` when station text does not support either conclusion.
- **Evidence key pattern:** `granular_data.linear_ebus_stations_detail.{index}.lymphocytes_present`

### 5) Nashville bleeding grade (0–4)
- **Path:** `registry.complications.bleeding.bleeding_grade_nashville`
- **Type:** `int | null` (0–4; `0` = none)
- **Derivation (narrative-first):**
  - Prefer explicit “Nashville grade X” when present.
  - Otherwise derive from documented interventions:
    - **1:** suction-only bleeding control (with bleeding context)
    - **2:** wedge / cold saline / topical vasoconstrictor (e.g., epinephrine)
    - **3:** balloon tamponade / endobronchial blocker / procedure aborted for bleeding
    - **4:** transfusion, IR embolization, surgery (in bleeding context)
  - Do not downgrade due to templated “COMPLICATIONS: None” when narrative contradicts.
- **Related behavior:** when grade > 0, set `registry.complications.bleeding.occurred=true` and ensure complications summary reflects bleeding.
- **Evidence key:** `complications.bleeding.bleeding_grade_nashville`
