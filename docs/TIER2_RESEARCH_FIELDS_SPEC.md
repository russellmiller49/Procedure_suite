# Tier 2 Research Fields (Registry V3) — Field Spec

This document is the single source of truth for **Tier 2 research/quality fields** added or backstopped in the v3 `RegistryRecord` (extraction-first pipeline).

**Non-negotiables**
- **Evidence-first:** any populated Tier 2 field should have an evidence span (`record.evidence[...]`) so the UI can highlight it and integrity checks can keep it.
- **Narrative > templates/checkboxes:** deterministic derivations should prefer active-voice narrative over templated “none” statements.
- **Tools ≠ intent:** do not infer tool-in-lesion confirmation (or other high-impact claims) from equipment lists alone.

## Fields

### A) Navigation per-target detail (comparative effectiveness-ready)

#### 1) CT characteristics (density/consistency)
- **Path:** `registry.granular_data.navigation_targets[].ct_characteristics`
- **Type:** `"Solid" | "Part-solid" | "Ground-glass" | "Cavitary" | "Calcified" | null`
- **Derivation (explicit-only):**
  - Deterministic regex extracts when explicit CT descriptors appear in the target header/section text.
  - “Solid” is only set when lesion-context terms (nodule/lesion/mass/opacity) are present to avoid unrelated “solid” mentions.
- **Evidence key pattern:** `granular_data.navigation_targets.{index}.ct_characteristics`

#### 2) Distance from pleura (mm)
- **Path:** `registry.granular_data.navigation_targets[].distance_from_pleura_mm`
- **Type:** `float | null` (mm; `0.0` when explicitly “abutting pleura”)
- **Derivation (explicit-only):**
  - Extract numeric `mm/cm` distances from the target header/section text.
  - Map explicit “abutting/contacting/touching pleura” to `0.0`.
- **Evidence key pattern:** `granular_data.navigation_targets.{index}.distance_from_pleura_mm`

#### 3) PET SUV max (per target)
- **Path:** `registry.granular_data.navigation_targets[].pet_suv_max`
- **Type:** `float | null`
- **Derivation (explicit-only):**
  - Extract numeric `SUV`/`SUV max` values when explicitly present in the target header/section text.
- **Evidence key pattern:** `granular_data.navigation_targets.{index}.pet_suv_max`

#### 4) Bronchus sign (per target)
- **Path:** `registry.granular_data.navigation_targets[].bronchus_sign`
- **Type:** `"Positive" | "Negative" | "Not assessed" | null`
- **Derivation (explicit-only):**
  - Extract polarity only when the phrase “bronchus sign … positive/negative/present/absent” is explicitly documented.
  - Treat explicit “air bronchogram present/absent” as bronchus sign positive/negative.
  - Treat explicit “not assessed/unknown/indeterminate” as missing (leave `null`).
- **Evidence key pattern:** `granular_data.navigation_targets.{index}.bronchus_sign`

#### 5) Registration error (mm)
- **Path:** `registry.granular_data.navigation_targets[].registration_error_mm`
- **Type:** `float | null`
- **Derivation (explicit-only):**
  - Extract numeric `registration … error … X mm` or conservative `error of X mm` when “registration” is also present.
- **Evidence key pattern:** `granular_data.navigation_targets.{index}.registration_error_mm`

#### 6) Tool-in-lesion confirmation + method (per target)
- **Paths:**
  - `registry.granular_data.navigation_targets[].tool_in_lesion_confirmed`
  - `registry.granular_data.navigation_targets[].confirmation_method`
- **Types:**
  - `tool_in_lesion_confirmed`: `bool | null`
  - `confirmation_method`: `"CBCT" | "Augmented fluoroscopy" | "Fluoroscopy" | "Radial EBUS" | "None" | null`
- **Derivation (explicit-only):**
  - Set `tool_in_lesion_confirmed=true` only when the note explicitly confirms tool-in-lesion (“tool-in-lesion/TIL … confirmed/achieved/yes/positive”).
  - Set `tool_in_lesion_confirmed=false` only when explicitly negated (“TIL not confirmed/failed/negative/no”).
  - Set `confirmation_method` only when `tool_in_lesion_confirmed=true` and a method is explicitly mentioned near the confirmation statement.
- **Evidence key patterns:**
  - `granular_data.navigation_targets.{index}.tool_in_lesion_confirmed`
  - `granular_data.navigation_targets.{index}.confirmation_method`

#### 7) Tool-in-lesion roll-up (procedure-level)
- **Paths:**
  - `registry.procedures_performed.navigational_bronchoscopy.tool_in_lesion_confirmed`
  - `registry.procedures_performed.navigational_bronchoscopy.confirmation_method`
- **Types:**
  - `tool_in_lesion_confirmed`: `bool | null`
  - `confirmation_method`: `"Radial EBUS" | "CBCT" | "Fluoroscopy" | "Augmented Fluoroscopy" | "None" | null`
- **Derivation:**
  - When missing at procedure-level, roll up from **per-target** values (explicit-only) and copy evidence spans.
  - Note: enum differs between per-target and procedure-level (capitalization of “Augmented Fluoroscopy”).
- **Evidence keys:**
  - `procedures_performed.navigational_bronchoscopy.tool_in_lesion_confirmed`
  - `procedures_performed.navigational_bronchoscopy.confirmation_method`

### B) Complications (quality-ready)

#### 8) Pneumothorax intervention level
- **Path:** `registry.complications.pneumothorax.intervention[]`
- **Type:** `list[ "Observation" | "Aspiration" | "Pigtail catheter" | "Chest tube" | "Heimlich valve" | "Surgery" ] | null`
- **Derivation (explicit-only, narrative-first):**
  - Only derive when pneumothorax is mentioned in narrative, and an intervention term appears in pneumothorax context.
  - Do not infer from generic “chest tube kit” equipment lists.
- **Evidence key:** `complications.pneumothorax.intervention`

### C) EBUS station detail (guidelines-ready)

#### 9) Station size + technique evidence attachment
- **Paths:**
  - `registry.granular_data.linear_ebus_stations_detail[].short_axis_mm`
  - `registry.granular_data.linear_ebus_stations_detail[].long_axis_mm`
  - `registry.granular_data.linear_ebus_stations_detail[].needle_gauge`
  - `registry.granular_data.linear_ebus_stations_detail[].number_of_passes`
- **Types:** numeric fields (`float/int | null`)
- **Derivation:**
  - Values may be extracted/normalized by the station detail deterministic parser; evidence spans are attached when values are derived from station blocks.
- **Evidence key pattern:** `granular_data.linear_ebus_stations_detail.{index}.{field}`
