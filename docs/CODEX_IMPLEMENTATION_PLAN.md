# Codex Implementation Brief v4 (Merged + Updated)
Extraction‑First Registry → Deterministic CPT → **RAW ML Auditor** + Guarded Self‑Correction (OpenAI‑Protocol LLM)

## 0) Read-first (do this before editing)
- [ ] Read: README.md
- [ ] Read: docs/ARCHITECTURE.md
- [ ] Read: docs/AGENTS.md
- [ ] Identify entrypoints:
  - Registry extraction: modules/registry/application/registry_service.py
  - Granular derivation: modules/registry/schema_granular.py (derive_procedures_from_granular)
  - Existing rules: data/rules/coding_rules.py (move/refactor FIRST)
  - Hybrid orchestrator: modules/coder/application/smart_hybrid_policy.py
  - ML predictor: modules/ml_coder/predictor.py (MLCoderPredictor / classify_case)
  - Agents pipeline: modules/agents/run_pipeline.py

### 0.1 Critical call-graph fact (must be preserved in implementation + tests)
From smart_hybrid_policy.py, SmartHybridOrchestrator.get_codes():
- Calls self._ml.classify_case(note_text) ✅ raw ML exists here
- THEN runs rules validation: self._rules.validate(ml_candidates, note_text, strict=True) ❌ can veto ML
- And may call LLM fallback + re-validate with rules ❌
=> Therefore orchestrator output is **NOT** a pure auditor signal.
=> Registry audit MUST call the raw predictor (classify_case / raw probabilities) directly, bypassing rules/LLM.

---

## 1) Mission
Implement an extraction-first registry pipeline that:
1) Produces a clinically-derived RegistryRecord from note text **with zero CPT seeding**
2) Derives CPT deterministically from RegistryRecord only
3) Runs a **pure RAW-ML auditor** (no rules validation, no LLM fallback, no hybrid veto)
4) Optionally triggers a tightly controlled self-correction loop when RAW-ML indicates a high-confidence omission

---

## 2) Non-negotiable constraints (enforce via code + tests)
### 2.1 Extraction purity
- [ ] No CPT hints passed into extraction (no verified_cpt_codes, no ML codes, no orchestrator output, no merge).
- [ ] Extraction runs ONLY from note_text (plus harmless metadata like note_id).

### 2.2 Auditor purity (now includes verified call-graph reality)
- [ ] Registry audit MUST use raw ML predictor output only:
  - [ ] Call MLCoderPredictor.classify_case(raw_note_text) (or equivalent) directly
  - [ ] Use raw probabilities + model threshold buckets (high_conf / gray_zone / predictions)
- [ ] Do NOT use SmartHybridOrchestrator.get_codes() as auditor, because it:
  - [ ] runs self._rules.validate(... strict=True) and can veto ML
  - [ ] may LLM fallback + re-validate
- [ ] Audit must never call rules validation or LLM fallback.

### 2.3 Rules purity
- [ ] Deterministic Registry→CPT rules take ONLY RegistryRecord (no note_text).
- [ ] If a rule needs missing data → improve extraction / schema derivation, not rules.

### 2.4 Up-propagation (no parallel normalization step)
- [ ] Do NOT add up_propagate_flags().
- [ ] Enforce granular→aggregate consistency ONLY by expanding derive_procedures_from_granular(record).

### 2.5 Summarizer trap (distribution shift guardrail)
- [ ] If note focusing/summarizing is used for extraction, RAW-ML auditor still runs on FULL RAW NOTE TEXT (never summarized text).

### 2.6 Backward compatibility
- [ ] Default mode remains current behavior.
- [ ] New behavior behind feature flags.

---

## 3) Feature flags / configuration (implement early; defaults preserve current)
Add env + config/settings.py wiring:

### 3.1 Pipeline control
- [ ] PROCSUITE_PIPELINE_MODE="current" | "extraction_first" (default "current")
- [ ] REGISTRY_EXTRACTION_ENGINE:
  - "engine" (default)
  - "agents_focus_then_engine"
  - "agents_structurer"

### 3.2 Auditor source (explicit)
- [ ] REGISTRY_AUDITOR_SOURCE="raw_ml" | "disabled" (default "raw_ml"; REQUIRED for extraction_first)

### 3.3 Auditor thresholds + sizing (NEW)
- [ ] REGISTRY_ML_AUDIT_TOP_K (default 25)
- [ ] REGISTRY_ML_AUDIT_MIN_PROB (default 0.50)
- [ ] REGISTRY_ML_SELF_CORRECT_MIN_PROB (default 0.95)
- [ ] REGISTRY_ML_AUDIT_USE_BUCKETS (default "1")
  - "1" => audit set = high_conf + gray_zone (preferred; uses per-code thresholds)
  - "0" => audit set = top_k + min_prob from raw predictions

### 3.4 Self-correction toggle
- [ ] REGISTRY_SELF_CORRECT_ENABLED="0" | "1" (default "0")

### 3.5 LLM provider config
- [ ] LLM_PROVIDER="gemini" | "openai_compat" (default "gemini")
- [ ] OPENAI_API_KEY, OPENAI_BASE_URL (optional), OPENAI_MODEL
- [ ] Optional overrides: OPENAI_MODEL_SUMMARIZER, OPENAI_MODEL_STRUCTURER, OPENAI_MODEL_JUDGE
- [ ] OPENAI_OFFLINE="0"|"1" (recommended for tests)

### 3.6 Registry model artifacts (S3 bootstrap; local + Railway)
The registry ML predictor artifacts are fetched at startup by:
- `modules/registry/model_bootstrap.ensure_registry_model_bundle()` (called by FastAPI lifespan and `scripts/railway_start.sh`)

Configuration:
- [ ] `MODEL_BACKEND` = `onnx` | `pytorch` | `auto`
- [ ] `REGISTRY_RUNTIME_DIR` (optional override; default `data/models/registry_runtime`)
- [ ] AWS creds/region in env (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)

S3 sources (either is supported):
- [ ] **Tarball bundle (pinned/immutable):**
  - `MODEL_BUNDLE_S3_URI_ONNX=s3://procedure-suite-models/deploy/registry/<version>/onnx/bundle.tar.gz`
  - `MODEL_BUNDLE_S3_URI_PYTORCH=s3://procedure-suite-models/deploy/registry/<version>/pytorch/bundle.tar.gz`
- [ ] **Prefix of artifacts (moving/latest):**
  - `MODEL_BUNDLE_S3_URI_ONNX=s3://procedure-suite-models/classifiers/`
    - Bootstrap auto-selects the newest `model_int8.onnx` under the prefix and downloads:
      `model_int8.onnx`, `thresholds*.json`, `label_order.json`, `tokenizer/` → into `REGISTRY_RUNTIME_DIR`
    - Bootstrap writes `.bootstrap_state.json` so subsequent startups can skip downloads when unchanged and refresh when a newer export appears.

---

## 4) Phase 0 — Safety harness + regression tests (write FIRST)
Create tests that *explicitly prevent the orchestrator-as-auditor trap*.

### 4.1 New test modules
- [ ] tests/registry/test_extraction_first_flow.py
- [ ] tests/registry/test_auditor_raw_ml_only.py
- [ ] tests/coder/test_registry_to_cpt_rules_pure_registry.py
- [ ] tests/registry/test_derive_procedures_from_granular_consistency.py
- [ ] tests/registry/test_self_correction_loop.py

### 4.2 Required assertions
1) Extraction-first does not consult CPT
- [ ] In extraction_first mode, assert NO calls to:
  - SmartHybridOrchestrator.get_codes()
  - _merge_cpt_fields_into_record
  - any CPT-hint injection into extraction context

2) Auditor uses raw ML ONLY (no orchestrator, no rules.validate)
- [ ] Monkeypatch SmartHybridOrchestrator.get_codes to raise if called
- [ ] Monkeypatch CodingRulesEngine.validate to raise if called during registry audit path
- [ ] Stub/patch MLCoderPredictor.classify_case to return a known CaseClassification
- [ ] Assert registry audit succeeds and uses classify_case output, and never triggers validate()

3) Auditor uses raw note text even when focusing is enabled
- [ ] Provide a note where focused text differs from raw text
- [ ] Ensure raw ML auditor receives raw note string (not focused/summarized)

4) Rules are registry-only
- [ ] Fail test if deterministic CPT rules accept note_text or read it

5) Up-propagation is in derive_procedures_from_granular
- [ ] Provide record with granular evidence but aggregate flags false; call derive_procedures_from_granular; assert aggregates become true
- [ ] Confirm pipeline calls derive_procedures_from_granular after extraction and after any patch

---

## 5) Phase 1 — Refactor RegistryService into extraction-first + RAW-ML audit
### 5.1 Create extract_record() (NO CPT hints)
In modules/registry/application/registry_service.py add:

- [ ] def extract_record(self, note_text: str, *, note_id: str | None = None) -> tuple[RegistryRecord, list[str], dict]:
  - [ ] Choose engine per REGISTRY_EXTRACTION_ENGINE
  - [ ] Run extraction with context=None or metadata-only context (no codes)
  - [ ] Immediately call derive_procedures_from_granular(record)
  - [ ] Return (record, warnings, metadata)

### 5.2 Enforce extraction_first execution order
In extraction_first mode, enforce strict order:

1) record, extraction_warnings, meta = extract_record(raw_note_text)
2) derived = registry_to_cpt_engine.apply(record)  (Phase 3)
3) ml_audit = RawMLAuditor().classify(raw_note_text)  (Phase 1.3)
4) audit_set = RawMLAuditor().audit_predictions(ml_audit, cfg)  (Phase 1.3)
5) audit_report = compare(derived.codes, audit_set)
6) if REGISTRY_SELF_CORRECT_ENABLED=1: attempt self_correct(...) (Phase 5)
7) finalize output (record + derived CPT + audit report + warnings)

Legacy path must remain unchanged when PROCSUITE_PIPELINE_MODE="current".

### 5.3 Implement RAW-ML auditor wrapper (BYPASS orchestrator)
Create modules/registry/audit/raw_ml_auditor.py:

- [ ] Use predictor directly:
  - from modules/ml_coder/predictor import MLCoderPredictor, CaseClassification, CodePrediction (names may vary; use repo-native types)
- [ ] Do NOT call SmartHybridOrchestrator.get_codes()
- [ ] Do NOT call rules.validate()

Recommended structure:

- [ ] class RawMLAuditor:
  - [ ] __init__(predictor: MLCoderPredictor | None = None)
  - [ ] classify(raw_note_text: str) -> CaseClassification:
        return predictor.classify_case(raw_note_text)
  - [ ] audit_predictions(cls: CaseClassification, cfg) -> list[CodePrediction]:
        if REGISTRY_ML_AUDIT_USE_BUCKETS:
            return list(cls.high_conf) + list(cls.gray_zone)
        else:
            preds = cls.predictions[:REGISTRY_ML_AUDIT_TOP_K]
            return [p for p in preds if p.prob >= REGISTRY_ML_AUDIT_MIN_PROB]
  - [ ] self_correct_triggers(cls: CaseClassification, cfg) -> list[CodePrediction]:
        # conservative default: start from high_conf + optional prob floor
        return [p for p in cls.high_conf if p.prob >= REGISTRY_ML_SELF_CORRECT_MIN_PROB]

Store/return in output:
- ml_difficulty = cls.difficulty (or value)
- ml_top_predictions = cls.predictions[:10] (debug)
- ml_audit_codes_used = audit_predictions(...)
- Trigger candidates = self_correct_triggers(...)

### 5.4 Keep SmartHybridOrchestrator for coder endpoint
- [ ] Do not delete or break coder endpoint logic
- [ ] Ensure registry extraction_first path never calls orchestrator

---

## 6) Phase 2 — Agent focusing becomes primary extraction enhancement
### 6.1 Add focusing helper
- [ ] Implement focus_note_for_extraction(note_text) -> (focused_text, meta)
  - Parser isolates Procedure/Findings
  - Summarizer may condense ONLY for deterministic extraction
  - Fallback to full note if focus fails

### 6.2 Integrate focusing into extract_record
- [ ] If REGISTRY_EXTRACTION_ENGINE="agents_focus_then_engine":
  - focused_text, meta = focus_note_for_extraction(note_text)
  - Run RegistryEngine on focused_text
- [ ] Summarizer trap guardrail (mandatory):
  - RAW-ML auditor ALWAYS runs on raw full note_text, never focused/summarized

### 6.3 Structurer-first mode (optional)
- [ ] If REGISTRY_EXTRACTION_ENGINE="agents_structurer":
  - Use structurer output to build RegistryRecord
  - Fallback to deterministic RegistryEngine if structurer fails

---

## 7) Phase 3 — Deterministic Registry→CPT rules engine (START by moving/refactoring existing rules)
### 7.1 Move + shim
- [ ] Move: data/rules/coding_rules.py
- [ ] To: modules/coder/domain_rules/registry_to_cpt/coding_rules.py
- [ ] Keep a temporary shim at data/rules/coding_rules.py that re-exports from the new location

### 7.2 Refactor rule signatures to registry-only
- [ ] Update every rule to accept ONLY RegistryRecord
- [ ] Remove regex/text parsing in rules
- [ ] If missing evidence:
  - Add deterministic warning ("missing stations; cannot derive 31653")
  - Improve extraction / derive_procedures_from_granular instead

### 7.3 Add engine wrapper and types
- [ ] types.py:
  - DerivedCode { code, rationale, rule_id, confidence }
  - RegistryCPTDerivation { codes: list[DerivedCode], warnings: list[str] }
- [ ] engine.py:
  - apply(record: RegistryRecord) -> RegistryCPTDerivation
  - populate rationale + rule_id per code
  - warnings for missing/contradictory evidence

### 7.4 Wire extraction_first path to use deterministic engine
- [ ] derived CPT is source-of-truth
- [ ] ML is audit-only

---

## 8) Phase 4 — Up-propagation by expanding derive_procedures_from_granular(record)
In modules/registry/schema_granular.py expand derive_procedures_from_granular(record) to:
- Flip aggregate flags TRUE when granular evidence present:
  - EBUS stations present → linear_ebus.performed = True
  - BAL sites present → bal.performed = True
  - biopsy list present → biopsy.performed = True
  - navigation targets present → navigation.performed = True
  - etc.
- Append warnings when:
  - performed=True but required detail missing
  - contradictory fields exist

Ensure extraction_first calls derive_procedures_from_granular:
- after initial extraction (in extract_record)
- after any self-correction patch (Phase 9)

---

## 9) Phase 5 — Discrepancy compare + audit reporting (using RAW-ML set)
Implement compare(derived.codes, ml_audit_codes) returning:
- missing_in_derived = ml_audit_set - derived_set
- missing_in_ml = derived_set - ml_audit_set
- high_conf_omissions = derived missing items where source is in high_conf (and/or prob >= threshold)
- include ml_difficulty, top predictions (debug), config used

Do NOT auto-merge ML outputs into RegistryRecord (audit only).

---

## 10) Phase 6 — Self-correction loop (guarded JSON patch) driven by RAW-ML
### 10.1 Triggering (RAW-ML only)
Only if REGISTRY_SELF_CORRECT_ENABLED=1 AND:
- discrepancy exists
- trigger candidate comes from RawMLAuditor.self_correct_triggers(cls, cfg)
  - default: high_conf bucket + prob floor
- target field is allowlisted
- keyword hit in focused procedure text (guardrail)

### 10.2 Judge implementation
- [ ] modules/registry/self_correction/judge.py:
  - Input: raw note text, focused procedure text (if available), current RegistryRecord, target discrepancy
  - Output: JSON patch + evidence quotes (exact strings)

### 10.3 Patch validation (strict)
Validate:
- every patch path is allowlisted
- evidence quote appears verbatim in focused procedure text (or raw note if no focus)
Reject entirely if any check fails.

### 10.4 Apply + re-run derivations
- Apply patch
- Run derive_procedures_from_granular(record)
- Re-run deterministic CPT derivation
- Recompute audit report
- Add warning: "AUTO_CORRECTED: ..."

---

## 11) Phase 7 — OpenAI-protocol LLM adapter + provider selection
- [ ] Implement modules/coder/adapters/llm/openai_compat_advisor.py (same interface as Gemini advisor)
- [ ] Provider selection via LLM_PROVIDER (default gemini)
- [ ] Support task-specific model overrides:
  - OPENAI_MODEL_SUMMARIZER / STRUCTURER / JUDGE
- [ ] Add OPENAI_OFFLINE=1 stub mode for tests

---

## 12) ML auditor + retraining roadmap (post-implementation)
### 12.1 Immediate (no retrain required)
- Use existing model weights as RAW-ML auditor:
  - MLCoderPredictor.classify_case(raw_note_text)
- Never route through orchestrator for registry audit.

### 12.2 Data hygiene pass
- Run historical data through extraction_first + derive_procedures_from_granular + deterministic rules
- Retag/clean training labels (remove bundling suppression artifacts)

### 12.3 Retrain to predict registry flags (preferred)
- Train multi-label registry flag predictor
- Replace CPT-based auditor with registry-flag auditor

---

## 13) Definition of done
Extraction-first mode:
- extraction runs without CPT hints
- deterministic CPT derived from RegistryRecord only
- audit uses RAW-ML predictor directly (classify_case outputs), not orchestrator
- audit path never calls rules.validate() or LLM fallback
- derive_procedures_from_granular is the only up-propagation mechanism
- self-correction (if enabled) is safe (allowlist + verbatim evidence)
Current mode remains unchanged; all existing tests pass.

---

## 14) Recommended workstream split
- A: RegistryService refactor + RawMLAuditor wiring + tests
- B: Move/refactor coding_rules.py + deterministic engine + tests
- C: Expand derive_procedures_from_granular + tests
- D: Agents focusing integration + tests (summarizer trap guardrail)
- E: Self-correction loop + tests
- F: OpenAI compat adapter + tests
