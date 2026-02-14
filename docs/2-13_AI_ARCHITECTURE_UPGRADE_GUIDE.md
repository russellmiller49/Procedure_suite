🎯 Project Vision & Context
Project: proc_suite_deploy (Interventional Pulmonology Registry & Extraction Suite)
Objective: Transform the repository from a single-document, regex-heavy pipeline into a Multi-Document, Zero-Knowledge Longitudinal Registry.

The upgraded system must guarantee 100% schema compliance via LLM Constrained Decoding, generate auditor-grade evidence anchors (exact quotes), resolve clinical entity relations natively via ML, and track patient timelines chronologically without ever storing protected health information (PHI) or dates.

🏛️ The 3 Core Architectural Pillars
Pillar 1: Schema-First Structured Outputs & Quote Anchoring
Goal: Eliminate the heuristic "God Method" (`app/registry/application/registry_service.py` → `RegistryService._extract_fields_extraction_first()`) and regex-based span retrofitting.

The Constraint: All extraction must run through StructurerAgent (`app/agents/structurer/structurer_agent.py`) utilizing JSON Schema Constrained Decoding (e.g., OpenAI Structured Outputs or Outlines/Instructor).

The Evidence Contract: Every non-null boolean or value MUST contain an exact_quote copied verbatim from the redacted note text.

Span Resolution: Spans [start, end] are computed post-hoc deterministically. (1) Exact substring search -> (2) Normalized whitespace search -> (3) rapidfuzz partial ratio. If the quote cannot be anchored, the extraction fails closed or is flagged as INFERRED.

Impact: Delete thousands of lines of brittle regex in `app/registry/deterministic_extractors.py`. UI highlighting becomes 100% truthful to the LLM's reasoning.

Pillar 2: Entity-Relation (RE) Extraction
Goal: Stop using Python proximity heuristics to guess which biopsy needle belongs to which lymph node station.

The Upgrade: Evolve the NER training pipeline (`ml/scripts/train_registry_ner.py`) from flat token classification (NER) to explicit Entity-Relation extraction.

Output Graph: The model must output directed edges: [Station 4R] --SAMPLED_WITH--> [22g needle] or [Lesion] --TREATED_WITH--> [Cryoablation].

Impact: Remove proximity heuristics in `app/registry/postprocess/` (e.g., `app/registry/postprocess/complications_reconcile.py`, `app/registry/postprocess/template_checkbox_negation.py`). The ML model assumes responsibility for spatial and instrumental clinical relationships.

Pillar 3: Zero-Knowledge (ZK) Longitudinal Registry
Goal: Accept a bundle of chronological documents (CT -> Procedure -> Pathology) and map a patient's outcome graph without storing PHI or absolute dates.

User-Generated Patient Key: The server relies on a zk_patient_id (e.g., a hashed patient_handle generated client-side from a random key or local MRN + site secret). The server NEVER stores MRNs or names.

Aggressive Date Redaction: The PhiRedactor (`app/phi/service.py`, with adapters in `app/phi/adapters/`) must intercept raw text first. ALL explicit dates are replaced with [DATE] and times with [TIME]. * Date-Free Chronology: Timeline ordering relies purely on relative structures:

episode_id: The procedural event cluster.

timepoint_role: PREOP_IMAGING, INDEX_PROCEDURE, PATHOLOGY, FOLLOW_UP.

seq: An integer input order.

Cross-Doc Coreference: The pipeline must resolve entities across documents (e.g., linking "1.2cm RUL nodule" in the CT to "RUL biopsy" in the procedure note).

📦 Golden Fixture Migration (~238 files)
The existing golden JSON files (`proc_suite_notes/data/knowledge/golden_extractions_final/golden_*.json`) contain legacy evidence objects that are conversational (e.g., "Defaulted to ASA 3"). These must be migrated to support the new rigid pipeline.

Draft Schema vs Final Schema: Introduce a draft schema for LLM generation (values + exact quotes) and a final schema for the API/UI (values + computed [start, end] spans).

Migration Task: We will write a script to update schema_version to vNext, rename legacy evidence to rationale, and scaffold empty evidence_quotes and evidence_spans for the new tests to populate and verify.

Existing validation helper: `ml/scripts/validate_golden_extractions.py`

🚀 Execution Playbook (Codex Instructions)
AI Assistant: Follow these phases sequentially when generating PRs or making codebase updates.

Phase 0: Lock Baseline & Harness
Action: Build `ml/scripts/eval_golden.py` (new) to run current endpoints against the ~238 golden JSONs in `proc_suite_notes/data/knowledge/golden_extractions_final/`.

Success: CI measures current value-equality coverage so we can detect regressions during the regex tear-down.

Phase 1: vNext Schemas & Evidence Objects
Action: In `proc_schemas/registry/` (existing: `proc_schemas/registry/ip_v3.py`, `proc_schemas/registry/ip_v2.py`), create `ip_vNext_draft.py` (LLM output schema) and `ip_vNext.py` (final API schema).

Action: Define strict EvidenceQuoteDraft and EvidenceSpan models.

Success: Pydantic model_json_schema() correctly outputs a strict schema we can pass to the LLM API.

Phase 2: Zero-Knowledge PHI & Date Redaction
Action: Update the existing PHI module (`app/phi/`) — key files: `app/phi/service.py`, `app/phi/adapters/phi_redactor_hybrid.py`, `app/phi/adapters/presidio_scrubber.py`. Alternatively, create `app/redaction/redactor.py` (new).

Action: Enforce removal of ALL date and time strings. Replace with [DATE] / [TIME].

Success: Redaction is idempotent. Downstream agents ONLY see date-free text.

Phase 3: Implement StructurerAgent
Action: Implement Native Constrained Decoding in the LLM caller (`app/llm/client.py`) or agent logic (`app/agents/structurer/structurer_agent.py`).

Action: Force the LLM to output the vNext_draft JSON Schema.

Success: 100% of LLM outputs parse into Pydantic without fuzzy JSON-repair scripts. Non-null values contain an exact_quote field.

Phase 4: Quote Anchoring Engine
Action: Build `app/evidence/quote_anchor.py` (new directory and file).

Action: Implement find_quote_span(redacted_text, quote) using exact match -> whitespace-normalized -> rapidfuzz partial match.

Success: Spans are calculated purely from LLM quotes. Failures yield null values or INFERRED flags.

Phase 5: Tear Down the Regex Monolith
Action: Introduce a feature flag STRUCTURED_EXTRACTION_ENABLED.

Action: In `app/registry/processing/` (existing files: `masking.py`, `focus.py`, `cao_interventions_detail.py`, `linear_ebus_stations_detail.py`, `navigation_targets.py`, `disease_burden.py`, `navigation_fiducials.py`) and `app/registry/extractors/` (existing files: `v3_extractor.py`, `llm_detailed.py`, `noop.py`, `disease_burden.py`), route logic to the new StructurerAgent.

Action: Systematically delete regex dictionaries (e.g., BAL patterns, device patterns) and heuristic span-injection logic in `app/registry/deterministic_extractors.py`.

Success: Codebase shrinks dramatically. Pipeline is completely driven by schema-constrained LLM + anchoring.

Phase 6: Relation Extraction (NER -> RE)
Action: Define relation schema (e.g., SAMPLED_WITH, LESION_LOCATED_IN) — extend NER training at `ml/scripts/train_registry_ner.py`.

Action: Update `app/registry/postprocess/` to ingest explicit relations from the ML model payload rather than relying on proximity heuristics.

Success: Multi-station cross-talk errors drop.

Phase 7: Multi-Doc Longitudinal Endpoint
Action: Create `POST /api/v1/process_bundle` in `app/api/routes/` (new route file alongside existing `app/api/routes/unified_process.py`).

Action: Accept patient_handle (ZK ID), episode_id, and a list of docs with timepoint_role and seq.

Action: Implement the Timeline Aggregator agent to merge ParsedDoc entities into a cross-document outcome graph.

Success: Can track a lesion from CT to Pathology without storing a single date.

Phase 8: Golden Fixture Re-Baselining
Action: Run `ml/scripts/migrate_goldens_vNext.py` (new) against `proc_suite_notes/data/knowledge/golden_extractions_final/golden_*.json`.

Action: Repopulate the ~238 goldens with the newly generated EvidenceSpan artifacts.

Success: Tests pass on the new pipeline with complete end-to-end evidence anchoring.

---

🔄 Playbook Upgrades & Implementation Steps

The following upgrades refine the phases above with a **temporal translation** architecture. Absolute dates enter the system as ephemeral, transient fields that are translated into deterministic `T±X DAYS` tokens before the LLM ever sees the text. This eliminates LLM date-math hallucination and keeps the pipeline truly zero-knowledge.

### 1. Update Phase 7: Multi-Doc API Payload (The Ephemeral Anchor)

The client or ingestion gateway must supply absolute dates strictly as **transient fields** that are excluded from persistence schemas.

Action: Update `app/api/routes/process_bundle.py` (new route file alongside `app/api/routes/unified_process.py`):

```python
class ParsedDocRequest(BaseModel):
    timepoint_role: Literal["PREOP_IMAGING", "INDEX_PROCEDURE", "PATHOLOGY", "FOLLOW_UP"]
    seq: int
    ephemeral_doc_date: str = Field(exclude=True)  # E.g., "2024-01-01" (Dropped after Phase 2)
    text: str

class ProcessBundleRequest(BaseModel):
    zk_patient_id: str
    episode_id: str
    ephemeral_index_date: str = Field(exclude=True)  # The universal T-Zero Anchor (Dropped after Phase 2)
    documents: List[ParsedDocRequest]
```

### 2. Update Phase 2: Context-Aware Redaction (`app/phi/service.py`)

Upgrade the PhiRedactor from a "blind masking" tool to a **"temporal translation" engine**.

**Document-Level Anchoring:** Calculate the document's overall offset: `doc_t_offset = ephemeral_doc_date - ephemeral_index_date`. Prepend this securely to the top of the redacted document: `[SYSTEM: Document timeline is T{doc_t_offset} DAYS from Index Procedure]`.

**Inline Date Translation:** When `app/phi/adapters/presidio_scrubber.py` detects an explicit date inline (e.g., "01/20/2024"), it parses it ephemerally, calculates the delta against the `ephemeral_index_date`, and replaces the text with: `[DATE: T{+|-}{delta} DAYS]`.

**Guardrail:** If any calculated delta implies a span > 89 years, safely fall back to `[DATE: REDACTED]`.

**Garbage Collection:** Explicitly `del` the ephemeral dates from memory.

**Impact:** The LLM does not see dates. It receives mathematically computable strings like: *"Patient was readmitted on [DATE: T+5 DAYS] with a pneumothorax."*

### 3. Update Phase 1: vNext Schemas (Extracting T-Tokens)

Do not force the LLM to do multi-document chronological math. Force the LLM to **strictly extract** the translated temporal tokens.

Action: In `proc_schemas/registry/ip_vNext_draft.py` (LLM Output Schema):

```python
class ComplicationEventDraft(BaseModel):
    complication_type: str
    relative_onset_marker: Optional[str] = Field(
        description="Extract the exact relative timeline marker from the text, e.g., '[DATE: T+5 DAYS]'"
    )
    exact_quote: str = Field(
        description="Must match the redacted text verbatim."
    )
```

Action: In `proc_schemas/registry/ip_vNext.py` (Final API Schema):

```python
class LongitudinalOutcomes(BaseModel):
    # These will be populated by Deterministic Python in Phase 7, not the LLM
    time_to_diagnosis_days: Optional[int]
    time_to_treatment_days: Optional[int]
    thirty_day_complication: Optional[bool]
    follow_up_interval_lengths: List[int]
```

### 4. Update Phase 4: Quote Anchoring Engine

**Architectural Win:** Because the StructurerAgent (`app/agents/structurer/structurer_agent.py`) is reading the ephemerally translated text, its `exact_quote` will naturally be: *"readmitted on [DATE: T+5 DAYS] with pneumothorax"*.

When the deterministic engine (`app/evidence/quote_anchor.py`) runs its exact substring search on the redacted text, it will match perfectly. Pillar 1's Evidence Contract remains unbroken.

### 5. Update Phase 7: Timeline Aggregator Math

Once the bundle is structured by the LLMs via Phase 1 and entities are linked via Phase 6 (NER->RE), hand the final interval calculations over to **standard Python integer math**. This completely eliminates LLM hallucination on date math.

Action: Build deterministic math in `app/agents/aggregator/timeline_aggregator.py` (new):

```python
def compute_outcomes(parsed_docs: List[Any], extracted_entities: Any) -> LongitudinalOutcomes:
    outcomes = LongitudinalOutcomes(follow_up_interval_lengths=[])

    # 1. Map Timepoints via Pillar 3 Structures
    imaging_doc = next((d for d in parsed_docs if d.timepoint_role == "PREOP_IMAGING"), None)
    path_doc = next((d for d in parsed_docs if d.timepoint_role == "PATHOLOGY"), None)
    index_doc = next((d for d in parsed_docs if d.timepoint_role == "INDEX_PROCEDURE"), None)

    # 2. Deterministic "Time To" Math (Using the doc_t_offsets assigned in Phase 2)
    if path_doc and imaging_doc:
        # e.g., Path (T+2) - Imaging (T-14) = 16 days
        outcomes.time_to_diagnosis_days = path_doc.doc_t_offset - imaging_doc.doc_t_offset

    if index_doc and path_doc and path_doc.doc_t_offset < 0:
        # e.g., Index (T=0) - Path (T-20) = 20 days
        outcomes.time_to_treatment_days = index_doc.doc_t_offset - path_doc.doc_t_offset

    # 3. Deterministic Follow-ups
    for doc in parsed_docs:
        if doc.timepoint_role == "FOLLOW_UP":
            outcomes.follow_up_interval_lengths.append(doc.doc_t_offset)

    # 4. Deterministic "Within 30 Days" Math (Using extracted schemas)
    for complication in extracted_entities.complications:
        if complication.relative_onset_marker:
            # Parse "[DATE: T+5 DAYS]" -> 5
            day_offset = extract_int_from_token(complication.relative_onset_marker)
            if 0 < day_offset <= 30:
                outcomes.thirty_day_complication = True
                break

    return outcomes
```

---

🎯 Summary of Wins for the Engineering Team

**Total Regex Teardown:** You no longer need heuristic regex in `app/registry/deterministic_extractors.py` to figure out if "2 weeks post-procedure" means <= 30 days. The redactor normalizes everything into a mathematical `T±X` integer syntax.

**True Zero-Knowledge:** Absolute dates exist in RAM for roughly ~50 milliseconds. Your DB schemas and LLM payloads contain zero HIPAA-restricted timelines.

**Flawless Goldens Migration:** For Phase 8, when you run `ml/scripts/migrate_goldens_vNext.py`, you can easily script the injection of `[DATE: T+X DAYS]` markers into your ~238 legacy test files (`proc_suite_notes/data/knowledge/golden_extractions_final/golden_*.json`) based on their known chronological properties, ensuring your CI/eval pipeline passes natively.