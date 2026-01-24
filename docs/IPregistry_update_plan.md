Single Codex Plan: Modernize IP_Registry.json without breaking the pipeline

Update plan for  data/knowledge/IP_Registry.json 

0) Guardrails and scope (non-negotiables)

Do not delete granular_data yet. It is explicitly present for backward compatibility, and code paths still expect it. Replace-in-place deletion is a breaking change.

Keep JSON Schema Draft-07 ("$schema": "http://json-schema.org/draft-07/schema#"), so use definitions (not $defs) for shared enums/refs (unless you intentionally upgrade draft + all validators).

Make changes in two layers:

Layer A (safe now): Add fields + add consistency constraints that prevent impossible states (“zombie records”).

Layer B (later, versioned): Full deprecation/removal of granular_data + move everything under procedure objects.

1) First, inventory the consumers (so we don’t break them)

Codex steps:

Locate all schema loaders/walkers (these are the “blast radius”):

Ripgrep for: IP_Registry.json, _SCHEMA_PATH, granular_data, jsonschema.validate, RegistryRecord.model_json_schema().

Confirm the primary “v3” consumers read data/knowledge/IP_Registry.json:

- modules/registry/schema.py (dynamic Pydantic model builder; does NOT resolve $ref)
- modules/registry/prompts.py (legacy/v2 field instructions read top-level schema.properties/enums; v3 prompt embeds RegistryRecord.model_json_schema())
- modules/registry/self_correction/prompt_improvement.py (reads top-level enums from schema.properties)

Clarify which file is “truth” today:

data/knowledge/IP_Registry.json is referenced as the schema definition in docs and code paths.

schemas/IP_Registry.json is a legacy *flat* schema used by modules/registry_cleaning/ (and some tests) and is intentionally out-of-sync with the v3 nested schema.

Deliverable: a short “Schema Consumer Map” markdown note listing every module/script that reads the schema and what it expects (inline enums vs refs, flat vs nested, etc.).

2) Decide the schema maintenance strategy (avoid $ref surprises)

Important constraint (current repo reality): the dynamic Pydantic model builder in modules/registry/schema.py and other utilities DO NOT resolve $ref. Introducing $ref into the runtime schema will silently break type generation/prompt generation.

Because some utilities walk schema properties directly (and will not resolve $ref), you have two viable approaches:

Option A (recommended): Source schema + compiled schema

Create a new canonical “source” schema that uses definitions + $ref to remove redundancy.

Add a small build script that dereferences/expands it into the fully-expanded runtime schema (no refs), written to:

data/knowledge/IP_Registry.json (runtime/validator input), and

(optionally) a separate generated artifact for tools that require a single file (do NOT overwrite the legacy flat schemas/IP_Registry.json unless you also migrate modules/registry_cleaning/).

Update Makefile / docs so it’s obvious which is generated.

This gives you maintainability and keeps downstream code that expects inline enums safe.

Option B: Teach consumers to resolve $ref

Update schema walkers/generators to resolve $ref (especially anything that reads enums/descriptions).

Higher risk, broader code changes.

Codex instruction: implement Option A unless you confirm no code depends on inline enums anywhere.

3) Layer A (safe now): Fix “split-brain” inconsistencies without removing data

Goal: prevent “performed=false but detail exists” and “granular detail exists but performed missing”.

Codex steps (Draft-07 if/then rules at the root, using allOf so you can add multiple rules cleanly):

Granular ⇒ performed must be true

If granular_data.linear_ebus_stations_detail has minItems: 1, then require:

procedures_performed.linear_ebus.performed: true

Repeat pattern for other granular arrays that imply a procedure occurred (e.g., navigation_targets ⇒ navigational_bronchoscopy.performed=true, blvr_valve_placements ⇒ blvr.performed=true, etc.). 

IP_Registry

performed=false ⇒ detail arrays must be empty/null

If procedures_performed.linear_ebus.performed is false, then enforce maxItems: 0 on:

procedures_performed.linear_ebus.stations_sampled

procedures_performed.linear_ebus.stations_planned

procedures_performed.linear_ebus.stations_detail

granular_data.linear_ebus_stations_detail

Apply similar “no detail when not performed” constraints for navigation and other procedures where you have split storage.

Important: do not require that stations arrays are non-empty when performed=true (too rigid for “EBUS performed, no nodes sampled” notes). Keep the constraints focused on impossible states, not completeness.

4) Layer A: Clinical refinements that won’t break existing data
A) Airway device sizing (ETT vs DLT vs Rigid)

Current schema has airway_type + ett_size limited 5.0–10.0, which fails DLT sizing. 

IP_Registry

Codex steps:

Keep existing fields for compatibility:

procedure_setting.airway_type

procedure_setting.ett_size

Add new fields (all optional):

procedure_setting.airway_device_type: enum ETT | DLT | Rigid | Tracheostomy | LMA | iGel | Native | Other | null

procedure_setting.ett_size_mm: number 5.0–10.0

procedure_setting.dlt_size_fr: integer 26–45

procedure_setting.rigid_barrel_size_mm: number (reasonable range)

Add Draft-07 conditionals:

if airway_device_type==ETT → ett_size_mm range applies

if airway_device_type==DLT → dlt_size_fr range applies
Keep them non-required so extraction can still pass when not documented.

B) Sedation medications as structured objects

Keep sedation.agents_used (back compat), add:

sedation.medications: array of objects with:

agent (string)

total_dose (number|null)

unit (enum: mg|mcg|g|mL|units|other|null)

optional infusion: infusion_rate, infusion_unit, duration_minutes

No hard requirements; this is for analytics readiness.

C) Specimen linkage via stable IDs

Add optional IDs without making LLM extraction fail:

Add target_id (uuid/string) to:

procedures_performed.linear_ebus.stations_detail[]

granular_data.linear_ebus_stations_detail[]

granular_data.navigation_targets[]

Add source_target_id to:

specimens.specimens_collected[]

granular_data.specimens_collected[] (if used)

Also add a note in descriptions: “UI/postprocessing assigns/maintains IDs; extraction may omit.”

D) Complications: add CTCAE grading without replacing existing fields

Do not rip out your current complication_list and nested bleeding/PTX structures. 

IP_Registry


Add:

complications.events[]: objects with:

type (string / enum of major complication types)

ctcae_grade (integer 1–5)

interventions (array of strings)

notes
This is parallel, migration later.

E) Datetime fields (keep existing date + time)

Add:

procedure_start_datetime / procedure_end_datetime (format: date-time, nullable)
Keep the old:

procedure_date, procedure_start_time, procedure_end_time (existing) 

IP_Registry

F) MRN regex relaxation + future-proofing for pseudonymization

Relax patient_mrn pattern to something like: ^[A-Za-z0-9\-_]{2,30}$ (still conservative). 

IP_Registry


Add optional:

patient_linkage_id (string) for your client-side pseudonymization direction (do not require it yet).

5) Layer A: Minimal conditional integrity rules (only the “safe” ones)

Add Draft-07 conditionals that prevent nonsensical combinations:

Smoking

If patient_demographics.smoking_status == "Never" → pack_years must be 0 or null.

Complications

If complications.any_complication == false → complication_list.maxItems = 0 (do not over-constrain the nested objects yet).

Trainees

If providers.trainee_present == true → require at least one non-empty name among:

fellow_name OR assistant_name
(Do not force which role; keep flexible.)

6) Update the code + tests in lockstep (so CI stays green)

Codex steps:

Schema files (avoid accidental “sync”)

- data/knowledge/IP_Registry.json = v3 nested schema used by extraction-first + dynamic RegistryRecord model (modules/registry/schema.py).
- schemas/IP_Registry.json = legacy flat schema used by modules/registry_cleaning/ and related tests.

Action: explicitly document that these are different and do not attempt to keep them identical unless you also migrate the cleaning pipeline.

Update schema-driven tooling that reads enums

Anything that walks the schema to build prompts/instructions should either:

read the compiled (dereferenced) schema, or

be upgraded to resolve refs.
The legacy prompt path reads data/knowledge/IP_Registry.json. 

modules/registry/prompts

Add tests

Add targeted tests that validate the new if/then guardrails and new fields:

granular EBUS detail present ⇒ performed must be true

performed false ⇒ detail arrays empty

never-smoker with pack_years>0 fails schema validation

DLT sizing accepted

Run:

make test

schema validation script(s) used by CI/Makefile (if any)

If make validate-schemas is still using Draft202012Validator for a Draft-07 schema, update scripts/validate_jsonschema.py to select Draft7Validator when "$schema" indicates draft-07 (so validation actually runs).

Add a tiny migration/cleanup helper (optional but recommended)

A script that “sanitizes” old records into compliance:

if performed=false → wipe detail arrays

if granular arrays exist → set performed=true
This keeps old stored JSON from failing after schema tightening.

7) Layer B (versioned future): Deprecate and remove granular_data

Once Layer A is stable and consumers are updated:

Introduce a new schema major/minor version (e.g., 2.2.0 or 3.0.0) where:

All “granular” arrays move under their procedure objects (encapsulation).

granular_data becomes deprecated → then removed.

Provide a one-time migration script:

granular_data.* → procedures_performed.*.<moved_field>

Update extraction + reconciliation code accordingly.

What Codex should deliver (checklist)

 Consumer map + decision on source/compiled strategy

 Layer A schema updates (new fields + safe integrity rules)

 No-breaking change handling for granular_data (consistency rules, not deletion)

 Updated schema sync story (data/knowledge vs schemas)

 Tests proving new guardrails work

 Optional migration sanitizer for old JSON
