# Registry V3 Extraction Upgrade Implementation Guide

This document consolidates the full upgrade plan into a single, end-to-end implementation guide for **granular, evidence-gated registry extraction** and the pivot to an **extraction-first** architecture (Registry → deterministic CPT).

It is written to be added to this repo as a working plan (e.g., `docs/REGISTRY_V3_IMPLEMENTATION_GUIDE.md`).

> Repo context / module map: see `gitingest.md` for the current module layout and extraction-first pivot notes. fileciteturn3file0

---

## 0. What’s already done (your Phase 0 baseline)

You already implemented Phase 0 data + metrics foundation:

- **Data organization**
  - `data/registry_granular/notes/` (per-note text)
  - `data/registry_granular/csvs/` (phase0 labeling exports)
  - `data/knowledge/golden_registry_v3/` (per-note_id JSON gold in V3-ish format)

- **Phase 0 ingestion**
  - `scripts/ingest_phase0_data.py` converts CSV → per-note JSON in `data/knowledge/golden_registry_v3/`
  - Verified: wrote 10 gold JSONs

- **Granular eval harness**
  - `scripts/eval_registry_granular.py` runs evaluation + JSONL error output
  - Contains placeholder `extract_registry_v3()` (currently empty predictions)
  - Verified: runs, micro precision/recall are 0.000 as expected

This guide starts at **Phase B: Engine Implementation**, replaces the mock extractor, and then proceeds through the remaining upgrade steps.

---

## 1. North-star architecture and invariants

### 1.1 Target pipeline (Extraction-First V3)
```
Raw note text
  ├─> (A) deterministic focus/section slicing  ──────┐
  │                                                  │
  ├─> (B) deterministic anchors/regex/normalizers     │
  │                                                  ▼
  ├─> (C) strict structured LLM extraction (V3 events)
  │         + evidence_quote required for each event
  │
  ├─> (D) evidence verification (hard gate)
  │         - drop/reject any event/field lacking verifiable evidence
  │
  ├─> (E) deterministic postprocess/normalization
  │
  ├─> (F) optional self-correction (evidence-gated + anchor-bounded)
  │
  └─> (G) derived outputs
          - aggregate performed flags (legacy compatibility)
          - deterministic CPT derivation
          - eval + audit reports
```

### 1.2 Hard invariants (do not violate)
1) **Audit must use raw note text** (never focused text).
2) **Every high-cardinality extraction must be evidence-backed** (quote must be found in text).
3) **Events are source-of-truth**, booleans become derived projections.
4) **No hallucinated numbers**: prefer deterministic extraction or NER anchors for stations/sizes/counts.
5) **Feature flags** gate rollout; keep backward-compatible paths until metrics are stable.

---

## 2. Step-by-step implementation roadmap (in required order)

### Step 1 — Operationalize section-aware extraction as a hard filter (focusing)

**Goal:** Prevent history/plan text from being misinterpreted as performed procedures by restricting what the extractor sees.

**Where:**
- Implement in `modules/registry/extraction/focus.py` (already exists).
- Expose a helper used by the V3 pipeline:
  - `get_procedure_focus(note_text: str) -> str`
  - optionally `get_indication_focus(note_text: str) -> str`
  - optionally `get_complications_focus(note_text: str) -> str`

**Implementation requirements:**
- Use existing deterministic sectionization:
  - `modules/common/sectionizer.py` or `modules/coder/sectionizer.py`, or `ParserAgent` segmentation.
- Extract and join sections (case-insensitive header match):
  - PROCEDURE, FINDINGS, IMPRESSION, TECHNIQUE, OPERATIVE REPORT
- Fail-safe: if nothing found, return full `note_text`

**Tests to add:**
- Add fixtures in `tests/fixtures/notes/` showing “history of X” but no performed X.
- Add unit tests in `tests/registry/` asserting focusing excludes HISTORY-only mentions from being extracted as performed.

**Acceptance criteria:**
- Eval harness shows decreased false positives for history-vs-performed notes.
- Focus function is deterministic and stable across formatting changes.

---

### Step 2 — Implement strict structured generation (constrained decoding)

**Goal:** Make the LLM output always conform to the V3 schema (no schema hallucinations).

**Where:**
- Create `modules/registry/extractors/v3_extractor.py`
- Use your existing LLM wrapper infrastructure (openai_compat / gemini) used elsewhere in the repo.
- Continue to support `REGISTRY_USE_STUB_LLM=1` for tests.

**Core function:**
- `extract_v3_draft(focused_text: str, *, anchors: dict | None = None) -> IPRegistryV3`

**Requirements:**
- System prompt enforces:
  - V3 schema only
  - **evidence_quote per event**
  - event list only for **performed** actions
- If OpenAI-compatible backend is active, use JSON schema / structured response mode.
- If backend lacks strict mode, implement:
  1) prompt JSON
  2) `IPRegistryV3.model_validate_json()`
  3) single “repair” attempt that fixes only validation errors (optional, later)

**Acceptance criteria:**
- For a stable test set of ~10 notes, extractor returns schema-valid V3 every run.
- Validation failures fail loudly with a clear error.

---

### Step 3 — Add evidence verification as a non-negotiable guardrail

**Goal:** Reject hallucinations by requiring evidence quotes exist verbatim in the note text.

**Where:**
- New module: `modules/registry/evidence/verifier.py`

**Functionality:**
- `normalize_text(text: str) -> str` (lowercase + collapse whitespace)
- `verify_registry(registry: IPRegistryV3, source_text: str) -> IPRegistryV3`
  - iterate events
  - each event must have `evidence_quote`
  - verify normalized quote exists in normalized source text
  - if not found: remove event OR mark rejected (removal is simplest for Phase B)

**Integration:**
- Called immediately after extraction and before any postprocessing/derivation.

**Acceptance criteria:**
- “Forced hallucination” tests fail safely (event dropped).
- Evidence quotes appear per event in `V3_Procedure_Events` and in `V3_Registry_JSON`.

---

### Step 4 — Migrate from “flat booleans” to nested event logs (V3 schema)

**Goal:** Represent what happened as event objects (action + target + device + quantities + outcomes), not disconnected flags.

**Where:**
- V3 models:
  - `proc_schemas/registry/ip_v3.py`
  - `modules/registry/schema/ip_v3.py` (your new path)
- Add projection layer for compatibility:
  - `modules/registry/transform_v3.py` (new) or extend `modules/registry/transform.py`

**Minimum event model must cover:**
- Bronchoscopy actions (BAL, brushing, TBNA, cryobiopsy, aspiration, navigation)
- Linear EBUS staging (inspected + sampled + needle gauge + passes)
- Therapeutic airway (dilation, stent, debulking) including:
  - stent size/material/brand
  - airway lumen pre/post outcomes
- Pleural (thora, chest tube, IPC, pleurodesis) including:
  - catheter type + size
  - volume drained, manometry
  - pleural outcomes when stated

**Projection must produce:**
- V2-compatible 30 booleans for ML + legacy consumers
- Aggregate performed flags derived from event logs

**Acceptance criteria:**
- Multi-action notes yield multiple events without losing relationships.

---

### Step 5 — Expand deterministic extractors + normalization for high-cardinality entities

**Goal:** Improve recall/precision for entities LLMs hallucinate or mangle.

**Where:**
- `modules/registry/deterministic_extractors.py`
- `modules/registry/normalization.py`
- `modules/registry/postprocess.py`
- Lexicons under `configs/lex/`

**Priority deterministic extractors:**
- LN stations (4R, 7, 11Rs/11Ri/11L)
- Needle gauges (19G/21G/22G/23G)
- Lobe/segment targets (LB10/RB1 etc)
- Counts (passes per station, # samples)
- Volumes (BAL instill/return; pleural volume)
- Stent sizing (DxL), catheter sizes (Fr)
- Therapeutic outcomes (“~80% obstruction” pre; “widely patent” post)

**How to use them:**
- Produce `anchors` passed into the LLM prompt.
- Use postprocess to normalize event fields.

**Acceptance criteria:**
- Higher precision on stations/gauges/counts in eval harness.
- Reduced “invented station” errors.

---

### Step 6 — Transition ML from document classification → token classification (NER)

**Goal:** Build an entity extractor for spans to ground the LLM and reduce hallucinations.

**Data:**
- Use Phase 0 workbook + anchor-first spans.
- Convert hydrated spans into NER training format.

**Training:**
- New training script: `scripts/train_registry_ner.py`
- Labels match your granular label set (stations, sizes, gauges, devices, counts).

**Integration:**
- Predictor wrapper: `modules/registry/ml/registry_ner_predictor.py`
- In V3 pipeline:
  - run NER on focused text
  - add entities into `anchors`
  - LLM must prefer anchors

**Acceptance criteria:**
- Strong entity-level F1 for stations/gauges/sizes.
- Errors shift from wrong-value → missing-value.

---

### Step 7 — Upgrade self-correction loop to be evidence-gated + anchor-bounded

**Goal:** Prevent judge-driven self-correction from inventing facts.

You already have a guarded loop in extraction-first in `modules/registry/application/registry_service.py` (feature-flagged). Upgrade it:

1) Evidence required for every patch op (or proposal).
2) Evidence quote must exist in raw note text.
3) Anchor-bounding:
   - if patch sets station/gauge/size, it must exist in anchors or be quoted verbatim.

**Where:**
- `modules/registry/self_correction/judge.py`
- `modules/registry/self_correction/validation.py`
- optional helper `modules/registry/self_correction/evidence_gate.py`

**Acceptance criteria:**
- No patch introduces unseen station/gauge/size.
- Rejected patches logged clearly.

---

### Step 8 — Finish the pivot: make extraction-first the default registry truth path

**Goal:** Extraction-first becomes default with safe rollback.

**Flip defaults carefully:**
- Default `PROCSUITE_PIPELINE_MODE=extraction_first`
- Keep a rollback path to `current` for 1–2 releases

**Rollout:**
- enable in staging → subset of prod → default prod

**Acceptance criteria:**
- Eval harness improves and production spot-checks maintain safety and correctness.
- Audit warnings decrease over time.

---

## 3. Phase B (Engine Implementation): replace the mock extractor in eval harness

### B1) Section focusing
Implement `get_procedure_focus()` in `modules/registry/extraction/focus.py`.

### B2) Strict V3 extractor
Create `modules/registry/extractors/v3_extractor.py` with `extract_v3_draft()` using strict schema decoding where possible; require evidence_quote per event.

### B3) Evidence verifier
Create `modules/registry/evidence/verifier.py` with `verify_registry()` that drops events whose quote is not found.

### B4) V3 pipeline entrypoint
Create `modules/registry/pipelines/v3_pipeline.py` with `run_v3_extraction(full_note_text)`.

### B5) Wire into eval
Update `scripts/eval_registry_granular.py` to call `run_v3_extraction(note_text)`.

**Expected:** metrics become non-zero and JSONL error output becomes actionable.

---

## 4. NER build guide (practical)

1) Build dataset:
- `scripts/build_registry_ner_dataset.py` reads hydrated spans + notes to create train/val/test JSONL.

2) Train:
- `scripts/train_registry_ner.py` outputs `artifacts/registry_ner/` (HF format), optional ONNX.

3) Integrate:
- `modules/registry/ml/registry_ner_predictor.py` returns anchors for pipeline + self-correction.

---

## 5. Feature flags (recommended)

New:
- `REGISTRY_V3_ENABLED=0/1`
- `REGISTRY_V3_STRICT_EVIDENCE=0/1` (default 1)
- `REGISTRY_V3_USE_NER_ANCHORS=0/1` (default 0 until trained)
- `REGISTRY_V3_SELF_CORRECT=0/1` (default 0)

Existing:
- `PROCSUITE_PIPELINE_MODE=extraction_first` (startup-enforced; legacy pipeline modes are disabled by default)
- `REGISTRY_EXTRACTION_ENGINE=parallel_ner|engine|agents_focus_then_engine|agents_structurer`
- `REGISTRY_SCHEMA_VERSION=v3|v2` (production requires `v3`)
- `REGISTRY_SELF_CORRECT_ENABLED=0/1`

---

## 6. Definition of Done (sign-off checklist)

- [ ] Eval harness uses real V3 extraction and yields non-zero precision/recall
- [ ] V3 contains multi-event logs with relationships intact
- [ ] Evidence verifier reliably drops hallucinated events
- [ ] Deterministic anchors reduce station/gauge/count hallucinations
- [ ] Self-correction cannot introduce unseen facts
- [ ] Extraction-first becomes default (with rollback)
- [ ] NER trained and integrated (recommended)

---

## 7. Next Codex prompt (copy/paste)

Codex Instructions: Phase B (The Engine)
We are implementing the V3 Extraction Engine. This replaces the mock logic with a real, evidence-gated pipeline.

Step 1: Section Focusing
File: modules/registry/processing/focus.py

Create the logic to "slice" the note.

Imports: Import your existing Sectionizer or ParserAgent.

Function: def get_procedure_focus(note_text: str) -> str

Logic:

Attempt to extract segments: PROCEDURE, FINDINGS, IMPRESSION, TECHNIQUE, OPERATIVE REPORT.

Crucial Fallback: If the resulting string is empty (no headers found), return note_text (the original full text). Do not return an empty string.

Join segments with \n\n.

Step 2: Strict V3 Extractor
File: modules/registry/extractors/v3_extractor.py

Implement the LLM extraction using Pydantic schemas.

Imports: IPRegistryV3 (from modules.registry.schema.ip_v3_extraction), and your LLM client.

Function: def extract_v3_draft(focused_text: str) -> IPRegistryV3

Schema Handling:

Get the JSON schema: schema = IPRegistryV3.model_json_schema()

Pass this to the LLM (using response_format for OpenAI or equivalent for your provider).

Prompt:

"Extract interventional pulmonology events. You MUST provide a verbatim evidence_quote for every event. Output JSON only."

Output: Parse the LLM response back into an IPRegistryV3 object.

Step 3: Evidence Verifier (The Judge)
File: modules/registry/evidence/verifier.py

Helper: def normalize_text(text: str) -> str

Lower case.

Remove punctuation.

Collapse multiple spaces/newlines to single space.

Function: def verify_registry(registry: IPRegistryV3, full_source_text: str) -> IPRegistryV3

Logic:

Normalize full_source_text once.

Iterate over registry.procedures.

For each event:

If event.evidence is missing, Drop Event.

Normalize the quote.

Check if normalized_quote in normalized_source.

If Match: Keep event.

If No Match: Drop Event (Hallucination detected).

Return the pruned registry.

Step 4: Wire the Pipeline
File: modules/registry/pipelines/v3_pipeline.py

Function: def run_v3_extraction(note_text: str) -> IPRegistryV3

Flow:

focused = get_procedure_focus(note_text)

draft = extract_v3_draft(focused)

final = verify_registry(draft, note_text) (Verify against full text to be safe).

Return final.

Step 5: Activate Eval
File: scripts/eval_registry_granular.py

Import run_v3_extraction.

Replace the mock function call with run_v3_extraction(note_content).

Run the script and print the Precision/Recall stats.

Step 6: Add tests (focusing + evidence verifier).
Step 7:  Run `python scripts/eval_registry_granular.py` and confirm non-zero metrics and JSONL error output.
