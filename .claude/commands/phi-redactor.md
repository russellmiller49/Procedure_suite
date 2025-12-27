# PHI Redactor Development Skill

Use this skill when working on the PHI (Protected Health Information) redaction pipeline, including the client-side UI, veto layer, ML model, or training data.

## Architecture Overview

The PHI redactor is a **hybrid client-side detection system** combining:
1. **ML Detection** (DistilBERT via Transformers.js) - Probabilistic PHI detection
2. **Regex Detection** - Deterministic header/pattern matching
3. **Veto Layer** - Post-processing filter to prevent false positives

```
Input Text
    ↓
[Windowed Processing: 2500 chars, 250 overlap]
    ↓
ML NER (DistilBERT) + Regex Patterns
    ↓
Merge Overlaps (prefer regex)
    ↓
Expand to Word Boundaries
    ↓
Apply Veto Layer (protectedVeto.js)
    ↓
Final Detections
```

## Key Files

### Client-Side UI (Browser)
| File | Purpose |
|------|---------|
| `modules/api/static/phi_redactor/redactor.worker.js` | Web Worker for ML inference + regex detection |
| `modules/api/static/phi_redactor/protectedVeto.js` | Veto/allow-list layer (prevents false positives) |
| `modules/api/static/phi_redactor/app.js` | Main UI application (Monaco editor integration) |
| `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/` | ONNX model bundle |
| `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json` | Protected clinical terms config |

### Server-Side (Python)
| File | Purpose |
|------|---------|
| `modules/phi/adapters/phi_redactor_hybrid.py` | Server-side hybrid redactor |
| `modules/phi/adapters/presidio_scrubber.py` | Presidio-based scrubber |

### Training Pipeline
| File | Purpose |
|------|---------|
| `scripts/distill_phi_labels.py` | Silver: Piiranha → BIO token distillation |
| `scripts/sanitize_dataset.py` | Clean false positives from training data |
| `scripts/normalize_phi_labels.py` | Map labels to standard schema |
| `scripts/train_distilbert_ner.py` | Train DistilBERT NER model |
| `scripts/export_phi_model_for_transformersjs.py` | Export ONNX for browser |
| `scripts/audit_model_fp.py` | Audit for false positive violations |
| `scripts/prodigy_prepare_phi_batch.py` | Prodigy: Pre-annotate notes with DistilBERT |
| `scripts/prodigy_export_corrections.py` | Prodigy: Export corrections to BIO format |

### Training Data
| Location | Purpose |
|----------|---------|
| `data/ml_training/distilled_phi_labels.jsonl` | Raw Piiranha output |
| `data/ml_training/distilled_phi_CLEANED.jsonl` | Sanitized |
| `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl` | Normalized (training ready) |
| `data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl` | With Prodigy corrections merged |
| `data/ml_training/prodigy_batch.jsonl` | Current Prodigy annotation batch |
| `data/ml_training/prodigy_manifest.json` | Tracks annotated windows |
| `synthetic_phi.jsonl` | Dense synthetic PHI data (300 records) |

## PHI Label Schema

| Label | Description | Examples |
|-------|-------------|----------|
| PATIENT | Patient names | "John Smith", "Mrs. Jones" |
| DATE | Dates, DOB | "01/15/2024", "Jan 15" |
| ID | MRN, SSN, IDs | "MRN: 12345", "123-45-6789" |
| GEO | Addresses, locations | "New York", "123 Main St" |
| CONTACT | Phone, email | "555-123-4567" |
| O | Not PHI | (background) |

## Common Tasks

### 1. Fix False Positives (Over-Redaction)
Clinical terms being incorrectly redacted.

**Quick Fix (Veto Layer):**
Edit `protectedVeto.js`:
- Add to `STOPWORDS_ALWAYS` for single words
- Add to `CLINICAL_ALLOW_LIST` for clinical terms
- Add regex pattern for structured patterns (device models, durations)

**Example:**
```javascript
// In STOPWORDS_ALWAYS - add clinical verbs
"intubated", "identified", "placed", "transferred"

// In CLINICAL_ALLOW_LIST - add abbreviations
"ip", "d/c", "medical thoracoscopy"
```

### 2. Fix False Negatives (PHI Leaking)
Patient names or IDs not being detected.

**Quick Fix (Regex):**
Edit `redactor.worker.js`:
- Add new regex pattern for the pattern type
- Update `runRegexDetectors()` to process it
- Include provider exclusion logic if name-like

**Example:**
```javascript
const INLINE_PATIENT_NAME_RE = /\b([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(?:a\s+)?\d+-year-old/gi;
```

### 3. Retrain the Model (From Scratch)
When regex/veto isn't enough and you need fresh training data.

```bash
# 1. Distill new training data
make distill-phi-silver

# 2. Sanitize (remove false positives)
make sanitize-phi-silver

# 3. Normalize labels
make normalize-phi-silver

# 4. Train
python scripts/train_distilbert_ner.py --epochs 3

# 5. Evaluate
make eval-phi-client

# 6. Audit for violations
make audit-phi-client

# 7. Export to ONNX
make export-phi-client-model
```

### 4. Iterative Correction with Prodigy (Recommended)
Human-in-the-loop workflow using [Prodigy](https://prodi.gy/) for targeted improvements.

```bash
# Option A: From golden notes (random sample)
make prodigy-prepare

# Option B: From specific file (e.g., dense synthetic PHI)
make prodigy-prepare-file PRODIGY_INPUT_FILE=synthetic_phi.jsonl

# Launch Prodigy UI (opens at http://localhost:8080)
make prodigy-annotate

# After annotation, export corrections
make prodigy-export

# Fine-tune model (preserves learned weights - RECOMMENDED)
make prodigy-finetune PRODIGY_EPOCHS=2

# OR train from scratch (loses learned weights)
make prodigy-retrain

# Evaluate and export
make eval-phi-client
make export-phi-client-model
```

**Key Prodigy Files:**
| File | Purpose |
|------|---------|
| `scripts/prodigy_prepare_phi_batch.py` | Pre-annotate notes with DistilBERT |
| `scripts/prodigy_export_corrections.py` | Convert Prodigy → BIO training format |
| `data/ml_training/prodigy_manifest.json` | Track annotated windows |
| `synthetic_phi.jsonl` | Dense synthetic PHI data (300 records) |

**Tips:**
- Use `prodigy-finetune` (not `prodigy-retrain`) to preserve learned weights
- Drop dataset to re-annotate: `prodigy drop phi_corrections`
- Override epochs: `make prodigy-finetune PRODIGY_EPOCHS=3`
- Prodigy runs in system Python 3.12 (not conda)

### 5. Update Protected Terms Config
Edit `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json`:
- `anatomy_terms`: Anatomical terms to protect
- `device_manufacturers`: Company names that look like person names
- `protected_device_names`: Device names to protect
- `station_markers`: LN station context words
- `code_markers`: CPT/billing context words

## Debugging

### Console Logging
Enable debug mode in the UI:
```javascript
// In app.js WORKER_CONFIG
const WORKER_CONFIG = {
  debug: true,  // Enables console logging
  aiThreshold: 0.45,
  forceUnquantized: true,
};
```

### Check Veto Reasons
With debug enabled, check browser console for:
```
[VETO] reason "text" (LABEL score=0.xx)
```

Common veto reasons:
- `stopword` - Word in STOPWORDS_ALWAYS
- `anatomy_list` - In IP_SPECIFIC_ANATOMY
- `clinical_allow_list` - In CLINICAL_ALLOW_LIST
- `provider_role_or_credential` - Detected as provider name
- `device_model_number` - Matches device model pattern
- `passive_voice_verb` - Preceded by "was/were"

### Model Output Issues
If model returns 0 detections:
1. Check `[PHI] raw spans count: X` in console
2. If 0, model may have cold-start issue
3. Regex patterns should still catch header PHI
4. Try refreshing the page (re-initializes model)

## Testing

```bash
# Run PHI redactor UI tests
pytest tests/api/test_phi_redactor_ui.py -v

# Run PHI contract tests (if available)
pytest tests/test_phi_redaction_contract.py -v

# Audit for must-not-redact violations
make audit-phi-client
```

### Smoke Test Checklist
Paste this in the UI at `/ui/phi_redactor/`:

```
Patient: John Smith, 65-year-old male
MRN: 12345678
DOB: 01/15/1960

Attending: Dr. Laura Brennan
Assistant: Dr. Miguel Santos (Fellow)

Procedure: Rigid bronchoscopy with EBUS-TBNA of stations 4R, 7, 11L.
The patient was intubated with size 8.0 ETT. Navigation performed
using Pentax EB-1990i scope. Follow-up in 1-2wks.

Pathology showed adenocarcinoma at station 7.
```

**Expected:**
- REDACTED: "John Smith", "12345678", "01/15/1960"
- NOT REDACTED: "Dr. Laura Brennan", "Dr. Miguel Santos", "4R", "7", "11L", "intubated", "EB-1990i", "1-2wks", "adenocarcinoma"

## Common Patterns to Remember

### Provider Name Detection (Keep Visible)
The veto layer protects provider names when:
- Preceded by "Dr.", "Attending:", "Proceduralist:", etc.
- Followed by credentials: ", MD", ", RN", ", PhD"
- In attribution context: "performed by", "supervised by"

### Passive Voice Pattern
"was placed", "was identified" - the veto catches these via:
1. Check if preceded by "was/were/is/are/been/being"
2. Check if span ends in -ed/-en or is in STOPWORDS_ALWAYS
3. If both true, veto (don't redact)

### Device Model Numbers
Pattern: `EB-1990i`, `BF-H190`, `CV-180`
Regex: `/^(?:EB|BF|CV|EU|GIF|...)[-\s]?[A-Z0-9]{2,10}$/i`

### Duration Patterns
Pattern: `1-2wks`, `3-5 days`, `2hrs`
Regex: `/^\d+(?:-\d+)?\s*(?:wks?|days?|hrs?|...)$/i`

## Safety Requirements

**Post-veto must-not-redact violations MUST be 0.**

The audit script checks that these are never redacted:
- CPT codes (31653, 77012) in billing context
- LN stations (4R, 7, 11L) with station context
- Anatomical terms (Left Upper Lobe, RUL)
- Device names (Monarch, ION, PleurX)
- Clinical measurements (24 French, 5 ml)

Raw model violations may be non-zero; the veto layer guarantees safety.
