# Procedure Suite — Documentation Home

This repo already contains a lot of “deep dive” documents. This page is the **single entrypoint** and **reading order** so you can understand how the system works from documentation alone.

If you’re new here, start with:

1. **Repo Guide (end-to-end):** [`docs/REPO_GUIDE.md`](REPO_GUIDE.md)
2. **Quick repo map:** [`docs/REPO_INDEX.md`](REPO_INDEX.md)
3. **How to run + contribute:** [`docs/DEVELOPMENT.md`](DEVELOPMENT.md)
4. **How to use it (scripts/UI/API):** [`docs/USER_GUIDE.md`](USER_GUIDE.md)
5. **Architecture overview:** [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)

## What this system is (one sentence)

Procedure Suite is a **stateless clinical logic engine**: **(scrubbed) procedure note text in → registry fields + derived CPT codes out** (authoritative API: `POST /api/v1/process`).

## Quick start (local)

- Install: follow [`docs/INSTALLATION.md`](INSTALLATION.md)
- Run: `./scripts/devserver.sh`
- Open:
  - UI: `http://localhost:8000/ui/`
  - API docs: `http://localhost:8000/docs`

## Documentation map

### Start here (recommended order)

- [`docs/REPO_GUIDE.md`](REPO_GUIDE.md) — “How it works” from UI → API → pipelines → outputs.
- [`docs/REPO_INDEX.md`](REPO_INDEX.md) — high-signal repo map: entrypoints, directories, “edit here to change X”.
- [`README.md`](../README.md) — high-level summary + links.
- [`AGENTS.md`](../AGENTS.md) and [`CLAUDE.md`](../CLAUDE.md) — concise operational constraints for agents/automation.

### Development & contribution

- [`docs/INSTALLATION.md`](INSTALLATION.md) — environment setup, model downloads, LLM provider configuration.
- [`docs/DEVELOPMENT.md`](DEVELOPMENT.md) — source-of-truth dev rules, module ownership, test practices.
- [`docs/MAKEFILE_COMMANDS.md`](MAKEFILE_COMMANDS.md) — canonical `make` target reference.
- [`docs/Production_Readiness_Review.md`](Production_Readiness_Review.md) — operational readiness checklist (historical, still useful).

### Architecture, data flow, and design decisions

- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — module breakdown + data flows.
- [`docs/DEPLOY_ARCH.md`](DEPLOY_ARCH.md) — production deploy architecture notes.
- [`docs/DEPLOYMENT.md`](DEPLOYMENT.md) — operations guide (metrics, Supabase, CI).
- [`docs/ml_first_hybrid_policy.md`](ml_first_hybrid_policy.md) — background on the older ML-first hybrid policy (kept for context).

### API and UI

- [`docs/Registry_API.md`](Registry_API.md) — legacy registry endpoints + mode descriptions.
- [`docs/phi_review_system/README.md`](phi_review_system/README.md) — PHI review workflow and storage.
- UI static app lives in `modules/api/static/phi_redactor/` and is served at `/ui/`.

### Registry schema & extraction

- [`docs/REGISTRY_V3_IMPLEMENTATION_GUIDE.md`](REGISTRY_V3_IMPLEMENTATION_GUIDE.md) — V3 schema/extraction implementation notes.
- [`NOTES_SCHEMA_REFACTOR.md`](../NOTES_SCHEMA_REFACTOR.md) — 2026-01 schema refactor notes.
- [`docs/GRANULAR_NER_UPDATE_WORKFLOW.md`](GRANULAR_NER_UPDATE_WORKFLOW.md) — how to update/train granular NER.
- [`docs/REGISTRY_PRODIGY_WORKFLOW.md`](REGISTRY_PRODIGY_WORKFLOW.md) — “Diamond Loop” human-in-the-loop process.
- [`docs/Registry_ML_summary.md`](Registry_ML_summary.md) — ML model summary/background.

### Knowledge base (billing + terminology)

- [`docs/KNOWLEDGE_INVENTORY.md`](KNOWLEDGE_INVENTORY.md) — what is source-of-truth and where it lives.
- [`docs/KNOWLEDGE_RELEASE_CHECKLIST.md`](KNOWLEDGE_RELEASE_CHECKLIST.md) — safe KB/schema release steps.
- [`docs/REFERENCES.md`](REFERENCES.md) — supported CPT reference list.

### Reporting

- [`docs/STRUCTURED_REPORTER.md`](STRUCTURED_REPORTER.md) — structured reporter overview.
- [`docs/REPORTER_STYLE_GUIDE.md`](REPORTER_STYLE_GUIDE.md) — style guide for generated reports.
- [`modules/reporting/EXTRACTION_RULES.md`](../modules/reporting/EXTRACTION_RULES.md) — reporter extraction/derivation rules (implementation-adjacent).

### Observability

- [`docs/GRAFANA_DASHBOARDS.md`](GRAFANA_DASHBOARDS.md) — dashboards and metric guidance.

## Where to look in code (entrypoints)

- FastAPI app wiring + startup env validation: `modules/api/fastapi_app.py`
- Unified production endpoint: `modules/api/routes/unified_process.py`
- Extraction-first orchestration: `modules/registry/application/registry_service.py`
- Deterministic registry → CPT derivation (no note parsing): `modules/coder/domain_rules/registry_to_cpt/coding_rules.py`
- UI static assets: `modules/api/static/phi_redactor/`

---

Last updated: 2026-01-30

