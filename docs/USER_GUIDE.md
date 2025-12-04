# Procedure Suite - User Guide

This guide explains how to use the Procedure Suite tools for generating reports, coding procedures, and validating registry data.

## 🚀 Quick Start: The Dev Server

The easiest way to interact with the system is the development server, which provides a web UI and API documentation.

```bash
./scripts/devserver.sh
```
*Starts the server on port 8000.*

- **Web UI**: [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html) (Note: path may vary based on static setup)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠 CLI Tools

The suite includes several command-line scripts for batch processing and validation.

### 1. Validate Registry Extraction
Run the extraction pipeline on synthetic notes and compare against ground truth.

```bash
make validate-registry
```
*Output*: `reports/registry_validation_output.txt` and `data/registry_errors.jsonl`

### 2. Evaluate CPT Coder
Test the CPT coding engine against the training dataset.

```bash
python scripts/evaluate_cpt.py
```
*Output*: Accuracy metrics and error logs in `data/cpt_errors.jsonl`.

### 3. Self-Correction (LLM)
Ask the LLM to analyze specific registry fields or errors and suggest improvements.

```bash
# Analyze errors for a specific field
make self-correct-registry FIELD=sedation_type
```
*Output*: `reports/registry_self_correction_sedation_type.md`

### 4. Clean & Normalize Registry
Run the full cleaning pipeline (Schema Norm -> CPT Logic -> Consistency -> Clinical QC) on a raw dataset.

```bash
python scripts/clean_ip_registry.py \
  --registry-data data/samples/my_registry_dump.jsonl \
  --output-json reports/cleaned_registry_data.json \
  --issues-log reports/issues_log.csv
```

---

## 🔌 API Usage

You can interact with the system programmatically via the REST API.

### CPT Coding Endpoint
**POST** `/v1/coder/run`

Input:
```json
{
  "note": "Bronchoscopy with EBUS at station 7.",
  "locality": "00",
  "setting": "facility"
}
```

Output:
```json
{
  "codes": [
    {
      "cpt": "31652",
      "description": "Bronchoscopy w/ EBUS 1-2 stations",
      "confidence": 0.95
    }
  ],
  "financials": {
    "total_work_rvu": 4.46
  }
}
```

### Registry Extraction Endpoint
**POST** `/v1/registry/run`

Input:
```json
{
  "note": "Patient is a 65yo male..."
}
```

Output:
```json
{
  "record": {
    "patient_age": 65,
    "gender": "M",
    "cpt_codes": [...]
  }
}
```

---

## 📊 Key Files

- **`data/knowledge/ip_coding_billing.v2_7.json`**: The "Brain". Contains all CPT codes, RVUs, and bundling rules.
- **`schemas/IP_Registry.json`**: The "Law". Defines the valid structure for registry data.
- **`reports/`**: Where output logs and validation summaries are saved.

```

# Start the local server
uvicorn modules.api.fastapi_app:app --reload --port 8000