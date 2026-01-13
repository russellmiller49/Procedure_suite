# Multi-Agent Pipeline Documentation

This document describes the 3-agent pipeline used for structured note processing in the Procedure Suite.

## Overview

The agents module (`modules/agents/`) provides **deterministic, structured note processing** that can be used in two ways:

- **Focused extraction helper (used today)**: `ParserAgent` is used to segment notes and optionally “focus” extraction onto high-yield sections for deterministic registry extraction (see `modules/registry/extraction/focus.py`).
- **Full 3-agent pipeline (available, experimental)**: `Parser → Summarizer → Structurer` via `modules/agents/run_pipeline.py`. Today, `StructurerAgent` is a placeholder and the “agents structurer” extraction mode is intentionally guarded/fallbacks to the engine.

The goal is to make downstream extraction more reliable and auditable without seeding registry extraction with CPT hints when running in extraction-first mode.

## Registry V3 focusing (LLM input slicing)

Registry V3 introduces a stricter, section-aware focusing helper used to limit what the V3 extractor sees:

- **Entry point:** `modules/registry/processing/focus.py:get_procedure_focus()`
- **Sources:** prefers `ParserAgent` segmentation, then `SectionizerService`, with a regex fallback.
- **Target sections:** `PROCEDURE`, `FINDINGS`, `IMPRESSION`, `TECHNIQUE`, `OPERATIVE REPORT`
- **Fail-safe:** if no target headings are found, returns the full original note text (never empty).

## Where this fits in the system

The system has two major registry flows (feature-flagged):

- **Hybrid-first (default)**: CPT coder → CPT→registry mapping → registry engine extraction → merge/validate.
- **Extraction-first (feature flag)**: extract registry from raw note text (no CPT hints) → deterministic registry→CPT derivation → optional auditing/self-correction.

Agents are relevant primarily to **extraction-first**:

- When `PROCSUITE_PIPELINE_MODE=extraction_first` and `REGISTRY_EXTRACTION_ENGINE=agents_focus_then_engine`, the system will use `ParserAgent` to focus the note text for the deterministic engine extraction. Guardrail: auditing always uses the full raw note text.

### Configuration

These environment variables control whether/where agents are used:

- **`PROCSUITE_PIPELINE_MODE`**: `current` (hybrid-first) or `extraction_first`
- **`REGISTRY_EXTRACTION_ENGINE`** (only meaningful in extraction-first): `engine`, `agents_focus_then_engine`, or `agents_structurer`

Notes:
- `agents_structurer` is currently **not implemented** (it is expected to raise `NotImplementedError` and fall back to the deterministic engine).
- CPT coding is handled by the coder module (`modules/coder/`) and is **not** produced by agents in the current architecture.

## Full pipeline (conceptual)

The agents module implements a pipeline of three specialized agents that process procedure notes sequentially:

```
Raw Text → Parser → Summarizer → Structurer → Registry + Codes
```

Each agent has:
- **Input contract** (Pydantic model)
- **Output contract** (Pydantic model)
- **Status tracking** (ok, degraded, failed)
- **Error/warning collection**
- **Trace metadata** for debugging

## Architecture

```
modules/agents/
├── contracts.py                # I/O schemas for all agents
├── run_pipeline.py             # Pipeline orchestration
├── parser/
│   └── parser_agent.py         # ParserAgent implementation
├── summarizer/
│   └── summarizer_agent.py     # SummarizerAgent implementation
└── structurer/
    └── structurer_agent.py     # StructurerAgent implementation
```

## Current implementation status

- **ParserAgent**: implemented and used for deterministic section segmentation and focusing.
- **SummarizerAgent**: implemented, used primarily in the standalone 3-agent pipeline.
- **StructurerAgent**: currently a placeholder that returns empty structures. It is **not** used for production registry extraction.

## Agent Contracts

All contracts are defined in `modules/agents/contracts.py`:

### Common Types

```python
class AgentWarning(BaseModel):
    """Non-blocking warning from an agent."""
    code: str           # e.g., "MISSING_HEADER", "AMBIGUOUS_SECTION"
    message: str
    section: Optional[str] = None

class AgentError(BaseModel):
    """Error that may prevent successful output."""
    code: str           # e.g., "NO_SECTIONS_FOUND", "PARSING_FAILED"
    message: str
    section: Optional[str] = None

class Segment(BaseModel):
    """A segmented portion of the note."""
    id: str
    type: str           # "HISTORY", "PROCEDURE", "FINDINGS", etc.
    text: str
    start_char: Optional[int]
    end_char: Optional[int]
    spans: List[Tuple[int, int]]

class Entity(BaseModel):
    """An extracted entity (e.g., EBUS station, stent type)."""
    label: str
    value: str
    name: str
    type: str
    offsets: Optional[Tuple[int, int]]
    evidence_segment_id: Optional[str]
    attributes: Optional[Dict[str, Any]]

class Trace(BaseModel):
    """Debugging metadata for agent output."""
    trigger_phrases: List[str]
    rule_paths: List[str]
    confounders_checked: List[str]
    confidence: float
    notes: Optional[str]
```

### Parser Contracts

```python
class ParserIn(BaseModel):
    """Input to Parser agent."""
    note_id: str
    raw_text: str

class ParserOut(BaseModel):
    """Output from Parser agent."""
    note_id: str
    segments: List[Segment]      # Extracted segments
    entities: List[Entity]       # Extracted entities
    trace: Trace
    warnings: List[AgentWarning]
    errors: List[AgentError]
    status: Literal["ok", "degraded", "failed"]
```

### Summarizer Contracts

```python
class SummarizerIn(BaseModel):
    """Input to Summarizer agent."""
    parser_out: ParserOut

class SummarizerOut(BaseModel):
    """Output from Summarizer agent."""
    note_id: str
    summaries: Dict[str, str]    # Section -> summary mapping
    caveats: List[str]           # Important notes/caveats
    trace: Trace
    warnings: List[AgentWarning]
    errors: List[AgentError]
    status: Literal["ok", "degraded", "failed"]
```

### Structurer Contracts

```python
class StructurerIn(BaseModel):
    """Input to Structurer agent."""
    summarizer_out: SummarizerOut

class StructurerOut(BaseModel):
    """Output from Structurer agent."""
    note_id: str
    registry: Dict[str, Any]     # Structured registry fields
    codes: Dict[str, Any]        # Generated CPT codes
    rationale: Dict[str, Any]    # Coding rationale
    trace: Trace
    warnings: List[AgentWarning]
    errors: List[AgentError]
    status: Literal["ok", "degraded", "failed"]
```

### Pipeline Result

```python
class PipelineResult(BaseModel):
    """Full result from running the 3-agent pipeline."""
    pipeline_status: Literal[
        "ok",
        "degraded",
        "failed_parser",
        "failed_summarizer",
        "failed_structurer"
    ]
    parser: Optional[ParserOut]
    summarizer: Optional[SummarizerOut]
    structurer: Optional[StructurerOut]
    registry: Optional[Dict[str, Any]]
    codes: Optional[Dict[str, Any]]
```

## Agent Implementations

### 1. ParserAgent

**Purpose:** Split raw procedure notes into structured segments and extract entities.

**Location:** `modules/agents/parser/parser_agent.py`

**Algorithm:**
1. Search for common section headings (HPI, History, Procedure, Findings, etc.)
2. Split text at heading boundaries
3. Create `Segment` objects with type, text, and character offsets
4. Fallback: treat entire note as single "full" segment if no headings found

**Recognized Headings:**
- HPI
- History
- Procedure
- Findings
- Sedation
- Complications
- Disposition

**Example Input:**
```python
ParserIn(
    note_id="note_001",
    raw_text="History: 65yo male with lung nodule.\nProcedure: Bronchoscopy with EBUS."
)
```

**Example Output:**
```python
ParserOut(
    note_id="note_001",
    segments=[
        Segment(type="History", text="65yo male with lung nodule.", ...),
        Segment(type="Procedure", text="Bronchoscopy with EBUS.", ...),
    ],
    entities=[],
    status="ok",
    trace=Trace(rule_paths=["parser.heading_split.v1"], ...)
)
```

### 2. SummarizerAgent

**Purpose:** Generate section summaries from parsed segments and entities.

**Location:** `modules/agents/summarizer/summarizer_agent.py`

**Algorithm:**
1. Iterate through segments from parser output
2. Generate concise summaries for each section type
3. Collect caveats (important notes requiring attention)
4. Handle missing or ambiguous sections gracefully

**Example Output:**
```python
SummarizerOut(
    note_id="note_001",
    summaries={
        "History": "65-year-old male evaluated for lung nodule",
        "Procedure": "EBUS bronchoscopy performed",
    },
    caveats=[],
    status="ok"
)
```

### 3. StructurerAgent

**Purpose:** Map summaries to structured registry fields and generate CPT codes.

**Location:** `modules/agents/structurer/structurer_agent.py`

**Algorithm:**
1. Extract demographic info from History summary
2. Identify procedures from Procedure summary
3. Map to registry schema fields
4. Generate appropriate CPT codes
5. Provide coding rationale

**Example Output:**
```python
StructurerOut(
    note_id="note_001",
    registry={
        "patient_demographics": {"age_years": 65, "gender": "Male"},
        "procedures_performed": {"linear_ebus": {"performed": True}},
    },
    codes={"cpt_codes": ["31652"]},
    rationale={"31652": "EBUS-TBNA performed"},
    status="ok"
)
```

## Pipeline Orchestration

The pipeline is orchestrated by `run_pipeline()` in `modules/agents/run_pipeline.py`:

```python
from modules.agents.run_pipeline import run_pipeline, run_pipeline_typed

# Dict interface
result = run_pipeline({"note_id": "123", "raw_text": "..."})

# Typed interface
result = run_pipeline_typed({"note_id": "123", "raw_text": "..."})
```

### Pipeline Flow

```
1. Parser
   ├── Success (ok) → Continue to Summarizer
   ├── Degraded → Continue with warning
   └── Failed → Return failed_parser result

2. Summarizer
   ├── Success (ok) → Continue to Structurer
   ├── Degraded → Continue with warning
   └── Failed → Return failed_summarizer result

3. Structurer
   ├── Success (ok) → Return ok result
   ├── Degraded → Return degraded result
   └── Failed → Return failed_structurer result
```

### Error Handling

Each agent stage is wrapped in error handling:
- Exceptions are caught and converted to `AgentError`
- Failed stages stop the pipeline
- Degraded stages continue with warnings
- Partial results are preserved for debugging

### Timing

Pipeline execution is timed using `observability.timing`:
- `pipeline.total` - Total pipeline time
- `pipeline.parser` - Parser stage time
- `pipeline.summarizer` - Summarizer stage time
- `pipeline.structurer` - Structurer stage time

## Usage Examples

### Basic Usage

```python
from modules.agents.run_pipeline import run_pipeline

note = {
    "note_id": "test_001",
    "raw_text": """
    History: 65-year-old male with 2cm RUL nodule.
    Procedure: EBUS bronchoscopy with TBNA of station 4R and 7.
    Findings: Lymph nodes appeared abnormal on ultrasound.
    Complications: None
    """
}

result = run_pipeline(note)

print(f"Status: {result['pipeline_status']}")
print(f"Registry: {result['registry']}")
print(f"Codes: {result['codes']}")
```

### Error Handling

```python
result = run_pipeline({"note_id": "123", "raw_text": ""})

if result["pipeline_status"].startswith("failed"):
    stage = result["pipeline_status"].split("_")[1]
    errors = result.get(stage, {}).get("errors", [])
    for error in errors:
        print(f"Error [{error['code']}]: {error['message']}")
```

### Accessing Intermediate Results

```python
result = run_pipeline_typed(note)

# Access parser output
for segment in result.parser.segments:
    print(f"Section: {segment.type}")
    print(f"Text: {segment.text[:100]}...")

# Access summarizer output
for section, summary in result.summarizer.summaries.items():
    print(f"{section}: {summary}")

# Access structurer output
print(f"Registry: {result.structurer.registry}")
print(f"Rationale: {result.structurer.rationale}")
```

## Extending the Pipeline

### Adding a New Agent

1. Create a new directory: `modules/agents/myagent/`
2. Define the agent class in `myagent_agent.py`:

```python
from modules.agents.contracts import MyAgentIn, MyAgentOut

class MyAgent:
    def run(self, input: MyAgentIn) -> MyAgentOut:
        # Implementation
        return MyAgentOut(...)
```

3. Add contracts to `contracts.py`:

```python
class MyAgentIn(BaseModel):
    ...

class MyAgentOut(BaseModel):
    status: Literal["ok", "degraded", "failed"]
    ...
```

4. Update `run_pipeline.py` to include the new stage.

### Customizing Existing Agents

Each agent can be subclassed or replaced:

```python
class CustomParserAgent(ParserAgent):
    def run(self, parser_in: ParserIn) -> ParserOut:
        # Custom implementation
        ...
```

## Best Practices

1. **Status Tracking**: Always set appropriate status (ok/degraded/failed)
2. **Error Collection**: Add errors with descriptive codes and messages
3. **Trace Metadata**: Include rule paths and trigger phrases for debugging
4. **Graceful Degradation**: Continue with warnings when possible
5. **Contract Compliance**: Always return valid contract objects

---

*Last updated: January 2026*
