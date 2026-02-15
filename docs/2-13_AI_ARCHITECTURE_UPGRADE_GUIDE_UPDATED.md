🎯 Project Vision & Context
Project: proc_suite_deploy (Interventional Pulmonology Registry & Extraction Suite)
Objective: Transform the repository from a single-document, regex-heavy pipeline into a Multi-Document, Zero-Knowledge Longitudinal Registry.

Non‑negotiables:
- 100% schema compliance via LLM Constrained Decoding
- Auditor-grade evidence anchors (quotes + spans)
- Correct entity relations (no multi-station “cross-talk”)
- Chronology across documents **without ever sending absolute dates or PHI to the server**

---

✅ Repo Status (as of 2026-02-14)

- Phase 0 baseline harness: `ml/scripts/eval_golden.py` (CI runs it; it skips when fixtures are absent).
- Quote anchoring: `app/evidence/quote_anchor.py` + V3 verifier anchoring in `app/registry/evidence/verifier.py:verify_registry()`.
- Quote repair retry (best-effort): `app/registry/extractors/v3_extractor.py:repair_v3_evidence_quotes()` (enabled by default via `REGISTRY_V3_QUOTE_REPAIR_ENABLED=1`).
- Experimental structurer engine: `REGISTRY_EXTRACTION_ENGINE=agents_structurer` is now wired via `app/registry/extraction/structurer.py` and projects V3 event-log → `RegistryRecord` (falls back to deterministic engine when LLM is unconfigured/offline).
- Bundle endpoint (experimental): `POST /api/v1/process_bundle` in `app/api/routes/process_bundle.py` enforces “no absolute dates” and processes multi-doc bundles (expects client-side `T±N` tokens).
- Phase 7 (experimental): `app/agents/aggregator/timeline_aggregator.py` builds an **entity ledger** with explicit cross-doc link proposals (`linked_to_id`, `confidence`, `reasoning_short`) and `process_bundle` returns it under `entity_ledger`.
- Phase 8 (experimental): `process_bundle` also returns `relations_heuristic`, `relations_ml`, and merged `relations`; `ml/scripts/bootstrap_relations_silver.py` can bootstrap a reviewable silver edge set from saved bundle outputs.
- Phase 5/6 UI (experimental): `/ui/` dashboard now includes a “Bundle (Zero‑Knowledge Timeline)” panel with Index Date + Document Date, a Chronology Preview modal, date tokenization (`[DATE: T±N DAYS]` or `[DATE: REDACTED]`), and a bundle composer that submits to `POST /api/v1/process_bundle`.
- PHI guardrails hardened: month-name dates are detected client-side (`redactor.worker*.js`), bundle leak-check now scans inside bracket tokens, doc offsets prefer `[SYSTEM: ...]` headers, and the server strips a leading `[SYSTEM: ...]` line before extraction.

---

🏛️ The 3 Core Architectural Pillars (with guardrails)

Pillar 1: Schema-First Structured Outputs & Robust Quote Anchoring
Goal: Eliminate the heuristic “God Method” (`app/registry/application/registry_service.py` → `RegistryService._extract_fields_extraction_first()`) and regex-based span retrofitting.

Primary risk (Gotcha): “Exact quote” paraphrasing paradox
- LLMs occasionally normalize text (typo fixes, abbreviation expansion like “RUL” → “Right Upper Lobe”, punctuation cleanup).
- When the quote is paraphrased, anchoring can fail, breaking UI highlight trust or dropping data.

Mitigation (required contract):
1) Draft Evidence must include context, not only the quote:
   - `rationale` (short; internal/debug only)
   - `prefix_3_words`, `exact_quote`, `suffix_3_words`
2) Quote Fidelity Guard:
   - If `exact_quote` is not an exact substring of the scrubbed input, automatically trigger ONE “quote repair” retry prompt:
     - “Return the same JSON, but copy the quote verbatim from the provided text. Do not expand abbreviations.”
3) Soft Fuzzy Fallback (never drop the value):
   - If anchoring fails completely, keep the extracted value.
   - Set `evidence_span=null`, mark `evidence_status="INFERRED_UNANCHORED"` and let UI render without highlight.

Impact:
- Evidence highlighting becomes truthful and non-brittle.
- Reviewers still see data even when quote anchoring fails.

---

Pillar 2: Bootstrapped Entity-Relation (RE) Extraction (Shadow Mode First)
Goal: Stop using Python proximity heuristics to guess relationships (needle↔station, specimen↔lesion).

Primary risk (Gotcha): RE annotation bottleneck + hallucinated edges
- RE labeling takes 3–5× longer than NER.
- Small datasets → hallucinated edges.
- Deleting heuristics too early increases errors (multi-station cross-talk).

Mitigation (phased delivery):
1) Weak Supervision / Silver Data first:
   - Generate candidate edges using existing heuristics (and optionally a frontier LLM for edge proposals).
   - Load into Prodigy as “Approve/Reject” (humans do fast verification, not edge creation).
2) Shadow Mode heuristics:
   - Run RE model alongside heuristics.
   - If RE returns empty/low-confidence edges, fall back to heuristics.
3) Delete heuristics only after sustained win:
   - Require a tracked F1 threshold and stable error rates on multi-station notes before removal.

Impact:
- You de-risk RE while still improving correctness over time.

---

Pillar 3: Zero-Knowledge Longitudinal Registry (Client-Side Temporal Translation)
Goal: Accept a bundle of chronological documents (CT → Procedure → Pathology → Follow-up) and compute time-to outcomes **without storing PHI or absolute dates**.

Primary risk (Gotcha): client-side date parsing brittleness + DST off-by-one
- Clinical dates are messy (“POD #2”, “1–2wks”, ambiguous “10/11/12”).
- Native `Date.parse()` is brittle and timezone/DST can shift deltas by ±1.

Mitigation (required):
1) Use a robust NLP date parser in the Worker:
   - Bundle Chrono Node (preferred) for messy/relative expressions.
2) Force UTC math at noon:
   - Convert Index Date + Doc Date + Parsed Dates to UTC at 12:00 PM before diff.
3) Interactive Chronology Preview:
   - Show: Original → Parsed interpretation → Token replacement (T±X DAYS).
   - Require user confirm before dispatching bundle.
4) Token types (v1 + extensions):
   - Exact: `[DATE: T+N DAYS]`
   - Range (optional): `[DATE_RANGE: T+N1..N2 DAYS]`
   - Unparsed: `[DATE: REDACTED]`

Impact:
- Timelines remain reliable without leaking absolute dates.

---

⚠️ Additional known system-level gotchas (and built-in mitigations)

Gotcha: Cross-document coreference overload (Aggregator)
- The aggregator must know that “1.2cm RUL nodule” (CT) == “Target 1” (robotic note) == “Specimen A” (path).
- Without structure, LLMs misattribute pathology to wrong targets when multiple lesions exist.

Mitigation:
- “Entity Ledger” schema is mandatory for the Aggregator:
  - Establish canonical entities early and require explicit linking (`linked_to_id`, `confidence`, `reasoning_short`).
- Two-stage aggregation:
  1) Per-doc structured extraction (within-doc IDs)
  2) Cross-doc linking step (ledger updates), then outcome computation

Gotcha: Golden fixture migration poisoning
- Auto-converting hundreds of goldens into spans is error-prone and can permanently poison baselines.

Mitigation:
- Never overwrite legacy goldens.
- Create a new vNext golden directory.
- Migration generates quotes (not spans) + HTML diff for human approval.

---

📦 Golden Fixtures Strategy (Safe Baselines)

Legacy:
- `data/knowledge/golden_extractions_final/` (do NOT modify)

vNext (new):
- `data/knowledge/golden_extractions_vNext/` (new fixtures only)

Principle:
- Goldens store value + quote context (prefix/quote/suffix).
- Spans are computed deterministically at test/runtime by the Quote Anchor (never “guessed” in the fixture).

---

🚀 Execution Playbook (Reordered for highest likelihood of success)

AI Assistant: Follow phases sequentially. Do not delete or “clean up” legacy paths until the relevant phase explicitly says so.

Phase 0: Freeze Baseline & Protect Against Poisoning
Goal: Ensure you can detect regressions and avoid corrupting the truth set.
Actions:
- Build/verify legacy evaluator:
  - `ml/scripts/eval_golden.py` runs current extraction-first logic against legacy goldens.
- Add CI step that runs legacy eval (read-only fixtures).
Success:
- Legacy pass rate is measurable and stable.
Guardrail:
- No modifications to `data/knowledge/golden_extractions_final/`.

Phase 1: vNext Schemas (Draft vs Final) + Evidence Contract (Anti-Paraphrase)
Goal: Define schemas that enable robust quote anchoring and UI trust.
Actions:
- Create:
  - `proc_schemas/registry/ip_vnext_draft.py` (LLM output schema)
  - `proc_schemas/registry/ip_vnext.py` (final API schema)
- EvidenceQuoteDraft fields (minimum):
  - `rationale` (short string; internal/debug)
  - `prefix_3_words`, `exact_quote`, `suffix_3_words`
  - `confidence` (optional: low/med/high)
- Final Evidence includes:
  - `evidence_span: {start:int,end:int} | null`
  - `evidence_status: ANCHORED | INFERRED_UNANCHORED | INFERRED_NOQUOTE`
Success:
- `model_json_schema()` is strict and ready for constrained decoding.

Phase 2: StructurerAgent Constrained Decoding + Quote Fidelity Retry
Goal: Guarantee schema compliance and minimize paraphrased quotes.
Actions:
- Implement constrained decoding in:
  - `app/agents/structurer/structurer_agent.py` and/or `app/common/llm.py`
- Add Quote Fidelity Guard:
  - After LLM returns draft JSON, verify each `exact_quote` is substring of scrubbed text.
  - If not, run one targeted retry prompt for “verbatim quotes”.
Success:
- Draft outputs parse 100% and most quotes pass substring check without fuzz.

Phase 3: Quote Anchoring Engine (Context-Aware) + Soft Fallback
Goal: Compute spans deterministically and never drop extracted values.
Actions:
- Build/upgrade:
  - `app/evidence/quote_anchor.py`
- Anchoring algorithm (recommended order):
  1) Exact substring match of `exact_quote`
  2) Whitespace-normalized match
  3) Context bounded search using `prefix_3_words` / `suffix_3_words` to narrow candidate region
  4) rapidfuzz fallback within bounded region
- If anchoring fails:
  - keep value, set `evidence_span=null`, set `evidence_status="INFERRED_UNANCHORED"`
Success:
- UI never “loses” data because of anchoring failures.

Phase 4: vNext Golden Migration Tool (Human-Approved) + Small Smoke Set First
Goal: Build a trustworthy vNext fixture set without poisoning.
Actions:
- Create:
  - `ml/scripts/migrate_goldens_vNext.py` (LLM-assisted quote rewrite; spans not generated)
  - Output to `data/knowledge/golden_extractions_vNext/pending/`
- Generate HTML diff report:
  - old legacy rationale vs new (prefix/quote/suffix) side-by-side
  - developer quickly approves/rejects each fixture
- Start with a smoke subset (e.g., 20–30 fixtures), then expand.
Suggested workflow:
```bash
# 1) Generate a small pending subset + HTML report (no LLM by default)
python ml/scripts/migrate_goldens_vNext.py --limit 30

# 2) Review the report
open data/knowledge/golden_extractions_vNext/migration_report.html

# 3) Approve by moving selected JSONs from pending → approved
ls data/knowledge/golden_extractions_vNext/pending/
mv data/knowledge/golden_extractions_vNext/pending/<case>.json data/knowledge/golden_extractions_vNext/approved/

# 4) Validate anchoring on the approved subset (CI runs this step optionally too)
python ml/scripts/eval_golden_vNext_quotes.py
```
Success:
- vNext CI runs on the approved subset with stable results.

Phase 5: Bulletproof Client-Side Temporal Translation (Chrono + UTC + Preview)
Goal: Achieve true ZK timelines with high parse success and user verification.
Actions (UI):
- Add Index Date (T=0) and per-document Document Date + timepoint_role + seq.
- Add “Chronology Preview” modal showing parsed interpretation + token result.
Actions (Worker):
- Bundle Chrono Node in:
  - `ui/static/phi_redactor/redactor.worker.js`
- Force UTC-noon math for deltas.
- Replace inline dates with `[DATE: T±N DAYS]` (and optionally DATE_RANGE tokens).
Server guardrail:
- Reject any bundle doc that still contains raw date-like strings (leak-check).
Success:
- Bundle ingestion contains only relative tokens; no DST drift.

Phase 6: Bundle Endpoint v1 (Per-Doc Extraction + Deterministic Timeline Math)
Goal: Ship multi-doc ingestion without requiring perfect cross-doc linking on day one.
Actions:
- Implement `POST /api/v1/process_bundle` under `app/api/routes/`.
- For each doc:
  - run StructurerAgent → produce structured doc output
- Timeline math:
  - parse `[SYSTEM: ... T±X ...]` headers and/or `[DATE: T±N DAYS]` tokens
  - compute time-to metrics deterministically
Success:
- Works for single-lesion and straightforward multi-doc episodes.

Phase 7: Aggregator v2 (Entity Ledger + Explicit Cross-Doc Linking)
Goal: Reduce pathology misattribution in multi-lesion scenarios.
Actions:
- Implement ledger schema in:
  - `app/agents/aggregator/timeline_aggregator.py`
- Require explicit linking objects:
  - `linked_to_id`, `confidence`, `reasoning_short`
- Prefer aggregator input as structured doc objects + small context snippets, not full raw notes.
Success:
- Multi-lesion episodes show correct lesion↔specimen↔path linkage with confidence.

Phase 8: Relation Extraction (Weak Supervision → Shadow Mode → Replacement)
Goal: Improve relations without incurring an annotation death spiral.
Actions:
- Create silver edge generator:
  - `ml/scripts/bootstrap_relations_silver.py` (uses heuristics + optional LLM proposals)
- Prodigy workflow:
  - approve-reject loop (fast); see `docs/RELATIONS_PRODIGY_WORKFLOW.md`
- Shadow mode integration:
  - pipeline emits `relations_ml` + `relations_heuristic`
  - merge strategy: ML if high confidence else heuristic
- Runtime ML proposer (optional):
  - `RELATIONS_ML_ENABLED=1` enables an LLM-based proposer that consumes ONLY the entity ledger
    (labels/attributes; no raw note text).
  - `RELATIONS_ML_ONLY_MISSING=1` proposes only when heuristics have no edge for the key.
  - `RELATIONS_ML_PROPOSE_NAV_TARGETS=1` also proposes `linked_to_lesion` (default: specimens only).
  - Safety/perf guards:
    - `RELATIONS_ML_MAX_CANDIDATES` (default `40`)
    - `RELATIONS_ML_MAX_CANONICAL_LESIONS` (default `20`)
- Track merge stats:
  - `process_bundle` now returns `relations_warnings` and `relations_metrics` for evaluation.
- Track metrics and only then delete heuristic reconcilers.
Success:
- RE accuracy beats heuristics on multi-station set before removal.

Phase 9: Tear Down the Regex Monolith (Last)
Goal: Shrink complexity only after correctness is protected.
Actions:
- Introduce feature flag `STRUCTURED_EXTRACTION_ENABLED`.
- Route extraction to StructurerAgent by default, keep legacy behind flag.
- Add a PHI-safe “shadow diff” runner to compare `engine` vs `agents_structurer` on vNext fixtures:
  - `ml/scripts/shadow_diff_structured_extraction.py` (writes a JSON report; never writes note text)
  - Example:
  ```bash
  python ml/scripts/shadow_diff_structured_extraction.py \
    --input data/knowledge/golden_extractions_vNext/approved \
    --output-json output/shadow_diff_structured_extraction_report.json
  ```
- Delete regex dictionaries and span retrofitting only after vNext fixtures are strong.
Success:
- Codebase shrinks with no loss of correctness.

---

🔄 Client-Side Temporal Translation Implementation Notes (Drop-in)
Absolute dates never leave the browser. The client does the math, replaces dates with T‑tokens, and prepends doc offsets.

Recommended payload (server sees only ZK text):
```python
class ParsedDocRequest(BaseModel):
    timepoint_role: Literal["PREOP_IMAGING", "INDEX_PROCEDURE", "PATHOLOGY", "FOLLOW_UP"]
    seq: int
    text: str  # pre-scrubbed with T tokens + SYSTEM header

class ProcessBundleRequest(BaseModel):
    zk_patient_id: str
    episode_id: str
    documents: List[ParsedDocRequest]
```

---

✅ Definition of Done (What “success” looks like)
- Evidence UI never breaks when quotes aren’t anchorable (soft fallback works).
- Legacy goldens remain untouched and still pass.
- vNext goldens are created safely via human-approved migration.
- Bundles contain no absolute dates, and deltas are DST-safe.
- Aggregator produces correct lesion/specimen linking with explicit ledger entries.
- RE improves relations while heuristics remain as fallback until proven better.
