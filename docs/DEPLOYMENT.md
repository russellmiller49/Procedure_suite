# Deployment & Operations Guide

This guide covers deploying Procedure Suite in production with:
- Supabase for persistent storage (optional, recommended for production)
- Prometheus metrics for observability
- CI integration for testing

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Production Deployment                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   FastAPI    │────▶│   Supabase   │     │  Prometheus  │    │
│  │   Backend    │     │  (Postgres)  │     │   Scraper    │    │
│  │  :8000       │     │              │     │              │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                                         │              │
│         │  GET /metrics                          │              │
│         └────────────────────────────────────────┘              │
│                                                                  │
│  ┌──────────────┐                                               │
│  │   Grafana    │◀── Queries Prometheus for dashboards          │
│  │              │                                                │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (not anon key!) | `eyJhbGc...` |
| `PROCEDURE_STORE_BACKEND` | Storage backend | `supabase` |
| `METRICS_BACKEND` | Metrics collection mode | `prometheus` |
| `PSUITE_KNOWLEDGE_FILE` | Path to knowledge base JSON | `data/knowledge/ip_coding_billing_v3_0.json` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `METRICS_ENABLED` | Enable /metrics endpoint | `true` if METRICS_BACKEND=prometheus |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `LOG_FORMAT` | Log format (json/text) | `json` |

### Development Defaults

For local development without Supabase:
```bash
# Uses InMemoryProcedureStore (no persistence)
export PROCEDURE_STORE_BACKEND=memory
export METRICS_BACKEND=stdout  # Logs metrics to stderr as JSON
```

---

## Supabase Setup

### 1. Apply Database Migrations

The migration file is located at:
```
/home/rjm/projects/Proc_suite_website_integration/supabase/migrations/20241203000000_add_procedure_suite_tables.sql
```

**Option A: Supabase CLI (Recommended)**
```bash
cd /home/rjm/projects/Proc_suite_website_integration
supabase db push
```

**Option B: Direct SQL**
1. Go to Supabase Dashboard → SQL Editor
2. Paste and run the migration SQL

### 2. Tables Created

| Table | Purpose |
|-------|---------|
| `procedure_code_suggestions` | AI-generated code suggestions pending review |
| `procedure_coding_results` | Metadata for coding runs (latency, versions, etc.) |
| `procedure_code_reviews` | Clinician review actions (accept/reject/modify) |
| `procedure_final_codes` | Approved codes ready for billing |
| `procedure_registry_exports` | IP Registry export records |

### 3. Row-Level Security (RLS)

The migration enables RLS with policies for:
- **SELECT**: Authenticated users can read all rows
- **INSERT/UPDATE/DELETE**: Service role required

For production, customize RLS to restrict access by organization or user.

### 4. Verify Setup

```bash
# Run smoke tests to verify connectivity
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export RUN_SUPABASE_TESTS=1

pytest tests/integration/persistence/test_supabase_procedure_store.py -v
```

---

## Metrics & Monitoring

### Enable Prometheus Metrics

```bash
export METRICS_BACKEND=prometheus
```

This enables:
- In-process metrics registry (thread-safe)
- `GET /metrics` endpoint in Prometheus text format
- `GET /metrics/json` for debugging
- `GET /metrics/status` for health checks

### Prometheus Scrape Config

Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'proc_suite'
    scrape_interval: 15s
    static_configs:
      - targets: ['your-api-host:8000']
    metrics_path: /metrics
```

### Available Metrics

#### Counters
| Metric | Labels | Description |
|--------|--------|-------------|
| `proc_suite_coder_suggestions_total` | `procedure_type`, `used_llm` | Total code suggestions generated |
| `proc_suite_coder_reviews_total` | `procedure_type`, `source` | Total review actions |
| `proc_suite_coder_reviews_accepted_total` | `procedure_type`, `source` | Accepted suggestions |
| `proc_suite_coder_reviews_rejected_total` | `procedure_type`, `source` | Rejected suggestions |
| `proc_suite_coder_reviews_modified_total` | `procedure_type`, `source` | Modified suggestions |
| `proc_suite_coder_final_codes_total` | `source`, `procedure_type` | Final codes added |
| `proc_suite_coder_manual_codes_total` | `procedure_type` | Manually added codes |
| `proc_suite_coder_registry_exports_total` | `version`, `status` | Registry exports |
| `proc_suite_coder_registry_exports_success_total` | `version`, `status` | Successful exports |

#### Histograms (Latency)
| Metric | Labels | Description |
|--------|--------|-------------|
| `proc_suite_coder_pipeline_latency_ms` | `procedure_type`, `used_llm` | Full pipeline latency (ms) |
| `proc_suite_coder_llm_latency_ms` | `procedure_type` | LLM advisor latency (ms) |
| `proc_suite_coder_rule_engine_latency_ms` | (none) | Rule engine latency (ms) |
| `proc_suite_coder_registry_export_latency_ms` | `version` | Registry export latency (ms) |

#### Gauges
| Metric | Labels | Description |
|--------|--------|-------------|
| `proc_suite_coder_acceptance_rate` | `procedure_type` | Current acceptance rate (0-1) |
| `proc_suite_coder_registry_completeness_score` | `version` | Registry entry completeness (0-1) |

### Bucket Configuration

Histogram buckets for timing metrics (in ms):
```
10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000
```

---

## Running the Application

### Development
```bash
# Install with dev dependencies
pip install -e ".[api,dev]"

# Run with InMemory store (no persistence)
PROCEDURE_STORE_BACKEND=memory uvicorn app.api.fastapi_app:app --reload
```

### Production
```bash
# Set all required environment variables first
export SUPABASE_URL="..."
export SUPABASE_SERVICE_ROLE_KEY="..."
export PROCEDURE_STORE_BACKEND=supabase
export METRICS_BACKEND=prometheus
export PSUITE_KNOWLEDGE_FILE="data/knowledge/ip_coding_billing_v3_0.json"

# Run with gunicorn
gunicorn app.api.fastapi_app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Docker (Example)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install ".[api]"

ENV PROCEDURE_STORE_BACKEND=supabase
ENV METRICS_BACKEND=prometheus

CMD ["gunicorn", "app.api.fastapi_app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

---

## CI/CD Integration

### Standard CI (No Supabase)

The default CI runs all tests except Supabase smoke tests:
```yaml
- name: Pytest
  run: pytest -q
```

Supabase tests are automatically skipped unless `RUN_SUPABASE_TESTS=1`.

### CI with Supabase (Optional)

To run Supabase smoke tests in CI:

1. Add secrets to your GitHub repo:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`

2. Add a separate job or step:
```yaml
- name: Supabase Integration Tests
  if: ${{ secrets.SUPABASE_URL != '' }}
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
    RUN_SUPABASE_TESTS: "1"
  run: pytest tests/integration/persistence/test_supabase_procedure_store.py -v
```

### Running Tests Locally

```bash
# All tests (Supabase skipped)
pytest -q

# Specific test suites
pytest tests/unit/ -v
pytest tests/integration/api/ -v

# Include Supabase tests (requires credentials)
RUN_SUPABASE_TESTS=1 pytest tests/integration/persistence/ -v
```

---

## Troubleshooting

### Metrics endpoint returns 404
- Check `METRICS_BACKEND` is set to `prometheus` or `registry`
- Verify with `curl http://localhost:8000/metrics/status`

### Supabase connection fails
- Verify `SUPABASE_URL` includes `https://`
- Use service role key (not anon key) for write operations
- Check RLS policies allow your operations

### Tests fail with PersistenceError
- Ensure `PROCEDURE_STORE_BACKEND=memory` for unit tests
- Check Supabase credentials for integration tests

### High LLM latency
- Check `proc_suite_coder_llm_latency_ms` histogram in Prometheus
- Consider reducing LLM calls with `use_llm=false` for simpler cases

---

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Basic liveness check |
| `GET /metrics/status` | Metrics system status |
| `GET /metrics` | Full Prometheus metrics |

Example health check for container orchestration:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```
