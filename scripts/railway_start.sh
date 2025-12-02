#!/usr/bin/env bash
# Railway startup script for Procedure Suite API
#
# This script:
# 1. Warms up heavy NLP models before starting the server
# 2. Starts the FastAPI application with uvicorn
#
# Usage:
#   scripts/railway_start.sh
#
# Environment variables:
#   PORT - Port to listen on (default: 8000)
#   PROCSUITE_SPACY_MODEL - spaCy model to use (default: en_core_sci_sm)
#   WORKERS - Number of uvicorn workers (default: 1)
#
# Railway Configuration:
#   Set "Start Command" to: scripts/railway_start.sh

set -euo pipefail

# Ensure Python can find the local packages (modules, proc_*, etc.)
# Railway runs from /app with a virtual environment, but PYTHONPATH may not include /app
export PYTHONPATH="${PYTHONPATH:-}:${PWD}"
echo "[railway_start] PYTHONPATH=${PYTHONPATH}"

echo "[railway_start] =============================================="
echo "[railway_start] Starting Procedure Suite API"
echo "[railway_start] =============================================="
echo "[railway_start] PORT=${PORT:-8000}"
echo "[railway_start] PROCSUITE_SPACY_MODEL=${PROCSUITE_SPACY_MODEL:-en_core_sci_sm}"
echo "[railway_start] WORKERS=${WORKERS:-1}"
echo "[railway_start] =============================================="

# Step 1: Warm up NLP models
echo "[railway_start] Warming up NLP models..."
if ! python scripts/warm_models.py; then
    echo "[railway_start] WARNING: Model warmup had errors, but continuing..."
    # Don't exit on warmup errors - the app might still work
fi

echo "[railway_start] =============================================="
echo "[railway_start] Starting FastAPI (uvicorn)..."
echo "[railway_start] =============================================="

# Step 2: Start uvicorn
# Using exec to replace the shell process with uvicorn
# This ensures proper signal handling for graceful shutdown
# Use 'python -m uvicorn' to ensure we use the conda environment's Python
exec python -m uvicorn modules.api.fastapi_app:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WORKERS:-1}" \
    --log-level info
