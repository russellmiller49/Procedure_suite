# Deploy Mirror Guide (Slim Railway Source Repo)

## Purpose
Keep `Procedure_suite` as the full source-of-truth monorepo while automatically publishing a lightweight runtime-only mirror repo for Railway deployments.

This avoids manually maintaining two repos and reduces deploy payload size by excluding non-runtime/training assets.

## Source of truth files

- Allowlist: `ops/deploy/mirror_paths.txt`
- Build helper: `ops/tools/build_deploy_mirror.sh`
- Sync workflow: `.github/workflows/deploy-mirror-sync.yml`

## What is included

The mirror allowlist includes runtime code and deployment dependencies:

- `app/`, `observability/`, `ml/`, `config/`, `configs/`, `ops/`
- `proc_schemas/`, `proc_nlp/`, `proc_kb/`, `schemas/`
- `ui/static` + `ui/__init__.py`
- `alembic/`, `alembic.ini`
- minimal runtime data files under `data/`
- `pyproject.toml`, `requirements.txt`, `runtime.txt`

## What is excluded by default

- heavyweight PHI model artifacts under `ui/static/phi_redactor/vendor/phi_distilbert_ner*`
- common local/cache artifacts (`__pycache__`, `.pyc`, `.DS_Store`, pytest/mypy/ruff caches)

Core OCR runtime vendor assets remain included by default:

- `ui/static/phi_redactor/vendor/tesseract`
- `ui/static/phi_redactor/vendor/pdfjs`

If you need to include the heavyweight PHI model vendor assets in a one-off run:

```bash
DEPLOY_MIRROR_INCLUDE_VENDOR=1 bash ops/tools/build_deploy_mirror.sh /tmp/proc-suite-deploy
```

## GitHub setup

Configure the source repo (`Procedure_suite`) with:

1. **Repository variable**: `DEPLOY_MIRROR_REPO` = `owner/repo-name` for the target deploy repo.
2. **Repository variable (optional)**: `DEPLOY_MIRROR_BRANCH` (defaults to `main`).
3. **Repository secret**: `DEPLOY_MIRROR_PUSH_TOKEN` (PAT or fine-grained token with `contents: write` to target repo).

Workflow behavior:

- Runs on pushes to `main`.
- Can be run manually with `workflow_dispatch`.
- Skips automatically when `DEPLOY_MIRROR_REPO` or `DEPLOY_MIRROR_PUSH_TOKEN` is unset.

## Local dry run

```bash
bash ops/tools/build_deploy_mirror.sh /tmp/proc-suite-deploy
du -sh /tmp/proc-suite-deploy
```

## Railway notes

Point Railway to the deploy mirror repo once it is syncing cleanly.

Keep the same commands documented in `docs/DEPLOY_RAILWAY.md`:

- Start: `bash ops/railway_start_gunicorn.sh`
- Build: `python ops/tools/bootstrap_phi_redactor_vendor_bundle.py && python ops/tools/verify_phi_redactor_vendor_assets.py`

Because heavyweight PHI model assets are excluded by default in the mirror payload, set:

- `PHI_REDACTOR_VENDOR_BUNDLE_S3_URI`

Without that env var, `verify_phi_redactor_vendor_assets.py` fails when PHI model files are absent.
