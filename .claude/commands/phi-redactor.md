# PHI Redactor Development Skill

Use this skill when working on the PHI (Protected Health Information) redaction pipeline, including the client-side UI, veto layer, ML model, or training data.

## Architecture Overview

The PHI redactor is a **hybrid client-side detection system** combining:
1. **ML Detection** (DistilBERT via Transformers.js) - Probabilistic PHI detection
2. **Regex Detection** - Deterministic header/pattern matching
3. **Veto Layer** - Post-processing filter to prevent false positives

**Detection Mode:** Union (default) - Both ML and regex run, results combined, overlaps resolved after veto.

```
Input Text
    ↓
[Windowed Processing: 2500 chars, 250 overlap]
    ↓
ML NER (DistilBERT) + Regex Patterns  ← Union mode: both run
    ↓
Combine Results (dedupeSpans)
    ↓
Expand to Word Boundaries
    ↓
Apply Veto Layer (protectedVeto.js)
    ↓
Final Overlap Resolution
    ↓
Final Detections
```

## Key Files

### Client-Side UI (Browser)
| File | Purpose |
|------|---------|
| `modules/api/static/phi_redactor/redactor.worker.js` | Web Worker: ML inference + regex detection (union mode) |
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
| `scripts/export_phi_gold_standard.py` | Gold: Export pure Prodigy annotations |
| `scripts/split_phi_gold.py` | Gold: Train/test split with note grouping |

### Training Data
| Location | Purpose |
|----------|---------|
| `data/ml_training/phi_gold_standard_v1.jsonl` | **Gold Standard**: Pure Prodigy exports |
| `data/ml_training/phi_train_gold.jsonl` | Gold training set (80% of notes) |
| `data/ml_training/phi_test_gold.jsonl` | Gold test set (20% of notes) |
| `data/ml_training/ARCHIVE_distilled_phi_raw.jsonl` | Old mixed data (archived) |
| `data/ml_training/distilled_phi_labels.jsonl` | Raw Piiranha output |
| `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl` | Normalized silver data |
| `data/ml_training/prodigy_batch.jsonl` | Current Prodigy annotation batch |
| `data/ml_training/prodigy_manifest.json` | Tracks annotated windows |
| `synthetic_phi.jsonl` | Dense synthetic PHI data |

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

### 3. Gold Standard Training (RECOMMENDED)
Pure human-verified Prodigy annotations for highest quality.

```bash
# Full gold workflow (initial training or major updates)
make gold-export      # Export from Prodigy dataset
make gold-split       # 80/20 train/test split with note grouping
make gold-train       # Train with 10 epochs
make gold-audit       # Safety audit on test set
make gold-eval        # Evaluate F1 metrics

# Or run full cycle:
make gold-cycle

# Export to browser
make export-phi-client-model
```

**Key Files:**
- `phi_gold_standard_v1.jsonl` - Full gold export
- `phi_train_gold.jsonl` - Training set (80% of notes)
- `phi_test_gold.jsonl` - Test set (20% of notes)

### 4. Adding More Training Data (Incremental)
When you have new notes to add to gold training data.

```bash
# 1. Prepare new notes for Prodigy
make prodigy-prepare-file PRODIGY_INPUT_FILE=new_notes.jsonl PRODIGY_COUNT=50

# 2. Annotate in Prodigy UI
make prodigy-annotate

# 3. Incremental update (lighter than full train)
make gold-incremental   # export → split → finetune(3 epochs) → audit

# Or step-by-step:
make gold-export        # Re-export ALL gold (old + new)
make gold-split         # Re-split expanded dataset
make gold-finetune      # Light fine-tune (3 epochs, 5e-6 LR)
make gold-audit         # Verify safety

# Export to browser
make export-phi-client-model
```

**Override fine-tune epochs:**
```bash
make gold-finetune GOLD_FINETUNE_EPOCHS=5
```

### 5. Legacy Silver Training (From Scratch)
When starting fresh from Piiranha distillation.

```bash
# 1. Distill new training data
make distill-phi-silver

# 2. Sanitize (remove false positives)
make sanitize-phi-silver

# 3. Normalize labels
make normalize-phi-silver

# 4. Train
python scripts/train_distilbert_ner.py --epochs 3

# 5. Evaluate & audit
make eval-phi-client
make audit-phi-client

# 6. Export to ONNX
make export-phi-client-model
```

### 6. Prodigy Annotation Workflow
Human-in-the-loop using [Prodigy](https://prodi.gy/).

```bash
# Option A: From golden notes (random sample)
make prodigy-prepare PRODIGY_COUNT=100

# Option B: From specific file
make prodigy-prepare-file PRODIGY_INPUT_FILE=synthetic_phi.jsonl

# Launch Prodigy UI (opens at http://localhost:8080)
make prodigy-annotate

# After annotation, use gold workflow
make gold-export
make gold-split
make gold-finetune  # or gold-train for full training
```

**Prodigy Tips:**
- Prodigy runs in system Python 3.12 (not conda)
- Drop dataset to re-annotate: `prodigy drop phi_corrections`
- Check stats: `prodigy stats phi_corrections`

### 7. Update Protected Terms Config
Edit `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json`:
- `anatomy_terms`: Anatomical terms to protect
- `device_manufacturers`: Company names that look like person names
- `protected_device_names`: Device names to protect
- `station_markers`: LN station context words
- `code_markers`: CPT/billing context words

## Makefile Quick Reference

| Target | Description |
|--------|-------------|
| `gold-export` | Export pure gold from Prodigy |
| `gold-split` | 80/20 split with note grouping |
| `gold-train` | Full training (10 epochs, 1e-5 LR) |
| `gold-finetune` | Light fine-tune (3 epochs, 5e-6 LR) |
| `gold-audit` | Safety audit on gold test |
| `gold-eval` | Evaluate metrics on gold test |
| `gold-cycle` | Full: export → split → train → audit → eval |
| `gold-incremental` | Incremental: export → split → finetune → audit |
| `prodigy-prepare` | Prepare batch from golden folder |
| `prodigy-prepare-file` | Prepare batch from specific file |
| `prodigy-annotate` | Launch Prodigy UI |
| `audit-phi-client` | Audit on silver data |
| `export-phi-client-model` | Export ONNX for browser |

## Debugging

### Console Logging
Enable debug mode in the UI:
```javascript
// In app.js WORKER_CONFIG or via URL ?debug=1
const WORKER_CONFIG = {
  debug: true,  // Enables console logging
  aiThreshold: 0.45,
  forceUnquantized: true,
  mergeMode: "union",  // default: both ML + regex
};
```

### Check Detection Sources
With debug enabled:
```
[PHI] mergeMode: union
[PHI] mlSpans: X  regexSpans: Y
[PHI] afterVeto: Z
```

### Check Veto Reasons
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
3. Regex patterns should still catch header PHI (union mode)
4. Try refreshing the page (re-initializes model)

## Testing

```bash
# Audit for must-not-redact violations (gold test set)
make gold-audit

# Audit on silver data
make audit-phi-client

# Evaluate metrics
make gold-eval
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
