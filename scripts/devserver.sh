#!/usr/bin/env bash
set -euo pipefail

export PSUITE_KNOWLEDGE_FILE="data/knowledge/ip_coding_billing.v2_2.json"

exec uvicorn modules.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
