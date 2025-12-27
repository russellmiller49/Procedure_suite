# Deploy Architecture (QA Sandbox + IU)

This document maps the deployed QA sandbox stack used by `https://interventionalpulm.com/qa-sandbox` / `qa-admin`.

## Repos in this workspace

### IU / FastAPI backend (Python)

- **Repo:** `proc_suite/`
- **Active FastAPI app (IU):** `proc_suite/modules/api/fastapi_app.py` (`app = FastAPI(...)`)
- **Railway start wrapper:** `proc_suite/scripts/railway_start.sh`
- **Key endpoint:** `POST /qa/run` (defined in `proc_suite/modules/api/fastapi_app.py`)

### Frontend + Supabase logging (Next.js)

- **Repo:** `IP_website/`
- **Pages:**
  - QA sandbox UI: `IP_website/src/app/qa-sandbox/page.tsx`
  - QA admin UI: `IP_website/src/app/qa-admin/page.tsx` + `IP_website/src/app/qa-admin/session-list.tsx`
- **Server-side API routes (call backend + log to Supabase):**
  - Run + log: `IP_website/src/app/api/qa/run/route.ts`
  - Feedback: `IP_website/src/app/api/qa/feedback/route.ts`
  - Sessions list: `IP_website/src/app/api/qa/sessions/route.ts`
  - Delete: `IP_website/src/app/api/qa/delete/route.ts`
- **Supabase admin client (service role; server-only):** `IP_website/src/lib/supabase/admin.ts`

## Call flow (who calls what)

1. Browser hits `IP_website` UI routes:
   - `GET /qa-sandbox` → `IP_website/src/app/qa-sandbox/page.tsx`
   - `GET /qa-admin` → `IP_website/src/app/qa-admin/*`
2. UI calls Next.js API route:
   - `POST /api/qa/run` → `IP_website/src/app/api/qa/run/route.ts`
3. Next.js calls the Python IU:
   - `POST ${PROC_API_URL}/qa/run`
4. Next.js writes results to Supabase:
   - table: `proc_qa_sessions` (see schema references in `Proc_suite_website_integration/supabase_schema.sql`)

## Model loading (where it lives in code)

This workspace has multiple “predictor” implementations for registry ML:

- **ONNX predictor (production-optimized):** `proc_suite/modules/registry/inference_onnx.py`
  - Default ONNX path: `models/registry_model_int8.onnx`
- **Sklearn TF-IDF fallback predictor:** `proc_suite/modules/ml_coder/registry_predictor.py`
  - Default artifacts: `data/models/registry_classifier.pkl`, `data/models/registry_mlb.pkl`, `data/models/registry_thresholds.json`

The application-layer wiring that chooses which predictor to use currently lives in:
- `proc_suite/modules/registry/application/registry_service.py` (`RegistryService._get_registry_ml_predictor`)

## Key env vars

### Frontend (Railway service for `IP_website/`)

- `PROC_API_URL` (base URL of the Python IU, e.g. `https://procedure-suite-xxx.up.railway.app`)
- `SUPABASE_URL` (server-side)
- `SUPABASE_SERVICE_ROLE_KEY` (server-side only)
- `NEXT_PUBLIC_SUPABASE_URL` (client)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (client)

### Backend / IU (Railway service for `proc_suite/`)

- `PORT` (provided by Railway)
- `WORKERS` (optional; uvicorn workers)
- `DEMO_MODE` (enables QA sandbox mode in some flows)
- `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_USE_OAUTH` (LLM reporter/coder as configured)
- `CODER_VERSION`, `REPORTER_VERSION` (returned in `/qa/run` metadata)
- `DISABLE_STATIC_FILES` (controls mounting `/ui` in `fastapi_app.py`)

Model bundle env vars (used by model bootstrap wiring):
- `MODEL_BACKEND` (`pytorch`, `onnx`, or `auto`)
- `MODEL_BUNDLE_S3_URI_PYTORCH` (e.g. `s3://procedure-suite-models/deploy/registry/<version>/pytorch/bundle.tar.gz`)
- `MODEL_BUNDLE_S3_URI_ONNX` (e.g. `s3://procedure-suite-models/deploy/registry/<version>/onnx/bundle.tar.gz`)

## Model artifacts on disk (expected layout)

Runtime-extracted bundle directory (recommended):
- `proc_suite/data/models/registry_runtime/`
  - `manifest.json`
  - `thresholds.json`
  - `label_order.json`
  - `registry_label_fields.json`
  - `tokenizer/` (HuggingFace tokenizer files)
  - PyTorch: `config.json` + `model.safetensors` (and/or `pytorch_model.bin`)
  - ONNX: `registry_model_int8.onnx` (when using ONNX)

## Railway start command (IU)

Railway should run one of:

- **Preferred (wrapper):** `scripts/railway_start.sh`
- **Equivalent direct:** `python -m uvicorn modules.api.fastapi_app:app --host 0.0.0.0 --port $PORT --workers ${WORKERS:-1} --log-level info`

