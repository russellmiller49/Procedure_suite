# CODEX PR CHECKLIST — Extraction‑First Registry + Deterministic CPT + **RAW‑ML Auditor**

Use this checklist for any PR that touches the extraction-first registry pipeline, deterministic Registry→CPT rules, ML auditing, or self-correction.

---

## PR metadata
- [ ] PR title clearly states scope (e.g., “Phase 1.3 RawMLAuditor wiring”)
- [ ] PR description links to `docs/CODEX_IMPLEMENTATION_PLAN.md` sections touched
- [ ] PR includes “How to test” commands + expected outcomes
- [ ] Any new env vars are documented in README and listed in PR description

---

## Non‑negotiable invariants (blockers if violated)
### Extraction purity
- [ ] Extraction-first path does **not** pass CPT hints into extraction
  - [ ] No `verified_cpt_codes`
  - [ ] No ML-predicted codes
  - [ ] No orchestrator output injected into extractor context
- [ ] No `_merge_cpt_fields_into_record` (or equivalent) runs in extraction-first mode

### Auditor purity (RAW‑ML only)
- [ ] Registry audit **does not** call `SmartHybridOrchestrator.get_codes()`
- [ ] Registry audit **does** call raw predictor directly (e.g., `MLCoderPredictor.classify_case(raw_note_text)`)
- [ ] Audit path never calls rule validation (e.g., `rules.validate(... strict=True)`) and never triggers LLM fallback
- [ ] Auditor always receives **raw note text**, not focused/summarized text (summarizer trap avoided)

### Rules purity
- [ ] Deterministic Registry→CPT rules accept **only** `RegistryRecord` (no `note_text`)
- [ ] No rule reads/parses `note_text` internally (no regex on note text inside rules)
- [ ] If a rule needs missing evidence, it emits a warning and extraction/derivation is improved instead

### Up‑propagation location
- [ ] Granular→aggregate consistency is enforced **only** in `derive_procedures_from_granular(record)`
- [ ] No parallel `up_propagate_flags()` / “normalization step” was introduced

---

## Feature flags / behavior gating
- [ ] `PROCSUITE_PIPELINE_MODE` defaults to `"current"` and legacy behavior is unchanged
- [ ] `"extraction_first"` enables the new flow (extraction → deterministic CPT → raw ML audit → optional self-correct)
- [ ] `REGISTRY_EXTRACTION_ENGINE` respected:
  - [ ] `"engine"`
  - [ ] `"agents_focus_then_engine"`
  - [ ] `"agents_structurer"`
- [ ] Auditor controls respected:
  - [ ] `REGISTRY_AUDITOR_SOURCE` (`raw_ml` / `disabled`)
  - [ ] `REGISTRY_ML_AUDIT_TOP_K`
  - [ ] `REGISTRY_ML_AUDIT_MIN_PROB`
  - [ ] `REGISTRY_ML_SELF_CORRECT_MIN_PROB`
  - [ ] `REGISTRY_ML_AUDIT_USE_BUCKETS`
- [ ] `REGISTRY_SELF_CORRECT_ENABLED` is default off and safe when on

### Registry model bootstrap (S3 artifacts; local + Railway)
- [ ] Startup attempts `modules/registry/model_bootstrap.ensure_registry_model_bundle()` and does **not** hard-fail if bootstrap is unavailable (degraded start is OK)
- [ ] `MODEL_BACKEND` and `REGISTRY_RUNTIME_DIR` behavior is documented and unchanged
- [ ] `MODEL_BUNDLE_S3_URI_ONNX` supports:
  - [ ] tarball bundle URIs (`.../deploy/registry/<version>/onnx/bundle.tar.gz`)
  - [ ] prefix URIs (e.g. `s3://procedure-suite-models/classifiers/`), which auto-pick the newest `model_int8.onnx`
- [ ] Prefix-based bootstraps write `.bootstrap_state.json` so a broad prefix can refresh to newer exports without changing env vars

---

## Code review checkpoints by module

### RegistryService (extraction-first order)
- [ ] Extraction-first order is exactly:
  1) `extract_record(raw_note_text)` (no CPT hints)
  2) `registry_to_cpt_engine.apply(record)`
  3) `RawMLAuditor.classify(raw_note_text)` (raw predictor)
  4) build audit comparison report
  5) optional self-correction loop (if enabled)
  6) finalize output
- [ ] Legacy/current path remains intact and unchanged under `"current"`

### RAW‑ML Auditor wrapper
- [ ] Wrapper lives in `modules/registry/audit/…` (or equivalent)
- [ ] Wrapper uses repo-native predictor + types (no hybrid veto logic)
- [ ] Audit set logic matches config:
  - [ ] buckets (high_conf + gray_zone) when enabled
  - [ ] else top‑k + min_prob from raw predictions
- [ ] Output includes enough debug info (difficulty, top predictions, config used) without leaking PHI in logs

### Deterministic Registry→CPT rules engine
- [ ] Existing rules file moved/refactored:
  - [ ] `data/rules/coding_rules.py` moved to `modules/coder/domain_rules/registry_to_cpt/…`
  - [ ] Shim re-export remains (temporary) to avoid breaking imports
- [ ] Each derived code includes: `code`, `rationale`, `rule_id`, `confidence`
- [ ] Bundling decisions happen only in deterministic CPT derivation (not in evidence extraction, not in auditor)

### `derive_procedures_from_granular`
- [ ] Function flips aggregate `.performed` flags based on granular evidence
- [ ] Function adds warnings when performed=True but required details are missing
- [ ] Function is called:
  - [ ] after initial extraction
  - [ ] after any self-correction patch application

### Agents focusing integration (if included)
- [ ] Focused/summarized text used only for deterministic extraction
- [ ] Raw ML auditor still runs on raw note text
- [ ] Fallback to full note when focusing fails is implemented + tested

### Self‑correction loop (if included)
- [ ] Trigger uses **RAW‑ML** high-confidence signals only
- [ ] Field/path allowlist exists and is enforced
- [ ] Evidence quotes are verified verbatim against text before applying patch
- [ ] Patch application re-runs:
  - [ ] `derive_procedures_from_granular`
  - [ ] deterministic CPT derivation
  - [ ] audit comparison
- [ ] Auto-corrections are explicitly labeled in output warnings/metadata

### OpenAI‑compat LLM adapter (if included)
- [ ] LLM provider switch via `LLM_PROVIDER` works
- [ ] `OPENAI_OFFLINE=1` (or equivalent) prevents network calls in tests
- [ ] Existing Gemini path remains functional

---

## Tests (must be green)
- [ ] New tests exist and pass:
  - [ ] `test_extraction_first_flow.py` (no CPT seeding)
  - [ ] `test_auditor_raw_ml_only.py` (no orchestrator; no rules.validate)
  - [ ] `test_registry_to_cpt_rules_pure_registry.py` (rules take only RegistryRecord)
  - [ ] `test_derive_procedures_from_granular_consistency.py` (up-propagation works)
  - [ ] `test_self_correction_loop.py` (safety + success cases)
- [ ] Tests explicitly “trip” if:
  - [ ] `SmartHybridOrchestrator.get_codes()` is called in registry audit path
  - [ ] rule validation is invoked during audit
- [ ] CI commands run locally and in CI:
  - [ ] `pytest`
  - [ ] `ruff` / `mypy` / any repo-specific checks
- [ ] Fixtures are synthetic only; no real PHI

---

## Docs updates (required when behavior/config changes)
- [ ] README updated with new env vars + examples
- [ ] `docs/ARCHITECTURE.md` updated with extraction-first + raw-ML audit flow
- [ ] `docs/CODEX_IMPLEMENTATION_PLAN.md` updated if plan changed
- [ ] `docs/CODEX_PR_CHECKLIST.md` updated if new invariants were added

---

## Merge readiness
- [ ] Reviewer can answer “Where is RAW‑ML called?” with a direct code pointer
- [ ] Reviewer can answer “How do we guarantee no orchestrator-as-auditor?” with:
  - [ ] a test that fails if called
  - [ ] a clear code path that bypasses orchestrator
- [ ] Rollback is safe (feature flags keep default behavior)
