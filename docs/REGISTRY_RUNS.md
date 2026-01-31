# Registry Runs (Persistence + Feedback Backend)

Registry Runs provides a persistence layer around the existing stateless extraction-first engine:

- **Stateless engine**: `POST /api/v1/process` (Text In → Codes Out)
- **Persistent wrapper**: `POST /api/v1/registry/runs` (Text In → Codes Out **+ store run**)

Non-negotiable: the server must persist **scrubbed-only** note text. Never store raw PHI.

## Enable/Disable

Registry Runs endpoints are hard-gated by environment:

- `REGISTRY_RUNS_PERSIST_ENABLED` (default: false)
  - When false, Registry Runs endpoints return `503`.

## Database

The registry store uses SQLAlchemy and the main Alembic target DB.

DB URL resolution:

1) `REGISTRY_STORE_DATABASE_URL` (optional override)
2) `DATABASE_URL`
3) `PHI_DATABASE_URL`
4) `sqlite:///./phi_demo.db` (repo default)

### Migration

Apply migrations (creates `registry_runs` table):

```bash
alembic upgrade head
```

## PHI Persistence Safety Gate

Before writing any run, the server performs a lightweight PHI risk scan on the **scrubbed** note text.

Default behavior:

- If high-risk patterns are detected → **reject persistence** with HTTP `400`

Override:

- `REGISTRY_RUNS_ALLOW_PHI_RISK_PERSIST=true`
  - Allows saving but forces:
    - `needs_manual_review=true`
    - `review_status="phi_risk"`

UI reference: see `/ui/phi_identifiers` and `docs/PHI_IDENTIFIERS.md`.

## API Endpoints

All endpoints live under `/api/v1/registry/*`.

### Create + Persist Run

`POST /api/v1/registry/runs`

- Input: same fields as `/api/v1/process` plus `submitter_name` (optional)
- Output:
  - `run_id`
  - `result` (same schema as `/api/v1/process`)

### Submit Feedback (One-Time)

`POST /api/v1/registry/runs/{run_id}/feedback`

- Enforced: **exactly one** feedback submission per run
- Second submit returns `409`

### Save Corrections (Upsert)

`PUT /api/v1/registry/runs/{run_id}/correction`

- Stores the UI’s “Edited JSON (Training)” payload and an edited tables snapshot
- Can be overwritten while iterating

### List / Get / Export

- `GET /api/v1/registry/runs` (admin-lite list; filters and paging)
- `GET /api/v1/registry/runs/{run_id}` (full row)
- `GET /api/v1/registry/export` (JSONL export; scrubbed-only note text)

## UI (PHI Redactor) Integration

UI lives at `/ui/` (static files in `modules/api/static/phi_redactor/`).

Behavior:

- On submit, the UI attempts to create a Registry Run.
  - If persistence is disabled/unavailable, it falls back to stateless `/api/v1/process`.
- A “Confirm PHI removal” dialog is shown before attempting persistence.
- Feedback panel:
  - Submit feedback (one-time)
  - Save corrections (upsert)

Tester mode:

- Add `?tester=1` to auto-expand the feedback panel.
- In tester mode, persistence is attempted only after a name is provided.

