# Multi-Agent Pipeline Documentation

This document describes the 3-agent pipeline used for structured note processing in the Procedure Suite.

## Overview

The agents module (`modules/agents/`) implements a pipeline of three specialized agents that process procedure notes sequentially:

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

*Last updated: December 2025*
