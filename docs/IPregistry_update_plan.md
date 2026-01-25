# IP Registry + Coding Update Plan (Procedure Suite)

Last updated: 2026-01-24

This repo is transitioning to **zero‑knowledge client‑side pseudonymization**: the browser scrubs PHI and the server acts as a **stateless logic engine** (**Text In → Codes Out**).

This plan targets the **extraction‑first** pipeline:
`note_text → RegistryRecord → deterministic RegistryRecord→CPT → registry schema validation`.

---

## 0) Non‑Negotiables / Constraints

- **Authoritative API endpoint:** `POST /api/v1/process` (`modules/api/routes/unified_process.py`)
- **Pipeline mode:** `PROCSUITE_PIPELINE_MODE=extraction_first` is required and enforced on startup (`modules/api/fastapi_app.py`).
- **Deterministic CPT derivation must not parse the raw note.** All rules in `modules/coder/domain_rules/registry_to_cpt/coding_rules.py` must consume `RegistryRecord` only.
- **Schema drives code.** `RegistryRecord` is generated dynamically from `data/knowledge/IP_Registry.json` (`modules/registry/schema.py`).

---

## 1) Repo Reality Check (What Already Exists)

These items are already present and should be treated as “done”, unless regression bugs appear:

- **Menu/CPT block masking:** `modules/registry/processing/masking.py:mask_extraction_noise()`.
- **Granular → aggregate propagation (single place):** `modules/registry/application/registry_service.py:_apply_granular_up_propagation()` via `modules/registry/schema_granular.py:derive_procedures_from_granular()`.
- **TBNA normalization guardrails:** `modules/registry/schema_granular.py` migrates non‑station “TBNA” to `peripheral_tbna` and suppresses phantom `tbna_conventional` when EBUS is present.
- **Stent evidence guardrails (avoid “stent in good position” → placement):** `modules/domain/coding_rules/coding_rules_engine.py` (R004 stent 4‑gate).
- **Master index preference for RVUs:** `modules/common/knowledge.py:get_rvu()` prefers `master_code_index` when present.

---

## 2) High‑Priority Gaps to Close (Implement First)

### 2.1 Release gating: “Freeze, Map, and Gate”

Goal: prevent knowledge/schema refactors from silently breaking extraction or coding.

- [x] Add a **knowledge inventory map** (single‑source‑of‑truth matrix) → `docs/KNOWLEDGE_INVENTORY.md`
  - **Code lookup + RVUs:** `data/knowledge/ip_coding_billing_v3_0.json` (`master_code_index`)
  - **Terminology:** `data/knowledge/ip_coding_billing_v3_0.json` (`synonyms`, `terminology_mappings`)
  - **Registry schema:** `data/knowledge/IP_Registry.json`
  - **Golden knowledge (legacy / reference):** `ip_golden_knowledge_v2_2.json`
- [x] Add a repo‑level **knowledge release checklist** → `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`
  - `make validate-schemas`
  - `make test`
  - KB version + checksum check
- [x] Add a no‑network **release validation script** → `scripts/validate_knowledge_release.py`
  - Make target: `make validate-knowledge-release`

Notes:
- The KB semantic version is stored in `data/knowledge/ip_coding_billing_v3_0.json` as `"version": "3.0"`.
- KB loaders enforce filename semver ↔ internal `"version"` by default.
  - Override (dev only): `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`

### 2.2 Deterministic RegistryRecord → CPT correctness fixes

Goal: eliminate known mismaps/false positives in the deterministic derivation path.

- [x] **BLVR valve family mapping**
  - Valve placement: `31647` (initial lobe) + `31651` (each additional lobe)
  - Valve removal: `31648` (initial lobe) + `31649` (each additional lobe)
- [x] **Chartis (balloon occlusion) bundling**
  - Derive `31634` when granular Chartis measurements exist.
  - Suppress `31634` when Chartis is performed in the same lobe as valve placement (bundled).
  - When Chartis is documented in a distinct lobe, allow and flag modifier/documentation requirements.
- [x] **Moderate sedation threshold**
  - Suggest `99152` (and `+99153` when appropriate) only when:
    - `sedation.type == "Moderate"`
    - `sedation.anesthesia_provider == "Proceduralist"`
    - `sedation.intraservice_minutes >= 10` (or computed from start/end times)
  - If `<10`, suppress and add a QA warning (“below threshold”).

### 2.3 Registry schema small enhancement (Pathology)

Goal: avoid dropping pathology values that use ranges/operators.

- [x] Keep `pathology_results.pdl1_tps_percent` as `number|null` (0–100)
- [x] Add `pathology_results.pdl1_tps_text` as `string|null` to support values like `"<1%"`, `">50%"`.

### 2.4 Phase 1–2 Knowledge Hygiene (Single Source of Truth)

Goal: eliminate drift by ensuring runtime lookups use the canonical KB sections.

- [x] **Filename/version alignment**
  - Canonical KB path: `data/knowledge/ip_coding_billing_v3_0.json`
  - Deprecation entry: `metadata.deprecations[]` documents the old `v2_9` path.
- [x] **Authoritative code metadata/RVUs**
  - `modules/coder/adapters/persistence/csv_kb_adapter.py` now loads `ProcedureInfo` from `master_code_index` (not `fee_schedules`).
- [x] **Authoritative synonym layer**
  - `modules/autocode/ip_kb/ip_kb.py` now reads phrase lists from KB `synonyms` (with safe fallback to legacy canonical rules).
  - Adding a new navigation platform synonym is now a **one‑file edit**: `data/knowledge/ip_coding_billing_v3_0.json`.

### 2.5 Phase 3 — Standardize Rule Outputs (coding_support)

Goal: make deterministic coding behavior explainable and reviewable without parsing free-text warnings.

- [x] Populate `registry.coding_support` deterministically in the extraction-first pipeline:
  - `coding_summary.lines[]` with `selection_status`, `selection_reason`, and optional `note_spans`
  - `coding_rationale.rules_applied[]` + per-code `qa_flags[]` derived from deterministic rule warnings
- [x] Keep deterministic derivation warning text stable (tests assert substrings like `Suppressed 31629` and `Modifier 59`).

Implementation:
- Builder: `modules/registry/application/coding_support_builder.py`
- Wiring: `modules/registry/application/registry_service.py:_extract_fields_extraction_first()`

### 2.6 Phase 4 — “Golden Thread” Traceability + Provider Normalization

Goal: link each billed CPT line back to structured objects and evidence spans, and normalize providers without breaking compatibility.

- [x] Schema: add `billing.cpt_codes[].derived_from` (registry pointers) + `billing.cpt_codes[].evidence` (V3 evidence contract)
- [x] Schema: add `providers_team[]` while keeping legacy `providers` for backward compatibility
- [x] Runtime:
  - `billing.cpt_codes[]` now includes `derived_from` + `evidence` when available
  - `providers_team` auto-populates from `providers` during `RegistryRecord` validation

---

## 3) Acceptance Checks (Concrete Commands)

- Schema integrity: `make validate-schemas`
- Unit tests: `make test`
- Single note smoke: `python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct`

---

## 4) Backlog (Next Phases)

These are valuable but larger than a single implementation pass:

- Rules DSL unification (`ip_golden_knowledge.rules` vs KB `qa_rules` / `bundling_rules`)
- Full NCCI PTP import with modifier indicators + effective dates
- Pathology extraction knowledge layer + parser (histology/NGS/PD‑L1)
