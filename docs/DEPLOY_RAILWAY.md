# Railway Deployment (Procedure Suite IU)

## Service roles

This project is typically deployed as **two Railway services**:

1. **Backend / IU (FastAPI)** from `proc_suite/`
2. **Frontend (Next.js)** from `IP_website/` (separate repo/service)

## Backend (proc_suite)

### Start command

- `scripts/railway_start.sh`

### Required env vars (production)

- `MODEL_BACKEND=onnx`
- `MODEL_BUNDLE_S3_URI_ONNX=s3://procedure-suite-models/deploy/registry/<version>/onnx/bundle.tar.gz`
- AWS credentials + region (via Railway env vars):
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`

Common:
- `PORT` (Railway provides)
- `WORKERS` (optional)
- `CODER_VERSION` (optional; returned in `/qa/run`)
- `REPORTER_VERSION` (optional; returned in `/qa/run`)

### Local dev (recommended)

- `MODEL_BACKEND=pytorch`
- `MODEL_BUNDLE_S3_URI_PYTORCH=s3://procedure-suite-models/deploy/registry/<version>/pytorch/bundle.tar.gz`

## Frontend (IP_website)

- `PROC_API_URL=https://<your-backend>.up.railway.app`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

