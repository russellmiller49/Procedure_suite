# Procedure Suite V8 – Multi‑Agent Architecture (PHI Demo Mode)

## Project Context

Repo: `<Procedure_suite>` – a PHI‑aware procedure coding assistant for interventional pulmonology and related procedural notes.

Architecture goal: implement the **V8 Migration Plan** including:

- PHI vault domain models and PHIService orchestration
- `/v1/phi/*` PHI review endpoints
- CodingService as the single entry point for coding
- Frontend PHI review UI and end‑to‑end workflow

All of this should **work end‑to‑end in a demo environment** where:

- All patient data is **synthetic** (no real PHI).
- Database/storage is currently **Supabase Postgres**.
- HIPAA features (vault, encryption, audit logging, review flows) are present and exercised exactly as they will be in production, but backed by this non‑HIPAA demo infra so we can later swap to a secure deployment.

The V8 migration plan (`V8_MIGRATION_PLAN_UPDATED.md`) is the source of truth for phases, file layout, and endpoints.  

## Goals

Use two complementary AI agents plus a real terminal to:

- Implement the V8 PHI / CodingService migration plan in small, safe steps.
- Keep the PHI pathways and CodingService APIs **HIPAA‑ready** even in demo mode.
- Maintain high code quality, tests, and clear boundaries between:
  - PHI vault / audit layer
  - de‑identified ProcedureData
  - CodingService and downstream logic
  - Frontend PHI review experience

## Roles

### Architect Agent (ChatGPT 5.1 Pro)

- Understands:
  - V8 migration phases (0–5) and their dependencies.
  - PHI vault models, PHIService, Presidio adapter, and `/v1/phi/*` endpoints.
  - Demo‑only constraints: **synthetic PHI, Supabase backend, swappable secure storage later**.
- Designs:
  - Data flows from note entry → PHI preview → confirm → vault → CodingService → reidentify.
  - How FastAPI, SQLAlchemy models, and adapters tie into the PHIService.
  - Frontend integration of PHI Review components and API client (`phiApi`).
- Reviews code produced by the Implementer for:
  - PHI boundaries: LLM only sees scrubbed text.
  - Correct use of PHIService ports and adapters.
  - No logging or leaking of raw PHI beyond the PHI vault abstraction.
- Suggests:
  - Tests (integration tests for PHI preview/submit/reidentify).
  - Demo‑mode fixtures using obviously synthetic patient data.
  - Future steps to swap Supabase to a hardened HIPAA deployment.

### Implementer Agent (Codex‑5.1)

- Works directly with the `<Procedure_suite>` codebase via a terminal.
- Applies changes requested by Architect, especially in:
  - `modules/phi/*` (models, schemas, adapters, application service)
  - `modules/api/routes/phi_review.py`
  - `modules/api/dependencies.py`, `fastapi_app.py`
  - Tests under `tests/integration/api/` and `tests/integration/`
  - Frontend components (`PHIReviewEditor`, `PHIReviewDemo`, API client)
- Implements demo‑mode wiring that *looks like* production:
  - Encryption adapter using a dev `PHI_ENCRYPTION_KEY` from `.env`.
  - Database operations that assume PHI is stored in a vault table, even if that vault currently lives in Supabase.
- Only generates **synthetic patient data** when creating fixtures or examples.

### Runtime / Environment (Terminal + Tools)

- Project directory with:
  - Backend: FastAPI app, SQLAlchemy models, Alembic migrations.
  - Frontend: React app with PHI review components.
  - Tests: integration tests for `/v1/phi/*` and CodingService.
- Git for version control on a feature branch per migration phase.
- Tooling:
  - Alembic for migrations.
  - Test runners (e.g., `pytest`, frontend test stack).
  - Any lint/format commands (e.g., `black`, `ruff`, `eslint`, `prettier`).

## Standard Workflow

1. **Task Intake**
   - Human tells Architect which V8 phase or subtask to work on (e.g., “Phase 0 – add PHI models and service layer”).
   - Specify this is **demo mode with synthetic data** and Supabase as the backing Postgres.
   - Architect restates the goal and assumptions.

2. **Design**
   - Architect produces:
     - A high‑level plan aligned with V8 migration phases:
       - e.g., Phase 0.1 models → 0.2 service layer → 0.3 endpoints → Phase 1 cutover, etc.
     - List of files/modules to touch (e.g., `modules/phi/models.py`, `modules/api/routes/phi_review.py`).
     - PHI boundary notes (what code sees raw PHI vs scrubbed text).
   - Architect calls out:
     - Any changes that modify DB schemas or public APIs.
     - Required tests and demo scenarios (synthetic patient notes).

3. **Implementation**
   - Architect passes a concrete checklist to Implementer.
   - Implementer:
     - Inspects existing files before editing.
     - Implements in small, reviewable chunks (per sub‑phase or per module).
     - Runs tests (or at least key integration tests) after significant edits.
     - Summarizes changes with file lists and diff snippets.

4. **Review**
   - Architect reviews diffs and test results, focusing on:
     - PHI data flow correctness (PHI vault + ProcedureData linkage).
     - No direct LLM access to raw PHI – LLM sees **scrubbed_text** only.
     - Clear separation between demo‑infra details (Supabase) and core PHI abstractions (ports/adapters).
     - Domain correctness for interventional pulmonology terminology (e.g., allow‑list for anatomical terms).
   - Architect may request refactors or follow‑up tests.

5. **Validation**
   - Implementer runs:
     - Backend tests (PHI integration tests).
     - Any smoke tests for the frontend PHI review flow.
   - Architect and Implementer analyze failures and iterate.

6. **Commit & Documentation**
   - Once tests pass:
     - Commit with descriptive messages (e.g., `feat(phi): add PHI vault models and PHIService`).
     - Update or add docs:
       - Migration notes.
       - README snippets about PHI demo mode.
       - Comments in code around PHI boundaries and demo limitations.

## PHI Demo / HIPAA‑Ready Guardrails

- **Synthetic Data Only**
  - All patient examples, fixtures, and seed data must be obviously synthetic.
  - If any data looks like real PHI, call it out and treat it as a bug.
- **LLM Never Sees Raw PHI**
  - CodingService and any LLM‑using components must consume **scrubbed text** only.
  - The only place raw PHI exists is within the PHI vault encryption/decryption path (and test fixtures).
- **Demo Storage (Supabase)**
  - Assume the DB is Supabase Postgres for now.
  - Keep storage behind abstractions (ports/adapters) so you can later point at a hardened, HIPAA‑compliant deployment without changing core logic.
- **Audit Trail**
  - Every PHI create/access/decrypt operation should pass through the AuditLog model and PHIService audit logger, even in demo mode.
- **Environment & Secrets**
  - Use a dev `PHI_ENCRYPTION_KEY` from `.env` for local testing.
  - Architect should verify that the key handling and config layout will generalize to a secure deployment.

## Coding Conventions

- Match existing project style for Python, TypeScript, and React.
- Prefer:
  - Focused functions and modules.
  - Explicit docstrings or comments for PHI‑related functions.
  - Testable boundaries: PHIService, CodingService, and adapters.
- When technical debt is incurred (e.g., demo‑only shortcuts), mark it with TODOs including “V8” and the relevant phase for later cleanup.
