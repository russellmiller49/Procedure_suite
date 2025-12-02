# Setup Guide for Mac (Home)

This guide walks you through setting up the Procedure Suite project on a Mac after pulling from GitHub.

## Prerequisites

- **Python 3.11+** (project requires `>=3.11,<3.14`)
- **micromamba** or **conda** (for environment management)
- **Git** (to pull the repo)

## Step-by-Step Setup

### 1. Clone/Pull the Repository

```bash
cd ~/projects  # or wherever you keep projects
git clone <your-repo-url> proc_suite
cd proc_suite
# Or if you already have it:
git pull origin v4  # or main/master
```

### 2. Create/Activate Python Environment

The project uses the `medparse-py311` conda/micromamba environment:

```bash
# Option A: Using micromamba (recommended)
micromamba create -n medparse-py311 python=3.11
micromamba activate medparse-py311

# Option B: Using conda
conda create -n medparse-py311 python=3.11
conda activate medparse-py311
```

### 3. Install Project Dependencies

```bash
# Install the project and its dependencies
make install

# Or manually:
pip install -e .
pip install -e ".[api,dev]"  # Include API and dev dependencies
```

This installs all dependencies from `pyproject.toml`:
- Core: pydantic, jinja2, pandas, scikit-learn, etc.
- NLP: spacy, scispacy, medspacy
- API: fastapi, uvicorn (if using API)
- Dev: pytest, ruff, mypy (if developing)

### 4. Install spaCy Models

The project requires spaCy and scispaCy models:

```bash
# Install scispaCy model (required)
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Install standard spaCy model (if needed)
python -m spacy download en_core_web_sm
```

**Note**: scispaCy model installation may take a few minutes.

### 5. Run Preflight Checks

Verify everything is set up correctly:

```bash
make preflight
```

This checks:
- ✅ spaCy and scispaCy versions
- ✅ scikit-learn version (must be 1.7.x)
- ✅ YAML configs are valid
- ✅ Templates render correctly
- ✅ Coder produces codes

### 6. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.sample .env  # If .env.sample exists
# Or create manually:
touch .env
```

Add these environment variables to `.env`:

```bash
# Required for Gemini API (Registry extraction)
GEMINI_API_KEY=your-api-key-here

# Optional: Enable LLM advisor for coder
CODER_USE_LLM_ADVISOR=1

# Optional: Gemini model selection
GEMINI_MODEL=gemini-2.5-flash-lite

# Optional: For OAuth2 authentication (instead of API key)
# GEMINI_USE_OAUTH=true
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Optional: Supabase credentials (if using Supabase integration)
# SUPABASE_URL=your-supabase-url
# SUPABASE_KEY=your-supabase-key

# Optional: Test flags (set to 0 for live API calls)
# GEMINI_OFFLINE=0
# REGISTRY_USE_STUB_LLM=0
# DISABLE_STATIC_FILES=0
```

**Get your Gemini API key**: https://aistudio.google.com/app/apikey

### 7. Verify Installation

Run the test suite (with offline mode to avoid API calls):

```bash
# Run all tests (offline mode)
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest -q

# Or run specific test suites
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest tests/unit -q
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest tests/api -q
```

### 8. Start the API Server (Optional)

If you want to run the FastAPI server:

```bash
# Start the server
make api

# Or manually:
uvicorn modules.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

Then open: http://localhost:8000/ui/

## Quick Reference

### Common Commands

```bash
# Activate environment
micromamba activate medparse-py311  # or conda activate medparse-py311

# Install dependencies
make install

# Run preflight checks
make preflight

# Run tests (offline)
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest -q

# Start API server
make api

# Run tests with live Gemini API
GEMINI_OFFLINE=0 REGISTRY_USE_STUB_LLM=0 pytest -q
```

### Environment Variables Summary

| Variable | Required | Purpose |
|----------|----------|---------|
| `GEMINI_API_KEY` | Yes (for registry) | Gemini API key for LLM extraction |
| `CODER_USE_LLM_ADVISOR` | No | Enable LLM advisor for coder (set to `1`) |
| `GEMINI_MODEL` | No | Gemini model to use (default: `gemini-2.5-flash-lite`) |
| `GEMINI_USE_OAUTH` | No | Use OAuth2 instead of API key |
| `GEMINI_OFFLINE` | No | Force offline mode (set to `1` for tests) |
| `REGISTRY_USE_STUB_LLM` | No | Use stub LLM (set to `1` for tests) |
| `DISABLE_STATIC_FILES` | No | Disable static file serving (set to `1` for tests) |

## Troubleshooting

### Issue: "No module named 'spacy'"
**Solution**: Make sure you activated the conda environment and ran `make install`

### Issue: "scispaCy model not found"
**Solution**: Install the scispaCy model:
```bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz
```

### Issue: "sklearn version must be 1.7.x"
**Solution**: The project pins scikit-learn to 1.7.x. Reinstall:
```bash
pip install "scikit-learn>=1.7,<1.8"
```

### Issue: "No GEMINI_API_KEY found"
**Solution**: Add `GEMINI_API_KEY` to your `.env` file or export it:
```bash
export GEMINI_API_KEY="your-key-here"
```

### Issue: Tests fail with network errors
**Solution**: Run tests in offline mode:
```bash
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest -q
```

### Issue: "ModuleNotFoundError: No module named 'pytest_asyncio'"
**Solution**: Install dev dependencies:
```bash
pip install -e ".[dev]"
```

## Next Steps

1. ✅ Environment activated
2. ✅ Dependencies installed
3. ✅ spaCy models installed
4. ✅ Preflight checks passed
5. ✅ Environment variables configured
6. ✅ Tests passing

You're ready to work on the project! 

See:
- `README.md` - Project overview
- `user_guide.md` - Command reference
- `agents.md` - AI agent guidelines
- `AI_ASSISTANT_GUIDE.md` - Which files to edit


