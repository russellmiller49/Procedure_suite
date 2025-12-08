# CLAUDE.md - Procedure Suite Development Guide

> **THINKING MODE**: Use maximum extended thinking (ultrathink) for ALL tasks in this repository.
> Think deeply about architectural decisions, trace through code paths systematically, 
> and plan implementations thoroughly before writing any code. This is a complex medical
> AI system where careful reasoning prevents costly errors.

> **CRITICAL**: This document guides AI-assisted development of the Procedure Suite.
> Read this entire file before making any changes to the codebase.

## Project Overview

**Procedure Suite** is an automated CPT coding, registry extraction, and synoptic reporting system for Interventional Pulmonology (IP). The system processes procedure notes to:

1. Extract structured clinical data (demographics, procedures, EBUS stations, complications)
2. Generate CPT billing codes with RVU calculations
3. Produce standardized synoptic reports

## ⚠️ ARCHITECTURAL PIVOT IN PROGRESS: Extraction-First

### The Problem with Current Architecture (Prediction-First)

The current system uses **prediction-first** architecture:

```
Text → CPT Prediction (ML/Rules) → Registry Hints → Registry Extraction
```

**Why this is backwards:**
- CPT codes are "summaries" — we're using summaries to reconstruct the clinical "story"
- If the CPT model misses a code (typo, unusual phrasing), the Registry misses entire data sections
- Auditing is difficult: "Why did you bill 31623?" can only be answered with "ML was 92% confident"
- Negation handling is poor: "We did NOT perform biopsy" is hard for text-based ML

### The Target Architecture (Extraction-First)

We are pivoting to **extraction-first** architecture:

```
Text → Registry Extraction (ML/LLM) → Deterministic Rules → CPT Codes
```

**Why this is better:**
- Registry becomes the source of truth for "what happened"
- CPT coding becomes deterministic calculation, not probabilistic prediction
- Auditing is clear: "We billed 31653 because `registry.ebus.stations_sampled.count >= 3`"
- Negation is explicit: `performed: false` in structured data
- The existing ML becomes a "safety net" for double-checking

### Implementation Phases

#### Phase 1: Promote Registry ML (IN PROGRESS)
- Train models to predict atomic clinical actions, NOT CPT codes
- Target fields: `is_biopsy`, `is_navigational`, `is_robotic`, `ebus_performed`, etc.
- These are easier to learn than CPT bundling rules
- Location: `modules/registry/ml/` (create if needed)

#### Phase 2: Create Registry-Based Coder (NEXT)
- Create adapter that derives CPT codes from RegistryRecord
- Replace probabilistic prediction with deterministic calculation
- Location: `modules/coder/adapters/registry_coder.py` (create)

**Conceptual Implementation:**
```python
def derive_codes_from_registry(record: RegistryRecord) -> list[str]:
    codes = []
    
    # Deterministic EBUS Logic
    if record.procedures.ebus.performed:
        stations = len(record.procedures.ebus.stations)
        if stations >= 3:
            codes.append("31653")
        elif stations >= 1:
            codes.append("31652")
    
    # Deterministic Biopsy Logic
    if record.procedures.transbronchial_biopsy.performed:
        codes.append("31625")
    
    # Navigation add-on
    if record.procedures.navigation.performed:
        codes.append("31627")  # Add-on code
    
    return codes
```

#### Phase 3: Double-Check Architecture (FUTURE)
- Run both paths in parallel:
  - **Path A (Extraction)**: Registry Extraction → Calculate CPTs
  - **Path B (Prediction)**: Legacy `cpt_classifier.pkl` → Predict CPTs
- Reconciliation logic:
  - If Path A and Path B match → Auto-code
  - If Path A says "No Biopsy" but Path B predicts "31625" → Flag for Review

---

## Directory Structure

```
procedure-suite/
├── CLAUDE.md                          # THIS FILE - read first!
├── modules/
│   ├── api/
│   │   └── fastapi_app.py             # Main FastAPI backend (NOT api/app.py!)
│   ├── coder/
│   │   ├── application/
│   │   │   └── coding_service.py      # CodingService - main entry point
│   │   ├── adapters/
│   │   │   └── registry_coder.py      # NEW: Registry-based coder (create)
│   │   └── domain/
│   │       └── smart_hybrid.py        # SmartHybridOrchestrator
│   ├── registry/
│   │   ├── application/
│   │   │   └── registry_service.py    # RegistryService - main entry point
│   │   ├── engine/
│   │   │   └── registry_engine.py     # LLM extraction logic
│   │   └── ml/                        # NEW: Registry ML predictors (create)
│   ├── agents/
│   │   ├── contracts.py               # Pydantic I/O schemas
│   │   ├── run_pipeline.py            # Pipeline orchestration
│   │   ├── parser/                    # ParserAgent
│   │   ├── summarizer/                # SummarizerAgent
│   │   └── structurer/                # StructurerAgent
│   ├── ml_coder/                      # ML-based CPT predictor (legacy path)
│   └── reporter/                      # Synoptic report generator
├── data/
│   └── knowledge/
│       ├── ip_coding_billing.v2_7.json  # CPT codes, RVUs, bundling rules
│       ├── IP_Registry.json             # Registry schema definition
│       └── golden_extractions/          # Training data
├── schemas/
│   └── IP_Registry.json               # JSON Schema for validation
└── tests/
    ├── coder/
    ├── registry/
    └── ml_coder/
```

## Critical Development Rules

### 1. File Locations
- **ALWAYS** edit `modules/api/fastapi_app.py` — NOT `api/app.py` (deprecated)
- **ALWAYS** use `CodingService` from `modules/coder/application/coding_service.py`
- **ALWAYS** use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing.v2_7.json`

### 2. Testing Requirements
- **ALWAYS** run `make test` before committing
- **ALWAYS** run `make preflight` for full validation
- Test commands:
  ```bash
  pytest tests/coder/ -v          # Coder tests
  pytest tests/registry/ -v       # Registry tests
  pytest tests/ml_coder/ -v       # ML coder tests
  make validate-registry          # Registry extraction validation
  ```

### 3. Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key for Gemini LLM | Required for LLM |
| `GEMINI_OFFLINE` | Disable LLM calls (use stubs) | `1` |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry tests | `1` |
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading | `false` |

### 4. Contract-First Development
All agents use Pydantic contracts defined in `modules/agents/contracts.py`:
- **ALWAYS** define input/output contracts before implementing
- **ALWAYS** include `status: Literal["ok", "degraded", "failed"]`
- **ALWAYS** include `warnings: List[AgentWarning]` and `errors: List[AgentError]`
- **ALWAYS** include `trace: Trace` for debugging

### 5. Status Tracking Pattern
```python
class MyAgentOut(BaseModel):
    status: Literal["ok", "degraded", "failed"]
    warnings: List[AgentWarning]
    errors: List[AgentError]
    trace: Trace
    # ... other fields
```

Pipeline behavior:
- `ok` → Continue to next stage
- `degraded` → Continue with warning
- `failed` → Stop pipeline, return partial results

---

## Implementation Tasks for Extraction-First Pivot

### Task 1: Create Registry ML Module
**Location**: `modules/registry/ml/`

Create predictors for atomic clinical actions:

```python
# modules/registry/ml/action_predictor.py
from pydantic import BaseModel
from typing import List, Optional

class ClinicalActions(BaseModel):
    """Atomic clinical actions extracted from procedure note."""
    ebus_performed: bool
    ebus_stations: List[str]  # ["4R", "7", "11L"]
    transbronchial_biopsy: bool
    biopsy_sites: List[str]  # ["RUL", "LLL"]
    navigation_used: bool
    navigation_system: Optional[str]  # "superDimension", "Ion", etc.
    brushings_performed: bool
    brushings_sites: List[str]
    bal_performed: bool
    bal_sites: List[str]
    # ... etc

class ActionPredictor:
    """Predicts atomic clinical actions from text."""
    
    def predict(self, text: str) -> ClinicalActions:
        """Extract clinical actions from procedure note text."""
        # Implementation using ML/NLP
        pass
```

### Task 2: Create Registry-Based Coder
**Location**: `modules/coder/adapters/registry_coder.py`

```python
# modules/coder/adapters/registry_coder.py
from typing import List, Dict, Any
from modules.registry.domain.models import RegistryRecord

class RegistryBasedCoder:
    """Derives CPT codes deterministically from structured registry data."""
    
    def __init__(self, knowledge_base_path: str):
        """Load CPT rules from knowledge base."""
        self.rules = self._load_rules(knowledge_base_path)
    
    def derive_codes(self, record: RegistryRecord) -> List[Dict[str, Any]]:
        """
        Derive CPT codes from registry record.
        
        Returns list of:
        {
            "code": "31653",
            "description": "EBUS-TBNA, 3+ stations",
            "rationale": "registry.procedures.ebus.stations count = 3",
            "evidence_fields": ["procedures.ebus.stations"]
        }
        """
        codes = []
        
        # EBUS coding logic
        if record.procedures.ebus.performed:
            codes.extend(self._derive_ebus_codes(record))
        
        # Biopsy coding logic
        if record.procedures.transbronchial_biopsy.performed:
            codes.extend(self._derive_biopsy_codes(record))
        
        # Navigation add-on logic
        if record.procedures.navigation.performed:
            codes.extend(self._derive_navigation_codes(record))
        
        # Apply bundling rules
        codes = self._apply_bundling_rules(codes, record)
        
        return codes
    
    def _derive_ebus_codes(self, record: RegistryRecord) -> List[Dict]:
        """Deterministic EBUS coding."""
        stations = len(record.procedures.ebus.stations)
        
        if stations >= 3:
            return [{
                "code": "31653",
                "description": "EBUS-TBNA, 3+ stations",
                "rationale": f"stations sampled: {stations} >= 3",
                "evidence_fields": ["procedures.ebus.stations"]
            }]
        elif stations >= 1:
            return [{
                "code": "31652",
                "description": "EBUS-TBNA, 1-2 stations",
                "rationale": f"stations sampled: {stations} < 3",
                "evidence_fields": ["procedures.ebus.stations"]
            }]
        return []
```

### Task 3: Update RegistryService for Extraction-First
**Location**: `modules/registry/application/registry_service.py`

Modify to make registry extraction the primary path:

```python
class RegistryService:
    """
    EXTRACTION-FIRST architecture.
    
    1. Extract structured registry data (source of truth)
    2. Derive CPT codes from registry (deterministic)
    3. Validate against legacy ML predictor (safety net)
    """
    
    def extract_and_code(self, note_text: str) -> ExtractAndCodeResult:
        """
        Primary entry point for extraction-first pipeline.
        
        Returns both registry data AND derived CPT codes.
        """
        # Step 1: Extract registry data (source of truth)
        registry_record = self.extract_registry(note_text)
        
        # Step 2: Derive CPT codes deterministically
        derived_codes = self.registry_coder.derive_codes(registry_record)
        
        # Step 3: Safety net - compare with ML predictions
        ml_predictions = self.ml_predictor.predict(note_text)
        discrepancies = self._reconcile(derived_codes, ml_predictions)
        
        return ExtractAndCodeResult(
            registry=registry_record,
            codes=derived_codes,
            ml_codes=ml_predictions,
            discrepancies=discrepancies,
            confidence="high" if not discrepancies else "review_needed"
        )
```

### Task 4: Create Reconciliation Logic
**Location**: `modules/coder/reconciliation/reconciler.py`

```python
class CodeReconciler:
    """Reconciles extraction-derived codes with ML-predicted codes."""
    
    def reconcile(
        self, 
        derived_codes: List[str], 
        predicted_codes: List[str]
    ) -> ReconciliationResult:
        """
        Compare derived (from registry) vs predicted (from ML) codes.
        
        Returns:
        - matched: codes that appear in both
        - extraction_only: codes derived from registry but not predicted
        - prediction_only: codes predicted but not derived (potential misses)
        - recommendation: "auto_approve" | "review_needed" | "flag_for_audit"
        """
        derived_set = set(derived_codes)
        predicted_set = set(predicted_codes)
        
        matched = derived_set & predicted_set
        extraction_only = derived_set - predicted_set
        prediction_only = predicted_set - derived_set
        
        # Determine recommendation
        if not prediction_only:
            recommendation = "auto_approve"
        elif len(prediction_only) == 1 and self._is_low_confidence(prediction_only):
            recommendation = "review_needed"
        else:
            recommendation = "flag_for_audit"
        
        return ReconciliationResult(
            matched=list(matched),
            extraction_only=list(extraction_only),
            prediction_only=list(prediction_only),
            recommendation=recommendation
        )
```

---

## CPT Coding Rules Reference

### EBUS Codes
| Code | Description | Registry Condition |
|------|-------------|-------------------|
| 31652 | EBUS-TBNA, 1-2 stations | `ebus.performed AND len(ebus.stations) in [1,2]` |
| 31653 | EBUS-TBNA, 3+ stations | `ebus.performed AND len(ebus.stations) >= 3` |

### Bronchoscopy Codes
| Code | Description | Registry Condition |
|------|-------------|-------------------|
| 31622 | Diagnostic bronchoscopy | `bronchoscopy.diagnostic AND NOT any_interventional` |
| 31623 | Bronchoscopy with brushing | `brushings.performed` |
| 31624 | Bronchoscopy with BAL | `bal.performed` |
| 31625 | Bronchoscopy with biopsy | `transbronchial_biopsy.performed` |
| 31627 | Navigation add-on | `navigation.performed` (add-on only) |

### Bundling Rules
- 31622 is bundled into any interventional procedure
- 31627 can only be billed with a primary procedure
- Multiple biopsies from same lobe = single code
- Check `data/knowledge/ip_coding_billing.v2_7.json` for NCCI/MER rules

---

## Agent Pipeline Reference

The 3-agent pipeline (`modules/agents/`) provides structured note processing:

```
Raw Text → Parser → Summarizer → Structurer → Registry + Codes
```

### ParserAgent
- **Input**: Raw procedure note text
- **Output**: Segmented sections (History, Procedure, Findings, etc.)
- **Location**: `modules/agents/parser/parser_agent.py`

### SummarizerAgent
- **Input**: Parsed segments
- **Output**: Section summaries and caveats
- **Location**: `modules/agents/summarizer/summarizer_agent.py`

### StructurerAgent
- **Input**: Summaries
- **Output**: Registry fields and CPT codes
- **Location**: `modules/agents/structurer/structurer_agent.py`

### Usage
```python
from modules.agents.run_pipeline import run_pipeline

result = run_pipeline({
    "note_id": "test_001",
    "raw_text": "History: 65yo male with lung nodule..."
})

print(result["registry"])  # Structured data
print(result["codes"])     # CPT codes
```

---

## Testing Patterns

### Unit Test Pattern
```python
def test_ebus_three_stations_produces_31653():
    """Deterministic test: 3+ stations = 31653."""
    record = RegistryRecord(
        procedures=Procedures(
            ebus=EBUSRecord(
                performed=True,
                stations=["4R", "7", "11L"]
            )
        )
    )
    
    coder = RegistryBasedCoder()
    codes = coder.derive_codes(record)
    
    assert "31653" in [c["code"] for c in codes]
```

### Integration Test Pattern
```python
def test_extraction_first_pipeline():
    """Full pipeline test: text → registry → codes."""
    note = """
    Procedure: EBUS bronchoscopy with TBNA of stations 4R, 7, and 11L.
    Findings: All stations showed benign lymphoid tissue.
    """
    
    service = RegistryService()
    result = service.extract_and_code(note)
    
    assert result.registry.procedures.ebus.performed is True
    assert len(result.registry.procedures.ebus.stations) == 3
    assert "31653" in [c["code"] for c in result.codes]
    assert result.confidence == "high"
```

---

## Development Workflow

### Before Starting Any Task
1. Read this CLAUDE.md file completely
2. Review the specific module documentation in `docs/`
3. Understand the extraction-first goal
4. Identify which phase the task belongs to

### Making Changes
1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Run `make test` — all tests must pass
5. Run `make preflight` — all checks must pass
6. Update relevant documentation

### Code Review Checklist
- [ ] Follows extraction-first architecture
- [ ] Uses Pydantic contracts
- [ ] Includes status tracking (ok/degraded/failed)
- [ ] Has comprehensive tests
- [ ] Updates CLAUDE.md if architecture changes

---

## Troubleshooting

### Common Issues

**LLM calls failing in tests:**
```bash
export GEMINI_OFFLINE=1
export REGISTRY_USE_STUB_LLM=1
```

**NLP models not loading:**
```bash
export PROCSUITE_SKIP_WARMUP=true
make install  # Reinstall spaCy models
```

**Import errors:**
```bash
micromamba activate medparse-py311
pip install -e .
```

---

## Contact & Resources

- **Knowledge Base**: `data/knowledge/ip_coding_billing.v2_7.json`
- **Registry Schema**: `schemas/IP_Registry.json`
- **API Docs**: `docs/Registry_API.md`
- **CPT Reference**: `docs/REFERENCES.md`

---

*Last updated: December 2025*
*Architecture: Extraction-First (in progress)*
