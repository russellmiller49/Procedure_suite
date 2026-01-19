# Codex Instructions: Extraction Pipeline V2 (Consolidation Plan)

## 0. Phase 0: Architecture Cleanup (Resolve Conflicts)
**Goal:** Fix the "Split Brain" issues identified in the audit before applying new logic.

1.  **Eliminate Duplicate Endpoint:**
    *   **Delete** the inline definition of `@app.post("/api/v1/process")` in `modules/api/fastapi_app.py` (approx line 880).
    *   **Verify** that `fastapi_app.py` mounts the `unified_process` router correctly. This is now the single source of truth.
2.  **Unify Reconciliation Logic:**
    *   Codex found two engines: `CodeReconciler` (legacy) vs `ConfidenceCombiner` (production).
    *   **Refactor:** Ensure the `parallel_ner` engine utilizes **`ConfidenceCombiner`**.
    *   **Logic:** The combiner must implement "Evidence > Probability" (NER hits override low-confidence ML predictions) regardless of whether the LLM is active.
3.  **Expanded Legacy Lockout:**
    *   The following endpoints must be added to the "Forbidden" list (return 410 Gone if legacy mode is off):
        *   `/api/registry/extract`
        *   `/api/v1/procedures/{id}/extract`

---

## 1. Configuration Contract (Fail-Fast)

Codex must enforce these values in `modules/api/fastapi_app.py` startup events.

### 1.1 Required Production Env
```bash
# --- Golden path ---
PROCSUITE_PIPELINE_MODE=extraction_first   # Must be exactly this
REGISTRY_EXTRACTION_ENGINE=parallel_ner
REGISTRY_SCHEMA_VERSION=v3

# --- Safety Net ---
PROCSUITE_ALLOW_LEGACY_ENDPOINTS=0         # Hard disable of old paths
REGISTRY_AUDITOR_SOURCE=raw_ml
REGISTRY_SELF_CORRECT_ENABLED=1            # Enable LLM judge on scrubbed text (set 0 for faster responses)
```

### 1.2 Validation Rules
If PROCSUITE_PIPELINE_MODE == "parallel_ner", RAISE ERROR. Do not alias. Force config cleanup.

If PROCSUITE_ALLOW_LEGACY_ENDPOINTS is 0, requests to old endpoints (including the newly identified ones) must fail immediately.

2. Fix the "LLM Disabled" Trap
2.1 Stop using NoOpLLMExtractor on production routes
Production: Reject any request attempting to use NoOpLLMExtractor.

Dev: If mode="no_llm", route to parallel_ner (using ConfidenceCombiner) with the LLM flag disabled. Do not route to the old "engine_only" path.

2.1b LLM usage policy (approved)

- The server may call an external LLM **only on scrubbed text** as part of registry self-correction (`REGISTRY_SELF_CORRECT_ENABLED=1`).
- For faster responses, set `REGISTRY_SELF_CORRECT_ENABLED=0` (or `PROCSUITE_FAST_MODE=1` in dev).

2.2 Fix Evidence Plumbing
Requirement: No extraction response shall return evidence: {} if a value was found.

Implementation:

Modify parallel_ner to return span data in the V3 Prediction format.

Update RegistryService._shape_registry_payload to accept and merge this evidence.

Schema: {"source": "ner_span", "text": "...", "span": [x, y], "confidence": 1.0}.

3. Clinical Guardrails (Post-Process)
Implement the following logic in a new class modules/extraction/postprocessing/clinical_guardrails.py.

3.1 Navigation Failure (Modifier -53)
Trigger: CPT 31627 extracted + keywords (mis-registering, unable to navigate, aborted, failure).

Action:

Do NOT remove 31627.

Set needs_review = true.

Append warning: "Navigation failure detected. Verify Modifier -53."

3.2 Radial vs. Linear EBUS
Trigger: Ambiguity between 31652 (Linear) and 31654 (Radial).

Rule:

"Concentric" OR "Eccentric" view = Radial (31654).

"Convex" OR "Station [X] Sampling" = Linear (31652).

Action: Hard override of the code.

3.3 IPC vs. Chest Tube
Trigger: 32550 (IPC) vs 32551 (Chest Tube).

Rule:

"PleurX", "Aspira", "Tunneled" = IPC.

"Pigtail", "Wayne", "Pleur-evac" = Chest Tube.

Conflict: If both present, prioritize the device being implanted.

4. Documentation & Artifacts
Create Missing File: Create Output_examples.txt in the root if missing, populating it with the failure cases described.

Update User Guide: Explicitly document /api/v1/process as the Machine Extraction endpoint, noting that it returns needs_review=true for PHI compliance.

Config Reference: Update .env.example to remove the deprecated parallel_ner value for PROCSUITE_PIPELINE_MODE.

5. Regression Tests
Create tests/integration/test_pipeline_integrity.py:

Test Duplicate Route: Verify /api/v1/process hits the Router (check for a specific header or response structure unique to the router).

Test Legacy Lockout: Verify /api/registry/extract returns 410.

Test Config Crash: Mock env var PROCSUITE_PIPELINE_MODE=parallel_ner and verify app startup raises ValueError.

Test Evidence: Verify parallel_ner returns populated evidence objects.
