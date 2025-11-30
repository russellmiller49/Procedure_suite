# ML Feedback Loops Across the Procedure Suite

## Executive Summary

The ML feedback loop architecture can and **should** apply to all three modules, but with different purposes and priorities:

| Module | ML Value | Priority | Complexity |
|--------|----------|----------|------------|
| **Coder** | High - catch missed codes, validate rules | **P0** (Start here) | Medium |
| **Reporter** | Very High - improve completeness, reduce errors | **P1** (Next) | High |
| **Registry** | Medium - validate mappings, catch data quality issues | **P2** (Later) | Low |

The coder is the right place to start because:
1. Discrete, measurable outputs (codes are right or wrong)
2. Clear ground truth (human-reviewed codes)
3. Fastest feedback cycle

But the **reporter module may actually benefit MORE** from ML assistance because:
1. Natural language generation is where LLMs excel
2. Context extraction is error-prone with rules alone
3. Completeness gaps directly impact downstream coding

---

## Module-by-Module Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROCEDURE SUITE PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│   │   REPORTER   │ ───► │    CODER     │ ───► │   REGISTRY   │             │
│   │              │      │              │      │              │             │
│   │ Free text →  │      │ Structured → │      │ Codes →      │             │
│   │ Structured   │      │ CPT codes    │      │ Registry fmt │             │
│   └──────────────┘      └──────────────┘      └──────────────┘             │
│         │                     │                     │                       │
│         ▼                     ▼                     ▼                       │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│   │ ML Advisor:  │      │ ML Advisor:  │      │ ML Advisor:  │             │
│   │ - Extract    │      │ - Suggest    │      │ - Validate   │             │
│   │   missing    │      │   codes      │      │   mappings   │             │
│   │   fields     │      │ - Flag       │      │ - Check      │             │
│   │ - Suggest    │      │   errors     │      │   completeness│            │
│   │   values     │      │              │      │              │             │
│   └──────────────┘      └──────────────┘      └──────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. REPORTER MODULE: ML for Context Extraction

### Current State
The reporter module transforms free-text procedure notes into structured reports using:
- Template matching
- Gemini LLM for extraction
- Rule-based field validation

### The Problem
Based on our previous conversations, you mentioned the reporter is **"consistently missing context"**. This is a perfect ML improvement target because:

1. **Unstructured → Structured is inherently ML-suited**
2. **Context understanding requires reasoning**, not just pattern matching
3. **Field completeness directly impacts coding accuracy**

### ML Feedback Loop for Reporter

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REPORTER ML FEEDBACK LOOP                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INPUT                           OUTPUT                                    │
│   ┌─────────────────┐            ┌─────────────────┐                       │
│   │ Free-text note  │            │ Structured      │                       │
│   │ "EBUS performed │ ────────►  │ Report          │                       │
│   │  with sampling  │            │ {               │                       │
│   │  of 4R, 7..."   │            │   stations: [], │  ◄── MISSING!        │
│   └─────────────────┘            │   bal: null,    │  ◄── MISSING!        │
│                                  │   ...           │                       │
│                                  │ }               │                       │
│                                  └─────────────────┘                       │
│                                          │                                  │
│                                          ▼                                  │
│                                  ┌─────────────────┐                       │
│                                  │ CODER finds     │                       │
│                                  │ missing data    │                       │
│                                  │ when trying to  │                       │
│                                  │ assign codes    │                       │
│                                  └─────────────────┘                       │
│                                          │                                  │
│                                          ▼                                  │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                    REPORTER TRACE                                │      │
│   ├─────────────────────────────────────────────────────────────────┤      │
│   │ trace_id: "rpt-001"                                             │      │
│   │ input_text: "EBUS performed with sampling of 4R, 7..."          │      │
│   │ extracted_fields: {stations: [], bal: null}                     │      │
│   │ expected_fields: {stations: ["4R", "7"], bal: true}  ◄── GROUND │      │
│   │ extraction_model: "gemini-1.5-pro"                       TRUTH  │      │
│   │ extraction_prompt_version: "v2.3"                               │      │
│   │ field_completeness: 0.65                                        │      │
│   │ downstream_coding_impact: ["31653 missed due to no stations"]   │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                          │                                  │
│                                          ▼                                  │
│                                  ┌─────────────────┐                       │
│                                  │ IMPROVEMENTS    │                       │
│                                  ├─────────────────┤                       │
│                                  │ • Prompt tuning │                       │
│                                  │ • Schema updates│                       │
│                                  │ • Extraction    │                       │
│                                  │   fine-tuning   │                       │
│                                  └─────────────────┘                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Reporter Trace Model

```python
class ReporterTrace(BaseModel):
    """Trace for reporter module extractions."""
    
    # Identifiers
    trace_id: str
    timestamp: datetime
    report_id: Optional[str]
    
    # Input
    input_text: str
    input_source: str  # "free_text", "extractor_hints", "ehr_import"
    procedure_type_hint: Optional[str]
    
    # Extraction output
    extracted_fields: dict[str, Any]
    extraction_confidence: dict[str, float]
    extraction_model: str
    extraction_prompt_version: str
    
    # Quality metrics
    field_completeness: float  # 0.0 to 1.0
    missing_required_fields: list[str]
    low_confidence_fields: list[str]
    
    # Downstream impact (from coder)
    coding_gaps_due_to_extraction: list[str]
    
    # Ground truth (from human review)
    corrected_fields: Optional[dict[str, Any]]
    human_reviewed: bool
```

### What Reporter Can Learn

| Pattern | Detection | Improvement |
|---------|-----------|-------------|
| Missing EBUS stations | Coder can't determine 31652 vs 31653 | Improve station extraction prompt |
| Missing laterality | Coder can't apply -50 modifier | Add laterality extraction rules |
| Missing sedation times | Coder can't calculate 99152/99153 | Parse time patterns better |
| Missing device details | Registry incomplete | Expand device extraction schema |
| Incorrect procedure type | Wrong template used | Improve classification |

### Reporter-Specific Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Field Completeness | % of required fields extracted | >90% |
| Extraction Accuracy | % of extracted values correct | >95% |
| Downstream Impact | Coding errors caused by extraction gaps | <5% |
| Template Match Rate | % of reports matching correct template | >98% |

---

## 2. CODER MODULE: ML for Code Suggestions

### Current State
The coder transforms structured reports into CPT/HCPCS codes using:
- Rule-driven pipeline with `ip_golden_knowledge_v2_2.json`
- NCCI edit validation
- MER (Multiple Endoscopy Rule) logic
- Confidence scoring

### The Problem
You mentioned the coder is **"making mistakes"**. ML can help by:
1. Catching codes the rules miss
2. Flagging potentially incorrect codes
3. Identifying patterns in rule failures

### Why Coder is Priority 0

The coder is the best place to START the ML feedback loop because:

1. **Discrete outputs**: Codes are either right or wrong (easy to measure)
2. **Clear ground truth**: Human-reviewed codes are definitive
3. **Fast iteration**: Can test improvements on historical data
4. **Lower risk**: Advisor only suggests, rules still decide

*This is the system we've been designing throughout this conversation.*

### Coder-Specific Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Code Precision | % of assigned codes that are correct | >95% |
| Code Recall | % of correct codes that are assigned | >90% |
| Modifier Accuracy | % of modifiers correctly applied | >95% |
| NCCI Compliance | % of code pairs passing NCCI edits | 100% |

---

## 3. REGISTRY MODULE: ML for Data Validation

### Current State
The registry module transforms reports and codes into registry-ready bundles for:
- Supabase uploads
- External registry submissions
- Analytics pipelines

### The Problem
Registry errors are often **data quality issues** that slip through:
- Missing required fields for specific registries
- Incorrect mappings (CPT → registry-specific codes)
- Inconsistent formatting

### ML Value for Registry

Registry is **lower priority** for ML because:
1. Mappings are mostly deterministic
2. Errors are caught by downstream validation
3. Less complex than extraction or coding

But ML can still help with:
- **Anomaly detection**: Flag unusual patterns
- **Completeness validation**: Predict what fields are needed
- **Cross-registry consistency**: Ensure same procedure maps correctly to multiple registries

### Registry Trace Model

```python
class RegistryTrace(BaseModel):
    """Trace for registry export operations."""
    
    # Identifiers
    trace_id: str
    timestamp: datetime
    report_id: str
    
    # Input
    structured_report: dict
    assigned_codes: list[str]
    target_registry: str  # "aabip", "sts", "internal"
    
    # Output
    registry_bundle: dict
    export_format: str
    
    # Validation
    validation_errors: list[str]
    validation_warnings: list[str]
    field_completeness: float
    
    # Downstream
    submission_status: Optional[str]  # "success", "rejected", "pending"
    rejection_reasons: Optional[list[str]]
```

### Registry-Specific Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Export Success Rate | % of exports accepted by registry | >99% |
| Field Completeness | % of registry fields populated | >95% |
| Mapping Accuracy | % of code mappings correct | 100% |
| Validation Pass Rate | % passing pre-submission validation | >98% |

---

## Integrated Feedback Loop

The real power comes from **connecting all three modules**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTEGRATED FEEDBACK LOOP                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌──────────────────┐                                 │
│                        │   Free-Text      │                                 │
│                        │   Procedure Note │                                 │
│                        └────────┬─────────┘                                 │
│                                 │                                           │
│                                 ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                       REPORTER                                   │      │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │      │
│   │  │ Rule-based  │───►│ LLM Extract │───►│ Structured  │         │      │
│   │  │ Templates   │    │ (Gemini)    │    │ Report      │         │      │
│   │  └─────────────┘    └─────────────┘    └──────┬──────┘         │      │
│   │                                               │                 │      │
│   │  ◄──── ReporterTrace logs extraction ────────┘                 │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                 │                                           │
│                                 │ If extraction gaps found,                 │
│                                 │ trace links back to reporter              │
│                                 ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                        CODER                                     │      │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │      │
│   │  │ Rule Engine │───►│ ML Advisor  │───►│ CPT Codes   │         │      │
│   │  │ (Golden KB) │    │ (Gemini)    │    │ + Modifiers │         │      │
│   │  └─────────────┘    └─────────────┘    └──────┬──────┘         │      │
│   │                                               │                 │      │
│   │  ◄──── CodingTrace logs suggestions ─────────┘                 │      │
│   │                                                                 │      │
│   │  If code missed due to missing field:                          │      │
│   │  → Link to ReporterTrace                                        │      │
│   │  → Attribute error to extraction, not coding                    │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                 │                                           │
│                                 │ If registry rejects,                      │
│                                 │ trace links back to coder/reporter        │
│                                 ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                       REGISTRY                                   │      │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │      │
│   │  │ Mapping     │───►│ Validation  │───►│ Registry    │         │      │
│   │  │ Rules       │    │ (ML assist) │    │ Bundle      │         │      │
│   │  └─────────────┘    └─────────────┘    └──────┬──────┘         │      │
│   │                                               │                 │      │
│   │  ◄──── RegistryTrace logs exports ───────────┘                 │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌──────────────────┐                                 │
│                        │ HUMAN REVIEW     │                                 │
│                        │ (QA Sandbox)     │                                 │
│                        │                  │                                 │
│                        │ Reviews all three│                                 │
│                        │ stages together  │                                 │
│                        └────────┬─────────┘                                 │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌──────────────────┐                                 │
│                        │ UNIFIED TRACE    │                                 │
│                        │                  │                                 │
│                        │ Links:           │                                 │
│                        │ • Reporter trace │                                 │
│                        │ • Coding trace   │                                 │
│                        │ • Registry trace │                                 │
│                        │                  │                                 │
│                        │ Attributes errors│                                 │
│                        │ to correct stage │                                 │
│                        └────────┬─────────┘                                 │
│                                 │                                           │
│                                 ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                    EVALUATION ENGINE                             │      │
│   │                                                                  │      │
│   │  Analyzes traces to determine:                                  │      │
│   │  • Is this a REPORTER problem? (extraction gap)                 │      │
│   │  • Is this a CODER problem? (rule gap)                          │      │
│   │  • Is this a REGISTRY problem? (mapping gap)                    │      │
│   │                                                                  │      │
│   │  Routes improvements to correct module                          │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Error Attribution Example

```
SCENARIO: Code 31653 (EBUS 3+ stations) was missed

INVESTIGATION:
1. Check CodingTrace:
   - autocode_codes: ["31622"] (missing 31653)
   - advisor_candidate_codes: ["31622"] (also missed)
   
2. Check linked ReporterTrace:
   - extracted_fields.stations: []  ← EMPTY!
   - input_text: "EBUS with sampling of 4R, 7, and 11L"
   
3. ROOT CAUSE: Reporter failed to extract stations

ATTRIBUTION: Reporter error, not Coder error

ACTION: Improve station extraction in reporter prompts
```

---

## Recommended Implementation Order

### Phase 1: Coder ML (Months 1-4)
**Why first:** Easiest to measure, fastest feedback cycle

- [x] Design trace model (done)
- [x] Design advisor interface (done)
- [x] Design API endpoints (done)
- [ ] Deploy and collect traces
- [ ] First evaluation batch
- [ ] Initial improvements

### Phase 2: Reporter ML (Months 3-6)
**Why second:** Biggest impact on overall quality

- [ ] Design ReporterTrace model
- [ ] Add extraction confidence tracking
- [ ] Link reporter traces to coding traces
- [ ] Identify extraction gaps causing coding errors
- [ ] Improve extraction prompts
- [ ] Fine-tune extraction model

### Phase 3: Registry ML (Months 5-8)
**Why third:** Lower complexity, depends on upstream quality

- [ ] Design RegistryTrace model
- [ ] Add submission outcome tracking
- [ ] Link registry rejections to upstream causes
- [ ] Add validation ML advisor
- [ ] Improve mapping rules

### Phase 4: Integrated Loop (Months 7-12)
**Why last:** Requires all modules working

- [ ] Unified trace linking
- [ ] Cross-module error attribution
- [ ] Holistic evaluation dashboard
- [ ] End-to-end optimization

---

## Summary: Where ML Helps Most

| Module | ML Role | Impact |
|--------|---------|--------|
| **Reporter** | Extract missing context, suggest field values | **VERY HIGH** - LLMs excel at NLU |
| **Coder** | Suggest missed codes, validate rule outputs | **HIGH** - Clear feedback loop |
| **Registry** | Validate mappings, predict rejections | **MEDIUM** - Mostly deterministic |

### My Recommendation

1. **Start with Coder** (what we've been designing) because it's easiest to measure and iterate
2. **Add Reporter ML next** because extraction quality is the root cause of many coding errors
3. **Add Registry ML last** because it's lower impact and depends on upstream quality

The integrated loop is the ultimate goal, where a single trace can attribute errors to the correct module and route improvements automatically.

---

## Quick Wins for Reporter (If You Want to Start Now)

Even before building the full reporter ML loop, you can:

### 1. Add Extraction Confidence Scores
```python
# In reporter output
class ExtractionResult(BaseModel):
    fields: dict[str, Any]
    confidence: dict[str, float]  # Per-field confidence
    low_confidence_fields: list[str]  # Flag for review
```

### 2. Link Reporter Output to Coder Input
```python
# In coding trace
class CodingTrace(BaseModel):
    # ... existing fields ...
    
    # Link to reporter
    reporter_trace_id: Optional[str]
    extraction_gaps: list[str]  # Fields that were empty/uncertain
    coding_limited_by_extraction: bool
```

### 3. Track Extraction → Coding Impact
```python
# In evaluation
def attribute_coding_error(coding_trace, reporter_trace):
    """Determine if coding error was caused by extraction gap."""
    
    # Check if missed code required a field that wasn't extracted
    for missed_code in coding_trace.missed_codes:
        required_fields = CODE_REQUIRED_FIELDS[missed_code]
        for field in required_fields:
            if field in reporter_trace.missing_fields:
                return "reporter", f"{missed_code} missed due to missing {field}"
    
    return "coder", "Rule or advisor gap"
```

This gives you visibility into whether your problems are in extraction or coding, which helps prioritize improvements.
