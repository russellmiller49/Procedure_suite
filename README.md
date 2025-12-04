# Procedure Suite

**Automated CPT Coding, Registry Extraction, and Synoptic Reporting for Interventional Pulmonology.**

This toolkit allows you to:
1.  **Predict CPT Codes**: Analyze procedure notes to automatically generate billing codes with RVU calculations.
2.  **Extract Registry Data**: Use LLMs to extract structured clinical data (EBUS stations, complications, demographics) into a validated schema.
3.  **Generate Reports**: Create standardized, human-readable procedure reports from structured data.

## 📚 Documentation

- **[Installation & Setup](docs/INSTALLATION.md)**: Setup guide for Python, spaCy models, and API keys.
- **[User Guide](docs/USER_GUIDE.md)**: How to use the CLI tools and API endpoints.
- **[Development Guide](docs/DEVELOPMENT.md)**: **CRITICAL** for contributors and AI Agents. Defines the system architecture and coding standards.
- **[Architecture](docs/ARCHITECTURE.md)**: System design and module breakdown.
- **[CPT Reference](docs/REFERENCES.md)**: List of supported codes.

## ⚡ Quick Start

1.  **Install**:
    ```bash
    micromamba activate medparse-py311
    make install
    make preflight
    ```

2.  **Configure**:
    Create `.env` with your `GEMINI_API_KEY`.

3.  **Run**:
    ```bash
    # Start the API/Dev Server
    ./scripts/devserver.sh
    ```

## 🏗️ Key Modules

| Module | Description |
|--------|-------------|
| **`modules/api/fastapi_app.py`** | The main FastAPI backend. |
| **`proc_autocode/`** | Enhanced CPT coding engine with Knowledge Base support. |
| **`modules/registry/`** | LLM-based registry extraction pipeline. |
| **`proc_report/`** | Template-based synoptic report generator. |
| **`/ui/phi_demo.html`** | Synthetic PHI demo UI for scrubbing → vault → review → reidentify. |

## ⚠️ Note for AI Assistants

**Please read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) before making changes.**
*   Always edit `modules/api/fastapi_app.py`.
*   Never edit `api/app.py` (Deprecated).
*   Use `EnhancedCPTCoder` from `proc_autocode/coder.py`.
