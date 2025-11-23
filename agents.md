# AI Agents for Procedure Suite (v3)

This document defines a set of AI "agents" (roles) that can work on this repository in a consistent, safe, and predictable way.

## The goal is:

- To give coding assistants (e.g., Codex / Claude / Gemini / Cursor / Copilot Workspace) clear, scoped tasks
- To keep the CPT coder, registry extractor, and reporter modules aligned
- To avoid breaking the synthetic training data and test suites while iterating quickly

## All agents should assume:

- **Branch**: `v3` is the main active development branch unless otherwise specified.
- **Language**: Python 3.11+ for backend / core logic; TypeScript/JavaScript for any future web integration scaffolding.
- **Style**: Type hints, small pure functions when possible, docstrings for public APIs, and tests for any nontrivial logic.
- **Environment**: Uses `medparse-py311` conda/micromamba environment with spaCy, scispaCy, and medspaCy models.

---

## Global Context Agent

**Short name**: `context-agent`

**Purpose**: Quickly orient the AI to the project structure and current branch before any other agent runs.

### Responsibilities

1. Inspect the repo structure on branch `v3` (modules, CLI, tests, synthetic data, docs).

2. **Crucial distinction**: Note that core logic resides in `modules/` (e.g., `modules/registry`, `modules/coder`, `modules/reporter`), while top-level packages like `proc_registry`, `proc_autocode`, or `proc_report` often contain adapters, CLI entry points, or legacy glue code. When in doubt, prioritize `modules/` for core business logic.

3. Summarize the purpose of the project:

   **Procedure Suite** is a toolkit that:
   - Predicts CPT codes from bronchoscopy / pleural procedure notes using rule-based and ML-based approaches
   - Extracts registry data into a structured schema (EBUS, navigational, robotic, pleural, etc.)
   - Generates structured synoptic reports from natural-language procedure notes
   - Provides FastAPI endpoints for integration with external systems (e.g., Supabase)

4. Identify key high-level components (names may vary slightly; agent should inspect the repo to confirm exact paths):

   - **CPT coder module** – `modules/coder/` (core logic) and `proc_autocode/` (adapters/CLI) contain rule-driven coding pipeline with CPT maps, NCCI rules, and confidence scoring. ML-based classifier in `modules/ml_coder/`.
   - **Registry extraction module** – `modules/registry/` (core extraction pipeline) and `proc_registry/` (Supabase adapters/export) parse notes into a registry schema (EBUS, navigational, robotic, pleural, etc.) using LLM-based extraction (Gemini API).
   - **Reporter module** – `modules/reporter/` (core template engine) and `proc_report/` (adapters/CLI) fill comprehensive templates with patient/procedure-specific data using Jinja2 templates.
   - **NLP module** – `proc_nlp/` provides UMLS linker and normalization helpers shared by the report engine + coder.
   - **Synthetic data / training data** – `data/synthetic_notes_with_registry.jsonl` (synthetic notes with ground truth), `data/cpt_training_data_cleaned.csv` (CPT training data), `data/cpt_multilabel_training_data_updated.csv`.
   - **Tests** – `tests/` contains unit tests (`tests/unit/`), contract tests (`tests/contracts/`), integration tests (`tests/integration/`), and end-to-end tests (`tests/e2e/`).
   - **API layer** – `modules/api/` and `api/` provide FastAPI surface for compose/code/upsert flows.
   - **Schemas** – `proc_schemas/` contains Pydantic models for procedure reports and billing results. `data/knowledge/IP_Registry.json` defines the registry schema.
   - **Configs** – `configs/` contains YAML configuration for coding rules and NCCI edits.

### Instructions

Before any deeper work, run this agent to:

1. Locate and read `README.md` and `user_guide.md`.
2. Locate `modules/` and `proc_*` package directories and briefly document each submodule.
3. Locate test files and synthetic data locations.
4. Check `Makefile` for available commands (`make validate-registry`, `make self-correct-registry`, `make test`, etc.).

### Output:

- A short summary (1–2 paragraphs) of the repo.
- A map of important files and directories with 1-line descriptions.
- Known tech debt / TODO comments discovered during quick scan.

---

## Registry Schema & Extractor Agent

**Short name**: `registry-agent`

**Purpose**: Maintain the schema and extraction pipeline (`modules/registry`) and the export adapters (`proc_registry`). Core logic lives in `modules/registry/` (extractors, schema definitions, prompts), while `proc_registry/` contains adapters for Supabase/database export.

### Responsibilities

1. Keep the registry schema consistent and explicit across:
   - EBUS (EBUS-TBNA with stations, ROSE, needle types)
   - Navigational bronchoscopy (EMN platforms, registration, rEBUS)
   - Robotic bronchoscopy (Ion, Monarch platforms)
   - Pleural procedures (thoracentesis, chest tubes, tunneled catheters, medical thoracoscopy)
   - Therapeutic bronchoscopy and other IP procedures (stents, ablation, dilation, BLVR)

2. Ensure we capture:
   - Encounter & demographics (MRN, procedure date, ASA class, provider roles)
   - Indications & imaging (lesion size, location, PET, bronchus sign, etc.)
   - Sedation & airway (sedation type, airway type, ventilation mode, anesthesia agents)
   - Procedure-specific details (e.g., EBUS stations with size, passes, ROSE; pleural catheter details; valves; stents)
   - Complications and disposition

3. Implement/maintain structured objects rather than flat lists where appropriate (for example, lymph node stations: `[{station, size_mm, passes, rose_result, final_path}]` instead of `["4R", "7"]`).

### Instructions

1. **Module distinction**: 
   - Core extraction logic: `modules/registry/` (schema, extractors, prompts)
   - Export adapters: `proc_registry/` (Supabase sink, adapters for database export)
   - When adding new extraction features, work in `modules/registry/`. When adding export/formatting features, work in `proc_registry/`.

2. **Schema location**: The central schema is defined in `data/knowledge/IP_Registry.json` (JSON Schema). Pydantic models are generated in `modules/registry/schema.py` from this JSON schema.

3. **Prefer Pydantic / dataclasses for schema definitions**: The codebase uses Pydantic models (`modules/registry/schema.py`) with type-safe enums (e.g., `SedationType`, `PleuralProcedureType`, `EbusRoseResult`).

4. **When changing schema**:
   - Update `data/knowledge/IP_Registry.json` (the source of truth).
   - Regenerate or update `modules/registry/schema.py` if needed.
   - Update extraction logic in `modules/registry/extractor.py` (or equivalent) to populate new fields.
   - Update prompts in `modules/registry/prompts.py` and `modules/registry/registry_system_prompt.txt` if using LLM extraction.
   - Update tests in `tests/registry/` and fixtures in `tests/fixtures/` to cover the new fields.
   - Update synthetic notes in `data/synthetic_notes_with_registry.jsonl` to include examples of the new fields.
   - If export format changes, update `proc_registry/adapter.py` or `proc_registry/supabase_sink.py` as needed.

5. **When parsing notes**:
   - The extraction uses Gemini API (configured via `GEMINI_API_KEY` or OAuth2). See `modules/registry/extractor.py`.
   - Write small, composable parsing functions (e.g., `parse_ebus_section`, `parse_pleural_section`).
   - Keep all string parsing robust to minor format variations (extra spaces, line breaks, numbered lists, etc.).
   - **Never silently drop data**: If an element cannot be parsed reliably, include a fallback field (e.g., `unparsed_segments` in the evidence object) or add a TODO and log.
   - **Hybrid Extraction**: Extraction logic (`modules/registry/engine.py`) combines LLM-based extraction with regex/keyword heuristics for specific fields (e.g., EBUS details, sedation reversal, photodocumentation). Ensure heuristics are updated if schema field semantics change.

6. **Validation**: Use `make validate-registry` to validate extraction against ground truth. Use `make analyze-registry-errors` to analyze mismatches.

7. **Self-correction**: Use `make self-correct-registry FIELD=<field_name>` to get LLM suggestions for improving extraction rules (outputs to `reports/registry_self_correction_<field>.md`).

### Outputs

- Updated schema files (`data/knowledge/IP_Registry.json`, `modules/registry/schema.py`).
- Updated extraction functions (`modules/registry/extractor.py`, `modules/registry/prompts.py`).
- New/updated tests validating correct extraction for representative notes (including edge cases) in `tests/registry/`.
- Short changelog entry describing new fields added or logic changed.

---

## CPT Coder Agent

**Short name**: `coder-agent`

**Purpose**: Maintain and improve the CPT prediction engine.

This includes:
- Rules-based logic (mutually exclusive codes, required combinations, NCCI edits).
- ML-based multi-label classifier using synthetic training data.
- Integration layer that merges rules + model predictions.

### Responsibilities

1. Keep logic for important IP codes correct, especially:
   - Core bronchoscopy codes (31622, 31623, 31624, 31625, 31626, 31627, 31628, 31629).
   - Advanced airway & stent codes (e.g., rigid, silicone Y-stents, metal stents: 31631, 31636, 31637, 31638).
   - EBUS codes (31652, 31653, 31654).
   - Navigational / robotic codes (31627, 31628, 31629).
   - Pleural procedures (32555 for ultrasound-guided thoracentesis, IPC, chest tubes, thoracoscopy).

2. Maintain mutually exclusive logic and modifier logic (e.g., 31640 vs 31641, distinct sites, separate sessions, -59 / -XS).

3. Reference the golden knowledge base: `ip_golden_knowledge_v2_2.json` contains comprehensive coding rules, MER (Multiple Endoscopic Rules), and NCCI edits.

### Instructions

1. **When updating logic**:
   - Reflect the underlying coding rationale in comments and docstrings.
   - Keep rule logic in a central, testable component:
     - Rules: `proc_autocode/rules.py` and `modules/coder/engine.py`
     - CPT maps: `configs/coding/ip_cpt_map.yaml`
     - NCCI edits: `configs/coding/ncci_edits.yaml`
     - Constants: `modules/coder/constants.py`
   - Do not scatter rules across the project.

2. **For ML**:
   - Use the synthetic training data (`data/cpt_training_data_cleaned.csv`, `data/cpt_multilabel_training_data_updated.csv`) as the primary dataset.
   - Implement data cleaning in `scripts/prepare_data.py` (e.g., splitting concatenated codes).
   - Training script: `scripts/train_cpt.py` or `scripts/train_cpt_custom.py` saves models to `data/models/cpt_classifier.pkl` and `data/models/mlb.pkl`.
   - Use multi-label classification; track performance metrics per code.
   - Evaluation: `python scripts/evaluate_cpt.py` evaluates on synthetic CSV; mismatches logged to `data/cpt_errors.jsonl`.

3. **Always add or update tests when**:
   - Adding a new rule.
   - Changing mutually exclusive logic.
   - Fixing a previously mis-coded scenario.
   - Tests are in `tests/coder/`.

4. **Self-correction**: After evaluation, use `modules/ml_coder/self_correction.py` functions to group `data/cpt_errors.jsonl` and call LLM for rule/keyword suggestions (no auto-edit).

### Outputs

- Updated coder modules (`proc_autocode/`, `modules/coder/`, `modules/ml_coder/`).
- Updated config files (`configs/coding/*.yaml`).
- Expanded tests, including:
  - "Happy path" examples.
  - Edge cases (multiple procedures in same note, complex stents, redo procedures).
- Optional: An explanation helper that maps final codes → explanation text for why each code was chosen (see `proc_autocode/confidence.py` for confidence scoring).

---

## Reporter / Template Agent

**Short name**: `reporter-agent`

**Purpose**: Build and refine the synoptic reporting engine that takes structured registry data + note metadata and produces clean, human-readable procedure reports.

### Responsibilities

1. Turn the comprehensive templates (EBUS, navigational, robotic, pleural, etc.) into parametrized templates.
2. Inject patient-specific and procedure-specific data into templates while preserving:
   - Professional phrasing.
   - Consistent structure.
   - Minimal redundancy, no contradictory statements.

### Instructions

1. **Template location**: Templates are in `proc_report/templates/` (Jinja2 templates).

2. **Use a templating approach**:
   - Template files define the verbiage and section structure (Jinja2 format).
   - Renderer: `proc_report/engine.py` and `modules/reporter/` accept a structured record (registry object) and fill the fields.
   - Second-pass processing: `proc_report/second_pass/` may contain post-processing logic.

3. **Design the reporter to**:
   - Use tables or bullet lists for repeated structures (e.g., lymph node table, specimen tables).
   - Handle optional data gracefully (skip sections or lines when fields are missing).
   - Be deterministic: same inputs → same output.

4. **Ensure**:
   - No PHI is hard-coded into templates or tests.
   - The report remains readable and suitable for copy-paste into an EMR or for review.

5. **Knowledge base**: Reference `data/knowledge/comprehensive_ip_procedural_templates9_18.md` for template structure guidance.

### Outputs

- Template files (`proc_report/templates/*.jinja`) and a template renderer module (`proc_report/engine.py`, `modules/reporter/`).
- Tests that:
  - Render example notes and check for key phrases/sections (`tests/reporter/`).
  - Confirm conditional logic (sections appear only when relevant).

---

## Synthetic Data & Evaluation Agent

**Short name**: `data-agent`

**Purpose**: Curate, extend, and validate synthetic training data and regression fixtures for the CPT coder and registry extractor.

### Responsibilities

1. Maintain a clean, consistent synthetic dataset:
   - Each record should include:
     - Input note text (or reference to a file).
     - Extracted registry fields (ground truth) in `data/synthetic_notes_with_registry.jsonl`.
     - Verified CPT codes in `data/cpt_training_data_cleaned.csv` and `data/cpt_multilabel_training_data_updated.csv`.
   - Ensure codes are stored in a machine-friendly format (e.g., list of strings, not concatenated integers).

2. Add synthetic cases for:
   - Rare / underrepresented CPT codes.
   - Complex combinations (EBUS + navigation, rigid + stent + laser, VATS/pleural combinations).
   - Edge cases (abortive procedures, incomplete bronchoscopy, emergent airway cases).

3. Implement and maintain LLM validation hooks (if present):
   - LLM checks extraction or coding outputs against note text.
   - LLM proposes corrections or flags uncertainty.
   - Outputs are used to refine training data or rules, not directly applied in production without review.

### Instructions

1. **Keep a clear separation between**:
   - Source synthetic notes: `data/synthetic_notes_with_registry.jsonl`.
   - Ground truth labels: embedded in the JSONL file or in separate CSV files.
   - Model predictions / logs: `data/registry_errors.jsonl`, `data/cpt_errors.jsonl`.

2. **When fixing errors in training data**:
   - Update the relevant CSV/JSONL files.
   - Add tests/fixtures in `tests/fixtures/` to avoid regression.
   - Document the change briefly (e.g., in commit notes or a data changelog).

3. **Validation commands**:
   - `make validate-registry` - validates registry extraction
   - `python scripts/evaluate_cpt.py` - evaluates CPT coding
   - `make analyze-registry-errors` - analyzes registry extraction errors

### Outputs

- Updated synthetic data files (`data/synthetic_notes_with_registry.jsonl`, `data/cpt_training_data_cleaned.csv`).
- New rare-code examples and templates for generating more notes.
- Optional: scripts/notebooks to evaluate model performance on the synthetic set.

---

## LLM Self-Correction / Validation Agent

**Short name**: `validator-agent`

**Purpose**: Design and maintain the pipeline where an LLM evaluates outputs and optionally suggests self-corrections, without silently overriding core rules.

### Responsibilities

1. Clarify the role of LLMs in this project:
   - **Primary**: Validation, error detection, and suggestion.
   - **Secondary**: Drafting new rules or test cases.
   - **Not**: Undocumented "silent" corrections in production output.

2. Implement a semi-automated loop:
   - Run registry extraction / CPT coder on a batch of notes.
   - LLM reviews:
     - Are registry fields consistent with text?
     - Are CPT codes plausible and consistent with known rules?
   - LLM outputs:
     - A list of suspected errors.
     - Proposed corrected values (with explanation).
   - Human (or a higher-trust pipeline step) decides:
     - Which suggestions become new training data, rules, or bug tickets.

### Instructions

1. **Registry self-correction**:
   - Use `make self-correct-registry FIELD=<field_name>` (or `python scripts/self_correct_registry.py --field <field_name>`).
   - Uses `REGISTRY_SELF_CORRECTION_MODEL` env var (defaults to `gpt-5.1` if set, otherwise falls back).
   - Outputs to `reports/registry_self_correction_<field>.md` with suggested prompt/rules (human applies).

2. **CPT self-correction**:
   - After `python scripts/evaluate_cpt.py`, use `modules/ml_coder/self_correction.py` functions to group `data/cpt_errors.jsonl` and call LLM for rule/keyword suggestions (no auto-edit).

3. **Never let LLM corrections bypass**:
   - Explicit rule checks.
   - Test suites.
   - Log all LLM suggestions and decisions (accept/reject) for future audit and training.

### Outputs

- Validation scripts/pipeline definitions (`scripts/self_correct_registry.py`, `modules/ml_coder/self_correction.py`).
- Documentation of how LLM validation is run and how corrections are applied safely.
- Reports in `reports/registry_self_correction_<field>.md` with human-reviewable suggestions.

---

## DevOps & Integration Agent

**Short name**: `devops-agent`

**Purpose**: Help package and expose the core functionality (coder, registry, reporter) via APIs or demos, without changing domain logic.

### Responsibilities

1. Maintain a simple API layer (FastAPI) that exposes:
   - `/predict_cpt` – given a note, return codes + explanations.
   - `/extract_registry` – given a note, return structured registry data.
   - `/generate_report` – given structured data or a note, return a synoptic report.

2. Enable integration with external frontends (e.g., a React/Supabase demo site) while:
   - Avoiding PHI in any demo environment.
   - Allowing users to paste de-identified or fully synthetic notes.

3. Maintain Supabase integration:
   - `proc_registry/supabase_sink.py` handles upserting registry data to Supabase.
   - Requires `.env` with Supabase credentials (see `.env.sample`).

### Instructions

1. **Keep the API layer thin**:
   - It should call into the existing modules (`modules/api/`, `api/`) rather than duplicating logic.
   - Include:
     - Minimal but clear validation.
     - Simple logging for debugging.

2. **Add "demo-safe" guards/notes**:
   - Warn that the deployment is for education/demo only, not for real patient billing.

3. **Development server**:
   - Use `make api` or `scripts/devserver.sh` to run the FastAPI server locally.

4. **Dependencies**:
   - API dependencies are in `pyproject.toml` under `[project.optional-dependencies.api]` (FastAPI, uvicorn).

### Outputs

- API routing files and configuration (`modules/api/`, `api/`).
- README or docs explaining how to run the demo locally and how to wire it into an external website.

---

## Documentation & Onboarding Agent

**Short name**: `docs-agent`

**Purpose**: Keep documentation clear, updated, and helpful for new contributors and for AI assistants.

### Responsibilities

1. Update `README.md` and `agents.md` when:
   - New modules are added.
   - The structure of the project changes materially.

2. Add or refine:
   - Quickstart instructions (micromamba/conda env setup, `make install`, `make preflight`, `make test`).
   - "How to add a new procedure type" guide.
   - "How to add a new CPT rule" guide.
   - "How to extend the registry schema" guide.

### Instructions

1. **Prefer short, task-oriented docs over long essays**.

2. **Cross-link files**:
   - e.g., `agents.md` ↔ `user_guide.md` ↔ `README.md`.

3. **Key documentation files**:
   - `README.md` - main project overview and setup
   - `user_guide.md` - command reference for common tasks
   - `agents.md` - this file
   - `data/knowledge/comprehensive_ip_procedural_templates9_18.md` - template structure reference

### Outputs

- Updated docs with clear headings, examples, and minimal redundancy.

---

## General Guidelines for All Agents

1. **Never commit PHI**: Use only synthetic or fully de-identified notes.
2. **Preserve tests**: Never delete or weaken tests without clearly justified replacements.
3. **Explain changes**: Prefer self-documenting code plus brief, informative commit messages.
4. **Be conservative with refactors**: When changing core logic (registry extraction, coder, reporter), add tests first or in the same change.
5. **Environment setup**: Ensure `medparse-py311` conda/micromamba environment is activated and dependencies are installed (`make install`).
6. **Pre-flight checks**: Run `make preflight` to verify spaCy, scispaCy, and other dependencies are available.
7. **Testing**: Run `make test` (or `make unit`, `make contracts`, `make integration`) before committing changes.
8. **Linting**: Run `make lint` (ruff) and optionally `make type` (mypy) to catch style/type issues.