#!/usr/bin/env bash
set -euo pipefail

export PSUITE_KNOWLEDGE_FILE="data/knowledge/ip_coding_billing_v2_8.json"
# Enable LLM Advisor for dev server to verify reliability fixes
export CODER_USE_LLM_ADVISOR=true

# Use 'python -m uvicorn' to ensure we use the conda environment's Python
exec python -m uvicorn modules.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
