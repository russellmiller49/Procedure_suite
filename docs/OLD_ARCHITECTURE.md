# Procedure Suite System Architecture

## Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Modules](#core-modules)
4. [Knowledge Base](#knowledge-base)
5. [Data Pipeline](#data-pipeline)
6. [Legacy vs. Active Components](#legacy-vs-active-components)

---

## Overview

The Procedure Suite is a modular system designed to automate the processing of Interventional Pulmonology procedure notes. It sits between the EMR/Extractor and downstream analytics/billing systems.

**Key Capabilities:**
- **Autonomous CPT coding**: Rule-based and ML-augmented code prediction.
- **Registry Extraction**: LLM-driven extraction of clinical data into a strict schema.
- **Structured Reporting**: Generating standardized reports from raw inputs.
- **RVU Calculation**: Real-time financial estimation based on CMS data.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                           │
│         (Interventional-Pulm-Education-Project)                 │
└─────────┬───────────────────────────────────────────────────────┘
          │ HTTP / JSON
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python Backend (FastAPI)                           │
│           [modules/api/fastapi_app.py]                          │
│                                                                 │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐   │
│  │  /v1/coder  │   │ /v1/registry │   │ /report/render      │   │
│  └──────┬──────┘   └──────┬───────┘   └──────────┬──────────┘   │
│         │                 │                      │              │
│         ▼                 ▼                      ▼              │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐   │
│  │ Enhanced    │   │ Registry     │   │ Reporter Engine     │   │
│  │ CPT Coder   │   │ Engine       │   │ (proc_report)       │   │
│  └──────┬──────┘   └──────┬───────┘   └─────────────────────┘   │
│         │                 │                                     │
│         │                 ▼                                     │
│         │          [Gemini API (LLM)]                           │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 Knowledge Layer                          │   │
│  │         (data/knowledge/ip_coding_billing.v2_7.json)     │   │
│  │         (schemas/IP_Registry.json)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. API Layer (`modules/api/`)
- **File**: `fastapi_app.py`
- **Status**: **Active**
- **Role**: Entry point. Routes requests to the appropriate engines. Handles standard FastAPI validation and schemas.

### 2. Autocode Engine (`proc_autocode/`)
- **File**: `coder.py` (`EnhancedCPTCoder`)
- **Status**: **Active**
- **Role**: Analyzes text to identify procedures. Applies complex bundling rules (NCCI), mutually exclusive checks, and logic from the IP Knowledge Base. Calculates RVUs.

### 3. Registry Engine (`modules/registry/`)
- **Status**: **Active**
- **Role**: Manages the extraction of structured data.
- **Process**:
    1.  **Schema Norm**: Coerces types and standardizes enums.
    2.  **LLM Extraction**: Sends prompts to Gemini to parse text.
    3.  **Post-processing**: Cleans up LLM outputs (e.g., string-to-list conversion).
    4.  **Validation**: Checks against `IP_Registry.json` schema.

### 4. Reporter Engine (`proc_report/`)
- **Status**: **Active**
- **Role**: Generates synoptic reports.
- **Features**:
    - **Inference**: Auto-fills fields based on other data (e.g., implying 'General Anesthesia' if 'Propofol' and 'Rocuronium' are used).
    - **Validation**: Warns about missing required fields for specific procedure types.
    - **Rendering**: Uses Jinja2 templates to produce Markdown reports.

### 5. Adapters (`proc_registry/`)
- **Status**: **Active**
- **Role**: Connects the internal Python objects to external systems (Supabase) or converts between internal schemas (Registry -> Clinical Pydantic models).

---

## Knowledge Base

The system is data-driven, relying heavily on external configuration files rather than hard-coded logic.

| File | Path | Purpose |
|------|------|---------|
| **IP Coding & Billing** | `data/knowledge/ip_coding_billing.v2_7.json` | Source of truth for CPT codes, RVUs, NCCI edits, and bundling rules. |
| **IP Registry Schema** | `schemas/IP_Registry.json` | JSON Schema defining the valid structure of a clinical registry entry. |
| **Templates** | `proc_report/templates/` | Jinja2 templates for report generation. |

---

## Legacy vs. Active Components

Significant refactoring has occurred (v4). It is crucial to distinguish between active and dead code.

| Component | Active Implementation | Legacy / Deprecated |
|-----------|-----------------------|---------------------|
| **Web Server** | `modules/api/fastapi_app.py` | `api/app.py` |
| **Coder** | `proc_autocode/coder.py` | `modules/coder/engine.py` |
| **Router** | `modules/api/routes/` | `api/enhanced_coder_routes.py` |

**Note**: Legacy files are kept in the repository for reference but should not be used or edited. They may be moved to `_archive/` in future cleanups.
