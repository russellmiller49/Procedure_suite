11) OpenAI compat adapter hardening (fix 400/404 + timeouts)

Goal
- Eliminate OpenAI-provider errors that block product functionality (HTTP 400/404) while keeping GPT-5-class models usable.
- Add deterministic fallback behavior and tests.

Most likely causes
- 400 from sending unsupported parameters for a given model (e.g., `response_format`, `temperature/top_p` constraints on some GPT-5 variants).
- 404 from one of: incorrect base URL/path (double `/v1`, missing `/chat`), wrong endpoint for the request type (`/v1/chat/completions` vs `/v1/responses`), or model not enabled/available for the project.

Deliverables
- Capability-aware request builder that strips/adjusts incompatible params per model family.
- Base URL normalization (guarantee exactly one `/v1` segment).
- Endpoint routing and fallback:
  - Primary: `/v1/chat/completions` for chat payloads
  - Optional: `/v1/responses` for structured output workflows where used
  - On 404/400, retry once with a safe fallback configuration.
- Provider self-test command: verify model availability (via `GET /v1/models`) and verify that chosen model can complete a minimal prompt.
- Increased timeouts for registry extraction tasks; configurable per task.

Tasks
1. **Normalize OpenAI base URL**
   - Ensure code never produces `.../v1/v1/...`.
   - Add unit tests for URL joining.
2. **Capability matrix + param filtering**
   - Add `model_capabilities.py` (or equivalent) to decide whether a model supports: JSON response formats, tool strict outputs, and which sampling params are allowed.
   - Strip unsupported keys from the payload before sending.
3. **Retry + fallback policy**
   - If request returns 400 with “unsupported parameter” semantics, retry once after removing the offending parameter(s).
   - If request returns 404, run a lightweight model availability check and fall back to a known-good model snapshot for the task (configurable).
4. **Timeouts**
   - Set higher defaults for extraction tasks and make them configurable by task type.
5. **Tests (must be green)**
   - Add tests that simulate 400/404 responses (mock httpx) and assert the adapter retries/falls back correctly.
   - Ensure tests never call real network.

Acceptance
- Local devserver no longer logs OpenAI 400/404 for supported configurations.
- Registry extraction and coder LLM fallback succeed with configured models.

⸻

12) ML auditor + retraining roadmap (post‑implementation)

...

⸻

Codex Prompts (copy/paste)

Codex Prompt — Phase 11

Implement Phase 11 from docs/CODEX_IMPLEMENTATION_PLAN_v5_POST.md. Harden the OpenAI compat adapter to prevent 400/404 failures: normalize base URL, add model capability filtering to strip incompatible params, implement retry-on-unsupported-parameter, implement 404 model-availability check + fallback model routing, and increase configurable timeouts for extraction tasks. Add unit tests using mocked httpx responses to prove retries/fallbacks work and ensure no real network calls occur.

Codex Prompt — Phase 12.1

Implement Phase 12.1 from docs/CODEX_IMPLEMENTATION_PLAN_v5_POST.md. Add structured auditor output types (Pydantic), emit an MLAuditReport in extraction_first responses, and add an offline CLI script to run RawMLAuditor on a JSONL of notes. Ensure zero network calls. Add/extend tests that monkeypatch SmartHybridOrchestrator.get_codes and CodingRulesEngine.validate to raise if called; confirm auditor uses MLCoderPredictor.classify_case on raw note text.

Codex Prompt — Phase 12.2

Implement Phase 12.2. Add scripts/training/build_registry_training_dataset.py to run extraction_first + derive_procedures_from_granular + deterministic CPT rules on a batch of notes and output JSONL rows. Implement modules/training/label_cleaning.py to detect/flag bundling suppression artifacts and produce a review queue. Must run offline (no external LLM calls). Add tests for label_cleaning behavior on synthetic inputs.

Codex Prompt — Phase 12.3

Implement Phase 12.3. Define a stable registry-flag label set and extract_labels_from_registry(record). Update dataset builder to emit target_registry_flags. Add train/eval scripts to train a multi-label registry-flag predictor that outputs artifacts compatible with runtime (label_order.json, thresholds.json, model_int8.onnx or equivalent). Integrate a new auditor mode REGISTRY_AUDITOR_TARGET=registry_flags behind feature flags while keeping CPT audit as default. Add tests and docs.

⸻

If you want, paste your current MLCoderPredictor return type (what fields it exposes for predictions/buckets/thresholds) and your RegistryRecord schema surface, and I’ll tailor exact label names + mapping logic and the artifact-cleaning heuristics to your codebase (so Codex doesn’t have to guess types).