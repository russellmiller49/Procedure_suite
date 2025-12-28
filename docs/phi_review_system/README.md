# PHI Review System

A HIPAA-compliant medical coding system with physician-in-the-loop Protected Health Information (PHI) review using **client-side hybrid detection** (DistilBERT ML + regex patterns).

## Architecture Overview

### Client-Side Hybrid Detection Pipeline (Primary)

The PHI redaction system uses a **client-side hybrid pipeline** that runs entirely in the browser:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CLIENT-SIDE PHI DETECTION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Text Input ─────────────────────▶ Monaco Editor                         │
│                                                                              │
│   2. Web Worker Detection ────────────────────────────────────────────────   │
│      ├── ML Detection (DistilBERT via Transformers.js / ONNX)               │
│      └── Regex Detection (structured patterns: names, MRN, dates)           │
│                                                                              │
│   3. Protected Terms Veto (protectedVeto.js) ─────────────────────────────   │
│      └── Filters false positives: LN stations, anatomy, devices, CPT codes  │
│                                                                              │
│   4. User Review ─────────────────────────────────────────────────────────   │
│      ├── Highlight + checkbox toggle (exclude false positives)              │
│      └── Manual Additions (Selection + Add Redaction button)                │
│                                                                              │
│   5. Apply Redactions ──────────────▶ [REDACTED] placeholders               │
│                                                                              │
│   6. Submit Scrubbed Text ──────────▶ Server (only scrubbed text sent)      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Monaco UI | `/ui/phi_redactor/index.html` | Interactive editor |
| App Logic | `/ui/phi_redactor/app.js` | UI state, manual redaction |
| Worker | `/ui/phi_redactor/redactor.worker.js` | Hybrid ML+regex detection |
| Veto Layer | `/ui/phi_redactor/protectedVeto.js` | Filter false positives |
| ONNX Model | `/ui/phi_redactor/vendor/phi_distilbert_ner/` | DistilBERT NER |

### Why Client-Side?

1. **No PHI leaves the browser** until user confirms redactions
2. **Instant feedback** - no network latency for detection
3. **User control** - physician reviews and corrects before submission
4. **Offline capable** - works without server connection

### Manual Redaction Feature

Users can add redactions for PHI missed by auto-detection:
1. Select text in the editor
2. Choose entity type from dropdown (Patient, ID, Date, etc.)
3. Click "Add" button
4. Manual detections appear with **amber/yellow highlighting** (vs red for auto)
5. Manual detections appear in sidebar with "manual" source tag

---

### Server-Side Processing Layer (After Client Redaction)

Once the physician confirms redactions, the scrubbed text is submitted to the server:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURE PROCESSING LAYER                              │
│                                                                              │
│   ┌──────────────────┐         ┌──────────────────────────────────────────┐ │
│   │ PHI VAULT        │         │ PROCEDURE DATA                          │ │
│   │ (Optional)       │         │                                          │ │
│   │ • Encrypted PHI  │◀───────▶│ • Scrubbed text (no PHI)                │ │
│   │ • AES-256        │  UUID   │ • Entity map (for reconstruction)       │ │
│   │ • Key rotation   │  Link   │ • Processing status                     │ │
│   └──────────────────┘         └──────────────────────────────────────────┘ │
│                                             │                                │
│                                             ▼                                │
│                                   ┌─────────────────┐                       │
│                                   │ LLM PROCESSING  │                       │
│                                   │ (Gemini/GPT-4)  │                       │
│                                   │ • Only sees     │                       │
│                                   │   scrubbed text │                       │
│                                   └────────┬────────┘                       │
│                                            │                                 │
└────────────────────────────────────────────┼─────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RE-IDENTIFICATION                                  │
│                                                                              │
│   Authorized users can request re-identification to view results with PHI   │
│   • Decrypts PHI from vault                                                 │
│   • Merges with coding results                                              │
│   • Full audit trail logged                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Benefits

### 1. Physician-in-the-Loop (No Separate Review Queue)

Unlike traditional HITL architectures that require a separate review workforce, this system keeps the physician as the reviewer:

| Traditional HITL | This System |
|------------------|-------------|
| Separate review team | Physician reviews their own note |
| Queue delays (hours/days) | Inline review (seconds) |
| Additional headcount costs | Zero additional cost |
| Training required | Physician already understands context |

### 2. Prevents Semantic Destruction

The hybrid detection system includes a **protected terms veto layer** that prevents over-flagging clinical terms, but the physician can also:
- **Unflag** false positives via checkboxes (e.g., "LEFT UPPER LOBE" incorrectly flagged)
- **Add** missed PHI via selection + "Add" button
- **Preserve** clinically essential context for accurate coding

### 3. HIPAA Compliance

- **Audit Trail**: Every PHI access, modification, and decryption is logged
- **Expert Determination Support**: Physician attestation creates documentation for HIPAA Expert Determination method
- **Encryption at Rest**: All PHI encrypted with Fernet (AES-128-CBC)
- **Access Control**: Role-based permissions for re-identification

## Directory Structure

```
phi_review_system/
├── backend/
│   ├── main.py           # FastAPI application entry point
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── endpoints.py      # API route handlers
│   └── dependencies.py   # Dependency injection providers
│
├── frontend/
│   ├── PHIReviewEditor.jsx   # Main review component
│   └── PHIReviewDemo.jsx     # Full workflow demo page
│
└── README.md
```

## Database Schema

### Core Tables

#### `phi_vault`
Encrypted storage for Protected Health Information.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (also serves as job_id) |
| encrypted_data | BYTEA | Fernet-encrypted PHI JSON |
| data_hash | VARCHAR(64) | SHA-256 of plaintext for integrity verification |
| key_version | INTEGER | Supports key rotation |
| created_at | TIMESTAMP | When PHI was vaulted |

#### `procedure_data`
De-identified clinical text and processing results.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| phi_vault_id | UUID | Foreign key to phi_vault |
| scrubbed_text | TEXT | Text with PHI replaced by placeholders |
| entity_map | JSONB | Mapping for reconstruction |
| status | ENUM | Processing status |
| coding_results | JSONB | LLM output (CPT/ICD codes) |
| submitted_by | VARCHAR | Physician user ID |

#### `audit_log`
Comprehensive audit trail for HIPAA compliance.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | VARCHAR | Who performed the action |
| action | ENUM | What action was performed |
| phi_vault_id | UUID | Which PHI record was accessed |
| ip_address | VARCHAR | Request source |
| timestamp | TIMESTAMP | When action occurred |
| metadata | JSONB | Additional context |

#### `scrubbing_feedback`
ML improvement data from physician corrections.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| procedure_data_id | UUID | Link to procedure |
| false_positives | JSONB | Items Presidio flagged, physician unflagged |
| false_negatives | JSONB | Items physician added, Presidio missed |
| precision | FLOAT | Calculated metric |
| recall | FLOAT | Calculated metric |

## API Endpoints

### `POST /v1/coder/scrub/preview`
Analyze text for PHI without storing anything.

**Request:**
```json
{
  "raw_text": "Patient John Smith (MRN: 12345) underwent EBUS...",
  "document_type": "procedure_note",
  "specialty": "interventional_pulmonology"
}
```

**Response:**
```json
{
  "raw_text": "Patient John Smith...",
  "entities": [
    {
      "text": "John Smith",
      "start": 8,
      "end": 18,
      "entity_type": "PERSON",
      "confidence": 0.98,
      "source": "auto"
    }
  ],
  "preview_id": "prev_abc123",
  "expires_at": "2024-03-15T15:00:00Z",
  "processing_time_ms": 234
}
```

### `POST /v1/coder/submit`
Vault confirmed PHI and queue for processing.

**Request:**
```json
{
  "raw_text": "Patient John Smith...",
  "confirmed_phi": [
    {
      "text": "John Smith",
      "start": 8,
      "end": 18,
      "entity_type": "PERSON",
      "confidence": 0.98,
      "source": "auto"
    }
  ],
  "preview_id": "prev_abc123"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "phi_confirmed",
  "message": "PHI secured. Job queued for processing.",
  "phi_entities_secured": 5,
  "scrubbed_text_preview": "Patient <PERSON_0> (MRN: <MRN_1>) underwent...",
  "status_url": "/v1/coder/status/550e8400-e29b-41d4-a716-446655440000"
}
```

### `GET /v1/coder/status/{job_id}`
Check processing status.

### `POST /v1/coder/reidentify`
Re-attach PHI to results (authorized users only).

## Frontend Components

### PHIReviewEditor

The main review component with:
- Highlighted PHI entities (color-coded by type)
- Click to select/unflag entities
- Text selection to add missed PHI
- Entity type selector
- Summary panel
- Submit/cancel actions

### Color Coding

| Entity Type | Color |
|-------------|-------|
| PERSON | Red |
| DATE | Amber |
| MRN | Blue |
| LOCATION | Green |
| PHONE | Indigo |
| EMAIL | Pink |
| PROVIDER | Purple |

## Setup Instructions

### Client-Side PHI Redactor (Primary)

The PHI redactor runs entirely in the browser. No special setup needed:

```bash
# Start the main dev server
uvicorn modules.api.fastapi_app:app --reload --port 8000

# Access the PHI Redactor at:
# http://localhost:8000/ui/phi_redactor/
```

The client-side model files are served from:
- `/ui/phi_redactor/vendor/phi_distilbert_ner/` - ONNX model bundle

### Backend (For LLM Processing)

The backend only receives scrubbed text. No Presidio required:

```bash
cd procedure_suite

# Install dependencies
pip install -e .

# Set environment variables (optional - for vault storage)
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/phi_vault"
export ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Run the server
uvicorn modules.api.fastapi_app:app --reload --port 8000
```

## Configuration

### Protected Terms Veto Layer

The client-side veto layer (`/ui/phi_redactor/protectedVeto.js`) prevents over-redaction of clinical terms:

**Protected Categories:**
- **LN Stations**: 4R, 7, 11L, etc. (when "station" context present)
- **Anatomy**: trachea, carina, RUL, LLL, bronchus intermedius
- **Devices**: Ion, Monarch, Galaxy, Zephyr, Chartis, PleurX
- **Procedures**: EBUS, TBNA, BAL, bronchoscopy
- **CPT Codes**: 31653, 77012 (when in billing context)
- **Provider Names**: Dr. Smith, Attending, Fellow (not patient PHI)

To add new protected terms, edit `protectedVeto.js`:

```javascript
// In protectedVeto.js
const PROTECTED_DEVICES = ["ion", "monarch", "galaxy", /* add new */];
const LN_STATIONS = ["1", "2L", "2R", /* add new */];
```

### Encryption Key Rotation

The system supports key rotation via the `key_version` field:

```python
# In EncryptionService
def rotate_key(self, new_key: str):
    # 1. Generate new Fernet instance
    # 2. Update key_version in database
    # 3. Re-encrypt records on access (lazy rotation)
```

## Audit Compliance

### Tracked Actions

- `PHI_CREATED` - New PHI vaulted
- `PHI_ACCESSED` - PHI record queried
- `PHI_DECRYPTED` - PHI decrypted for display
- `REVIEW_STARTED` - Physician began PHI review
- `ENTITY_CONFIRMED` - Physician confirmed entity as PHI
- `ENTITY_UNFLAGGED` - Physician removed PHI flag
- `ENTITY_ADDED` - Physician flagged missed PHI
- `LLM_CALLED` - Request sent to LLM
- `REIDENTIFIED` - Results merged with PHI

### Audit Query Examples

```sql
-- All PHI access for a user in last 30 days
SELECT * FROM audit_log 
WHERE user_id = 'dr.smith@hospital.org'
  AND action IN ('PHI_ACCESSED', 'PHI_DECRYPTED')
  AND timestamp > NOW() - INTERVAL '30 days';

-- Failed access attempts
SELECT * FROM audit_log
WHERE metadata->>'authorized' = 'false';
```

## ML Improvement Loop

### Prodigy-Based Iterative Correction

The system uses [Prodigy](https://prodi.gy/) for human-in-the-loop model improvement:

1. **Sample notes** → Pre-annotate with DistilBERT model
2. **Prodigy ner.manual** → Human reviews/corrects annotations
3. **Export corrections** → Merge with training data
4. **Fine-tune model** → Retrain DistilBERT on corrected data

See `CLAUDE.md` for detailed Prodigy workflow commands:

```bash
make prodigy-prepare      # Sample + pre-annotate
make prodigy-annotate     # Launch Prodigy UI
make prodigy-export       # Export corrections
make prodigy-finetune     # Fine-tune model
make gold-cycle           # Full gold standard workflow
```

### Key Training Data Files

| File | Purpose |
|------|---------|
| `phi_gold_standard_v1.jsonl` | Pure human-verified Prodigy annotations |
| `phi_train_gold.jsonl` | Training set (80% of notes) |
| `phi_test_gold.jsonl` | Test set (20% of notes) |

## Security Considerations

1. **Network Isolation**: PHI vault should be in a private subnet
2. **TLS**: All API traffic must use HTTPS
3. **Authentication**: Implement proper JWT validation (placeholder in code)
4. **Key Management**: Use AWS KMS or HashiCorp Vault for encryption keys
5. **Audit Log Protection**: Make audit_log append-only (no UPDATE/DELETE)
6. **Data Retention**: Implement TTL policies for PHI vault

## License

Internal use only. Contains HIPAA-regulated design patterns.
