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

---

## 🚀 Implementation Roadmap

### Phase 1: Data Augmentation & Prep (Local)

**Goal**: Turn ~160 "Golden" notes into a robust training set of 2,000–5,000 examples, fixing class imbalance.

**Tasks:**

1. **Run Augmentation Agent** (`scripts/augment_registry_data.py`)
   - Generate 10-20 variations for every rare case (e.g., `blvr`, `thermal_ablation`, `cryotherapy`)
   - Target: Every label has at least 50+ positive examples
   
2. **Finalize Data Splits** (`modules/ml_coder/data_prep.py`)
   - Generate `registry_train.csv` and `registry_test.csv`
   - **Critical**: Ensure "Edge Cases" are in the Test Set to verify the model generalizes, not memorizes

**Checklist:**
- [ ] Run `augment_registry_data.py` 
- [ ] Verify rare classes have 50+ examples each
- [ ] Generate train/test splits
- [ ] Confirm edge cases are in test set

---

### Phase 2: RoBERTa Student Training (Local - Fast Track)

**Goal**: Train a high-performance deep learning model without a teacher. This will likely be sufficient.

**Hardware/Environment:**
- **GPU**: RTX 4070 Ti (local)
- **Framework**: PyTorch with CUDA 11.8/12.1
- **Mixed Precision**: `fp16=True`

**Model Selection:**
- **Primary**: `pminervini/RoBERTa-base-PM-M3-Voc-hf` (PubMed/MIMIC vocabulary)
- **Alternative**: Distill-Align checkpoint with clinical vocabulary

**Training Script** (`scripts/train_roberta.py`):

```python
# Key configuration
model_name = "pminervini/RoBERTa-base-PM-M3-Voc-hf"
loss_function = BCEWithLogitsLoss(pos_weight=calculated_weights)
batch_size = 16  # or 32 depending on VRAM
fp16 = True

# CRITICAL: Calculate pos_weight for each label based on training data
# If "Stent" is rare (e.g., 5% positive), weight it ~19x higher
pos_weight = (num_negative / num_positive) for each label
```

**Success Criteria:**
- Macro F1 Score > 0.90 on `registry_test.csv`
- F1 > 0.85 on rare classes (BLVR, thermal ablation, cryotherapy)
- **If criteria met → SKIP Phase 3, proceed to Phase 4**

**Checklist:**
- [ ] Configure PyTorch with CUDA
- [ ] Implement `scripts/train_roberta.py`
- [ ] Calculate `pos_weight` for class imbalance
- [ ] Train model with fp16 mixed precision
- [ ] Evaluate Macro F1 on test set
- [ ] Evaluate F1 on rare classes specifically

---

### Phase 3: Teacher-Student Distillation (Cloud - CONDITIONAL)

> **Only execute if Phase 2 fails (Macro F1 < 0.85)**

**Goal**: Use a larger model to "teach" the smaller model through knowledge distillation.

**Steps:**

1. **Rent Cloud GPU** (~1 hour)
   - Options: Lambda Labs, AWS (A10G), RunPod
   - Target: NVIDIA A10G or A100

2. **Train Teacher Model**
   - Model: `RoBERTa-large-PM-M3-Voc` (larger variant)
   - Fine-tune on augmented training data

3. **Generate Soft Labels**
   - Run trained Teacher on Training Data
   - Save output logits: `teacher_logits.pt`

4. **Retrain Student (Local)**
   - Return to RTX 4070 Ti
   - Loss function: `0.5 * GroundTruthLoss + 0.5 * TeacherDistillationLoss`

**Checklist:**
- [ ] Spin up cloud GPU (if needed)
- [ ] Train teacher model
- [ ] Export soft labels to `teacher_logits.pt`
- [ ] Retrain student with distillation loss

---

### Phase 4: Rules Engine (Deterministic Logic)

**Goal**: Derive CPT codes from Registry flags deterministically—no ML guessing for the final coding step.

**Location**: `data/rules/coding_rules.py`

**Implementation Pattern:**

```python
# data/rules/coding_rules.py

def rule_31652(registry: dict) -> bool:
    """EBUS-TBNA, 1-2 stations."""
    return (
        registry.get("linear_ebus", False) and 
        1 <= registry.get("stations_sampled", 0) <= 2
    )

def rule_31653(registry: dict) -> bool:
    """EBUS-TBNA, 3+ stations."""
    return (
        registry.get("linear_ebus", False) and 
        registry.get("stations_sampled", 0) >= 3
    )

def rule_31625(registry: dict) -> bool:
    """Bronchoscopy with transbronchial biopsy."""
    return registry.get("transbronchial_biopsy", False)

def rule_31627(registry: dict) -> bool:
    """Navigation add-on (requires primary procedure)."""
    return registry.get("navigation_used", False)

def derive_all_codes(registry: dict) -> list[str]:
    """Master function to derive all applicable CPT codes."""
    codes = []
    
    # EBUS (mutually exclusive)
    if rule_31653(registry):
        codes.append("31653")
    elif rule_31652(registry):
        codes.append("31652")
    
    # Biopsies
    if rule_31625(registry):
        codes.append("31625")
    
    # Add-ons (only if primary exists)
    if codes and rule_31627(registry):
        codes.append("31627")
    
    return codes
```

**Validation Process:**
1. Run all 5,000+ Golden Notes through the rules engine
2. Compare `Engine_CPT` vs. `Verified_CPT`
3. **Fix rules until 100% match on verified cases**

**Checklist:**
- [ ] Create `data/rules/coding_rules.py`
- [ ] Implement all CPT rule functions
- [ ] Create unit tests for each rule
- [ ] Validate against Golden Notes (target: 100% match)
- [ ] Document edge cases and exceptions

---

### Phase 5: Optimization & Deployment (Railway)

**Goal**: Deploy an optimized, cost-effective inference system on Railway Pro plan.

#### 5.1 Model Quantization (Local)

**Process:**
1. Convert trained PyTorch model (`.pt`) to **ONNX format**
2. Apply **INT8 quantization**

**Results:**
- Model size: ~350MB → ~80MB
- Inference speed: ~3x faster
- RAM usage: <500MB

**Script** (`scripts/quantize_to_onnx.py`):

```python
import torch
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

# Export to ONNX
torch.onnx.export(model, dummy_input, "registry_model.onnx")

# INT8 Quantization
quantize_dynamic(
    "registry_model.onnx",
    "registry_model_int8.onnx",
    weight_type=QuantType.QUInt8
)
```

#### 5.2 ONNX Inference Service

**Location**: `modules/registry/inference_onnx.py`

```python
# modules/registry/inference_onnx.py
import onnxruntime as ort
import numpy as np

class ONNXRegistryPredictor:
    """Lightweight ONNX-based registry prediction."""
    
    def __init__(self, model_path: str = "models/registry_model_int8.onnx"):
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
    
    def predict(self, text: str) -> dict:
        """Run inference on procedure note text."""
        # Tokenize and run inference
        inputs = self._preprocess(text)
        outputs = self.session.run(None, inputs)
        return self._postprocess(outputs)
```

#### 5.3 Railway Deployment

**Benefits of INT8 Model:**
- RAM usage: <500MB (leaves room for app + overhead)
- No GPU required (CPU inference sufficient)
- Avoids Railway overage charges
- Response time: <100ms typical

**Checklist:**
- [ ] Export model to ONNX format
- [ ] Apply INT8 quantization
- [ ] Verify quantized model accuracy (should be ~same as original)
- [ ] Create `modules/registry/inference_onnx.py`
- [ ] Test locally with ONNX runtime
- [ ] Deploy to Railway
- [ ] Monitor RAM usage and response times

---

## Summary Checklist

| Phase | Task | Status |
|-------|------|--------|
| 1 | Generate 2,000+ synthetic notes | [ ] |
| 1 | Finalize train/test splits | [ ] |
| 2 | Train `RoBERTa-base-PM-M3-Voc` on RTX 4070 Ti | [ ] |
| 2 | Achieve Macro F1 > 0.90 | [ ] |
| 3 | (Conditional) Teacher-student distillation | [ ] |
| 4 | Write deterministic CPT rule functions | [ ] |
| 4 | Validate rules against Golden Notes (100%) | [ ] |
| 5 | Convert model to ONNX INT8 | [ ] |
| 5 | Deploy to Railway | [ ] |

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
│   │   │   └── registry_coder.py      # Registry-based coder
│   │   └── domain/
│   │       └── smart_hybrid.py        # SmartHybridOrchestrator
│   ├── registry/
│   │   ├── application/
│   │   │   └── registry_service.py    # RegistryService - main entry point
│   │   ├── engine/
│   │   │   └── registry_engine.py     # LLM extraction logic
│   │   ├── inference_onnx.py          # NEW: ONNX inference service
│   │   └── ml/                        # Registry ML predictors
│   ├── agents/
│   │   ├── contracts.py               # Pydantic I/O schemas
│   │   ├── run_pipeline.py            # Pipeline orchestration
│   │   ├── parser/                    # ParserAgent
│   │   ├── summarizer/                # SummarizerAgent
│   │   └── structurer/                # StructurerAgent
│   ├── ml_coder/                      # ML-based CPT predictor
│   │   └── data_prep.py               # Train/test split generation
│   └── reporter/                      # Synoptic report generator
├── scripts/
│   ├── augment_registry_data.py       # Data augmentation for rare classes
│   ├── train_roberta.py               # RoBERTa training script
│   └── quantize_to_onnx.py            # ONNX conversion & quantization
├── data/
│   ├── knowledge/
│   │   ├── ip_coding_billing.v2_7.json  # CPT codes, RVUs, bundling rules
│   │   ├── IP_Registry.json             # Registry schema definition
│   │   └── golden_extractions/          # Training data
│   └── rules/
│       └── coding_rules.py            # Deterministic CPT derivation rules
├── models/
│   ├── registry_model.pt              # Trained PyTorch model
│   └── registry_model_int8.onnx       # Quantized ONNX model
├── schemas/
│   └── IP_Registry.json               # JSON Schema for validation
└── tests/
    ├── coder/
    ├── registry/
    ├── ml_coder/
    └── rules/                         # NEW: Rules engine tests
```

## Critical Development Rules

### 1. File Locations
- **ALWAYS** edit `modules/api/fastapi_app.py` — NOT `api/app.py` (deprecated)
- **ALWAYS** use `CodingService` from `modules/coder/application/coding_service.py`
- **ALWAYS** use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing.v2_7.json`
- Deterministic rules are at `data/rules/coding_rules.py`

### 2. Testing Requirements
- **ALWAYS** run `make test` before committing
- **ALWAYS** run `make preflight` for full validation
- Test commands:
  ```bash
  pytest tests/coder/ -v          # Coder tests
  pytest tests/registry/ -v       # Registry tests
  pytest tests/ml_coder/ -v       # ML coder tests
  pytest tests/rules/ -v          # Rules engine tests
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

### Rules Engine Test Pattern
```python
def test_rule_31653():
    """Test EBUS 3+ stations rule."""
    registry = {
        "linear_ebus": True,
        "stations_sampled": 4
    }
    assert rule_31653(registry) is True
    
    registry["stations_sampled"] = 2
    assert rule_31653(registry) is False

def test_rule_31652():
    """Test EBUS 1-2 stations rule."""
    registry = {
        "linear_ebus": True,
        "stations_sampled": 2
    }
    assert rule_31652(registry) is True
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

**ONNX inference issues:**
```bash
pip install onnxruntime  # CPU-only runtime
# or
pip install onnxruntime-gpu  # If GPU available
```

---

## Contact & Resources

- **Knowledge Base**: `data/knowledge/ip_coding_billing.v2_7.json`
- **Registry Schema**: `schemas/IP_Registry.json`
- **API Docs**: `docs/Registry_API.md`
- **CPT Reference**: `docs/REFERENCES.md`
- **Rules Engine**: `data/rules/coding_rules.py`

---

*Last updated: December 2025*
*Architecture: Extraction-First with RoBERTa ML + Deterministic Rules Engine*
*Deployment Target: Railway (ONNX INT8)*
