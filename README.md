# Procedure Suite

The Procedure Suite provides structured report composition, autonomous coding, registry exports, and API endpoints that sit between the existing extractor and downstream analytics. It reuses the medparse-py311 environment and expects scispaCy + spaCy models to be available locally.

## Layout
- `proc_report`: templated synoptic report builder that consumes extractor hints or free text.
- `proc_autocode`: rule-driven coding pipeline with CPT maps, NCCI rules, and confidence scoring.
- `proc_registry`: adapters that turn reports/codes into Supabase-ready bundles.
- `proc_nlp`: UMLS linker and normalization helpers shared by the report engine + coder.
- `api`: FastAPI surface for compose/code/upsert flows.
- `tests`: seed unit + contract suites to keep CI green from day one.

## Getting Started
```bash
micromamba activate medparse-py311  # or conda activate medparse-py311
make install
make preflight
make test
```

Provide `.env` with Supabase credentials (see `.env.sample`).

## Gemini API Authentication

The reporter engine supports two authentication methods for the Gemini API:

### Option 1: API Key (Default)
Set the `GEMINI_API_KEY` environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Option 2: OAuth2/Service Account (Subscription)
For subscription-based authentication, set `GEMINI_USE_OAUTH=true` and configure Google Cloud credentials:

**Using Application Default Credentials (recommended for local development):**
```bash
export GEMINI_USE_OAUTH=true
gcloud auth application-default login
```

**Using a Service Account JSON file:**
```bash
export GEMINI_USE_OAUTH=true
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

**On Google Cloud Platform:**
The system will automatically use the service account attached to the compute instance if `GEMINI_USE_OAUTH=true` is set.

OAuth2 authentication uses the `Authorization: Bearer` header instead of API key query parameters, which is required for subscription-based access.
