#!/usr/bin/env bash
# Local development server for Procedure Suite API
#
# This script mirrors railway_start.sh but with hot-reload enabled.
# Uses the same optimization settings for consistent behavior.
#
# Usage:
#   ./scripts/devserver.sh
#
# Environment variables (all optional, sensible defaults provided):
#   PORT - Port to listen on (default: 8000)
#   SKIP_WARMUP - Skip model warmup for faster startup (default: false)
#   ENABLE_UMLS_LINKER - Load UMLS linker (default: true, set false to save RAM)

set -euo pipefail

# Knowledge base
export PSUITE_KNOWLEDGE_FILE="${PSUITE_KNOWLEDGE_FILE:-data/knowledge/ip_coding_billing_v2_9.json}"

# Enable LLM Advisor for dev server to verify reliability fixes
export CODER_USE_LLM_ADVISOR="${CODER_USE_LLM_ADVISOR:-true}"

# Model backend (onnx for production parity, or pytorch for debugging)
export MODEL_BACKEND="${MODEL_BACKEND:-onnx}"

# Limit BLAS/OpenMP thread oversubscription (matches Railway settings)
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"

# Concurrency settings
export LIMIT_CONCURRENCY="${LIMIT_CONCURRENCY:-50}"
export LLM_CONCURRENCY="${LLM_CONCURRENCY:-2}"
export CPU_WORKERS="${CPU_WORKERS:-1}"

echo "[devserver] =============================================="
echo "[devserver] Starting Procedure Suite API (dev mode)"
echo "[devserver] =============================================="
echo "[devserver] PORT=${PORT:-8000}"
echo "[devserver] MODEL_BACKEND=${MODEL_BACKEND}"
echo "[devserver] PSUITE_KNOWLEDGE_FILE=${PSUITE_KNOWLEDGE_FILE}"
# NOTE:
# - The FastAPI app loads `.env` via python-dotenv (see `modules/api/fastapi_app.py`).
# - This script prints from the *shell* environment, so if ENABLE_UMLS_LINKER isn't exported,
#   it would misleadingly show the default ("true") even if `.env` sets it to "false".
# To reduce confusion, we also peek at `.env` for display purposes when the variable isn't set.
dotenv_enable_umls=""
if [[ -z "${ENABLE_UMLS_LINKER+x}" ]] && [[ -f ".env" ]]; then
  dotenv_enable_umls="$(
    awk -F= '
      /^[[:space:]]*ENABLE_UMLS_LINKER[[:space:]]*=/ {
        sub(/^[^=]*=/, "", $0)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
        gsub(/^"|"$/, "", $0)
        val=$0
      }
      END { if (val != "") print val }
    ' .env
  )"
fi
enable_umls_display="${ENABLE_UMLS_LINKER-${dotenv_enable_umls:-true}}"
echo "[devserver] ENABLE_UMLS_LINKER=${enable_umls_display}"
echo "[devserver] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[devserver] =============================================="

# Use 'python -m uvicorn' to ensure we use the conda environment's Python
# --reload enables hot-reload for development
exec python -m uvicorn modules.api.fastapi_app:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --limit-concurrency "${LIMIT_CONCURRENCY}" \
    --reload \
    --log-level info
