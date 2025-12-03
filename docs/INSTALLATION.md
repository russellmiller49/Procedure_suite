# Installation & Setup Guide

This guide covers setting up the Procedure Suite environment, including Python dependencies, spaCy models, and Gemini API configuration.

## 1. Prerequisites

- **Python 3.11+** (Required: `>=3.11,<3.14`)
- **micromamba** or **conda** (Recommended for environment management)
- **Git**

## 2. Environment Setup

### Create Python Environment

Using `micromamba` (recommended) or `conda`:

```bash
# Create environment
micromamba create -n medparse-py311 python=3.11
micromamba activate medparse-py311
```

### Install Dependencies

Install the project in editable mode along with API and dev dependencies:

```bash
make install
# Or manually: pip install -e ".[api,dev]"
```

### Install spaCy Models

The project requires specific spaCy models for NLP tasks:

```bash
# Install scispaCy model (Required - may take a few minutes)
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Install standard spaCy model
python -m spacy download en_core_web_sm
```

## 3. Configuration (.env)

Create a `.env` file in the project root to store configuration and secrets:

```bash
touch .env
```

### Gemini API Configuration (Required for Extraction)

The system uses Google's Gemini models for registry extraction.

**Option 1: API Key (Simpler)**
Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).

```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite  # Optional: Override default model
```

**Option 2: OAuth2 / Service Account (For Cloud Subscriptions)**
If running on GCP or using a service account:

```bash
GEMINI_USE_OAUTH=true
# Optional: Path to service account JSON if not using default credentials
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Other Settings

```bash
# Enable LLM Advisor for Coder (Optional)
CODER_USE_LLM_ADVISOR=1

# Supabase Integration (Optional - for DB export)
# SUPABASE_DB_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

## 4. Verification

Run the preflight check to validate your setup:

```bash
make preflight
```

This script checks:
- ✅ Python version
- ✅ Installed dependencies (including `sklearn` version)
- ✅ spaCy models
- ✅ Configuration validity

## 5. Running Tests (Offline vs Online)

By default, tests run in **offline mode** using a stub LLM to avoid API costs and network dependency.

### Offline Mode (Default)
```bash
pytest -q
```

### Online Mode (Live API)
To test with the real Gemini API:

```bash
# Override default offline flags
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="your-key"

pytest -q
```

## 6. Starting the API Server

To run the FastAPI backend locally:

```bash
make api
# Or: ./scripts/devserver.sh
```

The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`
