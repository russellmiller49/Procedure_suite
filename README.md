# Procedure Suite

The Procedure Suite provides structured report composition, autonomous coding, registry exports, and API endpoints that sit between the existing extractor and downstream analytics. It reuses the medparse-py311 environment and expects scispaCy + spaCy models to be available locally.

## Layout
- `proc_report`: templated synoptic report builder that consumes extractor hints or free text.
- `proc_autocode`: rule-driven coding pipeline with CPT maps, NCCI rules, and confidence scoring.
- `proc_registry`: adapters that turn reports/codes into Supabase-ready bundles.
- `proc_nlp`: UMLS linker and normalization helpers shared by the report engine + coder.
- `api`: FastAPI surface for compose/code/upsert flows.
- `tests`: seed unit + contract suites to keep CI green from day one.

## Getting Started
```bash
micromamba activate medparse-py311  # or conda activate medparse-py311
make install
make preflight
make test
```

Provide `.env` with Supabase credentials (see `.env.sample`).
