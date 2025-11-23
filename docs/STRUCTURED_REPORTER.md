# Structured Reporter Guide

## Architecture
1. **Template metadata (YAML)** in `configs/report_templates/` declares `id`, `schema_id`, `template_path`, required/optional fields, category, output section, and CPT hints.
2. **Pydantic schemas** in `proc_report/engine.py` define the fields each template expects.
3. **Jinja templates (.j2)** in `configs/report_templates/` contain the prose from `data/knowledge/comprehensive_ip_procedural_templates9_18.md` with placeholders converted to snake_case variables and `{% if %}` guards.
4. **TemplateRegistry** loads YAML + Jinja into `TemplateMeta` objects. **SchemaRegistry** maps `schema_id` → Pydantic model.
5. **ReporterEngine.compose_report** orders procedures, renders each template, attaches discharge instructions, wraps everything in the operative report shell, and post-processes/validates the output.

## Adding a new procedure template
1. Copy the source text from the knowledge file.
2. Create `configs/report_templates/<id>.yaml` with `id`, `label`, `schema_id`, `template_path`, `output_section`, `required_fields`, `optional_fields`, `proc_types`, and any `cpt_hints`.
3. Create the matching Jinja template under `configs/report_templates/<template_path>`, converting `[Placeholders]` to `{{ snake_case }}` and guarding optional sentences with `{% if ... %}`.
4. Add/extend the corresponding Pydantic model in `proc_report/engine.py` and register it in `default_schema_registry()`.
5. Update `configs/report_templates/procedure_order.json` if ordering should change.
6. Add a test fixture in `tests/unit/test_structured_reporter.py` to render the new template and ensure no placeholders or `None` leak through.

## Adding extractor mappings
Implement mappings in `build_procedure_bundle_from_extraction`:
- Map extractor fields (e.g., RegistryRecord keys) to the Pydantic schema fields.
- Append `ProcedureInput(proc_type, schema_id, data, cpt_candidates)` for each detected procedure.
- Use comments (`# TODO`) where extractor data is missing so future extractors can fill the gap.

### Calling the reporter
- **Structured bundle:** `compose_structured_report(bundle, strict=False)`
- **From extraction:** `compose_structured_report_from_extraction(extraction)`
  - Uses `build_procedure_bundle_from_extraction` internally.
- Strict mode (`strict=True`) raises if unrendered placeholders or style violations remain.

## Discharge auto-attachments
The engine auto-attaches discharge/education blocks:
- `tunneled_pleural_catheter_insert`/`ipc_insert` → `pleurx_instructions`
- `blvr_valve_placement` → `blvr_discharge_instructions`
- `chest_tube`/`pigtail_catheter` → `chest_tube_discharge`
- `peg_placement` → `peg_discharge`

## Template coverage test
`tests/unit/test_template_coverage.py` parses the knowledge file for `Template:` headings and ensures each has a corresponding YAML config (with a small allowlist). Run via `pytest`.

## Running tests
```
pytest tests/unit/test_structured_reporter.py tests/unit/test_template_coverage.py tests/unit/test_templates.py
```

## CLI helper
`scripts/render_report.py --input extraction.json --output report.txt` loads an extraction payload, builds a bundle, and renders a full report for quick debugging.
