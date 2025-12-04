# PHI Review System

A HIPAA-compliant medical coding system with physician-in-the-loop Protected Health Information (PHI) review.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHYSICIAN WORKFLOW                                 │
│                                                                              │
│   ┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐  │
│   │ 1. Input │───▶│ 2. Auto-Scrub│───▶│ 3. Review   │───▶│ 4. Confirm   │  │
│   │ Note     │    │ (Presidio)   │    │ Highlights  │    │ & Submit     │  │
│   └──────────┘    └──────────────┘    └─────────────┘    └──────┬───────┘  │
│                                                                  │          │
└──────────────────────────────────────────────────────────────────┼──────────┘
                                                                   │
                          ┌────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURE PROCESSING LAYER                              │
│                                                                              │
│   ┌──────────────────┐         ┌──────────────────────────────────────────┐ │
│   │ PHI VAULT        │         │ PROCEDURE DATA                          │ │
│   │                  │         │                                          │ │
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

Auto-scrubbers like Presidio often over-flag clinical terms. The physician can:
- **Unflag** false positives (e.g., "LEFT UPPER LOBE" flagged as location)
- **Add** missed PHI that the auto-scrubber missed
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

### Backend

```bash
cd phi_review_system/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg presidio-analyzer cryptography pydantic

# Download spaCy model for Presidio
python -m spacy download en_core_web_lg

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/phi_vault"
export ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd phi_review_system/frontend

# If using Vite
npm create vite@latest phi-review-ui -- --template react
cd phi-review-ui
npm install

# Copy components
cp ../PHIReviewEditor.jsx src/
cp ../PHIReviewDemo.jsx src/

# Update App.jsx to use PHIReviewDemo
# Run dev server
npm run dev
```

## Configuration

### Presidio Allow-Lists

Critical for preventing over-scrubbing. Configure in `dependencies.py`:

```python
anatomical_terms = [
    "left", "right", "bilateral",
    "upper lobe", "middle lobe", "lower lobe",
    "left upper lobe", "right middle lobe",
    # ... etc
]
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

The `scrubbing_feedback` table captures:
- What Presidio got wrong (false positives/negatives)
- Precision and recall metrics per document
- Breakdown by document type and specialty

Use this data to:
1. Add terms to Presidio allow-lists
2. Create custom Presidio recognizers
3. Fine-tune underlying NER models
4. Track improvement over time

```sql
-- Presidio accuracy by specialty
SELECT 
  specialty,
  AVG(precision) as avg_precision,
  AVG(recall) as avg_recall,
  AVG(f1_score) as avg_f1
FROM scrubbing_feedback
GROUP BY specialty;
```

## Security Considerations

1. **Network Isolation**: PHI vault should be in a private subnet
2. **TLS**: All API traffic must use HTTPS
3. **Authentication**: Implement proper JWT validation (placeholder in code)
4. **Key Management**: Use AWS KMS or HashiCorp Vault for encryption keys
5. **Audit Log Protection**: Make audit_log append-only (no UPDATE/DELETE)
6. **Data Retention**: Implement TTL policies for PHI vault

## License

Internal use only. Contains HIPAA-regulated design patterns.
