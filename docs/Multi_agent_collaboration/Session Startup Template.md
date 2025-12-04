=== AI COLLAB SESSION STARTUP (Procedure Suite V8 / PHI Demo) ===

1) Prepare the environment
   - Open the `<Procedure_suite>` project directory in the terminal.
   - Ensure git is on a feature branch for the current V8 phase:
     - `git status`
     - `git checkout -b v8-phase-<N>-<short-description>` (if starting new work)
   - Confirm demo DB connection (Supabase Postgres) and `.env`:
     - `PHI_ENCRYPTION_KEY` is set (dev key).
     - Any feature flags for PHI workflow or CodingService.

2) Start Architect (GPT‑5.1 Pro)
   - Open a new chat.
   - Paste the **Architect priming script (Procedure Suite V8 / PHI Demo)**.
   - Provide project context:
     - Repo name: `<Procedure_suite>`
     - Main languages: Python (FastAPI, SQLAlchemy), TypeScript/React (frontend).
     - Short project description:
       - “PHI‑aware procedure coding assistant, implementing the V8 PHI vault + CodingService migration. All data is synthetic and stored in Supabase for demo; design is HIPAA‑ready.”
     - Link or paste relevant excerpts from `V8_MIGRATION_PLAN_UPDATED.md` for today’s phase.
   - Explicitly remind the Architect:
     - “This is **demo mode**: synthetic PHI only, but please design and enforce full HIPAA‑ready PHI paths.”

3) Start Implementer (Codex‑5.1 with Terminal)
   - Open Codex with terminal access to the same project directory.
   - Paste the **Codex priming script (Procedure Suite V8 / PHI Demo)**.
   - Confirm current directory and branch:
     - `pwd`
     - `git status`
   - Optionally run a quick test or lint command to verify environment:
     - e.g., `pytest -q` or a narrower `pytest tests/integration/api/test_phi_workflow.py -q`.

4) Define today’s task
   - In the Architect chat:
     - Describe the task in 3–5 sentences, anchored to a V8 phase, e.g.:
       - “Today: implement Phase 0.1 and 0.2 – PHI models, schemas, PHIService, and Presidio adapter with anatomical allow‑list.”
       - “Today: wire `/v1/phi/submit` to CodingService and add integration tests.”
       - “Today: add the frontend PHIReviewEditor component and demo page that exercises the full workflow with synthetic notes.”
     - Ask for:
       - A high‑level plan.
       - Risk areas (DB migrations, PHI boundaries, breaking APIs).
       - Files/modules likely to be involved.
   - Once you have the plan, move to Codex with the concrete instructions from Architect.

5) Execute the loop
   - Architect:
     - Produces the plan and concrete step list.
   - Codex:
     - Follows the instructions in the terminal.
     - Summarizes changes and outputs in small chunks.
   - Architect:
     - Reviews changes, suggests refinements, and checks PHI boundaries and demo‑mode constraints.
   - You (human):
     - Nudge priorities (e.g., “focus on integration tests first”).
     - Decide when changes are “good enough” for merging.

6) Closeout
   - Run the backend test suite (at least all PHI and CodingService integration tests).
   - Optionally run frontend tests or a manual smoke test of the PHI Review demo page.
   - In Codex:
     - `git status`
     - Summarize changes by file and what they did.
   - In Architect:
     - Ask for a brief summary of:
       - What changed in terms of PHI data flow and CodingService.
       - Any remaining TODOs for the current phase.
       - Future refactor ideas (e.g., swapping Supabase to a hardened PHI vault deployment).
