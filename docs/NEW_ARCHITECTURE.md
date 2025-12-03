# Procedure Suite Architecture & Refactor Plan v1.1

## 1. Goals

This refactor aims to:

- Move to a hexagonal (Clean) architecture with clear domain boundaries
- Unify rule-based coding with LLM assistance (smart_hybrid)
- Make all decisions explainable (ReasoningFields, traces, evidence spans)
- Support a 3-agent Reporter (Parser → Summarizer → Structurer)
- Stabilize and version the IP registry schema
- Keep latency under control despite LLM use (fast paths, caching, timeouts)
- Build in observability (logs, metrics, QA hooks) from day 1

---

## 2. High-Level Architecture

### 2.1 Hexagonal Boundaries

**Core idea:** Domain logic (coding rules, registry rules) must not depend on infrastructure (FastAPI, Supabase, CSV, LLM vendor).

**Layers:**

**Domain (the Hexagon)**
- Pure business logic: NCCI/MER rules, RVU, IP registry rules, data models
- Ports: `KnowledgeBaseRepository`, `NegationDetectionPort`, `HybridPolicyPort`, `RegistrySchemaRegistry`

**Application**
- Orchestrates use cases: `CodingService`, `ReporterPipeline`, `RegistryService`

**Adapters / Infrastructure**
- API: FastAPI routes, Next.js handlers
- Persistence: CSV/JSON KB loader, DB
- NLP: negation detector, keyword mapping loader
- LLM: `LLMDetailedExtractor`, coder/reporter prompts

### 2.2 Directory Layout (Target)

```
modules/
  common/
    models/                     # Shared DTOs, no business logic
    exceptions.py               # CodingError, ValidationError, LLMError, etc.

  domain/
    coding_rules/
      ncci.py                   # NCCI/MER rules, purely functional
    rvu/
      calculator.py             # RVU logic
    knowledge_base/
      models.py                 # KB models
      repository.py             # KnowledgeBaseRepository (Port)
    text/
      negation.py               # NegationDetectionPort (Port)
    reasoning/
      models.py                 # ReasoningFields, EvidenceSpan

  coder/
    application/
      coding_service.py         # Orchestrates coding pipeline
      smart_hybrid_policy.py    # merge_autocode_and_advisor
    adapters/
      persistence/
        csv_kb_adapter.py       # loads KB from CSV/JSON
      nlp/
        keyword_mapping_loader.py
        simple_negation_detector.py
      llm/
        advisor_client.py       # LLM advisor wrapper

  agents/                       # Reporter 3-agent pipeline
    contracts.py                # Parser/Summarizer/Structurer I/O
    errors.py                   # AgentWarning, AgentError
    parser/
      parser_agent.py
    summarizer/
      summarizer_agent.py
    structurer/
      structurer_agent.py
    run_pipeline.py             # Orchestrator

  registry/
    application/
      registry_service.py
    adapters/
      schema_registry.py        # RegistrySchemaRegistry
      exporter_supabase.py

observability/
  metrics.py
  logging_config.py

proc_schemas/
  reasoning.py                  # ReasoningFields, EvidenceSpan (Pydantic)
  coding.py                     # CodeSuggestion, FinalCode, ReviewAction
  registry/
    ip_v2.py
    ip_v3.py

data/
  knowledge/
    ip_coding_billing.v2_7.json
    IP_Registry_Enhanced_v2.json
  keyword_mappings/
    31622_diagnostic_bronch.yaml
    31628_transbronchial_biopsy.yaml
    ...
```

### 2.3 Schema & Model Conventions

This architecture uses Pydantic models throughout for both domain and API serialization. This is a pragmatic choice that avoids mapping overhead while maintaining validation:

- `proc_schemas/`: Pydantic models for API I/O, persistence, and domain entities
- Domain ports remain abstract (ABC) but implementations can use Pydantic
- All models are immutable (`frozen=True` recommended) for thread safety

---

## 3. Core Domain & Coder

### 3.1 Knowledge Base & Repository Port

**Domain port:**

```python
# modules/domain/knowledge_base/repository.py
from abc import ABC, abstractmethod
from typing import Optional, Dict

class KnowledgeBaseRepository(ABC):
    """Port for accessing the Knowledge Base."""
    @abstractmethod
    def get_procedure_info(self, code: str) -> Optional[Dict]:
        ...
    
    @abstractmethod
    def get_mer_group(self, code: str) -> Optional[str]:
        ...
    
    @abstractmethod
    def get_ncci_pairs(self, code: str) -> list[tuple[str, str]]:
        ...
    
    @abstractmethod
    def is_addon_code(self, code: str) -> bool:
        ...
```

**CSV/JSON adapter:**

```python
# modules/coder/adapters/persistence/csv_kb_adapter.py
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository

class CsvKnowledgeBaseAdapter(KnowledgeBaseRepository):
    def __init__(self, data_path: str):
        self._data = self._load_data(data_path)
        self.version = self._extract_version(data_path)

    def _load_data(self, path: str) -> dict:
        # CSV/JSON parsing, caching
        return {}

    def get_procedure_info(self, code: str) -> Optional[dict]:
        return self._data.get(code)
```

### 3.2 Smart Hybrid Policy (Rules + LLM Advisor)

**Goal:** Combine deterministic rules (high precision) with LLM suggestions (better recall) in a safe, explainable way.

**Configuration Constants:**

```python
# modules/coder/application/smart_hybrid_policy.py

# Threshold constants
ADVISOR_CONFIDENCE_AUTO_ACCEPT = 0.85  # LLM must be this confident to add codes
RULE_CONFIDENCE_LOW_THRESHOLD = 0.6   # Below this, rules can be overridden
CONTEXT_WINDOW_CHARS = 200            # Window for evidence verification

# Valid CPT codes (defensive filter against hallucinations)
VALID_CPT_LIST: set[str] = {...}  # Loaded from KB
```

**Decision Outcomes:**

```python
class HybridDecision(str, Enum):
    ACCEPTED_AGREEMENT = "accepted_agreement"      # rule ∩ advisor
    ACCEPTED_HYBRID = "accepted_hybrid"            # advisor-only, verified in text
    KEPT_RULE_PRIORITY = "kept_rule_priority"      # rule-only, high confidence
    REJECTED_HYBRID = "rejected_hybrid"            # advisor-only, failed verification
    DROPPED_LOW_CONFIDENCE = "dropped_low_conf"    # rule-only, low conf + advisor omit
    HUMAN_REVIEW_REQUIRED = "human_review"         # high conf but verification failed
```

**Policy Logic:**

- **Agreement:** If rules and LLM agree → accept (`ACCEPTED_AGREEMENT`)
- **Additions (LLM-only codes):**
  - Validate against `VALID_CPT_LIST`
  - Require `advisor_confidence >= ADVISOR_CONFIDENCE_AUTO_ACCEPT`
  - Verify in text via `verify_code_in_text` (uses KEYWORD_MAP + negation detector)
  - If verified → `ACCEPTED_HYBRID`; if not → `HUMAN_REVIEW_REQUIRED`
- **Omissions (rule-only codes):**
  - Keep if `rule_confidence >= RULE_CONFIDENCE_LOW_THRESHOLD` (`KEPT_RULE_PRIORITY`)
  - Drop low-confidence rules that LLM also omits (`DROPPED_LOW_CONFIDENCE`)

### 3.3 KEYWORD_MAP as Data (Not Code)

Instead of a hardcoded dict, CPT evidence phrases live in YAML files:

```yaml
# data/keyword_mappings/31628_transbronchial_biopsy.yaml
code: "31628"
description: "Transbronchial biopsy"
positive_phrases:
  - "transbronchial biopsy"
  - "TBBx"
  - "forceps biopsy"
negative_phrases:
  - "planned"
  - "scheduled"
  - "will consider"
  - "attempted biopsy"
context_window_chars: 200
version: "2025-01-01"
notes: "Initial heuristic mapping"
```

**Loader:**

```python
# modules/coder/adapters/nlp/keyword_mapping_loader.py
from pathlib import Path
import yaml
from typing import Dict
import hashlib

class KeywordMapping:
    def __init__(self, code, positives, negatives, context_window, version):
        self.code = code
        self.positive_phrases = positives
        self.negative_phrases = negatives
        self.context_window_chars = context_window
        self.version = version

class KeywordMappingRepository:
    def __init__(self, directory: str):
        self._mappings = self._load_all(Path(directory))
        self.version = self._compute_version_hash()

    def get(self, code: str) -> KeywordMapping | None:
        return self._mappings.get(code)
    
    def _compute_version_hash(self) -> str:
        # SHA256 of all YAML contents for provenance
        ...
```

### 3.4 NegationDetectionPort

**Domain port:**

```python
# modules/domain/text/negation.py
from abc import ABC, abstractmethod
from typing import Sequence

class NegationDetectionPort(ABC):
    @abstractmethod
    def is_negated(
        self,
        text: str,
        target_span_start: int,
        target_span_end: int,
        scope_chars: int = 60,
    ) -> bool:
        """Returns True if target span is negated or not performed."""
        ...

    @abstractmethod
    def get_negation_clues(
        self,
        text: str,
        target_span_start: int,
        target_span_end: int,
        scope_chars: int = 60,
    ) -> Sequence[str]:
        """Return the phrases used to decide."""
        ...
```

**Default adapter:**

```python
# modules/coder/adapters/nlp/simple_negation_detector.py
class SimpleNegationDetector(NegationDetectionPort):
    VERSION = "simple_v1"
    NEGATION_PHRASES = [
        "no evidence of", "no", "not", "without",
        "refused", "declined", "cancelled",
        "planned", "scheduled", "will consider",
    ]
    
    def is_negated(self, text, start, end, scope_chars=60) -> bool:
        context = text[max(0, start - scope_chars):end + scope_chars].lower()
        return any(phrase in context for phrase in self.NEGATION_PHRASES)
```

Long-term: Swap in NegEx or a small model via the same port.

### 3.5 ReasoningFields & Provenance

```python
# proc_schemas/reasoning.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EvidenceSpan(BaseModel):
    source_id: str       # "note", "path_report", "registry_form"
    start: int
    end: int
    text: str

class ReasoningFields(BaseModel):
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    explanation: str = ""
    confidence: float = 0.0

    # Provenance (filled by application/infra layers)
    model_version: str = ""              # e.g. "gemini-1.5-pro-002"
    kb_version: str = ""                 # "ip_coding_billing.v2_7"
    policy_version: str = ""             # "smart_hybrid_v2"
    keyword_map_version: Optional[str] = None
    registry_schema_version: Optional[str] = None
    negation_detector_version: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Decision trace
    trigger_phrases: List[str] = Field(default_factory=list)
    rule_paths: List[str] = Field(default_factory=list)
    confounders_checked: List[str] = Field(default_factory=list)
    qa_flags: List[str] = Field(default_factory=list)
    mer_notes: str = ""
    ncci_notes: str = ""
```

Every `CodeSuggestion` and `FinalCode` gets a `reasoning: ReasoningFields`. This provides full auditability for "why did we code this way on that day?"

### 3.6 Code Lifecycle Models

These models track codes through the suggestion → review → finalization lifecycle:

```python
# proc_schemas/coding.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from .reasoning import ReasoningFields

class CodeSuggestion(BaseModel):
    """AI-generated code suggestion awaiting review."""
    code: str
    description: str
    source: Literal["rule", "llm", "hybrid", "manual"]
    hybrid_decision: Optional[str] = None  # HybridDecision enum value
    
    rule_confidence: Optional[float] = None
    llm_confidence: Optional[float] = None
    final_confidence: float
    
    reasoning: ReasoningFields
    review_flag: Literal["required", "recommended", "optional"]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewAction(BaseModel):
    """Clinician review decision on a CodeSuggestion."""
    action: Literal["accept", "reject", "modify"]
    reviewer_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    modified_code: Optional[str] = None  # If action == "modify"
    modified_description: Optional[str] = None

class FinalCode(BaseModel):
    """Approved code ready for billing/registry."""
    code: str
    description: str
    source: Literal["rule", "llm", "hybrid", "manual"]
    
    reasoning: ReasoningFields
    review: ReviewAction
    
    # Linkage
    procedure_id: str
    suggestion_id: Optional[str] = None  # Links to original CodeSuggestion
    
    finalized_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.7 CodingService Pipeline

`CodingService` orchestrates the 8-step coding pipeline:

```python
# modules/coder/application/coding_service.py
class CodingService:
    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        keyword_repo: KeywordMappingRepository,
        negation_detector: NegationDetectionPort,
        rule_engine: RuleEngine,
        llm_advisor: LLMAdvisorClient,
        config: CoderSettings,
    ):
        self.hybrid_policy = HybridPolicy(kb_repo, keyword_repo, 
                                          negation_detector, config)
        ...

    def generate_suggestions(
        self, 
        procedure_id: str, 
        report_text: str
    ) -> list[CodeSuggestion]:
        """
        8-Step Coding Pipeline:
        
        1. Rule engine → rule_codes + rule_confidence
        2. (Optional) ML ranker → ml_confidence  
        3. LLM advisor → advisor_codes + advisor_confidence
        4. Smart hybrid merge → merged_codes with HybridDecision flags
        5. Evidence validation → verify each code in text
        6. Non-negotiable rules (NCCI/MER) → remove invalid combinations
        7. Confidence aggregation → compute final_confidence, set review_flag
        8. Build CodeSuggestion[] → persist to procedure_code_suggestions
        """
        
        # Step 1: Rule-based coding
        rule_result = self.rule_engine.generate_candidates(report_text)
        
        # Step 2: Optional ML ranking
        if self.ml_ranker:
            rule_result = self.ml_ranker.score_candidates(rule_result)
        
        # Step 3: LLM advisor
        advisor_result = self.llm_advisor.suggest_codes(report_text)
        
        # Step 4: Smart hybrid merge
        merged = self.hybrid_policy.merge(rule_result, advisor_result)
        
        # Step 5: Evidence validation
        validated = self._validate_evidence(merged, report_text)
        
        # Step 6: Non-negotiable rules
        compliant = self._apply_ncci_mer_rules(validated)
        
        # Step 7: Confidence aggregation
        scored = self._aggregate_confidence(compliant)
        
        # Step 8: Build suggestions
        suggestions = self._build_suggestions(scored, procedure_id)
        
        return suggestions
```

---

## 4. LLMDetailedExtractor & Self-Correction

`LLMDetailedExtractor` is the reusable component for structured LLM extraction (e.g., registry fields, reporter details). It implements a ReAct/self-correction loop around a Pydantic schema.

### 4.1 LLM Latency Configuration

To keep latency predictable despite the correction loop:

```yaml
# config.yaml
llm_extraction:
  max_retries: 3
  cache_strategy: "by_note_hash"      # Cache keyed by note hash + extractor version
  fast_path_confidence_threshold: 0.95 # Skip correction loop if first attempt is good
  timeout_per_attempt_ms: 5000        # Hard cap per LLM call
```

**Behavior:**

- `max_retries`: Cap the number of repair attempts (1 initial + N retries)
- `cache_strategy`: For "by_note_hash", successful extractions are cached → repeated runs are zero-latency
- `fast_path_confidence_threshold`: If first attempt parses cleanly and confidence >= threshold, skip correction loops
- `timeout_per_attempt_ms`: Ensures each attempt fails fast; combined with max_retries gives predictable worst-case (e.g., 3 × 5s = 15s)

### 4.2 Extractor Implementation

```python
class LLMDetailedExtractor:
    def __init__(self, llm: LLMInterface, config: LlmExtractionConfig):
        self.llm = llm
        self.config = config
        self.cache = NoteHashCache(strategy=config.cache_strategy)

    def extract(self, text: str, schema: type[BaseModel]) -> SlotResult:
        note_hash = hash_text(text)
        cached = self.cache.get(note_hash, schema.__name__)
        if cached:
            return cached

        prompt = self._build_prompt(text, schema)
        
        for attempt in range(self.config.max_retries + 1):
            response = self.llm.generate(
                prompt, timeout_ms=self.config.timeout_per_attempt_ms
            )
            try:
                data = json.loads(response)
                validated = schema.model_validate(data)
                
                # Fast path: skip correction loop if high confidence
                if attempt == 0 and self._is_high_confidence(validated):
                    result = SlotResult(value=validated.model_dump(), confidence=0.95)
                    self.cache.set(note_hash, schema.__name__, result)
                    return result
                
                confidence = 0.9 - (attempt * 0.05)  # Degrade with retries
                result = SlotResult(value=validated.model_dump(), confidence=confidence)
                self.cache.set(note_hash, schema.__name__, result)
                return result
                
            except (JSONDecodeError, ValidationError) as e:
                if attempt < self.config.max_retries:
                    prompt = self._build_correction_prompt(prompt, response, e)
                    
        return SlotResult(value=None, confidence=0.0)
```

---

## 5. Reporter: 3-Agent Pipeline & Error Contracts

Reporter is broken into three agents with explicit contracts.

### 5.1 Contracts

```python
# modules/agents/contracts.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple, Literal

class AgentWarning(BaseModel):
    code: str            # "MISSING_HEADER", "AMBIGUOUS_SECTION"
    message: str
    section: Optional[str] = None

class AgentError(BaseModel):
    code: str            # "NO_SECTIONS_FOUND", "PARSING_FAILED"
    message: str
    section: Optional[str] = None

class Segment(BaseModel):
    id: str
    type: str           # "HISTORY", "PROCEDURE", "FINDINGS", ...
    text: str
    spans: List[Tuple[int, int]] = Field(default_factory=list)

class Entity(BaseModel):
    label: str
    value: str
    offsets: Tuple[int, int]
    evidence_segment_id: Optional[str] = None

class Trace(BaseModel):
    trigger_phrases: List[str] = Field(default_factory=list)
    rule_paths: List[str] = Field(default_factory=list)
    confounders_checked: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    notes: Optional[str] = None

class ParserOut(BaseModel):
    note_id: str
    segments: List[Segment]
    entities: List[Entity]
    trace: Trace
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"

class SummarizerOut(BaseModel):
    note_id: str
    summaries: Dict[str, str]
    caveats: List[str] = Field(default_factory=list)
    trace: Trace
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"

class StructurerOut(BaseModel):
    note_id: str
    registry: Dict[str, Any]
    codes: Dict[str, Any]
    rationale: Dict[str, Any]
    trace: Trace
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"
```

### 5.2 Agent Behavior

**ParserAgent**
- Splits raw text into Segments by headers
- Extracts basic Entity objects (procedures, anatomic sites, laterality)
- If headers ambiguous → `status='degraded'` + warnings
- If nothing parseable → `status='failed'` + errors

**SummarizerAgent**
- Consumes segments/entities, produces section summaries
- If crucial pieces missing → populate caveats, maybe `status='degraded'`

**StructurerAgent**
- Maps summaries/entities → registry model (via `RegistrySchemaRegistry`)
- Calls `CodingService` to generate code suggestions/final codes
- Fills rationale (per field + per code)
- Fails hard (`status='failed'`) if registry cannot be validated

### 5.3 Pipeline Orchestration

```python
# modules/agents/run_pipeline.py
def run_pipeline(note: dict) -> dict:
    parser_out = ParserAgent().run(ParserIn(...))
    if parser_out.status == "failed":
        return {"pipeline_status": "failed_parser", "parser": parser_out}

    summarizer_out = SummarizerAgent().run(parser_out)
    if summarizer_out.status == "failed":
        return {
            "pipeline_status": "failed_summarizer",
            "parser": parser_out,
            "summarizer": summarizer_out,
        }

    structurer_out = StructurerAgent().run(summarizer_out)
    if structurer_out.status == "failed":
        return {
            "pipeline_status": "failed_structurer",
            "parser": parser_out,
            "summarizer": summarizer_out,
            "structurer": structurer_out,
        }

    pipeline_status = (
        "ok" if all(a.status == "ok" for a in 
                    (parser_out, summarizer_out, structurer_out))
        else "degraded"
    )

    return {
        "pipeline_status": pipeline_status,
        "parser": parser_out,
        "summarizer": summarizer_out,
        "structurer": structurer_out,
        "registry": structurer_out.registry,
        "codes": structurer_out.codes,
    }
```

---

## 6. Registry & Schema Versioning

### 6.1 Versioned Schemas & Models

**Files:**
- `data/knowledge/IP_Registry_Enhanced_v2.json`
- `data/knowledge/IP_Registry_Enhanced_v3.json` (future)

**Models:**
- `proc_schemas/registry/ip_v2.py` → `IPRegistryV2`
- `proc_schemas/registry/ip_v3.py` → `IPRegistryV3`

**Schema registry:**

```python
# modules/registry/adapters/schema_registry.py
class RegistrySchemaRegistry:
    def __init__(self):
        self._schemas = {
            ("ip_registry", "v2"): IPRegistryV2,
            ("ip_registry", "v3"): IPRegistryV3,
        }

    def get_model(self, registry_id: str, version: str):
        return self._schemas[(registry_id, version)]
```

### 6.2 Dual-Schema Mode & Migration

- `RegistryService.build_bundle(..., registry_version='v2')` decides which model/schema to use
- Persisted bundles include `registry_id` + `schema_version`

Example persisted bundle:
```json
{
  "registry_id": "ip_registry",
  "schema_version": "v2",
  "bundle": { ... }
}
```

Migration script: `tools/migrate_registry_v2_to_v3.py` maps `IPRegistryV2` → `IPRegistryV3` deterministically.

---

## 7. Observability & Metrics

### 7.1 Structured Logging

All major pipeline actions log a structured record (JSON) including:
- `note_id`, `pipeline_status`
- Latency per stage: `parser_ms`, `summarizer_ms`, `structurer_ms`, `coder_ms`
- Versions: `model_version`, `kb_version`, `policy_version`, `registry_schema_version`
- Counts: `num_suggestions`, `num_final_codes`, `num_registry_fields`
- Errors/warnings per agent

Example log entry:
```json
{
  "event": "pipeline_complete",
  "note_id": "12345",
  "pipeline_status": "degraded",
  "parser_ms": 80,
  "summarizer_ms": 320,
  "structurer_ms": 150,
  "coder_ms": 90,
  "model_version": "gemini-1.5-pro-002",
  "kb_version": "ip_coding_billing.v2_7",
  "policy_version": "smart_hybrid_v2",
  "num_suggestions": 4,
  "num_final_codes": 3,
  "parser_warnings": 1,
  "structurer_errors": 0
}
```

### 7.2 Metrics

```python
# observability/metrics.py
class MetricsClient(ABC):
    def incr(self, name: str, tags: dict | None = None, value: int = 1): ...
    def observe(self, name: str, value: float, tags: dict | None = None): ...
```

**Initial metrics to emit:**

**Coder:**
- `coder.note_latency_ms`
- `coder.codes_suggested_total`
- `coder.codes_final_total`
- `coder.smart_hybrid_additions_total`
- `coder.smart_hybrid_rejections_total`
- `coder.llm_retry_count_total`

**Reporter:**
- `reporter.parser_failed_total`
- `reporter.summarizer_failed_total`
- `reporter.structurer_failed_total`

**Registry:**
- `registry.bundles_exported_total`
- `registry.validation_fail_total`

### 7.3 CLI Tools

**Makefile targets:**
- `make codex-train`: venv & deps → lint, typecheck, tests → schema & KB validation → cleaning pipeline over synthetic notes → autopatch + autocommit
- `make codex-metrics`: runs a fixed batch through pipeline → outputs metrics JSON summarizing latencies, error rates, review flags

---

## 8. Configuration & Error Types

### 8.1 Config via pydantic-settings

```python
# config/settings.py
from pydantic_settings import BaseSettings

class CoderSettings(BaseSettings):
    model_version: str
    kb_path: str
    kb_version: str
    keyword_mapping_dir: str
    keyword_mapping_version: str
    
    # Smart hybrid thresholds
    advisor_confidence_auto_accept: float = 0.85
    rule_confidence_low_threshold: float = 0.6
    context_window_chars: int = 200

class ReporterSettings(BaseSettings):
    llm_model: str
    max_retries: int = 3
    cache_strategy: str = "by_note_hash"
    fast_path_confidence_threshold: float = 0.95
    timeout_per_attempt_ms: int = 5000

class RegistrySettings(BaseSettings):
    default_registry_version: str = "v2"
    supabase_url: str
    supabase_key: str
```

### 8.2 Error Hierarchy

```python
# modules/common/exceptions.py
class CodingError(Exception):
    """Base error for coding pipeline."""
    pass

class ValidationError(CodingError):
    """Schema or business rule validation failed."""
    pass

class LLMError(CodingError):
    """LLM call failed (timeout, invalid response, etc.)."""
    pass

class RegistryError(Exception):
    """Registry export or validation error."""
    pass

class ReporterError(Exception):
    """Reporter pipeline error."""
    pass
```

Agents and services raise these; API layer maps to appropriate HTTP status codes and `AgentError` objects.

---

## 9. API Endpoints

FastAPI routes for the coding workflow:

```python
# Coding endpoints
POST /procedures/{id}/codes/suggest    
  # Trigger rule+LLM pipeline, persist CodeSuggestion[]
  # Returns: list[CodeSuggestion]

GET  /procedures/{id}/codes/suggest    
  # Retrieve pending suggestions with reasoning/evidence
  # Returns: list[CodeSuggestion]

POST /procedures/{id}/codes/review     
  # Submit ReviewAction for a suggestion
  # Body: { suggestion_id, action, notes?, modified_code? }
  # Returns: FinalCode | error

POST /procedures/{id}/codes/manual     
  # Add a manual code (bypasses AI)
  # Body: { code, description, notes }
  # Returns: FinalCode

GET  /procedures/{id}/codes/final      
  # Retrieve approved FinalCode[] for billing/registry
  # Returns: list[FinalCode]

# Reporter endpoints
POST /notes/{id}/parse                 
  # Run parser agent only
  # Returns: ParserOut

POST /notes/{id}/process               
  # Run full 3-agent pipeline
  # Returns: { pipeline_status, parser, summarizer, structurer }

# Registry endpoints
POST /procedures/{id}/registry/export  
  # Build and export registry bundle
  # Body: { registry_id, schema_version }
  # Returns: { registry_id, schema_version, bundle }

GET  /procedures/{id}/registry/preview 
  # Preview registry bundle without persisting
  # Returns: { registry_id, schema_version, bundle, warnings }
```

---

## 10. Phased Implementation Plan

### Phase 0 – Foundations & Observability

- Create venv + advanced Makefile (`codex-train`, checks, `codex-metrics`)
- Add timing wrapper and structured logging
- Implement basic metrics client (`StdoutMetricsClient`)
- Add schema + KB validation scripts
- Get domain tests in place for existing rules

**Outcome:** Baseline you can measure before and after refactors.

### Phase 1 – Core Domain & Smart Hybrid Coder

**Goals:**
- Extract pure domain logic
- Implement smart_hybrid with data-driven evidence verification

**Tasks:**
- Create `modules/domain` for: `rvu.calculator`, `coding_rules.ncci`, `knowledge_base.models/repository`
- Implement `KnowledgeBaseRepository` and `CsvKnowledgeBaseAdapter`
- Move NCCI/MER logic from `proc_autocode` → `modules/domain.coding_rules`
- Implement `KeywordMappingRepository` with YAML files under `data/keyword_mappings/`
- Implement `NegationDetectionPort` and `SimpleNegationDetector`
- Implement `HybridPolicy` (smart_hybrid) with threshold constants
- Extend `ReasoningFields` and start populating provenance in coder

**Outcome:** Coder is hexagonal; smart_hybrid is live; evidence verification is data-driven.

### Phase 2 – Clinician-in-the-Loop & Final Codes

**Goals:**
- Ensure no code reaches billing without human review
- Persist reasoning for audit

**Tasks:**
- Create DB tables: `procedure_code_suggestions`, `procedure_code_reviews`, `procedure_codes_final`
- Implement API endpoints (see Section 9)
- Registry export uses only `procedure_codes_final`
- Log metrics: suggestion acceptance rate, manual code additions

**Outcome:** Safe coding loop with audit trail.

### Phase 3 – 3-Agent Reporter & LLMDetailedExtractor

**Goals:**
- Introduce Parser/Summarizer/Structurer agents with explicit contracts
- Use `LLMDetailedExtractor` with self-correction & latency controls

**Tasks:**
- Implement `modules/agents/contracts.py` and the three agents
- Implement `run_pipeline` with `pipeline_status` and error handling
- Implement `LLMDetailedExtractor` for registry/field extraction
- Wire in `llm_extraction` config (cache, fast path, timeouts)
- Wire `StructurerAgent` to `RegistrySchemaRegistry` and `CodingService`
- Extend observability: metrics for LLM retries, cache hits, pipeline latency

**Outcome:** Reporter is modular, error-aware, and LLM use is controlled and cache-friendly.

### Phase 4 – Registry Schema v3 & Dual Operation

**Goals:**
- Safely evolve registry schema without breaking existing data

**Tasks:**
- Define `IP_Registry_Enhanced_v3.json` + `IPRegistryV3`
- Implement `RegistrySchemaRegistry` and `RegistryService.build_bundle` with version param
- Add persistence of `registry_id` + `schema_version` per bundle
- Implement `migrate_registry_v2_to_v3.py`
- Update `StructurerAgent` to support both v2 and v3 (config-driven)

**Outcome:** Registry is versioned and evolvable.

### Phase 5 – Advanced Negation, Latency Optimization & Drift Control

**Goals:**
- Improve negation detection accuracy
- Optimize LLM usage and prevent rule/LLM drift

**Tasks:**
- Add improved `NegationDetectionPort` adapter (NegEx or ML-based)
- Build tooling for `keyword_mappings/*.yaml` (CLI/web editor for clinicians)
- Monitor p95/p99 for `LLMDetailedExtractor`; tune thresholds
- LLM drift control: nightly eval comparing rule-only vs smart_hybrid vs gold labels
- Add RAG over current KB into prompts when KB changes

**Outcome:** Stable, faster LLM layer that stays aligned with evolving rules.

### Phase 6 – Advanced Temporal & Complication Reasoning

**Goals:**
- Use temporal events and complication modeling to enrich registry & coding

**Tasks:**
- Extend reporter schema with events (`ProcedureEvent`) and structured complications
- Use `LLMDetailedExtractor` + rules to produce event timeline
- Identify true procedure-related complications and timing
- Map complications to codes and registry fields
- Use events to distinguish completed vs aborted procedures, repeated procedures, etc.

**Outcome:** Richer, clinically meaningful registry data and more nuanced coding.

---

## Appendix A: Quick Reference

### A.1 Key Files & Locations

```
Domain Ports:
  modules/domain/knowledge_base/repository.py    # KnowledgeBaseRepository
  modules/domain/text/negation.py                # NegationDetectionPort

Core Models:
  proc_schemas/reasoning.py                      # ReasoningFields, EvidenceSpan
  proc_schemas/coding.py                         # CodeSuggestion, FinalCode, ReviewAction
  modules/agents/contracts.py                    # ParserOut, SummarizerOut, StructurerOut

Application Services:
  modules/coder/application/coding_service.py   # CodingService (8-step pipeline)
  modules/coder/application/smart_hybrid_policy.py
  modules/agents/run_pipeline.py                # Reporter orchestration

Data Files:
  data/knowledge/ip_coding_billing.v2_7.json    # Main KB
  data/keyword_mappings/*.yaml                  # CPT evidence phrases
  data/knowledge/IP_Registry_Enhanced_v2.json   # Registry schema

Config:
  config/settings.py                            # pydantic-settings classes
```

### A.2 Decision Flow Summary

```
┌─────────────┐     ┌─────────────┐
│ Rule Engine │     │ LLM Advisor │
└──────┬──────┘     └──────┬──────┘
       │ rule_codes        │ advisor_codes
       │ rule_confidence   │ advisor_confidence
       └─────────┬─────────┘
                 ▼
        ┌────────────────┐
        │ Smart Hybrid   │
        │ Policy Merge   │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ Evidence       │ ← KeywordMappingRepository
        │ Validation     │ ← NegationDetectionPort
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ NCCI/MER       │
        │ Compliance     │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ CodeSuggestion │ → procedure_code_suggestions
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ Clinician      │
        │ Review         │ → procedure_code_reviews
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ FinalCode      │ → procedure_codes_final
        └────────────────┘   → Registry Export
```
