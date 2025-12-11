# Hybrid ML Advisor Integration Plan for Procedure_suite

**Version:** 2.0  
**Date:** November 29, 2025  
**Target Branch:** v4 (or create new feature branch `feature/ml-advisor`)  
**Repository:** https://github.com/russellmiller49/Procedure_suite

---

## Executive Summary

This plan integrates a pluggable ML/LLM advisor into the existing rule-based `proc_autocode` pipeline. The advisor will suggest codes and provide confidence scores while the deterministic rule engine remains the final authority. Key improvements over the original plan include:

- **Better alignment with existing repo structure** (uses `modules/` directory pattern)
- **Integration with existing Gemini infrastructure** (reuses `geminiquota.py` and OAuth patterns)
- **Compatibility with `ip_golden_knowledge_v2_2.json`** (your validated NCCI/coding rules)
- **Clearer separation of concerns** (advisor suggests, rules decide)
- **Incremental deployment strategy** (feature flags at each stage)

---

## Table of Contents

1. [Phase 0: Repository Reconnaissance](#phase-0-repository-reconnaissance)
2. [Phase 1: Coding Trace Logger](#phase-1-coding-trace-logger)
3. [Phase 2: ML Advisor Module](#phase-2-ml-advisor-module)
4. [Phase 3: Hybrid Integration](#phase-3-hybrid-integration)
5. [Phase 4: Evaluation Harness](#phase-4-evaluation-harness)
6. [Phase 5: Safety, Audits & Documentation](#phase-5-safety-audits--documentation)
7. [Acceptance Checklist](#acceptance-checklist)
8. [Risk Mitigation](#risk-mitigation)

---

## Phase 0: Repository Reconnaissance

### Objective
Map the existing autocode pipeline and API entry points to ensure safe integration.

### Prerequisites
- Read `AI_ASSISTANT_GUIDE.md` first (source of truth for file locations)
- Confirm current branch is `v4` or appropriate feature branch

### Discovery Tasks

#### 0.1 Locate the FastAPI Entry Point
```bash
# The canonical entry point (NOT api/app.py which is deprecated)
cat modules/api/fastapi_app.py

# Search for proc_autocode imports
grep -r "from proc_autocode" modules/api/
grep -r "import proc_autocode" modules/api/
```

**Expected findings:**
- Main FastAPI app in `modules/api/fastapi_app.py`
- Import pattern like `from proc_autocode import <function>` or similar

#### 0.2 Identify the Coding Entry Point
```bash
# Find the main coding function(s)
grep -rn "def.*code" proc_autocode/
grep -rn "def.*autocode" proc_autocode/
grep -rn "def process" proc_autocode/

# Check __init__.py for exported functions
cat proc_autocode/__init__.py
```

**Document:**
- Function name that takes structured report → returns CPT codes
- Input parameter types (Pydantic model? dict? dataclass?)
- Return type structure (codes, confidence, rationales)

#### 0.3 Map the Data Models
```bash
# Find Pydantic/dataclass models for reports and codes
grep -rn "class.*Report" proc_autocode/ proc_report/ modules/
grep -rn "class.*Code" proc_autocode/
grep -rn "BaseModel" proc_autocode/
grep -rn "@dataclass" proc_autocode/

# Check for schemas module
ls -la proc_autocode/schemas* 2>/dev/null || ls -la modules/proc_autocode/schemas* 2>/dev/null
```

**Document:**
- Structured procedure report model (likely in `proc_schemas` or `proc_report`)
- Autocode output model (codes, modifiers, confidence, rationales)
- Any intermediate models

#### 0.4 Locate NCCI/Golden Knowledge Rules
```bash
# Find the golden knowledge file
find . -name "ip_golden_knowledge*.json" -o -name "*ncci*.json"

# See how it's loaded
grep -rn "golden_knowledge" proc_autocode/
grep -rn "ncci" proc_autocode/
```

**Document:**
- Path to `ip_golden_knowledge_v2_2.json` or equivalent
- How rules are loaded and applied
- What validation occurs (NCCI edits, MER, etc.)

#### 0.5 Review Existing Gemini Integration
```bash
# Find Gemini client code
find . -name "*gemini*" -type f
cat geminiquota.py 2>/dev/null || cat modules/geminiquota.py 2>/dev/null

# Check for OAuth/API key handling
grep -rn "GEMINI_API_KEY" .
grep -rn "GEMINI_USE_OAUTH" .
grep -rn "genai" proc_report/
```

**Document:**
- Location of Gemini client helpers
- Auth pattern (API key vs OAuth)
- Rate limiting approach (`geminiquota.py`)

### Deliverable
Append findings to `docs/CODEX_INTEGRATION_VERIFICATION.md` or create `docs/PHASE_0_RECON.md`:

```markdown
## Phase 0 Reconnaissance Results

### Entry Points
- FastAPI app: `modules/api/fastapi_app.py`
- Coding function: `proc_autocode.<function_name>()` at line X
- Called from API endpoint: `POST /path/to/endpoint`

### Data Models
- Report input: `proc_report.models.StructuredReport` (or actual name)
- Code output: `proc_autocode.models.AutocodeResult` (or actual name)
- Fields: codes[], modifiers[], confidence, rationales{}

### Rule Engine
- Golden knowledge: `data/ip_golden_knowledge_v2_2.json`
- Loader: `proc_autocode/rules.py:load_ncci_rules()`
- Applies: MER, NCCI edits, modifier logic

### Gemini Client
- Module: `geminiquota.py`
- Auth: Env vars GEMINI_API_KEY or GEMINI_USE_OAUTH
- Rate limit: X requests/minute
```

---

## Phase 1: Coding Trace Logger

### Objective
Record every coding run to build a training/evaluation dataset without affecting current behavior.

### 1.1 Create the Coding Trace Model

**File:** `modules/analysis/coding_trace.py`

```python
"""
Coding trace model for logging autocode pipeline runs.
Used for training data collection and evaluation.
"""

from __future__ import annotations
import uuid
import json
import logging
import fcntl
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default output location
DEFAULT_TRACE_FILE = Path("data/coding_traces.jsonl")


@dataclass
class CodingTrace:
    """
    Immutable record of a single autocode pipeline run.
    
    Captures inputs, outputs, and metadata for later analysis.
    """
    # Identifiers
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    report_id: Optional[str] = None
    
    # Inputs
    report_text: str = ""
    structured_report: dict = field(default_factory=dict)
    procedure_type: Optional[str] = None
    
    # Rule engine outputs
    autocode_codes: list[str] = field(default_factory=list)
    autocode_modifiers: dict[str, list[str]] = field(default_factory=dict)
    autocode_confidence: dict[str, float] = field(default_factory=dict)
    autocode_rationales: dict[str, str] = field(default_factory=dict)
    autocode_metadata: dict[str, Any] = field(default_factory=dict)
    
    # NCCI/rule warnings
    ncci_warnings: list[str] = field(default_factory=list)
    mer_applied: bool = False
    
    # Advisor outputs (populated in Phase 3)
    advisor_candidate_codes: list[str] = field(default_factory=list)
    advisor_code_confidence: dict[str, float] = field(default_factory=dict)
    advisor_explanation: Optional[str] = None
    advisor_disagreements: list[str] = field(default_factory=list)
    
    # Final outputs (for human override tracking)
    final_codes: Optional[list[str]] = None
    human_override: bool = False
    
    # Provenance
    source: str = "unknown"
    pipeline_version: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)


def log_coding_trace(
    trace: CodingTrace,
    output_file: Path = DEFAULT_TRACE_FILE
) -> bool:
    """
    Append a coding trace to the JSONL log file.
    
    Uses file locking for concurrent safety. Fails silently with warning
    to avoid breaking the main API flow.
    
    Args:
        trace: The CodingTrace to log
        output_file: Path to the JSONL file
        
    Returns:
        True if logged successfully, False otherwise
    """
    try:
        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append with file locking
        with open(output_file, "a", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(trace.to_json() + "\n")
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        logger.debug(f"Logged coding trace {trace.trace_id}")
        return True
        
    except Exception as e:
        logger.warning(f"Failed to log coding trace: {e}")
        return False


def load_coding_traces(
    input_file: Path = DEFAULT_TRACE_FILE,
    limit: Optional[int] = None
) -> list[CodingTrace]:
    """
    Load coding traces from JSONL file.
    
    Args:
        input_file: Path to the JSONL file
        limit: Maximum number of traces to load (None = all)
        
    Returns:
        List of CodingTrace objects
    """
    traces = []
    
    if not input_file.exists():
        logger.warning(f"Trace file not found: {input_file}")
        return traces
    
    with open(input_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            try:
                data = json.loads(line.strip())
                traces.append(CodingTrace(**data))
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Skipping malformed trace on line {i+1}: {e}")
    
    return traces
```

### 1.2 Wire Logging into the Autocode Pipeline

**Modification to:** `proc_autocode/<main_coder_file>.py` (based on Phase 0 findings)

```python
# Add import at top of file
from modules.analysis.coding_trace import CodingTrace, log_coding_trace

# Feature flag for logging (can be env var controlled)
import os
ENABLE_CODING_TRACE = os.getenv("ENABLE_CODING_TRACE", "true").lower() == "true"


def existing_autocode_function(report_input, **kwargs):
    """
    Your existing autocode function - modify to add trace logging.
    """
    # ... existing logic to generate codes ...
    result = your_existing_coding_logic(report_input)
    
    # === NEW: Log the coding trace ===
    if ENABLE_CODING_TRACE:
        trace = CodingTrace(
            report_id=getattr(report_input, "report_id", None),
            report_text=_extract_report_text(report_input),
            structured_report=_extract_structured_report(report_input),
            procedure_type=getattr(report_input, "procedure_type", None),
            autocode_codes=result.codes,
            autocode_modifiers=result.modifiers,
            autocode_confidence=result.confidence,
            autocode_rationales=result.rationales,
            autocode_metadata=result.metadata,
            ncci_warnings=result.warnings,
            mer_applied=result.mer_applied,
            source="api.autocode",
            pipeline_version=os.getenv("PIPELINE_VERSION", "v4"),
        )
        log_coding_trace(trace)
    # === END NEW ===
    
    return result


def _extract_report_text(report_input) -> str:
    """Extract raw text from report input (adapt to your model)."""
    if hasattr(report_input, "raw_text"):
        return report_input.raw_text
    if hasattr(report_input, "text"):
        return report_input.text
    if isinstance(report_input, dict):
        return report_input.get("raw_text", report_input.get("text", ""))
    return str(report_input)


def _extract_structured_report(report_input) -> dict:
    """Extract structured data from report input (adapt to your model)."""
    if hasattr(report_input, "dict"):
        return report_input.dict()
    if hasattr(report_input, "model_dump"):
        return report_input.model_dump()
    if isinstance(report_input, dict):
        return report_input
    return {}
```

### 1.3 Add Unit Tests

**File:** `tests/test_coding_trace.py`

```python
"""Tests for coding trace logging."""

import json
import tempfile
from pathlib import Path
import pytest

from modules.analysis.coding_trace import (
    CodingTrace,
    log_coding_trace,
    load_coding_traces,
)


class TestCodingTrace:
    """Tests for CodingTrace model."""
    
    def test_default_values(self):
        """Trace should have sensible defaults."""
        trace = CodingTrace()
        
        assert trace.trace_id  # Should have UUID
        assert trace.timestamp  # Should have timestamp
        assert trace.autocode_codes == []
        assert trace.final_codes is None
    
    def test_serialization(self):
        """Trace should serialize to valid JSON."""
        trace = CodingTrace(
            report_text="Test bronchoscopy",
            autocode_codes=["31622", "31623"],
            autocode_confidence={"31622": 0.95, "31623": 0.87},
        )
        
        json_str = trace.to_json()
        data = json.loads(json_str)
        
        assert data["report_text"] == "Test bronchoscopy"
        assert data["autocode_codes"] == ["31622", "31623"]
        assert data["autocode_confidence"]["31622"] == 0.95


class TestLogging:
    """Tests for trace logging functions."""
    
    def test_log_and_load(self, tmp_path):
        """Should log and reload traces correctly."""
        trace_file = tmp_path / "traces.jsonl"
        
        # Log a trace
        trace = CodingTrace(
            report_text="EBUS procedure",
            autocode_codes=["31652"],
        )
        success = log_coding_trace(trace, trace_file)
        assert success
        
        # Load it back
        traces = load_coding_traces(trace_file)
        assert len(traces) == 1
        assert traces[0].report_text == "EBUS procedure"
        assert traces[0].autocode_codes == ["31652"]
    
    def test_log_creates_directory(self, tmp_path):
        """Should create parent directories if needed."""
        trace_file = tmp_path / "nested" / "dir" / "traces.jsonl"
        trace = CodingTrace(report_text="Test")
        
        success = log_coding_trace(trace, trace_file)
        
        assert success
        assert trace_file.exists()
    
    def test_log_silent_failure(self, tmp_path):
        """Should fail silently on permission errors."""
        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        
        trace_file = readonly_dir / "traces.jsonl"
        trace = CodingTrace(report_text="Test")
        
        # Should return False but not raise
        success = log_coding_trace(trace, trace_file)
        assert not success
        
        # Cleanup
        readonly_dir.chmod(0o755)
```

### 1.4 Integration Test

**File:** `tests/integration/test_autocode_logging.py`

```python
"""Integration test: verify autocode writes traces."""

import os
import json
import tempfile
from pathlib import Path
import pytest

# Import your actual autocode function (adjust path based on Phase 0)
# from proc_autocode import autocode_procedure


@pytest.fixture
def trace_file(tmp_path):
    """Temporary trace file."""
    return tmp_path / "test_traces.jsonl"


@pytest.fixture(autouse=True)
def enable_tracing(trace_file, monkeypatch):
    """Enable tracing and redirect to temp file."""
    monkeypatch.setenv("ENABLE_CODING_TRACE", "true")
    # You may need to monkeypatch the default path
    # monkeypatch.setattr("modules.analysis.coding_trace.DEFAULT_TRACE_FILE", trace_file)


@pytest.mark.integration
def test_autocode_creates_trace(trace_file):
    """Calling autocode should write a trace."""
    # TODO: Adjust to your actual API based on Phase 0 findings
    # result = autocode_procedure(your_test_input)
    
    # Verify trace was written
    # assert trace_file.exists()
    # with open(trace_file) as f:
    #     line = f.readline()
    #     trace_data = json.loads(line)
    # assert "autocode_codes" in trace_data
    pass  # Remove this and uncomment above after Phase 0
```

---

## Phase 2: ML Advisor Module

### Objective
Create a pluggable advisor that suggests codes from text, callable from the autocode pipeline or independently.

### 2.1 Create the Advisor Package

**Directory structure:**
```
modules/
└── proc_ml_advisor/
    ├── __init__.py
    ├── models.py          # Input/output data models
    ├── base.py            # Interface and stub implementation
    ├── gemini_advisor.py  # Gemini-backed implementation
    └── prompts.py         # Prompt templates
```

**File:** `modules/proc_ml_advisor/__init__.py`

```python
"""
ML Advisor module for the Procedure Suite autocode pipeline.

This module provides code suggestions from ML/LLM models to augment
the deterministic rule engine. The advisor ONLY suggests - rules decide.
"""

from .models import MLAdvisorInput, MLAdvisorSuggestion
from .base import get_ml_advice, AdvisorBackend

__all__ = [
    "MLAdvisorInput",
    "MLAdvisorSuggestion", 
    "get_ml_advice",
    "AdvisorBackend",
]
```

**File:** `modules/proc_ml_advisor/models.py`

```python
"""Data models for the ML advisor."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MLAdvisorInput:
    """
    Input to the ML advisor.
    
    Contains all context needed for the model to suggest codes.
    """
    trace_id: str
    report_id: Optional[str]
    report_text: str
    structured_report: dict
    
    # Existing rule-based codes (for comparison/refinement)
    autocode_codes: list[str] = field(default_factory=list)
    
    # Optional context
    procedure_type: Optional[str] = None
    patient_context: Optional[dict] = None
    

@dataclass
class MLAdvisorSuggestion:
    """
    Output from the ML advisor.
    
    Contains suggested codes with confidence and explanations.
    Does NOT make final coding decisions.
    """
    # Suggested codes (may overlap with or differ from rule codes)
    candidate_codes: list[str] = field(default_factory=list)
    
    # Confidence per code (0.0 to 1.0)
    code_confidence: dict[str, float] = field(default_factory=dict)
    
    # Human-readable explanation of suggestions
    explanation: Optional[str] = None
    
    # Codes advisor suggests that rules did not include
    additions: list[str] = field(default_factory=list)
    
    # Codes advisor thinks may be unnecessary
    removals: list[str] = field(default_factory=list)
    
    # Raw model output for debugging
    raw_model_output: Optional[dict[str, Any]] = None
    
    # Processing metadata
    model_name: Optional[str] = None
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    
    @property
    def disagreements(self) -> list[str]:
        """Codes where advisor and rules disagree."""
        return self.additions + self.removals
```

**File:** `modules/proc_ml_advisor/base.py`

```python
"""
Base advisor interface and stub implementation.

The advisor follows a provider pattern - different backends can be
plugged in via the AdvisorBackend enum and ADVISOR_BACKEND env var.
"""

from __future__ import annotations
import os
import logging
from enum import Enum
from typing import Callable

from .models import MLAdvisorInput, MLAdvisorSuggestion

logger = logging.getLogger(__name__)


class AdvisorBackend(Enum):
    """Available advisor backends."""
    STUB = "stub"
    GEMINI = "gemini"
    # Future: OPENAI = "openai"
    # Future: LOCAL = "local"


def get_ml_advice(
    payload: MLAdvisorInput,
    backend: AdvisorBackend | None = None,
) -> MLAdvisorSuggestion:
    """
    Get ML advisor suggestions for a coding payload.
    
    This is the main entry point. It routes to the appropriate backend
    based on configuration.
    
    Args:
        payload: The input data for the advisor
        backend: Optional override for the backend (uses env var if None)
        
    Returns:
        MLAdvisorSuggestion with candidate codes and confidence scores
    """
    if backend is None:
        backend_str = os.getenv("ADVISOR_BACKEND", "stub")
        try:
            backend = AdvisorBackend(backend_str.lower())
        except ValueError:
            logger.warning(f"Unknown ADVISOR_BACKEND '{backend_str}', using stub")
            backend = AdvisorBackend.STUB
    
    # Route to appropriate backend
    if backend == AdvisorBackend.GEMINI:
        from .gemini_advisor import gemini_get_advice
        return gemini_get_advice(payload)
    else:
        return stub_get_advice(payload)


def stub_get_advice(payload: MLAdvisorInput) -> MLAdvisorSuggestion:
    """
    Stub advisor that returns minimal/echo response.
    
    Use this when:
    - ML advisor is not configured
    - Testing the integration without API calls
    - Establishing baseline behavior
    """
    return MLAdvisorSuggestion(
        candidate_codes=payload.autocode_codes.copy(),  # Echo back rule codes
        code_confidence={code: 0.5 for code in payload.autocode_codes},
        explanation="ML advisor not configured (stub mode)",
        additions=[],
        removals=[],
        model_name="stub",
    )
```

### 2.2 Prompt Templates

**File:** `modules/proc_ml_advisor/prompts.py`

```python
"""
Prompt templates for the ML advisor.

These prompts are designed to work with Gemini and similar LLMs.
They emphasize that the model should SUGGEST, not DECIDE.
"""

SYSTEM_PROMPT = """You are an expert medical coding advisor for interventional pulmonology procedures.
Your role is to SUGGEST CPT codes based on procedure documentation - you do NOT make final coding decisions.

Key principles:
1. Analyze the procedure text and structured data carefully
2. Consider CPT coding guidelines, NCCI edits, and the Multiple Endoscopy Rule (MER)
3. Flag codes that may need review, not definitive answers
4. Acknowledge uncertainty when present
5. NEVER invent codes - only suggest valid CPT codes from the bronchoscopy family (31xxx) and related procedures

Your suggestions will be reviewed by a deterministic rule engine that makes final decisions."""


CODE_SUGGESTION_PROMPT = """Analyze this interventional pulmonology procedure and suggest appropriate CPT codes.

## Procedure Text
{report_text}

## Structured Data
{structured_json}

## Rule Engine Codes (for reference)
The deterministic rule engine has already suggested these codes: {rule_codes}

## Your Task
1. Review the procedure documentation
2. Identify all billable procedures performed
3. Consider appropriate modifiers (-50 bilateral, -51 multiple procedures, -59 distinct, etc.)
4. Note any NCCI bundling concerns
5. Suggest any codes the rule engine may have missed
6. Flag any rule engine codes that seem questionable

## Response Format
Return a JSON object with this exact structure:
{{
  "candidate_codes": ["31622", "31625", ...],  // All codes you think apply
  "code_confidence": {{"31622": 0.95, "31625": 0.80, ...}},  // 0.0 to 1.0
  "additions": ["31625"],  // Codes you suggest that rules didn't include
  "removals": [],  // Rule codes you think may be wrong
  "explanation": "Brief explanation of your suggestions and reasoning",
  "warnings": ["Any NCCI concerns", "Documentation gaps", ...]
}}

IMPORTANT: Only output the JSON object, no other text."""


def format_code_suggestion_prompt(
    report_text: str,
    structured_report: dict,
    rule_codes: list[str],
) -> str:
    """Format the code suggestion prompt with actual data."""
    import json
    
    return CODE_SUGGESTION_PROMPT.format(
        report_text=report_text,
        structured_json=json.dumps(structured_report, indent=2),
        rule_codes=", ".join(rule_codes) if rule_codes else "(none)",
    )
```

### 2.3 Gemini-Backed Implementation

**File:** `modules/proc_ml_advisor/gemini_advisor.py`

```python
"""
Gemini-backed ML advisor implementation.

Reuses the existing Gemini infrastructure from the reporter module.
"""

from __future__ import annotations
import os
import json
import time
import logging
from typing import Optional

from .models import MLAdvisorInput, MLAdvisorSuggestion
from .prompts import SYSTEM_PROMPT, format_code_suggestion_prompt

logger = logging.getLogger(__name__)

# Try to import existing Gemini client
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed, Gemini advisor unavailable")


def _configure_genai() -> bool:
    """
    Configure the Gemini client using existing patterns.
    
    Supports both API key and OAuth authentication.
    Returns True if configured successfully.
    """
    if not GENAI_AVAILABLE:
        return False
    
    # Check for OAuth mode first (matches GEMINI_SETUP.md)
    if os.getenv("GEMINI_USE_OAUTH", "").lower() == "true":
        # OAuth uses application default credentials
        # genai handles this automatically when no API key is set
        return True
    
    # Fall back to API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set and GEMINI_USE_OAUTH not true")
        return False
    
    genai.configure(api_key=api_key)
    return True


def gemini_get_advice(payload: MLAdvisorInput) -> MLAdvisorSuggestion:
    """
    Get coding suggestions from Gemini.
    
    Falls back to stub response if Gemini is unavailable or errors.
    """
    from .base import stub_get_advice
    
    if not _configure_genai():
        logger.info("Gemini not configured, falling back to stub")
        return stub_get_advice(payload)
    
    try:
        return _call_gemini(payload)
    except Exception as e:
        logger.error(f"Gemini advisor error: {e}")
        return stub_get_advice(payload)


def _call_gemini(payload: MLAdvisorInput) -> MLAdvisorSuggestion:
    """Make the actual Gemini API call."""
    start_time = time.time()
    
    # Use Gemini 1.5 Pro for best coding accuracy
    model_name = os.getenv("ADVISOR_MODEL", "gemini-1.5-pro")
    model = genai.GenerativeModel(
        model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.2,  # Low temp for more deterministic output
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
    )
    
    # Format the prompt
    prompt = format_code_suggestion_prompt(
        report_text=payload.report_text,
        structured_report=payload.structured_report,
        rule_codes=payload.autocode_codes,
    )
    
    # Call Gemini
    response = model.generate_content(prompt)
    latency_ms = (time.time() - start_time) * 1000
    
    # Parse response
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse Gemini JSON response: {response.text[:200]}")
        result = {"candidate_codes": [], "explanation": "Failed to parse model output"}
    
    # Build suggestion
    return MLAdvisorSuggestion(
        candidate_codes=result.get("candidate_codes", []),
        code_confidence=result.get("code_confidence", {}),
        explanation=result.get("explanation"),
        additions=result.get("additions", []),
        removals=result.get("removals", []),
        raw_model_output=result,
        model_name=model_name,
        latency_ms=latency_ms,
        tokens_used=response.usage_metadata.total_token_count if hasattr(response, "usage_metadata") else None,
    )
```

### 2.4 Tests for Advisor Module

**File:** `tests/test_ml_advisor.py`

```python
"""Tests for the ML advisor module."""

import pytest
from unittest.mock import patch, MagicMock

from modules.proc_ml_advisor.models import MLAdvisorInput, MLAdvisorSuggestion
from modules.proc_ml_advisor.base import get_ml_advice, AdvisorBackend, stub_get_advice


class TestMLAdvisorModels:
    """Tests for advisor data models."""
    
    def test_input_defaults(self):
        """Input should have sensible defaults."""
        input_data = MLAdvisorInput(
            trace_id="test-123",
            report_id="report-456",
            report_text="Test bronchoscopy",
            structured_report={"procedure": "bronchoscopy"},
        )
        assert input_data.autocode_codes == []
        assert input_data.procedure_type is None
    
    def test_suggestion_disagreements(self):
        """Disagreements should combine additions and removals."""
        suggestion = MLAdvisorSuggestion(
            candidate_codes=["31622", "31625"],
            additions=["31625"],
            removals=["31623"],
        )
        assert suggestion.disagreements == ["31625", "31623"]


class TestStubAdvisor:
    """Tests for stub advisor."""
    
    def test_echoes_rule_codes(self):
        """Stub should echo back rule codes."""
        input_data = MLAdvisorInput(
            trace_id="test",
            report_id=None,
            report_text="Test",
            structured_report={},
            autocode_codes=["31622", "31623"],
        )
        
        result = stub_get_advice(input_data)
        
        assert result.candidate_codes == ["31622", "31623"]
        assert result.model_name == "stub"
        assert result.additions == []
        assert result.removals == []


class TestGetMLAdvice:
    """Tests for the main get_ml_advice function."""
    
    def test_uses_stub_by_default(self, monkeypatch):
        """Should use stub when no backend configured."""
        monkeypatch.delenv("ADVISOR_BACKEND", raising=False)
        
        input_data = MLAdvisorInput(
            trace_id="test",
            report_id=None,
            report_text="Test",
            structured_report={},
        )
        
        result = get_ml_advice(input_data)
        
        assert result.model_name == "stub"
    
    def test_explicit_backend_override(self):
        """Should respect explicit backend parameter."""
        input_data = MLAdvisorInput(
            trace_id="test",
            report_id=None,
            report_text="Test",
            structured_report={},
        )
        
        result = get_ml_advice(input_data, backend=AdvisorBackend.STUB)
        
        assert result.model_name == "stub"
```

---

## Phase 3: Hybrid Integration

### Objective
Wire the advisor into the rule engine and API, maintaining rules as the final authority.

### 3.1 Create the Hybrid Combiner

**File:** `modules/proc_autocode/hybrid.py`

```python
"""
Hybrid combiner for rule-based and ML advisor coding results.

The combiner merges suggestions while keeping rules as the final authority.
In v1, final_codes always equals rule_codes. The advisor only suggests.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional

from modules.proc_ml_advisor.models import MLAdvisorSuggestion


@dataclass
class HybridCodingResult:
    """
    Combined result from rule engine and ML advisor.
    
    Attributes:
        final_codes: The authoritative codes (rule engine in v1)
        rule_codes: Codes from the deterministic rule engine
        rule_confidence: Confidence from rule engine
        advisor_candidate_codes: Codes suggested by ML advisor
        advisor_code_confidence: Confidence per advisor code
        advisor_explanation: Human-readable advisor explanation
        disagreements: Where advisor and rules differ
        metadata: Additional context
    """
    # Final output (rules win in v1)
    final_codes: list[str]
    
    # Rule engine results
    rule_codes: list[str]
    rule_confidence: dict[str, float]
    rule_rationales: dict[str, str] = field(default_factory=dict)
    
    # Advisor results  
    advisor_candidate_codes: list[str] = field(default_factory=list)
    advisor_code_confidence: dict[str, float] = field(default_factory=dict)
    advisor_explanation: Optional[str] = None
    
    # Comparison
    disagreements: list[str] = field(default_factory=list)
    advisor_additions: list[str] = field(default_factory=list)
    advisor_removals: list[str] = field(default_factory=list)
    
    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)


def merge_autocode_and_advisor(
    rule_codes: list[str],
    rule_confidence: dict[str, float],
    rule_rationales: dict[str, str],
    advisor: MLAdvisorSuggestion,
    policy: str = "rules_only",  # Future: "advisor_augments", "human_review"
) -> HybridCodingResult:
    """
    Merge rule engine and advisor results.
    
    Args:
        rule_codes: Codes from the deterministic rule engine
        rule_confidence: Confidence scores from rules
        rule_rationales: Explanations from rules
        advisor: ML advisor suggestions
        policy: How to combine (v1 only supports "rules_only")
        
    Returns:
        HybridCodingResult with combined information
    """
    # In v1, rules always win
    if policy == "rules_only":
        final_codes = rule_codes.copy()
    # Future policies could allow advisor to add/modify codes
    else:
        final_codes = rule_codes.copy()
    
    # Identify disagreements
    rule_set = set(rule_codes)
    advisor_set = set(advisor.candidate_codes)
    
    advisor_additions = list(advisor_set - rule_set)
    advisor_removals = [code for code in advisor.removals if code in rule_set]
    disagreements = advisor_additions + advisor_removals
    
    return HybridCodingResult(
        final_codes=final_codes,
        rule_codes=rule_codes,
        rule_confidence=rule_confidence,
        rule_rationales=rule_rationales,
        advisor_candidate_codes=advisor.candidate_codes,
        advisor_code_confidence=advisor.code_confidence,
        advisor_explanation=advisor.explanation,
        disagreements=disagreements,
        advisor_additions=advisor_additions,
        advisor_removals=advisor_removals,
        metadata={
            "policy": policy,
            "advisor_model": advisor.model_name,
            "advisor_latency_ms": advisor.latency_ms,
        },
    )
```

### 3.2 Update the Autocode Pipeline

**Modification to:** `proc_autocode/<main_coder_file>.py`

```python
# Add imports
from modules.proc_ml_advisor import get_ml_advice, MLAdvisorInput
from modules.proc_autocode.hybrid import merge_autocode_and_advisor, HybridCodingResult
from modules.analysis.coding_trace import CodingTrace, log_coding_trace

# Feature flags
import os
ENABLE_CODING_TRACE = os.getenv("ENABLE_CODING_TRACE", "true").lower() == "true"
ENABLE_ML_ADVISOR = os.getenv("ENABLE_ML_ADVISOR", "false").lower() == "true"


def autocode_with_advisor(
    report_input,
    include_advisor: bool = None,
    **kwargs
) -> HybridCodingResult:
    """
    Enhanced autocode function with optional ML advisor.
    
    Args:
        report_input: Structured procedure report
        include_advisor: Override for advisor (uses env var if None)
        **kwargs: Additional arguments for the rule engine
        
    Returns:
        HybridCodingResult with rule codes and advisor suggestions
    """
    # Determine if advisor should run
    if include_advisor is None:
        include_advisor = ENABLE_ML_ADVISOR
    
    # Step 1: Run the rule engine (your existing logic)
    rule_result = your_existing_coding_logic(report_input, **kwargs)
    
    # Step 2: Prepare trace data
    trace_id = str(uuid.uuid4())
    report_text = _extract_report_text(report_input)
    structured_report = _extract_structured_report(report_input)
    
    # Step 3: Run ML advisor if enabled
    if include_advisor:
        advisor_input = MLAdvisorInput(
            trace_id=trace_id,
            report_id=getattr(report_input, "report_id", None),
            report_text=report_text,
            structured_report=structured_report,
            autocode_codes=rule_result.codes,
            procedure_type=getattr(report_input, "procedure_type", None),
        )
        advisor_suggestion = get_ml_advice(advisor_input)
    else:
        # Create empty advisor suggestion
        from modules.proc_ml_advisor.models import MLAdvisorSuggestion
        advisor_suggestion = MLAdvisorSuggestion()
    
    # Step 4: Merge results
    hybrid_result = merge_autocode_and_advisor(
        rule_codes=rule_result.codes,
        rule_confidence=rule_result.confidence,
        rule_rationales=rule_result.rationales,
        advisor=advisor_suggestion,
        policy="rules_only",  # v1: rules are authoritative
    )
    
    # Step 5: Log trace
    if ENABLE_CODING_TRACE:
        trace = CodingTrace(
            trace_id=trace_id,
            report_id=getattr(report_input, "report_id", None),
            report_text=report_text,
            structured_report=structured_report,
            autocode_codes=rule_result.codes,
            autocode_confidence=rule_result.confidence,
            autocode_rationales=rule_result.rationales,
            ncci_warnings=rule_result.warnings,
            advisor_candidate_codes=advisor_suggestion.candidate_codes,
            advisor_code_confidence=advisor_suggestion.code_confidence,
            advisor_explanation=advisor_suggestion.explanation,
            advisor_disagreements=hybrid_result.disagreements,
            source="api.autocode_with_advisor",
        )
        log_coding_trace(trace)
    
    return hybrid_result
```

### 3.3 Add API Endpoint

**Modification to:** `modules/api/fastapi_app.py`

```python
# Add imports
from pydantic import BaseModel, Field
from typing import Optional
from modules.proc_autocode.hybrid import HybridCodingResult

# === NEW RESPONSE MODELS ===

class AdvisorMetadata(BaseModel):
    """Metadata about advisor processing."""
    model: Optional[str] = None
    latency_ms: Optional[float] = None
    policy: str = "rules_only"


class HybridCodingResponse(BaseModel):
    """Response from the hybrid coding endpoint."""
    # Final codes (rule engine in v1)
    final_codes: list[str]
    
    # Rule engine results
    rule_codes: list[str]
    rule_confidence: dict[str, float] = Field(default_factory=dict)
    
    # Advisor results
    advisor_candidate_codes: list[str] = Field(default_factory=list)
    advisor_code_confidence: dict[str, float] = Field(default_factory=dict)
    advisor_explanation: Optional[str] = None
    
    # Comparison
    disagreements: list[str] = Field(default_factory=list)
    
    # Metadata
    metadata: AdvisorMetadata = Field(default_factory=AdvisorMetadata)
    
    class Config:
        json_schema_extra = {
            "example": {
                "final_codes": ["31622", "31653"],
                "rule_codes": ["31622", "31653"],
                "rule_confidence": {"31622": 0.95, "31653": 0.90},
                "advisor_candidate_codes": ["31622", "31653", "31625"],
                "advisor_code_confidence": {"31622": 0.92, "31653": 0.88, "31625": 0.75},
                "advisor_explanation": "Consider adding 31625 for lavage if documented",
                "disagreements": ["31625"],
                "metadata": {"model": "gemini-1.5-pro", "latency_ms": 450.2, "policy": "rules_only"}
            }
        }


# === NEW ENDPOINT ===

@app.post("/code_with_advisor", response_model=HybridCodingResponse, tags=["Coding"])
async def code_with_advisor(
    request: YourExistingCodeRequest,  # Use your existing request model
    include_advisor: bool = True,
):
    """
    Code a procedure report with optional ML advisor suggestions.
    
    This endpoint runs the deterministic rule engine AND the ML advisor,
    returning both results. In v1, final_codes always equals rule_codes.
    
    The advisor suggestions are for review/QA purposes only.
    """
    try:
        # Import here to avoid circular deps
        from proc_autocode import autocode_with_advisor
        
        result = autocode_with_advisor(
            request,
            include_advisor=include_advisor,
        )
        
        return HybridCodingResponse(
            final_codes=result.final_codes,
            rule_codes=result.rule_codes,
            rule_confidence=result.rule_confidence,
            advisor_candidate_codes=result.advisor_candidate_codes,
            advisor_code_confidence=result.advisor_code_confidence,
            advisor_explanation=result.advisor_explanation,
            disagreements=result.disagreements,
            metadata=AdvisorMetadata(
                model=result.metadata.get("advisor_model"),
                latency_ms=result.metadata.get("advisor_latency_ms"),
                policy=result.metadata.get("policy", "rules_only"),
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === OPTIONAL: Add advisor info to existing endpoint ===

# If you want to augment the existing coding endpoint rather than
# create a new one, you can add optional fields to the response model
# and populate them when include_advisor=True is passed as a query param.
```

---

## Phase 4: Evaluation Harness

### Objective
Create tools to compare rule-only vs ML advisor vs hybrid policies.

### 4.1 Evaluation Script

**File:** `modules/analysis/eval_hybrid_coder.py`

```python
"""
Evaluation harness for comparing coding approaches.

Usage:
    python -m modules.analysis.eval_hybrid_coder --input data/coding_traces.jsonl
"""

from __future__ import annotations
import json
import argparse
from pathlib import Path
from dataclasses import dataclass
from collections import Counter
from typing import Optional

from modules.analysis.coding_trace import load_coding_traces, CodingTrace


@dataclass
class EvaluationMetrics:
    """Metrics from evaluating coding traces."""
    total_traces: int = 0
    traces_with_advisor: int = 0
    
    # Agreement metrics
    full_agreement: int = 0  # Advisor and rules produced same codes
    advisor_suggested_extras: int = 0  # Advisor suggested codes rules didn't
    advisor_suggested_removals: int = 0  # Advisor flagged rule codes as wrong
    
    # Code statistics
    unique_rule_codes: set = None
    unique_advisor_codes: set = None
    
    # If final_codes (human-reviewed) are available
    traces_with_final: int = 0
    rule_precision: Optional[float] = None
    rule_recall: Optional[float] = None
    advisor_precision: Optional[float] = None
    advisor_recall: Optional[float] = None
    
    def __post_init__(self):
        if self.unique_rule_codes is None:
            self.unique_rule_codes = set()
        if self.unique_advisor_codes is None:
            self.unique_advisor_codes = set()


def evaluate_traces(traces: list[CodingTrace]) -> EvaluationMetrics:
    """
    Compute evaluation metrics from coding traces.
    
    Args:
        traces: List of CodingTrace objects
        
    Returns:
        EvaluationMetrics summarizing the evaluation
    """
    metrics = EvaluationMetrics()
    metrics.total_traces = len(traces)
    
    # For precision/recall calculation
    rule_tp, rule_fp, rule_fn = 0, 0, 0
    advisor_tp, advisor_fp, advisor_fn = 0, 0, 0
    
    for trace in traces:
        # Track unique codes seen
        metrics.unique_rule_codes.update(trace.autocode_codes)
        
        if trace.advisor_candidate_codes:
            metrics.traces_with_advisor += 1
            metrics.unique_advisor_codes.update(trace.advisor_candidate_codes)
            
            # Check agreement
            rule_set = set(trace.autocode_codes)
            advisor_set = set(trace.advisor_candidate_codes)
            
            if rule_set == advisor_set:
                metrics.full_agreement += 1
            
            if advisor_set - rule_set:
                metrics.advisor_suggested_extras += 1
            
            if trace.advisor_disagreements:
                removals = [c for c in trace.advisor_disagreements 
                           if c in rule_set and c not in advisor_set]
                if removals:
                    metrics.advisor_suggested_removals += 1
        
        # If we have human-reviewed final codes, compute precision/recall
        if trace.final_codes is not None:
            metrics.traces_with_final += 1
            final_set = set(trace.final_codes)
            rule_set = set(trace.autocode_codes)
            advisor_set = set(trace.advisor_candidate_codes) if trace.advisor_candidate_codes else set()
            
            # Rule engine metrics
            rule_tp += len(rule_set & final_set)
            rule_fp += len(rule_set - final_set)
            rule_fn += len(final_set - rule_set)
            
            # Advisor metrics
            advisor_tp += len(advisor_set & final_set)
            advisor_fp += len(advisor_set - final_set)
            advisor_fn += len(final_set - advisor_set)
    
    # Calculate precision/recall if we have final codes
    if metrics.traces_with_final > 0:
        if rule_tp + rule_fp > 0:
            metrics.rule_precision = rule_tp / (rule_tp + rule_fp)
        if rule_tp + rule_fn > 0:
            metrics.rule_recall = rule_tp / (rule_tp + rule_fn)
        if advisor_tp + advisor_fp > 0:
            metrics.advisor_precision = advisor_tp / (advisor_tp + advisor_fp)
        if advisor_tp + advisor_fn > 0:
            metrics.advisor_recall = advisor_tp / (advisor_tp + advisor_fn)
    
    return metrics


def print_report(metrics: EvaluationMetrics) -> None:
    """Print a human-readable evaluation report."""
    print("\n" + "=" * 60)
    print("HYBRID CODER EVALUATION REPORT")
    print("=" * 60)
    
    print(f"\n📊 Dataset Statistics")
    print(f"   Total traces: {metrics.total_traces}")
    print(f"   Traces with advisor: {metrics.traces_with_advisor}")
    print(f"   Traces with human review: {metrics.traces_with_final}")
    
    print(f"\n🔍 Agreement Analysis")
    if metrics.traces_with_advisor > 0:
        agreement_pct = metrics.full_agreement / metrics.traces_with_advisor * 100
        print(f"   Full agreement: {metrics.full_agreement} ({agreement_pct:.1f}%)")
        print(f"   Advisor suggested extras: {metrics.advisor_suggested_extras}")
        print(f"   Advisor suggested removals: {metrics.advisor_suggested_removals}")
    else:
        print("   No traces with advisor data")
    
    print(f"\n📋 Code Coverage")
    print(f"   Unique rule codes: {len(metrics.unique_rule_codes)}")
    print(f"   Unique advisor codes: {len(metrics.unique_advisor_codes)}")
    
    if metrics.traces_with_final > 0:
        print(f"\n🎯 Accuracy Metrics (vs human review)")
        print(f"   Rule Engine:")
        if metrics.rule_precision is not None:
            print(f"      Precision: {metrics.rule_precision:.3f}")
        if metrics.rule_recall is not None:
            print(f"      Recall: {metrics.rule_recall:.3f}")
        print(f"   ML Advisor:")
        if metrics.advisor_precision is not None:
            print(f"      Precision: {metrics.advisor_precision:.3f}")
        if metrics.advisor_recall is not None:
            print(f"      Recall: {metrics.advisor_recall:.3f}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate hybrid coder performance from coding traces"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=Path("data/coding_traces.jsonl"),
        help="Path to coding traces JSONL file",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=None,
        help="Limit number of traces to evaluate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    # Load traces
    print(f"Loading traces from {args.input}...")
    traces = load_coding_traces(args.input, limit=args.limit)
    
    if not traces:
        print("No traces found!")
        return
    
    # Evaluate
    metrics = evaluate_traces(traces)
    
    # Output
    if args.json:
        output = {
            "total_traces": metrics.total_traces,
            "traces_with_advisor": metrics.traces_with_advisor,
            "traces_with_final": metrics.traces_with_final,
            "full_agreement": metrics.full_agreement,
            "advisor_suggested_extras": metrics.advisor_suggested_extras,
            "advisor_suggested_removals": metrics.advisor_suggested_removals,
            "unique_rule_codes": len(metrics.unique_rule_codes),
            "unique_advisor_codes": len(metrics.unique_advisor_codes),
            "rule_precision": metrics.rule_precision,
            "rule_recall": metrics.rule_recall,
            "advisor_precision": metrics.advisor_precision,
            "advisor_recall": metrics.advisor_recall,
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(metrics)


if __name__ == "__main__":
    main()
```

---

## Phase 5: Safety, Audits & Documentation

### 5.1 Audit Trail Requirements

Ensure these are preserved/implemented:

1. **Rule explanations unchanged**: The existing rationale fields from the rule engine must remain intact
2. **Clear labeling**: Advisor suggestions are ALWAYS labeled as "advisor suggestion" not "recommended codes"
3. **No blurring**: Never mix advisor codes into final_codes without explicit flag
4. **Provenance**: Every trace includes source, version, and timestamp

### 5.2 Documentation Updates

**File:** `docs/hybrid_coder_overview.md`

```markdown
# Hybrid Coder Architecture

## Overview

The Procedure Suite coding pipeline combines deterministic rules with ML/LLM suggestions:

```
┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│   Reporter   │────▶│  Structured  │────▶│    Rule     │
│   Module     │     │    Report    │     │   Engine    │
└──────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                     ┌──────────────┐            │
                     │  ML Advisor  │◀───────────┤
                     │  (Gemini)    │            │
                     └──────┬───────┘            │
                            │                    │
                            ▼                    ▼
                     ┌──────────────────────────────────┐
                     │         Hybrid Combiner          │
                     │  (Rules = Authority in v1)       │
                     └───────────────┬──────────────────┘
                                     │
                                     ▼
                     ┌──────────────────────────────────┐
                     │            FastAPI               │
                     │   /code_with_advisor endpoint    │
                     └──────────────────────────────────┘
```

## Key Principles

1. **Rules are authoritative**: The deterministic rule engine makes final coding decisions
2. **Advisor only suggests**: ML suggestions are for QA/review, not auto-applied
3. **Full transparency**: Disagreements are highlighted for human review
4. **Backward compatible**: Existing endpoints work unchanged

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CODING_TRACE` | `true` | Log coding traces to JSONL |
| `ENABLE_ML_ADVISOR` | `false` | Enable ML advisor (requires Gemini) |
| `ADVISOR_BACKEND` | `stub` | `stub` or `gemini` |
| `ADVISOR_MODEL` | `gemini-1.5-pro` | Gemini model to use |
| `GEMINI_API_KEY` | - | API key for Gemini |
| `GEMINI_USE_OAUTH` | `false` | Use OAuth instead of API key |

### Enabling the Advisor

```bash
# For production with API key
export ENABLE_ML_ADVISOR=true
export ADVISOR_BACKEND=gemini
export GEMINI_API_KEY=your-key-here

# For production with OAuth
export ENABLE_ML_ADVISOR=true
export ADVISOR_BACKEND=gemini
export GEMINI_USE_OAUTH=true
```

## API Usage

### Endpoint: POST /code_with_advisor

```bash
curl -X POST http://localhost:8000/code_with_advisor \
  -H "Content-Type: application/json" \
  -d '{
    "report_text": "Bronchoscopy with EBUS-TBNA...",
    "structured_report": {...}
  }'
```

Response includes both rule codes and advisor suggestions:

```json
{
  "final_codes": ["31622", "31653"],
  "rule_codes": ["31622", "31653"],
  "advisor_candidate_codes": ["31622", "31653", "31625"],
  "advisor_explanation": "Consider 31625 if BAL was performed",
  "disagreements": ["31625"]
}
```

## Evaluation

Run offline evaluation:

```bash
python -m modules.analysis.eval_hybrid_coder --input data/coding_traces.jsonl
```
```

---

## Acceptance Checklist

Before considering implementation complete:

### Build & Test
- [ ] `make preflight` passes
- [ ] `make test` passes
- [ ] No new linting errors

### Backward Compatibility
- [ ] Existing `/code` endpoint behavior unchanged
- [ ] Can disable advisor with `ENABLE_ML_ADVISOR=false`
- [ ] Existing API clients work without modification

### Logging
- [ ] Traces written to `data/coding_traces.jsonl`
- [ ] Each trace has valid UUID and timestamp
- [ ] Log failures don't crash the API

### ML Advisor
- [ ] `modules/proc_ml_advisor/` package exists
- [ ] `get_ml_advice()` interface stable
- [ ] Stub implementation works without Gemini
- [ ] Gemini implementation uses existing auth patterns

### Hybrid Integration
- [ ] `merge_autocode_and_advisor()` works
- [ ] `final_codes == rule_codes` in v1
- [ ] Disagreements accurately identified
- [ ] `/code_with_advisor` endpoint exists and documented

### Evaluation
- [ ] `eval_hybrid_coder.py` runs from CLI
- [ ] Produces meaningful metrics
- [ ] JSON output option works

### Documentation
- [ ] `docs/hybrid_coder_overview.md` created
- [ ] Phase 0 findings documented
- [ ] Environment variables documented
- [ ] API changes in OpenAPI spec

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Advisor suggests incorrect codes | Rules remain authoritative; advisor only suggests |
| Gemini API failures | Graceful fallback to stub; silent failures in logging |
| Performance regression | Advisor is optional via feature flag |
| Data privacy | Trace logging is local JSONL, not transmitted |
| Breaking existing clients | New endpoint, existing unchanged |
| Golden knowledge drift | Advisor references rule codes, doesn't replace |

---

## Appendix: File Inventory

### New Files to Create
```
modules/
├── analysis/
│   ├── __init__.py
│   ├── coding_trace.py
│   └── eval_hybrid_coder.py
├── proc_ml_advisor/
│   ├── __init__.py
│   ├── models.py
│   ├── base.py
│   ├── gemini_advisor.py
│   └── prompts.py
└── proc_autocode/
    └── hybrid.py

tests/
├── test_coding_trace.py
├── test_ml_advisor.py
└── integration/
    └── test_autocode_logging.py

docs/
├── hybrid_coder_overview.md
└── PHASE_0_RECON.md

data/
└── coding_traces.jsonl  (created at runtime)
```

### Files to Modify
```
modules/api/fastapi_app.py          # Add /code_with_advisor endpoint
proc_autocode/<main_file>.py        # Add logging and advisor integration
.env.sample                          # Document new env vars
```
