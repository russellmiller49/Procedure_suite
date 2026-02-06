# Structured Reporter Guide

The structured reporter renders a `ProcedureBundle` into an Interventional Pulmonology operative report using YAML + Jinja templates.

The same engine powers the Interactive Reporter Builder loop (Text → seed bundle → validate/questions → RFC6902 patch → re-render).

## Read First (Repo Constraints)

- [`AGENTS.md`](../AGENTS.md)
- [`CLAUDE.md`](../CLAUDE.md)
- [`README.md`](../README.md) and [`docs/README.md`](README.md)
- [`docs/DEVELOPMENT.md`](DEVELOPMENT.md)

Reporter style rules are captured in [`docs/REPORTER_STYLE_GUIDE.md`](REPORTER_STYLE_GUIDE.md).

Notes:
- Startup-enforced pipeline invariants live in `modules/api/fastapi_app.py:_validate_startup_env()`; do not bypass them.
- Keep the server stateless: the client stores the bundle and resubmits it each request; do not persist raw note text.

## Key Entry Points

- Rendering core: `modules/reporting/engine.py`
- Seeding bundles: `modules/reporting/engine.py:build_procedure_bundle_from_extraction()`
- Validation issues: `modules/reporting/validation.py:ValidationEngine`
- Questions/prompts: `modules/reporting/questions.py` (`QuestionSpec`, `PROMPT_SPEC_REGISTRY`)
- RFC6902 patch: `modules/reporting/json_patch.py:apply_bundle_json_patch()`
- API routes: `modules/api/fastapi_app.py` (`POST /report/seed_from_text`, `/report/questions`, `/report/render`)
- UI: `modules/api/static/phi_redactor/reporter_builder.html` (+ `reporter_builder.js`)

Note: `modules/reporter/` is a deprecated shim; import from `modules/reporting/` instead.

## Architecture (Bundle → Note)

1. **Template metadata (YAML)** in `configs/report_templates/` declares `id`, `schema_id`, `template_path`, output section, required/critical/recommended/optional fields, category, and CPT hints.
2. **Jinja templates (.j2)** in `configs/report_templates/` contain prose with placeholders converted to `snake_case` variables and `{% if %}` guards.
3. **Pydantic schemas** live in `proc_schemas/clinical/` (plus a small set of reporter-only partial overrides in `modules/reporting/partial_schemas.py` for interactive drafts).
4. **TemplateRegistry + SchemaRegistry** (in `modules/reporting/engine.py`) load YAML + Jinja into `TemplateMeta` objects and map `schema_id` → Pydantic model.
5. **ReporterEngine.compose_report_with_metadata** orders procedures, renders templates, attaches discharge instructions, wraps everything in the operative report shell (`configs/report_templates/ip_or_main_oper_report_shell.*`), and post-processes/validates the output.

In the interactive endpoints we also run:

- **Inference**: `modules/reporting/inference.py:InferenceEngine.infer_bundle()`
- **Validation**: `modules/reporting/validation.py:ValidationEngine.list_missing_critical_fields()` (drives issues + questions)

## Interactive Reporter Builder (Prompt Loop)

The interactive flow is stateless: the client holds the latest `bundle` and re-submits it every request.

- `POST /report/seed_from_text`
  - Scrubs text (server-side for now), runs extraction-first registry extraction, builds a `ProcedureBundle`, runs inference + validation, renders a draft, and returns UI-ready questions.
- `POST /report/questions`
  - Re-runs inference + validation on a client-provided bundle and returns questions.
- `POST /report/render`
  - Applies patch (BundlePatch or RFC6902 JSON Patch ops), re-runs inference + validation, and returns updated bundle + rendered draft.

### RFC6902 JSON Patch Contract

- Preferred UI patch format is a list of RFC6902 ops:
  - Example: `[{"op":"replace","path":"/procedures/0/data/needle_gauge","value":"22"}]`
- The UI should use `questions[].pointer` directly as the patch `path` (stable contract for the prompt loop).
- The server normalizes a few UI-friendly shapes during `/report/render`:
  - `/echo_features`: list → comma-separated string.
  - `/tests`: string → `list[str]` split on commas/newlines.

### Strict Mode

- `strict=false`: renders drafts even when required fields are missing; missing fields appear as issues and questions.
- `strict=true`: enables style validation (no `None`, no placeholders, no obvious formatting artifacts). For the interactive UI, strict failures fall back to a non-strict preview but still return the missing-field issues.

## Adding a New Procedure Template

1. Create the YAML meta file: `configs/report_templates/<id>.yaml`.
2. Create the Jinja template: `configs/report_templates/<template_path>.j2` (guard optional fields; follow `docs/REPORTER_STYLE_GUIDE.md`).
3. Add/extend the Pydantic model in `proc_schemas/clinical/*` (or add a reporter-only partial model in `modules/reporting/partial_schemas.py` if interactive drafts should render with missing fields).
4. Register the schema in `modules/reporting/engine.py:default_schema_registry()`.
5. Update ordering if needed: `configs/report_templates/procedure_order.json`.
6. Add a test that renders and asserts missing-field prompting works:
   Prefer API coverage in `tests/api/test_fastapi.py` for the seed → questions → patch → rerender loop.

## Seeding / Extraction Mappings

- `modules/reporting/engine.py:build_procedure_bundle_from_extraction()` converts a `RegistryRecord` (or extraction dict) into a reporter `ProcedureBundle`.
- `modules/reporting/engine.py:_add_compat_flat_fields()` bridges nested V3 shapes (`equipment`, `procedures_performed`, etc.) into legacy flat keys expected by `modules/registry/legacy/adapters/*`.
- When adding mappings, prefer reading from nested registry record fields; avoid inventing values. Leave missing fields as `None` and prompt via validation/questions.

## Template Coverage Test

`tests/unit/test_template_coverage.py` parses the knowledge file for `Template:` headings and ensures each has a corresponding YAML config (with a small allowlist). Run via `pytest`.

## CLI Helper

`scripts/render_report.py --input extraction.json --output report.txt` loads an extraction payload, builds a bundle, and renders a full report for quick debugging.
