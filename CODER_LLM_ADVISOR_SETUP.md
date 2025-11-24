# Coder LLM Advisor Setup

## Problem
The `EnhancedCPTCoder` was not calling the Gemini API because it didn't have LLM advisor functionality integrated.

## Solution
Added optional LLM advisor support to `EnhancedCPTCoder` that uses Gemini API to suggest codes and compare with knowledge base results.

## How to Enable

### Option 1: Environment Variable (Recommended)
```bash
export CODER_USE_LLM_ADVISOR=1
# Then start the server
make api
```

### Option 2: Set in .env file
```bash
echo "CODER_USE_LLM_ADVISOR=1" >> .env
```

### Option 3: Programmatically
```python
from proc_autocode.coder import EnhancedCPTCoder
coder = EnhancedCPTCoder(use_llm_advisor=True)
```

## How It Works

1. **Knowledge Base Detection**: `EnhancedCPTCoder` uses IP knowledge base to detect codes from note text
2. **LLM Suggestions** (if enabled): Gemini API suggests codes based on the note
3. **Comparison**: System compares knowledge base codes vs LLM suggestions
4. **Disagreements**: Any differences are reported in `llm_disagreements` field

## API Response

When LLM advisor is enabled, the `/v1/coder/run` endpoint returns:
- `llm_suggestions`: Array of codes suggested by Gemini
- `llm_disagreements`: Array of strings describing differences between KB and LLM

## Requirements

- `GEMINI_API_KEY` must be set in environment
- Or `GEMINI_USE_OAUTH=true` for OAuth2 authentication
- See `modules/common/llm.py` for authentication options

## Verification

Check if LLM advisor is active:
```bash
# Check environment
echo $CODER_USE_LLM_ADVISOR

# Test API call
curl -X POST http://localhost:8000/v1/coder/run \
  -H "Content-Type: application/json" \
  -d '{"note": "Bronchoscopy with EBUS-TBNA..."}' | jq '.llm_suggestions'
```

If `llm_suggestions` is populated, the LLM advisor is working.

