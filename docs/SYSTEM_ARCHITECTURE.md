# Procedure Suite System Architecture

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Knowledge Base Files](#knowledge-base-files)
4. [Registry Cleaning Pipeline](#registry-cleaning-pipeline)
5. [API Endpoints](#api-endpoints)
6. [Frontend Integration](#frontend-integration)
7. [Supabase Integration](#supabase-integration)
8. [Railway Deployment](#railway-deployment)
9. [Local Development](#local-development)
10. [Configuration Reference](#configuration-reference)

---

## Overview

The Procedure Suite is a comprehensive system for:
- **Autonomous CPT coding** from procedure notes
- **Clinical registry extraction** using LLM
- **Structured report generation** from unstructured text
- **RVU/payment calculation** with NCCI bundling rules
- **Data quality validation** pipeline

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                            │
│         Interventional-Pulm-Education-Project                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ /qa-sandbox │  │ /qa-admin   │  │ /board-prep (education) │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────┘  │
└─────────┼────────────────┼──────────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                Next.js API Routes (/api/*)                       │
│  POST /api/qa/run  │  POST /api/qa/feedback  │  GET /api/qa/*   │
└─────────┬───────────────────────────────────────────────────────┘
          │
          ▼ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│              Python Backend (FastAPI on Railway)                 │
│                   Procedure_suite repo                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  modules/api/fastapi_app.py (port 8000)                  │   │
│  │  ├── POST /v1/coder/run     → EnhancedCPTCoder           │   │
│  │  ├── POST /v1/registry/run  → RegistryEngine             │   │
│  │  ├── POST /qa/run           → Combined QA endpoint       │   │
│  │  └── GET  /health           → Health check               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────▼──────────────────────────────┐   │
│  │                    Core Modules                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ proc_auto   │  │ modules/    │  │ proc_report/    │   │   │
│  │  │ code/       │  │ registry/   │  │ engine.py       │   │   │
│  │  │ coder.py    │  │ engine.py   │  │ (report gen)    │   │   │
│  │  │ (CPT coding)│  │ (extraction)│  │                 │   │   │
│  │  └──────┬──────┘  └──────┬──────┘  └─────────────────┘   │   │
│  │         │                │                                │   │
│  │         ▼                ▼                                │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │           Knowledge Base Layer                       │ │   │
│  │  │  ip_coding_billing.v2_7.json  │  IP_Registry.json   │ │   │
│  │  │  (CPT codes, RVUs, bundling)  │  (registry schema)  │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supabase (PostgreSQL)                         │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐  │
│  │ proc_qa_sessions    │  │ bronchoscopy_procedure           │  │
│  │ (QA test data)      │  │ bronchoscopy_specimens           │  │
│  │                     │  │ bronchoscopy_complications       │  │
│  └─────────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

### Procedure_suite (Python Backend)

```
Procedure_suite/
├── modules/                          # NEW - Active module architecture
│   ├── api/
│   │   ├── fastapi_app.py           # MAIN FastAPI app (USE THIS)
│   │   ├── schemas.py               # Request/response models
│   │   └── static/                  # Embedded UI (optional)
│   │
│   ├── registry/                    # LLM-driven registry extraction
│   │   ├── engine.py                # RegistryEngine orchestrator
│   │   ├── schema.py                # RegistryRecord model
│   │   └── extractors/              # Field extraction strategies
│   │
│   ├── registry_cleaning/           # Data quality pipeline
│   │   ├── logging_utils.py         # Issue tracking & CSV export
│   │   ├── schema_utils.py          # JSON schema normalization
│   │   ├── cpt_utils.py             # CPT code validation & bundling
│   │   ├── consistency_utils.py     # Cross-field validation
│   │   └── clinical_qc.py           # Clinical reasonableness checks
│   │
│   ├── coder/                       # High-level coder abstractions
│   │   ├── llm_coder.py             # LLM-based suggestions (Gemini)
│   │   └── schema.py                # CoderOutput, FinancialSummary
│   │
│   └── common/                      # Shared utilities
│       ├── knowledge.py             # KB loader with hot-reload
│       ├── llm.py                   # GeminiLLM client wrapper
│       └── rvu_calc.py              # RVU lookup wrapper
│
├── proc_autocode/                   # MAIN coder implementation
│   ├── coder.py                     # EnhancedCPTCoder (USE THIS)
│   ├── ip_kb/
│   │   ├── ip_kb.py                 # IPCodingKnowledgeBase class
│   │   ├── ip_coding_billing.v2_7.json  # Central knowledge base
│   │   └── canonical_rules.py       # Python bundling rules
│   └── rvu/
│       ├── rvu_calculator.py        # RVU + GPCI calculations
│       └── data/                    # RVU CSV files
│
├── proc_report/                     # Report composition
│   ├── engine.py                    # ReporterEngine
│   └── templates/                   # Jinja2 templates
│
├── proc_registry/                   # Database adapters
│   └── supabase_sink.py             # Supabase upsert logic
│
├── schemas/
│   └── IP_Registry.json             # Registry entry JSON schema
│
├── scripts/
│   ├── clean_ip_registry.py         # Registry cleaning CLI
│   └── devserver.sh                 # Dev server launcher
│
├── data/
│   └── samples/
│       └── my_registry_dump.jsonl   # Sample test data
│
├── tests/
│   └── test_clean_ip_registry.py    # Pipeline tests
│
├── _archive/                        # Archived old versions
│
├── .env                             # Environment variables
├── pyproject.toml                   # Project config
└── requirements.txt                 # Railway dependencies
```

### Key Directories

| Directory | Purpose | Status |
|-----------|---------|--------|
| `modules/api/` | FastAPI application | ACTIVE (main entry) |
| `modules/registry_cleaning/` | Data quality pipeline | ACTIVE |
| `proc_autocode/` | CPT coding engine | ACTIVE |
| `proc_autocode/ip_kb/` | Knowledge base files | ACTIVE |
| `api/` | Legacy FastAPI | DEPRECATED (do not use) |

---

## Knowledge Base Files

### 1. ip_coding_billing.v2_7.json

**Location:** `proc_autocode/ip_kb/ip_coding_billing.v2_7.json`

**Purpose:** Central knowledge base for IP coding, billing, and bundling rules.

**Structure:**
```json
{
  "version": "2.3",
  "metadata": {
    "updated_on": "2025-06-27",
    "source_documents": ["AABIP webinars", "Noah 2025", "Ion 2025", ...]
  },

  "fee_schedules": {
    "physician_2025_airway": {
      "codes": {
        "31622": {
          "description": "Bronchoscopy; diagnostic",
          "work_rvu": 2.53,
          "total_facility_rvu": 3.90,
          "mpfs_facility_payment": 126,
          "apc": "5153",
          "opps_payment": 1724
        },
        "31652": {
          "description": "Bronchoscopy; with EBUS sampling, 1-2 stations",
          "work_rvu": 4.46,
          "total_facility_rvu": 6.48,
          "mpfs_facility_payment": 210
        }
        // ... all bronchoscopy, pleural, thoracoscopy codes
      }
    }
  },

  "rvus": {
    "31622": {"work": 3.1, "pe": 6.0, "mp": 0.3},
    "31628": {"work": 4.2, "pe": 8.3, "mp": 0.4}
    // ... RVU components for calculation
  },

  "code_lists": {
    "bronchoscopy_diagnostic": ["31622"],
    "bronchoscopy_biopsy_parenchymal": ["31628"],
    "bronchoscopy_ebus_linear": ["31652", "31653"],
    "bronchoscopy_ebus_radial": ["+31654"],
    "bronchoscopy_navigation": ["+31627"],
    "pleural_drainage_codes": ["32556", "32557"],
    "thoracoscopy_diagnostic": ["32601", "32604", "32606", "32609"]
    // ... named groups for code lookup
  },

  "add_on_codes": ["+31627", "+31632", "+31633", "+31654", ...],

  "bundling_rules": {
    "diagnostic_with_surgical": {
      "drop_codes": ["31622"],
      "therapeutic_codes": ["31625", "31628", "31629", ...],
      "description": "Diagnostic bronchoscopy bundled into biopsy"
    },
    "tblbx_bundles_tbna_brush": {
      "dominant_codes": ["31628"],
      "drop_codes": ["31623", "31625", "31629"]
    }
    // ... auto-drop rules
  },

  "ncci_pairs": [
    {"primary": "31628", "secondary": "31622", "modifier_allowed": false},
    {"primary": "31636", "secondary": "31630", "modifier_allowed": true}
    // ... NCCI edit pairs
  ],

  "synonyms": {
    "navigation_terms": ["emn", "ion", "robotic", "superdimension"],
    "ebus_terms": ["ebus", "endobronchial ultrasound"],
    "tblb_terms": ["transbronchial lung biopsy", "tblb", "cryobiopsy"]
    // ... text matching synonyms
  }
}
```

**How It's Used:**

1. **Code Generation** (`IPCodingKnowledgeBase.groups_from_text()`):
   - Scans note text for synonyms
   - Returns matching code_lists groups
   - Generates candidate CPT codes

2. **Bundling Enforcement** (`CPTProcessor._apply_auto_drop_rules()`):
   - Checks `bundling_rules` for conflicts
   - Auto-drops bundled codes (e.g., 31622 when 31628 present)
   - Logs actions with reasons

3. **RVU Calculation** (`_calculate_total_rvu()`):
   - Looks up work, PE, MP from `rvus` section
   - Applies GPCI geographic adjustments
   - Returns total payment estimate

4. **NCCI Enforcement** (`_apply_ncci_pairs()`):
   - Checks all code pairs against `ncci_pairs`
   - Drops secondary if no modifier allowed
   - Flags for review if modifier present

---

### 2. IP_Registry.json

**Location:** `schemas/IP_Registry.json`

**Purpose:** JSON Schema defining valid registry entry structure.

**Key Sections:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "required": ["patient_mrn", "procedure_date", "attending_name", "data_entry_status"],

  "properties": {
    // Patient Demographics
    "patient_mrn": {"type": "string"},
    "patient_age": {"type": ["integer", "null"]},
    "gender": {"type": ["string", "null"], "enum": ["M", "F", "Other", null]},

    // Procedure Details
    "sedation_type": {"enum": ["Moderate", "General", "Local", "Monitored Anesthesia Care", null]},
    "airway_type": {"enum": ["Native", "ETT", "Tracheostomy", null]},
    "primary_indication": {"type": ["string", "null"]},

    // Billing
    "cpt_codes": {"type": ["array", "null"], "items": {"type": "string"}},
    "calculated_total_rvu": {"type": ["number", "null"]},

    // Complications
    "pneumothorax": {"type": ["boolean", "null"]},
    "bleeding_severity": {"type": ["string", "null"]},
    "disposition": {"type": ["string", "null"]}
  }
}
```

**How It's Used:**

1. **Schema Normalization** (`SchemaNormalizer`):
   - Validates entries against schema
   - Coerces types (string → int, boolean)
   - Normalizes enums ("Male" → "M", "mac" → "Monitored Anesthesia Care")

2. **Registry Extraction** (`RegistryEngine`):
   - Guides LLM extraction prompts
   - Validates extracted fields
   - Ensures completeness

---

## Registry Cleaning Pipeline

### Overview

The pipeline validates and normalizes registry data through 4 passes:

```
Raw Entry → Schema Normalization → CPT Cleanup → Consistency → Clinical QC → Cleaned Entry
              (Pass 1)              (Pass 2)       (Pass 3)      (Pass 4)
```

### Components

#### 1. Schema Normalization (`schema_utils.py`)

```python
class SchemaNormalizer:
    def normalize_entry(self, raw_entry, entry_id, logger):
        # 1. Ensure evidence dict exists
        # 2. Remove unknown fields → move to evidence
        # 3. Coerce types (string→int, boolean)
        # 4. Canonicalize enums ("Male"→"M")
        # 5. Apply required defaults
        # 6. Validate against JSON schema
```

**Enum Aliases:**
```python
ENUM_ALIASES = {
    "gender": {"male": "M", "female": "F", "woman": "F", "man": "M"},
    "sedation_type": {"mac": "Monitored Anesthesia Care", "ga": "General"},
    "airway_type": {"ett": "ETT", "trach": "Tracheostomy"}
}
```

#### 2. CPT Cleanup (`cpt_utils.py`)

```python
class CPTProcessor:
    def process_entry(self, entry, entry_id, logger):
        # 1. Normalize code format (parse modifiers)
        # 2. Flag unknown codes
        # 3. Enforce add-on requirements (+31627 needs primary)
        # 4. Apply auto-drop bundling rules
        # 5. Apply NCCI pairs
        # 6. Enforce sedation rules (drop 99152 if GA)
        # 7. Calculate total RVU
```

**Key Bundling Rules:**
| Rule | Trigger | Drops |
|------|---------|-------|
| `diagnostic_with_surgical` | 31628, 31629, etc. | 31622 |
| `tblbx_bundles_tbna_brush` | 31628 | 31623, 31625, 31629 |
| `sedation_incompatible` | sedation_type=General | 99152, +99153 |

#### 3. Consistency Checks (`consistency_utils.py`)

```python
class ConsistencyChecker:
    def apply(self, entry, entry_id, logger):
        # 1. Sync trainee_present from fellow_name
        # 2. Sync sedation_reversal_given from agent
        # 3. Sync pleurodesis_performed from agent
        # 4. Infer pneumothorax from intervention
        # 5. Flag missing disposition after complication
```

#### 4. Clinical QC (`clinical_qc.py`)

```python
class ClinicalQCChecker:
    def check(self, entry, cpt_context, entry_id, logger):
        # 1. Flag vague indications (< 6 chars or generic)
        # 2. Require radiographic_findings for imaging codes
        # 3. Require EBUS stations for 31652/31653
        # 4. Require nav_platform for +31627
        # 5. Require stent details for 31631/31636
        # 6. Flag missing complication fields when Complete
```

### Running the Pipeline

**CLI Usage:**
```bash
cd /Users/russellmiller/Projects/Procedure_suite
conda run -n medparse-py311 python scripts/clean_ip_registry.py \
  --registry-data data/samples/my_registry_dump.jsonl \
  --schema schemas/IP_Registry.json \
  --coding-kb proc_autocode/ip_kb/ip_coding_billing.v2_7.json \
  --output-json reports/cleaned_registry_data.json \
  --issues-log reports/issues_log.csv
```

**Output:**
```
[RegistryCleaner] Loaded 10 entries from data/samples/my_registry_dump.jsonl (format=ndjson)
Processed 10 entries -> reports/cleaned_registry_data.json
Captured 62 issues -> reports/issues_log.csv
Auto Fixed issues:
  - bundling_auto_drop: 1
  - enum_normalized: 12
  - integer_coerced: 2
Flagged For Manual issues:
  - complication_field_missing: 13
  - indication_too_vague: 1
Entries with severity=error: 0
```

**Issues Log Format (CSV):**
```csv
entry_id,issue_type,severity,action,field,details
MRN-001_2025-01-15_00000,bundling_auto_drop,info,auto_fixed,cpt_codes,{"old":"31622","rule":"diagnostic_with_surgical"}
MRN-001_2025-01-15_00000,enum_normalized,info,auto_fixed,gender,{"old":"Male","new":"M"}
```

---

## API Endpoints

### FastAPI Application

**Location:** `modules/api/fastapi_app.py` (NOT `api/app.py`)

**Server:** Port 8000

### Core Endpoints

#### Health Check
```
GET /health
Response: {"ok": true}
```

#### Coder Endpoint
```
POST /v1/coder/run
Content-Type: application/json

Request:
{
  "note": "Linear EBUS performed at stations 4R, 7, 11R...",
  "locality": "00",
  "setting": "facility",
  "explain": true
}

Response:
{
  "codes": [
    {
      "cpt": "31653",
      "description": "Bronchoscopy; with EBUS sampling, >=3 stations",
      "modifiers": [],
      "confidence": 0.9,
      "context": {
        "rvu_data": {
          "work_rvu": 4.96,
          "facility_payment": 232
        }
      }
    }
  ],
  "financials": {
    "total_work_rvu": 4.96,
    "total_facility_payment": 232
  },
  "ncci_actions": [...],
  "version": "0.2.0"
}
```

#### Registry Endpoint
```
POST /v1/registry/run
Content-Type: application/json

Request:
{
  "note": "65 year old male with lung nodule...",
  "explain": true
}

Response:
{
  "record": {
    "patient_age": 65,
    "gender": "M",
    "primary_indication": "lung nodule",
    "cpt_codes": ["31628"],
    ...
  },
  "evidence": {
    "patient_age": {"span": [0, 12], "text": "65 year old"}
  }
}
```

#### QA Sandbox Endpoint
```
POST /qa/run
Content-Type: application/json

Request:
{
  "note_text": "Procedure note text...",
  "modules_run": "all",  // "reporter", "coder", "registry", or "all"
  "procedure_type": "EBUS"
}

Response:
{
  "reporter_output": {...},
  "coder_output": {...},
  "registry_output": {...},
  "reporter_version": "v4.0",
  "coder_version": "v4.0",
  "repo_branch": "main",
  "repo_commit_sha": "abc123"
}
```

---

## Frontend Integration

### Interventional-Pulm-Education-Project

**Framework:** Next.js 14 with TypeScript

**Connection to Backend:**
```typescript
// Environment variable
PROC_API_URL=http://localhost:8000  // local
PROC_API_URL=https://procedure-suite-xxx.up.railway.app  // production
```

### API Routes (Next.js)

**`/api/qa/run` (POST):**
```typescript
// 1. Create session in Supabase
// 2. Call Python backend POST /qa/run
// 3. Store results in proc_qa_sessions table
// 4. Return outputs to frontend
```

**`/api/qa/feedback` (POST):**
```typescript
// Store user feedback (rating, error categories)
// Updates existing session record
```

### Data Flow

```
User enters note in /qa-sandbox
        │
        ▼
Frontend calls /api/qa/run
        │
        ▼
Next.js API creates Supabase session
        │
        ▼
Calls Python backend /qa/run (60s timeout)
        │
        ▼
Backend runs coder/registry/reporter
        │
        ▼
Results stored in Supabase
        │
        ▼
Displayed in frontend UI
        │
        ▼
User provides feedback → /api/qa/feedback
```

---

## Supabase Integration

### Connection

**Backend (`proc_registry/supabase_sink.py`):**
```python
SUPABASE_DB_URL = os.environ["SUPABASE_DB_URL"]
# postgresql://postgres:password@db.xxx.supabase.co:6543/postgres
```

**Frontend (3 clients):**
```typescript
// Browser client (anon key, client-side)
supabaseBrowser()

// Server client (anon key + cookies, server components)
supabaseServer()

// Admin client (service role key, API routes only)
supabaseAdmin()
```

### Database Tables

**proc_qa_sessions:**
```sql
CREATE TABLE proc_qa_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT now(),

  -- Input
  note_text TEXT NOT NULL,
  modules_run TEXT NOT NULL,  -- 'reporter', 'coder', 'registry', 'all'
  procedure_type TEXT,

  -- Outputs (JSONB)
  reporter_output JSONB,
  coder_output JSONB,
  registry_output JSONB,

  -- Versioning
  reporter_version TEXT,
  coder_version TEXT,
  repo_branch TEXT,
  repo_commit_sha TEXT,

  -- Feedback
  quality_rating INTEGER,  -- 1-5
  safe_to_use BOOLEAN,
  error_categories TEXT[],
  free_text_feedback TEXT,
  feedback_at TIMESTAMPTZ
);
```

---

## Railway Deployment

### Backend Service

**Start Command:**
```bash
uvicorn modules.api.fastapi_app:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```bash
PORT=8000                          # Set by Railway
GEMINI_API_KEY=<your-key>          # Required for LLM
GEMINI_MODEL=gemini-2.5-flash      # Model selection
SUPABASE_DB_URL=postgresql://...   # Database connection
CODER_USE_LLM_ADVISOR=false        # Disable in prod for speed
```

### Frontend Service

**railway.toml:**
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "npm run start:prod"
restartPolicyType = "on_failure"
```

**Environment Variables:**
```bash
PROC_API_URL=https://procedure-suite-xxx.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...  # Server-side only
```

---

## Local Development

### Backend Setup

```bash
cd /Users/russellmiller/Projects/Procedure_suite

# Activate environment
conda activate medparse-py311

# Set environment variables
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-flash"
export SUPABASE_DB_URL="postgresql://..."

# Start server
uvicorn modules.api.fastapi_app:app --reload --host 0.0.0.0 --port 8000

# Or use the dev script
./scripts/devserver.sh
```

### Frontend Setup

```bash
cd /Users/russellmiller/Projects/Interventional-Pulm-Education-Project

# Install dependencies
pnpm install

# Set environment (create .env.local)
echo 'PROC_API_URL=http://localhost:8000' >> .env.local

# Start dev server
pnpm dev  # Runs on port 3001
```

### Running Tests

```bash
cd /Users/russellmiller/Projects/Procedure_suite

# Run specific test
conda run -n medparse-py311 pytest tests/test_clean_ip_registry.py -v

# Run all tests
make test

# Type checking
make type

# Linting
make lint
```

---

## Configuration Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Model name (default: gemini-2.5-flash) |
| `SUPABASE_DB_URL` | Yes (prod) | PostgreSQL connection string |
| `CODER_USE_LLM_ADVISOR` | No | Enable LLM suggestions (default: false) |
| `PSUITE_KNOWLEDGE_FILE` | No | Path to knowledge base JSON |
| `PSUITE_KNOWLEDGE_WATCH` | No | Auto-reload on file change |

### File Paths

| Purpose | Path |
|---------|------|
| Main FastAPI app | `modules/api/fastapi_app.py` |
| CPT Coder | `proc_autocode/coder.py` |
| Knowledge base | `proc_autocode/ip_kb/ip_coding_billing.v2_7.json` |
| Registry schema | `schemas/IP_Registry.json` |
| Cleaning pipeline | `modules/registry_cleaning/*.py` |
| Cleaning CLI | `scripts/clean_ip_registry.py` |

### Important Notes

1. **DO NOT USE** `api/app.py` - it's deprecated
2. Always use `EnhancedCPTCoder` from `proc_autocode/coder.py`
3. Knowledge base hot-reloads when modified (dev mode)
4. Tests require `medparse-py311` conda environment
5. Only synthetic/de-identified notes - no real PHI
