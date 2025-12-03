# Gemini API Setup Guide

## Overview

The Procedure Suite uses Google's Gemini API for LLM-based registry extraction. By default, tests run in **offline mode** using a stub LLM to avoid network calls and API costs. This guide explains how to switch to **online mode** to use the real Gemini API.

## How It Works

The system checks three conditions to decide whether to use online Gemini or a stub:

1. **`GEMINI_OFFLINE`** environment variable - if set to `"1"`, `"true"`, or `"yes"`, forces offline mode
2. **`REGISTRY_USE_STUB_LLM`** environment variable - if set to `"1"`, `"true"`, or `"yes"`, forces stub LLM
3. **`GEMINI_API_KEY`** environment variable - must be set for online mode to work

**Decision logic** (from `modules/registry/extractors/llm_detailed.py`):
```python
use_stub = os.getenv("REGISTRY_USE_STUB_LLM", "").lower() in ("1", "true", "yes")
use_stub = use_stub or os.getenv("GEMINI_OFFLINE", "").lower() in ("1", "true", "yes")

if use_stub or not os.getenv("GEMINI_API_KEY"):
    self.llm = DeterministicStubLLM()  # Offline stub
else:
    self.llm = GeminiLLM()  # Online Gemini API
```

## Default Test Configuration

Tests are configured to run offline by default in:
- `tests/conftest.py` - sets `GEMINI_OFFLINE=1` by default
- `tests/api/conftest.py` - sets `GEMINI_OFFLINE=1` by default

This ensures tests don't make real API calls unless explicitly enabled.

## Enabling Online Gemini

### Option 1: Set Environment Variables (Recommended for Testing)

To run tests with online Gemini, **unset or override** the offline flags:

```bash
# Method 1: Unset the offline flags
unset GEMINI_OFFLINE
unset REGISTRY_USE_STUB_LLM

# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Run tests
pytest -q
```

```bash
# Method 2: Explicitly set to "0" or "false" (overrides defaults)
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="your-api-key-here"

# Run tests
pytest -q
```

### Option 2: Use .env File

Create a `.env` file in the project root:

```bash
# .env file
GEMINI_API_KEY=your-api-key-here
GEMINI_OFFLINE=0
REGISTRY_USE_STUB_LLM=0
```

The `modules/common/llm.py` file automatically loads `.env` files using `python-dotenv`.

### Option 3: Inline with pytest (One-time)

```bash
GEMINI_OFFLINE=0 REGISTRY_USE_STUB_LLM=0 GEMINI_API_KEY="your-key" pytest -q
```

## Authentication Methods

### API Key (Default)

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get your API key from: https://aistudio.google.com/app/apikey

### OAuth2/Service Account (For Subscriptions)

If you have a Google Cloud subscription, you can use OAuth2:

```bash
# Option A: Application Default Credentials (local dev)
export GEMINI_USE_OAUTH=true
gcloud auth application-default login

# Option B: Service Account JSON
export GEMINI_USE_OAUTH=true
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Example: Running Tests with Online Gemini

```bash
# 1. Set your API key
export GEMINI_API_KEY="your-api-key-here"

# 2. Disable offline mode
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0

# 3. Run tests (DISABLE_STATIC_FILES is optional, keeps static file serving disabled)
DISABLE_STATIC_FILES=1 pytest -q

# Or run specific test file
DISABLE_STATIC_FILES=1 pytest tests/e2e/test_registry_e2e.py -v
```

## Example: Running Tests with Offline Mode (Default)

```bash
# These flags are set by default in conftest.py, but you can be explicit:
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest -q
```

## Verifying Configuration

You can verify which mode is active by checking the logs:

- **Offline mode**: You'll see `"Using DeterministicStubLLM"` in logs
- **Online mode**: You'll see `"Sending request to Gemini model: gemini-2.5-flash-lite"` in logs

## Model Selection

By default, the system uses `gemini-2.5-flash-lite`. To use a different model:

```bash
export GEMINI_MODEL="gemini-2.0-flash"  # or any other Gemini model
```

## Troubleshooting

### "No GEMINI_API_KEY found"
- Make sure `GEMINI_API_KEY` is set: `echo $GEMINI_API_KEY`
- Check that `.env` file is being loaded (if using one)

### Still using stub LLM
- Check that `GEMINI_OFFLINE` is not set to `"1"`, `"true"`, or `"yes"`
- Check that `REGISTRY_USE_STUB_LLM` is not set to `"1"`, `"true"`, or `"yes"`
- Verify API key is set: `python -c "import os; print(os.getenv('GEMINI_API_KEY'))"`

### OAuth2 errors
- Ensure `google-auth` is installed: `pip install google-auth`
- Verify credentials: `gcloud auth application-default print-access-token`

## Code References

- **LLM Configuration**: `modules/common/llm.py` - `GeminiLLM` class
- **Registry Extractor**: `modules/registry/extractors/llm_detailed.py` - `LLMDetailedExtractor` class
- **Test Configuration**: `tests/conftest.py`, `tests/api/conftest.py`


