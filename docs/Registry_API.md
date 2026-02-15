# Registry API (Legacy)

This document describes **legacy** registry endpoints.

**Authoritative production endpoint:** `POST /api/v1/process` (see `app/api/routes/unified_process.py`).

**Experimental (multi-doc, ZK timelines):** `POST /api/v1/process_bundle` (see `app/api/routes/process_bundle.py`). This endpoint expects client-side temporal translation (`T±N` tokens) and rejects raw absolute date-like strings.

It also returns:
- `entity_ledger` (Phase 7)
- `relations_heuristic`, `relations_ml`, merged `relations` (Phase 8 shadow mode)
- `relations_warnings` + `relations_metrics` for evaluation (Phase 8)

The current production direction is **extraction-first** (registry extraction → deterministic Registry→CPT derivation) when `PROCSUITE_PIPELINE_MODE=extraction_first`.

## Endpoints

### POST `/api/registry/extract`

Extract registry fields from a procedure note using the hybrid-first pipeline.

**Pipeline Flow:**
1. **SmartHybridOrchestrator** determines CPT codes using ternary classification:
   - HIGH_CONF: ML + Rules fast path
   - GRAY_ZONE: Uses LLM for arbitration
   - LOW_CONF: LLM fallback
2. **CPT-to-Registry Mapping** converts codes to boolean registry flags
3. **RegistryEngine** extracts structured fields from note text
4. **Validation** performs CPT-registry consistency checks
5. Returns combined result with manual review flags if needed

**Request:**
```json
{
  "note_text": "The raw procedure note text..."
}
```

**Response:**
```json
{
  "record": {
    "procedure_type": "bronchoscopy",
    "procedures_performed": {
      "linear_ebus": true,
      "tbna_performed": true
    },
    ...
  },
  "cpt_codes": ["31652", "31622"],
  "coder_difficulty": "HIGH_CONF",
  "coder_source": "ml_rules_fastpath",
  "mapped_fields": {
    "procedures_performed.linear_ebus": true
  },
  "warnings": [],
  "needs_manual_review": false,
  "validation_errors": []
}
```

**Response Fields:**
- `record`: Extracted registry record fields
- `cpt_codes`: CPT codes identified by the hybrid coder
- `coder_difficulty`: Case difficulty (HIGH_CONF, GRAY_ZONE, or LOW_CONF)
- `coder_source`: Source of codes (ml_rules_fastpath or hybrid_llm_fallback)
- `mapped_fields`: Registry fields derived from CPT code mapping
- `warnings`: Non-blocking warnings about the extraction
- `needs_manual_review`: Whether this case requires human review
- `validation_errors`: Validation errors found during CPT-registry reconciliation

**Manual Review Triggers:**
- `coder_difficulty` is LOW_CONF or GRAY_ZONE
- Any validation errors detected (CPT code doesn't match registry field)

## Smoke Test

Test the endpoint with curl:

```bash
curl -X POST http://localhost:8000/api/registry/extract \
  -H "Content-Type: application/json" \
  -d '{
    "note_text": "PROCEDURE: EBUS-TBNA\n\nThe patient underwent linear EBUS with TBNA of stations 4R, 7, and 11L. Three lymph node stations were sampled. BAL was performed from the right middle lobe. No complications."
  }'
```

Expected response should include:
- `cpt_codes` containing `31653` (EBUS 3+ stations)
- `mapped_fields` with `procedures_performed.linear_ebus: true`
- `record.procedures_performed.linear_ebus` set to `true`

## Error Responses

| Status | Description |
|--------|-------------|
| 503 | Hybrid orchestrator not configured |
| 500 | Internal extraction error |

## Telemetry & Monitoring

The registry extraction service logs validation outcomes for monitoring. Each extraction logs:

```json
{
  "message": "registry_validation_complete",
  "coder_difficulty": "high_confidence",
  "coder_source": "ml_rules_fastpath",
  "needs_manual_review": false,
  "validation_error_count": 0,
  "warning_count": 0,
  "cpt_code_count": 2
}
```

Key metrics to monitor:
- `needs_manual_review=true` rate (target: < 20%)
- `validation_error_count > 0` rate (indicates CPT-registry mismatches)
- `coder_difficulty` distribution (HIGH_CONF should dominate)

## UI Integration

Once the API is stable, integrate with the frontend:

```javascript
// Example: Call registry extraction endpoint
async function extractRegistryFields(noteText) {
  const response = await fetch('/api/registry/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note_text: noteText }),
  });
  return response.json();
}

// Display in registry form
const result = await extractRegistryFields(noteText);

// Populate form fields from result.record
populateRegistryForm(result.record);

// Show manual review badge if needed
if (result.needs_manual_review) {
  showBadge('Manual Review Required', 'warning');
}

// Display validation errors as warnings
result.validation_errors.forEach(error => {
  showAlert(error, 'error');
});

// Show CPT codes for reference
displayCPTCodes(result.cpt_codes, result.coder_difficulty);
```

UI Components to Display:
- **Record Fields**: Pre-populate registry form from `result.record`
- **Manual Review Badge**: Show warning badge when `needs_manual_review=true`
- **Validation Errors**: Display as inline warnings/alerts
- **CPT Codes**: Show identified codes with difficulty indicator
- **Confidence Indicator**: Color-coded based on `coder_difficulty`

## Extraction Engine Modes

The registry extraction engine supports multiple modes via the `REGISTRY_EXTRACTION_ENGINE` environment variable:

| Mode | Description |
|------|-------------|
| `engine` | Legacy LLM-based extraction via RegistryEngine |
| `agents_focus_then_engine` | Focus/summarize note, then extract |
| `agents_structurer` | Structurer-first extraction (V3 event-log → `RegistryRecord`) |
| `parallel_ner` | **Recommended** (required in production): NER→Registry→Rules + ML safety net |

Default behavior when `REGISTRY_EXTRACTION_ENGINE` is **unset**:
- If `STRUCTURED_EXTRACTION_ENABLED=1` (default), the service will use `agents_structurer` when an LLM provider is configured, otherwise it uses `engine`.
- If `STRUCTURED_EXTRACTION_ENABLED=0`, the service uses `engine`.

### Parallel NER Mode

The `parallel_ner` mode implements extraction-first architecture using a trained NER model:

```
Text → [Path A: NER → Registry → Rules → Codes]
     → [Path B: ML Classification → Codes]
            ↓
     [Confidence Combiner + Review Flagger]
```

**Enable:**
```bash
export REGISTRY_EXTRACTION_ENGINE=parallel_ner
```

**Response includes additional metadata:**
```json
{
  "record": {...},
  "warnings": [...],
  "meta": {
    "extraction_engine": "parallel_ner",
    "parallel_pathway": {
      "path_a": {
        "source": "ner_rules",
        "codes": ["31653", "31624"],
        "ner_entity_count": 25,
        "stations_sampled_count": 3
      },
      "path_b": {
        "source": "ml_classification",
        "codes": ["31653"],
        "confidences": {"31653": 0.95}
      },
      "final_codes": ["31653", "31624"],
      "needs_review": false,
      "review_reasons": []
    }
  }
}
```

**Review flagging**: Cases are flagged for review when Path A (NER+Rules) and Path B (ML) disagree.

## Related Endpoints

- `POST /v1/registry/run` - Legacy registry extraction (RegistryEngine only)
- `POST /qa/run` - QA sandbox with registry, reporter, and coder modules
